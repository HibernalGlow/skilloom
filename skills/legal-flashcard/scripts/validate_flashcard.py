#!/usr/bin/env python3
"""Deterministically validate DAMO flashcard Markdown schema 1."""

from __future__ import annotations

import argparse
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

ATTR_RE = re.compile(r'(?P<key>[A-Za-z][\w-]*)="(?P<value>[^"]*)"')
IAL_LINE_RE = re.compile(r'^\{: [A-Za-z][\w-]*="[^"]*"(?: [A-Za-z][\w-]*="[^"]*")*\}$')
CARD_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SOURCE_KEY_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*$")
STYLE_ANCHOR_RE = re.compile(
    r'\*\*[^*\n]+\*\*\{:\s+style="[^"]*(?:color|background-color):\s*var\(--b3-font-(?:color|background)(?:[2-9]|1[0-3])\);?[^"]*"\}'
)
REPORT_RE = re.compile(r"候选\s*(\d+)\D+接受\s*(\d+)\D+拒绝\s*(\d+)")
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
    "custom-qb-note-topic-id",
}
KINDS = {"basic", "cloze", "mnemonic"}
RENDERERS = {"list", "mark", "blockquote", "callout"}


@dataclass(frozen=True)
class Finding:
    line: int
    code: str
    message: str


def parse_ial_blocks(
    lines: list[str],
) -> tuple[list[tuple[int, int, dict[str, str], str, list[str]]], list[Finding]]:
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
            if len(body) != 1:
                findings.append(Finding(start + 1, "E022", "Card IAL must occupy exactly one physical line."))
            if in_fence:
                findings.append(Finding(start + 1, "E008", "Card IAL is inside a code fence."))
            if not raw.rstrip().endswith("}"):
                findings.append(Finding(start + 1, "E001", "Unclosed IAL."))
            if len(body) == 1 and not IAL_LINE_RE.fullmatch(line.strip()):
                findings.append(Finding(start + 1, "E023", "IAL attributes must use one ASCII space and no space before }."))
            matches = list(ATTR_RE.finditer(raw))
            keys = [match.group("key") for match in matches]
            attrs = {match.group("key"): match.group("value") for match in matches}
            for key, count in Counter(keys).items():
                if count > 1:
                    findings.append(Finding(start + 1, "E024", f"Duplicate IAL attribute: {key}."))
            cards.append((start, index, attrs, raw, keys))
        index += 1
    return cards, findings


def _visible_text(text: str) -> str:
    text = re.sub(r'\{:\s*[^}]*\}', "", text)
    text = re.sub(r"[*_=`~<>]", "", text)
    return re.sub(r"\s+", "", text)


def _card_body(lines: list[str], ial_start: int, renderer: str | None) -> tuple[int | None, str]:
    if ial_start == 0 or not lines[ial_start - 1].strip():
        return None, ""
    cursor = ial_start - 1
    if renderer in {"list", "mark"}:
        while cursor >= 0 and lines[cursor].strip() and not lines[cursor].lstrip().startswith("{:"):
            cursor -= 1
        start = cursor + 1
        roots = [index for index in range(start, ial_start) if re.match(r"^-\s+", lines[index])]
        if not roots:
            return None, ""
        root = roots[-1]
        return root, "\n".join(lines[root:ial_start])
    if renderer in {"blockquote", "callout"}:
        while cursor >= 0 and lines[cursor].lstrip().startswith(">"):
            cursor -= 1
        start = cursor + 1
        return (start, "\n".join(lines[start:ial_start])) if start < ial_start else (None, "")
    return ial_start - 1, lines[ial_start - 1]


