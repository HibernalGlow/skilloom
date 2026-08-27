#!/usr/bin/env python3
"""Validate option-by-option GoldQuest analysis against the question text."""

from __future__ import annotations

import re
from dataclasses import dataclass


QUESTION_OPTION_PATTERN = re.compile(
    r"^\s*[-*+]\s*\[\s*[xX]?\s*\]\s*(?:\*\*)?"
    r"(?:(?P<label>[A-Z])(?:[.．、)）]|\s*项)|[（(](?P<bracket_label>[A-Z])[)）])"
    r"(?:\*\*)?\s*(?P<body>.+?)\s*$"
)
ANALYSIS_OPTION_PATTERN = re.compile(
    r"^(?P<indent>\s*)(?:[-*+]|\d+[.)])\s+(?P<emoji>[✅❌])?\s*(?:\*\*)?"
    r"(?:(?P<label>[A-Z])(?:[.．、)）]|\s*项)|[（(](?P<bracket_label>[A-Z])[)）])"
    r"(?:\*\*)?\s*[：:]?\s*(?P<body>.+?)\s*$"
)
OPTION_REFERENCE_PATTERN = re.compile(
    r"(?<![A-Z])(?:选项\s*(?P<prefix_label>[A-Z])|(?P<suffix_label>[A-Z])\s*(?:项|选项))"
)
INLINE_IAL_PATTERN = re.compile(r"\{:\s*[^}\n]*\}")
HTML_EMPHASIS_PATTERN = re.compile(r"</?(?:u|em|strong|span)\b[^>]*>", re.IGNORECASE)
LOCAL_CUE_PATTERNS = (
    re.compile(r"~~\S(?:.*?\S)?~~"),
    re.compile(r"==\S(?:.*?\S)?=="),
    re.compile(r"<u(?:\s+[^>]*)?>\S(?:.*?\S)?</u>", re.IGNORECASE),
    re.compile(r'\*\*[^*\n]+\*\*\{:\s*style="[^"]*b3-font-(?:color|background)\d+'),
)
CHILD_REASON_PATTERN = re.compile(r"^(?P<indent>\s*)(?:[-*+]|\d+[.)])\s+(?P<body>\S.+?)\s*$")
DEFERRED_REASON_PATTERN = re.compile(r"下文|后文|综合推理|完整推理|推理过程")
VERDICT_BOILERPLATE_PATTERN = re.compile(
    r"(?:破绽|依据|破题点|理由|结论|故|因此|所以|综上所述|选项|本项|该项|说法|"
    r"[A-ZＡ-Ｚ]项?|应当|应|正确答案|答案|正确|错误|排除|当选|不当选|选|不选|为|是|均|项|"
    r"[A-ZＡ-Ｚ]+)+"
)


@dataclass(frozen=True)
class OptionGateFinding:
    code: str
    line: int
    message: str


@dataclass(frozen=True)
class OptionGateResult:
    findings: tuple[OptionGateFinding, ...]
    replay_lines: frozenset[int]


def _label(match: re.Match[str]) -> str:
    return (match.groupdict().get("label") or match.groupdict().get("bracket_label") or "").upper()


def _normalize_option_text(value: str) -> str:
    value = INLINE_IAL_PATTERN.sub("", value)
    value = HTML_EMPHASIS_PATTERN.sub("", value)
    value = re.sub(r"\\([\\`*_{}\[\]()#+\-.!])", r"\1", value)
    for marker in ("**", "__", "~~", "==", "`"):
        value = value.replace(marker, "")
    return re.sub(r"\s+", "", value)


def _has_local_cue(body: str) -> bool:
    return any(pattern.search(body) for pattern in LOCAL_CUE_PATTERNS)


STRIKE_SPAN_RE = re.compile(r"~~([^~]+)~~")


def _whole_option_strike(body: str) -> bool:
    """True when a strike span covers almost the whole option body."""
    plain = _normalize_option_text(body)
    if len(plain) < 8:
        return False
    struck = "".join(_normalize_option_text(part) for part in STRIKE_SPAN_RE.findall(body))
    return len(struck) / len(plain) >= 0.9


