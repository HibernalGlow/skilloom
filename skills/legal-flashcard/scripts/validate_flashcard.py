#!/usr/bin/env python3
"""Deterministically validate DAMO flashcard Markdown schema 1."""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

ATTR_RE = re.compile(r'(?P<key>[A-Za-z][\w-]*)="(?P<value>[^"]*)"')
IAL_LINE_RE = re.compile(r'^\{: [A-Za-z][\w-]*="[^"]*"(?: [A-Za-z][\w-]*="[^"]*")*\}$')
CARD_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SOURCE_KEY_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*$")
STYLE_ANCHOR_RE = re.compile(
    r'\*\*[^*\n]+\*\*\{:\s+style="[^"]*(?:color|background-color):\s*var\(--b3-font-(?:color|background)(?:[2-9]|1[0-3])\);?[^"]*"\}'
)
STYLE_PROPERTY_RE = re.compile(r"(?:^|;)\s*(background-color|color):\s*([^;]+)")
STYLE_ANCHOR_TEXT_RE = re.compile(
    r'\*\*(?P<text>[^*\n]+)\*\*\{:\s+style="[^\"]*(?:color|background-color):'
)
PROVIDER_IAL_RE = re.compile(r'^\{:[^\n]*custom-qb-note-topic-id="([^"]+)"[^\n]*\}$')
REPORT_RE = re.compile(r"候选\s*(\d+)\D+接受\s*(\d+)\D+拒绝\s*(\d+)")
AUDIT_PREAMBLE_RE = re.compile(
    r"^-\s+(?:源笔记|协议|标签|构成|着色图例|章节|样式继承|源笔记说明|高亮职责)："
)
SOURCE_PROTOCOL_RE = re.compile(r"^原笔记：\[\[[^\]\n]+\]\] · 协议：DAMO 闪卡 schema 1$")
RUNTIME_RE = re.compile(
    r"(?:custom-riff-decks|\bdue\b|\binterval\b|review\s+log|\bsuspend\b|\bbury\b|device\s+state|srs\s+state)",
    re.IGNORECASE,
)
KNOWLEDGE_TAG_RE = re.compile(r"#(?!闪卡/优先级/)[^#\s]+#")
PRIORITY_TAG_RE = re.compile(r"#闪卡/优先级/([^#\s]+)#")
GENERATED_LABEL_RE = re.compile(r"^\s*(?:>\s*)?(?:-\s+)?(?:问题|答案)[：:]")
CALL_OUT_TITLE_STYLE_RE = re.compile(r"\{:\s*style=|\*\*|==|~~|`|<\/?(?:em|u)(?:\s|>)", re.IGNORECASE)
ORDER_CUE_RE = re.compile(r"顺序|次序|步骤|阶段|程序|流程|先后|依次|优先|第[一二三四五六七八九十0-9]+步")
MERMAID_TYPE_RE = re.compile(
    r"^(?:flowchart|graph|sequenceDiagram|classDiagram|stateDiagram(?:-v2)?|erDiagram|journey|gantt|pie|"
    r"quadrantChart|requirementDiagram|gitGraph|mindmap|timeline|zenuml|sankey-beta|xychart-beta|"
    r"block-beta|packet-beta|kanban|architecture-beta|radar-beta|treemap-beta)\b"
)
RECALL_SLOT_RE = re.compile(r"(?:[①②③④⑤⑥⑦⑧⑨⑩]|\?{1,}|？{1,}|_{2,}|…)")
ALLOWED = {
    "custom-dm-source-key",
    "custom-dm-card-id",
    "custom-dm-card-schema",
    "custom-dm-card-kind",
    "custom-dm-card-renderer",
    "custom-qb-note-topic-id",
}
KINDS = {"basic", "cloze", "mnemonic"}
RENDERERS = {"list", "mark", "blockquote", "callout"}
MNEMONIC_GENERIC_LABELS = {"口诀", "记忆口诀", "记忆线索", "线索", "提示", "记忆点", "口诀卡"}


@dataclass(frozen=True)
class Finding:
    line: int
    code: str
    message: str


def has_blocking_findings(findings: list[Finding]) -> bool:
    return any(not finding.code.startswith("W") for finding in findings)


def parse_ial_blocks(
    lines: list[str],
) -> tuple[list[tuple[int, int, dict[str, str], str, list[str]]], list[Finding]]:
    cards = []
    findings: list[Finding] = []
    in_fence = False
    index = 0
    while index < len(lines):
        line = lines[index]
        if re.match(r"^\s*(?:>\s*)?```", line):
            in_fence = not in_fence
            index += 1
            continue
        if line.lstrip().startswith("{:"):
            start = index
            body = [line]
            while not body[-1].rstrip().endswith("}") and index + 1 < len(lines):
                index += 1
                body.append(lines[index])
            raw = "\n".join(body)
            if len(body) != 1:
                findings.append(Finding(start + 1, "E022", "Card IAL must occupy exactly one physical line."))
            if in_fence:
                findings.append(Finding(start + 1, "E008", "Card IAL is inside a code fence."))
            if not raw.rstrip().endswith("}"):
                findings.append(Finding(start + 1, "E001", "Unclosed IAL."))
            if len(body) == 1 and not IAL_LINE_RE.fullmatch(line.strip()):
                findings.append(Finding(start + 1, "E023", "IAL attributes must use one ASCII space and no space before }."))
            matches = list(ATTR_RE.finditer(raw))
            keys = [match.group("key") for match in matches]
            attrs = {match.group("key"): match.group("value") for match in matches}
            for key, count in Counter(keys).items():
                if count > 1:
                    findings.append(Finding(start + 1, "E024", f"Duplicate IAL attribute: {key}."))
            cards.append((start, index, attrs, raw, keys))
        index += 1
    return cards, findings


