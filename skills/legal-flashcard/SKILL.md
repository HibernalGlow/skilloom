---
name: legal-flashcard
description: Generate DAMO-compatible legal flashcard Markdown in two explicit modes. Use during ordinary legal-note organization to identify atomic flashcard candidates without emitting card containers, and use when the user explicitly asks to make, generate, draft, or export flashcards/cards to produce validated formal cards.
---

# Legal Flashcard

Use this skill as a mode router. It outputs portable Markdown semantics only; it does not call Riff, write SiYuan runtime state, or implement DAMO.

## Route the request

1. Select **ordinary mode** when the request is note organization, summarization, formatting, or repair and does not explicitly ask for flashcards. Read [ordinary-mode.md](references/ordinary-mode.md). If the source provider is broad or incomplete, also read [topic-resolution.md](references/topic-resolution.md) to complete candidate topic mapping; do not load dedicated card rules. Completion criterion: the note preserves its source contract, records only review candidates with narrow topics or named gaps, and contains no formal `custom-dm-*` card IAL or runtime SRS field.
2. Select **dedicated-card mode** only when the user explicitly asks to make, generate, draft, export, or review flashcards/cards. On this route only, invoke the separately registered `legal-marknote` skill by name; do not assume the two skills share a parent directory. Then read [dedicated-mode.md](references/dedicated-mode.md), [card-design.md](references/card-design.md), [protocol-contract.md](references/protocol-contract.md), [marknote-integration.md](references/marknote-integration.md), [style-inheritance.md](references/style-inheritance.md) when a source note or source range exists, and [naming-and-placement.md](references/naming-and-placement.md) when a file, path, export, or saved deck is requested. Completion criterion: every source fact has a disposition and every accepted card has one scoring axis, a normative card-kind container, stable identity, source grounding, narrow note-topic provider, provider-scoped source-style inheritance, and (when a file is requested) a source-derived title, filename, and dedicated destination, or generation stops with a named gap.
3. If the request mixes both modes, finish ordinary organization first and run the dedicated route only for the explicitly selected material. Completion criterion: the output labels the two result sets and no ordinary highlight is silently promoted to a card.

## Shared hand-off

- Treat the source range, existing cards, topic map, and requested card budget as inputs. Do not infer missing IDs, legal exceptions, dates, or source boundaries.
- Resolve incomplete provider maps before card drafting. The agent should self-complete from confirmed repository providers and existing multi-provider mounting patterns; only an evidence-backed unresolved mapping becomes a reported gap.
- Build the source-fact ledger, then draft candidates before acceptance. Apply `python -X utf8 scripts/validate_flashcard.py <draft.md> --source <source.md> --require-report` when the source is a file; omit only `--source` when no source file exists. Then report candidate, accepted, rejected counts and rejection reasons. Completion criterion: every ledger row has one disposition, the report reconciles to the candidate records and accepted cards, and the source-aware check passes whenever a source file exists.
- Keep `custom-dm-card-kind` (semantic card kind) separate from `custom-dm-card-renderer` (host container). Schema routing is explicit: read the versioned contract when a schema other than `1` is requested. Completion criterion: no card mixes schema versions or invents future runtime attributes.
- Use the card-unit standard from [card-design.md](references/card-design.md): one scoring axis, one specific expected answer or fixed closed set, short clozes, source traceability, and non-duplicative sibling variants. DAMO Markdown never emits Anki scheduling fields or runtime state. Completion criterion: the output contains semantic card content only and no generated `问题：` or `答案：` prefix.

## References

- Ordinary mode: [ordinary-mode.md](references/ordinary-mode.md)
- Atomic topic mapping: [topic-resolution.md](references/topic-resolution.md)
- Dedicated mode: [dedicated-mode.md](references/dedicated-mode.md)
- Recall-unit gate, card kinds, normative examples, variants, and semantic deduplication: [card-design.md](references/card-design.md)
- Portable fields, IAL boundary, and schema routing: [protocol-contract.md](references/protocol-contract.md)
- Validation findings and rejection taxonomy: [validation.md](references/validation.md)
- Dedicated-card MarkNote adapter: [marknote-integration.md](references/marknote-integration.md)
- Dedicated source-style map and byte-for-byte inheritance: [style-inheritance.md](references/style-inheritance.md)
- Filename, H1, destination folder, and collision routing: [naming-and-placement.md](references/naming-and-placement.md)
- Repeatable path/title check (including the leading `⚡` H1 role marker): `python -X utf8 scripts/validate_naming.py <output.md> --source <source.md>`
- External flashcard-skill audit: read [anki-compatibility.md](references/anki-compatibility.md) only when revising card-design rules or comparing another Anki/flashcard skill.
