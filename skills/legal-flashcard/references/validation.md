# Validation and rejection taxonomy

Run `python -X utf8 scripts/validate_flashcard.py <draft.md>` for dedicated mode. The checker is structural; legal accuracy and source truth remain human/source checks.

Reject a candidate when one of these conditions is observed:

- `unsupported`: a question, answer, citation, or cloze target is absent from supplied material.
- `ambiguous-boundary`: the card root, answer boundary, source range, or variant parent cannot be determined.
- `missing-topic`: no confirmed `custom-qb-question-topic-ids` value exists.
- `duplicate`: normalized question or stable ID duplicates an existing card in the same source range.
- `over-budget`: the card is valid but exceeds the requested card budget after priority ordering.
- `uncertain-law`: a date, period, exception, case, or statute needs verification.

The checker must fail on invalid attribute names, schema values, card IDs, renderer values, duplicate IDs, detached roots, code-fence IALs, malformed topic IDs, runtime-field leakage, and missing required fields. A passing result is necessary but not sufficient for legal accuracy.
