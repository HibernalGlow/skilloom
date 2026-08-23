# Dedicated-card mode

Read this file only after the user explicitly requests flashcards. It is a stricter output contract layered on top of `legal-marknote` or `legal-goldquest`; those skills remain the source of truth for legal formatting and question preservation.

## Deterministic workflow

1. Establish the source range, source key, known topic IDs, existing cards, and card budget. Completion criterion: each input is present or listed as a blocking gap.
2. Run a source-grounding pass. Every question, answer, citation, and cloze target must be traceable to supplied material. Mark uncertain statutes, dates, exceptions, and cases as `待核实`; do not fill them from memory. Completion criterion: every proposed fact has a source locator or a blocking note.
3. Draft one-card/one-recall-target candidates. Use `basic` for a direct question and answer, `cloze` for one short missing term, and `mnemonic` when the material is better recalled as a口诀, sequence, compact comparison, or other source-grounded cue without inventing a question. Split long answers into answer subitems or separate cards; allow variants only when they test the same parent fact. Completion criterion: each candidate states one independent recall target, a stable variant key, and its semantic kind.
4. Compare the same source range's existing card IDs and normalized question text. Reject near-duplicates before rendering. Completion criterion: every rejection names `duplicate`, `unsupported`, `ambiguous-boundary`, `missing-topic`, `over-budget`, or another listed reason in [validation.md](validation.md).
5. Render accepted cards with the default `basic/list` container. Use `cloze/mark`, `blockquote`, or `callout` only when the material's retrieval behavior requires it. Keep headings and superBlocks out of the default route. Completion criterion: the root block and its IAL make the card boundary explicit.
6. Run `scripts/validate_flashcard.py` on the draft, then preview and budget-filter the passing cards. Completion criterion: the checker exits 0 and the report reconciles candidate, accepted, and rejected counts.
7. Output only the accepted Markdown plus the count report; do not call Riff or mutate runtime state. Completion criterion: the final text contains no runtime scheduling fields and states the count and rejection reasons.

## Rendering rules

- Basic cards use one root list item `- 问题：...` and indented `- 答案：...` items. Attach the card IAL to that root list block, outside any code fence.
- Cloze cards use `==明确关键术语==` as the deletion target. Keep the cloze short; never highlight an entire conclusion sentence.
- Mnemonic cards do not require a fake question. Put the complete source-grounded口诀 or cue in a visible `==...==` highlight. When each sentence contributes a character or segment, highlight the complete口诀, the corresponding character/segment in every source sentence, and the assembled result; retain the mapping order. Use a child list for the sentence-to-character mapping when it improves auditability.
- A blockquote or callout must carry a substantive property (for example an exception or warning), not decoration.
- Preserve existing mark cards. Do not rewrite them as basic/list cards.
- A variant ID is the parent business ID plus a stable suffix such as `-v1`; variants share the parent prefix and never use a block ID, Riff ID, or database row ID.
