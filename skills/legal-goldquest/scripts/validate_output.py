#!/usr/bin/env python3
"""Validate generated legal-study Markdown against shared and profile rules."""
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
import json
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from legal_goldquest_option_gate import validate_option_analysis  # noqa: E402
from legal_goldquest_semantic_structure_gate import validate_semantic_structure, visual_families  # noqa: E402
from legal_marknote_prose_gate import validate_marknote_prose_structure  # noqa: E402
from legal_mermaid_semantics_gate import validate_mermaid_semantics  # noqa: E402

ALLOWED_CALLOUTS = {"TIP", "NOTE", "IMPORTANT", "CAUTION", "WARNING", "QUESTION"}
GENERIC_QUESTION_TITLE_PATTERN = re.compile(
    r"^✏️\s+(?:习题|试一试|练习题|真题|题目)(?:\s*[一二三四五六七八九十\d]+)?$"
)
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
MERGE_TOKEN_PATTERN = re.compile(r"\{:\s*(?:colspan='\d+'|rowspan='\d+'|class='fn__none')\}")
TABLE_ROW_PATTERN = re.compile(r"^\s*\|.*\|\s*$")
TABLE_SEPARATOR_PATTERN = re.compile(r"^:?-{3,}:?$")
MERGE_SPAN_PATTERN = re.compile(r"\b(?P<name>colspan|rowspan)=['\"](?P<value>\d+)['\"]")
MERGE_PLACEHOLDER_PATTERN = re.compile(r"\bclass=['\"]fn__none['\"]")
CONTRAST_PAIRS = (("有效", "无效"), ("成立", "不成立"), ("原则", "例外"), ("允许", "禁止"))
# E509 verifies a visible semantic cue, not an emoji dictionary or a fixed
# position. Meaning and placement are reviewed in the skill contract because a
# Unicode regex cannot determine whether an icon fits a legal relationship.
EMOJI_PATTERN = re.compile(
    r"[\U0001F000-\U0001FAFF\u2300-\u23FF\u2600-\u27BF\u2B00-\u2BFF](?:\ufe0f|\U0001F3FB-\U0001F3FF|\u200d[\U0001F000-\U0001FAFF\u2300-\u27BF\u2B00-\u2BFF])*"
)
GENERATED_LABEL_PREFIX_PATTERN = re.compile(r"(?:问题|题干|答案|解析|问)[：:]")
DECISION_OPTION_LINE_PATTERN = re.compile(r"^\s*(?:[-+*]|\d+[.)])\s+[✅❌]\s*(?:[A-Z]|[甲乙丙丁戊])(?:[.、:：\s])")
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


LIST_ITEM_START_PATTERN = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
LIST_ITEM_VISIBLE_LIMIT = 20


def _list_item_visible_length(line: str) -> int:
    """Visible length of a list item's content (main or nested), 0 when not a list item
    or when the line is a task checkbox, a quote, or a table row."""
    match = LIST_ITEM_START_PATTERN.match(line)
    if not match:
        return 0
    content = line[match.end():]
    if content.startswith((">", "[", "|")):
        return 0
    return prose_visible_length(content)


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


def has_semantic_emoji_cue(value: str, *, exclude_decision_options: bool = False) -> bool:
    """Return whether prose has an open-set emoji cue outside decision options."""
    for line in prose_without_fenced_blocks(value).splitlines():
        if exclude_decision_options and DECISION_OPTION_LINE_PATTERN.match(line):
            continue
        for match in EMOJI_PATTERN.finditer(line):
            if match.group() not in {"✅", "❌"}:
                return True
    return False


EMOJI_GENERIC_CUE_RE = re.compile(r"重点|难点|要点|注意|提示|警惕|小心|牢记|警示|易错|陷阱|考点|归纳|小结|总结")
COLOR_ANCHOR_TOKEN_RE = re.compile(r"b3-font-(?:color|background)(?:[2-9]|1[0-3])")


