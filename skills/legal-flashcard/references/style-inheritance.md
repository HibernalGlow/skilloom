# Source-style inheritance

Read this file only in dedicated-card mode when a source note or source range is available. The source note is the visual authority; `legal-marknote` supplies syntax and semantic interpretation, not a replacement palette.

## Build the map before drafting

For each atomic `custom-qb-note-topic-id`, record a source-style map with:

- the exact styled fragment, including its complete Markdown or HTML wrapper;
- its semantic role in that source range: subject/object, procedure, threshold, exception, result, or mnemonic segment;
- its source line or heading;
- its container role: list depth, Callout type, table relation, or ordinary prose.

Include bold color/background anchors, highlight, underline, italic, strikethrough, inline code, list depth, and substantive Callouts. A source-wide palette is insufficient: map the provider range used by the card. Completion criterion: every candidate has a provider-scoped map or a named `missing-style-source` gap before card wording is drafted.

## Inherit, then adapt the boundary

1. Copy every source-derived styled fragment byte-for-byte when its text is reused in a card. Preserve the original foreground/background variable and compound style. Do not recolor it from a generic deck palette.
2. Write the question directly on the root and answers directly on its child items. Leave generated connective wording unstyled. A question may contain an exact source-styled concept, but it does not receive a new color merely because it is the root.
3. Preserve the source's meaningful child-list relationships inside the card. Preserve a Callout role only when the warning, exception, mnemonic, or conclusion itself is the retrieval unit; otherwise retain its styled content inside the default list card.
4. Treat source `==...==` separately from visual inheritance. Carry it into a formal card only when that exact span is intentionally selected as the card's short `cloze` target or explicit `mnemonic` target. Other source reading highlights remain source evidence and are not copied as active deletions.
5. Keep tables, images, Mermaid, and headings in the source note unless the whole object is required to answer one card. Link or cite the source instead of flattening a large visual into an answer list.

Completion criterion: every accepted card that reuses styled source text contains at least one exact provider-scoped styled fragment; every emitted color/background fragment exists byte-for-byte in that provider range; generated question scaffolding is unstyled; no ordinary source highlight became a deletion without an explicit `cloze` or `mnemonic` decision.

## No-style ranges

When the authoritative exported source range has no reusable style fragment, first distinguish a genuinely plain source from an unexported or wrongly selected source. A `20-整理` note is not evidence of a plain range. If the export is genuinely plain **or its provider palette is sparse**, invoke legal-marknote's rich visual contract and build a working semantic style plan for generated anchors before drafting. Add a role dictionary with at least four distinct foreground colors across 主体/对象、要件/门槛、程序/权限、例外/限制、成立/有效结果、无效/风险结果; use at least three distinct signatures, including at least three distinct background signatures, and do not repeat a two-color foreground-only palette. Generated rich augmentation may add short foreground role anchors as well as background anchors; every anchor must have a documented semantic role, remain within the GoldQuest eight-character boundary, and be attached to a real term in the answer line. Do not recolor arbitrary words or modify the original note unless separately requested. Record `missing-style-source` only when the style plan cannot be grounded in the source. Completion criterion: the card is either plain because the source and request justify it, or its generated styles trace to a documented MarkNote semantic role map, every substantive answer line is actively anchored, and the medium/complex deck reaches at least four foreground colors.

## Card-unit style gate

Count source-grounded foreground colors, background colors, and intentional `==...==` cloze/mnemonic highlights inside each card root. A complete foreground/background property combination is one signature regardless of property order; repeating it on several anchors does not create diversity.

- A card with no style stays eligible only when its provider range is genuinely plain.
- A styled card with exactly one unique signature fails `E047`.
- A complex card or deck with exactly two signatures receives `W110`/`W111` for low visual diversity; revise toward three or more semantically distinct signatures when the source/style plan supplies three or more roles. Two signatures are not a successful end state merely because `E047` is avoided.
- In `--rich-style`, complex cards also surface `W116` when either foreground or background/highlight is absent and `W117` when no auxiliary family (highlight, underline, code, strike, or italic) marks a real boundary. Uncolored substantive answer lines fail `E074`, and under-colored multi-sentence lines fail `E075`; a short definition may remain restrained, and every revision must remain source-grounded or covered by the approved MarkNote style plan.
- A styled card with foreground color but no background color or intentional highlight, or with background/highlight but no foreground color, receives advisory `W101`. The warning does not change the validator exit status.
- An intentional `==...==` target counts as the background/highlight dimension only for a `cloze` or `mnemonic` decision. Ordinary reading highlights are not copied into a card to satisfy balance.

