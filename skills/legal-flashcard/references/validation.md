# Validation and rejection taxonomy

Run `python -X utf8 scripts/validate_flashcard.py <draft.md> --source <source.md> --require-report` for dedicated mode when the source is a file. The checker is structural; legal accuracy and source truth remain human/source checks.

For an unsaved draft, pipe the Markdown to `python -X utf8 scripts/validate_flashcard.py - --require-report`. This stdin pass still enforces schema, identity, card boundaries, style diversity, duplicate-summary heuristics, and report reconciliation; run a second pass with `--source` when a source file is available. Completion criterion: an in-memory draft is validated rather than exempted because it lacks a path.

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

The checker must fail on invalid attribute names, multiline or malformed IALs, schema values, card IDs, renderer values, duplicate IDs, detached roots, code-fence IALs, malformed or over-reused note-topic IDs, unresolved broad-topic fallback, missing source-grounded knowledge tags, missing or multiple `#闪卡/优先级/P1#`-`P4` tags, invalid priority tags, generated `问题：`/`答案：` prefixes, basic fronts without a final question mark, basic fronts that use `==...==`, missing direct answer children, obviously complex flat backs without a source-shaped structure, mnemonic roots disguised as questions or missing a specific recall-subject label, cloze or mnemonic highlights absent from the source provider range, invented, mismatched, or dropped source styles when `--source` is supplied, one-signature styled cards (`E047`), missing MarkNote anchors when no source is supplied, oversized answer items, excessive answer counts, report mismatches, top-level source/protocol/style audit preambles, a missing, duplicated, malformed, or non-final source/protocol line, runtime-field leakage, and missing required fields. When `--rich-style` is supplied, it must also fail the GoldQuest-level rich visual contract (`E060` auxiliary styles, `E061` structural families, `E062` background anchors, and `E063` missing primary visual). Read [style-inheritance.md](style-inheritance.md#card-unit-style-gate) for the authoritative style-counting rule.

Warnings are advisory: print each finding, but return success when every finding begins with `W`. Review all warnings before acceptance:

When `--rich-style` is supplied for a medium/complex dedicated deck, these GoldQuest-level findings are blocking:

- `E060`: fewer than four auxiliary style families (`highlight`, `italic`, `strike`, `code`, `underline`).
- `E061`: fewer than four structural families (`nested-list`, `callout`, `subheading`, `table`, `visual`, `divider`).
- `E062`: fewer than three short `background-color` anchors.
- `E063`: a relation-heavy deck has no Mermaid, inherited image, or other documented primary visual.
- `E064`: a color/background anchor exceeds eight visible characters.
- `E065`: punctuation is inside a color/background anchor.
- `E066`: a sparse foreground palette was not augmented with three distinct semantic background signatures.
- `E067`: a Callout title is not a complete question; the title is the DAMO card front.
- `E068`: a Callout title contains inline styling; titles must be plain-text questions and styles belong in the answer body.

- `W101`: foreground color and background/highlight are not both represented; inherit the missing dimension only when the provider range supplies it.
- `W102`: a borderline flat multi-item back may hide a parent/child relation or mixed recall axes.
- `W103`: ordered answers lack an explicit sequence, procedure, chronology, or priority cue on the front.
- `W104`: a table or Mermaid carrier is not directly inherited from the supplied source; audit every mapping.
- `W105`: one card uses both a table and Mermaid; confirm that both are necessary for one scoring axis.
- `W106`: ordered answers have no sequence semantics in the supplied source range; source numbering alone remains unordered peers.
- `W107`: a multi-answer card repeats at least two exact answer facts already tested by sibling cards and is probably a duplicate summary.
- `W108`: a question-side Mermaid has no visible recall slot and may expose the answer instead of cueing it.
- `W109`: a Mermaid lacks explicit semantic classes; use source classes or generated `known`/`recall`/`answer` roles instead of default styling.
- `W110`: a complex card uses exactly two style signatures; review whether three or more source/MarkNote roles are available instead of stopping at the minimum `E047` gate.
- `W111`: a styled deck uses two or fewer unique signatures overall; the deck is visually monotone even though no single card triggers `E047`.
- `W112`: a medium/complex process, branch, role mapping, comparison, or many-to-one card has no Mermaid, inherited image, or documented primary visual carrier.

Completion criterion: every warning has an explicit keep, revise, split, or reject disposition, and running the checker on a warning-only file exits `0` while any `E` finding exits nonzero.

The checker cannot fully infer legal recall axes, carrier equivalence, source-semantic hierarchy, broad-provider misuse, or complete source coverage. Manually apply [card-design.md](card-design.md), [answer-structure.md](answer-structure.md), and [topic-resolution.md](topic-resolution.md) after it passes: compare each back with the source, keep shared-action clauses intact, verify one primary carrier per expected answer, reject definition/status/policy mixtures and duplicate summaries, require a narrow provider per independent axis, and reconcile every source-fact ledger row. A passing result is necessary but not sufficient for card quality or legal accuracy.

When a file path is part of the request, also run `scripts/validate_naming.py <output.md> --source <source.md>`. It checks the source-derived filename, dedicated sibling placement, and exact source-derived H1; a failure is a naming or placement rejection, not a reason to edit the source note.
