#!/usr/bin/env python3
"""Apply same-ID Markdown edits to existing SiYuan blocks through the native CLI."""

from __future__ import annotations

import argparse
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


IAL_RE = re.compile(r"^\s*\{:\s*(?P<attrs>[^{}\r\n]+)\}\s*$")
INLINE_IAL_RE = re.compile(r"\{:\s*(?P<attrs>[^{}\r\n]+)\}")
ATTR_RE = re.compile(r'(?P<name>[A-Za-z][\w-]*)="(?P<value>[^"]*)"')
EDITABLE_BLOCK_ATTRS = {"style"}


class PatchError(RuntimeError):
    pass


@dataclass(frozen=True)
class BlockRecord:
    block_id: str
    line_number: int
    content: str | None
    attrs: tuple[tuple[str, str], ...]


def _id_from_attrs(attrs: str) -> str | None:
    return _parse_attrs(attrs).get("id")


def _parse_attrs(value: str) -> dict[str, str]:
    return {match.group("name"): match.group("value") for match in ATTR_RE.finditer(value)}


def parse_blocks(text: str) -> dict[str, BlockRecord]:
    lines = text.splitlines()
    records: dict[str, BlockRecord] = {}

    def add_record(block_id: str, line_number: int, content: str | None, attrs: dict[str, str]) -> None:
        if block_id in records:
            raise PatchError(f"Duplicate block id {block_id}")
        records[block_id] = BlockRecord(block_id, line_number, content, tuple(sorted(attrs.items())))

    for index, line in enumerate(lines):
        ial = IAL_RE.fullmatch(line)
        if not ial:
            for inline in INLINE_IAL_RE.finditer(line):
                attrs = _parse_attrs(inline.group("attrs"))
                if block_id := attrs.get("id"):
                    add_record(block_id, index + 1, None, attrs)
            continue
        block_id = _id_from_attrs(ial.group("attrs"))
        if not block_id:
            continue
        attrs = _parse_attrs(ial.group("attrs"))
        cursor = index - 1
        while cursor >= 0 and not lines[cursor].strip():
            cursor -= 1
        if cursor < 0:
            raise PatchError(f"IAL with id {block_id} has no preceding block")
        previous = lines[cursor].rstrip()
        if IAL_RE.fullmatch(previous):
            add_record(block_id, index + 1, None, attrs)
            continue
        inline_ids = [
            match
            for match in INLINE_IAL_RE.finditer(previous)
            if _parse_attrs(match.group("attrs")).get("id")
        ]
        if inline_ids:
            content = INLINE_IAL_RE.sub("", previous)
            content = re.sub(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)", "", content).strip()
        else:
            content = previous
        if not content:
            raise PatchError(f"IAL with id {block_id} has an empty block")
        add_record(block_id, cursor + 1, content, attrs)
    return records


def changed_blocks(before: dict[str, BlockRecord], after: dict[str, BlockRecord]) -> list[tuple[BlockRecord, BlockRecord]]:
    if set(before) != set(after):
        missing = sorted(set(before) - set(after))
        added = sorted(set(after) - set(before))
        raise PatchError(f"Block ID set changed; missing={missing}, added={added}. Use explicit insert/delete workflow.")
    changes: list[tuple[BlockRecord, BlockRecord]] = []
    for block_id in before:
        old = before[block_id]
        new = after[block_id]
        old_attrs = dict(old.attrs)
        new_attrs = dict(new.attrs)
        protected_changes = {
            key
            for key in set(old_attrs) | set(new_attrs)
            if key not in EDITABLE_BLOCK_ATTRS and old_attrs.get(key) != new_attrs.get(key)
        }
        if protected_changes:
            raise PatchError(f"Protected attributes changed on {block_id}: {sorted(protected_changes)}")
        if (old.content is None) != (new.content is None):
            raise PatchError(f"Block content role changed on {block_id}; use explicit structural workflow.")
        if old.content != new.content or any(old_attrs.get(key) != new_attrs.get(key) for key in EDITABLE_BLOCK_ATTRS):
            changes.append((old, new))
    return changes


def _run_siyuan(workspace: str, args: Sequence[str], *, dry_run: bool) -> subprocess.CompletedProcess[str]:
    command = ["siyuan", "-w", workspace]
    if dry_run:
        command.append("--dry-run")
    command.extend(args)
    return subprocess.run(command, check=True, text=True, capture_output=True)


def apply_patch(workspace: str, before_path: Path, after_path: Path, *, confirm: bool) -> list[str]:
    before = parse_blocks(before_path.read_text(encoding="utf-8"))
    after = parse_blocks(after_path.read_text(encoding="utf-8"))
    changes = changed_blocks(before, after)
    for old, new in changes:
        if old.content != new.content and new.content is not None:
            _run_siyuan(
                workspace,
                ["block", "update", "--id", old.block_id, "--data", new.content, "--lock-type"],
                dry_run=not confirm,
            )
        old_attrs = dict(old.attrs)
        new_attrs = dict(new.attrs)
        for name in sorted(EDITABLE_BLOCK_ATTRS):
            if old_attrs.get(name) != new_attrs.get(name):
                _run_siyuan(
                    workspace,
                    ["attr", "set", "--id", old.block_id, "--attr", f"{name}={new_attrs.get(name, '')}"],
                    dry_run=not confirm,
                )
    return [old.block_id for old, _ in changes]


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--before", required=True, type=Path)
    parser.add_argument("--after", required=True, type=Path)
    parser.add_argument("--confirm", action="store_true", help="Write through native siyuan CLI; default is dry-run.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        changed = apply_patch(args.workspace, args.before, args.after, confirm=args.confirm)
    except (OSError, PatchError, subprocess.CalledProcessError) as error:
        print(f"ERROR siyuan live patch: {error}")
        return 1
    mode = "applied" if args.confirm else "dry-run"
    print(f"{mode}: {len(changed)} block(s)" + (f" [{', '.join(changed)}]" if changed else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
