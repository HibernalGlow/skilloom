#!/usr/bin/env python3
"""标准列表缩进门禁（CommonMark）。

CommonMark 规则：列表项的内容列 = 标记起始列 + 标记宽度 + 标记后空格数（按 1–4 计）。
子列表必须缩进在 [父项内容列, 父项内容列 + 3] 的窗口内才会被解析为嵌套列表：

- `` `- `` 父项内容列为 2，子列表允许 2–5 列（每级 2 或 4 空格）；
- `` `1. `` 内容列为 3（允许 3–6 列）；`` `10. `` 内容列为 4（允许 4–7 列）；
- tab 按 CommonMark 制表位展开（每 4 列）：1 个 tab = 4 列，2 个 tab = 8 列。

缩进超出窗口上界（如一级 `` `- `` 列表下的子列表缩进 6 列以上、用两个 tab、或跳级缩进）时，
该行不再被解析为子列表：CommonMark 会把它并入父项正文（子列表标记变成字面文本）或解析为
缩进代码块；思源基于 Lute（CommonMark 兼容），同样无法解析出嵌套层级。
顶层（没有打开的父列表项）列表只能缩进 0–3 列，≥4 列会被当作缩进代码块。

实现说明：按 CommonMark 语义做行级栈匹配，tab 先按制表位展开；围栏代码块内部跳过；
列表项后的裸文本续行（lazy continuation）视为关闭该列表项——技能输出本就禁止裸续行，
该近似不会漏报真实违规。窗口语义已用 markdown-it-py（CommonMark 参考级实现）实测核对。
"""

from __future__ import annotations

import re

LIST_MARKER_PATTERN = re.compile(r"^([ ]*)([-*+]|\d{1,9}[.)])([ ]+)(?=\S)")
FENCE_START_PATTERN = re.compile(r"^(`{3,}|~{3,})")

TAB_STOP = 4
MAX_MARKER_GAP = 4


def _content_column(indent: int, marker: str, gap: str) -> int:
    return indent + len(marker) + min(len(gap), MAX_MARKER_GAP)


def _sublist_message(indent: int, floor: int) -> str:
    return (
        f"标准列表缩进违规：本行列表项缩进 {indent} 列，超出父列表项内容列 {floor} 的允许窗口"
        f"（{floor}–{floor + 3} 列）。缩进超窗后 CommonMark 不再把它当作子列表，而是并入父项正文"
        f"（子列表标记变成字面文本）或解析为缩进代码块，嵌套层级丢失，思源无法正确解析。"
        f"修法：子列表按每级 4 空格缩进到父项内容列（`- ` 父项内容列为 2，允许 2–5 列；"
        f"`1. ` 为 3；`10. ` 为 4），禁止用 tab 缩进。"
    )


def _top_level_message(indent: int) -> str:
    return (
        f"标准列表缩进违规：本行列表项缩进 {indent} 列，但当前没有打开的父列表项；顶层列表"
        f"只能缩进 0–3 列，≥4 列会被 CommonMark 解析为缩进代码块而非列表，思源无法解析。"
        f"修法：顶层列表顶格书写；作为子列表时按每级 4 空格缩进到父项内容列（`- ` 父项为 2 列），"
        f"禁止用 tab 缩进。"
    )


def find_overindented_sublists(text: str) -> list[tuple[int, str]]:
    """返回 (行号, 修复提示) 列表；行号从 1 计。"""
    findings: list[tuple[int, str]] = []
    open_items: list[int] = []  # 打开的列表项内容列，由外到内
    fence_char = ""
    fence_len = 0
    for line_no, raw in enumerate(text.splitlines(), start=1):
        expanded = raw.expandtabs(TAB_STOP)
        stripped = expanded.strip()
        if fence_char:
            close = FENCE_START_PATTERN.match(stripped)
            if close and close.group(1)[0] == fence_char and len(close.group(1)) >= fence_len:
                fence_char = ""
            continue
        if not stripped:
            continue
        indent = len(expanded) - len(expanded.lstrip(" "))
        while open_items and open_items[-1] > indent:
            open_items.pop()
        fence = FENCE_START_PATTERN.match(stripped)
        if fence is not None:
            fence_char = fence.group(1)[0]
            fence_len = len(fence.group(1))
            continue
        marker = LIST_MARKER_PATTERN.match(expanded)
        if marker is None:
            continue
        content_column = _content_column(indent, marker.group(2), marker.group(3))
        if open_items:
            floor = open_items[-1]
            if indent >= floor + TAB_STOP:
                findings.append((line_no, _sublist_message(indent, floor)))
        elif indent >= TAB_STOP:
            findings.append((line_no, _top_level_message(indent)))
        open_items.append(content_column)
    return findings
