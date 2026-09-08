"""引述块碎片化门禁（fragmented quote blocks）。

一段连续内容只允许占一个引述块：块内行保持 ``> `` 连续，内部分段写空的
``>`` 行。把同一段连续内容用空行拆成多个引述块，在思源里会渲染成几个互不
相连的引用框，属于碎片化缺陷。命中两种信号：

1. 句中断裂：前一个引述块末行以逗号/顿号/分号/冒号等延续标记收尾，紧接着
   空行后又是另一个引述块——同一句话被切开；
2. 结构串联：三个及以上无 Callout 指令的普通引述块仅被空行串联——同一段
   连续内容被拆成一串单块。

不同性质、不同来源、不同 Callout 类型的独立引述保持空行分立是允许的。

返回 (行号, 消息) 二元组列表，由各技能校验器包装成自己的 Finding。
"""

from __future__ import annotations

import re

QUOTE_LINE_RE = re.compile(r"^\s*>($|\s)")
FENCE_RE = re.compile(r"^(?:\s*>\s*)?```")
CALLOUT_DIRECTIVE_RE = re.compile(r"^\s*>\s*\[!")
IAL_TAIL_RE = re.compile(r"\{:\s*[^}]*\}\s*$")
CONTINUATION_TAIL_RE = re.compile(r"[,，、；：:;,]\s*$")

_TAIL_MESSAGE = (
    "引述块碎片化：前一个引述块末行以延续标记（逗号/顿号/分号/冒号）收尾，"
    "同一句连续内容被空行切成两个引述块，思源里会渲染成两个断开的引用框。"
    "合并为一个引述块——块内行保持 > 连续、内部分段写空的 > 行——或改写成普通正文/列表。"
)
_STREAK_MESSAGE = (
    "引述块碎片化：多个引述块仅被空行串联成同一段连续内容，一段话只允许占一个引述块。"
    "合并为一个引述块——块内行保持 > 连续、内部分段写空的 > 行——"
    "只有真正独立（不同来源、不同 Callout 类型）的引述才允许空行分立。"
)


def _quote_content(line: str) -> str:
    body = re.sub(r"^\s*>\s?", "", line)
    body = IAL_TAIL_RE.sub("", body)
    return body.strip()


def _run_tail_content(run_lines: list[str]) -> str:
    for line in reversed(run_lines):
        content = _quote_content(line)
        if content:
            return content
    return ""


def find_fragmented_quote_blocks(text: str) -> list[tuple[int, str]]:
    """Return (1-based line number, message) pairs for fragmented quote chains."""
    lines = text.splitlines()
    runs: list[tuple[int, int, list[str], bool]] = []
    current_lines: list[str] = []
    current_start = 0
    current_has_directive = False
    in_fence = False

    def close_run(end_index: int) -> None:
        nonlocal current_lines, current_start, current_has_directive
        if current_lines:
            runs.append((current_start, end_index, current_lines, current_has_directive))
        current_lines = []
        current_has_directive = False

    for index, line in enumerate(lines):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            close_run(index - 1)
            continue
        if in_fence:
            continue
        if QUOTE_LINE_RE.match(line):
            if not current_lines:
                current_start = index
                current_lines = [line]
            else:
                current_lines.append(line)
            if CALLOUT_DIRECTIVE_RE.match(line):
                current_has_directive = True
        else:
            close_run(index - 1)
    close_run(len(lines) - 1)

    def gap_all_blank(prev_end: int, next_start: int) -> bool:
        return all(not lines[index].strip() for index in range(prev_end + 1, next_start))

    findings: list[tuple[int, str]] = []
    plain_streak = 0
    for position in range(len(runs) - 1):
        prev_start, prev_end, prev_body, prev_directive = runs[position]
        next_start, _, _, next_directive = runs[position + 1]
        if not gap_all_blank(prev_end, next_start):
            plain_streak = 0
            continue
        tail = _run_tail_content(prev_body)
        if tail and CONTINUATION_TAIL_RE.search(tail):
            findings.append((next_start + 1, _TAIL_MESSAGE))
        if not prev_directive and not next_directive:
            plain_streak += 1
            if plain_streak == 2:
                findings.append((next_start + 1, _STREAK_MESSAGE))
        else:
            plain_streak = 0
    return findings
