#!/usr/bin/env python3
"""GoldQuest question gates split out of validate_output.py.

Question structure, generated-label, reasoning-integrity, and
source-preservation checks live here so an agent debugging one error code
reads this file instead of the whole shared validator; validate_output
re-exports the public gates through lazy wrappers.
"""

from __future__ import annotations

import re
from collections import Counter

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_output import (  # noqa: E402
    ANSWER_STATUS_TERMS,
    COLORED_TERM_PATTERN,
    COLOR_ATTRIBUTE_PATTERN,
    COMMON_SUBJECT_TERMS,
    COMMON_SURNAME_INITIALS,
    EMOJI_PATTERN,
    Finding,
    GENERATED_LABEL_PREFIX_PATTERN,
    HIGHLIGHT_PATTERN,
    IAL_PATTERN,
    IMAGE_PATTERN,
    LEGACY_ANSWER_MASK_PATTERN,
    LIST_ITEM_VISIBLE_LIMIT,
    MERGE_TOKEN_PATTERN,
    QUESTION_HEADING_PATTERN,
    STATUS_COLORS,
    STYLED_TERM_PATTERN,
    TABLE_ROW_PATTERN,
    VISIBLE_ANSWER_LINE_PATTERN,
    _list_item_visible_length,
    has_semantic_emoji_cue,
    ial_attributes,
    line_for_offset,
    prose_visible_length,
    prose_without_fenced_blocks,
    style_families,
    table_block_content_is_preserved_as_axis_list,
    table_block_content_is_preserved_as_label_rule_list,
    table_block_content_is_preserved_in_tables,
    table_block_has_large_list,
    table_block_is_simple_label_rule,
    table_blocks,
    table_cell_content_is_preserved,
    visible_length,
)
from legal_goldquest_option_gate import validate_option_analysis  # noqa: E402
from legal_goldquest_semantic_structure_gate import (  # noqa: E402
    validate_semantic_structure,
    visual_families,
)


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
    provider_indices = [
        index
        for index, line in enumerate(lines)
        if "custom-qb-note-topic-id" in ial_attributes(line)
    ]
    summary_indices = [
        index
        for index, line in enumerate(lines)
        if re.match(r"^##\s+📌\s*考点必背\s*$", line)
    ]
    if len(h5_indices) >= 2 and provider_indices:
        first_question = h5_indices[0]
        root_provider = next((index for index in provider_indices if index < first_question), None)
        if root_provider is not None:
            root_h1 = next((line for line in lines[:root_provider] if re.match(r"^#\s+", line)), "")
            if not re.match(r"^#\s+\d+\s+\S", root_h1):
                findings.append(Finding("W", "638", 1, "Multi-question GoldQuest topic H1 should start with a sortable Arabic-number prefix, for example '# 06 专题六 共同诉讼'."))
            if not summary_indices:
                findings.append(Finding("E", "634", first_question + 1, "Multi-question GoldQuest topic documents require '## 📌 考点必背' before the first question."))
            else:
                if len(summary_indices) > 1:
                    findings.append(Finding("E", "637", summary_indices[1] + 1, "GoldQuest topic documents must contain exactly one '## 📌 考点必背' section."))
                summary_index = summary_indices[0]
                if not root_provider < summary_index < first_question:
                    findings.append(Finding("E", "635", summary_index + 1, "'## 📌 考点必背' must follow the root provider IAL and precede the first H5 question."))
                else:
                    summary_text = "\n".join(lines[summary_index + 1:first_question])
                    forbidden_summary_fields = re.findall(
                        r"custom-(?:qb-(?:id|answer|section|question-topic-ids)|dm-[\w-]+|riff-[\w-]+)",
                        summary_text,
                    )
                    if forbidden_summary_fields:
                        fields = sorted(set(forbidden_summary_fields))
                        findings.append(Finding("E", "636", summary_index + 1, f"Topic summary must remain navigation prose and cannot contain question, answer, flashcard, or runtime fields: {fields}."))
                    spoiler_hits = [
                        match.group(0)
                        for pattern in (r"本题(?!组)", r"第\s*[\d０-９]+\s*题", r"[上下]一?题")
                        for match in re.finditer(pattern, summary_text)
                    ]
                    if spoiler_hits:
                        hits = sorted(set(spoiler_hits))
                        findings.append(Finding("E", "813", summary_index + 1, f"Topic summary must not label specific questions; remove question pointers such as {hits}."))
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
                if prefix:
                    findings.append(Finding("E", "628", relative_index, "A numbered GoldQuest subquestion must start its own list line, separate from the shared stem (no 题干：/问题： labels)."))
        if sum(len(markers) for _, _, markers in parenthesized_subquestions) >= 2:
            stem_lines = [
                line
                for line in question_lines
                if line.strip()
                and not IAL_PATTERN.fullmatch(line.strip())
                and not re.search(r"-\s*\[[ xX]\]", line)
                and not re.search(r"[（(]\s*\d+\s*[）)]", line)
            ]
            if not stem_lines:
                findings.append(Finding("E", "629", index + 1, "Multi-part GoldQuest questions need a shared stem line before the one-line numbered subquestions; 题干：/问题： labels are forbidden."))
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
            if _list_item_visible_length(line) > LIST_ITEM_VISIBLE_LIMIT and number not in option_gate.replay_lines:
                findings.append(Finding("E", "648", number, "Analysis list items must stay within 20 visible characters; split the content semantically into a governing parent and child items (main and nested items both; the verbatim option replay is exempt)."))
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
        complex_reasoning = analysis_length >= 320 or branch_count >= 6 or analysis_sentence_count >= 8
        semantic_findings = validate_semantic_structure(answer_lines, analysis_start + 1, medium_complexity=medium_complexity, complex_reasoning=complex_reasoning)
        findings.extend(Finding("E", item.code, item.line, item.message) for item in semantic_findings)
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
        if medium_complexity and not has_semantic_emoji_cue(analysis_text, exclude_decision_options=True):
            findings.append(Finding("E", "509", analysis_start + 1, "Medium-or-higher complexity analysis needs at least one semantic emoji cue outside decision-option lines; its position follows the labeled legal relationship."))
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


