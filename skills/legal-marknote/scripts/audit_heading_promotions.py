#!/usr/bin/env python3
"""Audit generated Markdown headings and safe promotion of internal labels."""

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
    def key(self) -> tuple[int, str]:
        return self.level, normalize_title(self.title)


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
    return re.sub(r"\s+", " ", title).strip()


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
) -> list[Finding]:
    """Ensure source headings are preserved and additions stay at lower levels."""

    source_headings = parse_headings(source_text)
    output_headings = parse_headings(output_text)
    findings: list[Finding] = []

    source_keys = [heading.key for heading in source_headings]
    output_keys = [heading.key for heading in output_headings]
    output_by_key: dict[tuple[int, str], list[int]] = {}
    for index, key in enumerate(output_keys):
        output_by_key.setdefault(key, []).append(index)

    cursor = 0
    for source_heading in source_headings:
        match_index = next(
            (index for index in output_by_key.get(source_heading.key, []) if index >= cursor),
            None,
        )
        if match_index is None:
            findings.append(
                Finding(
                    "E",
                    "701",
                    source_heading.line,
                    f"Original heading was not preserved: {source_heading.title.strip()}",
                ),
            )
            continue
        cursor = match_index + 1

    source_counts = Counter(source_keys)
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
                Finding("E", "703", 1, f"Original heading count changed for H{key[0]} '{key[1]}': missing {count}.")
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
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_text = args.source.read_text(encoding="utf-8")
    output_text = args.output.read_text(encoding="utf-8")
    findings = audit_heading_promotions(
        source_text,
        output_text,
        minimum_added_level=args.minimum_added_level,
    )
    if args.format == "json":
        print(json.dumps([asdict(finding) for finding in findings], ensure_ascii=False, indent=2))
    elif findings:
        for finding in findings:
            print(f"{args.output}:{finding.line}: {finding.level}{finding.code}: {finding.message}")
    else:
        print(f"PASS heading promotion audit: {args.output}")
    has_errors = any(finding.level == "E" for finding in findings)
    has_warnings = any(finding.level == "W" for finding in findings)
    return 1 if has_errors or (args.strict and has_warnings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
