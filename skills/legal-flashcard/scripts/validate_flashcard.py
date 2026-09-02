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
REPORT_YAML_RE = re.compile(r"(?ms)^```yaml\s*\n(?P<body>.*?)^```\s*$")
REPORT_KEY_RE = re.compile(r"^  (?P<key>candidates|accepted|rejected):\s*(?P<value>\d+)\s*$", re.MULTILINE)
AUDIT_PREAMBLE_RE = re.compile(
    r"^-\s+(?:源笔记|协议|标签|构成|着色图例|章节|样式继承|源笔记说明|高亮职责)："
)
RUNTIME_RE = re.compile(
    r"(?:custom-riff-decks|\bdue\b|\binterval\b|review\s+log|\bsuspend\b|\bbury\b|device\s+state|srs\s+state)",
    re.IGNORECASE,
)
KNOWLEDGE_TAG_RE = re.compile(r"#(?!闪卡/优先级/)[^#\s]+#")
PRIORITY_TAG_RE = re.compile(r"#闪卡/优先级/([^#\s]+)#")
GENERATED_LABEL_PREFIX_RE = re.compile(r"(?:问题|题干|答案|解析|问)[：:]")
EMOJI_PATTERN = re.compile(
    r"[\U0001F000-\U0001FAFF\u2300-\u23FF\u2600-\u27BF\u2B00-\u2BFF](?:\ufe0f|\U0001F3FB-\U0001F3FF|\u200d[\U0001F000-\U0001FAFF\u2300-\u27BF\u2B00-\u2BFF])*"
)
EMOJI_GENERIC_CUE_RE = re.compile(r"重点|难点|要点|注意|提示|警惕|小心|牢记|警示|易错|陷阱|考点|归纳|小结|总结")
POSITIONAL_TAG_SEGMENT_RE = re.compile(
    r"^(?:专题[0-9零一二三四五六七八九十百]+|第[0-9零一二三四五六七八九十百]+[讲章节课编部分]|[0-9零一二三四五六七八九十百]+)$"
)
LIST_ORDERED_MARKER_START_RE = re.compile(
    r"^(?:(?:\d{1,3})\s*[.)、．]|[（(]\s*\d{1,3}\s*[）)]|[①-⑳])(?=\s*[^\d\s]|\s*$)"
)
MNEMONIC_SOURCE_CUE_RE = re.compile(r"口诀|助记|速记|顺口溜|取字|首字|谐音")
MEMORY_CALLOUT_CUE_RE = re.compile(r"[!](?:TIP|NOTE|IMPORTANT|CAUTION|WARNING)[^\n]*(?:记忆|口诀|助记|联想|谐音|取字|首字)", re.IGNORECASE)
PRIORITY_REPORT_KEY_RE = re.compile(r"^  priorities:\s*$", re.MULTILINE)
PRIORITY_COUNT_RE = re.compile(r"^    (?P<key>P[1-4]):\s*(?P<value>\d+)\s*$", re.MULTILINE)
COLOR_ANCHOR_TOKEN_RE = re.compile(r"b3-font-(?:color|background)(?:[2-9]|1[0-3])")
IMAGE_REF_RE = re.compile(r"!\[[^\]]*\]\([^)]+\)")
CALL_OUT_TITLE_STYLE_RE = re.compile(r"\{:\s*style=|\*\*|==|~~|`|<\/?(?:em|u)(?:\s|>)", re.IGNORECASE)
MEMORY_LINK_CUE_RE = re.compile(r"联系记忆|关联记忆|对比记忆")
CALLOUT_LINE_RE = re.compile(r"^\s*>\s+\[![A-Za-z][A-Za-z0-9_-]*\]\s+\S", re.MULTILINE)
CALLOUT_STRONG_CUE_RE = re.compile(r"例外|但书|陷阱|易混|联系记忆|关联记忆|对比记忆|特别注意|风险提示")
CALLOUT_SOFT_CUE_RE = re.compile(r"不得|禁止|无效|不予|仅限|除非|否则|原则上")
MEMORY_LINK_TITLE_RE = re.compile(
    r"^(?P<indent>\s*)>\s+\[!(?P<type>[A-Za-z][A-Za-z0-9_-]*)\]\s*(?P<label>联系记忆|关联记忆|对比记忆)(?:[：:](?P<target>.+))?\s*$"
)
ORDER_CUE_RE = re.compile(r"顺序|次序|步骤|阶段|程序|流程|先后|依次|优先|第[一二三四五六七八九十0-9]+步")
CASE_FRONT_CUE_RE = re.compile(r"案例分析|习题|真题|张某|李律师|王某|甲与乙|甲、乙|A[.、：:]|B[.、：:]|C[.、：:]|D[.、：:]")
MERMAID_TYPE_RE = re.compile(
    r"^(?:flowchart|graph|sequenceDiagram|classDiagram|stateDiagram(?:-v2)?|erDiagram|journey|gantt|pie|"
    r"quadrantChart|requirementDiagram|gitGraph|mindmap|timeline|zenuml|sankey-beta|xychart-beta|"
    r"block-beta|packet-beta|kanban|architecture-beta|radar-beta|treemap-beta)\b"
)
RECALL_SLOT_RE = re.compile(r"(?:[①②③④⑤⑥⑦⑧⑨⑩]|\?{1,}|？{1,}|_{2,}|…)")
FLASHCARD_SUBJECT_TERMS = (
    "法定代理人", "委托代理人", "被代理人", "当事人", "特别授权", "一般授权",
    "代理权", "诉讼行为", "诉讼程序", "执行程序", "审判程序", "法律效力",
    "诉讼地位", "裁判对象", "实体权利", "程序性权利", "债权人", "债务人", "法院", "律师",
)
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


def _has_semantic_emoji_cue(text: str) -> bool:
    """Return whether prose has an open-set emoji cue outside ✅/❌ decision markers."""
    for line in re.sub(r"```.*?```", "", text, flags=re.DOTALL).splitlines():
        for match in EMOJI_PATTERN.finditer(line):
            if match.group() not in {"✅", "❌"}:
                return True
    return False