SOURCE_QUESTION_LINE_RE = re.compile(r"^(?:#{0,6}\s*)?(\d{1,3})\.")
SOURCE_OPTION_LINE_RE = re.compile(r"(?m)^[A-D][\.、．:：]")
SOURCE_SECTION_RE = re.compile(r"^#{3,4}\s+考点\s*\d+")
SOURCE_BOILERPLATE_RE = re.compile(r"解题思路|题支逐项解析|题干信息解读|命题陷阱|总结与归纳|关键词为|本题考点|综上所述|正确答案|说法(?:错误|正确)|当选|有体系|框架图|图片|图片来源")
GOLDQUEST_GENERIC_PROMPT_RE = re.compile(r"下列(?:说法|哪一|表述)|据此可知|对此,?下列")
SOURCE_PUNCT = str.maketrans({"：": ":", "，": ",", "。": ".", "；": ";", "（": "(", "）": ")", "“": '"', "”": '"', "、": ",", "《": "<", "》": ">"})


def _source_plain(value: str) -> str:
    value = re.sub(r"\{:\s*[^}\n]+\}", "", value)
    value = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", value)
    value = re.sub(r"`", "", value)
    value = re.sub(r"[*_=~<>]", "", value)
    value = re.sub(r"(?m)^>\s*", "", value)
    value = re.sub(r"(?m)^#{1,6}\s+", "", value)
    value = re.sub(r"(?m)^\s*(?:[-+*]|\d+[.)])\s+", "", value)
    value = re.sub(r"\[[ xX]\]\s*", "", value)
    value = re.sub(r"\s+", "", value)
    return value.translate(SOURCE_PUNCT)


