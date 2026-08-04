---
name: legal-marknote
description: Convert legal study material into structured SiYuan Markdown while preserving source structure, law, tables, images, and explanations.
---

# Legal Marknote

Use this skill when法考教材、题目、解析或笔记需要整理成可复习的思源笔记。

## Workflow

1. Preserve the original hierarchy, wording, tables, images, statutory text, and explanations.
2. Separate source content from added summaries or study prompts.
3. Break long prose at semantic boundaries: a definition or explanation introduced by words such as “是” may begin a child list even without punctuation. Decide child lists from semantic independence, not labels or punctuation: split parallel branches that each retain their own applicable situation, object, judgment, or legal effect; keep the prerequisites, procedure, and consequence of one inseparable rule in one item. Use indentation only for containment or progression, then dedent when that relationship ends.
4. Plan semantic colors before writing the final Markdown.
5. Apply the active-coverage, density, boundary, and callout rules in [the detailed guide](references/note-guide-original.md).
6. Make long table cells scannable with short cue text and varied inline emphasis; put every numbered item on its own line with `<br />`.
7. Run `python -X utf8 scripts/validate_output.py <output.md> --strict`. When the original material is available as a file or snapshot, add `--source <source.md> --require-source` to gate headings, images, tables, and SiYuan merge attributes.
8. Fix every reported error and review every advisory. Then manually confirm legal accuracy, source completeness, semantic color choices, and whether each Callout category is substantively justified; syntax checks cannot decide those legal judgments.

## Accuracy

- Never replace a legal rule with an unsupported paraphrase.
- Keep answer bases and explanations attached to the material they justify.
- Use highlights and colors as retrieval cues, not decoration.
- Mark uncertain or incomplete source material for review.

The reference guide contains the complete formatting contract, color syntax, templates, and examples.
