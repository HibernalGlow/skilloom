---
name: legal-marknote
description: Convert legal study material into structured SiYuan Markdown while preserving legal substance, tables, images, and explanations. Repair clearly misrecognized headings, broken heading fragments, and semantic heading nesting; add equivalent, easier-to-review Markdown summaries below unwieldy memorization-sheet tables without replacing them. Also use for targeted repairs to text produced by an earlier legal-marknote version.
---

# Legal Marknote

Use this skill when法考教材、题目、解析或笔记需要整理成可复习的思源笔记。

## Workflow

1. Preserve legal substance, wording, tables, images, statutory text, explanations, and the intended hierarchy. Preserve title wording and order, but repair a title marker or title level when the source has clearly misrecognized the structure. When the user authorizes removal of non-standard headings, remove only the false heading marker or duplicate heading wrapper; preserve the answer, explanation, and legal content. Retain every source table as a table; when one unwieldy table contains two or more independent category groups, split it at category boundaries into smaller sibling tables without losing any group, row, column cue, qualification, or legal effect. After splitting, give every independent table a nearby, meaningful Markdown heading at the correct level; never leave a bare category line or raw cell text immediately above a table. Add an equivalent list or Callout summary below the retained or split tables when it improves review. For a SiYuan merged table, first map its logical grid: every `rowspan`/`colspan` must have exactly matching `fn__none` cells, and every `fn__none` must be covered by an actual merge. Do not emit redundant `colspan='1'` or `rowspan='1'`.
2. Run a heading-repair pass before formatting body content. Treat every source heading marker as a candidate, then keep, merge, demote, or convert it only from its role in the surrounding structure. First identify question-and-answer regions: from `###### 习题` through the fenced question and `**回答与解析：**` answers, a numbered line is answer content, not a heading. In that region, an existing `#### 1. ...`, `#### (1) ...`, `#### ① ...`, or equivalent numeric marker is a batch-recognition error, not evidence of a real heading; demote it to the corresponding quoted ordered-list item or body text. Never carry such a marker into the output heading hierarchy. Follow the decision rules in [the detailed guide](references/note-guide-original.md#标题识别与修复).
3. Separate source content from added summaries or study prompts.
4. Break long prose at semantic boundaries: a definition or explanation introduced by words such as “是” may begin a child list even without punctuation. Decide child lists from semantic independence, not labels or punctuation: split parallel branches that each retain their own applicable situation, object, judgment, or legal effect; keep the prerequisites, procedure, and consequence of one inseparable rule in one item. Use indentation only for containment or progression, then dedent when that relationship ends.
5. Plan semantic colors before writing the final Markdown.
6. Apply the active-coverage, density, boundary, and callout rules in [the detailed guide](references/note-guide-original.md).
7. Actively split every table cell that is not a short, single-rule statement at semantic boundaries. In the retained table, use short cue text and `<br />` to separate independently reviewable branches; audit dense cells before output instead of leaving a paragraph intact. In the supplementary summary below an unwieldy table, render the same branches as nested Markdown lists. Keep one inseparable prerequisite-to-procedure-to-consequence rule in one item. Apply the large-table supplementary-summary rules in [the detailed guide](references/note-guide-original.md#超大表格的补充摘要) after retaining an unwieldy table.
8. Run `python -X utf8 scripts/validate_output.py <output.md> --strict`. When the original material is available as a file or snapshot, add `--source <source.md> --require-source` to gate title wording, images, tables, and SiYuan merge attributes. Treat `E404`–`E410` as a mandatory merge-grid audit before delivery.
9. Fix every reported error and review every advisory. Then manually confirm legal accuracy, source completeness, repaired hierarchy, semantic color choices, and whether each Callout category is substantively justified; syntax checks cannot decide those legal judgments.

## Question-answer heading guardrail

Inside a `习题` block, treat `回答与解析` as a hard boundary: the answer sequence belongs to the question and must remain list/body content. During batch processing, do not treat an existing `####` or `#####` before an answer number as a structural fact. Demote that batch-recognition error, preserve the substantive text, and merge a duplicate marked line into the matching answer item when the same answer is already listed below. Keep `###### 习题` itself as the question label, but do not retain numeric answer headings such as `#### 1. (1)正确...`.

## Split-table heading guardrail

Before splitting a table, build the heading skeleton for the parent topic and each independent category. Each split table must be immediately preceded by a valid Markdown heading such as `### 保全措施` or `#### 诉前保全的适用情形`; choose the level from the surrounding hierarchy. Do not output:

```md
诉前保全
| 项目 | 规则 |
| --- | --- |
```

If the source provides only a category cell or plain label, promote that label into a concise heading while retaining the category and all legal content in the table. The heading must describe the table's complete rule group, not merely repeat an arbitrary first cell. Do not add a heading for every row when rows belong to one category, and do not use bold text alone as a substitute for a heading.

## Legacy Output Revision

When the user states that a text was already processed by an earlier `legal-marknote` version and asks only for corrections, use [the revision-only guide](references/legacy-output-revision.md). Do not rerun the full workflow or load `references/note-guide-original.md` by default; inspect only the affected fragment and its local context, then preserve every unrelated part of the existing output.

## Accuracy

- Never replace a legal rule with an unsupported paraphrase.
- Keep answer bases and explanations attached to the material they justify.
- Use highlights and colors as retrieval cues, not decoration.
- Mark uncertain or incomplete source material for review.

The reference guide contains the complete formatting contract, color syntax, templates, and examples.
