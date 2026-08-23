# Validation and rejection taxonomy

Run `python -X utf8 scripts/validate_flashcard.py <draft.md> --source <source.md> --require-report` for dedicated mode when the source is a file. The checker is structural; legal accuracy and source truth remain human/source checks.

Reject a candidate when one of these conditions is observed:

- `unsupported`: a question, answer, citation, or cloze target is absent from supplied material.
- `ambiguous-boundary`: the card root, answer boundary, source range, or variant parent cannot be determined.
- `missing-topic`: no reusable or collision-checked derived child `custom-qb-note-topic-id` can be resolved after the self-completion workflow in [topic-resolution.md](topic-resolution.md).
- `missing-tag`: neither an existing tag nor a stable tag from the source path/H1/nearest heading can identify the card's knowledge scope.
- `missing-priority`: the source boundary is too ambiguous to apply the P1-P4 evidence rubric; omission of an explicit source priority alone is not a rejection.
- `missing-style-source`: the relevant provider range has no reusable style fragment; keep the card plain and report the gap instead of inventing a style.
- `duplicate`: normalized question or stable ID duplicates an existing card in the same source range.
- `duplicate-summary`: the candidate only unions or restates facts already tested by accepted cards and adds no new scoring axis.
- `coverage-gap`: an independently testable source fact has no candidate or explicit rejection disposition in the working source-fact ledger.
- `over-budget`: the card is valid but exceeds an explicitly requested numerical card budget after priority ordering. Do not use this reason when no budget was supplied.
- `uncertain-law`: a date, period, exception, case, or statute needs verification.

The checker must fail on invalid attribute names, multiline or malformed IALs, schema values, card IDs, renderer values, duplicate IDs, detached roots, code-fence IALs, malformed or over-reused note-topic IDs, unresolved broad-topic fallback, missing source-grounded knowledge tags, missing or multiple `#闪卡/优先级/P1#`-`P4` tags, invalid priority tags, generated `问题：`/`答案：` prefixes, basic fronts without a final question mark, basic fronts that use `==...==`, missing direct answer children, mnemonic roots disguised as questions or missing a specific recall-subject label, cloze or mnemonic highlights absent from the source provider range, invented, mismatched, or dropped source styles when `--source` is supplied, missing MarkNote anchors when no source is supplied, oversized answer items, excessive answer counts, report mismatches, top-level source/protocol/style audit preambles, a missing, duplicated, malformed, or non-final source/protocol line, runtime-field leakage, and missing required fields.

The checker cannot infer legal recall axes, broad-provider misuse, or complete source coverage. Manually apply [card-design.md](card-design.md) and [topic-resolution.md](topic-resolution.md) after it passes: verify one expected-answer statement per card, reject definition/status/policy mixtures and duplicate summaries, require a narrow provider per independent axis, and reconcile every source-fact ledger row. A passing result is necessary but not sufficient for card quality or legal accuracy.

When a file path is part of the request, also run `scripts/validate_naming.py <output.md> --source <source.md>`. It checks the source-derived filename, dedicated sibling placement, and exact source-derived H1; a failure is a naming or placement rejection, not a reason to edit the source note.