def validate_line_color_diversity(text: str) -> list[Finding]:
    """Forbid adjacent lines dominated by the same color.

    A color is a semantic index: when three or more consecutive content lines
    are each dominated (>=60% of their anchors) by the same color, the palette
    stops distinguishing anything and the run fails `E204`.
    """
    findings: list[Finding] = []
    lines = text.splitlines()
    in_fence = False
    run_color: str | None = None
    run_count = 0
    run_start = 0
    for number, line in enumerate(lines, start=1):
        if re.match(r"^(?:\s*>\s*)?```", line):
            in_fence = not in_fence
            continue
        if in_fence or re.match(r"^#{1,6}\s+", line) or line.lstrip().startswith("{:"):
            run_color = None
            run_count = 0
            continue
        colors = COLOR_ANCHOR_TOKEN_RE.findall(line)
        if not colors:
            run_color = None
            run_count = 0
            continue
        dominant, dominant_count = Counter(colors).most_common(1)[0]
        if dominant_count / len(colors) < 0.6:
            run_color = None
            run_count = 0
            continue
        if dominant == run_color:
            run_count += 1
        else:
            run_color = dominant
            run_count = 1
            run_start = number
        if run_count == 3:
            findings.append(Finding("E", "204", run_start, f"Three consecutive lines are each dominated by color {dominant}; adjacent lines must vary their semantic colors so the palette stays an index instead of a wash."))
    return findings


def _emoji_is_anchored(line: str, start: int, end: int) -> bool:
    """Return whether an emoji occurrence has a neighboring content word (CJK/letter/digit)
    directly before or after it, ignoring whitespace and inline markup runes."""
    before = re.sub(r"[\s`*=~<>/]+$", "", line[:start])
    after = re.sub(r"^[\s`*=~<>/]+", "", line[end:])
    word = r"[\u4e00-\u9fffA-Za-z0-9]"
    return bool(
        (before and re.search(word, before[-1]))
        or (after and re.search(word, after[0]))
    )


