#!/usr/bin/env python3
"""Run the complete repository gate for legal-study skills and output validators."""

from __future__ import annotations

import py_compile
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = (
    ROOT / "scripts" / "legal_note_output_validator.py",
    ROOT / "skills" / "legal-marknote" / "scripts" / "validate_output.py",
    ROOT / "skills" / "legal-goldquest" / "scripts" / "validate_output.py",
)


def run(arguments: list[str]) -> None:
    result = subprocess.run(arguments, cwd=ROOT, text=True)
    if result.returncode:
        raise SystemExit(result.returncode)


def main() -> int:
    for script in SCRIPTS:
        py_compile.compile(str(script), doraise=True)
    run([sys.executable, "-X", "utf8", "scripts/sync_legal_output_validators.py", "--check"])
    run(
        [
            sys.executable,
            "-X",
            "utf8",
            "-m",
            "unittest",
            "discover",
            "-s",
            "scripts",
            "-p",
            "test_legal_note_output_validator.py",
        ],
    )

    contract_command = [sys.executable, "-X", "utf8", "scripts/validate_legal_skills.py"]
    quick_validator = Path.home() / ".codex" / "skills" / ".system" / "skill-creator" / "scripts" / "quick_validate.py"
    if quick_validator.is_file():
        contract_command.extend(["--quick-validator", str(quick_validator)])
    run(contract_command)
    print("PASS complete legal skill gate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
