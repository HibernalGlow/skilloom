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

When the relevant source range has no reusable style fragment, keep the card plain and record `missing-style-source`; do not attach an unrelated colored word. If the user has also requested a MarkNote restyle of the source, complete and validate that separate source-note operation first, then rebuild the map from the revised source. Completion criterion: a plain card is traceable to a genuinely plain provider range rather than a skipped source inspection.

## Card-unit style gate

Count source-grounded foreground colors, background colors, and intentional `==...==` cloze/mnemonic highlights inside each card root. A complete foreground/background property combination is one signature regardless of property order; repeating it on several anchors does not create diversity.

- A card with no style stays eligible only when its provider range is genuinely plain.
- A styled card with exactly one unique signature fails `E047`.
- A styled card with foreground color but no background color or intentional highlight, or with background/highlight but no foreground color, receives advisory `W101`. The warning does not change the validator exit status.
- An intentional `==...==` target counts as the background/highlight dimension only for a `cloze` or `mnemonic` decision. Ordinary reading highlights are not copied into a card to satisfy balance.

Reuse another exact provider-scoped signature when the source supplies one. When the provider range supplies only one reusable signature, reject or report insufficient source-style diversity; never invent a style, recolor a fragment, or widen the source boundary merely to satisfy `E047` or silence `W101`. Completion criterion: every accepted styled card has at least two distinct provider-grounded signatures, every one-sided card surfaces `W101`, and every style remains byte-for-byte source-grounded.

## Deterministic check

When the source is a file, run:

```text
python -X utf8 scripts/validate_flashcard.py <draft.md> --source <source.md> --require-report
```

The source-aware gate rejects invented color/background fragments, one-signature styled cards, and cards that fail to reuse an exact styled fragment when the provider range contains one. It prints advisory warnings without returning failure when no error code is present. It complements manual checks for list depth, Callout meaning, highlight intent, and legal accuracy.