def _goldquest_source_sections(source_text: str) -> dict[str, str]:
    """Split the source into knowledge-point sections (考点 headings).

    Section numbers restart across chapters, so every 考点 heading is its own
    scope; a source without 考点 headings stays one section. Comparison must
    stay inside one knowledge-point scope instead of crossing ranges.
    """
    lines = source_text.splitlines()
    sections: dict[str, str] = {}
    current = None
    buffer: list[str] = []
    for line in lines:
        if SOURCE_SECTION_RE.match(line):
            if current is not None:
                sections[current] = "\n".join(buffer)
            current = line.strip()
            buffer = [line]
        elif current is not None:
            buffer.append(line)
    if current is not None:
        sections[current] = "\n".join(buffer)
    return sections or {"<source>": source_text}


def _goldquest_source_questions(section_text: str) -> dict[str, list[str]]:
    lines = section_text.splitlines()
    starts: list[tuple[int, str]] = []
    for index, line in enumerate(lines):
        match = SOURCE_QUESTION_LINE_RE.match(line.strip())
        if match:
            starts.append((index, match.group(1)))
    segments: dict[str, list[str]] = {}
    for position, (index, number) in enumerate(starts):
        end = starts[position + 1][0] if position + 1 < len(starts) else len(lines)
        segment = "\n".join(lines[index:end])
        if SOURCE_OPTION_LINE_RE.search(segment):
            segments.setdefault(number, []).append(segment)
    return segments


def _goldquest_source_stem(segment: str) -> str:
    for line in segment.splitlines():
        plain = _source_plain(line)
        if len(plain) >= 16:
            prompt = GOLDQUEST_GENERIC_PROMPT_RE.search(plain)
            if prompt and prompt.start() >= 12:
                plain = plain[:prompt.start()]
            return plain
    return ""


def _goldquest_traceable(value: str, plain_output: str, window: int = 12) -> bool:
    plain = _source_plain(value)
    if len(plain) < window:
        return True
    return any(plain[index:index + window] in plain_output for index in range(len(plain) - window + 1))


GOLDQUEST_MAP_HEADING_RE = re.compile(r"^######\s+(?:规则地图|知识地图|考点地图|知识要点|争点|规则与法源|事实涵摄|命题思路)")


