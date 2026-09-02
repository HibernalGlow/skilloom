"""Audit quoted Markdown question groups and their answer sections."""
# ==========================================================================
# ⛔ 内容会话禁读本源码（用户纪律 2026-09-02）
#    校验器源码不供阅读。判定标准与修法的唯一权威渠道：
#    技能正文 + references/ + 运行本工具得到的真实报错
#    （goldquest 校验器另有 --explain <CODE> 权威词条，如 --explain E630）。
#    打开/grep/sed/脚本方式读取本文件属违规——包括动笔前的预防性阅读，
#    会被看护发现并上报用户。看不懂的报错：原样报告错误码与文本，等用户解释。
# ==========================================================================

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
QUESTION_CALLOUT = re.compile(r"^>\s*\[!QUESTION\](?:\s+(?P<title>\S.*?))?\s*$")
LEGACY_QUESTION_LABEL = re.compile(r"^(?:>\s*)?######\s*(?:习题|试一试|练习题|真题)")
GENERIC_QUESTION_TITLE = re.compile(
    r"^(?:习题|试一试|练习题|真题|题目)(?:\s*[一二三四五六七八九十\d]+)?$"
)
MARKDOWN_HEADING = re.compile(r"^#{1,6}\s+")


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


def validate_question_callouts(lines: list[str], path: Path) -> list[AuditError]:
    """Require one specifically titled QUESTION directive per exercise callout."""
    errors: list[AuditError] = []
    in_callout = False

    for number, line in enumerate(lines, start=1):
        if LEGACY_QUESTION_LABEL.match(line):
            errors.append(
                AuditError(
                    path,
                    number,
                    "legacy exercise heading must be replaced with '> [!QUESTION] ✏️ <specific topic or tested rule>'",
                )
            )
            continue

        directive = QUESTION_CALLOUT.match(line)
        if directive:
            if in_callout:
                errors.append(
                    AuditError(
                        path,
                        number,
                        "continuous exercise callout repeats the QUESTION directive; keep it only before the first question fence",
                    )
                )
            title = (directive.group("title") or "").strip()
            if not title.startswith("✏️ "):
                errors.append(
                    AuditError(
                        path,
                        number,
                        "QUESTION callout title must start with '✏️ ' and name the specific topic or tested rule",
                    )
                )
            else:
                topic = title.removeprefix("✏️ ").strip()
                if not topic or topic == "具体专题或考点" or GENERIC_QUESTION_TITLE.fullmatch(topic):
                    errors.append(
                        AuditError(
                            path,
                            number,
                            "QUESTION callout title must name the specific topic or tested rule, not a generic exercise label",
                        )
                    )
            in_callout = True
            continue

        if not in_callout:
            continue
        if line.lstrip().startswith(">"):
            continue
        in_callout = False

    return errors


def audit(path: Path, source: Path | None = None) -> tuple[list[AuditError], list[str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    errors = validate_question_callouts(lines, path)
    advisories: list[str] = []
    index = 0
    question_context = False

    while index < len(lines):
        if QUESTION_CALLOUT.match(lines[index]):
            question_context = True
            index += 1
            continue
        if LEGACY_QUESTION_LABEL.match(lines[index]):
            question_context = False
            index += 1
            continue
        if question_context and not lines[index].lstrip().startswith(">"):
            question_context = False
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
                        "multi-part question needs separate 题干： and 问题： lines before its one-line subquestions; write the shared stem as a 题干： line and the prompt as a 问题： line",
                    )
                )

        closing_index = index
        index += 1
        while index < len(lines) and lines[index].strip() == ">":
            index += 1

        has_answer_heading = index < len(lines) and ANSWER_HEADING.match(lines[index])
        has_direct_answer = index < len(lines) and ANSWER_ITEM.match(lines[index])
        if not has_answer_heading and not has_direct_answer:
            errors.append(
                AuditError(
                    path,
                    closing_index + 1,
                    "question block is not immediately followed by an answer list or **回答与解析：**; add the answer list (or the **回答与解析：** lead) directly after the last subquestion line",
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
            if not line.lstrip().startswith(">"):
                break
            if line.startswith(">    ") or line.startswith(">\t"):
                has_nested_list = True
            match = ANSWER_ITEM.match(line)
            if match:
                answer_numbers.append(int(match.group(1)))
            if NUMERIC_HEADING.match(line):
                errors.append(
                    AuditError(path, index + 1, "numeric answer content is still formatted as a heading; demote it to the matching quoted ordered-list item or body text so answers are not read as structure")
                )
            index += 1

        question_context = index < len(lines) and QUESTION_FENCE.match(lines[index]) is not None

        expected = question_numbers
        if expected and answer_numbers[: len(expected)] != expected:
            errors.append(
                AuditError(
                    path,
                    answer_line,
                    f"answer numbering {answer_numbers[:len(expected)]!r} does not match question numbering {expected!r}; renumber the answer lines to follow the question numbers exactly",
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
                    f"source={source_identifiers!r}, output={output_identifiers!r}; "
                    "restore the fenced question and subquestion identifiers byte-identical to the source",
                )
            )

    return errors, advisories


DEFAULT_REPORT_LIMIT = 40


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument(
        "--source",
        type=Path,
        help="Original Markdown used to verify exact question and subquestion identifiers inside quoted md fences.",
    )
    parser.add_argument("--all", action="store_true", help="Print every report line instead of the bounded default report.")
    parser.add_argument("--max-report", type=int, default=DEFAULT_REPORT_LIMIT, help=f"Report cap (default {DEFAULT_REPORT_LIMIT}); --all lifts the cap.")
    args = parser.parse_args()

    if args.source is not None and len(args.paths) != 1:
        parser.error("--source requires exactly one output path")

    errors: list[AuditError] = []
    advisories: list[str] = []
    for path in args.paths:
        file_errors, file_advisories = audit(path, args.source)
        errors.extend(file_errors)
        advisories.extend(file_advisories)

    report_lines = [f"ADVISORY {advisory}" for advisory in advisories]
    report_lines += [f"ERROR {error}" for error in errors]
    shown = report_lines if args.all else report_lines[: max(0, args.max_report)]
    for line in shown:
        print(line)
    hidden = len(report_lines) - len(shown)
    if hidden > 0:
        print(f"... {hidden} more report line(s) not shown of {len(report_lines)} total ({len(errors)} error(s), {len(advisories)} advisory/advisories). Lift the cap with --all or raise --max-report.")

    if errors:
        return 1
    print(f"OK: audited {len(args.paths)} file(s), {len(advisories)} advisory/advisories")
    return 0


if __name__ == "__main__":
    sys.exit(main())
