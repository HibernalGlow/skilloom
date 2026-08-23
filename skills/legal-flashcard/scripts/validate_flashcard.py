#!/usr/bin/env python3
"""Deterministically validate DAMO flashcard Markdown schema 1."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

ATTR_RE = re.compile(r'(?P<key>[A-Za-z][\w-]*)="(?P<value>[^"]*)"')
CARD_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SOURCE_KEY_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*$")
RUNTIME_RE = re.compile(
    r"(?:custom-riff-decks|\bdue\b|\binterval\b|review\s+log|\bsuspend\b|\bbury\b|device\s+state|srs\s+state)",
    re.IGNORECASE,
)
ALLOWED = {
    "custom-dm-source-key",
    "custom-dm-card-id",
    "custom-dm-card-schema",
    "custom-dm-card-kind",
    "custom-dm-card-renderer",
    "custom-qb-question-topic-ids",
}
KINDS = {"basic", "cloze", "mnemonic"}
RENDERERS = {"list", "mark", "blockquote", "callout"}


@dataclass(frozen=True)
class Finding:
    line: int
    code: str
    message: str


def parse_ial_blocks(lines: list[str]) -> tuple[list[tuple[int, int, dict[str, str], str]], list[Finding]]:
    cards = []
    findings: list[Finding] = []
    in_fence = False
    index = 0
    while index < len(lines):
        line = lines[index]
        if re.match(r"^\s*(?:>\s*)?```", line):
            in_fence = not in_fence
            index += 1
            continue
        if line.lstrip().startswith("{:"):
            start = index
            body = [line]
            while not body[-1].rstrip().endswith("}") and index + 1 < len(lines):
                index += 1
                body.append(lines[index])
            raw = "\n".join(body)
            if in_fence:
                findings.append(Finding(start + 1, "E008", "Card IAL is inside a code fence."))
            if not raw.rstrip().endswith("}"):
                findings.append(Finding(start + 1, "E001", "Unclosed IAL."))
            attrs = {m.group("key"): m.group("value") for m in ATTR_RE.finditer(raw)}
            cards.append((start, index, attrs, raw))
        index += 1
    return cards, findings


def validate(text: str) -> list[Finding]:
    lines = text.splitlines()
    cards, findings = parse_ial_blocks(lines)
    seen: dict[str, int] = {}
    for start, end, attrs, raw in cards:
        if not any(key.startswith("custom-dm-") for key in attrs):
            continue
        unknown = set(attrs) - ALLOWED
        for key in sorted(unknown):
            findings.append(Finding(start + 1, "E002", f"Unsupported card attribute: {key}."))
        required = {
            "custom-dm-source-key",
            "custom-dm-card-id",
            "custom-dm-card-schema",
            "custom-dm-card-kind",
            "custom-dm-card-renderer",
            "custom-qb-question-topic-ids",
        }
        for key in sorted(required - set(attrs)):
            findings.append(Finding(start + 1, "E003", f"Missing required card attribute: {key}."))
        card_id = attrs.get("custom-dm-card-id", "")
        if card_id:
            if not CARD_ID_RE.fullmatch(card_id):
                findings.append(Finding(start + 1, "E004", "custom-dm-card-id must be lowercase ASCII kebab-case."))
            if card_id in seen:
                findings.append(Finding(start + 1, "E005", f"Duplicate custom-dm-card-id; first seen on line {seen[card_id]}."))
            seen.setdefault(card_id, start + 1)
        source_key = attrs.get("custom-dm-source-key", "")
        if source_key and not SOURCE_KEY_RE.fullmatch(source_key):
            findings.append(Finding(start + 1, "E006", "custom-dm-source-key contains unsupported characters."))
        if attrs.get("custom-dm-card-schema") != "1":
            findings.append(Finding(start + 1, "E007", "Only custom-dm-card-schema=\"1\" is supported."))
        if attrs.get("custom-dm-card-kind") not in KINDS:
            findings.append(Finding(start + 1, "E009", "custom-dm-card-kind must be basic, cloze, or mnemonic."))
        renderer = attrs.get("custom-dm-card-renderer")
        if renderer not in RENDERERS:
            findings.append(Finding(start + 1, "E010", "custom-dm-card-renderer must be list, mark, blockquote, or callout."))
        topic_ids = [item.strip() for item in attrs.get("custom-qb-question-topic-ids", "").split(",") if item.strip()]
        if not topic_ids or any(not CARD_ID_RE.fullmatch(item) for item in topic_ids):
            findings.append(Finding(start + 1, "E012", "custom-qb-question-topic-ids must contain lowercase ASCII kebab-case IDs."))
        if len(topic_ids) != len(set(topic_ids)):
            findings.append(Finding(start + 1, "E013", "custom-qb-question-topic-ids contains duplicates."))
        if RUNTIME_RE.search(raw) or RUNTIME_RE.search("\n".join(lines[max(0, start - 8): min(len(lines), end + 8)])):
            findings.append(Finding(start + 1, "E014", "Runtime scheduling or Riff fields leaked into the card block."))
        previous = start - 1
        while previous >= 0 and not lines[previous].strip():
            previous -= 1
        root = lines[previous].strip() if previous >= 0 else ""
        if renderer == "list" and not re.match(r"^-\s+", root):
            findings.append(Finding(start + 1, "E015", "list renderer IAL must attach to a root list item."))
        if renderer == "mark" and "==" not in root:
            findings.append(Finding(start + 1, "E016", "mark renderer requires a visible short cloze target."))
        if renderer == "blockquote" and not root.startswith(">"):
            findings.append(Finding(start + 1, "E017", "blockquote renderer IAL must attach to a blockquote root."))
        if renderer == "callout" and not re.match(r"^>\s+\[![A-Z]+\]", root):
            findings.append(Finding(start + 1, "E018", "callout renderer IAL must attach to a callout root."))
        card_body = "\n".join(lines[max(0, previous):start])
        if attrs.get("custom-dm-card-kind") == "cloze" and "==" not in card_body:
            findings.append(Finding(start + 1, "E019", "cloze cards need an explicit short ==term== target."))
        if attrs.get("custom-dm-card-kind") == "mnemonic":
            if "==" not in card_body:
                findings.append(Finding(start + 1, "E020", "mnemonic cards require a highlighted source-grounded cue."))
            mapping_lines = [line for line in card_body.splitlines() if re.search(r"句|取字|首字|对应|组合|→", line)]
            if mapping_lines and any("==" not in line for line in mapping_lines):
                findings.append(Finding(start + 1, "E021", "Every mnemonic source sentence or mapping line needs an explicit ==highlight==."))
    for number, line in enumerate(lines, start=1):
        if RUNTIME_RE.search(line):
            findings.append(Finding(number, "E014", "Runtime scheduling or Riff field leaked into output."))
    return sorted(findings, key=lambda item: (item.line, item.code, item.message))


def validate_ordinary(text: str) -> list[Finding]:
    findings: list[Finding] = []
    for number, line in enumerate(text.splitlines(), start=1):
        if re.search(r"custom-dm-[\w-]+\s*=|custom-riff-decks\s*=|\b(?:due|interval|suspend|bury)\s*=", line, re.IGNORECASE):
            findings.append(Finding(number, "O001", "Ordinary mode contains formal card or runtime metadata."))
        for tag in re.findall(r"#闪卡/优先级/([^#]+)#", line):
            if tag not in {"P1", "P2", "P3", "P4"}:
                findings.append(Finding(number, "O002", "Flashcard priority tag must be P1, P2, P3, or P4."))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--mode", choices=("ordinary", "dedicated"), default="dedicated")
    args = parser.parse_args()
    text = args.output.read_text(encoding="utf-8")
    findings = validate_ordinary(text) if args.mode == "ordinary" else validate(text)
    if findings:
        for item in findings:
            print(f"{args.output}:{item.line}: {item.code}: {item.message}")
        return 1
    print(f"PASS legal-flashcard {args.mode} validation: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
