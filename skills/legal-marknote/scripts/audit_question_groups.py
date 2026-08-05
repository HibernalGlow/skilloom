"""Audit quoted Markdown question groups and their answer sections."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


QUESTION_FENCE = re.compile(r"^>\s*```md\s*$")
CLOSE_FENCE = re.compile(r"^>\s*```\s*$")
QUESTION_NUMBER = re.compile(r"^>\s*(\d+)\.\s+")
ANSWER_HEADING = re.compile(r"^>\s*\*\*回答与解析：\*\*\s*$")
NUMERIC_HEADING = re.compile(r"^>\s*#{1,6}\s+(?:\d+|\(\d+\)|[①②③④⑤⑥⑦⑧⑨⑩])(?:[.)、]|\s)")
ANSWER_ITEM = re.compile(r"^>\s*(\d+)\.\s+")
QUESTION_LABEL = re.compile(r"^>\s*######\s*习题")
MARKDOWN_HEADING = re.compile(r"^#{1,6}\s+")


class AuditError:
    def __init__(self, path: Path, line: int, message: str) -> None:
        self.path = path
        self.line = line
        self.message = message

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: {self.message}"


def audit(path: Path) -> tuple[list[AuditError], list[str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    errors: list[AuditError] = []
    advisories: list[str] = []
    index = 0
    question_context = False

    while index < len(lines):
        if QUESTION_LABEL.match(lines[index]):
            question_context = True
            index += 1
            continue
        if MARKDOWN_HEADING.match(lines[index]):
            question_context = False
        if not question_context or not QUESTION_FENCE.match(lines[index]):
            index += 1
            continue

        opening_line = index + 1
        index += 1
        question_numbers: list[int] = []
        while index < len(lines) and not CLOSE_FENCE.match(lines[index]):
            match = QUESTION_NUMBER.match(lines[index])
            if match:
                question_numbers.append(int(match.group(1)))
            index += 1

        if index == len(lines):
            errors.append(AuditError(path, opening_line, "question fence is not closed"))
            break

        if len(question_numbers) > 1:
            errors.append(
                AuditError(
                    path,
                    opening_line,
                    f"question block contains {len(question_numbers)} top-level numbered questions; expected one main question (subquestions are allowed)",
                )
            )

        closing_index = index
        index += 1
        while index < len(lines) and lines[index].strip() in {">", ""}:
            index += 1

        has_answer_heading = index < len(lines) and ANSWER_HEADING.match(lines[index])
        has_direct_answer = index < len(lines) and ANSWER_ITEM.match(lines[index])
        if not has_answer_heading and not has_direct_answer:
            errors.append(
                AuditError(
                    path,
                    closing_index + 1,
                    "question block is not immediately followed by an answer list or **回答与解析：**",
                )
            )
            question_context = False
            continue

        answer_line = index + 1
        if has_answer_heading:
            index += 1
        answer_numbers: list[int] = []
        has_nested_list = False
        while index < len(lines):
            line = lines[index]
            if QUESTION_FENCE.match(line):
                break
            if line.startswith(">    ") or line.startswith(">\t"):
                has_nested_list = True
            match = ANSWER_ITEM.match(line)
            if match:
                answer_numbers.append(int(match.group(1)))
            if NUMERIC_HEADING.match(line):
                errors.append(
                    AuditError(path, index + 1, "numeric answer content is still formatted as a heading")
                )
            index += 1

        question_context = False

        expected = question_numbers
        if expected and answer_numbers[: len(expected)] != expected:
            errors.append(
                AuditError(
                    path,
                    answer_line,
                    f"answer numbering {answer_numbers[:len(expected)]!r} does not match question numbering {expected!r}",
                )
            )

        if len(answer_numbers) > 0 and not has_nested_list:
            advisories.append(
                f"{path}:{answer_line}: answer group has no indented sublist; review whether independent reasons need semantic nesting"
            )

    return errors, advisories


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()

    errors: list[AuditError] = []
    advisories: list[str] = []
    for path in args.paths:
        file_errors, file_advisories = audit(path)
        errors.extend(file_errors)
        advisories.extend(file_advisories)

    for advisory in advisories:
        print(f"ADVISORY {advisory}")
    for error in errors:
        print(f"ERROR {error}")

    if errors:
        return 1
    print(f"OK: audited {len(args.paths)} file(s), {len(advisories)} advisory/advisories")
    return 0


if __name__ == "__main__":
    sys.exit(main())