def validate_emoji_semantics(text: str) -> list[Finding]:
    """Enforce emoji semantics: concept-anchored, diverse, not script-inserted.

    - `E510`: the same semantic emoji repeats more than eight times in one
      document; one specific emoji should map to one specific concept and no
      single icon should dominate.
    - `W511`: an emoji is anchored to a generic cue word (注意/重点/要点/考点/
      提示/陷阱…); anchor it to the specific legal concept instead.
    - `E512`: the same emoji + following-word pair repeats, a hard signature of
      scripted batch insertion; place emoji semantically per concept.
    - `E513`: most semantic emoji sit at sentence ends (piled after 。！？； or
      at the line end); each emoji must sit directly on the concept word it marks.
    - `E514`: most semantic emoji sit at line heads as label prefixes; embed them
      inside the analysis next to the concepts instead of only at the headline.
    - `E515`: a large share of semantic emoji float with no neighboring concept
      word (dangling at clause boundaries or between punctuation); anchor each
      icon to its term (right before or after it) so it is visually bound.
    """
    findings: list[Finding] = []
    counts: dict[str, int] = {}
    pairs: dict[str, int] = {}
    generic_hits = 0
    sentence_final = 0
    line_head = 0
    dangling = 0
    total_placed = 0
    for line in text.splitlines():
        if re.match(r"^##\s+📌\s*考点必背\s*$", line):
            # E634 mandates this exact heading for multi-question documents; its 📌 is
            # structural navigation required by the gate itself, not a semantic cue
            # anchoring the generic word 考点 — exempt it from the W511 window check.
            continue
        for match in EMOJI_PATTERN.finditer(line):
            if match.group() in {"✅", "❌"}:
                continue
            counts[match.group()] = counts.get(match.group(), 0) + 1
            window = line[max(0, match.start() - 3): match.end() + 4]
            if EMOJI_GENERIC_CUE_RE.search(window):
                generic_hits += 1
            pair = match.group() + re.sub(r"\s", "", line[match.end(): match.end() + 3])[:2]
            pairs[pair] = pairs.get(pair, 0) + 1
            total_placed += 1
            after = line[match.end(): match.end() + 3].lstrip()
            if not after or after[0] in "。！？；!?;”』」":
                sentence_final += 1
            if re.fullmatch(r"\s*(?:[-*]|>[ ]*)*\s*", line[:match.start()]):
                line_head += 1
            if not _emoji_is_anchored(line, match.start(), match.end()):
                dangling += 1
    if total_placed >= 5 and sentence_final / total_placed >= 0.7:
        findings.append(Finding("E", "513", 1, f"{sentence_final}/{total_placed} semantic emoji are piled at sentence ends; hard gate — put each emoji directly on the concept word it marks (right after or before the term, one emoji per parallel concept) so the term and the icon are visually bound."))
    if total_placed >= 5 and line_head / total_placed >= 0.7:
        findings.append(Finding("E", "514", 1, f"{line_head}/{total_placed} semantic emoji are bunched at line heads as label prefixes; hard gate — embed emoji inside the analysis sentences next to the concept words they mark (one per parallel concept) so the icons appear in the content, not only at the headline."))
    if total_placed >= 5 and dangling / total_placed >= 0.5:
        findings.append(Finding("E", "515", 1, f"{dangling}/{total_placed} semantic emoji float without a neighboring concept word (dangling at line ends, clause boundaries, or between punctuation); anchor each icon directly beside its term (词前或词后紧贴概念词), never as loose decoration."))
    for emoji, count in counts.items():
        if count > 8:
            findings.append(Finding("E", "510", 1, f"Emoji {emoji} repeats {count} times in this document; one specific emoji maps to one specific concept — diversify so no single icon dominates."))
    if generic_hits:
        findings.append(Finding("W", "511", 1, f"{generic_hits} emoji anchor to generic cue words (注意/重点/要点/考点/提示/陷阱…); anchor each emoji to the specific legal concept inside the knowledge point instead of a commonplace cue word."))
    for pair, count in pairs.items():
        if count >= 6 and re.search(r"[\u4e00-\u9fff]", pair):
            findings.append(Finding("E", "512", 1, f"Emoji-word pair {pair} repeats {count} times; hard gate — this is scripted batch emoji insertion. Place emoji semantically per concept, never by mechanical word replacement."))
    return findings


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
            findings.append(Finding("E", "101", line_for_offset(text, match.start()), "Highlight exceeds 6 visible characters; shorten the ==highlight== to the key term (2-6 characters) and let color or bold carry the rest."))
    for match in re.finditer(r"==[^=\n]+====[^=\n]+==", text):
        findings.append(Finding("E", "102", line_for_offset(text, match.start()), "Adjacent highlights need connecting text or punctuation between them; merge them into one highlight or restore the intervening words."))
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
            findings.append(Finding("E", "203", first_line_by_term[term], f"Repeated term '{term}' uses inconsistent text colors: {sorted(colors)}; unify the term to its first established color everywhere it reappears."))

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
            if number > 1:
                previous = lines[number - 2]
                if (
                    previous.strip()
                    and not previous.lstrip().startswith(">")
                    and not re.match(r"^#{1,6}\s+", previous)
                    and not re.match(r"^\s*```\s*$", previous)
                ):
                    findings.append(Finding("E", "310", number, "A Callout directive must be preceded by a blank line (or the start of a block, another quote line, a heading, or a fence boundary); directly after a list item or paragraph it is parsed as continuation text and will not be recognized."))
            kind = callout.group(1)
            if kind != kind.upper() or kind not in ALLOWED_CALLOUTS:
                findings.append(Finding("E", "303", number, f"Callout type must be one of: {', '.join(sorted(ALLOWED_CALLOUTS))}."))
            if kind == "QUESTION":
                title = line[callout.end():].strip()
                if not title.startswith("✏️ ") or not title.removeprefix("✏️ ").strip() or GENERIC_QUESTION_TITLE_PATTERN.fullmatch(title):
                    findings.append(Finding("E", "307", number, "QUESTION callout title must start with '✏️ ' and name a specific topic or tested rule."))
            cursor = number
            body_lines: list[str] = []
            body_valid = True
            while cursor < len(lines) and lines[cursor].strip():
                if not re.match(r"^\s*>($|\s)", lines[cursor]):
                    findings.append(Finding("E", "304", cursor + 1, "Every nonblank line inside a callout must start with '> '."))
                    body_valid = False
                    break
                if cursor > number:
                    body_lines.append(lines[cursor])
                cursor += 1
            if kind == "QUESTION" and body_valid:
                fence_indexes = [index for index, body_line in enumerate(body_lines) if re.match(r"^\s*>\s*```", body_line)]
                if not fence_indexes:
                    findings.append(Finding("E", "308", number, "QUESTION callout must place the question stem in a ```md code block inside the callout."))
                elif not any(
                    re.match(r"^\s*>\s*\S", body_line) and not re.match(r"^\s*>\s*```", body_line)
                    for body_line in body_lines[fence_indexes[-1] + 1:]
                ):
                    findings.append(Finding("E", "309", number, "QUESTION callout must keep its answer inside the callout after the stem code block."))
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
        findings.append(Finding("W", "502", 1, "Substantial output has no SiYuan semantic color anchors; wrap key terms as **term**{: style=\"color: var(--b3-font-colorN);\"} so subjects and concepts stay indexable."))
    return findings


