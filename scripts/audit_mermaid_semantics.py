#!/usr/bin/env python3
"""Audit a note tree for perfunctory Mermaid diagrams.

Scans every Markdown file below the given directory, parses each fenced
Mermaid block, and reports blocks that fail `legal_mermaid_semantics_gate`
(E901 isolated keyword pairs, E902 bare keyword chains).  Exits 1 when any
finding is reported so it can guard CI.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from legal_mermaid_semantics_gate import validate_mermaid_semantics


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="Directory tree to audit for perfunctory Mermaid.")
    parser.add_argument("--skip-prefix", action="append", default=["_"], help="Path parts that mark work/junk dirs to skip.")
    args = parser.parse_args()

    findings: list[str] = []
    for path in sorted(args.directory.rglob("*.md")):
        if any(part.startswith(tuple(args.skip_prefix)) for part in path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for finding in validate_mermaid_semantics(text):
            findings.append(f"{path}:{finding.line}: E{finding.code}: {finding.message}")

    for finding in findings:
        print(finding)
    print(f"AUDIT {args.directory}: {len(findings)} perfunctory Mermaid block(s)")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())