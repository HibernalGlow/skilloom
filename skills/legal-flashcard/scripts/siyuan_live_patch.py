#!/usr/bin/env python3
"""Apply an adaptive Markdown revision to a live SiYuan document.

Existing blocks are patched by ID. Structural changes are rebuilt in one
document update only after special identities have been checked.
"""

from __future__ import annotations

import argparse
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

IAL_RE = re.compile(r"^\s*\{:\s*(?P<attrs>[^{}\r\n]+)\}\s*$")
INLINE_IAL_RE = re.compile(r"\{:\s*(?P<attrs>[^{}\r\n]+)\}")
ATTR_RE = re.compile(r'(?P<name>[A-Za-z][\w-]*)="(?P<value>[^"]*)"')
INFRA_ATTRS = {"id", "updated", "type", "title"}
IDENTITY_ATTRS = {"id", "type", "title"}
SPECIAL_ATTR_RE = re.compile(
    r"(?:^custom-|^riff|^av-|^database|^ref|^memo$|^bookmark$|^due$|^interval$|^review|^suspend$|^bury$)",
    re.IGNORECASE,
)


class PatchError(RuntimeError):
    pass


@dataclass(frozen=True)
class BlockRecord:
    block_id: str
    line_number: int
    content: str | None
    attrs: tuple[tuple[str, str], ...]


def _parse_attrs(value: str) -> dict[str, str]:
    return {match.group("name"): match.group("value") for match in ATTR_RE.finditer(value)}


def _id_from_attrs(attrs: str) -> str | None:
    return _parse_attrs(attrs).get("id")


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
            match for match in INLINE_IAL_RE.finditer(previous) if _parse_attrs(match.group("attrs")).get("id")
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


def _unbound_content_lines(text: str) -> list[int]:
    """Find non-empty Markdown lines without a following full-IAl owner.

    Full `--ial all` exports have one IAL per block.  A line left without one
    is therefore a newly created ordinary block and must use the rebuild path.
    """

    lines = text.splitlines()
    consumed: set[int] = set()
    for index, line in enumerate(lines):
        if not IAL_RE.fullmatch(line):
            continue
        cursor = index - 1
        while cursor >= 0 and not lines[cursor].strip():
            cursor -= 1
        if cursor >= 0 and not IAL_RE.fullmatch(lines[cursor]):
            consumed.add(cursor)
    return [index + 1 for index, line in enumerate(lines) if line.strip() and index not in consumed and not IAL_RE.fullmatch(line)]


def special_reasons(attrs: dict[str, str]) -> tuple[str, ...]:
    reasons: list[str] = []
    for name in attrs:
        if name in INFRA_ATTRS or not SPECIAL_ATTR_RE.search(name):
            continue
        if name == "custom-dm-card-id":
            reasons.append("flashcard")
        elif name.startswith("custom-qb-"):
            reasons.append("topic-binding")
        elif name.startswith(("ref", "memo")):
            reasons.append("reference")
        elif name.startswith(("av-", "database")):
            reasons.append("database")
        else:
            reasons.append(name)
    return tuple(sorted(set(reasons)))


def special_ids(records: dict[str, BlockRecord]) -> dict[str, tuple[str, ...]]:
    return {
        block_id: reasons
        for block_id, record in records.items()
        if (reasons := special_reasons(dict(record.attrs)))
    }


def _protected_changes(
    before: dict[str, BlockRecord], after: dict[str, BlockRecord], protected: set[str]
) -> dict[str, list[str]]:
    changes: dict[str, list[str]] = {}
    for block_id in sorted(set(before) & set(after)):
        old = dict(before[block_id].attrs)
        new = dict(after[block_id].attrs)
        names = sorted(name for name in protected if old.get(name) != new.get(name))
        if names:
            changes[block_id] = names
    return changes


