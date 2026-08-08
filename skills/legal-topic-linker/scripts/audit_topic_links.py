#!/usr/bin/env python3
"""Inventory legal-question topic references and note providers in Markdown."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence


ATTR_RE = re.compile(r'([A-Za-z0-9_-]+)="([^"]*)"')
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


@dataclass(frozen=True)
class Location:
    path: str
    line: int
    label: str


@dataclass(frozen=True)
class Question:
    question_id: str
    topics: tuple[str, ...]
    location: Location


@dataclass(frozen=True)
class Provider:
    topic_id: str
    location: Location


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str
    location: Location | None = None


def parse_attributes(line: str) -> dict[str, str]:
    return dict(ATTR_RE.findall(line))


def split_topic_ids(raw: str) -> tuple[str, ...]:
    return tuple(part.strip() for part in raw.split(",") if part.strip())


def preceding_label(lines: Sequence[str], ial_index: int) -> str:
    for index in range(ial_index - 1, -1, -1):
        candidate = lines[index].strip()
        if candidate:
            return candidate[:180]
    return "<document-start>"


def scan_markdown(path: Path) -> tuple[list[Question], list[Provider], list[Finding]]:
    text = path.read_text(encoding="utf-8-sig")
    lines = text.splitlines()
    questions: list[Question] = []
    providers: list[Provider] = []
    findings: list[Finding] = []

    for index, line in enumerate(lines):
        if "custom-qb-" not in line:
            continue
        attrs = parse_attributes(line)
        if not attrs:
            continue
        location = Location(str(path), index + 1, preceding_label(lines, index))
        is_question = "custom-qb-id" in attrs

        if is_question:
            question_id = attrs["custom-qb-id"].strip()
            topics = split_topic_ids(attrs.get("custom-qb-question-topic-ids", ""))
            questions.append(Question(question_id, topics, location))

            if not question_id:
                findings.append(Finding("error", "empty-question-id", "Question has an empty custom-qb-id.", location))
            elif not ID_RE.fullmatch(question_id):
                findings.append(Finding("error", "invalid-question-id", f"Invalid question ID: {question_id}", location))

            if not topics:
                findings.append(Finding("error", "missing-question-topics", "Question has no custom-qb-question-topic-ids.", location))
            for topic in topics:
                if not ID_RE.fullmatch(topic):
                    findings.append(Finding("error", "invalid-question-topic", f"Invalid question topic ID: {topic}", location))
            duplicates = sorted(topic for topic, count in Counter(topics).items() if count > 1)
            if duplicates:
                findings.append(Finding("error", "duplicate-question-topic", f"Question repeats topic IDs: {', '.join(duplicates)}", location))

            if "custom-qb-note-topic-id" in attrs:
                findings.append(Finding("error", "mixed-topic-directions", "Question IAL also declares custom-qb-note-topic-id.", location))
        elif "custom-qb-question-topic-ids" in attrs:
            findings.append(Finding("error", "orphan-question-topics", "custom-qb-question-topic-ids requires custom-qb-id on the same IAL.", location))

        if "custom-qb-note-topic-id" in attrs and not is_question:
            raw_provider = attrs["custom-qb-note-topic-id"].strip()
            provider_topics = split_topic_ids(raw_provider)
            if len(provider_topics) != 1 or not ID_RE.fullmatch(provider_topics[0]):
                findings.append(Finding("error", "invalid-provider-topic", f"Provider requires exactly one valid topic ID: {raw_provider or '<empty>'}", location))
            else:
                providers.append(Provider(provider_topics[0], location))

    return questions, providers, findings


def collect_markdown(inputs: Sequence[Path]) -> list[Path]:
    files: set[Path] = set()
    for input_path in inputs:
        if input_path.is_file():
            if input_path.suffix.lower() == ".md":
                files.add(input_path.resolve())
            continue
        if input_path.is_dir():
            files.update(path.resolve() for path in input_path.rglob("*.md") if path.is_file())
    return sorted(files, key=lambda path: str(path).lower())


def build_report(paths: Sequence[Path], fanout_threshold: int = 8) -> dict[str, object]:
    questions: list[Question] = []
    providers: list[Provider] = []
    findings: list[Finding] = []

    for path in paths:
        file_questions, file_providers, file_findings = scan_markdown(path)
        questions.extend(file_questions)
        providers.extend(file_providers)
        findings.extend(file_findings)

    question_ids: dict[str, list[Location]] = defaultdict(list)
    question_uses: dict[str, list[Location]] = defaultdict(list)
    provider_uses: dict[str, list[Location]] = defaultdict(list)

    for question in questions:
        question_ids[question.question_id].append(question.location)
        for topic in dict.fromkeys(question.topics):
            if ID_RE.fullmatch(topic):
                question_uses[topic].append(question.location)
    for provider in providers:
        provider_uses[provider.topic_id].append(provider.location)

    for question_id, locations in sorted(question_ids.items()):
        if question_id and len(locations) > 1:
            for location in locations:
                findings.append(Finding("error", "duplicate-question-id", f"Question ID appears {len(locations)} times: {question_id}", location))

    for topic, locations in sorted(question_uses.items()):
        if topic not in provider_uses:
            findings.append(Finding("warning", "topic-without-provider", f"Question topic has no note provider: {topic}", locations[0]))
        if len(locations) >= fanout_threshold:
            findings.append(Finding("warning", "high-fanout-topic", f"Topic is used by {len(locations)} questions; review whether it is too broad: {topic}", locations[0]))

    for topic, locations in sorted(provider_uses.items()):
        if topic not in question_uses:
            findings.append(Finding("info", "provider-without-question", f"Provider topic is not referenced by an in-scope question: {topic}", locations[0]))

    severity_order = {"error": 0, "warning": 1, "info": 2}
    findings.sort(key=lambda item: (severity_order[item.severity], item.code, item.location.path if item.location else "", item.location.line if item.location else 0))

    return {
        "summary": {
            "files": len(paths),
            "questions": len(questions),
            "question_topics": len(question_uses),
            "provider_blocks": len(providers),
            "provider_topics": len(provider_uses),
            "errors": sum(item.severity == "error" for item in findings),
            "warnings": sum(item.severity == "warning" for item in findings),
            "info": sum(item.severity == "info" for item in findings),
        },
        "questions": [asdict(item) for item in questions],
        "providers": [asdict(item) for item in providers],
        "topic_index": {
            topic: {
                "question_count": len(question_uses.get(topic, [])),
                "provider_count": len(provider_uses.get(topic, [])),
                "questions": [asdict(location) for location in question_uses.get(topic, [])],
                "providers": [asdict(location) for location in provider_uses.get(topic, [])],
            }
            for topic in sorted(set(question_uses) | set(provider_uses))
        },
        "findings": [asdict(item) for item in findings],
    }


def format_text(report: dict[str, object]) -> str:
    summary = report["summary"]
    assert isinstance(summary, dict)
    lines = [
        "Legal topic link audit",
        (
            f"files={summary['files']} questions={summary['questions']} "
            f"question_topics={summary['question_topics']} provider_blocks={summary['provider_blocks']} "
            f"provider_topics={summary['provider_topics']} errors={summary['errors']} "
            f"warnings={summary['warnings']} info={summary['info']}"
        ),
    ]
    findings = report["findings"]
    assert isinstance(findings, list)
    if not findings:
        lines.append("No structural relationship findings.")
        return "\n".join(lines)

    lines.append("")
    for finding in findings:
        assert isinstance(finding, dict)
        location = finding.get("location")
        where = ""
        if isinstance(location, dict):
            where = f" {location['path']}:{location['line']}"
        lines.append(f"[{finding['severity'].upper()}] {finding['code']}{where} - {finding['message']}")
    return "\n".join(lines)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path, help="Markdown files or directories to scan recursively.")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--json-out", type=Path, help="Also write the complete JSON report to this path.")
    parser.add_argument("--fanout-threshold", type=int, default=8, help="Warn when one topic is used by at least this many questions.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.fanout_threshold < 2:
        print("--fanout-threshold must be at least 2", file=sys.stderr)
        return 2

    missing = [str(path) for path in args.paths if not path.exists()]
    if missing:
        print(f"Input paths do not exist: {', '.join(missing)}", file=sys.stderr)
        return 2

    paths = collect_markdown(args.paths)
    if not paths:
        print("No Markdown files found.", file=sys.stderr)
        return 2

    report = build_report(paths, fanout_threshold=args.fanout_threshold)
    json_text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json_text + "\n", encoding="utf-8")
    print(json_text if args.format == "json" else format_text(report))
    summary = report["summary"]
    assert isinstance(summary, dict)
    return 1 if summary["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
