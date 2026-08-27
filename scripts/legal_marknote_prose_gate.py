#!/usr/bin/env python3
"""Detect mechanically fragmented MarkNote prose and dangling color anchors."""

from __future__ import annotations

import re
from dataclasses import dataclass


INLINE_IAL_PATTERN = re.compile(r"\{:\s*[^}\n]*\}")
HTML_TAG_PATTERN = re.compile(r"</?[^>]+>")
DANGLING_COLOR_ANCHOR_PATTERN = re.compile(
    r'[。！？；.!?;]\s*\*\*[^*\n]+\*\*\{:\s*style="[^"]*b3-font-(?:color|background)\d+[^"]*"\}\s*$'
)
STRUCTURAL_PATTERN = re.compile(
    r"^(?:#{1,6}\s+|[-+*]\s+|\d+[.)]\s+|\|.*\|\s*$|\{:\s*.+\}\s*$|"
    r"-{3,}\s*$|!\[[^]]*\]\([^)]+\)\s*$|</?(?:div|table|thead|tbody|tr|td|th|style|svg)\b)",
    re.IGNORECASE,
)
LIST_ITEM_PATTERN = re.compile(r"^(?P<indent>\s*)(?:[-+*]|\d+[.)])\s+")
INLINE_ENUMERATION_PATTERN = re.compile(
    r"(?<![\w第])(?:\d{1,3}[.)、．]|[（(]\s*\d{1,3}\s*[）)]|[①-⑳])(?=\s*[^\d\s])"
)
LIST_ORDERED_MARKER_START_PATTERN = re.compile(
    r"^(?:(?:\d{1,3})\s*[.)、．]|[（(]\s*\d{1,3}\s*[）)]|[①-⑳])(?=\s*[^\d\s]|\s*$)"
)


@dataclass(frozen=True)
class ProseGateFinding:
    level: str
    code: str
    line: int
    message: str


def _unwrap_quote(line: str) -> tuple[int, str]:
    depth = 0
    content = line.lstrip()
    while content.startswith(">"):
        depth += 1
        content = content[1:].lstrip()
    return depth, content


def _plain_text(value: str) -> str:
    value = INLINE_IAL_PATTERN.sub("", value)
    value = HTML_TAG_PATTERN.sub("", value)
    value = re.sub(r"!\[([^]]*)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"[`*_~=]", "", value)
    return value.strip()


def validate_marknote_prose_structure(text: str) -> tuple[ProseGateFinding, ...]:
    findings: list[ProseGateFinding] = []
    lines = text.splitlines()
    run: list[tuple[int, str]] = []
    run_quote_depth: int | None = None
    pending_list_line: int | None = None
    pending_list_quote_depth: int | None = None
    in_fence = False
    frontmatter_end = (
        next((index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---"), None)
        if lines and lines[0].strip() == "---"
        else None
    )

    def flush() -> None:
        nonlocal run, run_quote_depth
        if len(run) > 1:
            findings.append(
                ProseGateFinding(
                    "W",
                    "505",
                    run[0][0],
                    "Consecutive prose lines are Markdown soft breaks, not semantic structure; use one paragraph, blank-separated paragraphs, or a Markdown parent/child list while preserving every inline Markdown and SiYuan IAL anchor intact.",
                )
            )
        run = []
        run_quote_depth = None

    for number, line in enumerate(lines, start=1):
        if frontmatter_end is not None and number <= frontmatter_end + 1:
            continue
        stripped = line.strip()
        if stripped.startswith(("```", "> ```")):
            flush()
            in_fence = not in_fence
            continue
        if in_fence:
            if INLINE_IAL_PATTERN.search(_unwrap_quote(line)[1]):
                findings.append(
                    ProseGateFinding(
                        "W",
                        "508",
                        number,
                        "A SiYuan IAL appears inside a code fence; keep fenced content to standard Markdown or source text and attach the IAL to a rendered block outside the fence.",
                    )
                )
            continue

        quote_depth, content = _unwrap_quote(line)
        content = content.strip()
        if not content:
            flush()
            pending_list_line = None
            pending_list_quote_depth = None
            continue
        if DANGLING_COLOR_ANCHOR_PATTERN.search(content):
            findings.append(
                ProseGateFinding(
                    "W",
                    "506",
                    number,
                    "A color anchor is dangling after a completed sentence; integrate it into the sentence or remove the decorative duplicate.",
                )
            )
        list_match = LIST_ITEM_PATTERN.match(content)
        if list_match:
            after_marker = content[list_match.end():]
            if LIST_ORDERED_MARKER_START_PATTERN.match(after_marker):
                findings.append(
                    ProseGateFinding(
                        "E",
                        "311",
                        number,
                        "A list item's content begins with an ordered-list marker (1. / 1、 / 1) / （1） / ①); the renderer reads it as a nested ordered list and misrecognizes the structure — drop the marker or write each numbered child as its own indented list line, preserving every inline Markdown and SiYuan IAL anchor intact.",
                    )
                )
            elif INLINE_ENUMERATION_PATTERN.search(after_marker):
                findings.append(
                    ProseGateFinding(
                        "W",
                        "507",
                        number,
                        "A list item contains an inline enumeration; give each child its own indented list line instead of keeping its marker in the parent text, preserving every inline Markdown and SiYuan IAL anchor intact.",
                    )
                )
        if list_match:
            flush()
            pending_list_line = number
            pending_list_quote_depth = quote_depth
            continue
        # A Callout directive is structurally separate from its first body line.
        if content.startswith("[!") or STRUCTURAL_PATTERN.match(content):
            flush()
            pending_list_line = None
            pending_list_quote_depth = None
            continue
        if run_quote_depth is not None and quote_depth != run_quote_depth:
            flush()
        if pending_list_line is not None and quote_depth == pending_list_quote_depth:
            findings.append(
                ProseGateFinding(
                    "W",
                    "505",
                    pending_list_line,
                    "A list item continues as bare text; make the continuation a nested list item or a blank-separated paragraph, preserving every inline Markdown and SiYuan IAL anchor intact.",
                )
            )
        pending_list_line = None
        pending_list_quote_depth = None
        run_quote_depth = quote_depth
        run.append((number, _plain_text(content)))

    flush()
    return tuple(findings)