# MarkNote richness gates live in legal_marknote_richness_gate.py; lazy wrappers keep
# the public names on validate_output.
def validate_marknote_richness (text: str):
    from legal_marknote_richness_gate import validate_marknote_richness as _gate

    return _gate(text)

def validate_paragraph_parent_fragmentation (text: str):
    from legal_marknote_richness_gate import validate_paragraph_parent_fragmentation as _gate

    return _gate(text)


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



# GoldQuest question gates live in legal_goldquest_question_gate.py; these lazy wrappers
# keep validate_output as the single import surface for tests and external tooling.
def validate_goldquest (text: str):
    from legal_goldquest_question_gate import validate_goldquest as _gate

    return _gate(text)

def validate_goldquest_knowledge_placement (text: str):
    from legal_goldquest_question_gate import validate_goldquest_knowledge_placement as _gate

    return _gate(text)

def validate_generated_label_prefixes (text: str):
    from legal_goldquest_question_gate import validate_generated_label_prefixes as _gate

    return _gate(text)

def validate_goldquest_reasoning_integrity (text: str):
    from legal_goldquest_question_gate import validate_goldquest_reasoning_integrity as _gate

    return _gate(text)

def validate_source_preservation ( text: str, source_text: str, profile: str, allow_structural_repair: bool = False, ):
    from legal_goldquest_question_gate import validate_source_preservation as _gate

    return _gate(text, source_text, profile, allow_structural_repair)

def validate_goldquest_source_content (text: str, source_text: str):
    from legal_goldquest_question_gate import validate_goldquest_source_content as _gate

    return _gate(text, source_text)

def validate_goldquest_solution_volume (text: str, source_text: str):
    from legal_goldquest_question_gate import validate_goldquest_solution_volume as _gate

    return _gate(text, source_text)


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
    if profile in {"legal-marknote", "legal-goldquest"}:
        findings.extend(validate_emoji_semantics(text))
        findings.extend(validate_line_color_diversity(text))
    if profile in {"legal-marknote", "legal-goldquest"}:
        findings.extend(
            Finding("E", item.code, item.line, item.message)
            for item in validate_mermaid_semantics(
                text, require_case_grounding=profile == "legal-goldquest"
            )
        )
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
        findings.extend(validate_goldquest_knowledge_placement(text))
        findings.extend(validate_generated_label_prefixes(text))
        findings.extend(validate_goldquest_reasoning_integrity(text))
    if source_text is not None:
        findings.extend(validate_source_preservation(text, source_text, profile, allow_structural_repair))
    if profile == "legal-goldquest" and source_text is not None:
        findings.extend(validate_goldquest_source_content(text, source_text))
        findings.extend(validate_goldquest_solution_volume(text, source_text))
    return sorted(findings, key=lambda finding: (finding.line, finding.level != "E", finding.code))


