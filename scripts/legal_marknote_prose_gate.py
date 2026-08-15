#!/usr/bin/env python3
"""Detect mechanically fragmented MarkNote prose and dangling color anchors."""

from __future__ import annotations

import re
from dataclasses import dataclass


INLINE_IAL_PATTERN = re.compile(r"\{:\s*[^}\n]*\}")
HTML_TAG_PATTERN = re.compile(r"</?[^>]+>")
TERMINAL_PATTERN = re.compile(r"[。！？；.!?;][\"'”’）》】\]]*$")
CONTINUATION_PATTERN = re.compile(r"[，、：,,:]$")
DANGLING_COLOR_ANCHOR_PATTERN = re.compile(
    r'[。！？；.!?;]\s*\*\*[^*\n]+\*\*\{:\s*style="[^"]*b3-font-(?:color|background)\d+[^"]*"\}\s*$'
)
STRUCTURAL_PATTERN = re.compile(
    r"^(?:#{1,6}\s+|[-+*]\s+|\d+[.)]\s+|\|.*\|\s*$|\{:\s*.+\}\s*$|"
    r"-{3,}\s*$|!\[[^]]*\]\([^)]+\)\s*$|</?(?:div|table|thead|tbody|tr|td|th|style|svg)\b)",
    re.IGNORECASE,
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


def _has_fragment_boundary(previous: str) -> bool:
    return bool(CONTINUATION_PATTERN.search(previous)) or not TERMINAL_PATTERN.search(previous)


def validate_marknote_prose_structure(text: str) -> tuple[ProseGateFinding, ...]:
    findings: list[ProseGateFinding] = []
    lines = text.splitlines()
    run: list[tuple[int, str]] = []
    run_quote_depth: int | None = None
    in_fence = False
    frontmatter_end = (
        next((index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---"), None)
        if lines and lines[0].strip() == "---"
        else None
    )

    def flush() -> None:
        nonlocal run, run_quote_depth
        found_fragment = False
        for (number, previous), (_, _) in zip(run, run[1:]):
            if _has_fragment_boundary(previous):
                findings.append(
                    ProseGateFinding(
                        "W",
                        "505",
                        number,
                        "Plain line breaks do not create semantic structure; merge one inseparable sentence or convert independent parts into a Markdown parent/child list.",
                    )
                )
                found_fragment = True
                break
        if not found_fragment and run and re.search(r"[，、,]$", run[-1][1]):
            findings.append(
                ProseGateFinding(
                    "W",
                    "505",
                    run[-1][0],
                    "A standalone prose fragment ends with continuation punctuation; complete it on one line or attach semantic list children.",
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
            continue

        quote_depth, content = _unwrap_quote(line)
        content = content.strip()
        if not content:
            flush()
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
        if content.startswith("[!") or STRUCTURAL_PATTERN.match(content):
            flush()
            continue
        if run_quote_depth is not None and quote_depth != run_quote_depth:
            flush()
        run_quote_depth = quote_depth
        run.append((number, _plain_text(content)))

    flush()
    return tuple(findings)
