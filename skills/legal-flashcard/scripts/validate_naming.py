#!/usr/bin/env python3
"""Validate a flashcard file's source-derived name, location, and first heading."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

FLASH_MARKER_RE = re.compile(r"(?:闪卡|flash[- ]?cards?)", re.IGNORECASE)
TITLE_MARKER = "⚡"
HEADING_RE = re.compile(r"^(?P<marks>#{1,6})\s+(?P<title>.+?)\s*$")
H1_RE = re.compile(r"^#\s+(?P<title>.+?)\s*$")


def first_heading(text: str) -> tuple[int, str] | None:
    for line in text.splitlines():
        match = HEADING_RE.match(line)
        if match and match.group("title").strip():
            return len(match.group("marks")), match.group("title").strip()
    return None


def expected_stem(source: Path) -> str:
    stem = source.stem
    return stem if FLASH_MARKER_RE.search(stem) else f"{stem}-闪卡"


def output_title_stem(output: Path) -> str:
    title = re.sub(r"(?:[- ·]?闪卡|[- ]?flash[- ]?cards?)$", "", output.stem, flags=re.IGNORECASE)
    title = title.removeprefix(TITLE_MARKER).lstrip()
    return f"{TITLE_MARKER}{title}"


def validate(output: Path, source: Path) -> list[str]:
    findings: list[str] = []
    if output.parent == source.parent:
        findings.append("N002 placement-mismatch: output must be in a dedicated sibling flashcard directory.")
    if not FLASH_MARKER_RE.search(output.parent.name):
        findings.append("N003 placement-mismatch: destination directory does not identify a flashcard collection.")
    expected_name = f"{expected_stem(source)}{source.suffix}"
    if output.name != expected_name:
        findings.append(f"N001 filename-mismatch: expected {expected_name!r}, observed {output.name!r}.")
    source_heading = first_heading(source.read_text(encoding="utf-8"))
    output_text = output.read_text(encoding="utf-8")
    output_heading = H1_RE.match(output_text.splitlines()[0]) if output_text.splitlines() else None
    if output_heading is None:
        code = "N004 fallback-title" if source_heading is None else "N005 title-mismatch"
        findings.append(f"{code}: output must start with a source-derived H1 prefixed by {TITLE_MARKER!r}.")
    else:
        title = output_title_stem(output)
        if output_heading.group("title").strip() != title:
            findings.append(
                f"N005 title-mismatch: expected H1 {title!r}, observed {output_heading.group('title').strip()!r}."
            )
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--source", required=True, type=Path)
    args = parser.parse_args()
    findings = validate(args.output, args.source)
    if findings:
        for finding in findings:
            print(f"{args.output}: {finding}")
        return 1
    print(f"PASS legal-flashcard naming validation: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