def infer_profile(script_path: Path) -> str | None:
    for parent in script_path.parents:
        if parent.name in {"legal-marknote", "legal-goldquest"}:
            return parent.name
    return None


DEFAULT_REPORT_LIMIT = 40


def code_summary(findings: list[Finding]) -> str:
    counts = Counter(finding.code for finding in findings)
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    head = " ".join(f"{code}×{count}" for code, count in ranked[:8])
    extra = len(ranked) - 8
    return f"{head} (+{extra} more codes)" if extra > 0 else head


def print_finding_report(
    findings: list[Finding],
    *,
    render,
    label: str,
    show_all: bool = False,
    only_codes: list[str] | None = None,
    limit: int = DEFAULT_REPORT_LIMIT,
) -> None:
    """Bounded text report: the full per-finding detail stays behind --all,
    --code, and --format json so a large audit cannot flood the agent's
    context window; the exit code is always computed by the caller over the
    complete findings list."""
    wanted = {code.strip().upper().lstrip("EW") for code in only_codes or [] if code.strip()}
    selected = [finding for finding in findings if finding.code.upper().lstrip("EW") in wanted] if wanted else findings
    if wanted and not selected:
        print(f"No findings match --code {' '.join(only_codes or [])}; full report has {len(findings)} finding(s): {code_summary(findings)}")
    shown = selected if show_all else selected[: max(0, limit)]
    for finding in shown:
        print(render(finding))
    hidden = len(selected) - len(shown)
    if hidden > 0:
        print(f"... {hidden} more finding(s) not shown of {len(findings)} total. Focus with --code <CODE> (repeatable, e.g. --code E630), lift the cap with --all, or dump everything with --format json.")
    print(f"SUMMARY {label}: {len(findings)} finding(s); by code: {code_summary(findings)}")