def _visible_text(text: str) -> str:
    text = re.sub(r'\{:\s*[^}]*\}', "", text)
    text = re.sub(r"[*_=`~<>]", "", text)
    return re.sub(r"\s+", "", text)


def _card_body(lines: list[str], ial_start: int, renderer: str | None) -> tuple[int | None, str]:
    if ial_start == 0 or not lines[ial_start - 1].strip():
        return None, ""
    cursor = ial_start - 1
    if renderer in {"list", "mark"}:
        while cursor >= 0:
            line = lines[cursor]
            if line.lstrip().startswith("{:") or re.match(r"^#{1,6}\s+", line):
                break
            if re.match(r"^-\s+", line):
                return cursor, "\n".join(lines[cursor:ial_start])
            if line.strip() and not line[0].isspace():
                break
            cursor -= 1
        return None, ""
    if renderer in {"blockquote", "callout"}:
        while cursor >= 0 and lines[cursor].lstrip().startswith(">"):
            cursor -= 1
        start = cursor + 1
        return (start, "\n".join(lines[start:ial_start])) if start < ial_start else (None, "")
    return ial_start - 1, lines[ial_start - 1]


def _mnemonic_label(root: str) -> str:
    """Return the visible cue label before the mnemonic root's colon."""
    label_source = re.sub(r"\{:\s*[^}]*\}", "", root)
    match = re.match(r"^-\s+(.*?)\s*(?:：|:)", label_source)
    if not match:
        return ""
    label = re.sub(r"[*_`~]", "", match.group(1))
    label = re.sub(r"[（）()\[\]【】·\s]", "", label)
    for generic in MNEMONIC_GENERIC_LABELS:
        label = label.replace(generic, "")
    return label


def _front_line(card_body: str, renderer: str | None) -> str:
    lines = card_body.splitlines()
    if renderer in {"list", "mark"}:
        return lines[0].strip() if lines else ""
    if renderer == "callout":
        for line in lines:
            match = re.match(r"^\s*>\s+\[![A-Z]+\]\s*(.*)$", line)
            if match:
                return match.group(1).strip()
        return ""
    for line in lines:
        candidate = line.lstrip()
        if not candidate.startswith(">"):
            continue
        candidate = candidate[1:].strip()
        if not candidate or re.match(r"^\[![A-Z]+\]", candidate) or candidate.startswith("-"):
            continue
        return candidate
    return ""


def _is_question_front(front: str) -> bool:
    without_tags = re.sub(r"\s+#[^#\s]+#", "", front).strip()
    return without_tags.endswith(("？", "?"))


