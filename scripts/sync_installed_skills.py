#!/usr/bin/env python3
"""Deploy skilloom skills to the installed skill directories agents read.

skilloom is the canonical source; ``~/.agents/skills`` (the default skill
read location) and ``~/.zcode/skills`` are deployment targets that do not
update themselves. Run this after editing any skill's SKILL.md, references,
or scripts. Copying is byte-compared, so unchanged files are never touched
and concurrent-session mtimes stay meaningful.
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JUNK = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".DS_Store"}
SUFFIX_JUNK = {".pyc", ".pyo"}


def source_skills() -> list[Path]:
    return sorted(path for path in (ROOT / "skills").iterdir() if (path / "SKILL.md").is_file())


def payload_files(skill_dir: Path) -> list[Path]:
    files = [
        path
        for path in skill_dir.rglob("*")
        if path.is_file()
        and not any(part in JUNK for part in path.parts)
        and path.suffix not in SUFFIX_JUNK
    ]
    return sorted(files, key=lambda path: path.relative_to(skill_dir).as_posix())


def plan_skill(source: Path, target: Path, *, prune: bool) -> list[tuple[str, str]]:
    """Return (action, relative-path) actions needed to sync target to source."""
    actions: list[tuple[str, str]] = []
    for path in payload_files(source):
        relative = path.relative_to(source).as_posix()
        destination = target / relative
        if destination.is_file() and destination.read_bytes() == path.read_bytes():
            continue
        actions.append(("NEW" if not destination.is_file() else "COPY", relative))
    if prune:
        for path in payload_files(target):
            relative = path.relative_to(target).as_posix()
            if not (source / relative).is_file():
                actions.append(("PRUNE", relative))
    return actions


def apply_actions(target: Path, actions: list[tuple[str, str]], source: Path) -> None:
    for action, relative in actions:
        if action == "PRUNE":
            (target / relative).unlink()
            continue
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / relative, destination)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Report pending changes without writing.")
    parser.add_argument("--create", action="store_true", help="Also create installed copies for skills that have none yet.")
    parser.add_argument("--skill", action="append", default=[], metavar="NAME", help="Restrict to these skills (repeatable).")
    parser.add_argument("--prune", action="store_true", help="Delete files in installed skill copies that no longer exist in skilloom.")
    args = parser.parse_args()

    wanted = set(args.skill)
    install_roots = [Path.home() / ".agents" / "skills", Path.home() / ".zcode" / "skills"]
    pending = 0
    for source in source_skills():
        if wanted and source.name not in wanted:
            continue
        for root in install_roots:
            target = root / source.name
            if not target.is_dir():
                if args.create:
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    print(f"MISSING {root.parent.name}/{source.name} (pass --create to seed it)")
                    continue
            actions = plan_skill(source, target, prune=args.prune)
            if not actions:
                continue
            pending += len(actions)
            for action, relative in actions:
                if args.check:
                    print(f"PENDING {source.name}/{root.parent.name} {action} {relative}")
                else:
                    apply_actions(target, [(action, relative)], source)
                    print(f"SYNC {source.name}/{root.parent.name} {action} {relative}")
            if not args.check:
                print(f"OK {source.name} -> {root.parent.name}: {len(actions)} file(s)")
    if args.check:
        if pending:
            print(f"{pending} change(s) pending; run without --check to apply.")
            return 1
        print("PASS all installed skill copies match skilloom.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
