#!/usr/bin/env python3
"""Gate question references so they resolve to leaf topic providers."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


ATTR_RE = re.compile(r'([A-Za-z0-9_-]+)="([^"]*)"')
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


@dataclass(frozen=True)
class Finding:
    level: str
    code: str
    path: Path
    line: int
    message: str

    def render(self) -> str:
        return f"{self.path}:{self.line}: {self.level}{self.code}: {self.message}"


def attrs(line: str) -> dict[str, str]:
    return dict(ATTR_RE.findall(line))


def topic_ids(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


def collect(paths: Sequence[Path]) -> list[Path]:
    files: set[Path] = set()
    for path in paths:
        if path.is_file() and path.suffix.lower() == ".md":
            files.add(path.resolve())
        elif path.is_dir():
            files.update(item.resolve() for item in path.rglob("*.md") if item.is_file())
    return sorted(files, key=lambda item: str(item).lower())


def audit(paths: Sequence[Path]) -> list[Finding]:
    providers: dict[str, tuple[Path, int]] = {}
    children: dict[str, set[str]] = {}
    questions: list[tuple[Path, int, list[str], str | None]] = []
    findings: list[Finding] = []

    for path in collect(paths):
        lines = path.read_text(encoding="utf-8-sig").splitlines()
        for index, line in enumerate(lines):
            current = attrs(line)
            if not current:
                continue
            line_no = index + 1
            provider = current.get("custom-qb-note-topic-id")
            parent = current.get("custom-qb-note-topic-parent-id")
            if provider is not None:
                if len(topic_ids(provider)) != 1 or not ID_RE.fullmatch(provider.strip()):
                    findings.append(Finding("E", "301", path, line_no, "Provider topic ID must be one lowercase ASCII kebab-case ID."))
                else:
                    provider_id = provider.strip()
                    if provider_id in providers:
                        findings.append(Finding("E", "302", path, line_no, f"Duplicate provider topic ID: {provider_id}."))
                    providers.setdefault(provider_id, (path, line_no))
                    if parent is not None:
                        parent_id = parent.strip()
                        if not ID_RE.fullmatch(parent_id):
                            findings.append(Finding("E", "303", path, line_no, "custom-qb-note-topic-parent-id must be lowercase ASCII kebab-case."))
                        elif parent_id == provider_id:
                            findings.append(Finding("E", "304", path, line_no, "A topic cannot be its own parent."))
                        else:
                            children.setdefault(parent_id, set()).add(provider_id)
            elif parent is not None:
                findings.append(Finding("E", "305", path, line_no, "custom-qb-note-topic-parent-id requires custom-qb-note-topic-id on the same IAL."))

            question_id = current.get("custom-qb-id")
            if question_id is not None:
                questions.append((path, line_no, topic_ids(current.get("custom-qb-question-topic-ids", "")), current.get("custom-qb-topic-granularity-exception")))

    for path, line_no, topics, exception in questions:
        if exception is not None and not exception.strip():
            findings.append(Finding("E", "306", path, line_no, "Granularity exception requires a specific non-empty reason."))
        broad = sorted(topic for topic in topics if topic in children)
        if broad and not (exception and exception.strip()):
            details = ", ".join(f"{topic} -> {', '.join(sorted(children[topic]))}" for topic in broad)
            findings.append(Finding("E", "307", path, line_no, f"Question references non-leaf topic(s): {details}. Use the finest child topic IDs or declare a justified exception."))

    for parent, child_ids in children.items():
        if parent not in providers:
            location = next((item for item in paths if item.is_file()), Path("<input>"))
            findings.append(Finding("E", "308", location, 1, f"Parent topic provider is missing: {parent} (children: {', '.join(sorted(child_ids))})."))
    return sorted(findings, key=lambda item: (str(item.path).lower(), item.line, item.code))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path, help="Markdown files or directories to scan recursively.")
    parser.add_argument("--strict", action="store_true", help="Treat all findings as blocking (reserved for gate parity).")
    args = parser.parse_args(argv)
    missing = [str(path) for path in args.paths if not path.exists()]
    if missing:
        print(f"Input paths do not exist: {', '.join(missing)}", file=sys.stderr)
        return 2
    files = collect(args.paths)
    if not files:
        print("No Markdown files found.", file=sys.stderr)
        return 2
    findings = audit(args.paths)
    for finding in findings:
        print(finding.render())
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
