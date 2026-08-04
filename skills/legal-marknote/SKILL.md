---
name: legal-marknote
description: Convert legal study material into structured SiYuan Markdown while preserving legal substance, tables, images, and explanations. Repair clearly misrecognized headings, broken heading fragments, and semantic heading nesting; add equivalent, easier-to-review Markdown summaries below unwieldy memorization-sheet tables without replacing them. Also use for targeted repairs to text produced by an earlier legal-marknote version.
---

# Legal Marknote

Use this skill when法考教材、题目、解析或笔记需要整理成可复习的思源笔记。

## Workflow

1. Preserve legal substance, wording, tables, images, statutory text, explanations, and the intended hierarchy. Preserve title wording and order, but repair a title marker or title level when the source has clearly misrecognized the structure. Retain every source table as a table; when one unwieldy table contains two or more independent category groups, split it at category boundaries into smaller sibling tables without losing any group, row, column cue, qualification, or legal effect. Add an equivalent list or Callout summary below the retained or split tables when it improves review.
2. Run a heading-repair pass before formatting body content. Treat every source heading marker as a candidate, then keep, merge, demote, or convert it only from its role in the surrounding structure. Follow the decision rules in [the detailed guide](references/note-guide-original.md#标题识别与修复).
3. Separate source content from added summaries or study prompts.
4. Break long prose at semantic boundaries: a definition or explanation introduced by words such as “是” may begin a child list even without punctuation. Decide child lists from semantic independence, not labels or punctuation: split parallel branches that each retain their own applicable situation, object, judgment, or legal effect; keep the prerequisites, procedure, and consequence of one inseparable rule in one item. Use indentation only for containment or progression, then dedent when that relationship ends.
5. Plan semantic colors before writing the final Markdown.
6. Apply the active-coverage, density, boundary, and callout rules in [the detailed guide](references/note-guide-original.md).
7. Actively split long table-cell text at semantic boundaries. In the retained table, use short cue text and `<br />` to separate independently reviewable branches; in the supplementary summary below an unwieldy table, render the same branches as nested Markdown lists. Keep one inseparable prerequisite-to-procedure-to-consequence rule in one item. Apply the large-table supplementary-summary rules in [the detailed guide](references/note-guide-original.md#超大表格的补充摘要) after retaining an unwieldy table.
8. Run `python -X utf8 scripts/validate_output.py <output.md> --strict`. When the original material is available as a file or snapshot, add `--source <source.md> --require-source` to gate title wording, images, tables, and SiYuan merge attributes.
9. Fix every reported error and review every advisory. Then manually confirm legal accuracy, source completeness, repaired hierarchy, semantic color choices, and whether each Callout category is substantively justified; syntax checks cannot decide those legal judgments.

## Legacy Output Revision

When the user states that a text was already processed by an earlier `legal-marknote` version and asks only for corrections, use [the revision-only guide](references/legacy-output-revision.md). Do not rerun the full workflow or load `references/note-guide-original.md` by default; inspect only the affected fragment and its local context, then preserve every unrelated part of the existing output.

## Accuracy

- Never replace a legal rule with an unsupported paraphrase.
- Keep answer bases and explanations attached to the material they justify.
- Use highlights and colors as retrieval cues, not decoration.
- Mark uncertain or incomplete source material for review.

The reference guide contains the complete formatting contract, color syntax, templates, and examples.