Reuse another exact provider-scoped signature when the source supplies one. When the provider range supplies only one reusable signature, reject or report insufficient source-style diversity; never invent a style, recolor a fragment, or widen the source boundary merely to satisfy `E047` or silence `W101`. Completion criterion: every accepted styled card has at least two distinct provider-grounded signatures, every one-sided card surfaces `W101`, and every style remains byte-for-byte source-grounded.

## Deterministic check

When the source is a file, run:

```text
python -X utf8 scripts/validate_flashcard.py <draft.md> --source <source.md> --require-report
```

The source-aware gate rejects invented color/background fragments, one-signature styled cards, and cards that fail to reuse an exact styled fragment when the provider range contains one. It prints advisory warnings without returning failure when no error code is present. It complements manual checks for list depth, Callout meaning, highlight intent, and legal accuracy.

## GoldQuest-level rich visual contract

When a dedicated deck is medium or complex, apply the same visual floor used by `legal-goldquest`, not merely the local `E047` minimum:

- Build a semantic color dictionary before drafting. Repeated parties, institutions, objects, concepts, states and aliases keep stable colors; concept lists are split into legal-function slots such as主体/对象、要件/门槛、程序/权限、例外/限制、成立/有效结果、无效/风险结果.
- Use at least four auxiliary style families across the deck from `==短高亮==`, `<em>斜体</em>`, `~~删除线~~`, inline code and `<u>下划线</u>`. The families must have semantic jobs; do not add decorative wrappers merely to reach four.
- Use at least four structural families across the deck from nested lists, substantive Callout, source-derived subheadings, a real comparison table, a visual, and dividers.
- Use at least three short background-color anchors for visual hierarchy. They may mark a conclusion, exception, deadline, decision point or core condition; do not color whole sentences.
- Treat every substantive answer line of at least fourteen visible characters as a GoldQuest analysis line: give it at least one short color/background anchor, and when it carries several sentences give it one anchor per one or two sentences. Reuse the same role color for recurring subjects, concepts, and aliases; split different legal-function slots rather than cycling one lead style.
- Balance the deck after semantic assignment. Preserve each recurring term's stable source/role color, then use the other grounded roles on their own terms and reorder cards when necessary: adjacent cards fail when their actual foreground-anchor distributions substantially repeat (`E080`), and the deck fails when one color exceeds the frequency ceiling in `validation.md` (`E081`). Do not recolor one concept between cards or insert decorative anchors to manufacture balance.
- Apply GoldQuest subject coverage inside each card: once `法定代理人`, `委托代理人`, `当事人`, `特别授权`, `一般授权`, `代理权`, `诉讼行为`, or another mapped role/concept receives a semantic color, every later answer occurrence must retain that color. A line containing two independent roles or a role plus its legal effect should carry two short anchors, not one decorative anchor at the end.
- Use at least one intentional visual for medium/complex content. Prefer editable SiYuan Mermaid for procedures, branches, role relationships, comparisons and many-to-one mappings; use an inherited image only when it is the materially better source carrier.
- Keep all style anchors bold-first and source-grounded. `E047` remains the per-card hard floor, while `E060`-`E063` enforce the deck-level rich contract when `--rich-style` is used.
- In rich mode, apply the GoldQuest anchor boundary as well: each foreground/background anchor is at most eight visible characters and keeps punctuation outside the styled span (`E064`/`E065`).

Completion criterion: a medium/complex dedicated deck passes `python -X utf8 scripts/validate_flashcard.py <draft.md> --source <source.md> --require-report --rich-style` with no rich-style `E` finding, adjacent cards have distinct foreground distributions, no foreground color exceeds the deck balance ceiling, and each warning about low signature diversity or a missing visual has a documented disposition.