def _semantic_emoji_set(text: str) -> set[str]:
    """Return the set of open-set emoji cues (✅/❌ excluded, fences skipped)."""
    result: set[str] = set()
    for line in re.sub(r"```.*?```", "", text, flags=re.DOTALL).splitlines():
        for match in EMOJI_PATTERN.finditer(line):
            if match.group() not in {"✅", "❌"}:
                result.add(match.group())
    return result


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


def _has_generated_label_prefix(line: str) -> bool:
    """Return whether a card line opens with a generated 问题：/题干：/答案：/解析：/问： label,
    tolerating list/quote markers, bold asterisks, and leading emoji so none of them can mask it."""
    text = EMOJI_PATTERN.sub("", line).replace("*", "")
    text = re.sub(r"^[\s>\-+\d.]+", "", text)
    return bool(GENERATED_LABEL_PREFIX_RE.match(text))


def _ngrams(text: str, size: int = 6) -> set[str]:
    plain = _visible_text(text)
    return {plain[i:i + size] for i in range(max(0, len(plain) - size + 1))}


def _validate_callout_value(card_body: str, card_line: int) -> list[Finding]:
    """A Callout must add value: its body must not mostly repeat the card's non-Callout text (E095)."""
    findings: list[Finding] = []
    non_callout = "\n".join(line for line in card_body.splitlines() if not line.lstrip().startswith(">"))
    non_callout_grams = _ngrams(non_callout)
    lines = card_body.splitlines()
    for index, line in enumerate(lines):
        directive = re.match(r"^\s*>\s+\[![A-Za-z][A-Za-z0-9_-]*\]\s*(.*)$", line)
        if not directive:
            continue
        body_lines = []
        for body_line in lines[index + 1:]:
            if not body_line.lstrip().startswith(">"):
                break
            body_lines.append(body_line)
        grams = _ngrams("\n".join(body_lines))
        if not grams:
            continue
        overlap = len(grams & non_callout_grams) / len(grams)
        if overlap >= 0.6:
            findings.append(Finding(card_line, "E095", "A Callout's body mostly repeats the card's non-Callout answer text (≥60% character-gram overlap); a Callout must add value — state the boundary, exception, trap, or reasoning in new words, or drop it."))
    return findings


def _validate_line_color_diversity(card_body: str, card_line: int) -> list[Finding]:
    """Three consecutive content lines dominated by the same color lose indexing value (E096)."""
    findings: list[Finding] = []
    run = 0
    run_color: str | None = None
    for line in card_body.splitlines():
        stripped = line.strip()
        if (
            not stripped
            or re.match(r"^#{1,6}\s+", stripped)
            or re.match(r"^\s*```\s*$", stripped)
            or re.match(r"^\{:", stripped)
        ):
            run = 0
            run_color = None
            continue
        tokens = COLOR_ANCHOR_TOKEN_RE.findall(line)
        if not tokens:
            run = 0
            run_color = None
            continue
        dominant = Counter(tokens).most_common(1)[0]
        dominant_color, dominant_count = dominant
        if dominant_color != run_color or dominant_count / len(tokens) < 0.6:
            run = 1 if dominant_count / len(tokens) >= 0.6 else 0
            run_color = dominant_color if dominant_count / len(tokens) >= 0.6 else None
        else:
            run += 1
        if run >= 3:
            findings.append(Finding(card_line, "E096", "Three consecutive answer lines are each dominated by the same color; vary semantic colors across adjacent lines (or add backgrounds) so the palette stays an index."))
            run = 0
    return findings


def _long_back_items(card_body: str, threshold: int = 20) -> list[str]:
    """Back list items (direct or nested, outside Callouts/fences) longer than the threshold."""
    long_items: list[str] = []
    in_fence = False
    for raw in card_body.splitlines()[1:]:
        if re.match(r"^(?:\s*>\s*)?```", raw):
            in_fence = not in_fence
            continue
        if in_fence or raw.lstrip().startswith((">", "{:")):
            continue
        item = re.match(r"^\s*(?:[-*]|\d+\.)\s+(\S.*)$", raw)
        if item and len(_visible_text(item.group(1))) > threshold:
            long_items.append(raw.strip())
    return long_items


