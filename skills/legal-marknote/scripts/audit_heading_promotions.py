#!/usr/bin/env python3
"""Audit generated Markdown headings and safe promotion of internal labels."""
# ==========================================================================
# ⛔ 内容会话禁读本源码（用户纪律 2026-09-02）
#    校验器源码不供阅读。判定标准与修法的唯一权威渠道：
#    技能正文 + references/ + 运行本工具得到的真实报错
#    （goldquest 校验器另有 --explain <CODE> 权威词条，如 --explain E630）。
#    打开/grep/sed/脚本方式读取本文件属违规——包括动笔前的预防性阅读，
#    会被看护发现并上报用户。看不懂的报错：原样报告错误码与文本，等用户解释。
# ==========================================================================

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path


HEADING_PATTERN = re.compile(r"^(?P<marks>#{1,6})[ \t]+(?P<title>.*?)[ \t]*#*[ \t]*$")
FENCE_PATTERN = re.compile(r"^\s*(`{3,}|~{3,})")


@dataclass(frozen=True)
class Heading:
    level: int
    title: str
    line: int

    @property
    def key(self) -> str:
        return normalize_title(self.title)


@dataclass(frozen=True)
class Finding:
    level: str
    code: str
    line: int
    message: str


def normalize_title(title: str) -> str:
    """Compare headings by meaning while allowing harmless inline styling."""

    title = re.sub(r"\{:[^}]+\}", "", title)
    title = re.sub(r"!\[([^]]*)\]\([^)]*\)", r"\1", title)
    title = re.sub(r"[`*_~=]", "", title)
    title = re.sub(r"(?<=\d)\s*(?=[\u3400-\u9fff])", " ", title)
    title = re.sub(r"\s+", " ", title).strip()
    return re.sub(r"\s*[:：]\s*$", "", title)


def is_repairable_shell_heading(heading: Heading) -> bool:
    """Recognize only headings whose marker is structural noise, not substance."""

    title = normalize_title(heading.title)
    compact = re.sub(r"\s+", "", title)
    return bool(
        re.fullmatch(r"(?:\d+[.、]?|[（(]?\d+[）)]|[①-⑳])", compact)
        or re.fullmatch(r"例\s*\d+", title)
        or title in {"热点"}
    )


def parse_headings(text: str) -> list[Heading]:
    headings: list[Heading] = []
    in_fence = False
    fence_marker = ""
    for number, line in enumerate(text.splitlines(), start=1):
        fence = FENCE_PATTERN.match(line)
        if fence:
            marker = fence.group(1)
            if not in_fence:
                in_fence = True
                fence_marker = marker[0]
            elif marker[0] == fence_marker:
                in_fence = False
            continue
        if in_fence or line.lstrip().startswith(">"):
            continue
        match = HEADING_PATTERN.match(line)
        if match:
            headings.append(Heading(len(match.group("marks")), match.group("title"), number))
    return headings