def validate_goldquest_knowledge_placement(text: str) -> list[Finding]:
    """Keep knowledge inside the per-option analysis instead of restating it.

    - `E816`: a fixed 规则地图-style knowledge section splits the knowledge
      from the per-option analysis — the complete knowledge belongs inside
      each option's analysis, Mermaid being the only separate exposition, and
      the skill forbids disguised fixed templates.
    - `E817`: a Callout body near-verbatim repeats the question's own text; a
      Callout must add new value (statute text, trap, boundary, memory link).
    """
    findings: list[Finding] = []
    for number, line in enumerate(text.splitlines(), start=1):
        if GOLDQUEST_MAP_HEADING_RE.match(line):
            findings.append(Finding("E", "816", number, "A fixed 规则地图-style knowledge section splits knowledge from the per-option analysis. Migration is mandatory before any removal: first merge EVERY rule, element, legal effect, and application in this section into the corresponding option analysis, then drop the section; a rule that fits no option stays as a NOTE Callout or a Mermaid node. Never delete the section wholesale without migrating its content — the knowledge inside it is required, not optional."))
    blocks: list[list[str]] = []
    current: list[str] = []
    for line in text.splitlines():
        if re.match(r"^#####\s+(?!#)", line):
            if current:
                blocks.append(current)
            current = [line]
        else:
            current.append(line)
    if current:
        blocks.append(current)
    for block in blocks:
        analysis_region: list[str] = []
        started = False
        in_fence = False
        for line in block:
            if re.match(r"^######\s+答案与解析", line):
                started = True
                continue
            if not started:
                continue
            if re.match(r"^(?:\s*>\s*)?```", line):
                in_fence = not in_fence
                continue
            if in_fence or re.match(r"^#{2,6}\s+", line) or line.lstrip().startswith("{:"):
                continue
            analysis_region.append(line)
        first_replay = next(
            (index for index, line in enumerate(analysis_region) if re.match(r"^[-*]\s+[❌✅]\s*[A-D]", line)),
            None,
        )
        if first_replay is None:
            continue
        separated = False
        for index in range(first_replay):
            line = analysis_region[index]
            if re.match(r"^[-*]\s+(?!正确答案)", line) and not re.match(r"^[-*]\s+[❌✅]", line):
                cursor = index + 1
                while cursor < len(analysis_region) and not analysis_region[cursor].strip():
                    cursor += 1
                if cursor < len(analysis_region) and re.match(r"^\s{2,}(?:[-*]|\d+\.)\s+\S", analysis_region[cursor]):
                    base = len(line) - len(line.lstrip())
                    if len(analysis_region[cursor]) - len(analysis_region[cursor].lstrip()) > base:
                        separated = True
                        break
        if separated:
            findings.append(Finding("E", "816", 1, "The analysis opens with a knowledge block (a bold parent with children) before the per-option replays; put the complete knowledge directly inside each option's analysis — Mermaid is the only separate exposition."))
        callout_sections: list[list[str]] = []
        other_lines: list[str] = []
        in_fence = False
        index = 0
        while index < len(block):
            line = block[index]
            if re.match(r"^(?:\s*>\s*)?```", line):
                in_fence = not in_fence
                index += 1
                continue
            if in_fence:
                index += 1
                continue
            if re.match(r"^\s*>\s+\[![A-Z]+\]", line):
                section = [line]
                index += 1
                while index < len(block) and re.match(r"^\s*>", block[index]):
                    section.append(block[index])
                    index += 1
                callout_sections.append(section)
                continue
            other_lines.append(line)
            index += 1
        other_plain = _source_plain("\n".join(other_lines))
        for callout_section in callout_sections:
            callout_plain = _source_plain("\n".join(callout_section))
            if not other_plain or len(callout_plain) < 15:
                continue
            callout_indexes = {block.index(line) for line in callout_section}
            rest_lines = [line for position, line in enumerate(block) if position not in callout_indexes]
            rest_plain = _source_plain("\n".join(rest_lines))
            grams = {callout_plain[pos:pos + 6] for pos in range(0, len(callout_plain) - 5)}
            hits = sum(1 for gram in grams if gram in rest_plain)
            if len(grams) and hits / len(grams) >= 0.6:
                findings.append(Finding("E", "817", 1, "A Callout body mostly repeats the analysis text; the Callout must add new value (statute text, trap, boundary, memory link) instead of restating what the per-option analysis already covers."))
                break
    return findings


def validate_goldquest_source_content(text: str, source_text: str) -> list[Finding]:
    """Compare an organized GoldQuest document against the original source file.

    The source is split into knowledge-point sections first so that per-考点
    outputs are compared only against the 考点 they cover, never across ranges.
    A section is in scope when the output preserves at least half of its
    questions; any question in an in-scope section whose stem leaves no trace
    is a dropped question and fails `E814`. For in-scope questions that are
    present, source reasoning/statute lines with no trace become a `W815`
    warning so compressed statutes and definitions are reviewed.
    """
    findings: list[Finding] = []
    plain_output = _source_plain(text)
    total_lines = 0
    lost_lines = 0
    missing: list[tuple[str, str, str]] = []
    for section, section_text in _goldquest_source_sections(source_text).items():
        questions = _goldquest_source_questions(section_text)
        if not questions:
            continue
        covered_numbers: set[str] = set()
        section_missing: list[tuple[str, str]] = []
        for number, seg_list in questions.items():
            for segment in seg_list:
                stem = _goldquest_source_stem(segment)
                if stem and _goldquest_traceable(stem, plain_output):
                    covered_numbers.add(number)
                    for line in segment.splitlines():
                        plain = _source_plain(line)
                        if (
                            len(plain) < 12
                            or re.match(r"^#{1,6}\s+", line)
                            or re.match(r"^```", line.strip())
                            or re.match(r"^\|.*\|$", line.strip())
                            or SOURCE_BOILERPLATE_RE.search(plain)
                        ):
                            continue
                        total_lines += 1
                        if not _goldquest_traceable(plain, plain_output, window=6):
                            lost_lines += 1
                else:
                    section_missing.append((number, stem or segment[:40]))
        if covered_numbers and len(covered_numbers) / len(questions) >= 0.5:
            for number, stem in section_missing:
                missing.append((section, number, stem))
    if missing:
        detail = "; ".join(
            f"{section} {number}({stem[:40]})" for section, number, stem in missing[:5]
        )
        findings.append(Finding("E", "814", 1, f"Source questions missing from the organized output within the covered knowledge-point scope: {detail}. Compare against the original file in the same 考点 scope and restore every dropped question with its options and analysis."))
    if total_lines >= 25 and lost_lines / total_lines > 0.55:
        findings.append(Finding("W", "815", 1, f"{lost_lines}/{total_lines} source reasoning or statute lines from covered questions have no trace in the output; restore dropped statutes, definitions, and reasoning steps."))
    return findings