def _validate_emoji_semantics(text: str) -> list[Finding]:
    """Enforce deck-level emoji semantics: concept-anchored, diverse, not script-inserted.

    - `E094`: the same semantic emoji repeats more than eight times in one deck;
      one specific emoji maps to one specific concept and no single icon dominates.
    - `W129`: an emoji is anchored to a generic cue word (注意/重点/要点/考点/
      提示/陷阱…); anchor it to the specific legal concept instead.
    - `E130`: the same emoji + following-word pair repeats, a hard signature of
      scripted batch insertion; place emoji semantically per concept.
    - `E131`: most semantic emoji sit at sentence ends; each emoji must sit on
      the concept word it marks.
    - `E132`: most semantic emoji sit at line heads as label prefixes; embed them
      in the answer content instead.
    - `E133`: a large share of semantic emoji float with no neighboring concept
      word; anchor each icon to its term so it is visually bound.
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
        findings.append(Finding(1, "E131", f"{sentence_final}/{total_placed} semantic emoji are piled at sentence ends; hard gate — put each emoji directly on the concept word it marks (right after or before the term, one emoji per parallel concept) so the term and the icon are visually bound."))
    if total_placed >= 5 and line_head / total_placed >= 0.7:
        findings.append(Finding(1, "E132", f"{line_head}/{total_placed} semantic emoji are bunched at line heads as label prefixes; hard gate — embed emoji inside the answer content next to the concept words they mark (one per parallel concept) so the icons appear in the content, not only at the headline."))
    if total_placed >= 5 and dangling / total_placed >= 0.5:
        findings.append(Finding(1, "E133", f"{dangling}/{total_placed} semantic emoji float without a neighboring concept word (dangling at line ends, clause boundaries, or between punctuation); anchor each icon directly beside its term (词前或词后紧贴概念词), never as loose decoration."))
    for emoji, count in counts.items():
        if count > 8:
            findings.append(Finding(1, "E094", f"Emoji {emoji} repeats {count} times in this deck; one specific emoji maps to one specific concept — diversify so no single icon dominates."))
    if generic_hits:
        findings.append(Finding(1, "W129", f"{generic_hits} emoji anchor to generic cue words (注意/重点/要点/考点/提示/陷阱…); anchor each emoji to the specific legal concept inside the knowledge point instead of a commonplace cue word."))
    for pair, count in pairs.items():
        if count >= 6 and re.search(r"[\u4e00-\u9fff]", pair):
            findings.append(Finding(1, "E130", f"Emoji-word pair {pair} repeats {count} times; hard gate — this is scripted batch emoji insertion. Place emoji semantically per concept, never by mechanical word replacement."))
    return findings


def _parse_report_yaml(text: str) -> tuple[int, int, int, str, dict[str, int] | None] | None:
    blocks = list(REPORT_YAML_RE.finditer(text))
    if len(blocks) != 1:
        return None
    body = blocks[0].group("body")
    if not re.match(r"^report:\s*$", body, re.MULTILINE):
        return None
    values = {match.group("key"): int(match.group("value")) for match in REPORT_KEY_RE.finditer(body)}
    if set(values) != {"candidates", "accepted", "rejected"}:
        return None
    if not re.search(r"^  rejection_reasons:\s*(?:\{\})?\s*$", body, re.MULTILINE):
        return None
    note = re.search(r'^source:\s*\n  note:\s*"(?P<note>[^"\n]+)"\s*\n  protocol:\s*"(?P<protocol>DAMO 闪卡 schema 1)"\s*$', body, re.MULTILINE)
    if not note:
        return None
    priorities: dict[str, int] | None = None
    if PRIORITY_REPORT_KEY_RE.search(body):
        priority_values = {match.group("key"): int(match.group("value")) for match in PRIORITY_COUNT_RE.finditer(body)}
        if set(priority_values) == {"P1", "P2", "P3", "P4"}:
            priorities = priority_values
    return values["candidates"], values["accepted"], values["rejected"], note.group("note"), priorities


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


def _validate_memory_links(card_body: str, renderer: str | None, card_line: int) -> list[Finding]:
    findings: list[Finding] = []
    lines = card_body.splitlines()
    answer_lines = _basic_answer_lines(card_body, renderer)
    first_answer_index = next((index for index, line in enumerate(lines) if line in answer_lines), None)
    answer_indents = _list_item_indents(card_body)
    answer_indent = min(answer_indents) if answer_indents else None
    for index, line in enumerate(lines):
        if not MEMORY_LINK_CUE_RE.search(line) or "[!" not in line:
            continue
        match = MEMORY_LINK_TITLE_RE.match(line)
        target = match.group("target").strip() if match and match.group("target") else ""
        indent = len(match.group("indent")) if match else 0
        if renderer != "list" or answer_indent is None or indent <= answer_indent or first_answer_index is None or index <= first_answer_index:
            findings.append(Finding(card_line, "E082", "A memory-link Callout must be indented into the answer sub-list (deeper than the direct answer items) and follow the direct answer."))
        generic_target = bool(
            re.fullmatch(r"(?:与)?(?:其他|相关|相近)(?:内容|制度|考点|卡片)(?:比较|对照|联系)?", target)
            or target == "本节内容"
        )
        if match is None or not target or generic_target or CALL_OUT_TITLE_STYLE_RE.search(line):
            findings.append(Finding(card_line, "E083", "Memory-link Callout title must be plain text and name a specific linked doctrine/card after a colon."))
        if not match:
            continue
        block_lines: list[str] = []
        for candidate in lines[index + 1:]:
            if candidate.strip() and len(candidate) - len(candidate.lstrip()) < indent:
                break
            if candidate.strip().startswith("{: "):
                break
            block_lines.append(candidate)
        block_visible = _visible_text("\n".join(block_lines))
        block_items = sum(1 for candidate in block_lines if re.match(r"^\s*>\s+(?:-|\d+\.)\s+\S", candidate))
        if len(block_visible) > 100 or block_items > 2:
            findings.append(Finding(card_line, "W118", "Memory-link block is too large for post-answer context; keep one relation axis and leave the linked answer in its own card."))
    return findings


def _back_callout_violations(card_body: str, renderer: str | None) -> list[int]:
    """Return 1-based body line numbers of back Callouts not nested into the answer sub-list.

    A Callout mounted inside a list card belongs to the card back only when it is
    indented deeper than the direct answer items. A Callout at answer-item depth
    renders as a sibling of the answer list and breaks the card's retrieval unit;
    write it nested into the sub-list or as a plain sub-list item instead.
    """
    if renderer not in {"list", "mark"}:
        return []
    indents = _list_item_indents(card_body)
    if not indents:
        return []
    answer_indent = min(indents)
    violations: list[int] = []
    in_fence = False
    for index, line in enumerate(card_body.splitlines(), start=1):
        if re.match(r"^\s*(?:>\s*)?```", line):
            in_fence = not in_fence
            continue
        if in_fence or MEMORY_LINK_CUE_RE.search(line) or "[!" not in line:
            continue
        match = re.match(r"^(?P<indent> *)(?:>\s+)?\[![A-Za-z][A-Za-z0-9_-]*\]", line)
        if match and len(match.group("indent")) <= answer_indent:
            violations.append(index)
    return violations


def _leftover_card_container_lines(lines: list[str], cards: list[tuple[int, int, dict[str, str], str, list[str]]]) -> list[int]:
    """Return 1-based lines of custom-dm-* card IALs nested inside another card's body.

    A list/mark card's body ends at the first `{:` line found above its IAL. When
    that line is itself a card container (`custom-dm-*`), the source range had
    already been cardified; the generator must strip the leftover attribute line
    completely instead of keeping an already-cardified block.
    """
    markers: list[int] = []
    for start, _end, attrs, _raw, _keys in cards:
        if not any(key.startswith("custom-dm-") for key in attrs):
            continue
        if attrs.get("custom-dm-card-renderer") not in {"list", "mark"}:
            continue
        cursor = start - 1
        while cursor >= 0:
            line = lines[cursor]
            stripped = line.lstrip()
            if stripped.startswith("{:") and "custom-dm-" in line:
                markers.append(cursor + 1)
                break
            if stripped.startswith("{:") or re.match(r"^#{1,6}\s+", line):
                break
            if re.match(r"^-\s+", line):
                break
            if line.strip() and not line[0].isspace():
                break
            cursor -= 1
    return sorted(set(markers))


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


def _is_rich_complex_card(card_body: str, kind: str | None, renderer: str | None) -> bool:
    """Identify cards that need the GoldQuest per-card visual floor.

    A short one-fact card can remain visually restrained. Once a card carries
    a substantial answer, several direct children, or an advanced carrier, it
    is an explanation surface rather than a single recall cue and needs local
    semantic color density.
    """
    visible = _visible_text(re.sub(r"```.*?```", "", card_body, flags=re.DOTALL))
    answer_lines = _basic_answer_lines(card_body, renderer)
    cue = re.search(r"区别|对照|比较|例外|后果|陷阱|原则上|能否|是否|不得|错误|分别", visible)
    return (
        renderer == "callout"
        or len(answer_lines) >= 3
        or (len(answer_lines) >= 2 and len(visible) >= 130)
        or _has_table(card_body)
        or _has_mermaid(card_body)
        or bool(cue and len(visible) >= 130)
        or kind == "mnemonic" and len(visible) >= 70
    )


def _substantive_answer_lines(card_body: str, renderer: str | None) -> list[str]:
    """Return all answer prose lines eligible for GoldQuest-style density."""
    lines = card_body.splitlines()[1:]
    substantive: list[str] = []
    in_fence = False
    for line in lines:
        if re.match(r"^\s*(?:>|)?```", line):
            in_fence = not in_fence
            continue
        if in_fence or not line.strip() or line.lstrip().startswith("{: "):
            continue
        stripped = line.strip()
        if re.match(r"^#{1,6}\s+", stripped) or re.match(r"^\|.*\|$", stripped):
            continue
        tag_candidate = re.sub(r"^>\s*", "", stripped)
        if re.match(r"^>\s+\[![A-Z]+\]", stripped) or re.fullmatch(r"#[^#]+#(?:\s+#[^#]+#)*", tag_candidate):
            continue
        visible = _visible_text(line)
        if len(visible) >= 14:
            substantive.append(line)
    return substantive


def _styled_subject_gaps(card_body: str) -> list[str]:
    """Find legal role/concept terms that remain plain after a styled use.

    GoldQuest treats recurring subjects as a visual index: once a role is
    assigned a color, later occurrences cannot silently fall back to white.
    Remove complete styled fragments first so shorter aliases inside a longer
    styled phrase are not reported as false gaps.
    """
    prose = re.sub(r"```.*?```", "", card_body, flags=re.DOTALL)
    styled = STYLE_ANCHOR_RE.findall(prose)
    remaining = prose
    for fragment in styled:
        remaining = remaining.replace(fragment, "")
    gaps: list[str] = []
    for term in FLASHCARD_SUBJECT_TERMS:
        if term not in prose:
            continue
        if term in remaining:
            gaps.append(term)
    return gaps


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


def _foreground_counter(text: str) -> Counter[str]:
    colors: Counter[str] = Counter()
    for match in STYLE_ANCHOR_RE.finditer(text):
        style = re.search(r'style="([^"]+)"', match.group(0))
        if not style:
            continue
        colors.update(value.strip() for name, value in STYLE_PROPERTY_RE.findall(style.group(1)) if name == "color")
    return colors


def _has_substantive_callout(text: str) -> bool:
    return bool(CALLOUT_LINE_RE.search(text))


def _validate_rich_deck(
    text: str,
    card_styles: list[set[tuple[tuple[str, str], ...]]],
    card_foregrounds: list[Counter[str]],
    card_count: int,
    callout_card_count: int,
) -> list[Finding]:
    if not _is_rich_complex_deck(text, card_count):
        return []
    findings: list[Finding] = _validate_style_anchor_bounds(text)
    auxiliary = _auxiliary_style_families(text)
    if len(auxiliary) < 4:
        findings.append(Finding(1, "E060", f"Rich flashcard decks need at least four auxiliary style families; found {len(auxiliary)} ({', '.join(sorted(auxiliary)) or 'none'})."))
    structural = _structural_families(text)
    if len(structural) < 4:
        findings.append(Finding(1, "E061", f"Rich flashcard decks need at least four structural families; found {len(structural)} ({', '.join(sorted(structural)) or 'none'})."))
    if card_count >= 4:
        required_callout_cards = max(1, (card_count + 5) // 6)
        if callout_card_count < required_callout_cards:
            findings.append(Finding(1, "E084", f"Rich decks need substantive Callout coverage in at least {required_callout_cards}/{card_count} cards; found {callout_card_count}. Use a callout root or a nested answer Callout for a real exception, warning, conclusion peak, or memory relation."))
    backgrounds = len(re.findall(r"b3-font-background(?:[2-9]|1[0-3])", text))
    if backgrounds < 3:
        findings.append(Finding(1, "E062", f"Rich flashcard decks need at least three short background-color anchors; found {backgrounds}."))
    foregrounds, background_signatures = _distinct_style_dimensions(text)
    if len(foregrounds) <= 3 and len(background_signatures) < 3:
        findings.append(Finding(1, "E066", "A rich deck with a sparse foreground palette needs at least three distinct semantic background signatures; do not repeat a two-color foreground-only palette."))
    if len(foregrounds) < 4:
        findings.append(Finding(1, "E069", f"GoldQuest-level rich decks need at least four semantic foreground colors; found {len(foregrounds)}. Build a role dictionary instead of cycling a two- or three-color palette."))
    relation_cue = re.search(r"流程|程序|步骤|关系|对应|比较|区别|分支|情形|主体|阶段|如何", _visible_text(text))
    if relation_cue and "visual" not in structural:
        findings.append(Finding(1, "E063", "A rich deck with process, branch, role, comparison, or relation cues needs Mermaid, an inherited image, or another documented primary visual."))
    unique_signatures = set().union(*card_styles) if card_styles else set()
    if len(unique_signatures) <= 2 and unique_signatures:
        findings.append(Finding(1, "W111", "A styled rich deck uses two or fewer unique color/background signatures overall; revise toward three or more semantic roles."))
    for index, (left, right) in enumerate(zip(card_foregrounds, card_foregrounds[1:]), start=1):
        if not left or not right:
            continue
        colors = set(left) | set(right)
        weighted_overlap = sum(min(left[color], right[color]) for color in colors) / sum(
            max(left[color], right[color]) for color in colors
        )
        left_dominant, left_count = left.most_common(1)[0]
        right_dominant, right_count = right.most_common(1)[0]
        repeats_dominant = (
            left_dominant == right_dominant
            and left_count / left.total() >= 0.50
            and right_count / right.total() >= 0.50
        )
        if weighted_overlap >= 0.60 or repeats_dominant:
            reason = (
                f"{weighted_overlap:.0%} weighted overlap"
                if weighted_overlap >= 0.60
                else f"shared dominant color {left_dominant} supplies at least half of both cards"
            )
            findings.append(
                Finding(
                    1,
                    "E080",
                    f"Adjacent cards {index} and {index + 1} over-reuse their foreground palette ({reason}); diversify source-grounded semantic roles or reorder the cards.",
                )
            )
    coverage = Counter(color for colors in card_foregrounds for color in colors)
    if coverage and card_count >= 3:
        foreground_occurrences: Counter[str] = Counter()
        for colors in card_foregrounds:
            foreground_occurrences.update(colors)
        dominant_color, dominant_occurrences = foreground_occurrences.most_common(1)[0]
        dominant_cards = coverage[dominant_color]
        total_occurrences = sum(foreground_occurrences.values())
        dominant_share = dominant_occurrences / total_occurrences if total_occurrences else 0.0
        balance_ceiling = max(0.30, 2 / len(foreground_occurrences))
        if dominant_share > balance_ceiling:
            findings.append(
                Finding(
                    1,
                    "E081",
                    f"Foreground palette is unbalanced: {dominant_color} covers {dominant_cards}/{len(card_foregrounds)} cards and {dominant_share:.0%} of foreground anchors (limit {balance_ceiling:.0%}); treat generic color-table roles as soft cues and distribute local semantic roles across the approved palette.",
                )
            )
        elif dominant_share > 0.25:
            findings.append(
                Finding(
                    1,
                    "W124",
                    f"Foreground palette is becoming visually dominant: {dominant_color} supplies {dominant_share:.0%} of foreground anchors; diversify grounded local roles before this crosses the {balance_ceiling:.0%} hard ceiling.",
                )
            )
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


def _front_requires_order(front: str) -> bool:
    return bool(ORDER_CUE_RE.search(_visible_text(re.sub(r"#[^#\s]+#", "", front))))


def _source_exercise_contains_front(front: str, source_text: str | None) -> bool:
    if not source_text:
        return False
    visible_front = _visible_text(re.sub(r"^\s*[-*]\s+", "", re.sub(r"#[^#\s]+#", "", front)))
    if len(visible_front) < 12:
        return False
    lines = source_text.splitlines()
    exercise_indexes = [
        index for index, line in enumerate(lines)
        if re.search(r"习题|真题|案例分析|回答与解析|答案与解析", line)
    ]
    if not exercise_indexes:
        return False
    for index in exercise_indexes:
        window = "".join(_visible_text(line) for line in lines[index:index + 80])
        if visible_front in window:
            return True
    return False


def _normalized_answer_fact(line: str) -> str:
    return _visible_text(_answer_text(line)).strip("。；;，,")


def _source_maps(
    source_text: str,
) -> tuple[set[str], dict[str, set[str]], list[str], dict[str, list[str]], set[str], dict[str, set[str]]]:
    global_fragments = set(STYLE_ANCHOR_RE.findall(source_text))
    topic_fragments: dict[str, set[str]] = {}
    global_visible_lines = [_visible_text(line) for line in source_text.splitlines() if _visible_text(line)]
    topic_visible_lines: dict[str, list[str]] = {}
    global_images = set(IMAGE_REF_RE.findall(source_text))
    topic_images: dict[str, set[str]] = {}
    current_topic: str | None = None
    for line in source_text.splitlines():
        provider = PROVIDER_IAL_RE.fullmatch(line.strip())
        if provider:
            current_topic = provider.group(1)
            topic_fragments.setdefault(current_topic, set())
            topic_visible_lines.setdefault(current_topic, [])
            topic_images.setdefault(current_topic, set())
            continue
        if current_topic is not None:
            topic_fragments[current_topic].update(STYLE_ANCHOR_RE.findall(line))
            topic_images[current_topic].update(IMAGE_REF_RE.findall(line))
            visible = _visible_text(line)
            if visible:
                topic_visible_lines[current_topic].append(visible)
    return global_fragments, topic_fragments, global_visible_lines, topic_visible_lines, global_images, topic_images


def _style_text(fragment: str) -> str:
    match = re.match(r"\*\*([^*\n]+)\*\*", fragment)
    return _visible_text(match.group(1)) if match else ""


def _source_scope_topic(topic_id: str, known_topics: set[str]) -> str | None:
    if topic_id in known_topics:
        return topic_id
    parents = [known for known in known_topics if topic_id.startswith(f"{known}-")]
    return max(parents, key=len) if parents else None


def _priority_distribution_findings(priorities: list[str], line: int = 1) -> list[Finding]:
    count = len(priorities)
    if count < 4:
        return []
    findings: list[Finding] = []
    histogram = Counter(priorities)
    if histogram["P2"] * 2 > count:
        findings.append(Finding(line, "E089", f"P2 is the default tier for {histogram['P2']}/{count} cards (more than half the deck); recompare every P2 card against the source and re-rank — P2 is not a fallback."))
    elif histogram["P2"] / count >= 0.5:
        findings.append(Finding(line, "W121", f"P2 dominates {histogram['P2']}/{count} cards; recompare priorities against the source instead of using P2 as a fallback."))
    if count >= 8 and len(histogram) < 3:
        findings.append(Finding(line, "W122", f"This {count}-card deck uses only {len(histogram)} priority level(s); audit source-relative separation without mechanically filling tiers."))
    if count >= 8 and histogram["P4"] == 0:
        findings.append(Finding(line, "W123", "This large deck has no P4 cards; verify whether low-yield retained material was promoted or whether the source genuinely has no P4 tier."))
    return findings


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
    for number, line in enumerate(lines, start=1):
        if MEMORY_LINK_CUE_RE.search(line) and "[!" in line:
            match = MEMORY_LINK_TITLE_RE.match(line)
            if match and len(match.group("indent")) < 4:
                findings.append(Finding(number, "E082", "A memory-link Callout must be indented inside a list-card back and follow the direct answer."))
    seen: dict[str, int] = {}
    topic_lines: dict[str, list[int]] = {}
    accepted_card_lines: list[int] = []
    basic_records: list[tuple[int, str, str, set[str]]] = []
    deck_card_styles: list[set[tuple[tuple[str, str], ...]]] = []
    accepted_priorities: list[str] = []
    deck_card_foregrounds: list[Counter[str]] = []
    deck_callout_card_count = 0
    mnemonic_card_count = 0
    emoji_card_count = 0
    source_global_styles: set[str] = set()
    source_topic_styles: dict[str, set[str]] = {}
    source_global_visible_lines: list[str] = []
    source_topic_visible_lines: dict[str, list[str]] = {}
    source_global_images: set[str] = set()
    source_topic_images: dict[str, set[str]] = {}
    if source_text is not None:
        (
            source_global_styles,
            source_topic_styles,
            source_global_visible_lines,
            source_topic_visible_lines,
            source_global_images,
            source_topic_images,
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
        front_without_tags = re.sub(r"#[^#\s]+#", "", front)
        front_length = len(_visible_text(front_without_tags))
        if front_length > 70:
            findings.append(Finding(start + 1, "E092", f"Card front is too long ({front_length} visible characters; keep a question or mnemonic cue within about 70). Move the extra context into the back, or keep it on the front with <br /> line breaks or a text-block Callout — never a long front."))
        in_fence = False
        for body_line in card_body.splitlines():
            if re.match(r"^\s*(?:>\s*)?```", body_line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            if _has_generated_label_prefix(body_line):
                findings.append(Finding(start + 1, "E044", "Write the question and answer items directly; no 问题：/题干：/答案：/解析：/问： label prefix is allowed on any card line (front, back, or Callout body)."))
                break
        if not KNOWLEDGE_TAG_RE.search(card_body):
            findings.append(Finding(start + 1, "E033", "Accepted cards need a source-grounded knowledge tag on the root line."))
        for tag in KNOWLEDGE_TAG_RE.findall(card_body):
            positional = [segment for segment in tag.strip("#").split("/") if POSITIONAL_TAG_SEGMENT_RE.match(segment)]
            if positional:
                findings.append(Finding(start + 1, "E101", "Knowledge tags must use stable source-named concepts, not position labels: remove the " + "、".join(positional) + " segment from " + tag + " and replace it with the chapter or topic name (e.g. 专题二 → 诉的基本理论)."))
        if renderer == "mark" and _list_item_indents(card_body):
            findings.append(Finding(start + 1, "E093", "A cloze/mark card is front-only and has no back; bare child list items are parsed as the back card. Wrap any sub-list inside a Callout (e.g. a `> [!TIP]` block containing the items) or use <br /> line breaks instead."))
        findings.extend(_validate_callout_value(card_body, start + 1))
        findings.extend(_validate_line_color_diversity(card_body, start + 1))
        if source_text is not None:
            scoped_images = (
                source_topic_images[source_scope_topic]
                if source_scope_topic in source_topic_images
                else source_global_images
            )
            if scoped_images and not re.search(r"!\[[^\]]*\]\([^)]+\)", card_body):
                findings.append(Finding(start + 1, "W126", "The card's source range carries a Markdown diagram; copy it onto the card back beneath a governing answer child so the illustration stays with the rule."))
        for priority in PRIORITY_TAG_RE.findall(card_body):
            if priority not in {"P1", "P2", "P3", "P4"}:
                findings.append(Finding(start + 1, "E034", "Flashcard priority tag must be #闪卡/优先级/P1# through P4."))
        priorities = PRIORITY_TAG_RE.findall(card_body)
        if not priorities:
            findings.append(Finding(start + 1, "E035", "Every accepted card needs exactly one #闪卡/优先级/P1# through P4 tag."))
        elif len(priorities) > 1:
            findings.append(Finding(start + 1, "E035", "Every accepted card needs exactly one flashcard priority tag."))
        elif priorities[0] in {"P1", "P2", "P3", "P4"}:
            accepted_priorities.append(priorities[0])
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
        has_callout = _has_substantive_callout(card_body)
        if has_callout:
            deck_callout_card_count += 1
        if kind == "mnemonic":
            mnemonic_card_count += 1
        card_has_emoji = _has_semantic_emoji_cue(card_body)
        if card_has_emoji:
            emoji_card_count += 1
        simple_card = not _is_rich_complex_card(card_body, kind, renderer)
        if rich_style and not card_has_emoji and not simple_card:
            findings.append(Finding(start + 1, "E090", "This non-simple card needs at least one semantic emoji cue beyond ✅/❌; position it beside the labeled legal relationship, boundary, or conclusion."))
        elif rich_style and card_has_emoji and renderer != "callout":
            front_line = _front_line(card_body, renderer) or (card_body.splitlines()[0] if card_body else "")
            back_part = "\n".join(card_body.splitlines()[1:])
            if not (_has_semantic_emoji_cue(front_line) and _has_semantic_emoji_cue(back_part)):
                findings.append(Finding(start + 1, "W127", "A card that uses emoji should carry at least one on both the front and the back; keep a semantic cue on each side."))
            shared = _semantic_emoji_set(front_line) & _semantic_emoji_set(back_part)
            if shared:
                findings.append(Finding(start + 1, "E100", "This card reuses the same emoji on the front and the back (" + "、".join(sorted(shared)) + "); duplicating one marker is the lazy way to fake the emoji cue — the front anchors its question concept, so the back must anchor a different concept with a different emoji."))
        if rich_style and CALLOUT_STRONG_CUE_RE.search(_visible_text(card_body)) and not has_callout:
            findings.append(Finding(start + 1, "E085", "This card contains an explicit exception, trap, confusion, risk, or memory-link cue; render that semantic peak as a callout root or a nested answer Callout."))
        elif rich_style and CALLOUT_SOFT_CUE_RE.search(_visible_text(card_body)) and not has_callout:
            findings.append(Finding(start + 1, "W125", "This card contains a prohibition, invalidity, limiting, or principle cue; review whether a nested Callout would make the boundary easier to retrieve."))
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
            if _front_requires_order(front) and not _has_ordered_answers(card_body, renderer) and not has_table and not has_mermaid:
                findings.append(Finding(start + 1, "E078", "The front asks for a sequence, procedure, stage, or order, so its direct answer children must use an ordered Markdown list (1., 2., 3.)."))
            if _source_exercise_contains_front(front, source_text):
                findings.append(Finding(start + 1, "E079", "This card front reproduces a source exercise or case question. Reject the case replay; extract a general reusable rule or application path instead."))
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
            long_back_items = _long_back_items(card_body)
            if long_back_items:
                findings.append(Finding(start + 1, "E097", f"{len(long_back_items)} back item(s) exceed 20 visible characters; split each by semantics into a governing parent plus child items — use 1. ordered lists for steps, procedures, or sequences — instead of one long line."))
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
        findings.extend(_validate_memory_links(card_body, renderer, start + 1))
        for body_line in _back_callout_violations(card_body, renderer):
            violation_line = root_index + body_line if root_index is not None else start + 1
            findings.append(Finding(violation_line, "E086", "A Callout inside a list card must be indented into the answer sub-list (deeper than the direct answer items) or written as a normal sub-list item."))
        style_signatures, has_foreground, has_background = _style_profile(card_body, kind)
        deck_card_styles.append(style_signatures)
        deck_card_foregrounds.append(_foreground_counter(card_body))
        if len(style_signatures) == 1:
            findings.append(Finding(start + 1, "E047", "A styled card must use more than one source-grounded color/background style signature."))
        if rich_style and _is_rich_complex_card(card_body, kind, renderer):
            if len(style_signatures) == 2:
                findings.append(Finding(start + 1, "W110", "Complex card uses exactly two color/background signatures; review whether a third source or MarkNote role is available instead of stopping at E047."))
            if not has_foreground or not has_background:
                findings.append(Finding(start + 1, "W116", "Complex card is missing one visual dimension: keep a semantic foreground role and a background/highlight peak when the source or approved style plan supplies both."))
            if not _auxiliary_style_families(card_body):
                findings.append(Finding(start + 1, "W117", "Complex card has no auxiliary style family; add only a source-grounded highlight, underline, code, strike, or italic when it marks a real boundary or retrieval cue."))
            for answer_line in _substantive_answer_lines(card_body, renderer):
                anchor_count = len(STYLE_ANCHOR_RE.findall(answer_line))
                mnemonic_or_cloze_mark = kind in {"cloze", "mnemonic"} and "==" in answer_line
                if anchor_count == 0 and not mnemonic_or_cloze_mark:
                    findings.append(Finding(start + 1, "E074", "Every substantive answer line of fourteen or more visible characters needs a short semantic color/background anchor in rich mode, matching GoldQuest's E622 density rule."))
                sentence_count = len(re.findall(r"[。！？；]", _visible_text(answer_line)))
                if sentence_count >= 3 and anchor_count * 2 < sentence_count:
                    findings.append(Finding(start + 1, "E075", "A multi-sentence answer line needs at least one semantic color anchor per one or two sentences, matching GoldQuest's E616 rule."))
            for term in _styled_subject_gaps(card_body):
                findings.append(Finding(start + 1, "E076", f"Recurring subject or legal concept '{term}' has an uncolored answer occurrence; color it consistently for the same local role, while allowing another approved color when the relation changes."))
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
                generated_rich_style = rich_style and bool(re.search(r"(?:color|background-color):\s*var\(--b3-font-(?:color|background)(?:[2-9]|1[0-3])\)", fragment))
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
    for leftover_line in _leftover_card_container_lines(lines, cards):
        findings.append(Finding(leftover_line, "E087", "Card body contains a leftover card container; strip the nested custom-dm-* attribute line completely instead of keeping an already-cardified block."))
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
    findings.extend(_priority_distribution_findings(accepted_priorities, accepted_card_lines[0] if accepted_card_lines else 1))
    findings.extend(_validate_emoji_semantics(text))
    if rich_style and accepted_card_lines and _is_rich_complex_deck(text, len(accepted_card_lines)):
        if emoji_card_count / len(accepted_card_lines) <= 0.8:
            findings.append(Finding(1, "E091", f"Rich decks must keep overall emoji coverage above 80% of accepted cards; {emoji_card_count}/{len(accepted_card_lines)} carry a semantic emoji cue. Add concept-anchored emoji to the bare cards (simple cards are the only tolerated minority)."))
    if source_text is not None and mnemonic_card_count == 0 and (
        MNEMONIC_SOURCE_CUE_RE.search(source_text) or MEMORY_CALLOUT_CUE_RE.search(source_text)
    ):
        findings.append(Finding(1, "W128", "The source contains mnemonic material (a 口诀 label or an implicit mnemonic via inline-code sequence or memory Callout); turn it into a mnemonic card with a highlighted cue and decoded segments so it stays retrievable."))
    if rich_style:
        findings.extend(_validate_rich_deck(text, deck_card_styles, deck_card_foregrounds, len(accepted_card_lines), deck_callout_card_count))
    if require_report:
        report_values = _parse_report_yaml(text)
        if report_values is None:
            findings.append(Finding(max(1, len(lines)), "E070", "Dedicated output requires exactly one valid ```yaml report block with report.candidates, report.accepted, report.rejected, report.rejection_reasons, and report.priorities (P1-P4 counts)."))
        else:
            candidate, accepted, rejected, _source_note, priorities = report_values
            if candidate != accepted + rejected or accepted != len(accepted_card_lines):
                line = next((number for number, line in enumerate(lines, start=1) if line.strip() == "```yaml"), max(1, len(lines)))
                findings.append(Finding(line, "E032", "Report counts must reconcile and accepted must equal rendered card count."))
            actual_priorities = Counter(accepted_priorities)
            expected_priorities = {f"P{i}": actual_priorities[f"P{i}"] for i in range(1, 5)}
            if priorities != expected_priorities:
                line = next((number for number, line in enumerate(lines, start=1) if line.strip() == "```yaml"), max(1, len(lines)))
                findings.append(Finding(line, "E088", f"Report priority counts must match the accepted cards' #闪卡/优先级/# distribution: expected {expected_priorities}, got {priorities}."))
            report_block = next((match for match in REPORT_YAML_RE.finditer(text)), None)
            last_nonblank = max((number for number, line in enumerate(lines, start=1) if line.strip()), default=1)
            report_end = text[:report_block.end()].rstrip("\n").count("\n") + 1 if report_block else 1
            if report_end != last_nonblank:
                findings.append(Finding(report_end, "E071", "The YAML report and source/protocol fields must be the final nonblank block."))
    for number, line in enumerate(lines, start=1):
        if RUNTIME_RE.search(line):
            findings.append(Finding(number, "E014", "Runtime scheduling or Riff field leaked into output."))
        if AUDIT_PREAMBLE_RE.match(line):
            findings.append(Finding(number, "E042", "Internal source/protocol/style audit must not be emitted as a top-level card-deck preamble."))
    for number, line in enumerate(lines, start=1):
        if not re.match(r"^\s*>\s+\[![A-Z]+\]", line):
            continue
        if number > 1:
            previous = lines[number - 2]
            if (
                previous.strip()
                and not previous.lstrip().startswith(">")
                and not re.match(r"^#{1,6}\s+", previous)
                and not re.match(r"^\s*```\s*$", previous)
            ):
                findings.append(Finding(number, "E098", "A Callout directive must be preceded by a blank line (or the start of a block, another quote line, a heading, or a fence boundary); directly after a list item or paragraph it is parsed as continuation text and will not be recognized."))
    in_fence = False
    for number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or not stripped:
            continue
        content = stripped
        while content.startswith(">"):
            content = content[1:].lstrip()
        if not re.match(r"^[-+*]\s+", content):
            continue
        after_marker = re.sub(r"^[-+*]\s+", "", content)
        if LIST_ORDERED_MARKER_START_RE.match(after_marker):
            findings.append(Finding(number, "E099", "A list item's text begins with an ordered-list marker (1. / 1、 / 1) / （1） / ①); the card parser reads it as a nested ordered list and misrecognizes the structure — remove the marker from the item text, or give each numbered child its own indented list line."))
    return sorted(set(findings), key=lambda item: (item.line, item.code, item.message))


def validate_ordinary(text: str) -> list[Finding]:
    findings: list[Finding] = []
    priorities: list[str] = []
    for number, line in enumerate(text.splitlines(), start=1):
        if re.search(r"custom-dm-[\w-]+\s*=|custom-riff-decks\s*=|\b(?:due|interval|suspend|bury)\s*=", line, re.IGNORECASE):
            findings.append(Finding(number, "O001", "Ordinary mode contains formal card or runtime metadata."))
        for tag in re.findall(r"#闪卡/优先级/([^#]+)#", line):
            if tag not in {"P1", "P2", "P3", "P4"}:
                findings.append(Finding(number, "O002", "Flashcard priority tag must be P1, P2, P3, or P4."))
            else:
                priorities.append(tag)
    findings.extend(_priority_distribution_findings(priorities))
    return findings


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
        print(f"... {hidden} more finding(s) not shown of {len(findings)} total. Focus with --code <CODE> (repeatable, e.g. --code E041), lift the cap with --all, or dump everything with --format json.")
    print(f"SUMMARY {label}: {len(findings)} finding(s); by code: {code_summary(findings)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", help="Draft Markdown path, or - to read the draft from standard input.")
    parser.add_argument("--source", type=Path, help="Source note used to verify provider-scoped style inheritance.")
    parser.add_argument("--mode", choices=("ordinary", "dedicated"), default="dedicated")
    parser.add_argument("--require-report", action=argparse.BooleanOptionalAction, default=True, help="Require the bottom YAML report in dedicated mode (strict default). Relaxed mode is only available by passing the COMPLETE relaxation set --no-require-report --no-rich-style together; if any relaxation parameter is missing, validation refuses to run.")
    parser.add_argument("--rich-style", action=argparse.BooleanOptionalAction, default=True, help="Apply the legal-goldquest rich visual contract to medium/complex dedicated decks (strict default).")
    parser.add_argument("--max-cards-per-topic", type=int, default=4)
    parser.add_argument("--max-answer-items", type=int, default=4)
    parser.add_argument("--max-answer-chars", type=int, default=84)
    parser.add_argument("--all", action="store_true", help="Print every finding instead of the bounded default report.")
    parser.add_argument("--code", action="append", metavar="CODE", help="Show only findings with this code in the text report (repeatable). Validation and the exit code always cover every finding.")
    parser.add_argument("--max-report", type=int, default=DEFAULT_REPORT_LIMIT, help=f"Text-report cap (default {DEFAULT_REPORT_LIMIT}); --all lifts the cap.")
    args = parser.parse_args()
    if args.mode == "dedicated":
        relaxed = [flag for flag, enabled in (("--no-require-report", args.require_report), ("--no-rich-style", args.rich_style)) if not enabled]
        if relaxed:
            missing = [flag for flag in ("--no-require-report", "--no-rich-style") if flag not in relaxed]
            if missing:
                print(
                    "Relaxed mode requires the COMPLETE relaxation set; missing: "
                    + ", ".join(missing)
                    + ". Strict mode is the default in dedicated mode: pass --no-require-report --no-rich-style together to relax, or drop the relaxation flags.",
                    file=sys.stderr,
                )
                return 2
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
        error_count = sum(not item.code.startswith("W") for item in findings)
        warning_count = len(findings) - error_count
        print_finding_report(
            findings,
            render=lambda item: f"{output_label}:{item.line}: {item.code}: {item.message}",
            label=f"{output_label} [E:{error_count} W:{warning_count}]",
            show_all=args.all,
            only_codes=args.code,
            limit=args.max_report,
        )
        if has_blocking_findings(findings):
            return 1
        print(f"PASS legal-flashcard {args.mode} validation with {len(findings)} warning(s): {output_label}")
        return 0
    print(f"PASS legal-flashcard {args.mode} validation: {output_label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