def changed_blocks(
    before: dict[str, BlockRecord],
    after: dict[str, BlockRecord],
    *,
    protected_attrs: Iterable[str] = (),
) -> list[tuple[BlockRecord, BlockRecord]]:
    """Return same-ID edits; structural changes belong to the adaptive planner."""

    if set(before) != set(after):
        missing = sorted(set(before) - set(after))
        added = sorted(set(after) - set(before))
        raise PatchError(f"Block ID set changed; missing={missing}, added={added}. Use adaptive structural workflow.")
    protected = set(protected_attrs) | IDENTITY_ATTRS
    violations = _protected_changes(before, after, protected)
    if violations:
        details = "; ".join(f"{block_id}: {names}" for block_id, names in violations.items())
        raise PatchError(f"Protected attributes changed: {details}")
    changes: list[tuple[BlockRecord, BlockRecord]] = []
    for block_id in before:
        old = before[block_id]
        new = after[block_id]
        if (old.content is None) != (new.content is None):
            raise PatchError(f"Block content role changed on {block_id}; use adaptive structural workflow.")
        old_attrs = dict(old.attrs)
        new_attrs = dict(new.attrs)
        editable_changed = any(
            old_attrs.get(name) != new_attrs.get(name)
            for name in set(old_attrs) | set(new_attrs)
            if name not in INFRA_ATTRS
        )
        if old.content != new.content or editable_changed:
            changes.append((old, new))
    return changes


def _run_siyuan(workspace: str, args: Sequence[str], *, dry_run: bool) -> subprocess.CompletedProcess[str]:
    command = ["siyuan", "-w", workspace]
    if dry_run:
        command.append("--dry-run")
    command.extend(args)
    return subprocess.run(command, check=True, text=True, capture_output=True)


def _document_root(records: dict[str, BlockRecord]) -> str:
    roots = [block_id for block_id, record in records.items() if dict(record.attrs).get("type") == "doc"]
    if len(roots) != 1:
        raise PatchError(f"Expected one document root with type=doc, found {roots}")
    return roots[0]


def format_plan(
    before_path: Path,
    after_path: Path,
    *,
    special_ids_override: Iterable[str] = (),
) -> list[str]:
    """Return a compact, auditable description without invoking SiYuan."""

    before_text = before_path.read_text(encoding="utf-8")
    after_text = after_path.read_text(encoding="utf-8")
    before = parse_blocks(before_text)
    after = parse_blocks(after_text)
    structural = set(before) != set(after) or bool(_unbound_content_lines(after_text))
    if not structural:
        changes = changed_blocks(before, after)
        if not changes:
            return ["plan: no changes"]
        lines = [f"plan: same-id patch ({len(changes)} block(s))"]
        for old, new in changes:
            old_attrs = dict(old.attrs)
            new_attrs = dict(new.attrs)
            attrs = sorted(
                name for name in set(old_attrs) | set(new_attrs)
                if name not in INFRA_ATTRS and old_attrs.get(name) != new_attrs.get(name)
            )
            suffix = f" attrs={','.join(attrs)}" if attrs else ""
            lines.append(f"  change {old.block_id}{suffix}")
        return lines
    old_special = special_ids(before)
    old_special.update({block_id: ("explicit",) for block_id in special_ids_override if block_id in before})
    missing = sorted(set(before) - set(after))
    added = sorted(set(after) - set(before))
    ordinary_deleted = [block_id for block_id in missing if block_id not in old_special]
    special_deleted = [block_id for block_id in missing if block_id in old_special]
    ordinary_added = [block_id for block_id in added if block_id not in special_ids(after)]
    lines = ["plan: document rebuild", f"  ordinary-deleted: {len(ordinary_deleted)}", f"  ordinary-added-with-id: {len(ordinary_added)}"]
    lines.append(f"  idless-new-block-lines: {len(_unbound_content_lines(after_text))}")
    lines.append(f"  special-preserved: {len(set(old_special) & set(after))}")
    if special_deleted:
        lines.append(f"  special-deleted: {','.join(special_deleted)}")
    if ordinary_deleted:
        lines.append(f"  ordinary-deleted-ids: {','.join(ordinary_deleted)}")
    return lines


