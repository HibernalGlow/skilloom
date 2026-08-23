# Validation and rejection taxonomy

Run `python -X utf8 scripts/validate_flashcard.py <draft.md> --require-report` for dedicated mode. The checker is structural; legal accuracy and source truth remain human/source checks.

Reject a candidate when one of these conditions is observed:

- `unsupported`: a question, answer, citation, or cloze target is absent from supplied material.
- `ambiguous-boundary`: the card root, answer boundary, source range, or variant parent cannot be determined.
- `missing-topic`: no confirmed narrow `custom-qb-note-topic-id` value exists after the self-completion workflow in [topic-resolution.md](topic-resolution.md).
- `missing-tag`: no source-grounded knowledge tag can be confirmed for an accepted card.
- `missing-priority`: no single source-grounded flashcard priority from P1-P4 can be confirmed for an accepted card.
- `duplicate`: normalized question or stable ID duplicates an existing card in the same source range.
- `over-budget`: the card is valid but exceeds the requested card budget after priority ordering.
- `uncertain-law`: a date, period, exception, case, or statute needs verification.

The checker must fail on invalid attribute names, multiline or malformed IALs, schema values, card IDs, renderer values, duplicate IDs, detached roots, code-fence IALs, malformed or over-reused note-topic IDs, unresolved broad-topic fallback, missing source-grounded knowledge tags, missing or multiple `#闪卡/优先级/P1#`-`P4` tags, invalid priority tags, basic roots that use `==...==`, mnemonic roots disguised as questions or missing a specific recall-subject label, missing MarkNote anchors, oversized answer items, excessive answer counts, report mismatches, runtime-field leakage, and missing required fields. A passing result is necessary but not sufficient for legal accuracy.

When a file path is part of the request, also run `scripts/validate_naming.py <output.md> --source <source.md>`. It checks the source-derived filename, dedicated sibling placement, and exact source-derived H1; a failure is a naming or placement rejection, not a reason to edit the source note.