def _line_head_label_prefix(line: str) -> bool:
    """Return whether a line opens with a generated 问题：/题干：/答案：/解析：/问： label,
    tolerating list/quote markers, bold asterisks, digits, and leading emoji so none can mask it."""
    text = EMOJI_PATTERN.sub("", line).replace("*", "")
    text = re.sub(r"^[\s>\-+\d.]+", "", text)
    return bool(GENERATED_LABEL_PREFIX_PATTERN.match(text))


def validate_generated_label_prefixes(text: str) -> list[Finding]:
    """Reject generated 问题：/题干：/答案：/解析：/问： label prefixes at line heads (fences skipped)."""
    findings: list[Finding] = []
    lines = text.splitlines()
    in_fence = False
    for number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if _line_head_label_prefix(line):
            findings.append(Finding("E", "647", number, "Write the stem, question, and analysis directly; no 问题：/题干：/答案：/解析：/问： label prefix is allowed at the head of an output line."))
    return findings


GOLDQUEST_QUESTION_HEADING_RE = re.compile(r"^#####\s+")
GOLDQUEST_SOLUTION_HEADING_RE = re.compile(r"^######\s+答案与解析\s*$")
GOLDQUEST_INLINE_MARKUP_RE = re.compile(
    r"\{:\s*[^}\n]*\}"
    r"|</?(?:u|em|strong|span|mark|sub|sup)\b[^>]*>"
    r"|!\[[^\]]*\]\([^)]*\)"
    r"|`[^`]*`"
    r"|https?://\S+"
)
GOLDQUEST_PLACEHOLDER_TEMPLATE_RE = re.compile(
    r"本题落点清晰|按规则判断|程序与实体效果须分别核对|先看主体再看条件与期限|与本题规则无关"
)
GOLDQUEST_PLACEHOLDER_TOKENS = (
    "与规则不符", "与规则一致", "与规则无关", "与本题无关", "符合规则", "不符合规则",
    "本题落点清晰", "按规则判断", "规则要点", "程序与实体效果须分别核对",
    "先看主体再看条件与期限", "本题结论清晰", "按规则核对", "规则无关",
    "本题", "规则", "正确", "错误", "排除", "当选", "不当选", "符合", "不符",
    "无关", "一致", "落点", "清晰", "判断", "结论", "定案", "破绽", "破题点",
    "主体", "条件", "期限", "程序", "实体", "效果", "核对", "分别", "再看", "先看",
    "须", "看", "为", "是", "的", "了", "中", "在", "与", "和", "及",
)
GOLDQUEST_PUNCTUATION_DEBRIS_RE = re.compile(r"。，|，。|；。|：。|。；|。，，|。。")
GOLDQUEST_TERMINAL_PUNCTUATION = set("。！？；…”』」）》】\"'！？…：:")