def _list_item_indents(card_body: str) -> list[int]:
    indents: list[int] = []
    in_fence = False
    for line in card_body.splitlines()[1:]:
        if re.match(r"^\s*```", line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = re.match(r"^(?P<indent> +)(?:-|\d+\.)\s+\S", line)
        if match:
            indents.append(len(match.group("indent")))
    return indents


def _basic_answer_lines(card_body: str, renderer: str | None) -> list[str]:
    if renderer == "list":
        indents = _list_item_indents(card_body)
        if not indents:
            return []
        answer_indent = min(indents)
        return [line for line in card_body.splitlines() if re.match(rf"^ {{{answer_indent}}}(?:-|\d+\.)\s+\S", line)]
    if renderer in {"blockquote", "callout"}:
        return [line for line in card_body.splitlines() if re.match(r"^\s*>\s+(?:-|\d+\.)\s+\S", line)]
    return []


def _has_nested_answer_items(card_body: str, renderer: str | None) -> bool:
    if renderer == "list":
        indents = _list_item_indents(card_body)
        return bool(indents) and any(indent > min(indents) for indent in indents)
    if renderer in {"blockquote", "callout"}:
        for line in card_body.splitlines():
            match = re.match(r"^\s*>\s?(?P<indent> *)(?:-|\d+\.)\s+\S", line)
            if match and len(match.group("indent")) >= 4:
                return True
    return False


def _answer_text(line: str) -> str:
    return re.sub(r"^\s*(?:>\s*)?(?:-|\d+\.)\s+", "", line, count=1)


def _obviously_complex_flat_back(front: str, answer_lines: list[str], has_nested_items: bool) -> bool:
    if has_nested_items or len(answer_lines) < 3:
        return False
    visible_front = _visible_text(front)
    explicit_closed_set = re.search(
        r"(?:[0-9一二三四五六七八九十两]+(?:大|项|类|种|个|条|方面|原则|要件|情形|条件|步骤|阶段))",
        visible_front,
    )
    total_answer_chars = sum(len(_visible_text(_answer_text(line))) for line in answer_lines)
    return explicit_closed_set is None and total_answer_chars > 72


def _style_profile(card_body: str, kind: str | None) -> tuple[set[tuple[tuple[str, str], ...]], bool, bool]:
    signatures: set[tuple[tuple[str, str], ...]] = set()
    has_foreground = False
    has_background = False
    for fragment in STYLE_ANCHOR_RE.findall(card_body):
        style = re.search(r'style="([^"]+)"', fragment)
        if not style:
            continue
        properties = tuple(sorted((name, value.strip()) for name, value in STYLE_PROPERTY_RE.findall(style.group(1))))
        if not properties:
            continue
        signatures.add(properties)
        has_foreground = has_foreground or any(name == "color" for name, _value in properties)
        has_background = has_background or any(name == "background-color" for name, _value in properties)
    if kind in {"cloze", "mnemonic"} and re.search(r"==[^=\n]+==", card_body):
        signatures.add((("mark", "highlight"),))
        has_background = True
    return signatures, has_foreground, has_background


def _auxiliary_style_families(text: str) -> set[str]:
    prose = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    families: set[str] = set()
    if re.search(r"==[^=\n]+==", prose):
        families.add("highlight")
    if re.search(r"<em>[^<\n]+</em>", prose, re.IGNORECASE):
        families.add("italic")
    if re.search(r"~~[^~\n]+~~", prose):
        families.add("strike")
    if re.search(r"(?<!`)`[^`\n]+`(?!`)", prose):
        families.add("code")
    if re.search(r"<u(?:\s+[^>]*)?>[^<\n]+</u>", prose, re.IGNORECASE):
        families.add("underline")
    return families


def _structural_families(text: str) -> set[str]:
    families: set[str] = set()
    if re.search(r"^\s{8,}(?:-|\d+\.)\s+\S", text, re.MULTILINE):
        families.add("nested-list")
    if re.search(r"^\s*>\s+\[![A-Z]+\]", text, re.MULTILINE):
        families.add("callout")
    if re.search(r"^#{2,6}\s+\S", text, re.MULTILINE):
        families.add("subheading")
    if _has_table(text):
        families.add("table")
    if (
        _has_mermaid(text)
        or re.search(r"^\s*```html\s*$", text, re.MULTILINE)
        or re.search(r"!\[[^\]]*(?:可视化|图解|流程图|关系图|决策图|时间线|diagram)[^\]]*\]\([^)]*\)", text, re.IGNORECASE)
    ):
        families.add("visual")
    if re.search(r"^\s*---\s*$", text, re.MULTILINE):
        families.add("divider")
    return families


def _is_rich_complex_deck(text: str, card_count: int) -> bool:
    body = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    visible = _visible_text(body)
    sentence_count = len(re.findall(r"[。！？；]", visible))
    branch_count = len(re.findall(r"^\s{0,}(?:- |\d+\. )\S", body, re.MULTILINE))
    return len(visible) >= 160 or sentence_count >= 4 or branch_count >= 3 or card_count >= 3


def _validate_style_anchor_bounds(text: str) -> list[Finding]:
    findings: list[Finding] = []
    for match in STYLE_ANCHOR_TEXT_RE.finditer(text):
        anchor = _visible_text(match.group("text"))
        line = text.count("\n", 0, match.start()) + 1
        if len(anchor) > 8:
            findings.append(Finding(line, "E064", "Color/background anchors must stay within eight visible characters; style only the decisive retrieval term."))
        if re.search(r"[，。；：、,.!?！？]", anchor):
            findings.append(Finding(line, "E065", "Punctuation must remain outside a color/background anchor."))
    return findings


def _distinct_style_dimensions(text: str) -> tuple[set[str], set[str]]:
    foreground: set[str] = set()
    backgrounds: set[str] = set()
    for match in STYLE_ANCHOR_RE.finditer(text):
        style = re.search(r'style="([^"]+)"', match.group(0))
        if not style:
            continue
        for name, value in STYLE_PROPERTY_RE.findall(style.group(1)):
            if name == "color":
                foreground.add(value.strip())
            elif name == "background-color":
                backgrounds.add(value.strip())
    return foreground, backgrounds


def _validate_rich_deck(text: str, card_styles: list[set[tuple[tuple[str, str], ...]]], card_count: int) -> list[Finding]:
    if not _is_rich_complex_deck(text, card_count):
        return []
    findings: list[Finding] = _validate_style_anchor_bounds(text)
    auxiliary = _auxiliary_style_families(text)
    if len(auxiliary) < 4:
        findings.append(Finding(1, "E060", f"Rich flashcard decks need at least four auxiliary style families; found {len(auxiliary)} ({', '.join(sorted(auxiliary)) or 'none'})."))
    structural = _structural_families(text)
    if len(structural) < 4:
        findings.append(Finding(1, "E061", f"Rich flashcard decks need at least four structural families; found {len(structural)} ({', '.join(sorted(structural)) or 'none'})."))
    backgrounds = len(re.findall(r"b3-font-background(?:[2-9]|1[0-3])", text))
    if backgrounds < 3:
        findings.append(Finding(1, "E062", f"Rich flashcard decks need at least three short background-color anchors; found {backgrounds}."))
    foregrounds, background_signatures = _distinct_style_dimensions(text)
    if len(foregrounds) <= 3 and len(background_signatures) < 3:
        findings.append(Finding(1, "E066", "A rich deck with a sparse foreground palette needs at least three distinct semantic background signatures; do not repeat a two-color foreground-only palette."))
    relation_cue = re.search(r"流程|程序|步骤|关系|对应|比较|区别|分支|情形|主体|阶段|如何", _visible_text(text))
    if relation_cue and "visual" not in structural:
        findings.append(Finding(1, "E063", "A rich deck with process, branch, role, comparison, or relation cues needs Mermaid, an inherited image, or another documented primary visual."))
    unique_signatures = set().union(*card_styles) if card_styles else set()
    if len(unique_signatures) <= 2 and unique_signatures:
        findings.append(Finding(1, "W111", "A styled rich deck uses two or fewer unique color/background signatures overall; revise toward three or more semantic roles."))
    return findings


def _has_table(card_body: str) -> bool:
    return bool(re.search(r"^\s*(?:>\s*)?\|[^\n]+\|\s*$", card_body, re.MULTILINE))


def _mermaid_blocks(card_body: str) -> list[tuple[int, int, str]]:
    blocks: list[tuple[int, int, str]] = []
    lines = card_body.splitlines()
    index = 0
    while index < len(lines):
        match = re.match(r"^(?P<prefix>\s*(?:>\s*)?)```mermaid\s*$", lines[index])
        if not match:
            index += 1
            continue
        prefix = match.group("prefix")
        indent = len(prefix) if ">" not in prefix else len(prefix.split(">", 1)[1])
        content: list[str] = []
        end = index + 1
        while end < len(lines) and not re.match(r"^\s*(?:>\s*)?```\s*$", lines[end]):
            content.append(lines[end])
            end += 1
        blocks.append((index, indent, "\n".join(content)))
        index = end + 1
    return blocks


def _has_mermaid(card_body: str) -> bool:
    return bool(_mermaid_blocks(card_body))


def _mermaid_has_diagram_type(content: str) -> bool:
    for line in content.splitlines():
        candidate = line.strip()
        if not candidate or candidate.startswith("%%"):
            continue
        return bool(MERMAID_TYPE_RE.match(candidate))
    return False


def _mermaid_semantic_classes(content: str) -> tuple[set[str], set[str]]:
    defined = set(re.findall(r"^\s*classDef\s+([A-Za-z][\w-]*)\s+", content, re.MULTILINE))
    applied = set()
    for names in re.findall(r"^\s*class\s+[^\s]+\s+([A-Za-z][\w-]*)\s*;?\s*$", content, re.MULTILINE):
        applied.add(names)
    applied.update(re.findall(r":::\s*([A-Za-z][\w-]*)", content))
    return defined, applied


def _front_mermaid_blocks(card_body: str, renderer: str | None) -> tuple[list[tuple[int, int, str]], int | None]:
    if renderer != "list":
        return [], None
    answer_lines = _basic_answer_lines(card_body, renderer)
    if not answer_lines:
        return [], None
    lines = card_body.splitlines()
    answer_indexes = [index for index, line in enumerate(lines) if line in answer_lines]
    answer_indent = min(_list_item_indents(card_body))
    return [block for block in _mermaid_blocks(card_body) if block[0] < min(answer_indexes)], answer_indent


def _has_ordered_answers(card_body: str, renderer: str | None) -> bool:
    if renderer == "list":
        return any(re.match(r"^\s+\d+\.\s+\S", line) for line in _basic_answer_lines(card_body, renderer))
    if renderer in {"blockquote", "callout"}:
        return bool(re.search(r"^\s*>\s+\d+\.\s+\S", card_body, re.MULTILINE))
    return False


def _front_names_order(front: str) -> bool:
    without_tags = re.sub(r"#[^#\s]+#", "", front)
    return bool(ORDER_CUE_RE.search(_visible_text(without_tags)))


def _source_names_order(visible_lines: list[str]) -> bool:
    return any(ORDER_CUE_RE.search(re.sub(r"#[^#\s]+#", "", line)) for line in visible_lines)


def _normalized_answer_fact(line: str) -> str:
    return _visible_text(_answer_text(line)).strip("。；;，,")


def _source_maps(
    source_text: str,
) -> tuple[set[str], dict[str, set[str]], list[str], dict[str, list[str]]]:
    global_fragments = set(STYLE_ANCHOR_RE.findall(source_text))
    topic_fragments: dict[str, set[str]] = {}
    global_visible_lines = [_visible_text(line) for line in source_text.splitlines() if _visible_text(line)]
    topic_visible_lines: dict[str, list[str]] = {}
    current_topic: str | None = None
    for line in source_text.splitlines():
        provider = PROVIDER_IAL_RE.fullmatch(line.strip())
        if provider:
            current_topic = provider.group(1)
            topic_fragments.setdefault(current_topic, set())
            topic_visible_lines.setdefault(current_topic, [])
            continue
        if current_topic is not None:
            topic_fragments[current_topic].update(STYLE_ANCHOR_RE.findall(line))
            visible = _visible_text(line)
            if visible:
                topic_visible_lines[current_topic].append(visible)
    return global_fragments, topic_fragments, global_visible_lines, topic_visible_lines


def _style_text(fragment: str) -> str:
    match = re.match(r"\*\*([^*\n]+)\*\*", fragment)
    return _visible_text(match.group(1)) if match else ""


def _source_scope_topic(topic_id: str, known_topics: set[str]) -> str | None:
    if topic_id in known_topics:
        return topic_id
    parents = [known for known in known_topics if topic_id.startswith(f"{known}-")]
    return max(parents, key=len) if parents else None


def validate(
    text: str,
    *,
    source_text: str | None = None,
    require_report: bool = False,
    max_cards_per_topic: int = 4,
    max_answer_items: int = 4,
    max_answer_chars: int = 84,
    rich_style: bool = False,
) -> list[Finding]:
    lines = text.splitlines()
    cards, findings = parse_ial_blocks(lines)
    seen: dict[str, int] = {}
    topic_lines: dict[str, list[int]] = {}
    accepted_card_lines: list[int] = []
    basic_records: list[tuple[int, str, str, set[str]]] = []
    deck_card_styles: list[set[tuple[tuple[str, str], ...]]] = []
    source_global_styles: set[str] = set()
    source_topic_styles: dict[str, set[str]] = {}
    source_global_visible_lines: list[str] = []
    source_topic_visible_lines: dict[str, list[str]] = {}
    if source_text is not None:
        (
            source_global_styles,
            source_topic_styles,
            source_global_visible_lines,
            source_topic_visible_lines,
        ) = _source_maps(source_text)
    for start, end, attrs, raw, _keys in cards:
        if not any(key.startswith("custom-dm-") for key in attrs):
            continue
        accepted_card_lines.append(start + 1)
        unknown = set(attrs) - ALLOWED
        for key in sorted(unknown):
            findings.append(Finding(start + 1, "E002", f"Unsupported card attribute: {key}."))
        required = {
            "custom-dm-source-key",
            "custom-dm-card-id",
            "custom-dm-card-schema",
            "custom-dm-card-kind",
            "custom-dm-card-renderer",
            "custom-qb-note-topic-id",
        }
        for key in sorted(required - set(attrs)):
            findings.append(Finding(start + 1, "E003", f"Missing required card attribute: {key}."))
        card_id = attrs.get("custom-dm-card-id", "")
        if card_id:
            if not CARD_ID_RE.fullmatch(card_id):
                findings.append(Finding(start + 1, "E004", "custom-dm-card-id must be lowercase ASCII kebab-case."))
            if card_id in seen:
                findings.append(Finding(start + 1, "E005", f"Duplicate custom-dm-card-id; first seen on line {seen[card_id]}."))
            seen.setdefault(card_id, start + 1)
        source_key = attrs.get("custom-dm-source-key", "")
        if source_key and not SOURCE_KEY_RE.fullmatch(source_key):
            findings.append(Finding(start + 1, "E006", "custom-dm-source-key contains unsupported characters."))
        if attrs.get("custom-dm-card-schema") != "1":
            findings.append(Finding(start + 1, "E007", "Only custom-dm-card-schema=\"1\" is supported."))
        if attrs.get("custom-dm-card-kind") not in KINDS:
            findings.append(Finding(start + 1, "E009", "custom-dm-card-kind must be basic, cloze, or mnemonic."))
        renderer = attrs.get("custom-dm-card-renderer")
        if renderer not in RENDERERS:
            findings.append(Finding(start + 1, "E010", "custom-dm-card-renderer must be list, mark, blockquote, or callout."))
        topic_id = attrs.get("custom-qb-note-topic-id", "")
        if topic_id and not CARD_ID_RE.fullmatch(topic_id):
            findings.append(Finding(start + 1, "E012", "custom-qb-note-topic-id must be one lowercase ASCII kebab-case ID."))
        elif topic_id:
            topic_lines.setdefault(topic_id, []).append(start + 1)
        source_scope_topic = _source_scope_topic(topic_id, set(source_topic_styles) | set(source_topic_visible_lines))
        if RUNTIME_RE.search(raw) or RUNTIME_RE.search("\n".join(lines[max(0, start - 8): min(len(lines), end + 8)])):
            findings.append(Finding(start + 1, "E014", "Runtime scheduling or Riff fields leaked into the card block."))
        root_index, card_body = _card_body(lines, start, renderer)
        root = lines[root_index].strip() if root_index is not None else ""
        front = _front_line(card_body, renderer)
        for body_line in card_body.splitlines():
            if GENERATED_LABEL_RE.match(body_line):
                findings.append(Finding(start + 1, "E044", "Write the front and answer items directly; generated 问题：/答案： prefixes are forbidden."))
                break
        if not KNOWLEDGE_TAG_RE.search(card_body):
            findings.append(Finding(start + 1, "E033", "Accepted cards need a source-grounded knowledge tag on the root line."))
        for priority in PRIORITY_TAG_RE.findall(card_body):
            if priority not in {"P1", "P2", "P3", "P4"}:
                findings.append(Finding(start + 1, "E034", "Flashcard priority tag must be #闪卡/优先级/P1# through P4."))
        priorities = PRIORITY_TAG_RE.findall(card_body)
        if not priorities:
            findings.append(Finding(start + 1, "E035", "Every accepted card needs exactly one #闪卡/优先级/P1# through P4 tag."))
        elif len(priorities) > 1:
            findings.append(Finding(start + 1, "E035", "Every accepted card needs exactly one flashcard priority tag."))
        if re.search(r"#闪卡/(?!优先级/)[^#\s]+#", card_body):
            findings.append(Finding(start + 1, "E034", "Flashcard tags must use the #闪卡/优先级/P1# through P4 namespace."))
        if renderer in {"list", "mark"} and not re.match(r"^-\s+", root):
            findings.append(Finding(start + 1, "E015", "list renderer IAL must attach to a root list item."))
        if renderer == "mark" and "==" not in card_body:
            findings.append(Finding(start + 1, "E016", "mark renderer requires a visible short cloze target."))
        if renderer == "blockquote" and not root.startswith(">"):
            findings.append(Finding(start + 1, "E017", "blockquote renderer IAL must attach to a blockquote root."))
        if renderer == "callout" and not re.match(r"^>\s+\[![A-Z]+\]", root):
            findings.append(Finding(start + 1, "E018", "callout renderer IAL must attach to a callout root."))
        kind = attrs.get("custom-dm-card-kind")
        has_nested_items = _has_nested_answer_items(card_body, renderer)
        has_table = _has_table(card_body)
        has_mermaid = _has_mermaid(card_body)
        mermaid_blocks = _mermaid_blocks(card_body)
        for _offset, _indent, mermaid_content in mermaid_blocks:
            if not _mermaid_has_diagram_type(mermaid_content):
                findings.append(Finding(start + 1, "E048", "Every Mermaid fence must begin with a supported diagram type such as flowchart or sequenceDiagram."))
            defined_classes, applied_classes = _mermaid_semantic_classes(mermaid_content)
            if not defined_classes.intersection(applied_classes):
                findings.append(Finding(start + 1, "W109", "Mermaid has no applied semantic class; inherit source classes or define and use known/recall/answer roles."))
        front_mermaids, answer_indent = _front_mermaid_blocks(card_body, renderer)
        if front_mermaids:
            if kind != "basic" or renderer != "list":
                findings.append(Finding(start + 1, "E049", "Question-side Mermaid is supported only for basic/list cards."))
            elif answer_indent is None or any(indent != answer_indent for _offset, indent, _content in front_mermaids):
                findings.append(Finding(start + 1, "E049", "Question-side Mermaid must share the first answer list's direct-child indentation and precede it."))
            if not any(RECALL_SLOT_RE.search(content) for _offset, _indent, content in front_mermaids):
                findings.append(Finding(start + 1, "W108", "Question-side Mermaid has no visible recall slot and may expose the answer instead of cueing it."))
        if kind == "basic" and "==" in front:
            findings.append(Finding(start + 1, "E036", "Basic question roots must use semantic style anchors, not ==...== highlights."))
        if kind == "mnemonic" and _is_question_front(front):
            findings.append(Finding(start + 1, "E037", "Mnemonic cards are named cue cards; do not render the front as a question."))
        if renderer == "callout" and not _is_question_front(front):
            findings.append(Finding(start + 1, "E067", "Callout titles are the card front; the title must be a complete source-grounded question ending in ？ or ?."))
        if renderer == "callout" and CALL_OUT_TITLE_STYLE_RE.search(front):
            findings.append(Finding(start + 1, "E068", "Callout titles must be plain-text questions without inline styling; keep style anchors in the answer body."))
        if renderer == "callout" and re.search(r"#[^#\s]+#", front):
            findings.append(Finding(start + 1, "W115", "Keep Callout knowledge and priority tags on their own immediately following quote line, not in the question title."))
        if kind == "mnemonic" and not _mnemonic_label(root):
            findings.append(Finding(start + 1, "E038", "Mnemonic roots must name the specific recall subject or relationship; a bare 口诀 label is insufficient."))
        if kind == "basic":
            if not _is_question_front(front):
                findings.append(Finding(start + 1, "E025", "Basic card fronts must state the question directly and end in ？ or ?."))
            answer_lines = _basic_answer_lines(card_body, renderer)
            if not answer_lines:
                findings.append(Finding(start + 1, "E026", "Basic cards require at least one unlabeled direct answer child."))
            if len(answer_lines) > max_answer_items:
                findings.append(Finding(start + 1, "E027", f"Card has {len(answer_lines)} answer items; split above {max_answer_items}."))
            for answer in answer_lines:
                if len(_visible_text(_answer_text(answer))) > max_answer_chars:
                    findings.append(Finding(start + 1, "E028", f"Answer item exceeds {max_answer_chars} visible characters; split or reject it."))
                answer_text = _visible_text(_answer_text(answer))
                if len(answer_text) > 42 or re.search(r"，(?:并|但|或者|或|且)|；|条件为|分别|不成|否则", answer_text):
                    answer_indent = len(answer) - len(answer.lstrip())
                    has_child = any(
                        len(line) - len(line.lstrip()) > answer_indent
                        and re.match(r"^\s+(?:-|\d+\.)\s+\S", line)
                        for line in card_body.splitlines()
                    )
                    if not has_child:
                        findings.append(Finding(start + 1, "W114", "Answer line combines multiple semantic clauses; split it into a governing parent and source-shaped child items."))
            basic_records.append(
                (
                    start + 1,
                    source_key,
                    card_id,
                    {fact for line in answer_lines if (fact := _normalized_answer_fact(line))},
                )
            )
            if _obviously_complex_flat_back(front, answer_lines, has_nested_items):
                findings.append(Finding(start + 1, "E046", "Complex basic backs need a source-shaped structure; nest dependent branches, preserve a meaningful order, or select another eligible carrier."))
            total_answer_chars = sum(len(_visible_text(_answer_text(line))) for line in answer_lines)
            if (
                len(answer_lines) >= 2
                and not has_nested_items
                and not has_table
                and not has_mermaid
                and total_answer_chars > 36
                and not re.search(r"[0-9一二三四五六七八九十两]+(?:大|项|类|种|个|条|方面|原则|要件|情形|条件)", _visible_text(front))
            ):
                findings.append(Finding(start + 1, "W102", "Review this flat multi-item back for a semantic parent/child relation or separate recall axes."))
            if _has_ordered_answers(card_body, renderer):
                if not _front_names_order(front):
                    findings.append(Finding(start + 1, "W103", "Ordered answers need an explicit sequence, procedure, chronology, or priority cue; source numbering alone is insufficient."))
                if source_text is not None:
                    scoped_visible_lines = (
                        source_topic_visible_lines[source_scope_topic]
                        if source_scope_topic in source_topic_visible_lines
                        else source_global_visible_lines
                    )
                    if not _source_names_order(scoped_visible_lines):
                        findings.append(Finding(start + 1, "W106", "The supplied source range has no sequence semantics; keep source order but use unordered peers unless order changes the rule."))
        if attrs.get("custom-dm-card-kind") == "cloze" and "==" not in card_body:
            findings.append(Finding(start + 1, "E019", "cloze cards need an explicit short ==term== target."))
        if kind != "mnemonic":
            for highlight in re.findall(r"==([^=\n]+)==", card_body):
                if len(_visible_text(highlight)) > 6:
                    findings.append(Finding(start + 1, "E029", "Non-mnemonic highlights must not exceed six visible characters."))
        if attrs.get("custom-dm-card-kind") == "mnemonic":
            if "==" not in card_body:
                findings.append(Finding(start + 1, "E020", "mnemonic cards require a highlighted source-grounded cue."))
            mapping_lines = [line for line in card_body.splitlines() if re.search(r"句|取字|首字|对应|组合|→", line)]
            if mapping_lines and any("==" not in line for line in mapping_lines):
                findings.append(Finding(start + 1, "E021", "Every mnemonic source sentence or mapping line needs an explicit ==highlight==."))
        if source_text is not None and kind in {"cloze", "mnemonic"}:
            scoped_visible_lines = (
                source_topic_visible_lines[source_scope_topic]
                if source_scope_topic in source_topic_visible_lines
                else source_global_visible_lines
            )
            for highlight in re.findall(r"==([^=\n]+)==", card_body):
                visible_highlight = _visible_text(highlight)
                if visible_highlight and not any(visible_highlight in line for line in scoped_visible_lines):
                    findings.append(Finding(start + 1, "E045", f"Cloze or mnemonic highlight is absent from the source provider range: {highlight}"))
        card_styles = set(STYLE_ANCHOR_RE.findall(card_body))
        style_signatures, has_foreground, has_background = _style_profile(card_body, kind)
        deck_card_styles.append(style_signatures)
        if len(style_signatures) == 1:
            findings.append(Finding(start + 1, "E047", "A styled card must use more than one source-grounded color/background style signature."))
        if style_signatures and (not has_foreground or not has_background):
            missing = "foreground color" if not has_foreground else "background/highlight"
            findings.append(Finding(start + 1, "W101", f"Style balance: this card has no {missing}; inherit one only when the source range supplies it."))
        advanced = [name for name, present in (("table", has_table), ("Mermaid", has_mermaid)) if present]
        if len(advanced) > 1:
            findings.append(Finding(start + 1, "W105", "A card uses both a table and Mermaid; choose one primary carrier unless both are necessary for one scoring axis."))
        if advanced:
            source_has_carrier = source_text is not None and all(
                (name == "table" and _has_table(source_text)) or (name == "Mermaid" and _has_mermaid(source_text))
                for name in advanced
            )
            if not source_has_carrier:
                findings.append(Finding(start + 1, "W104", f"Advanced carrier ({', '.join(advanced)}) is not directly inherited from the supplied source; audit every mapping."))
        if source_text is None:
            if not card_styles:
                findings.append(Finding(start + 1, "E030", "Every accepted card needs a valid MarkNote bold semantic color anchor."))
        else:
            scoped_styles = (
                source_topic_styles[source_scope_topic]
                if source_scope_topic in source_topic_styles
                else source_global_styles
            )
            for fragment in sorted(card_styles - scoped_styles):
                generated_rich_style = rich_style and "background-color" in fragment
                if generated_rich_style:
                    continue
                findings.append(Finding(start + 1, "E039", f"Styled fragment is not inherited byte-for-byte from the source provider range: {fragment}"))
            if scoped_styles and not card_styles.intersection(scoped_styles):
                findings.append(Finding(start + 1, "E040", "Card does not reuse any exact styled fragment from its source provider range."))
            card_visible = _visible_text(card_body)
            styles_by_text: dict[str, set[str]] = {}
            for fragment in scoped_styles:
                visible = _style_text(fragment)
                if visible:
                    styles_by_text.setdefault(visible, set()).add(fragment)
            for visible, variants in sorted(styles_by_text.items()):
                if visible in card_visible and not card_styles.intersection(variants):
                    findings.append(Finding(start + 1, "E041", f"Source-styled text lost its provider-scoped style in the card: {visible}"))
    for line, source_key, card_id, answer_facts in basic_records:
        if len(answer_facts) < 2:
            continue
        repeated = {
            fact
            for fact in answer_facts
            if any(
                other_source_key == source_key and other_card_id != card_id and fact in other_facts
                for _other_line, other_source_key, other_card_id, other_facts in basic_records
            )
        }
        if len(repeated) >= 2:
            findings.append(Finding(line, "W107", "This multi-answer card repeats facts already tested by sibling cards; reject a duplicate summary unless it adds a new relation or scoring axis."))
    for topic_id, locations in topic_lines.items():
        if len(locations) > max_cards_per_topic:
            findings.append(Finding(locations[0], "E013", f"Topic ID {topic_id!r} is reused by {len(locations)} cards; confirm a narrower atomic topic mapping or raise the reviewed limit."))
    if rich_style:
        findings.extend(_validate_rich_deck(text, deck_card_styles, len(accepted_card_lines)))
    if require_report:
        reports = list(REPORT_RE.finditer(text))
        if len(reports) != 1:
            findings.append(Finding(max(1, len(lines)), "E031", "Dedicated output requires exactly one candidate/accepted/rejected report."))
        else:
            candidate, accepted, rejected = (int(value) for value in reports[0].groups())
            if candidate != accepted + rejected or accepted != len(accepted_card_lines):
                line = text[:reports[0].start()].count("\n") + 1
                findings.append(Finding(line, "E032", "Report counts must reconcile and accepted must equal rendered card count."))
        source_protocol_lines = [
            number for number, line in enumerate(lines, start=1) if SOURCE_PROTOCOL_RE.fullmatch(line.strip())
        ]
        if len(source_protocol_lines) != 1:
            findings.append(Finding(max(1, len(lines)), "E043", "Dedicated output requires exactly one final source/protocol line."))
        else:
            last_nonblank = max((number for number, line in enumerate(lines, start=1) if line.strip()), default=1)
            if source_protocol_lines[0] != last_nonblank:
                findings.append(Finding(source_protocol_lines[0], "E043", "Source/protocol line must be the last nonblank line."))
    for number, line in enumerate(lines, start=1):
        if RUNTIME_RE.search(line):
            findings.append(Finding(number, "E014", "Runtime scheduling or Riff field leaked into output."))
        if AUDIT_PREAMBLE_RE.match(line):
            findings.append(Finding(number, "E042", "Internal source/protocol/style audit must not be emitted as a top-level card-deck preamble."))
    return sorted(set(findings), key=lambda item: (item.line, item.code, item.message))


def validate_ordinary(text: str) -> list[Finding]:
    findings: list[Finding] = []
    for number, line in enumerate(text.splitlines(), start=1):
        if re.search(r"custom-dm-[\w-]+\s*=|custom-riff-decks\s*=|\b(?:due|interval|suspend|bury)\s*=", line, re.IGNORECASE):
            findings.append(Finding(number, "O001", "Ordinary mode contains formal card or runtime metadata."))
        for tag in re.findall(r"#闪卡/优先级/([^#]+)#", line):
            if tag not in {"P1", "P2", "P3", "P4"}:
                findings.append(Finding(number, "O002", "Flashcard priority tag must be P1, P2, P3, or P4."))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", help="Draft Markdown path, or - to read the draft from standard input.")
    parser.add_argument("--source", type=Path, help="Source note used to verify provider-scoped style inheritance.")
    parser.add_argument("--mode", choices=("ordinary", "dedicated"), default="dedicated")
    parser.add_argument("--require-report", action="store_true")
    parser.add_argument("--rich-style", action="store_true", help="Apply the legal-goldquest rich visual contract to medium/complex dedicated decks.")
    parser.add_argument("--max-cards-per-topic", type=int, default=4)
    parser.add_argument("--max-answer-items", type=int, default=4)
    parser.add_argument("--max-answer-chars", type=int, default=84)
    args = parser.parse_args()
    output_label = "<stdin>" if args.output == "-" else args.output
    text = sys.stdin.read() if args.output == "-" else Path(args.output).read_text(encoding="utf-8")
    source_text = args.source.read_text(encoding="utf-8") if args.source else None
    findings = validate_ordinary(text) if args.mode == "ordinary" else validate(
        text,
        source_text=source_text,
        require_report=args.require_report,
        max_cards_per_topic=args.max_cards_per_topic,
        max_answer_items=args.max_answer_items,
        max_answer_chars=args.max_answer_chars,
        rich_style=args.rich_style,
    )
    if findings:
        for item in findings:
            print(f"{output_label}:{item.line}: {item.code}: {item.message}")
        if has_blocking_findings(findings):
            return 1
        print(f"PASS legal-flashcard {args.mode} validation with {len(findings)} warning(s): {output_label}")
        return 0
    print(f"PASS legal-flashcard {args.mode} validation: {output_label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
