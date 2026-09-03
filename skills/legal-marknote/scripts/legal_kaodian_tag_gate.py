#!/usr/bin/env python3
"""Kaodian-tag gate shared by legal-marknote and legal-goldquest validators.

Every MarkNote note-topic provider block and every GoldQuest question heading
must carry one SiYuan native kaodian tag `#法考/…#`, reusing the flashcard
vocabulary snapshot in ../references/kaodian-tags.md verbatim whenever the
考点名 matches. Tags outside a vocabulary snapshot are reported (W823) so they
get confirmed and folded back into that snapshot before delivery.

This module is intentionally self-contained: the two validate_output.py cores
have diverged, so the gate re-declares the few patterns it needs instead of
importing them, and returns findings shaped exactly like the cores' Finding.
"""
# ==========================================================================
# ⛔ 内容会话禁读本源码（用户纪律 2026-09-02）
#    校验器源码不供阅读。判定标准与修法的唯一权威渠道：
#    技能正文 + references/ + 运行本工具得到的真实报错
#    （goldquest 校验器另有 --explain <CODE> 权威词条，如 --explain E630）。
# ==========================================================================

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

IAL_PATTERN = re.compile(r'^\{:\s*(?P<attrs>.+?)\s*\}$')
IAL_ATTRIBUTE_PATTERN = re.compile(r'(?P<key>[\w-]+)="(?P<value>[^"]*)"')
QUESTION_HEADING_PATTERN = re.compile(r"^#####\s+(?!#).+\S\s*$")

KAODIAN_TAG_PATTERN = re.compile(r"#(法考/[^#\s]+)#")
KAODIAN_TAG_ONLY_PATTERN = re.compile(r"^#法考/[^#\s]+#$")
KAODIAN_TAG_HINT_PATTERN = re.compile(r"#法考/")


@dataclass
class Finding:
    level: str
    code: str
    line: int
    message: str

    def render(self, path: Path) -> str:
        return f"{path}:{self.line}: {self.level}{self.code}: {self.message}"


def _vocabulary() -> set[str] | None:
    path = Path(__file__).resolve().parent.parent / "references" / "kaodian-tags.md"
    if not path.exists():
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    return set(re.findall(r"`(法考/[^`]+)`", text))


def _fenced_lines(lines: list[str]) -> set[int]:
    fenced: set[int] = set()
    marker = ""
    for index, line in enumerate(lines, start=1):
        stripped = line.strip()
        content = stripped[2:] if stripped.startswith("> ") else stripped
        if marker:
            fenced.add(index)
            if content.startswith(marker):
                marker = ""
            continue
        if content.startswith("```") or content.startswith("~~~"):
            marker = content[:3]
            fenced.add(index)
    return fenced


def _ial_attrs(line: str) -> dict[str, str]:
    match = IAL_PATTERN.fullmatch(line.strip())
    if not match:
        return {}
    return {item.group("key"): item.group("value") for item in IAL_ATTRIBUTE_PATTERN.finditer(match.group("attrs"))}


def validate_kaodian_tags(text: str, profile: str, require_tags: bool = True) -> list[Finding]:
    findings: list[Finding] = []
    if not require_tags:
        return findings
    lines = text.splitlines()
    fenced = _fenced_lines(lines)

    tag_lines: dict[int, list[str]] = {}
    for index, line in enumerate(lines, start=1):
        for match in KAODIAN_TAG_PATTERN.finditer(line):
            tag_lines.setdefault(index, []).append(match.group(1))

    consumed: set[int] = set()

    if profile == "legal-marknote":
        for index, line in enumerate(lines):
            attrs = _ial_attrs(line)
            if "custom-qb-note-topic-id" not in attrs:
                continue
            line_no = index + 1
            attach_no = index
            if tag_lines.get(attach_no):
                consumed.add(attach_no)
                continue
            lookahead = line_no + 1
            while lookahead <= len(lines) and not lines[lookahead - 1].strip():
                lookahead += 1
            if lookahead <= len(lines) and KAODIAN_TAG_ONLY_PATTERN.fullmatch(lines[lookahead - 1].strip()):
                consumed.add(lookahead)
                continue
            findings.append(Finding("E", "820", line_no, "A note-topic provider block carries no kaodian tag; append #法考/科目/[专题/]考点# to the heading line, or — only for a **考点：显示名** anchor without a heading — add one standalone tag paragraph directly after the IAL line (vocabulary: references/kaodian-tags.md)."))
    elif profile == "legal-goldquest":
        heading_indexes = [index for index, line in enumerate(lines) if QUESTION_HEADING_PATTERN.fullmatch(line)]
        for position, index in enumerate(heading_indexes):
            attrs = _ial_attrs(lines[index + 1]) if index + 1 < len(lines) else {}
            if "custom-qb-id" not in attrs or "custom-qb-question-topic-ids" not in attrs:
                continue
            span_end = heading_indexes[position + 1] if position + 1 < len(heading_indexes) else len(lines)
            solution_line = None
            for probe in range(index + 1, span_end):
                if _ial_attrs(lines[probe]).get("custom-qb-section") == "solution":
                    solution_line = probe
                    break
            if solution_line is None:
                continue
            if tag_lines.get(solution_line):
                consumed.add(solution_line)
                continue
            findings.append(Finding("E", "820", solution_line, "The GoldQuest solution line (正确答案…) carries no kaodian tag; append #法考/科目/[专题/]考点# at the end of that line — the practice view shows only stem/options/solution, and the tag must live where review happens without spoiling the stem (vocabulary: references/kaodian-tags.md)."))

    for line_no, tags in sorted(tag_lines.items()):
        if line_no in fenced:
            findings.append(Finding("E", "822", line_no, "Kaodian tag inside a code fence; tags are SiYuan inline marks and must sit on the GoldQuest solution line (正确答案…), or the MarkNote provider heading / its standalone tag paragraph, never inside fenced content."))
            continue
        if line_no in consumed:
            continue
        if profile == "legal-goldquest":
            findings.append(Finding("E", "822", line_no, "Kaodian tag on an unsupported line; in GoldQuest the only sanctioned position is the end of the 正确答案 solution line — headings, stems, options, and analysis prose stay tag-free."))
        else:
            findings.append(Finding("E", "822", line_no, "Kaodian tag on an unsupported line; only the MarkNote provider heading / its standalone tag paragraph after the provider IAL may carry a tag."))

    for line_no, line in enumerate(lines, start=1):
        if line_no in fenced:
            continue
        if IAL_PATTERN.fullmatch(line.strip()):
            continue
        if KAODIAN_TAG_HINT_PATTERN.search(line) and not KAODIAN_TAG_PATTERN.search(line):
            findings.append(Finding("E", "821", line_no, "Unclosed kaodian tag: '#法考/…' is missing its closing '#' or contains a space; a tag is exactly #法考/科目/[专题/]考点# with no whitespace inside."))

    vocabulary = _vocabulary()
    if vocabulary is not None:
        reported: set[str] = set()
        for line_no, tags in sorted(tag_lines.items()):
            if line_no in fenced:
                continue
            for tag in tags:
                if tag in reported:
                    continue
                reported.add(tag)
                if tag not in vocabulary:
                    findings.append(Finding("W", "823", line_no, f"#{tag}# is not in the flashcard vocabulary snapshot (references/kaodian-tags.md); if this is a genuinely new kaodian, confirm the path with the user, add it to that file, and re-validate — never invent a synonym path for an existing 考点名."))

    return findings
