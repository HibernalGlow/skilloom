#!/usr/bin/env python3
"""Reject formal structure that does not carry GoldQuest legal reasoning."""

from __future__ import annotations

import re
from dataclasses import dataclass


STATIC_VISUAL_PATTERN = re.compile(
    r"!\[[^\]]*(?:可视化|图解|流程图|关系图|决策图|时间线|diagram)[^\]]*\]"
    r"\([^)\s]+?\.(?:svg|png)(?:[?#][^)]*)?\)",
    re.IGNORECASE,
)
FENCE_PATTERN = re.compile(r"^(?:\s*>\s*)?```(?P<lang>[A-Za-z0-9_-]*)\s*$")
LIST_ITEM_PATTERN = re.compile(r"^(?P<indent>\s*)(?:[-+*]|\d+[.)])\s+(?P<body>\S.*)$")
OPTION_REPLAY_PATTERN = re.compile(r"^[✅❌]\s*(?:[A-Z]|[甲乙丙丁戊])(?:[.、:：\s]|项)")
MECHANICAL_LABEL_PATTERN = re.compile(
    r"^(?:推理主线|推理环节|分析环节|判断环节|逻辑环节|推理步骤|步骤|阶段)\s*\d*[：:]?$"
)
GENERIC_MERMAID_LABEL_PATTERN = re.compile(
    r"^(?:题干|问题|逐项判断|选项判断|判断|结论|正确|错误|排除|当选|不当选|选|不选|"
    r"[A-D](?:项|选项)?(?:正确|错误|排除|当选|不当选|选|不选)?)$",
    re.IGNORECASE,
)
CALLOUT_DIRECTIVE_PATTERN = re.compile(r"^\s*>\s*\[!(?:TIP|NOTE|IMPORTANT|CAUTION|WARNING)\]", re.IGNORECASE)
RELATION_CUE_PATTERN = re.compile(
    r"应当|不得|可以|只有|除非|若|如果|但|例外|前提|条件|程序|后果|承担|适用|导致|属于|"
    r"归于|先于|同时|之后|之前|不受|由[^，。；]{1,18}(?:承担|决定|负责|承受)"
)
GENERIC_CALLOUT_PATTERNS = (
    re.compile(r"本题核心考查.*逐项辨析后的破绽决定正误"),
    re.compile(r"偷换概念或以偏概全.*回到题干限定.*回放原文"),
    re.compile(r"逐项核对题干限定.*排除其余项"),
)
DEFERRED_REASONING_HEADING_PATTERN = re.compile(r"^#{1,6}\s+(?:综合推理|完整推理|推理过程|统一推理)\s*$")
OPTION_ANALYSIS_HEADING_PATTERN = re.compile(r"^#{1,6}\s+(?:逐项辨析|选项辨析|逐项分析)\s*$")
INLINE_MARKUP_PATTERN = re.compile(r"\{:\s*[^}\n]*\}|</?(?:u|em|strong|span)\b[^>]*>", re.IGNORECASE)
COLOR_ANCHOR_PATTERN = re.compile(r"b3-font-(?:color|background)\d+")


@dataclass(frozen=True)
class SemanticStructureFinding:
    code: str
    line: int
    message: str


def visual_families(value: str) -> set[str]:
    """Return SiYuan-compatible visual carriers present in Markdown."""
    families: set[str] = set()
    if re.search(r"(?m)^(?:\s*>\s*)?```mermaid\s*$", value):
        families.add("mermaid")
    if re.search(r"(?m)^(?:\s*>\s*)?```html\s*$", value):
        families.add("html")
    if STATIC_VISUAL_PATTERN.search(value):
        families.add("static-image")
    return families


def _plain(value: str) -> str:
    value = INLINE_MARKUP_PATTERN.sub("", value)
    value = re.sub(r"[`*_~=#>\[\]{}()\"'\s，。；：、,.!?！？]", "", value)
    return value


def _fenced_blocks(lines: list[str], language: str) -> list[tuple[int, list[str]]]:
    blocks: list[tuple[int, list[str]]] = []
    start = 0
    body: list[str] = []
    active_language = ""
    for offset, line in enumerate(lines):
        match = FENCE_PATTERN.match(line)
        if not match:
            if active_language:
                body.append(re.sub(r"^\s*>\s?", "", line))
            continue
        if not active_language:
            active_language = match.group("lang").lower()
            start = offset
            body = []
        else:
            if active_language == language:
                blocks.append((start, body))
            active_language = ""
            body = []
    return blocks


def _prose_outside_fences(lines: list[str]) -> str:
    prose: list[str] = []
    in_fence = False
    for line in lines:
        if FENCE_PATTERN.match(line):
            in_fence = not in_fence
        elif not in_fence:
            prose.append(line)
    return _plain("\n".join(prose))


