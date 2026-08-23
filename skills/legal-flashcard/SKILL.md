---
name: legal-flashcard
description: Generate DAMO-compatible legal flashcard Markdown in two explicit modes. Use during ordinary legal-note organization to identify atomic flashcard candidates without emitting card containers, and use when the user explicitly asks to make, generate, draft, or export flashcards/cards to produce validated formal cards.
---

# Legal Flashcard

Use this skill as a mode router. It outputs portable Markdown semantics only; it does not call Riff, write SiYuan runtime state, or implement DAMO.

## Route the request

1. Select **ordinary mode** when the request is note organization, summarization, formatting, or repair and does not explicitly ask for flashcards. Read [ordinary-mode.md](references/ordinary-mode.md). If the source provider is broad or incomplete, also read [topic-resolution.md](references/topic-resolution.md) to complete candidate topic mapping; do not load dedicated card rules. Completion criterion: the note preserves its source contract, records only review candidates with narrow topics or named gaps, and contains no formal `custom-dm-*` card IAL or runtime SRS field.
2. Select **dedicated-card mode** only when the user explicitly asks to make, generate, draft, export, or review flashcards/cards. On this route only, invoke the separately registered `legal-marknote` skill by name; do not assume the two skills share a parent directory. Then read [dedicated-mode.md](references/dedicated-mode.md), [marknote-integration.md](references/marknote-integration.md), and [protocol-contract.md](references/protocol-contract.md). Choose `basic` for focused Q/A, `cloze` for a short deletion, and `mnemonic` for a source-grounded口诀 or other non-Q/A memory cue. Completion criterion: every accepted card has a validated root container, stable identity, source grounding, narrow note-topic provider, and MarkNote semantic anchor, or generation stops with a named gap.
3. If the request mixes both modes, finish ordinary organization first and run the dedicated route only for the explicitly selected material. Completion criterion: the output labels the two result sets and no ordinary highlight is silently promoted to a card.

## Shared hand-off

- Treat the source range, existing cards, topic map, and requested card budget as inputs. Do not infer missing IDs, legal exceptions, dates, or source boundaries.
- Resolve incomplete provider maps before card drafting. The agent should self-complete from confirmed repository providers and existing multi-provider mounting patterns; only an evidence-backed unresolved mapping becomes a reported gap.
- Draft candidates before acceptance. Apply `python -X utf8 scripts/validate_flashcard.py <draft.md> --require-report` to the dedicated draft; then report candidate, accepted, rejected counts and rejection reasons. Completion criterion: the report reconciles to the number of candidate records and accepted cards.
- Keep `custom-dm-card-kind` (semantic card kind) separate from `custom-dm-card-renderer` (host container). Schema routing is explicit: read the versioned contract when a schema other than `1` is requested. Completion criterion: no card mixes schema versions or invents future runtime attributes.
- Use Anki-like note design only as a content heuristic: one recall target per card, short clozes, source traceability, and sibling variants. DAMO Markdown never emits Anki scheduling fields or runtime state. Completion criterion: the output contains semantic card content only.

## References

- Ordinary mode: [ordinary-mode.md](references/ordinary-mode.md)
- Atomic topic mapping: [topic-resolution.md](references/topic-resolution.md)
- Dedicated mode: [dedicated-mode.md](references/dedicated-mode.md)
- Fields, containers, card types, variants, and schema routing: [protocol-contract.md](references/protocol-contract.md)
- Validation findings and rejection taxonomy: [validation.md](references/validation.md)
- Dedicated-card MarkNote adapter: [marknote-integration.md](references/marknote-integration.md)
- Anki-like compatibility boundary and local search result: [anki-compatibility.md](references/anki-compatibility.md)