def _gq_solution_regions(lines: list[str]) -> list[tuple[int, int]]:
    """Return (start, end) line-index pairs for every question's 答案与解析 region."""
    regions: list[tuple[int, int]] = []
    h5_indices = [i for i, line in enumerate(lines) if GOLDQUEST_QUESTION_HEADING_RE.match(line)]
    for k, start in enumerate(h5_indices):
        end = h5_indices[k + 1] if k + 1 < len(h5_indices) else len(lines)
        heading = next(
            (i for i in range(start + 1, end) if GOLDQUEST_SOLUTION_HEADING_RE.match(lines[i])),
            None,
        )
        if heading is not None:
            regions.append((heading, end))
    return regions


def _gq_plain(value: str) -> str:
    value = GOLDQUEST_INLINE_MARKUP_RE.sub("", value)
    return re.sub(r"[\s#>*`|~=_]+", "", value)


def _gq_is_placeholder_line(value: str) -> bool:
    plain = _gq_plain(value)
    if not plain:
        return False
    if GOLDQUEST_PLACEHOLDER_TEMPLATE_RE.search(plain):
        return True
    remainder = plain
    for token in GOLDQUEST_PLACEHOLDER_TOKENS:
        remainder = remainder.replace(token, "")
    return len(remainder) == 0


def validate_goldquest_reasoning_integrity(text: str) -> list[Finding]:
    """Reject placeholder rationales, truncated solution tails, and punctuation debris.

    These encode the two audited failure archetypes: template placeholder
    solutions that carry no question-specific legal content (E650), and
    source prose mechanically cut into labeled fragments whose tail was
    truncated mid-sentence (E651). Punctuation debris (E652) marks broken
    sentence joining such as '。，'.
    """
    findings: list[Finding] = []
    lines = text.splitlines()
    placeholder_lines: list[int] = []
    in_fence = False
    for number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if GOLDQUEST_PUNCTUATION_DEBRIS_RE.search(line):
            findings.append(Finding("E", "652", number, "Punctuation debris (。，/，。/；。); repair the sentence joining instead of stacking terminal marks."))
        if not stripped or stripped.startswith("|") or re.match(r"^-{3,}$", stripped):
            continue
        if re.match(r"^#{1,6}\s+", stripped) or IAL_PATTERN.match(stripped):
            continue
        if _gq_is_placeholder_line(line):
            placeholder_lines.append(number)
    if placeholder_lines:
        detail = ", ".join(str(n) for n in placeholder_lines[:6])
        findings.append(Finding("E", "650", placeholder_lines[0], f"Placeholder rationale lines carry no question-specific legal content ({detail}); restore the source reasoning — name the rule, elements, and case application instead of '与规则不符/符合规则/按规则判断' shells."))

    for start, end in _gq_solution_regions(lines):
        in_fence = False
        last_prose: tuple[int, str] | None = None
        for i in range(start + 1, end):
            stripped = lines[i].strip()
            if stripped.startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence or not stripped:
                continue
            if stripped.startswith("|") or re.match(r"^-{3,}$", stripped):
                continue
            if re.match(r"^#{1,6}\s+", stripped) or IAL_PATTERN.match(stripped):
                continue
            last_prose = (i, stripped)
        if last_prose is None:
            continue
        number, stripped = last_prose
        plain = _gq_plain(stripped)
        if len(plain) < 10:
            continue
        bare = re.sub(r"^\s*(?:>\s*)?[-+*]\s+", "", stripped).strip()
        if re.search(r"[，、,:]$", bare):
            findings.append(Finding("E", "651", number, "Solution prose ends mid-sentence (truncated source cut); complete the remaining option reasoning or trim to a complete judgment."))
    return findings


GOLDQUEST_SOURCE_REF_RE = re.compile(r"20\d{2}\s*(?:金题)?[-0-9]{3,}")
GOLDQUEST_SOURCE_ANALYSIS_MARKER_RE = re.compile(r"[【\[][^\]】]{1,22}(?:解析|思路|分析|解读)[^\]】]{0,22}[】\]]")
GOLDQUEST_SOURCE_REF_ATTR_RE = re.compile(r"custom-qb-id=\"[^\"]*?(20\d{2}(?:金题)?[-0-9]{3,})")


