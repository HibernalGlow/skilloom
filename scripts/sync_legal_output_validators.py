#!/usr/bin/env python3
"""Synchronize the self-contained legal output validators into both skills."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts" / "legal_note_output_validator.py"
TARGETS = (
    ROOT / "skills" / "legal-marknote" / "scripts" / "validate_output.py",
    ROOT / "skills" / "legal-goldquest" / "scripts" / "validate_output.py",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Report stale or missing copies without writing them.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_bytes = SOURCE.read_bytes()
    stale = [target for target in TARGETS if not target.is_file() or target.read_bytes() != source_bytes]
    if args.check:
        for target in stale:
            print(f"STALE {target.relative_to(ROOT)}")
        if stale:
            print("Run: python -X utf8 scripts/sync_legal_output_validators.py")
            return 1
        print("PASS legal output validator copies are synchronized.")
        return 0
    for target in stale:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SOURCE, target)
        print(f"SYNC {target.relative_to(ROOT)}")
    if not stale:
        print("PASS legal output validator copies already synchronized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
