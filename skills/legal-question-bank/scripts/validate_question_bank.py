#!/usr/bin/env python3
"""Validate the portable Markdown + IAL contract for legal question-bank sources."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


QUESTION_HEADING = re.compile(r"^#####\s+(?!#).+\S\s*$")
IAL = re.compile(r'^\{:\s*(?P<attrs>.+)\s*\}$')
ATTRIBUTE = re.compile(r'(?P<key>[\w-]+)="(?P<value>[^"]*)"')
VALID_TYPES = {"single", "multiple", "true-false", "subjective"}
STABLE_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
OPTION = re.compile(r"^\s*(?:[-*]\s+(?:\[[ xX]\]\s+)?)?(?:\(?([A-Z])\)?[.、])\s+")
CHECKED_OPTION = re.compile(r"^\s*[-*]\s+\[[xX]\]\s+")
ANSWER_LEAK = re.compile(r"(?:正确答案|答案\s*[:：]|==[^=]+==|font-color(?:8|13))")


@dataclass(frozen=True)
class Finding:
    level: str
    code: str
    line: int
    message: str

    def render(self, path: Path) -> str:
        return f"{path}:{self.line}: {self.level}{self.code}: {self.message}"


def attrs_at(lines: list[str], index: int) -> dict[str, str]:
    if index >= len(lines):
        return {}
    match = IAL.match(lines[index].strip())
    if not match:
        return {}
    return {item.group("key"): item.group("value") for item in ATTRIBUTE.finditer(match.group("attrs"))}


def validate(text: str) -> list[Finding]:
    lines = text.splitlines()
    findings: list[Finding] = []
    question_indexes = [index for index, line in enumerate(lines) if QUESTION_HEADING.match(line)]
    seen_ids: dict[str, int] = {}

    for position, start in enumerate(question_indexes):
        end = question_indexes[position + 1] if position + 1 < len(question_indexes) else len(lines)
        attrs = attrs_at(lines, start + 1)
        line_no = start + 1
        question_id = attrs.get("custom-qb-id")
        question_type = attrs.get("custom-qb-type")

        if not question_id:
            findings.append(Finding("E", "101", line_no, "Question heading requires custom-qb-id in the next IAL block."))
        elif not STABLE_ID.fullmatch(question_id):
            findings.append(Finding("E", "102", line_no, "custom-qb-id must be lowercase ASCII kebab-case."))
        elif question_id in seen_ids:
            findings.append(Finding("E", "103", line_no, f"Duplicate custom-qb-id; first used on line {seen_ids[question_id]}."))
        else:
            seen_ids[question_id] = line_no

        if question_type not in VALID_TYPES:
            findings.append(Finding("E", "104", line_no, "custom-qb-type must be single, multiple, true-false, or subjective."))

        answer = attrs.get("custom-qb-answer")
        if question_type == "single" and not re.fullmatch(r"[A-Z]", answer or ""):
            findings.append(Finding("E", "105", line_no, "single questions require one uppercase custom-qb-answer option ID."))
        if question_type == "multiple" and not re.fullmatch(r"[A-Z](?:,[A-Z]){1,}", answer or ""):
            findings.append(Finding("E", "106", line_no, "multiple questions require two or more comma-separated uppercase option IDs."))
        if question_type == "true-false" and answer not in {"true", "false"}:
            findings.append(Finding("E", "107", line_no, "true-false questions require custom-qb-answer=true or false."))
        if question_type == "subjective" and answer is not None:
            findings.append(Finding("E", "108", line_no, "subjective questions must not declare custom-qb-answer."))

        solution = next(
            (candidate for candidate in range(start + 1, end) if attrs_at(lines, candidate).get("custom-qb-section") == "solution"),
            None,
        )
        if solution is None:
            findings.append(Finding("E", "109", line_no, "Question requires an explicit custom-qb-section=\"solution\" boundary."))
            prompt_end = end
        else:
            prompt_end = solution - 1

        prompt = lines[start + 1:prompt_end]
        if any(CHECKED_OPTION.match(line) for line in prompt):
            findings.append(Finding("E", "110", line_no, "Question-area task-list options must remain unchecked."))
        if any(ANSWER_LEAK.search(line) for line in prompt):
            findings.append(Finding("E", "111", line_no, "Question area appears to reveal an answer or status result before the solution boundary."))
        if question_type in {"single", "multiple"} and not any(OPTION.match(line) for line in prompt):
            findings.append(Finding("W", "201", line_no, "No recognizable option prefix found; add custom-qb-option only when needed."))

    for index, line in enumerate(lines):
        attrs = attrs_at(lines, index)
        if attrs.get("custom-qb-role") == "topic" and not STABLE_ID.fullmatch(attrs.get("custom-qb-topic-id", "")):
            findings.append(Finding("E", "112", index + 1, "Topic IAL requires lowercase ASCII kebab-case custom-qb-topic-id."))

    if not question_indexes:
        findings.append(Finding("W", "202", 1, "No five-level question headings found."))
    return sorted(findings, key=lambda item: (item.line, item.level, item.code))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--require-source", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    if args.require_source and args.source is None:
        print(f"{args.output}:1: E113: --source is required by this gate.", file=sys.stderr)
        return 2
    if args.source is not None and not args.source.is_file():
        print(f"{args.source}:1: E114: source file does not exist.", file=sys.stderr)
        return 2
    if not args.output.is_file():
        print(f"{args.output}:1: E115: output file does not exist.", file=sys.stderr)
        return 2

    findings = validate(args.output.read_text(encoding="utf-8"))
    for finding in findings:
        print(finding.render(args.output))
    return 1 if any(finding.level == "E" or args.strict for finding in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