def validate(
    text: str,
    *,
    require_report: bool = False,
    max_cards_per_topic: int = 4,
    max_answer_items: int = 4,
    max_answer_chars: int = 84,
) -> list[Finding]:
    lines = text.splitlines()
    cards, findings = parse_ial_blocks(lines)
    seen: dict[str, int] = {}
    topic_lines: dict[str, list[int]] = {}
    accepted_card_lines: list[int] = []
    for start, end, attrs, raw, _keys in cards:
        if not any(key.startswith("custom-dm-") for key in attrs):
            continue
        accepted_card_lines.append(start + 1)
        unknown = set(attrs) - ALLOWED
        for key in sorted(unknown):
            findings.append(Finding(start + 1, "E002", f"Unsupported card attribute: {key}."))
        required = {
            "custom-dm-source-key",
            "custom-dm-card-id",
            "custom-dm-card-schema",
            "custom-dm-card-kind",
            "custom-dm-card-renderer",
            "custom-qb-note-topic-id",
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
        topic_id = attrs.get("custom-qb-note-topic-id", "")
        if topic_id and not CARD_ID_RE.fullmatch(topic_id):
            findings.append(Finding(start + 1, "E012", "custom-qb-note-topic-id must be one lowercase ASCII kebab-case ID."))
        elif topic_id:
            topic_lines.setdefault(topic_id, []).append(start + 1)
        if RUNTIME_RE.search(raw) or RUNTIME_RE.search("\n".join(lines[max(0, start - 8): min(len(lines), end + 8)])):
            findings.append(Finding(start + 1, "E014", "Runtime scheduling or Riff fields leaked into the card block."))
        root_index, card_body = _card_body(lines, start, renderer)
        root = lines[root_index].strip() if root_index is not None else ""
        if renderer in {"list", "mark"} and not re.match(r"^-\s+", root):
            findings.append(Finding(start + 1, "E015", "list renderer IAL must attach to a root list item."))
        if renderer == "mark" and "==" not in card_body:
            findings.append(Finding(start + 1, "E016", "mark renderer requires a visible short cloze target."))
        if renderer == "blockquote" and not root.startswith(">"):
            findings.append(Finding(start + 1, "E017", "blockquote renderer IAL must attach to a blockquote root."))
        if renderer == "callout" and not re.match(r"^>\s+\[![A-Z]+\]", root):
            findings.append(Finding(start + 1, "E018", "callout renderer IAL must attach to a callout root."))
        kind = attrs.get("custom-dm-card-kind")
        if kind == "basic":
            if "问题：" not in root:
                findings.append(Finding(start + 1, "E025", "basic cards require a root '- 问题：' item."))
            answer_lines = [line for line in card_body.splitlines() if re.match(r"^\s{4,}-\s+答案：", line)]
            if not answer_lines:
                findings.append(Finding(start + 1, "E026", "basic cards require at least one indented '- 答案：' item."))
            if len(answer_lines) > max_answer_items:
                findings.append(Finding(start + 1, "E027", f"Card has {len(answer_lines)} answer items; split above {max_answer_items}."))
            for answer in answer_lines:
                if len(_visible_text(answer.split("答案：", 1)[1])) > max_answer_chars:
                    findings.append(Finding(start + 1, "E028", f"Answer item exceeds {max_answer_chars} visible characters; split or reject it."))
        if attrs.get("custom-dm-card-kind") == "cloze" and "==" not in card_body:
            findings.append(Finding(start + 1, "E019", "cloze cards need an explicit short ==term== target."))
        if kind != "mnemonic":
            for highlight in re.findall(r"==([^=\n]+)==", card_body):
                if len(_visible_text(highlight)) > 6:
                    findings.append(Finding(start + 1, "E029", "Non-mnemonic highlights must not exceed six visible characters."))
        if attrs.get("custom-dm-card-kind") == "mnemonic":
            if "==" not in card_body:
                findings.append(Finding(start + 1, "E020", "mnemonic cards require a highlighted source-grounded cue."))
            mapping_lines = [line for line in card_body.splitlines() if re.search(r"句|取字|首字|对应|组合|→", line)]
            if mapping_lines and any("==" not in line for line in mapping_lines):
                findings.append(Finding(start + 1, "E021", "Every mnemonic source sentence or mapping line needs an explicit ==highlight==."))
        if not STYLE_ANCHOR_RE.search(card_body):
            findings.append(Finding(start + 1, "E030", "Every accepted card needs a valid MarkNote bold semantic color anchor."))
    for topic_id, locations in topic_lines.items():
        if len(locations) > max_cards_per_topic:
            findings.append(Finding(locations[0], "E013", f"Topic ID {topic_id!r} is reused by {len(locations)} cards; confirm a narrower atomic topic mapping or raise the reviewed limit."))
    if require_report:
        reports = list(REPORT_RE.finditer(text))
        if len(reports) != 1:
            findings.append(Finding(max(1, len(lines)), "E031", "Dedicated output requires exactly one candidate/accepted/rejected report."))
        else:
            candidate, accepted, rejected = (int(value) for value in reports[0].groups())
            if candidate != accepted + rejected or accepted != len(accepted_card_lines):
                line = text[:reports[0].start()].count("\n") + 1
                findings.append(Finding(line, "E032", "Report counts must reconcile and accepted must equal rendered card count."))
    for number, line in enumerate(lines, start=1):
        if RUNTIME_RE.search(line):
            findings.append(Finding(number, "E014", "Runtime scheduling or Riff field leaked into output."))
    return sorted(set(findings), key=lambda item: (item.line, item.code, item.message))


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
    parser.add_argument("--require-report", action="store_true")
    parser.add_argument("--max-cards-per-topic", type=int, default=4)
    parser.add_argument("--max-answer-items", type=int, default=4)
    parser.add_argument("--max-answer-chars", type=int, default=84)
    args = parser.parse_args()
    text = args.output.read_text(encoding="utf-8")
    findings = validate_ordinary(text) if args.mode == "ordinary" else validate(
        text,
        require_report=args.require_report,
        max_cards_per_topic=args.max_cards_per_topic,
        max_answer_items=args.max_answer_items,
        max_answer_chars=args.max_answer_chars,
    )
    if findings:
        for item in findings:
            print(f"{args.output}:{item.line}: {item.code}: {item.message}")
        return 1
    print(f"PASS legal-flashcard {args.mode} validation: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
