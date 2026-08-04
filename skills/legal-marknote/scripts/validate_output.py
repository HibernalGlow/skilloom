#!/usr/bin/env python3
"""Validate generated legal-study Markdown against shared and profile rules."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


ALLOWED_CALLOUTS = {"TIP", "NOTE", "IMPORTANT", "CAUTION", "WARNING"}
STATUS_COLORS = {5, 8, 12, 13}
ANSWER_STATUS_TERMS = ("答案", "正确", "错误", "成立", "不成立", "有效", "无效", "应当", "不得", "排除")
HIGHLIGHT_PATTERN = re.compile(r"==(.+?)==")
COLOR_ATTRIBUTE_PATTERN = re.compile(r'\{:\s*style="([^"]*b3-font[^"]*)"\}')
COLORED_TERM_PATTERN = re.compile(
    r'\*\*(?P<term>.+?)\*\*\{:\s*style="[^"]*b3-font-color(?P<color>\d+)[^"]*"\}',
)
ENUMERATION_PATTERN = re.compile(r"(?<![\w])(?:\d{1,2}[、.]|[（(]\d{1,2}[）)]|[①-⑳])")
IMAGE_PATTERN = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
MERGE_TOKEN_PATTERN = re.compile(r"\{:\s*(?:colspan='\d+'|rowspan='\d+'|class='fn__none')\}")
CONTRAST_PAIRS = (("有效", "无效"), ("成立", "不成立"), ("原则", "例外"), ("允许", "禁止"))
ANSWER_MASK_PATTERN = re.compile(
    r"<div><style>b\{background:#c9cdd3;color:transparent;border-radius:4px;padding:0 6px\}b:hover\{background:#fff2c2;color:#c0392b\}</style>答案：<b>[^<]+</b></div>",
)


@dataclass(frozen=True)
class Finding:
    level: str
    code: str
    line: int
    message: str

    def render(self, path: Path) -> str:
        return f"{path}:{self.line}: {self.level}{self.code}: {self.message}"


def visible_length(value: str) -> int:
    plain = re.sub(r"[`*_~\s，。；：、,.!?！？（）()《》\[\]{}]", "", value)
    return len(plain)


def split_table_cells(line: str) -> list[str]:
    cells: list[str] = []
    current: list[str] = []
    escaped = False
    for character in line.strip().strip("|"):
        if escaped:
            current.append(character)
            escaped = False
        elif character == "\\":
            current.append(character)
            escaped = True
        elif character == "|":
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(character)
    cells.append("".join(current).strip())
    return cells


def is_table_divider(line: str) -> bool:
    return all(
        not cell or bool(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")))
        for cell in split_table_cells(line)
    )


def table_blocks(text: str) -> list[list[str]]:
    blocks: list[list[str]] = []
    current: list[str] = []
    for line in text.splitlines():
        if re.match(r"^\s*\|.*\|\s*$", line):
            current.append(line)
        elif current:
            blocks.append(current)
            current = []
    if current:
        blocks.append(current)
    return blocks


def normalized_table_content(value: str) -> str:
    value = re.sub(r"\{:\s*[^}]+\}", "", value)
    value = re.sub(r"<br\s*/?>", " ", value, flags=re.IGNORECASE)
    value = re.sub(r"[`*_~=]", "", value)
    return re.sub(r"\s+", "", value)


def table_cell_content_is_preserved(source_blocks: list[list[str]], output_text: str) -> bool:
    normalized_output = normalized_table_content(output_text)
    for block in source_blocks:
        for line in block:
            if is_table_divider(line):
                continue
            for cell in split_table_cells(line):
                fragment = normalized_table_content(cell)
                if len(fragment) >= 2 and fragment not in normalized_output:
                    return False
    return True


def style_families(value: str) -> set[str]:
    families: set[str] = set()
    if re.search(r"\*\*.+?\*\*", value):
        families.add("bold")
    if HIGHLIGHT_PATTERN.search(value):
        families.add("highlight")
    if re.search(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", value) or re.search(r"_(.+?)_", value):
        families.add("italic")
    if COLOR_ATTRIBUTE_PATTERN.search(value):
        families.add("color")
    return families


def line_for_offset(text: str, offset: int) -> int:
    return text.count("\n", 0, max(offset, 0)) + 1


def validate_highlights(text: str) -> list[Finding]:
    findings: list[Finding] = []
    for match in HIGHLIGHT_PATTERN.finditer(text):
        if visible_length(match.group(1)) > 6:
            findings.append(Finding("E", "101", line_for_offset(text, match.start()), "Highlight exceeds 6 visible characters."))
    for match in re.finditer(r"==[^=\n]+====[^=\n]+==", text):
        findings.append(Finding("E", "102", line_for_offset(text, match.start()), "Adjacent highlights need connecting text or punctuation."))
    for number, line in enumerate(text.splitlines(), start=1):
        if "\\=" in line:
            findings.append(Finding("E", "103", number, "Do not escape equals signs in highlight syntax."))
    return findings


def validate_colors(text: str) -> list[Finding]:
    findings: list[Finding] = []
    for match in COLOR_ATTRIBUTE_PATTERN.finditer(text):
        prefix = text[max(0, match.start() - 240):match.start()]
        if not re.search(r"\*\*[^*\n]+\*\*$", prefix):
            findings.append(Finding("E", "201", line_for_offset(text, match.start()), "SiYuan color style must attach directly to bold text."))
        numbers = [int(value) for value in re.findall(r"b3-font-(?:color|background)(\d+)", match.group(1))]
        if not numbers or any(value < 2 or value > 13 for value in numbers):
            findings.append(Finding("E", "202", line_for_offset(text, match.start()), "SiYuan color numbers must be integers from 2 through 13."))

    colors_by_term: dict[str, set[int]] = {}
    first_line_by_term: dict[str, int] = {}
    for match in COLORED_TERM_PATTERN.finditer(text):
        term = re.sub(r"\s+", "", match.group("term"))
        colors_by_term.setdefault(term, set()).add(int(match.group("color")))
        first_line_by_term.setdefault(term, line_for_offset(text, match.start()))
    for term, colors in colors_by_term.items():
        if len(colors) > 1:
            findings.append(Finding("E", "203", first_line_by_term[term], f"Repeated term '{term}' uses inconsistent text colors: {sorted(colors)}."))

    for left, right in CONTRAST_PAIRS:
        if left in text and right in text:
            relevant = [match for match in COLORED_TERM_PATTERN.finditer(text) if match.group("term") in {left, right}]
            if len(relevant) < 2:
                findings.append(Finding("W", "204", 1, f"Contrast pair '{left}/{right}' lacks two explicit semantic color anchors."))
    return findings


def validate_callouts_and_fences(text: str) -> list[Finding]:
    findings: list[Finding] = []
    lines = text.splitlines()
    in_fence = False
    for number, line in enumerate(lines, start=1):
        fence = re.match(r"^(?P<quote>\s*>\s*)?```(?P<lang>[A-Za-z0-9_-]*)", line)
        if fence:
            if not fence.group("quote"):
                findings.append(Finding("E", "301", number, "Code fences must be inside a blockquote."))
            if not in_fence and fence.group("lang") != "md":
                findings.append(Finding("E", "302", number, "Opening code fence must use the md language."))
            in_fence = not in_fence

        callout = re.match(r"^\s*>\s*\[!([^\]]+)\]", line)
        if callout:
            kind = callout.group(1)
            if kind != kind.upper() or kind not in ALLOWED_CALLOUTS:
                findings.append(Finding("E", "303", number, f"Callout type must be one of: {', '.join(sorted(ALLOWED_CALLOUTS))}."))
            cursor = number
            while cursor < len(lines) and lines[cursor].strip():
                if not re.match(r"^\s*>($|\s)", lines[cursor]):
                    findings.append(Finding("E", "304", cursor + 1, "Every nonblank line inside a callout must start with '> '."))
                    break
                cursor += 1
    if in_fence:
        findings.append(Finding("E", "305", len(lines) or 1, "Code fence is not closed."))
    return findings


def validate_tables(text: str) -> list[Finding]:
    findings: list[Finding] = []
    for number, line in enumerate(text.splitlines(), start=1):
        if not re.match(r"^\s*\|.*\|\s*$", line):
            continue
        for cell in split_table_cells(line):
            if re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")):
                continue
            segments = re.split(r"<br\s*/>", cell)
            marker_counts = [len(ENUMERATION_PATTERN.findall(segment)) for segment in segments]
            if sum(marker_counts) >= 2 and any(count > 1 for count in marker_counts):
                findings.append(Finding("E", "401", number, "Numbered table-cell items must be separated with <br />."))
            sentence_count = len(re.findall(r"[。！？；]", cell))
            if (visible_length(cell) >= 80 or sentence_count >= 2) and len(style_families(cell)) < 2:
                findings.append(Finding("E", "402", number, "Long table cell needs at least two semantic inline style families."))
    return findings


def validate_general_density(text: str) -> list[Finding]:
    findings: list[Finding] = []
    for number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", ">", "|", "- ", "* ", "```")):
            continue
        if visible_length(stripped) > 240:
            findings.append(Finding("W", "501", number, "Long prose line should be physically split into semantic list items."))
    if visible_length(text) >= 500 and not COLOR_ATTRIBUTE_PATTERN.search(text):
        findings.append(Finding("W", "502", 1, "Substantial output has no SiYuan semantic color anchors."))
    return findings


def validate_goldquest(text: str) -> list[Finding]:
    findings: list[Finding] = []
    lines = text.splitlines()
    for number, line in enumerate(lines, start=1):
        if re.search(r"-\s*\[[xX]\]", line):
            findings.append(Finding("E", "601", number, "Question options must remain unchecked."))
    task_options = [number for number, line in enumerate(lines, start=1) if re.search(r"-\s*\[[ xX]\]", line)]
    answer_headings = [number for number, line in enumerate(lines, start=1) if re.match(r"^######\s+答案与解析\s*$", line)]
    if task_options and not answer_headings:
        findings.append(Finding("E", "603", task_options[0], "Question options require a separate '###### 答案与解析' section."))

    h5_indices = [index for index, line in enumerate(lines) if re.match(r"^#####\s+", line) and not re.match(r"^######", line)]
    for index in h5_indices:
        end = next((candidate for candidate in range(index + 1, len(lines)) if re.match(r"^#{1,5}\s+", lines[candidate])), len(lines))
        answer = next((candidate for candidate in range(index + 1, end) if re.match(r"^######\s+答案与解析\s*$", lines[candidate])), None)
        if answer is None:
            continue
        question_text = "\n".join(lines[index + 1:answer])
        if HIGHLIGHT_PATTERN.search(question_text):
            findings.append(Finding("E", "604", index + 1, "Question area must not reveal answers with highlights."))
        leaking_terms = [
            match.group("term")
            for match in COLORED_TERM_PATTERN.finditer(question_text)
            if int(match.group("color")) in STATUS_COLORS
            and any(term in match.group("term") for term in ANSWER_STATUS_TERMS)
        ]
        if leaking_terms:
            findings.append(Finding("E", "605", index + 1, f"Question area uses status color on answer-bearing text: {leaking_terms}."))

        answer_lines = lines[answer + 1:end]
        first_content = next((line for line in answer_lines if line.strip()), None)
        if first_content is None or not ANSWER_MASK_PATTERN.search(first_content):
            findings.append(Finding("E", "606", answer + 1, "Answer section must start with the answer mask HTML block."))
        if any(ANSWER_MASK_PATTERN.search(line) for line in question_text.splitlines()):
            findings.append(Finding("E", "607", index + 1, "Answer mask HTML block is not allowed in the question area."))
    return findings


def validate_source_preservation(text: str, source_text: str, profile: str) -> list[Finding]:
    findings: list[Finding] = []
    for image in IMAGE_PATTERN.findall(source_text):
        if image not in IMAGE_PATTERN.findall(text):
            findings.append(Finding("E", "701", 1, f"Source image link was not preserved: {image}"))
    source_table_blocks = table_blocks(source_text)
    output_table_blocks = table_blocks(text)
    source_tables = sum(len(block) for block in source_table_blocks)
    output_tables = sum(len(block) for block in output_table_blocks)
    if output_tables < source_tables:
        findings.append(Finding("E", "702", 1, f"Output has fewer Markdown table rows than source ({output_tables} < {source_tables})."))
    allows_structural_table_split = (
        len(output_table_blocks) > len(source_table_blocks)
        and table_cell_content_is_preserved(source_table_blocks, text)
    )
    for token in MERGE_TOKEN_PATTERN.findall(source_text):
        if text.count(token) < source_text.count(token) and not allows_structural_table_split:
            findings.append(Finding("E", "703", 1, f"Source SiYuan table merge token was not preserved: {token}"))
    if profile == "legal-marknote":
        for heading in re.findall(r"^#{1,6}\s+(.+?)\s*$", source_text, re.MULTILINE):
            if heading not in text:
                findings.append(Finding("E", "704", 1, f"Source heading was not preserved: {heading}"))
    return findings


def validate_text(text: str, profile: str, source_text: str | None = None) -> list[Finding]:
    findings = []
    findings.extend(validate_highlights(text))
    findings.extend(validate_colors(text))
    findings.extend(validate_callouts_and_fences(text))
    findings.extend(validate_tables(text))
    findings.extend(validate_general_density(text))
    if profile == "legal-goldquest":
        findings.extend(validate_goldquest(text))
    if source_text is not None:
        findings.extend(validate_source_preservation(text, source_text, profile))
    return sorted(findings, key=lambda finding: (finding.line, finding.level != "E", finding.code))


def infer_profile(script_path: Path) -> str | None:
    for parent in script_path.parents:
        if parent.name in {"legal-marknote", "legal-goldquest"}:
            return parent.name
    return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="Generated Markdown file to validate.")
    parser.add_argument("--profile", choices=("legal-marknote", "legal-goldquest"), default=infer_profile(Path(__file__).resolve()))
    parser.add_argument("--source", type=Path, help="Original source file for preservation checks.")
    parser.add_argument("--require-source", action="store_true", help="Fail when --source is omitted.")
    parser.add_argument("--strict", action="store_true", help="Treat advisory warnings as gate failures.")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.profile is None:
        print("--profile is required when running the canonical validator.", file=sys.stderr)
        return 2
    if args.require_source and args.source is None:
        print(f"{args.output}:1: E700: --source is required by this gate.")
        return 1
    text = args.output.read_text(encoding="utf-8")
    source_text = args.source.read_text(encoding="utf-8") if args.source else None
    findings = validate_text(text, args.profile, source_text)
    if args.format == "json":
        print(json.dumps([asdict(finding) for finding in findings], ensure_ascii=False, indent=2))
    elif findings:
        for finding in findings:
            print(finding.render(args.output))
    else:
        print(f"PASS {args.profile} output validation: {args.output}")
    has_errors = any(finding.level == "E" for finding in findings)
    has_warnings = any(finding.level == "W" for finding in findings)
    return 1 if has_errors or (args.strict and has_warnings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
