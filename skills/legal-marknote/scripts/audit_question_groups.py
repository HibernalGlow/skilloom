"""Audit quoted Markdown question groups and their answer sections."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


QUESTION_FENCE = re.compile(r"^>\s*```md\s*$")
CLOSE_FENCE = re.compile(r"^>\s*```\s*$")
QUESTION_NUMBER = re.compile(r"^>\s*(?:\[[^\]\n]+\]\s*)?(\d+)\.\s*")
QUESTION_IDENTIFIER = re.compile(
    r"^>\s*(?:\[[^\]\n]+\]\s*)?(?P<identifier>"
    r"(?:第\s*\d+\s*题)"
    r"|(?:\d+[.．、])"
    r"|(?:[（(]\d+[)）])"
    r"|(?:[①②③④⑤⑥⑦⑧⑨⑩])"
    r"|(?:[一二三四五六七八九十]+[、.．])"
    r")"
)
SUBQUESTION_IDENTIFIER = re.compile(r"[（(]\d+[)）]|[①②③④⑤⑥⑦⑧⑨⑩]")
STEM_LABEL = re.compile(r"^>\s*题干[：:]\s*\S")
QUESTION_PROMPT_LABEL = re.compile(r"^>\s*问题[：:]\s*(?:\S.*)?$")
ANSWER_HEADING = re.compile(r"^>\s*\*\*回答与解析：\*\*\s*$")
NUMERIC_HEADING = re.compile(r"^>\s*#{1,6}\s+(?:\d+|\(\d+\)|[①②③④⑤⑥⑦⑧⑨⑩])(?:[.)、]|\s)")
ANSWER_ITEM = re.compile(r"^>\s*(\d+)\.\s+")
QUESTION_LABEL = re.compile(r"^>\s*######\s*习题")
MARKDOWN_HEADING = re.compile(r"^#{1,6}\s+")
QUOTED_HEADING = re.compile(r"^>\s*#{1,6}\s+")


class AuditError:
    def __init__(self, path: Path, line: int, message: str) -> None:
        self.path = path
        self.line = line
        self.message = message

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: {self.message}"


def fenced_question_identifiers(path: Path) -> list[str]:
    """Return source identifiers exactly as written inside quoted md fences."""
    lines = path.read_text(encoding="utf-8").splitlines()
    identifiers: list[str] = []
    in_question_fence = False
    for line in lines:
        if not in_question_fence and QUESTION_FENCE.match(line):
            in_question_fence = True
            continue
        if in_question_fence and CLOSE_FENCE.match(line):
            in_question_fence = False
            continue
        if not in_question_fence:
            continue
        occupied_spans: list[tuple[int, int]] = []
        match = QUESTION_IDENTIFIER.match(line)
        if match:
            identifiers.append(match.group("identifier"))
            occupied_spans.append(match.span("identifier"))
        for subquestion in SUBQUESTION_IDENTIFIER.finditer(line):
            if any(start <= subquestion.start() < end for start, end in occupied_spans):
                continue
            identifiers.append(subquestion.group(0))
    return identifiers


def validate_question_labels(lines: list[str], path: Path) -> list[AuditError]:
    """Require one exercise label per continuous quoted exercise group."""
    errors: list[AuditError] = []
    label_seen = False
    in_exercise_group = False

    for number, line in enumerate(lines, start=1):
        if QUESTION_LABEL.match(line):
            if label_seen:
                errors.append(
                    AuditError(
                        path,
                        number,
                        "continuous quoted exercise group repeats the '###### 习题' label; keep it only before the first question fence",
                    )
                )
            label_seen = True
            in_exercise_group = True
            continue

        if not in_exercise_group:
            continue
        if not line.strip() or line.lstrip().startswith(">"):
            if QUOTED_HEADING.match(line):
                label_seen = False
                in_exercise_group = False
            continue

        label_seen = False
        in_exercise_group = False

    return errors


def audit(path: Path, source: Path | None = None) -> tuple[list[AuditError], list[str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    errors = validate_question_labels(lines, path)
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
        fence_lines: list[tuple[int, str]] = []
        while index < len(lines) and not CLOSE_FENCE.match(lines[index]):
            fence_lines.append((index + 1, lines[index]))
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

        subquestion_count = 0
        for line_number, fence_line in fence_lines:
            markers = list(SUBQUESTION_IDENTIFIER.finditer(fence_line))
            main_identifier = QUESTION_IDENTIFIER.match(fence_line)
            if main_identifier:
                main_span = main_identifier.span("identifier")
                markers = [
                    marker
                    for marker in markers
                    if not (main_span[0] <= marker.start() < main_span[1])
                ]
            subquestion_count += len(markers)
            if len(markers) > 1:
                errors.append(
                    AuditError(
                        path,
                        line_number,
                        "question stem and numbered subquestions are crowded onto one line; keep the stem and every subquestion on separate lines",
                    )
                )
                continue
            if markers:
                prefix = re.sub(r"^>\s*", "", fence_line[:markers[0].start()]).strip()
                if prefix:
                    errors.append(
                        AuditError(
                            path,
                            line_number,
                            "numbered subquestion must start its own line instead of following stem or question text",
                        )
                    )
        if subquestion_count:
            has_stem = any(STEM_LABEL.match(line) for _, line in fence_lines)
            has_question_label = any(QUESTION_PROMPT_LABEL.match(line) for _, line in fence_lines)
            if not (has_stem and has_question_label):
                errors.append(
                    AuditError(
                        path,
                        opening_line,
                        "multi-part question needs separate 题干： and 问题： lines before its one-line subquestions",
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

    if source is not None:
        source_identifiers = fenced_question_identifiers(source)
        output_identifiers = fenced_question_identifiers(path)
        if source_identifiers != output_identifiers:
            errors.append(
                AuditError(
                    path,
                    1,
                    "fenced question identifiers changed: "
                    f"source={source_identifiers!r}, output={output_identifiers!r}",
                )
            )

    return errors, advisories


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument(
        "--source",
        type=Path,
        help="Original Markdown used to verify exact question and subquestion identifiers inside quoted md fences.",
    )
    args = parser.parse_args()

    if args.source is not None and len(args.paths) != 1:
        parser.error("--source requires exactly one output path")

    errors: list[AuditError] = []
    advisories: list[str] = []
    for path in args.paths:
        file_errors, file_advisories = audit(path, args.source)
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