# 门禁语义权威速查（与 SKILL.md 完成门禁段同步维护；改门禁必须同步改这里）。
# 这是内容会话了解门禁的唯一内置通道：--explain E630 / --explain all。
GATE_EXPLAIN: dict[str, str] = {
    "E203": "同一词在同一题内不得换色；对比双方用稳定的成对颜色。修法：给重复出现的词统一回它首次的颜色。",
    "E204": "连续三行以上被同一颜色支配（该色占每行锚点≥60%）即拒绝——颜色失去索引意义。修法：换语义角色调色或加背景色形成对比，不要整段刷一色。",
    "E310": "Callout 指令行（> [!NOTE] …）前必须有空行（或块起始/标题/围栏边界），否则被解析为上一块的续行。修法：在指令行前补空行。",
    "E311": "列表项内容不得以有序列表标记开头（- 1. …、- （1）…、- ① …）。修法：去掉标记只留内容，或写成缩进的真实 1. … 子行。",
    "E509": "中等及以上复杂度解析至少要有一条围栏外、非判项行的 emoji 语义提示；✅/❌ 不计入。",
    "E510": "同一 emoji 在文档中出现超过 8 次——一个 emoji 只对应一个概念，分散使用。",
    "E512": "同一「emoji+词」组合出现≥6 处即判机械批量插入。修法：按每处概念的实际语义逐个选 emoji，禁脚本统一加。",
    "E513": "句尾 emoji 堆积（≥70% 落在句末标点或行尾）。修法：把 emoji 贴到它修饰的概念词上。",
    "E514": "行首 emoji 贴标签（≥70% 落在条目开头）。修法：emoji 移到词前/词后紧贴概念。",
    "E515": "悬空 emoji（≥50% 两侧都不是概念词，悬在句尾或标点间）。修法：紧贴所锚定的概念词。",
    "W511": "emoji 贴在「注意/重点/要点/考点/提示/陷阱」等通用占位词上。修法：改贴具体法律概念词。",
    "E617": "锚点膨胀：颜色锚点只标关键短词（2-6 可见字符，完整制度名最多 8），标点放样式之外；顿号/连接词不得进锚点。",
    "E618": "合并锚点：一行内同一锚点不得把「谁+做什么+结果」整体染色。修法：拆成主体、条件、结果各自着色。",
    "E620": "辅助样式不足：中等及以上解析需至少 4 类辅助样式（highlight==…==、<em>、~~…~~、`code`、<u>）。",
    "E621": "超长行/机械换行：普通解析行 ≤42 可见字符，超长按语义边界拆成嵌套列表；不可分规则写成完整段落。",
    "E622": "实质推理行缺颜色锚点：任何 ≥14 可见字符的解析行必须至少一个颜色锚点（**词**{: style=…}）。",
    "E623": "主体词未着色或着色不完整：解析区的主体/关键概念词必须染色，且同一主体反复出现时保持同色；主体词内部的子串（如「中级法院」的「法院」）要单独处理。",
    "E624": "中等及以上复杂度必须有至少一个有意的可视化（Mermaid/div HTML/SVG/PNG，且是真分析）。",
    "E626": "结构载体不足：至少 4 类结构载体（嵌套列表、Callout、小标题、小表、可视化、分隔线）。",
    "E627": "背景色锚不足：至少 3 个短背景色签（{: style=\"…background-color…\"} 紧跟加粗文本）。",
    "E628": "编号小问（(1)/(2)…）必须独占一行、与共享题干分行。",
    "E630": "逐项回放缺失或不完整：逐项辨析区每个被分析的选项必须完整复写原选项原文（样式标记剥离后与题块选项逐字一致），前缀 ✅/❌ + 选项字母。",
    "E631": "逐项回放正文与选项原文不一致（改写/截断/多字都算）。修法：从题块选项行逐字复制。",
    "E632": "每个选项紧邻一条有实质法律信息的理由；答案复述、结论标签、「由综合推理可知」占位都失败。修法：写明决定正误的规则、要件与涵摄。",
    "E639": "Mermaid 接地：图中至少三个法律节点必须能从同题正文逐字回查；节点/边标签是解析文字的子串，不得自造词。",
    "E640": "实质 Callout 缺失：中等及以上解析需至少一个承载法条/条件/例外/程序/法律效果的 Callout；泛化「本题考查…」不计。",
    "E641": "Callout 或解析中出现按标点切出的残句。修法：恢复完整句子或按语义重写。",
    "E642": "机械标签（要点1/方法一/环节2 等纯标签行）拒绝。修法：用内容本身作标题。",
    "E643": "泛化考点复述/通用做题提醒不算实质 Callout 内容。修法：写本题具体的法条、边界或陷阱。",
    "E644": "禁止在逐项辨析后另设「综合推理」小节补写真正理由。20-整理保留版路由的原文解析节属来源保全载体，命中时按技能正文记录文件与题号，不得删原文。",
    "E645": "复杂推理必须使用合格 Mermaid（真判断链），不能只靠列表。",
    "E647": "行首禁加「问题：/题干：/答案：/解析：/问：」标签前缀——直接书写内容。",
    "E650": "模板占位假解析：「与规则不符，排除」类无具体法律内容的空壳行拒绝。每条选项理由必须点名本题的规则、要件与涵摄。",
    "E651": "解析区末行停在半句（截断痕迹）。修法：补全该选项的推理，或裁到完整判断为止。",
    "E652": "标点残渣（。，/，。/；。/。。）说明句子拼接损坏。修法：修复连接处，不是堆句号。",
    "E653": "整理解析体量过小：--source 下原书解析≥900 字而整理不足 25%（且绝对丢失≥600 字）直接失败。压缩必须保住推理链。",
    "W851": "整理不足原书体量 45% 的警告（严格模式下同样阻断）。同 E653 修法。",
    "E814": "源连续性：输出在已覆盖考点范围内整题缺失。对比必须限定同一知识点范围；源文件优先取 10-mineru，不在手边从 git 历史找回。",
    "W815": "被覆盖题目中有实质法条/推理行在新版无迹可寻。修法：回源核对补齐或说明差异。",
    "E816": "禁止独立的「规则地图/知识地图/争点/规则与法源」预陈述小节——完整知识点直接写进逐项辨析；删除前先「先融合后删」，融不进的独特规则用 Callout/Mermaid 保留。",
    "E817": "Callout 只能补充新价值（法条原文、陷阱、边界、记忆链接），不得复述解析内容。",
    "E901": "孤立关键词二元组罗列（多行 A[...] --> B[...] 节点互不共用）拒绝。一张图必须是一条完整连通推理链：共享节点、边标签写明被测关系或用决策菱形。",
    "E902": "无边标签、无决策菱形、无分支且标签为短关键词的裸链拒绝。画不出判断链就用列表。",
    "E903": "同一围栏内连通分量必须=1：多条独立链条或孤立节点拼进一张图仍是几张图。修法：经共享/汇聚节点接成一条链，确属无关内容拆列表或各自成图。",
    "E904": "知识点清单图：一个根节点扇形罗列制度分支、全图无任何本题落点词（本题/本案/题干/选项/正确/错误/甲乙丙丁等）即拒绝。解析区的图必须至少一条链用本案事实推到「哪个选项对错」。方向/布局/形状/配色自由，门禁只管逻辑链。",
    "W505": "机械换行审计：普通正文行是软换行时按结构问题处理；修 W505/W507 只动段落/列表/缩进，锚点与 IAL 原样随所属文字移动。",
    "W507": "编号子列表：父项行内的中段编号（1.、（1）、①）必须改成 4 空格缩进、独占一行的真实子行。",
}