def audit_heading_promotions(
    source_text: str,
    output_text: str,
    *,
    minimum_added_level: int = 3,
    allow_structural_repair: bool = False,
) -> list[Finding]:
    """Ensure source headings are preserved and additions stay at lower levels."""

    source_headings = parse_headings(source_text)
    output_headings = parse_headings(output_text)
    findings: list[Finding] = []

    source_keys = [heading.key for heading in source_headings]
    output_keys = [heading.key for heading in output_headings]
    output_by_key: dict[str, list[int]] = {}
    for index, key in enumerate(output_keys):
        output_by_key.setdefault(key, []).append(index)

    cursor = 0
    for source_heading in source_headings:
        match_index = next(
            (index for index in output_by_key.get(source_heading.key, []) if index >= cursor),
            None,
        )
        if match_index is None:
            if allow_structural_repair and is_repairable_shell_heading(source_heading):
                continue
            findings.append(
                Finding(
                    "E",
                    "701",
                    source_heading.line,
                    f"Original heading was not preserved: {source_heading.title.strip()}",
                ),
            )
            continue
        matched_heading = output_headings[match_index]
        if matched_heading.level != source_heading.level and not allow_structural_repair:
            findings.append(
                Finding(
                    "E",
                    "706",
                    matched_heading.line,
                    f"Original heading level changed from H{source_heading.level} to H{matched_heading.level}; rerun with --allow-structural-repair after semantic review.",
                )
            )
        cursor = match_index + 1

    source_counts = Counter(
        heading.key
        for heading in source_headings
        if not (allow_structural_repair and is_repairable_shell_heading(heading))
    )
    remaining = source_counts.copy()
    added_indices: set[int] = set()
    for index, heading in enumerate(output_headings):
        if remaining[heading.key]:
            remaining[heading.key] -= 1
        else:
            added_indices.add(index)
            if heading.level < minimum_added_level:
                findings.append(
                    Finding(
                        "E",
                        "702",
                        heading.line,
                        f"Promoted heading must be level H{minimum_added_level} or lower in the outline; found H{heading.level}.",
                    ),
                )

    for key, count in remaining.items():
        if count:
            findings.append(
                Finding("E", "703", 1, f"Original heading count changed for '{key}': missing {count}.")
            )

    stack: list[Heading] = []
    for index, heading in enumerate(output_headings):
        while stack and stack[-1].level >= heading.level:
            stack.pop()
        if index in added_indices and not stack:
            findings.append(
                Finding("E", "704", heading.line, "Promoted heading has no existing parent heading.")
            )
        if stack and heading.level > stack[-1].level + 1:
            findings.append(
                Finding(
                    "W",
                    "705",
                    heading.line,
                    f"Heading level jumps from H{stack[-1].level} to H{heading.level}; verify the outline parent.",
                )
            )
        stack.append(heading)

    return sorted(findings, key=lambda finding: (finding.line, finding.level != "E", finding.code))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Source Markdown before heading promotion.")
    parser.add_argument("output", type=Path, help="Generated Markdown after heading promotion.")
    parser.add_argument(
        "--minimum-added-level",
        type=int,
        default=3,
        choices=range(2, 7),
        help="Lowest allowed level for added headings; defaults to H3 so an H2 topic may gain H3 classifications.",
    )
    parser.add_argument("--strict", action="store_true", help="Treat outline warnings as failures.")
    parser.add_argument(
        "--allow-structural-repair",
        action="store_true",
        help="Allow removal of recognized numeric/example/empty shell headings while preserving substantive headings.",
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--all", action="store_true", help="Print every finding instead of the bounded default report.")
    parser.add_argument("--max-report", type=int, default=40, help="Text-report cap (default 40); --all lifts the cap. JSON output is never capped.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_text = args.source.read_text(encoding="utf-8")
    output_text = args.output.read_text(encoding="utf-8")
    findings = audit_heading_promotions(
        source_text,
        output_text,
        minimum_added_level=args.minimum_added_level,
        allow_structural_repair=args.allow_structural_repair,
    )
    if args.format == "json":
        print(json.dumps([asdict(finding) for finding in findings], ensure_ascii=False, indent=2))
    elif findings:
        error_count = sum(finding.level == "E" for finding in findings)
        warning_count = sum(finding.level == "W" for finding in findings)
        shown = findings if args.all else findings[: max(0, args.max_report)]
        for finding in shown:
            print(f"{args.output}:{finding.line}: {finding.level}{finding.code}: {finding.message}")
        hidden = len(findings) - len(shown)
        if hidden > 0:
            print(f"... {hidden} more finding(s) not shown of {len(findings)} total [E:{error_count} W:{warning_count}]. Lift the cap with --all or raise --max-report; --format json dumps everything.")
        print(f"SUMMARY {args.output} [E:{error_count} W:{warning_count}]: {len(findings)} finding(s)")
    else:
        print(f"PASS heading promotion audit: {args.output}")
    has_errors = any(finding.level == "E" for finding in findings)
    has_warnings = any(finding.level == "W" for finding in findings)
    return 1 if has_errors or (args.strict and has_warnings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
