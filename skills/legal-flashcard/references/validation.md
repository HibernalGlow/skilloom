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
- `case-narrative`: the candidate only reproduces an original case's parties, facts, chronology, or question stem without extracting a reusable rule, exception, distinction, application path, or trap.

The checker must fail on invalid attribute names, multiline or malformed IALs, schema values, card IDs, renderer values, duplicate IDs, detached roots, code-fence IALs, malformed or over-reused note-topic IDs, unresolved broad-topic fallback, missing source-grounded knowledge tags, missing or multiple `#闪卡/优先级/P1#`-`P4` tags, invalid priority tags, generated `问题：`/`答案：` prefixes, basic fronts without a final question mark, basic fronts that use `==...==`, missing direct answer children, obviously complex flat backs without a source-shaped structure, mnemonic roots disguised as questions or missing a specific recall-subject label, cloze or mnemonic highlights absent from the source provider range, invented, mismatched, or dropped source styles when `--source` is supplied, one-signature styled cards (`E047`), missing MarkNote anchors when no source is supplied, oversized answer items, excessive answer counts, YAML report mismatches, top-level source/protocol/style audit preambles, a missing, duplicated, malformed, or non-final YAML report/provenance block, runtime-field leakage, case/exercise front replay (`E079`), detached or vague memory-link Callouts (`E082`/`E083`), and missing required fields. When `--rich-style` is supplied, it must also fail the GoldQuest-level rich visual contract (`E060` auxiliary styles, `E061` structural families, `E062` background anchors, `E063` missing primary visual, `E074` uncolored substantive answer lines, `E075` under-colored multi-sentence lines, `E076` uncolored recurring subjects or legal concepts, `E080` adjacent-card palette repetition, `E081` deck-wide foreground imbalance). Sequence fronts must use ordered answer children (`E078`). Read [style-inheritance.md](style-inheritance.md#card-unit-style-gate) for the authoritative style-counting rule.

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
- `E069`: a medium/complex rich deck has fewer than four semantic foreground colors; build a role dictionary instead of cycling a sparse palette.
- `E070`: the generation report is missing or is not exactly one parseable YAML fenced block containing report counts and source/protocol fields.
- `E071`: the YAML report/source block is not the final nonblank block.
- `E074`: in rich mode, a substantive answer line of at least fourteen visible characters has no short semantic color/background anchor. Cloze/mnemonic highlights only satisfy this line when they are the intentional retrieval target.
- `E075`: in rich mode, a multi-sentence answer line has fewer than one semantic color anchor per one or two sentences.
- `E076`: in rich mode, a recurring subject or legal concept is colored in one answer occurrence but left plain in another; reuse the role color on every answer occurrence.
- `E080`: adjacent accepted cards have at least 60% weighted foreground-anchor overlap, or the same color supplies at least half of each card's foreground anchors; diversify source-grounded roles or reorder the cards.
- `E081`: one foreground color exceeds the deck balance ceiling `max(30%, 2 / distinct foreground colors)` by anchor count; treat color-table labels as soft cues, rebalance the local role palette, and do not insert token colors that do not carry a semantic role.
- `E082`: a `联系记忆`/`关联记忆`/`对比记忆` Callout is detached from the list-card back or appears before the direct answer; indent it inside the root and place it after the answer.
- `E083`: a memory-link Callout title is styled, lacks a colon plus specific linked target, or uses a generic target such as `相关考点`; keep the title plain and name what to compare or connect.
- `E078`: a front asks for a sequence, procedure, stage, or order but the direct answer children are unordered peer bullets without a necessary table/Mermaid carrier.
- `E079`: the front reproduces a source exercise or case question; extract a neutral reusable rule or reject the case candidate.

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
- `W116`: a complex card is missing either a semantic foreground color or a background/highlight peak; resolve only when the source/style plan supplies both dimensions.
- `W117`: a complex card has no auxiliary style family with a semantic job; add highlight, underline, code, strike, or italic only for a real boundary or retrieval cue.
- `W118`: a card-back memory link is long enough to resemble a second answer; reduce it to one relation axis and leave the linked doctrine's full answer in its own card.
- `W112`: a medium/complex process, branch, role mapping, comparison, or many-to-one card has no Mermaid, inherited image, or documented primary visual carrier.
- `W114`: an answer line combines multiple semantic clauses without a governing parent and child structure; split conditions, actions, effects, exceptions, or alternatives.
- `W115`: Callout tags are embedded in the title; move knowledge and priority tags to the immediately following quoted line.
- `W121`: P2 dominates a sufficiently large deck; recompare candidates against the source instead of treating P2 as the default.
- `W122`: a sufficiently large deck uses fewer than three priority levels; audit whether the source really lacks meaningful separation.
- `W123`: a deck of at least eight cards has no P4 cards; check whether valid low-yield material was promoted to P2/P3 or correctly rejected. An evidence-backed absence may remain.
- `W124`: one foreground color supplies more than 25% of the deck's foreground anchors (while still below `E081`); the palette is becoming a visual default. Reassign grounded semantic roles or add a source-grounded second dimension before delivery.

Completion criterion: every warning has an explicit keep, revise, split, or reject disposition, and running the checker on a warning-only file exits `0` while any `E` finding exits nonzero.

The checker cannot fully infer legal recall axes, carrier equivalence, source-semantic hierarchy, broad-provider misuse, or complete source coverage. Manually apply [card-design.md](card-design.md), [answer-structure.md](answer-structure.md), and [topic-resolution.md](topic-resolution.md) after it passes: compare each back with the source, keep shared-action clauses intact, verify one primary carrier per expected answer, reject definition/status/policy mixtures and duplicate summaries, require a narrow provider per independent axis, and reconcile every source-fact ledger row. A passing result is necessary but not sufficient for card quality or legal accuracy.

When a file path is part of the request, also run `scripts/validate_naming.py <output.md> --source <source.md>`. It checks the source-derived filename, dedicated sibling placement, and exact source-derived H1; a failure is a naming or placement rejection, not a reason to edit the source note.
