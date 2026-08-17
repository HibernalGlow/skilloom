#!/usr/bin/env python3
"""Validate generated legal-study Markdown against shared and profile rules."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from legal_goldquest_option_gate import validate_option_analysis  # noqa: E402
from legal_marknote_prose_gate import validate_marknote_prose_structure  # noqa: E402

ALLOWED_CALLOUTS = {"TIP", "NOTE", "IMPORTANT", "CAUTION", "WARNING"}
STATUS_COLORS = {5, 8, 12, 13}
ANSWER_STATUS_TERMS = ("答案", "正确", "错误", "成立", "不成立", "有效", "无效", "应当", "不得", "排除")
HIGHLIGHT_PATTERN = re.compile(r"==(.+?)==")
COLOR_ATTRIBUTE_PATTERN = re.compile(r'\{:\s*style="([^"]*b3-font[^"]*)"\}')
COLORED_TERM_PATTERN = re.compile(
    r'\*\*(?P<term>.+?)\*\*\{:\s*style="[^"]*b3-font-color(?P<color>\d+)[^"]*"\}',
)
STYLED_TERM_PATTERN = re.compile(
    r'\*\*(?P<term>.+?)\*\*\{:\s*style="(?P<style>[^"]*b3-font-(?:color|background)\d+[^\"]*)"\}',
)
CONCEPT_LIST_LEAD_PATTERN = re.compile(
    r'^(?P<quote>\s*(?:>\s*)?)(?P<indent>\s*)(?:[-+*]|\d+[.)])\s+'
    r'\*\*(?P<term>[^*\n]+)\*\*\{:\s*style="(?P<style>[^"]*b3-font-(?:color|background)\d+[^\"]*)"\}'
)
ENUMERATION_PATTERN = re.compile(r"(?<![\w])(?:\d{1,2}[、.]|[（(]\d{1,2}[）)]|[①-⑳])")
IMAGE_PATTERN = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
STATIC_VISUAL_PATTERN = re.compile(
    r"!\[(?P<alt>[^\]]*(?:可视化|图解|流程图|关系图|决策图|时间线|diagram)[^\]]*)\]"
    r"\((?P<target>[^)\s]+?\.(?:svg|png)(?:[?#][^)]*)?)\)",
    re.IGNORECASE,
)
MERGE_TOKEN_PATTERN = re.compile(r"\{:\s*(?:colspan='\d+'|rowspan='\d+'|class='fn__none')\}")
TABLE_ROW_PATTERN = re.compile(r"^\s*\|.*\|\s*$")
TABLE_SEPARATOR_PATTERN = re.compile(r"^:?-{3,}:?$")
MERGE_SPAN_PATTERN = re.compile(r"\b(?P<name>colspan|rowspan)=['\"](?P<value>\d+)['\"]")
MERGE_PLACEHOLDER_PATTERN = re.compile(r"\bclass=['\"]fn__none['\"]")
CONTRAST_PAIRS = (("有效", "无效"), ("成立", "不成立"), ("原则", "例外"), ("允许", "禁止"))
# W509 verifies a visible structural cue, not an emoji dictionary.  Meaning is
# intentionally reviewed in the skill contract because a Unicode regex cannot
# determine whether an icon fits the legal relationship it labels.
SEMANTIC_EMOJI_LABEL_PATTERN = re.compile(
    r"(?m)^(?:\s*(?:[-+*]|\d+[.)])\s+|\s*>\s*\[!(?:TIP|NOTE|IMPORTANT|CAUTION|WARNING)\]\s+)"
    r"(?![✅❌])[\U0001F000-\U0001FAFF\u2600-\u27BF](?:\ufe0f|\U0001F3FB-\U0001F3FF|\u200d[\U0001F000-\U0001FAFF\u2600-\u27BF])*\s*(?=\S)"
)
LEGACY_ANSWER_MASK_PATTERN = re.compile(
    r"<div><style>b\{background:#c9cdd3;color:transparent;border-radius:4px;padding:0 6px\}b:hover\{background:#fff2c2;color:#c0392b\}</style>答案：<b>[^<]+</b></div>",
)
VISIBLE_ANSWER_LINE_PATTERN = re.compile(r"^\s*(?:[-*]\s*)?(?:正确答案|答案)[：:]\s*\S+")
IAL_PATTERN = re.compile(r'^\{:\s*(?P<attrs>.+?)\s*\}$')
IAL_ATTRIBUTE_PATTERN = re.compile(r'(?P<key>[\w-]+)="(?P<value>[^"]*)"')
STABLE_TOPIC_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
COMMON_SUBJECT_TERMS = (
    "最高人民法院", "最高人民检察院", "人民法院", "人民检察院", "被申请人", "被上诉人", "被代理人", "申请人", "上诉人",
    "债权人", "债务人", "保证人", "第三人", "行为人", "相对人", "受让人", "转让人",
    "出租人", "承租人", "买受人", "出卖人", "委托人", "受托人", "代理人", "原告", "被告",
    "公安机关", "行政机关", "仲裁机构", "法院", "检察院", "甲", "乙", "丙", "丁", "戊",
)
COMMON_SURNAME_INITIALS = set("赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦许何吕张孔曹严华金魏陶姜谢邹苏潘葛范彭鲁韦马方任袁唐薛雷贺罗郝安于傅齐康伍余顾孟黄萧姚邵汪毛戴宋熊纪舒董梁杜阮江郭林徐高夏蔡田胡霍万庄柴阎廖曾白邓叶刘龙")
QUESTION_HEADING_PATTERN = re.compile(r"^#####\s+(?!#).+\S\s*$")
NOTE_TOPIC_ANCHOR_PATTERN = re.compile(r"^\*\*考点[：:]\s*.+?\*\*\s*$")
NUMERIC_ONLY_HEADING_PATTERN = re.compile(r"^(?:\s*>\s*)?#{1,6}\s+\d{1,3}(?:[.、．])?\s*$")
ANY_HEADING_PATTERN = re.compile(r"^(?:\s*>\s*)?#{1,6}\s+(?P<title>.+?)\s*$")
SHORT_CONCEPT_DEFINITION_PATTERN = re.compile(
    r'^(?:\*\*)?(?P<term>[^：:\n]{2,24}?)(?:\*\*)?(?:\{:\s*style="[^"]*"\})?\s*[：:]\s*(?P<definition>\S.+)$'
)
EXERCISE_REGION_PATTERN = re.compile(r"(?:习题|试一试|练习题|真题)")
EXERCISE_CONTINUATION_PATTERN = re.compile(r"^(?:答案与解析|回答与解析)[：:]?$")
NON_CONCEPT_LABELS = {"答案", "回答", "解析", "问题", "题目", "示例", "例题", "注意", "提示"}

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

def prose_visible_length(value: str) -> int:
    plain = re.sub(r'\{:\s*[^}\n]+\}', '', value)
    plain = re.sub(r'!\[[^\]]*\]\([^)]+\)', '', plain)
    plain = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', plain)
    return visible_length(plain)


def prose_without_fenced_blocks(value: str) -> str:
    lines: list[str] = []
    in_fence = False
    for line in value.splitlines():
        stripped = line.strip()
        if stripped.startswith(("```", "> ```")):
            in_fence = not in_fence
            continue
        if in_fence or IAL_PATTERN.match(stripped):
            continue
        lines.append(line)
    return "\n".join(lines)


def has_semantic_emoji_label(value: str) -> bool:
    """Return whether an open-set emoji leads a real structural label."""
    return SEMANTIC_EMOJI_LABEL_PATTERN.search(prose_without_fenced_blocks(value)) is not None


def visual_families(value: str) -> set[str]:
    """Return intentional SiYuan-compatible visual carriers present in Markdown."""
    families: set[str] = set()
    if re.search(r"(?m)^(?:\s*>\s*)?```mermaid\s*$", value):
        families.add("mermaid")
    if re.search(r"(?m)^(?:\s*>\s*)?```html\s*$", value):
        families.add("html")
    if STATIC_VISUAL_PATTERN.search(value):
        families.add("static-image")
    return families


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


def style_families(value: str) -> set[str]:
    families: set[str] = set()
    if re.search(r"\*\*.+?\*\*", value):
        families.add("bold")
    if HIGHLIGHT_PATTERN.search(value):
        families.add("highlight")
    if re.search(r"<em(?:\s[^>]*)?>[\s\S]+?</em>", value, re.IGNORECASE):
        families.add("italic")
    if re.search(r"~~[^~\n]+~~", value):
        families.add("strike")
    if re.search(r"(?<!`)`[^`\n]+`(?!`)", value):
        families.add("code")
    if re.search(r"text-decoration\s*:\s*underline|<u(?:\s[^>]*)?>.+?</u>", value, re.IGNORECASE):
        families.add("underline")
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


def validate_emphasis_syntax(text: str) -> list[Finding]:
    findings: list[Finding] = []
    in_fence = False
    asterisk_italic = re.compile(r"(?<!\*)\*(?![\s*])[^*\n]*?\S\*(?!\*)")
    underscore_italic = re.compile(r"(?<![\w_])_(?![_\s])[^_\n]*?\S_(?![\w_])")
    underscore_bold = re.compile(r"(?<!_)__(?![_\s])[^_\n]*?\S__(?!_)")

    for number, line in enumerate(text.splitlines(), start=1):
        if re.match(r"^(?:\s*>\s*)?```", line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        searchable = re.sub(r"(?<!`)`[^`\n]+`(?!`)", "", line)
        searchable = re.sub(r"\{:\s*[^}\n]*\}", "", searchable)
        if underscore_bold.search(searchable):
            findings.append(Finding("E", "105", number, "Double-underscore bold is disabled; use **text** for bold."))
        if asterisk_italic.search(searchable) or underscore_italic.search(searchable):
            findings.append(Finding("E", "104", number, "Markdown italic markers are disabled; use <em>text</em> sparingly."))
    return findings


def validate_colors(text: str) -> list[Finding]:
    findings: list[Finding] = []
    bad_underlines = list(
        re.finditer(
            r"</u>\s*\{:\s*style=\"(?P<style>[^\"]*b3-font-(?:color|background)[^\"]*)\"\s*\}",
            text,
            re.IGNORECASE,
        )
    )
    bad_style_starts = {match.start("style") for match in bad_underlines}
    for match in bad_underlines:
        findings.append(
            Finding(
                "E",
                "205",
                line_for_offset(text, match.start()),
                "Keep colored underline styling inside <u style=\"...\">text</u>; a style IAL after </u> is invalid.",
            )
        )
    for match in COLOR_ATTRIBUTE_PATTERN.finditer(text):
        prefix = text[max(0, match.start() - 240):match.start()]
        if match.start(1) in bad_style_starts:
            continue
        if not re.search(r"\*\*[^*\n]+\*\*$", prefix):
            findings.append(Finding("E", "201", line_for_offset(text, match.start()), "SiYuan foreground/background color style must attach directly to bold text."))
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
    fence_language = ""
    fence_body: list[str] = []
    fence_start = 0

    def finish_fence(number: int) -> None:
        nonlocal fence_body, fence_language, fence_start
        if fence_language == "html":
            body = "\n".join(re.sub(r"^\s*>\s?", "", item) for item in fence_body).strip()
            if not re.fullmatch(r"<div(?:\s[^>]*)?>[\s\S]*</div>", body, re.IGNORECASE):
                findings.append(Finding("E", "306", fence_start or number, "HTML code blocks must contain one outer <div>...</div> wrapper."))
        fence_body = []
        fence_language = ""
        fence_start = 0
    for number, line in enumerate(lines, start=1):
        fence = re.match(r"^(?P<quote>\s*>\s*)?```(?P<lang>[A-Za-z0-9_-]*)", line)
        if fence:
            if not fence.group("quote"):
                findings.append(Finding("E", "301", number, "Code fences must be inside a blockquote."))
            if not in_fence:
                fence_language = fence.group("lang")
                fence_start = number
                if fence_language not in {"md", "html", "mermaid"}:
                    findings.append(Finding("E", "302", number, "Opening code fence must use the md, html, or mermaid language."))
                in_fence = True
            else:
                finish_fence(number)
                in_fence = False
            continue

        if in_fence:
            fence_body.append(line)
            continue

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


def is_table_separator(cells: list[str]) -> bool:
    return bool(cells) and all(TABLE_SEPARATOR_PATTERN.fullmatch(cell.replace(" ", "")) for cell in cells)


def merge_span(cell: str, name: str) -> int | None:
    match = next((item for item in MERGE_SPAN_PATTERN.finditer(cell) if item.group("name") == name), None)
    return int(match.group("value")) if match else None


def is_merge_placeholder(cell: str) -> bool:
    return bool(MERGE_PLACEHOLDER_PATTERN.search(cell))


def table_blocks(text: str) -> list[list[tuple[int, list[str]]]]:
    blocks: list[list[tuple[int, list[str]]]] = []
    current: list[tuple[int, list[str]]] = []
    for number, line in enumerate(text.splitlines(), start=1):
        if TABLE_ROW_PATTERN.match(line):
            current.append((number, split_table_cells(line)))
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


def table_cell_content_is_preserved(source_blocks: list[list[tuple[int, list[str]]]], output_text: str) -> bool:
    normalized_output = normalized_table_content(output_text)
    for block in source_blocks:
        for _, cells in block:
            if is_table_separator(cells):
                continue
            for cell in cells:
                fragment = normalized_table_content(cell)
                if len(fragment) >= 2 and fragment not in normalized_output:
                    return False
    return True


def table_cell_has_large_list(cell: str) -> bool:
    numbered_items = len(ENUMERATION_PATTERN.findall(cell))
    bulleted_items = len(re.findall(r"(?:^|<br\s*/?>)\s*[-*]\s+", cell, re.IGNORECASE))
    item_count = numbered_items + bulleted_items
    return item_count >= 4 or (item_count >= 3 and visible_length(cell) >= 100)


def table_block_has_large_list(block: list[tuple[int, list[str]]]) -> bool:
    return any(table_cell_has_large_list(cell) for _, cells in block for cell in cells)


def table_block_is_simple_label_rule(block: list[tuple[int, list[str]]]) -> bool:
    content_rows = [cells for _, cells in block if not is_table_separator(cells)]
    if len(content_rows) < 2 or any(len(cells) != 2 for cells in content_rows):
        return False
    if any(MERGE_TOKEN_PATTERN.search(cell) for cells in content_rows for cell in cells):
        return False
    data_rows = content_rows[1:]
    return all(
        1 <= len(normalized_table_content(cells[0])) <= 24
        and len(normalized_table_content(cells[1]))
        >= max(12, len(normalized_table_content(cells[0])) + 4)
        for cells in data_rows
    )


def table_block_fingerprint(block: list[tuple[int, list[str]]]) -> str:
    return "|".join(normalized_table_content(cell) for _, cells in block for cell in cells)


def validate_table_structure(
    block: list[tuple[int, list[str]]],
    allowed_legacy_structures: set[str] | None = None,
) -> list[Finding]:
    if not block:
        return []
    fingerprint = table_block_fingerprint(block)
    if allowed_legacy_structures and fingerprint in allowed_legacy_structures:
        return []

    separator_indexes = [index for index, (_, cells) in enumerate(block) if is_table_separator(cells)]
    if not separator_indexes:
        return [Finding("E", "414", block[0][0], "Every Markdown table needs a real header row followed immediately by a separator row.")]
    if separator_indexes != [1]:
        return [Finding("E", "415", block[separator_indexes[0]][0], "The Markdown separator must be the table's second row, immediately after its real header.")]

    header_number, header_cells = block[0]
    if any(MERGE_TOKEN_PATTERN.search(cell) for cell in header_cells):
        return [Finding("E", "416", header_number, "The real Markdown header row must not contain rowspan, colspan, or fn__none; start merged cells in the first data row.")]
    return []


def table_block_content_is_preserved_as_label_rule_list(
    source_block: list[tuple[int, list[str]]],
    output_text: str,
) -> bool:
    if not table_block_is_simple_label_rule(source_block):
        return False
    normalized_output = normalized_table_content(output_text)
    content_rows = [cells for _, cells in source_block if not is_table_separator(cells)]
    for cells in content_rows[1:]:
        for cell in cells:
            fragment = normalized_table_content(cell)
            if len(fragment) >= 2 and fragment not in normalized_output:
                return False
    return True


def table_block_content_is_preserved_as_axis_list(
    source_block: list[tuple[int, list[str]]],
    output_text: str,
) -> bool:
    """Allow either table axis to become list parents when every labeled cell survives."""
    if any(MERGE_TOKEN_PATTERN.search(cell) for _, cells in source_block for cell in cells):
        return False
    normalized_output = normalized_table_content(output_text)
    for _, cells in source_block:
        if is_table_separator(cells):
            continue
        for cell in cells:
            fragment = normalized_table_content(cell)
            if len(fragment) >= 2 and fragment not in normalized_output:
                return False
    return True


def table_block_content_is_preserved_in_tables(
    source_block: list[tuple[int, list[str]]],
    output_blocks: list[list[tuple[int, list[str]]]],
) -> bool:
    normalized_output_tables = normalized_table_content(
        " ".join(cell for block in output_blocks for _, cells in block for cell in cells)
    )
    for _, cells in source_block:
        if is_table_separator(cells):
            continue
        for cell in cells:
            fragment = normalized_table_content(cell)
            if len(fragment) >= 2 and fragment not in normalized_output_tables:
                return False
    return True


def validate_table_cell(cell: str, number: int, allowed_list_cells: set[str] | None = None) -> list[Finding]:
    findings: list[Finding] = []
    if TABLE_SEPARATOR_PATTERN.fullmatch(cell.replace(" ", "")):
        return findings
    if table_cell_has_large_list(cell):
        fingerprint = normalized_table_content(cell)
        if allowed_list_cells and fingerprint in allowed_list_cells:
            return findings
        findings.append(Finding("E", "412", number, "A large list does not belong inside a table cell; expand it as a real nested list outside the table."))
        return findings
    segments = re.split(r"<br\s*/>", cell)
    marker_counts = [len(ENUMERATION_PATTERN.findall(segment)) for segment in segments]
    if sum(marker_counts) >= 2 and any(count > 1 for count in marker_counts):
        findings.append(Finding("E", "401", number, "Numbered table-cell items must be separated with <br />."))
    sentence_count = len(re.findall(r"[。！？；]", cell))
    has_multiple_branches = (
        sum(marker_counts) >= 2
        or sentence_count >= 2
        or (sentence_count >= 1 and visible_length(cell) >= 50)
    )
    if (visible_length(cell) >= 70 or has_multiple_branches) and not re.search(r"<br\s*/?>", cell, re.IGNORECASE):
        findings.append(Finding("E", "403", number, "Dense table cell must use <br /> to separate semantic rule branches."))
    if (visible_length(cell) >= 80 or sentence_count >= 2) and len(style_families(cell)) < 2:
        findings.append(Finding("E", "402", number, "Long table cell needs at least two semantic inline style families."))
    return findings


def validate_merge_grid(rows: list[tuple[int, list[str]]]) -> list[Finding]:
    findings: list[Finding] = []
    content_rows = [(number, cells) for number, cells in rows if not is_table_separator(cells)]
    if not content_rows:
        return findings

    width = max(len(cells) for _, cells in rows)
    active_rows: dict[int, int] = {}
    for number, cells in content_rows:
        if len(cells) != width:
            findings.append(Finding("E", "404", number, f"Table row has {len(cells)} physical cells; expected {width}."))
            continue

        horizontal_coverage: set[int] = set()
        next_active = {column: remaining - 1 for column, remaining in active_rows.items() if remaining > 1}
        for column, cell in enumerate(cells):
            placeholder = is_merge_placeholder(cell)
            vertically_covered = column in active_rows
            horizontally_covered = column in horizontal_coverage
            if placeholder:
                if not vertically_covered and not horizontally_covered:
                    findings.append(Finding("E", "406", number, "fn__none has no matching rowspan or colspan source."))
                continue
            if vertically_covered or horizontally_covered:
                findings.append(Finding("E", "407", number, "A merged table slot must be represented by fn__none."))
                continue

            colspan_value = merge_span(cell, "colspan")
            rowspan_value = merge_span(cell, "rowspan")
            colspan = colspan_value or 1
            rowspan = rowspan_value or 1
            if colspan_value == 1 or rowspan_value == 1:
                findings.append(Finding("E", "408", number, "Do not emit redundant colspan='1' or rowspan='1' attributes."))
            if column + colspan > width:
                findings.append(Finding("E", "409", number, "colspan extends beyond the table's physical column count."))
                continue
            if any(target in active_rows for target in range(column, column + colspan)):
                findings.append(Finding("E", "410", number, "A new merged cell overlaps an active rowspan."))
                continue
            horizontal_coverage.update(range(column + 1, column + colspan))
            if rowspan > 1:
                for target in range(column, column + colspan):
                    next_active[target] = max(next_active.get(target, 0), rowspan - 1)

        for column in set(active_rows) | horizontal_coverage:
            if not is_merge_placeholder(cells[column]):
                findings.append(Finding("E", "407", number, "A merged table slot must be represented by fn__none."))
        active_rows = next_active
    return findings


def validate_tables(
    text: str,
    allowed_list_cells: set[str] | None = None,
    allowed_label_rule_tables: set[str] | None = None,
    allowed_legacy_structures: set[str] | None = None,
) -> list[Finding]:
    findings: list[Finding] = []
    for number, line in enumerate(text.splitlines(), start=1):
        if not TABLE_ROW_PATTERN.match(line):
            continue
        for cell in split_table_cells(line):
            findings.extend(validate_table_cell(cell, number, allowed_list_cells))
    for block in table_blocks(text):
        findings.extend(validate_table_structure(block, allowed_legacy_structures))
        findings.extend(validate_merge_grid(block))
        if table_block_is_simple_label_rule(block):
            fingerprint = table_block_fingerprint(block)
            if not allowed_label_rule_tables or fingerprint not in allowed_label_rule_tables:
                findings.append(Finding("E", "413", block[0][0], "A two-column label-and-explanation structure should be a real Markdown list unless it has another comparison axis."))
    return findings


def validate_table_size(
    text: str,
    profile: str,
    max_columns: int,
    max_data_rows: int,
    allowed_source_tables: set[str] | None = None,
) -> list[Finding]:
    findings: list[Finding] = []
    for block in table_blocks(text):
        if allowed_source_tables and table_block_fingerprint(block) in allowed_source_tables:
            continue
        data_rows = [row for index, row in enumerate(block) if index >= 2 and not is_table_separator(row[1])]
        width = max(len(cells) for _, cells in block)
        if width > max_columns or len(data_rows) > max_data_rows:
            findings.append(
                Finding(
                    "E",
                    "411",
                    block[0][0],
                    f"{profile} tables must be at most {max_columns} columns by {max_data_rows} data rows; split larger comparisons semantically or explicitly raise --max-table-columns/--max-table-rows when the larger table is necessary.",
                )
            )
    return findings


def validate_list_density(text: str) -> list[Finding]:
    findings: list[Finding] = []
    run_start = None
    run_indent = None
    run_count = 0

    def flush() -> None:
        nonlocal run_start, run_indent, run_count
        if run_start is not None and run_count > 5:
            findings.append(Finding("W", "610", run_start, "同级列表超过 5 项；请按主体、阶段、条件或后果改成语义子列表。"))
        run_start = None
        run_indent = None
        run_count = 0

    for number, line in enumerate(text.splitlines() + [""], start=1):
        match = re.match(r"^(?P<indent>\s*)(?:[-*]|\d+\.)\s+", line)
        if not match or re.search(r"[-*]\s+\[[ xX]\]", line):
            flush()
            continue
        indent = len(match.group("indent").replace("\t", "    "))
        if run_indent == indent:
            run_count += 1
        else:
            flush()
            run_start = number
            run_indent = indent
            run_count = 1
    return findings


def ial_attributes(line: str) -> dict[str, str]:
    match = IAL_PATTERN.fullmatch(line.strip())
    if not match:
        return {}
    return {item.group("key"): item.group("value") for item in IAL_ATTRIBUTE_PATTERN.finditer(match.group("attrs"))}


def parse_topic_ids(value: str) -> tuple[list[str], list[str]]:
    values = [item.strip() for item in value.split(",")]
    invalid = [item for item in values if not STABLE_TOPIC_ID_PATTERN.fullmatch(item)]
    return values, invalid


def validate_topic_ials(text: str, profile: str, require_note_topic: bool = False) -> list[Finding]:
    findings: list[Finding] = []
    lines = text.splitlines()
    note_topic_count = 0

    for index, line in enumerate(lines):
        attrs = ial_attributes(line)
        if not attrs:
            continue
        line_no = index + 1
        note_topic_id = attrs.get("custom-qb-note-topic-id")
        question_topic_ids = attrs.get("custom-qb-question-topic-ids")

        if "custom-qb-role" in attrs or "custom-qb-topic-id" in attrs or "custom-qb-topic-ids" in attrs:
            findings.append(Finding("E", "805", line_no, "Legacy topic attributes are not valid new output; use custom-qb-note-topic-id or custom-qb-question-topic-ids."))

        if note_topic_id is not None:
            note_topic_count += 1
            previous = lines[index - 1].strip() if index > 0 else ""
            if not STABLE_TOPIC_ID_PATTERN.fullmatch(note_topic_id):
                findings.append(Finding("E", "801", line_no, "custom-qb-note-topic-id must contain exactly one lowercase ASCII kebab-case ID."))
            if not (re.match(r"^#{1,6}\s+\S", previous) or NOTE_TOPIC_ANCHOR_PATTERN.fullmatch(previous)):
                findings.append(Finding("E", "802", line_no, "custom-qb-note-topic-id must attach directly to a heading or **考点：显示名** anchor."))
            if "custom-qb-id" in attrs or question_topic_ids is not None:
                findings.append(Finding("E", "803", line_no, "A note-topic provider IAL cannot also identify or classify a question."))

        if question_topic_ids is not None:
            values, invalid = parse_topic_ids(question_topic_ids)
            if not values or invalid:
                findings.append(Finding("E", "806", line_no, "custom-qb-question-topic-ids must be a comma-separated list of lowercase ASCII kebab-case IDs."))
            if len(values) != len(set(values)):
                findings.append(Finding("E", "807", line_no, "custom-qb-question-topic-ids must not contain duplicate IDs."))
            if "custom-qb-id" not in attrs:
                findings.append(Finding("E", "808", line_no, "custom-qb-question-topic-ids must coexist with custom-qb-id."))
            if note_topic_id is not None:
                findings.append(Finding("E", "809", line_no, "A question-topic reference IAL cannot also provide note-topic material."))

    if profile == "legal-goldquest":
        for index, line in enumerate(lines):
            if not QUESTION_HEADING_PATTERN.fullmatch(line):
                continue
            attrs = ial_attributes(lines[index + 1]) if index + 1 < len(lines) else {}
            if "custom-qb-id" not in attrs:
                findings.append(Finding("E", "810", index + 1, "Every GoldQuest question heading requires an immediate IAL with custom-qb-id."))
            if "custom-qb-question-topic-ids" not in attrs:
                findings.append(Finding("E", "811", index + 1, "Every GoldQuest question IAL requires custom-qb-question-topic-ids."))
            if "custom-qb-note-topic-id" in attrs:
                findings.append(Finding("E", "812", index + 2, "GoldQuest question IAL must not use custom-qb-note-topic-id."))

    if profile == "legal-marknote" and require_note_topic and note_topic_count == 0:
        findings.append(Finding("E", "804", 1, "Normal MarkNote output requires at least one custom-qb-note-topic-id provider declaration."))
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

def validate_marknote_richness(text: str) -> list[Finding]:
    findings: list[Finding] = []
    lines = text.splitlines()
    body_lines: list[str] = []
    in_fence = False
    visuals = visual_families(text)
    has_callout = False
    has_table = False
    has_subheading = False
    has_divider = False
    nested_items = 0
    top_level_items = 0

    for number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith(("```", "> ```")):
            in_fence = not in_fence
            continue
        if in_fence or not stripped:
            continue
        if TABLE_ROW_PATTERN.match(line):
            has_table = True
            continue
        if IAL_PATTERN.match(stripped):
            continue
        if re.match(r"^-{3,}$", stripped):
            has_divider = True
            continue
        if re.match(r"^#{1,6}\s+", stripped):
            if re.match(r"^#{3,6}\s+", stripped):
                has_subheading = True
            continue
        if re.match(r"^\s*>\s*\[!(?:TIP|NOTE|IMPORTANT|CAUTION|WARNING)\]", line):
            has_callout = True
            continue
        if re.match(r"^\s*-\s+", line):
            if len(line) - len(line.lstrip()) >= 4:
                nested_items += 1
            else:
                top_level_items += 1
        prose_length = prose_visible_length(stripped)
        if prose_length > 42:
            findings.append(Finding("E", "621", number, "MarkNote prose lines must stay within 42 visible characters; split the logic into semantic sublists."))
        if prose_length >= 14 and not COLOR_ATTRIBUTE_PATTERN.search(stripped):
            findings.append(Finding("E", "622", number, "Each substantive MarkNote line needs at least one short semantic color anchor."))
        body_lines.append(line)

    body = "\n".join(body_lines)
    body_prose = prose_without_fenced_blocks(body)
    subject_pattern = re.compile("|".join(re.escape(term) for term in sorted(COMMON_SUBJECT_TERMS, key=len, reverse=True)))
    subject_scan_text = re.sub(r"(?:选项|第)[甲乙丙丁戊]|[甲乙丙丁戊]项", "", body_prose)
    subject_tokens = subject_pattern.findall(subject_scan_text)
    for term in set(subject_tokens):
        styled_occurrences = [match for match in STYLED_TERM_PATTERN.finditer(body_prose) if match.group("term") == term]
        occurrences = subject_tokens.count(term)
        if not styled_occurrences:
            findings.append(Finding("E", "625", 1, f"MarkNote subject '{term}' needs an actively assigned semantic color."))
        elif len(styled_occurrences) < occurrences:
            findings.append(Finding("E", "623", 1, f"MarkNote subject '{term}' has uncolored occurrences; reuse its established color everywhere."))

    auxiliary_styles = style_families(body) & {"highlight", "italic", "strike", "code", "underline"}
    body_length = prose_visible_length(body_prose)
    sentence_count = len(re.findall(r"[。！？；]", body_prose))
    branch_count = top_level_items + nested_items
    medium_complexity = body_length >= 160 or sentence_count >= 4 or branch_count >= 3
    if medium_complexity and len(auxiliary_styles) < 4:
        findings.append(Finding("E", "620", 1, "Medium-or-higher complexity MarkNote needs at least four auxiliary style families among highlight, italic, strikethrough, inline code, and underline."))
    if medium_complexity and not visuals:
        findings.append(Finding("E", "624", 1, "Medium-or-higher complexity MarkNote needs one intentional SiYuan visual: editable Mermaid, a div-wrapped HTML block, or an SVG/PNG image whose alt text identifies it as a visualization."))
    structural_styles = {
        name
        for name, present in (
            ("nested-list", nested_items > 0),
            ("callout", has_callout),
            ("subheading", has_subheading),
            ("table", has_table),
            ("visual", bool(visuals)),
            ("divider", has_divider),
        )
        if present
    }
    if medium_complexity and len(structural_styles) < 4:
        findings.append(Finding("E", "626", 1, "Medium-or-higher complexity MarkNote needs at least four structural families: nested list, Callout, subheading, table, visual, or divider."))
    background_anchor_count = len(re.findall(r"b3-font-background(?:[2-9]|1[0-3])", body))
    if medium_complexity and background_anchor_count < 3:
        findings.append(Finding("E", "627", 1, "Medium-or-higher complexity MarkNote needs at least three short background-color anchors for visual hierarchy."))
    if medium_complexity and not has_semantic_emoji_label(body):
        findings.append(Finding("W", "509", 1, "Medium-or-higher complexity MarkNote needs at least one semantic emoji leading a list or Callout label; decision emojis alone do not satisfy this cue."))
    findings.extend(validate_concept_list_palette(text))
    return findings


def validate_concept_list_palette(text: str) -> list[Finding]:
    """Flag visually monotonous runs while leaving semantic equivalence to review."""
    findings: list[Finding] = []
    run: list[tuple[int, str, str]] = []
    run_key: tuple[str, str] | None = None

    def flush() -> None:
        nonlocal run, run_key
        if len(run) >= 3 and len({term for _, term, _ in run}) >= 3:
            findings.append(
                Finding(
                    "W",
                    "503",
                    run[0][0],
                    "Three or more peer concept items reuse one identical lead-anchor style; split concepts into legal-function color slots, or keep the shared color and add a second visual dimension when they truly share one role.",
                )
            )
        run = []
        run_key = None

    in_fence = False
    for number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith(("```", "> ```")):
            in_fence = not in_fence
            flush()
            continue
        if in_fence or not stripped:
            flush()
            continue
        match = CONCEPT_LIST_LEAD_PATTERN.match(line)
        if not match:
            flush()
            continue
        style = ";".join(sorted(part.strip() for part in match.group("style").split(";") if part.strip()))
        key = (match.group("quote") + match.group("indent"), style)
        if run_key != key:
            flush()
            run_key = key
        run.append((number, match.group("term").strip(), style))
    flush()
    return findings

def validate_paragraph_parent_fragmentation(text: str) -> list[Finding]:
    """Flag repeated paragraph-plus-short-list groups that should form one hierarchy."""
    lines = text.splitlines()
    groups: list[tuple[int, int]] = []
    in_fence = False
    index = 0
    while index < len(lines):
        stripped = lines[index].strip()
        if stripped.startswith(("```", "> ```")):
            in_fence = not in_fence
            index += 1
            continue
        if (
            in_fence
            or not stripped
            or stripped.startswith(("#", ">", "|", "- ", "* ", "+ ", "```"))
            or IAL_PATTERN.match(stripped)
            or re.match(r"^\d+[.)]\s+", stripped)
        ):
            index += 1
            continue
        parent_line = index + 1
        cursor = index + 1
        while cursor < len(lines) and not lines[cursor].strip():
            cursor += 1
        child_count = 0
        while cursor < len(lines) and re.match(r"^\s*(?:[-+*]|\d+[.)])\s+", lines[cursor]):
            child_count += 1
            cursor += 1
        if 2 <= child_count <= 3:
            groups.append((parent_line, cursor))
            index = cursor
        else:
            index += 1

    findings: list[Finding] = []
    for first, second in zip(groups, groups[1:]):
        between = lines[first[1] : second[0] - 1]
        if all(not line.strip() for line in between):
            findings.append(
                Finding(
                    "W",
                    "504",
                    first[0],
                    "Repeated paragraph-plus-2-or-3-item groups should usually become peer parent list items with their original items nested beneath them; keep paragraphs only for independent conclusions or transitions.",
                )
            )
            break
    return findings


def validate_concept_headings(text: str, profile: str) -> list[Finding]:
    if profile != "legal-marknote":
        return []

    findings: list[Finding] = []
    lines = text.splitlines()
    in_fence = False
    in_exercise_region = False

    for index, line in enumerate(lines):
        if re.match(r"^(?:\s*>\s*)?```", line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        heading = ANY_HEADING_PATTERN.fullmatch(line)
        if heading:
            title = heading.group("title").strip()
            if EXERCISE_REGION_PATTERN.search(title):
                in_exercise_region = True
            elif (
                in_exercise_region
                and not NUMERIC_ONLY_HEADING_PATTERN.fullmatch(line)
                and not EXERCISE_CONTINUATION_PATTERN.fullmatch(title)
            ):
                in_exercise_region = False

        if in_exercise_region or not NUMERIC_ONLY_HEADING_PATTERN.fullmatch(line):
            continue

        cursor = index + 1
        while cursor < len(lines) and (not lines[cursor].strip() or IAL_PATTERN.fullmatch(lines[cursor].strip())):
            cursor += 1
        if cursor >= len(lines):
            continue

        body = lines[cursor].strip()
        if body.startswith((">", "|", "- ", "* ", "```")):
            continue
        definition = SHORT_CONCEPT_DEFINITION_PATTERN.fullmatch(body)
        if not definition:
            continue

        term = re.sub(r"[`*_~=]", "", definition.group("term")).strip()
        if (
            term in NON_CONCEPT_LABELS
            or visible_length(term) > 16
            or re.search(r"[。！？；?!]", term)
            or re.search(r"(?:下列|以下|何者|哪些|是否|如何|为什么)", term)
        ):
            continue
        findings.append(
            Finding(
                "E",
                "705",
                index + 1,
                f"Numeric-only concept heading must include the short term '{term}'; move it into the heading and remove the duplicate body prefix before the colon.",
            )
        )

    return findings


def validate_goldquest(text: str) -> list[Finding]:
    findings: list[Finding] = []
    lines = text.splitlines()
    if re.search(r"📌\s*\[|\[(?:总结与归纳|提示|易错|重点)\]", text):
        findings.append(Finding("E", "608", 1, "Use a semantic Callout instead of a pseudo-callout marker."))
    for number, line in enumerate(lines, start=1):
        if re.search(r"-\s*\[[xX]\]", line):
            findings.append(Finding("E", "601", number, "Question options must remain unchecked."))
    for match in STYLED_TERM_PATTERN.finditer(text):
        term = match.group("term")
        line = line_for_offset(text, match.start())
        if visible_length(term) > 8:
            findings.append(Finding("E", "617", line, "GoldQuest color anchors must stay within 8 visible characters; color only the decisive retrieval term."))
        if re.search(r"[，。；：、,.!?！？]", term):
            findings.append(Finding("E", "618", line, "Punctuation must remain outside a GoldQuest color anchor."))
    task_options = [number for number, line in enumerate(lines, start=1) if re.search(r"-\s*\[[ xX]\]", line)]
    answer_headings = [number for number, line in enumerate(lines, start=1) if re.match(r"^######\s+答案与解析\s*$", line)]
    if task_options and not answer_headings:
        findings.append(Finding("E", "603", task_options[0], "Question options require a separate '###### 答案与解析' section."))

    h5_indices = [index for index, line in enumerate(lines) if re.match(r"^#####\s+", line) and not re.match(r"^######", line)]
    for index in h5_indices:
        end = next((candidate for candidate in range(index + 1, len(lines)) if re.match(r"^#{1,5}\s+", lines[candidate])), len(lines))
        answer_heading = next((candidate for candidate in range(index + 1, end) if re.match(r"^######\s+答案与解析\s*$", lines[candidate])), None)
        solution_ial = next(
            (
                candidate
                for candidate in range(index + 1, end)
                if ial_attributes(lines[candidate]).get("custom-qb-section") == "solution"
            ),
            None,
        )
        visible_answer = next(
            (
                candidate
                for candidate in range(index + 1, end)
                if VISIBLE_ANSWER_LINE_PATTERN.match(lines[candidate])
            ),
            None,
        )

        if answer_heading is None:
            if solution_ial is not None or visible_answer is not None:
                findings.append(Finding("E", "613", index + 1, "Each GoldQuest question needs its own '###### 答案与解析' heading before the solution block."))
            else:
                findings.append(Finding("E", "614", index + 1, "GoldQuest question is missing its answer heading and custom-qb-section='solution' boundary."))
                continue

        answer_line = solution_ial - 1 if solution_ial is not None and solution_ial > index else None
        answer_contract_valid = (
            answer_heading is not None
            and solution_ial is not None
            and answer_line is not None
            and VISIBLE_ANSWER_LINE_PATTERN.match(lines[answer_line]) is not None
            and next((candidate for candidate in range(answer_heading + 1, solution_ial) if lines[candidate].strip()), None) == answer_line
        )
        if not answer_contract_valid:
            findings.append(Finding("E", "606", (answer_heading or visible_answer or index) + 1, "Answer section must start with a visible answer line immediately followed by custom-qb-section='solution'."))

        boundary = answer_heading if answer_heading is not None else (visible_answer if visible_answer is not None else solution_ial)
        if boundary is None:
            continue
        question_text = "\n".join(lines[index + 1:boundary])
        question_lines = lines[index + 1:boundary]
        parenthesized_subquestions: list[tuple[int, str, list[re.Match[str]]]] = []
        for relative_index, question_line in enumerate(question_lines, start=index + 2):
            if IAL_PATTERN.fullmatch(question_line.strip()) or re.search(r"-\s*\[[ xX]\]", question_line):
                continue
            markers = list(re.finditer(r"[（(]\s*\d+\s*[）)]", question_line))
            if markers:
                parenthesized_subquestions.append((relative_index, question_line, markers))
            if len(markers) > 1:
                findings.append(Finding("E", "628", relative_index, "Each GoldQuest subquestion must occupy its own line; split the shared stem and every numbered question."))
                continue
            if markers:
                prefix = question_line[:markers[0].start()]
                prefix = re.sub(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)", "", prefix).strip()
                if prefix and not re.fullmatch(r"\*\*问题", prefix):
                    findings.append(Finding("E", "628", relative_index, "A numbered GoldQuest subquestion must start its own list line, separate from the shared stem."))
        if sum(len(markers) for _, _, markers in parenthesized_subquestions) >= 2:
            has_stem_label = any(re.match(r"^\s*[-*+]\s+\*\*题干\*\*[：:]", line) for line in question_lines)
            has_question_label = any(re.match(r"^\s*[-*+]\s+\*\*问题\*\*[：:]", line) for line in question_lines)
            if not (has_stem_label and has_question_label):
                findings.append(Finding("E", "629", index + 1, "Multi-part GoldQuest questions need separate **题干** and **问题** blocks before the one-line subquestions."))
        question_attrs = next(
            (
                ial_attributes(lines[candidate])
                for candidate in range(index + 1, boundary)
                if "custom-qb-id" in ial_attributes(lines[candidate])
            ),
            {},
        )
        if re.search(r"-\s*\[[ xX]\]", question_text) and not question_attrs.get("custom-qb-answer"):
            findings.append(Finding("E", "619", index + 1, "Objective GoldQuest questions need custom-qb-answer in the question IAL for Damophus hiding and grading."))
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

        legacy_mask = next((candidate for candidate in range(index + 1, end) if LEGACY_ANSWER_MASK_PATTERN.search(lines[candidate])), None)
        if legacy_mask is not None:
            findings.append(Finding("E", "607", legacy_mask + 1, "Legacy HTML answer masks are not allowed; Damophus masks the answer through custom-qb-answer and custom-qb-section='solution'."))

        analysis_start = solution_ial + 1 if solution_ial is not None else ((visible_answer or boundary) + 1)
        answer_lines = lines[analysis_start:end]
        analysis_text = "\n".join(answer_lines)
        analysis_prose = prose_without_fenced_blocks(analysis_text)
        option_gate = validate_option_analysis(question_lines, answer_lines, analysis_start + 1, question_attrs.get("custom-qb-answer", ""))
        findings.extend(Finding("E", item.code, item.line, item.message) for item in option_gate.findings)
        analysis_subject_styles = {
            match.group("term")
            for match in STYLED_TERM_PATTERN.finditer(analysis_prose)
            if match.group("term") in COMMON_SUBJECT_TERMS
            or (
                2 <= len(match.group("term")) <= 3
                and match.group("term")[0] in COMMON_SURNAME_INITIALS
                and re.fullmatch(r"[\u4e00-\u9fff]+", match.group("term"))
            )
        }
        all_styled_terms = {
            match.group("term")
            for match in STYLED_TERM_PATTERN.finditer(analysis_prose)
        }
        for term in analysis_subject_styles:
            styled_form = re.compile(
                rf'\*\*{re.escape(term)}\*\*\{{:\s*style="[^"]*b3-font-(?:color|background)\d+[^\"]*"\}}'
            )
            remaining_prose = styled_form.sub("", analysis_prose)
            for other in all_styled_terms:
                if other != term and term in other:
                    longer_form = re.compile(
                        rf'\*\*{re.escape(other)}\*\*\{{:\s*style="[^"]*b3-font-(?:color|background)\d+[^\"]*"\}}'
                    )
                    remaining_prose = longer_form.sub("", remaining_prose)
            remaining_prose = re.sub(r"(?:选项|第)[甲乙丙丁戊]|[甲乙丙丁戊]项", "", remaining_prose)
            if term in remaining_prose:
                findings.append(Finding("E", "623", index + 1, f"Term '{term}' has uncolored occurrences in the analysis; reuse its established color every time."))

        subject_pattern = re.compile("|".join(re.escape(term) for term in sorted(COMMON_SUBJECT_TERMS, key=len, reverse=True)))
        subject_scan_text = re.sub(r"(?:选项|第)[甲乙丙丁戊]|[甲乙丙丁戊]项", "", analysis_prose)
        subject_tokens = subject_pattern.findall(subject_scan_text)
        for term in set(subject_tokens):
            occurrences = subject_tokens.count(term)
            styled_occurrences = [
                match
                for match in STYLED_TERM_PATTERN.finditer(analysis_prose)
                if match.group("term") == term
            ]
            if not styled_occurrences:
                findings.append(Finding("E", "625", index + 1, f"Analysis subject '{term}' needs an actively assigned semantic color."))
            elif len(styled_occurrences) < occurrences:
                findings.append(Finding("E", "623", index + 1, f"Analysis subject '{term}' has uncolored occurrences; reuse its established color everywhere in the analysis."))

        uncolored_sentences = 0
        top_level_analysis_items = 0
        nested_analysis_items = 0
        has_analysis_callout = False
        has_analysis_subheading = False
        has_analysis_table = False
        analysis_visuals = visual_families(analysis_text)
        has_analysis_divider = False
        in_analysis_fence = False
        for number, line in enumerate(answer_lines, start=analysis_start + 1):
            stripped = line.strip()
            if stripped.startswith(("```", "> ```")):
                in_analysis_fence = not in_analysis_fence
                continue
            if in_analysis_fence:
                continue
            if not stripped or LEGACY_ANSWER_MASK_PATTERN.search(line) or stripped.startswith("|"):
                if TABLE_ROW_PATTERN.match(line):
                    has_analysis_table = True
                continue
            if re.match(r"^-{3,}$", stripped):
                has_analysis_divider = True
                continue
            if IAL_PATTERN.match(stripped):
                continue
            if re.match(r"^#{1,6}\s+", stripped):
                if re.match(r"^######\s+(?!答案与解析).+", stripped):
                    has_analysis_subheading = True
                continue
            if re.match(r"^\s*>\s*\[!(?:TIP|NOTE|IMPORTANT|CAUTION|WARNING)\]", line):
                has_analysis_callout = True
                continue
            if re.match(r"^\s*-\s+", line):
                if len(line) - len(line.lstrip()) >= 4:
                    nested_analysis_items += 1
                else:
                    top_level_analysis_items += 1
            sentence_count = len(re.findall(r"[。！？；]", stripped))
            prose_length = prose_visible_length(stripped)
            if prose_length > 42 and number not in option_gate.replay_lines:
                findings.append(Finding("E", "621", number, "Analysis prose lines must stay within 42 visible characters; split the logic into a lead line and semantic sublist."))
            if prose_length >= 14 and not COLOR_ATTRIBUTE_PATTERN.search(stripped):
                findings.append(Finding("E", "622", number, "Each substantive analysis line needs at least one short semantic color anchor."))
            if sentence_count == 0 and visible_length(stripped) >= 35:
                sentence_count = 1
            if sentence_count == 0:
                continue
            color_anchor_count = len(COLOR_ATTRIBUTE_PATTERN.findall(stripped))
            if sentence_count >= 3 and color_anchor_count * 2 < sentence_count:
                findings.append(Finding("E", "616", number, "A long analysis line needs at least one semantic color anchor per one or two sentences."))
            if color_anchor_count:
                uncolored_sentences = 0
            else:
                uncolored_sentences += sentence_count
            if uncolored_sentences >= 3:
                findings.append(Finding("E", "609", number, "答案与解析连续三句没有语义颜色锚点。"))
                break
        has_relational_structure = nested_analysis_items > 0 or has_analysis_callout or has_analysis_subheading or has_analysis_table
        if top_level_analysis_items >= 3 and not has_relational_structure:
            findings.append(Finding("E", "615", analysis_start + 1, "Multiple independent analysis branches need an indented sublist, stage heading, small table, or semantic Callout; flat peer bullets and bold-only formatting are insufficient."))
        auxiliary_styles = style_families(analysis_text) & {"highlight", "italic", "strike", "code", "underline"}
        analysis_length = prose_visible_length(prose_without_fenced_blocks(analysis_text))
        analysis_sentence_count = len(re.findall(r"[。！？；]", prose_without_fenced_blocks(analysis_text)))
        branch_count = top_level_analysis_items + nested_analysis_items
        medium_complexity = analysis_length >= 160 or branch_count >= 3 or analysis_sentence_count >= 4
        if medium_complexity and len(auxiliary_styles) < 4:
            findings.append(Finding("E", "620", analysis_start + 1, "Medium-or-higher complexity analysis needs at least four auxiliary style families among highlight, italic, strikethrough, inline code, and underline."))
        if medium_complexity and not analysis_visuals:
            findings.append(Finding("E", "624", analysis_start + 1, "Medium-or-higher complexity analysis needs one intentional SiYuan visual: editable Mermaid, a div-wrapped HTML block, or an SVG/PNG image whose alt text identifies it as a visualization."))
        structural_styles = {
            name
            for name, present in (
                ("nested-list", nested_analysis_items > 0),
                ("callout", has_analysis_callout),
                ("subheading", has_analysis_subheading),
                ("table", has_analysis_table),
                ("visual", bool(analysis_visuals)),
                ("divider", has_analysis_divider),
            )
            if present
        }
        if medium_complexity and len(structural_styles) < 4:
            findings.append(Finding("E", "626", analysis_start + 1, "Medium-or-higher complexity analysis needs at least four structural families: nested list, Callout, subheading, table, visual, or divider."))
        background_anchor_count = len(re.findall(r"b3-font-background(?:[2-9]|1[0-3])", analysis_text))
        if medium_complexity and background_anchor_count < 3:
            findings.append(Finding("E", "627", analysis_start + 1, "Medium-or-higher complexity analysis needs at least three short background-color anchors for strong visual hierarchy."))
        if medium_complexity and not has_semantic_emoji_label(analysis_text):
            findings.append(Finding("W", "509", analysis_start + 1, "Medium-or-higher complexity analysis needs at least one semantic emoji leading a list or Callout label; option decision emojis do not satisfy this cue."))
    return findings


def normalize_source_heading(title: str) -> str:
    title = re.sub(r"\{:[^}]+\}", "", title)
    title = re.sub(r"!\[([^]]*)\]\([^)]*\)", r"\1", title)
    title = re.sub(r"[`*_~=]", "", title)
    title = re.sub(r"(?<=\d)\s*(?=[\u3400-\u9fff])", " ", title)
    title = re.sub(r"\s+", " ", title).strip()
    return re.sub(r"\s*[:：]\s*$", "", title)


def is_repairable_source_heading(title: str) -> bool:
    normalized = normalize_source_heading(title)
    compact = re.sub(r"\s+", "", normalized)
    return bool(
        re.fullmatch(r"(?:\d+[.、]?|[（(]?\d+[）)]|[①-⑳])", compact)
        or re.fullmatch(r"例\s*\d+", normalized)
        or normalized in {"热点"}
    )


def normalize_analysis_scaffold_label(value: str) -> str:
    value = re.sub(r"\{:\s*[^}\n]*\}", "", value)
    value = re.sub(r"!\[([^]]*)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"[`*_~=]", "", value)
    value = re.sub(r"\s+", "", value).strip()
    return value.rstrip("：:")


def goldquest_analysis_sections(text: str) -> list[list[str]]:
    lines = text.splitlines()
    sections: list[list[str]] = []
    for index, line in enumerate(lines):
        if not re.fullmatch(r"######\s+答案与解析\s*", line):
            continue
        end = next(
            (candidate for candidate in range(index + 1, len(lines)) if QUESTION_HEADING_PATTERN.fullmatch(lines[candidate])),
            len(lines),
        )
        sections.append(lines[index + 1 : end])
    return sections


def goldquest_analysis_scaffold_labels(text: str) -> set[str]:
    labels: set[str] = set()
    list_item = re.compile(r"^(?P<indent>\s*)(?:[-+*]|\d+[.)])\s+(?P<body>.+?)\s*$")
    for section in goldquest_analysis_sections(text):
        for index, line in enumerate(section):
            parent = list_item.match(line)
            if not parent:
                continue
            child = next((candidate for candidate in section[index + 1 :] if candidate.strip()), "")
            child_match = list_item.match(child)
            if not child_match or len(child_match.group("indent").expandtabs(4)) <= len(parent.group("indent").expandtabs(4)):
                continue
            label = normalize_analysis_scaffold_label(parent.group("body"))
            if 2 <= len(label) <= 24 and not label.startswith(("正确答案", "破绽", "破题点")):
                labels.add(label)
    return labels


def goldquest_analysis_structural_labels(text: str) -> set[str]:
    labels: set[str] = set()
    list_item = re.compile(r"^\s*(?:[-+*]|\d+[.)])\s+(?P<body>.+?)\s*$")
    for section in goldquest_analysis_sections(text):
        for line in section:
            heading = re.fullmatch(r"#{1,6}\s+(?P<body>.+?)\s*", line)
            item = list_item.match(line)
            if heading or item:
                label = normalize_analysis_scaffold_label((heading or item).group("body"))
                if label:
                    labels.add(label)
    return labels


def validate_source_preservation(
    text: str,
    source_text: str,
    profile: str,
    allow_structural_repair: bool = False,
) -> list[Finding]:
    findings: list[Finding] = []
    for image in IMAGE_PATTERN.findall(source_text):
        if image not in IMAGE_PATTERN.findall(text):
            findings.append(Finding("E", "701", 1, f"Source image link was not preserved: {image}"))
    source_table_blocks = table_blocks(source_text)
    output_table_blocks = table_blocks(text)
    source_tables = sum(len(block) for block in source_table_blocks)
    output_tables = sum(len(block) for block in output_table_blocks)
    preserves_table_content = table_cell_content_is_preserved(source_table_blocks, text)
    preserves_label_rule_content = all(
        table_block_content_is_preserved_as_label_rule_list(block, text)
        or table_block_content_is_preserved_in_tables(block, output_table_blocks)
        for block in source_table_blocks
    )
    preserves_axis_list_content = all(
        table_block_content_is_preserved_as_axis_list(block, text)
        or table_block_content_is_preserved_in_tables(block, output_table_blocks)
        for block in source_table_blocks
    )
    allows_structural_table_change = preserves_table_content and (
        len(output_table_blocks) > len(source_table_blocks)
        or all(
            table_block_has_large_list(block)
            or table_block_content_is_preserved_in_tables(block, output_table_blocks)
            for block in source_table_blocks
        )
    )
    allows_structural_table_change = allows_structural_table_change or (
        preserves_label_rule_content
        and all(
            table_block_is_simple_label_rule(block)
            or table_block_has_large_list(block)
            or table_block_content_is_preserved_in_tables(block, output_table_blocks)
            for block in source_table_blocks
        )
    )
    allows_structural_table_change = allows_structural_table_change or preserves_axis_list_content
    if output_tables < source_tables and not allows_structural_table_change:
        findings.append(Finding("E", "702", 1, f"Output has fewer Markdown table rows than source ({output_tables} < {source_tables})."))
    for token in MERGE_TOKEN_PATTERN.findall(source_text):
        if text.count(token) < source_text.count(token) and not allows_structural_table_change:
            findings.append(Finding("E", "703", 1, f"Source SiYuan table merge token was not preserved: {token}"))
    if profile == "legal-marknote":
        output_headings = [
            normalize_source_heading(heading)
            for heading in re.findall(r"^#{1,6}\s+(.+?)\s*$", text, re.MULTILINE)
        ]
        remaining = Counter(output_headings)
        for heading in re.findall(r"^#{1,6}\s+(.+?)\s*$", source_text, re.MULTILINE):
            normalized = normalize_source_heading(heading)
            if remaining[normalized]:
                remaining[normalized] -= 1
            elif allow_structural_repair and is_repairable_source_heading(heading):
                continue
            else:
                findings.append(Finding("E", "704", 1, f"Source heading was not preserved: {heading}"))
    if profile == "legal-goldquest":
        source_scaffolds = goldquest_analysis_scaffold_labels(source_text)
        if len(source_scaffolds) >= 2:
            output_structures = goldquest_analysis_structural_labels(text)
            missing = sorted(label for label in source_scaffolds if label not in output_structures)
            if missing:
                findings.append(
                    Finding(
                        "E",
                        "633",
                        1,
                        "Source analysis has a semantic parent/child rule map that must remain a structural map alongside option replays; missing parents: " + ", ".join(missing),
                    )
                )
    return findings


def validate_text(
    text: str,
    profile: str,
    source_text: str | None = None,
    require_note_topic: bool = False,
    allow_structural_repair: bool = False,
    max_table_columns: int = 3,
    max_table_rows: int = 3,
) -> list[Finding]:
    findings = []
    findings.extend(validate_highlights(text))
    findings.extend(validate_emphasis_syntax(text))
    findings.extend(validate_colors(text))
    findings.extend(validate_callouts_and_fences(text))
    allowed_list_cells = {
        normalized_table_content(cell)
        for block in table_blocks(source_text or "")
        for _, cells in block
        for cell in cells
        if table_cell_has_large_list(cell)
    }
    allowed_label_rule_tables = {
        table_block_fingerprint(block)
        for block in table_blocks(source_text or "")
        if table_block_is_simple_label_rule(block)
    }
    allowed_legacy_structures = {
        table_block_fingerprint(block)
        for block in table_blocks(source_text or "")
    }
    findings.extend(
        validate_table_size(
            text,
            profile,
            max_table_columns,
            max_table_rows,
            allowed_legacy_structures,
        )
    )
    findings.extend(
        validate_tables(
            text,
            allowed_list_cells,
            allowed_label_rule_tables,
            allowed_legacy_structures,
        )
    )
    findings.extend(validate_list_density(text))
    findings.extend(validate_general_density(text))
    if profile in {"legal-marknote", "legal-goldquest"}:
        findings.extend(Finding(item.level, item.code, item.line, item.message) for item in validate_marknote_prose_structure(text))
    if profile == "legal-marknote":
        findings.extend(validate_marknote_richness(text))
        findings.extend(validate_paragraph_parent_fragmentation(text))
    findings.extend(validate_concept_headings(text, profile))
    findings.extend(validate_topic_ials(text, profile, require_note_topic))
    if profile == "legal-goldquest":
        findings.extend(validate_goldquest(text))
    if source_text is not None:
        findings.extend(validate_source_preservation(text, source_text, profile, allow_structural_repair))
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
    parser.add_argument("--max-table-columns", type=int, help="Override the table column gate (default 3; strict default 2).")
    parser.add_argument("--max-table-rows", type=int, help="Override the table data-row gate (default 3; strict default 2).")
    parser.add_argument("--require-topic-ial", action="store_true", help="Require at least one MarkNote note-topic provider declaration.")
    parser.add_argument(
        "--allow-structural-repair",
        action="store_true",
        help="Allow recognized source shell headings to be repaired or demoted while preserving substantive headings.",
    )
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
    if (args.max_table_columns is not None and args.max_table_columns < 1) or (args.max_table_rows is not None and args.max_table_rows < 1):
        print("--max-table-columns and --max-table-rows must be positive integers.", file=sys.stderr)
        return 2
    text = args.output.read_text(encoding="utf-8")
    source_text = args.source.read_text(encoding="utf-8") if args.source else None
    findings = validate_text(
        text,
        args.profile,
        source_text,
        args.require_topic_ial,
        args.allow_structural_repair,
        args.max_table_columns if args.max_table_columns is not None else (2 if args.strict else 3),
        args.max_table_rows if args.max_table_rows is not None else (2 if args.strict else 3),
    )
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