def _mermaid_labels(body: list[str]) -> set[str]:
    source = "\n".join(body)
    candidates = re.findall(r'[\[({]\s*"([^"\n]+)"\s*[\])}]', source)
    candidates += re.findall(r"\[(?!\[)([^\[\]\n]+)\]", source)
    candidates += re.findall(r'\|\s*"?([^|"\n]+)"?\s*\|', source)
    labels: set[str] = set()
    for candidate in candidates:
        label = _plain(candidate)
        if len(label) >= 2 and not GENERIC_MERMAID_LABEL_PATTERN.fullmatch(label):
            labels.add(label)
    return labels


def _callout_blocks(lines: list[str]) -> list[tuple[int, str]]:
    blocks: list[tuple[int, str]] = []
    index = 0
    while index < len(lines):
        if not CALLOUT_DIRECTIVE_PATTERN.match(lines[index]):
            index += 1
            continue
        start = index
        body: list[str] = []
        index += 1
        while index < len(lines) and re.match(r"^\s*>($|\s)", lines[index]):
            body.append(re.sub(r"^\s*>\s?", "", lines[index]))
            index += 1
        blocks.append((start, "\n".join(body)))
    return blocks


def _substantive_callout(body: str) -> bool:
    plain = _plain(body)
    if len(plain) < 18 or any(pattern.search(plain) for pattern in GENERIC_CALLOUT_PATTERNS):
        return False
    return bool(re.search(r"第\s*\d+\s*条", plain)) or (
        bool(COLOR_ANCHOR_PATTERN.search(body)) and bool(RELATION_CUE_PATTERN.search(plain))
    )


def validate_semantic_structure(
    lines: list[str],
    start_line: int,
    *,
    medium_complexity: bool,
    complex_reasoning: bool,
) -> list[SemanticStructureFinding]:
    findings: list[SemanticStructureFinding] = []
    prose = _prose_outside_fences(lines)
    mermaid_blocks = _fenced_blocks(lines, "mermaid")
    substantive_mermaid_count = 0
    for offset, body in mermaid_blocks:
        labels = _mermaid_labels(body)
        grounded_labels = {label for label in labels if label in prose}
        if len(grounded_labels) < 3:
            findings.append(SemanticStructureFinding(
                "639",
                start_line + offset,
                "Mermaid must diagram at least three legal facts, rules, conditions, procedures, or effects that also appear in the prose; option letters and correct/exclude labels are not analysis.",
            ))
        else:
            substantive_mermaid_count += 1

    callouts = _callout_blocks(lines)
    substantive_callouts = 0
    for offset, body in callouts:
        if _substantive_callout(body):
            substantive_callouts += 1
        else:
            findings.append(SemanticStructureFinding(
                "643",
                start_line + offset,
                "Callout must carry a source-grounded rule, condition, exception, procedure, or legal effect; generic review advice and answer restatements do not count.",
            ))
    if medium_complexity and not substantive_callouts:
        findings.append(SemanticStructureFinding(
            "640",
            start_line,
            "Medium-or-higher complexity analysis needs a substantive Callout integrated at the reasoning point it supports.",
        ))
    if complex_reasoning and not substantive_mermaid_count:
        findings.append(SemanticStructureFinding(
            "645",
            start_line,
            "Complex reasoning requires a substantive Mermaid that exposes the actual legal reasoning chain.",
        ))

    option_heading_offset: int | None = None
    in_fence = False
    for offset, line in enumerate(lines):
        if FENCE_PATTERN.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        stripped = line.strip()
        if OPTION_ANALYSIS_HEADING_PATTERN.match(stripped):
            option_heading_offset = offset
        elif option_heading_offset is not None and DEFERRED_REASONING_HEADING_PATTERN.match(stripped):
            findings.append(SemanticStructureFinding(
                "644",
                start_line + offset,
                "Do not defer option reasons to a later comprehensive-reasoning section; put each reason beside its option or integrate the option conclusion into the rule map.",
            ))

        match = LIST_ITEM_PATTERN.match(line)
        if not match:
            continue
        body = _plain(match.group("body"))
        if OPTION_REPLAY_PATTERN.match(body):
            continue
        if MECHANICAL_LABEL_PATTERN.fullmatch(body):
            findings.append(SemanticStructureFinding(
                "642",
                start_line + offset,
                "Replace numbered reasoning-shell labels with a content label naming the governing subject, condition, stage, exception, or effect.",
            ))
        if re.search(r"[,，、]\s*$", match.group("body")):
            findings.append(SemanticStructureFinding(
                "641",
                start_line + offset,
                "A list item ends as a punctuation fragment; regroup by a complete legal meaning instead of splitting at punctuation.",
            ))
    return findings
