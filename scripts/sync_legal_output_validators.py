#!/usr/bin/env python3
"""RETIRED: do not run.

This script once copied ``scripts/legal_note_output_validator.py`` over both
skills' ``validate_output.py``. The two validators legitimately diverged
(2026-09-02: legal-goldquest split into validate_output.py +
legal_goldquest_question_gate.py + legal_marknote_richness_gate.py with its
own gates; legal-marknote keeps marknote-only gates), so a one-shot overwrite
would destroy the current gates. The stale source file stays only for
reference. Skill-to-install-copy deployment is handled by
``sync_installed_skills.py`` instead.
"""

from __future__ import annotations

import sys


def main() -> int:
    print(
        "RETIRED sync_legal_output_validators.py: the two skills' validate_output.py "
        "diverged (goldquest split + E-gates), so overwriting from the stale "
        "scripts/legal_note_output_validator.py is no longer allowed. "
        "Deploy skill files to installed copies with scripts/sync_installed_skills.py.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