GOLDQUEST_SOURCE_VOLUME_NOISE_RE = re.compile(
    r"本题(?:综合)?(?:考查|涉及)[^。。；;]{0,60}[。；;]?|综上所述[^。。]{0,20}[。。]?|"
    r"本题(?:的)?答案为?[^。。]{0,12}[。。]?"
)


def _gq_source_analysis_spans(source_text: str) -> dict[str, str]:
    """Map each source question ref to its analysis body (marker to next question ref)."""
    lines = source_text.splitlines()
    occurrences: list[tuple[int, str]] = []
    for li, line in enumerate(lines):
        if line.startswith("|"):
            continue
        for match in GOLDQUEST_SOURCE_REF_RE.finditer(line):
            ref = re.sub(r"[\s金题]", "", match.group(0))
            occurrences.append((li, ref))
    spans: dict[str, tuple[int, int]] = {}
    for k, (li, ref) in enumerate(occurrences):
        if ref in spans:
            continue
        spans[ref] = (li, occurrences[k + 1][0] if k + 1 < len(occurrences) else len(lines))
    bodies: dict[str, str] = {}
    for ref, (a, b) in spans.items():
        segment = "\n".join(lines[a:b])
        cut = re.search(r"本书答案速查|答案速查|答案索引", segment)
        if cut:
            segment = segment[: cut.start()]
        marker = GOLDQUEST_SOURCE_ANALYSIS_MARKER_RE.search(segment)
        body = segment[marker.end():] if marker else segment
        body = GOLDQUEST_SOURCE_VOLUME_NOISE_RE.sub("", body)
        bodies[ref] = body
    return bodies


def validate_goldquest_solution_volume(text: str, source_text: str) -> list[Finding]:
    """Flag solutions that shrink a source analysis below a reviewable floor.

    Paired by the year-patent ref inside custom-qb-id. Sources under 900
    visible characters are skipped (short analyses legitimately condense);
    below 25% with a ≥600-character absolute loss fails E653, below 45%
    warns W851 so strict runs force a conscious restore of dropped
    reasoning steps.
    """
    findings: list[Finding] = []
    source_bodies = _gq_source_analysis_spans(source_text)
    if not source_bodies:
        return findings
    lines = text.splitlines()
    for start, end in _gq_solution_regions(lines):
        question_start = max(
            (i for i in range(start, -1, -1) if GOLDQUEST_QUESTION_HEADING_RE.match(lines[i])),
            default=None,
        )
        if question_start is None:
            continue
        ref_match = None
        for i in range(question_start, start):
            ref_match = GOLDQUEST_SOURCE_REF_ATTR_RE.search(lines[i])
            if ref_match:
                break
        if not ref_match:
            continue
        ref = re.sub(r"金题", "", ref_match.group(1))
        if ref not in source_bodies:
            continue
        source_plain = _gq_plain(source_bodies[ref])
        if len(source_plain) < 900:
            continue
        solution_plain = _gq_plain("\n".join(lines[start:end]))
        solution_plain = re.sub(r"```mermaid.*?```", "", solution_plain)
        ratio = len(solution_plain) / len(source_plain)
        loss = len(source_plain) - len(solution_plain)
        if ratio < 0.25 and loss >= 600:
            findings.append(Finding("E", "653", question_start + 1, f"Solution keeps {len(solution_plain)} of {len(source_plain)} source-analysis characters ({ratio:.0%}); restore the dropped reasoning steps, statutes, and examples beside their options."))
        elif ratio < 0.45:
            findings.append(Finding("W", "851", question_start + 1, f"Solution keeps only {ratio:.0%} of the {len(source_plain)}-character source analysis; verify every reasoning chain survived the condensation or restore the dropped steps."))
    return findings