def _apply_same_ids(
    workspace: str,
    changes: list[tuple[BlockRecord, BlockRecord]],
    *,
    confirm: bool,
) -> list[str]:
    changed: list[str] = []
    for old, new in changes:
        if old.content != new.content and new.content is not None:
            _run_siyuan(
                workspace,
                ["block", "update", "--id", old.block_id, "--data", new.content],
                dry_run=not confirm,
            )
        old_attrs = dict(old.attrs)
        new_attrs = dict(new.attrs)
        for name in sorted((set(old_attrs) | set(new_attrs)) - INFRA_ATTRS):
            if old_attrs.get(name) != new_attrs.get(name):
                _run_siyuan(
                    workspace,
                    ["attr", "set", "--id", old.block_id, "--attr", f"{name}={new_attrs.get(name, '')}"],
                    dry_run=not confirm,
                )
        changed.append(old.block_id)
    return changed


def apply_patch(
    workspace: str,
    before_path: Path,
    after_path: Path,
    *,
    confirm: bool,
    protect_attrs: Iterable[str] = (),
    protect_custom_attrs: bool = False,
    allow_delete_special: Iterable[str] = (),
    special_ids_override: Iterable[str] = (),
) -> list[str]:
    before_text = before_path.read_text(encoding="utf-8")
    after_text = after_path.read_text(encoding="utf-8")
    before = parse_blocks(before_text)
    after = parse_blocks(after_text)
    protected = set(protect_attrs)
    if protect_custom_attrs:
        protected.update(name for record in before.values() for name, _ in record.attrs if name.startswith("custom-"))
    violations = _protected_changes(before, after, protected | IDENTITY_ATTRS)
    if violations:
        details = "; ".join(f"{block_id}: {names}" for block_id, names in violations.items())
        raise PatchError(f"Protected attributes changed: {details}")

    structural_change = set(before) != set(after) or bool(_unbound_content_lines(after_text))
    if not structural_change:
        return _apply_same_ids(workspace, changed_blocks(before, after, protected_attrs=protected), confirm=confirm)

    old_special = special_ids(before)
    for block_id in special_ids_override:
        if block_id in before:
            old_special.setdefault(block_id, ("explicit",))
    root_id = _document_root(before)
    if root_id not in after:
        raise PatchError(f"Document root id {root_id} is missing from after.md")
    missing_special = sorted(set(old_special) - set(after))
    allowed_deletes = set(allow_delete_special)
    unauthorized = [block_id for block_id in missing_special if block_id not in allowed_deletes]
    if unauthorized:
        details = ", ".join(f"{block_id} ({', '.join(old_special[block_id])})" for block_id in unauthorized)
        raise PatchError(
            "Structural rebuild would delete special block(s): " + details
            + ". Keep their id IALs or pass --allow-delete-special explicitly."
        )

    invented_ids = sorted(set(after) - set(before))
    if invented_ids:
        raise PatchError(
            "after.md contains IDs absent from before.md: " + ", ".join(invented_ids)
            + ". Leave IDs off newly created blocks so SiYuan allocates them."
        )

    _run_siyuan(
        workspace,
        ["block", "update", "--id", root_id, "--file", str(after_path)],
        dry_run=not confirm,
    )
    return [root_id]


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--before", required=True, type=Path)
    parser.add_argument("--after", required=True, type=Path)
    parser.add_argument("--protect-attr", action="append", default=[], dest="protect_attrs")
    parser.add_argument("--protect-custom-attrs", action="store_true")
    parser.add_argument("--allow-delete-special", action="append", default=[])
    parser.add_argument("--special-id", action="append", default=[], dest="special_ids")
    parser.add_argument("--confirm", action="store_true", help="Write through native siyuan CLI; default is dry-run.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        for line in format_plan(args.before, args.after, special_ids_override=args.special_ids):
            print(line)
        changed = apply_patch(
            args.workspace,
            args.before,
            args.after,
            confirm=args.confirm,
            protect_attrs=args.protect_attrs,
            protect_custom_attrs=args.protect_custom_attrs,
            allow_delete_special=args.allow_delete_special,
            special_ids_override=args.special_ids,
        )
    except (OSError, PatchError, subprocess.CalledProcessError) as error:
        print(f"ERROR siyuan live patch: {error}")
        return 1
    mode = "applied" if args.confirm else "dry-run"
    print(f"{mode}: {len(changed)} operation(s)" + (f" [{', '.join(changed)}]" if changed else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