def explain_gate(code: str) -> int:
    query = code.strip()
    if query.lower() == "all":
        for key in sorted(GATE_EXPLAIN):
            print(f"{key}: {GATE_EXPLAIN[key]}")
        return 0
    match = re.fullmatch(r"([EW])?\s*0*(\d{3})", query.upper())
    if match:
        prefix, digits = match.group(1), match.group(2)
        forms = [f"{prefix}{digits}"] if prefix else []
        candidates = forms + [f"E{digits}", f"W{digits}"]
    else:
        candidates = [query.upper()]
    for cand in candidates:
        if cand in GATE_EXPLAIN:
            print(f"{cand}: {GATE_EXPLAIN[cand]}")
            return 0
    print(f"未收录 {query} 的解释词条。该码的报错信息本身就是权威判定（含修法）；"
          f"可用 --explain all 查看全部已收录码。不得为理解该码去读校验器源码，看不懂就报告用户。")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, nargs="?", default=None, help="Generated Markdown file to validate.")
    parser.add_argument("--explain", metavar="CODE", help="Print the authoritative rule summary for a gate code (E630 / 630 / W505 / all) and exit. This is the sanctioned way to learn gate semantics — content sessions must not read validator source.")
    parser.add_argument("--profile", choices=("legal-marknote", "legal-goldquest"), default=infer_profile(Path(__file__).resolve()))
    parser.add_argument("--source", type=Path, help="Original source file for preservation checks.")
    parser.add_argument("--require-source", action="store_true", help="Fail when --source is omitted.")
    parser.add_argument("--strict", action="store_true", help="Strict mode (the default). Advisory warnings are gate failures and the table gate is 2 x 2; kept for compatibility with existing invocations.")
    parser.add_argument("--lenient", action="store_true", help="Relaxed mode. Only available when the COMPLETE relaxation set is passed: --lenient --max-table-columns N --max-table-rows N; if any relaxation parameter is missing, validation refuses to run.")
    parser.add_argument("--max-table-columns", type=int, help="Override the strict table column gate (default 2). Without --lenient this is a scoped per-table exception; warnings stay strict. With --lenient it is part of the complete relaxation set.")
    parser.add_argument("--max-table-rows", type=int, help="Override the strict table data-row gate (default 2). Without --lenient this is a scoped per-table exception; warnings stay strict. With --lenient it is part of the complete relaxation set.")
    parser.add_argument("--require-topic-ial", action="store_true", help="Require at least one MarkNote note-topic provider declaration.")
    parser.add_argument(
        "--allow-structural-repair",
        action="store_true",
        help="Allow recognized source shell headings to be repaired or demoted while preserving substantive headings.",
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--all", action="store_true", help="Print every finding instead of the bounded default report.")
    parser.add_argument("--code", action="append", metavar="CODE", help="Show only findings with this code in the text report (repeatable; E630 and 630 both work). Validation and the exit code always cover every finding.")
    parser.add_argument("--max-report", type=int, default=DEFAULT_REPORT_LIMIT, help=f"Text-report cap (default {DEFAULT_REPORT_LIMIT}); --all lifts the cap. JSON output is never capped.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.explain:
        return explain_gate(args.explain)
    if args.output is None:
        print("output file is required unless --explain is used.", file=sys.stderr)
        return 2
    if args.profile is None:
        print("--profile is required when running the canonical validator.", file=sys.stderr)
        return 2
    if args.require_source and args.source is None:
        print(f"{args.output}:1: E700: --source is required by this gate.")
        return 1
    if args.strict and args.lenient:
        print("--strict and --lenient are mutually exclusive: strict mode is the default; relaxed mode requires the complete relaxation set (--lenient --max-table-columns N --max-table-rows N).", file=sys.stderr)
        return 2
    if args.lenient:
        missing = [name for name, value in (("--max-table-columns", args.max_table_columns), ("--max-table-rows", args.max_table_rows)) if value is None]
        if missing:
            print(
                "Relaxed mode requires the COMPLETE relaxation set; missing: "
                + ", ".join(missing)
                + ". Pass --lenient --max-table-columns N --max-table-rows N together; strict mode is the default and table-size overrides alone are a scoped exception that keeps warnings strict.",
                file=sys.stderr,
            )
            return 2
    if (args.max_table_columns is not None and args.max_table_columns < 1) or (args.max_table_rows is not None and args.max_table_rows < 1):
        print("--max-table-columns and --max-table-rows must be positive integers.", file=sys.stderr)
        return 2
    text = args.output.read_text(encoding="utf-8")
    source_text = args.source.read_text(encoding="utf-8") if args.source else None
    strict = not args.lenient
    findings = validate_text(
        text,
        args.profile,
        source_text,
        args.require_topic_ial,
        args.allow_structural_repair,
        args.max_table_columns if args.max_table_columns is not None else (2 if strict else 3),
        args.max_table_rows if args.max_table_rows is not None else (2 if strict else 3),
    )
    if args.format == "json":
        print(json.dumps([asdict(finding) for finding in findings], ensure_ascii=False, indent=2))
    elif findings:
        error_count = sum(finding.level == "E" for finding in findings)
        warning_count = sum(finding.level == "W" for finding in findings)
        print_finding_report(
            findings,
            render=lambda finding: finding.render(args.output),
            label=f"{args.output} [E:{error_count} W:{warning_count}]",
            show_all=args.all,
            only_codes=args.code,
            limit=args.max_report,
        )
    else:
        print(f"PASS {args.profile} output validation: {args.output}")
    has_errors = any(finding.level == "E" for finding in findings)
    has_warnings = any(finding.level == "W" for finding in findings)
    return 1 if has_errors or (strict and has_warnings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
