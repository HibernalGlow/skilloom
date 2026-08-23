# Validation and rejection taxonomy

Run `python -X utf8 scripts/validate_flashcard.py <draft.md> --require-report` for dedicated mode. The checker is structural; legal accuracy and source truth remain human/source checks.

Reject a candidate when one of these conditions is observed:

- `unsupported`: a question, answer, citation, or cloze target is absent from supplied material.
- `ambiguous-boundary`: the card root, answer boundary, source range, or variant parent cannot be determined.
- `missing-topic`: no confirmed narrow `custom-qb-note-topic-id` value exists.
- `duplicate`: normalized question or stable ID duplicates an existing card in the same source range.
- `over-budget`: the card is valid but exceeds the requested card budget after priority ordering.
- `uncertain-law`: a date, period, exception, case, or statute needs verification.

The checker must fail on invalid attribute names, multiline or malformed IALs, schema values, card IDs, renderer values, duplicate IDs, detached roots, code-fence IALs, malformed or over-reused note-topic IDs, missing MarkNote anchors, oversized answer items, excessive answer counts, report mismatches, runtime-field leakage, and missing required fields. A passing result is necessary but not sufficient for legal accuracy.