def _has_immediate_reason(lines: list[str], offset: int, option_indent: str) -> bool:
    base_indent = len(option_indent.expandtabs(4))
    for candidate in lines[offset + 1:]:
        if not candidate.strip() or INLINE_IAL_PATTERN.fullmatch(candidate.strip()):
            continue
        match = CHILD_REASON_PATTERN.match(candidate)
        if not match or len(match.group("indent").expandtabs(4)) < base_indent + 4:
            return False
        reason = _normalize_option_text(match.group("body"))
        if not reason or DEFERRED_REASON_PATTERN.search(reason):
            return False
        substantive = VERDICT_BOILERPLATE_PATTERN.sub("", reason)
        return len(substantive) >= 4
    return False


def validate_option_analysis(
    question_lines: list[str],
    analysis_lines: list[str],
    analysis_start_line: int,
    answer_value: str,
) -> OptionGateResult:
    """Return structural findings and physical lines that replay original options."""
    originals: dict[str, str] = {}
    for line in question_lines:
        match = QUESTION_OPTION_PATTERN.match(line)
        if match:
            originals[_label(match)] = _normalize_option_text(match.group("body"))
    if not originals:
        return OptionGateResult((), frozenset())

    findings: list[OptionGateFinding] = []
    replay_lines: set[int] = set()
    formal_labels: set[str] = set()
    answer_labels = set(re.findall(r"(?<![A-Z])[A-Z](?![A-Z])", answer_value.upper()))
    in_fence = False

    for offset, line in enumerate(analysis_lines):
        stripped = line.strip()
        if stripped.startswith(("```", "> ```")):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = ANALYSIS_OPTION_PATTERN.match(line)
        if not match:
            continue

        number = analysis_start_line + offset
        label = _label(match)
        formal_labels.add(label)
        replay_lines.add(number)
        if label not in originals or _normalize_option_text(match.group("body")) != originals[label]:
            findings.append(
                OptionGateFinding(
                    "630",
                    number,
                    f"Option {label} analysis must replay the complete original option text; summaries and partial quotes are not sufficient.",
                )
            )

        cue_problems: list[str] = []
        if answer_labels:
            expected_emoji = "✅" if label in answer_labels else "❌"
            if match.group("emoji") != expected_emoji:
                cue_problems.append(f"use {expected_emoji} to match custom-qb-answer")
        elif match.group("emoji") not in {"✅", "❌"}:
            cue_problems.append("add a decision emoji after custom-qb-answer is supplied")
        body = match.group("body")
        wrong_option = match.group("emoji") == "❌" or (answer_labels and label not in answer_labels)
        if wrong_option and not STRIKE_SPAN_RE.search(body):
            cue_problems.append("mark the wrong part with a strikethrough fragment inside the original option text (colors alone do not show where it is wrong)")
        if not _has_local_cue(body):
            cue_problems.append("place strikethrough, highlight, color, or underline inside the original option text")
        if cue_problems:
            findings.append(OptionGateFinding("631", number, "Option cue is incomplete: " + "; ".join(cue_problems) + "."))
        if _whole_option_strike(body):
            findings.append(OptionGateFinding("646", number, "Do not strikethrough the whole option; strike only the decisive flawed fragment — the swapped subject, condition, degree, time, or legal effect."))
        if not _has_immediate_reason(analysis_lines, offset, match.group("indent")):
            findings.append(OptionGateFinding("632", number, "A marked option needs an immediately following indented reason item."))

    reported_references: set[tuple[int, str]] = set()
    in_fence = False
    for offset, line in enumerate(analysis_lines):
        if line.strip().startswith(("```", "> ```")):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if ANALYSIS_OPTION_PATTERN.match(line):
            continue
        for match in OPTION_REFERENCE_PATTERN.finditer(line):
            label = (match.group("prefix_label") or match.group("suffix_label")).upper()
            key = (offset, label)
            if label in originals and label not in formal_labels and key not in reported_references:
                reported_references.add(key)
                findings.append(
                    OptionGateFinding(
                        "630",
                        analysis_start_line + offset,
                        f"Option {label} is analyzed without a complete original-option replay line.",
                    )
                )

    return OptionGateResult(tuple(findings), frozenset(replay_lines))
