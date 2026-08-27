# Validation and rejection taxonomy

Run `python -X utf8 scripts/validate_flashcard.py <draft.md> --source <source.md> --require-report` for dedicated mode when the source is a file. **Dedicated mode is strict by default**: `--require-report` and `--rich-style` are on without any flag, so a missing report or an unsatisfied medium/complex rich contract already fails the run. Relaxed mode requires the COMPLETE manual relaxation set `--no-require-report --no-rich-style` together; passing only one exits with a usage error. The checker is structural; legal accuracy and source truth remain human/source checks.

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

The checker must fail on invalid attribute names, multiline or malformed IALs, schema values, card IDs, renderer values, duplicate IDs, detached roots, code-fence IALs, malformed or over-reused note-topic IDs, unresolved broad-topic fallback, missing source-grounded knowledge tags, missing or multiple `#闪卡/优先级/P1#`-`P4` tags, invalid priority tags, generated `问题：`/`题干：`/`答案：`/`解析：`/`问：` label prefixes (`E044`), basic fronts without a final question mark, basic fronts that use `==...==`, missing direct answer children, obviously complex flat backs without a source-shaped structure, mnemonic roots disguised as questions or missing a specific recall-subject label, cloze or mnemonic highlights absent from the source provider range, invented, mismatched, or dropped source styles when `--source` is supplied, one-signature styled cards (`E047`), missing MarkNote anchors when no source is supplied, oversized answer items, excessive answer counts, YAML report mismatches, top-level source/protocol/style audit preambles, a missing, duplicated, malformed, or non-final YAML report/provenance block, runtime-field leakage, case/exercise front replay (`E079`), detached or vague memory-link Callouts (`E082`/`E083`), back Callouts mounted at answer-item depth (`E086`), leftover card containers nested in a card body (`E087`), report priority counts missing or mismatched (`E088`), the P2 default-tier flood (`E089`), missing per-card or deck-level semantic emoji (`E090`/`E091`), overlong card fronts (`E092`), sub-lists inside front-only cloze/mark cards (`E093`), a dominant repeated emoji (`E094`), Callouts that repeat the direct answer (`E095`), adjacent-line color monotony (`E096`), long unsplit back items (`E097`), Callout directives not preceded by a blank line or block boundary (`E098`), list items whose text starts with an ordered-list marker (`E099`), a card that reuses the same emoji on front and back (`E100`), knowledge-tag segments that are position labels like `专题二`/`第19讲`/bare numbers (`E101`), and missing required fields. When `--rich-style` is supplied, it must also fail the GoldQuest-level rich visual contract (`E060` auxiliary styles, `E061` structural families, `E062` background anchors, `E063` missing primary visual, `E074` uncolored substantive answer lines, `E075` under-colored multi-sentence lines, `E076` uncolored recurring subjects or legal concepts, `E080` adjacent-card palette repetition, `E081` deck-wide foreground imbalance). Sequence fronts must use ordered answer children (`E078`). Read [style-inheritance.md](style-inheritance.md#card-unit-style-gate) for the authoritative style-counting rule.

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
- `E070`: the generation report is missing or is not exactly one parseable YAML fenced block containing report counts, `report.priorities` (P1-P4), and source/protocol fields.
- `E071`: the YAML report/source block is not the final nonblank block.
- `E074`: in rich mode, a substantive answer line of at least fourteen visible characters has no short semantic color/background anchor. Cloze/mnemonic highlights only satisfy this line when they are the intentional retrieval target.
- `E075`: in rich mode, a multi-sentence answer line has fewer than one semantic color anchor per one or two sentences.
- `E076`: in rich mode, a recurring subject or legal concept is colored in one answer occurrence but left plain in another; reuse the role color on every answer occurrence.
- `E080`: adjacent accepted cards have at least 60% weighted foreground-anchor overlap, or the same color supplies at least half of each card's foreground anchors; diversify source-grounded roles or reorder the cards.
- `E081`: one foreground color exceeds the deck balance ceiling `max(30%, 2 / distinct foreground colors)` by anchor count; treat color-table labels as soft cues, rebalance the local role palette, and do not insert token colors that do not carry a semantic role.
- `E082`: a `联系记忆`/`关联记忆`/`对比记忆` Callout is detached from the list-card back or appears before the direct answer; indent it inside the root and place it after the answer.
- `E083`: a memory-link Callout title is styled, lacks a colon plus specific linked target, or uses a generic target such as `相关考点`; keep the title plain and name what to compare or connect.
- `E084`: a rich deck of at least four cards has substantive Callouts in fewer than `ceil(accepted cards / 6)` card units; root and nested Callouts both count when they carry a real semantic peak.
- `E085`: a rich card explicitly contains an exception, trap, confusion, risk, or memory-link cue but has no root or nested Callout.
- `E086`: a Callout inside a list card sits at the same depth as the direct answer items instead of inside the answer sub-list; indent it deeper than the answers or write the note as a normal sub-list item.
- `E087`: a card body contains a leftover card container — a nested `custom-dm-*` attribute line from an already-cardified source range; strip the marker completely instead of keeping the block.
- `E088`: `report.priorities` is missing or does not match the accepted cards' actual `#闪卡/优先级/P1#`-`P4#` distribution; the four counts must sum to `report.accepted`.
- `E089`: P2 has become the default tier — in a deck of at least four cards, more than half sit in `P2`; recompare priorities against the source and differentiate a real lower-yield tier instead of defaulting to P2.
- `E090`: a non-simple card in a rich deck has no semantic emoji cue beyond `✅/❌`; every medium-or-higher card needs at least one, position it beside the labeled legal relationship, boundary, or conclusion.
- `E091`: rich-deck emoji coverage is at most 80% of accepted cards; overall coverage must exceed 80% — simple cards are the only tolerated minority without emoji.
- `W127`: a card that uses emoji carries it on only one side; keep a semantic cue on both the front and the back.
- `W128`: the source carries mnemonic material — a 口诀 label or an implicit mnemonic (inline-code compact sequence, memory Callout, 谐音/缩写/取字 mapping) — but the deck has no `mnemonic` card; turn it into a mnemonic card with a highlighted cue and decoded segments.
- `E092`: a card front (question or mnemonic cue) exceeds about 70 visible characters; keep it short and move context to the back, or onto the front as `<br />` line breaks or a text-block Callout.
- `E093`: a cloze/mark front-only card carries a bare child list sub-list; the sub-list is parsed as the back card — wrap it inside a Callout (a `> [!TIP]` block containing the quoted items) or use `<br />` line breaks to keep it on the front.
- `E094`: the same semantic emoji repeats more than eight times in one deck; one emoji maps to one specific concept — diversify.
- `E095`: a Callout's body mostly repeats the card's direct answer text (≥60% of its character grams already appear in the non-Callout content); a Callout must add value — state the boundary, exception, trap, or reasoning in new words, or drop it.
- `E096`: three consecutive card lines are each dominated by the same color (that color supplies ≥60% of each line's anchors); vary the semantic colors across adjacent answer lines so the palette stays an index.
- `E097`: a back list item — direct or nested, outside Callouts/fences — exceeds 42 visible characters; split it by semantics into a governing parent plus child items, and use ordered `1.` children for steps, procedures, or sequences.
- `E098`: a Callout directive must be preceded by a blank line (or the start of a block, another quote line, a heading, or a fence boundary); directly after a list item or paragraph it is parsed as continuation text and will not be recognized.
- `E099`: a list item's text begins with an ordered-list marker (`1.` / `1、` / `1)` / `（1）` / `①`); the card parser reads it as a nested ordered list and misrecognizes the structure — remove the marker from the item text, or give each numbered child its own indented real `1.` list line.
- `E100`: a card reuses the same emoji on the front and the back (one card in the corpus carried `💪` on both the question `支配权的概念是什么？` and the answer `又称绝对权`); duplicating one marker fakes the front/back emoji cue — the front emoji anchors the question's concept, so the back must anchor a different concept with a different emoji. The front of a card and the back of the card must share no semantic emoji.
- `E101`: a knowledge tag contains a position label as a segment (`专题二`/`第19讲`/`第三章`/bare `02`); position labels say nothing about content and go stale when chapters move — replace the segment with the stable source-named chapter or topic (e.g. `#法考/民诉/专题二/诉的分离#` → `#法考/民诉/诉的基本理论/诉的分离#`), keeping the filename/H1 sort prefix untouched.
- `W129`: an emoji anchors to a generic cue word (注意/重点/要点/考点/提示/陷阱…); anchor it to the specific legal concept instead.
- `E130`: an emoji + following-word pair repeats six or more times, a hard signature of scripted batch insertion; place emoji semantically per concept, never by mechanical word replacement.
- `E131`: most semantic emoji pile up at sentence ends (≥70%); hard gate — put each emoji directly on the concept word it marks (one emoji per parallel concept) so the term and the icon are visually bound.
- `E132`: most semantic emoji bunch up at line heads as label prefixes (≥70%); hard gate — embed emoji inside the answer content next to the concept words they mark so the icons appear in the content.
- `E133`: at least half the deck's semantic emoji float without a neighboring concept word (dangling at line ends, clause boundaries, or between punctuation); hard gate — anchor each icon directly beside its term (词前或词后紧贴概念词), never as loose decoration.
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
- `W121`: P2 supplies exactly half of a deck of at least six cards; recompare priorities against the source instead of treating P2 as the default.
- `W122`: a sufficiently large deck uses fewer than three priority levels; audit whether the source really lacks meaningful separation.
- `W123`: a deck of at least eight cards has no P4 cards; check whether valid low-yield material was promoted to P2/P3 or correctly rejected. An evidence-backed absence may remain.
- `W124`: one foreground color supplies more than 25% of the deck's foreground anchors (while still below `E081`); the palette is becoming a visual default. Reassign grounded semantic roles or add a source-grounded second dimension before delivery.
- `W125`: a rich card contains a prohibition, invalidity, limiting, or principle cue without a Callout; review whether a nested Callout would make that boundary easier to retrieve.
- `W126`: the card's source range contains a Markdown diagram (`![...](...)`) not carried on this card's back; copy the source image beneath a governing answer child when it carries legal content, or document why it was dropped.

Completion criterion: every warning has an explicit keep, revise, split, or reject disposition, and running the checker on a warning-only file exits `0` while any `E` finding exits nonzero.

The checker cannot fully infer legal recall axes, carrier equivalence, source-semantic hierarchy, broad-provider misuse, or complete source coverage. Manually apply [card-design.md](card-design.md), [answer-structure.md](answer-structure.md), and [topic-resolution.md](topic-resolution.md) after it passes: compare each back with the source, keep shared-action clauses intact, verify one primary carrier per expected answer, reject definition/status/policy mixtures and duplicate summaries, require a narrow provider per independent axis, and reconcile every source-fact ledger row. A passing result is necessary but not sufficient for card quality or legal accuracy.

When a file path is part of the request, also run `scripts/validate_naming.py <output.md> --source <source.md>`. It checks the source-derived filename, dedicated sibling placement, and exact source-derived H1; a failure is a naming or placement rejection, not a reason to edit the source note.
