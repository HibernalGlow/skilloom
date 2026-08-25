---
name: legal-flashcard
description: Generate DAMO-compatible legal flashcard Markdown in two explicit modes, export online or offline SiYuan documents with three IAL ranges, and batch-paste Markdown back into SiYuan through a real Protyle paste. Use during ordinary legal-note organization, SiYuan Markdown export or import, and explicit flashcard generation or review.
---

# Legal Flashcard

Use this skill as a mode router. Card generation outputs portable Markdown semantics and never writes Riff runtime state. The explicit SiYuan delivery route may create documents only through the bundled Protyle-paste script.

## Acquire SiYuan source

When the source is one or more `.sy` files, a SiYuan document directory, an offline workspace, a `20-整理` note, or a flashcard footer whose source is ambiguous, read [siyuan-export.md](references/siyuan-export.md) before routing. For dedicated-card mode, resolve and use a fresh export or matching `25-kramdown` snapshot as the style authority; `20-整理` is content navigation only. Run `scripts/export_siyuan_markdown.py` whenever the authoritative `.sy`/workspace source is available, even if a plain `20-整理` Markdown file opens first. Keep acquisition read-only and use portable IAL by default; use complete IAL when requested, and emit attribute-free Kramdown only when explicitly requested. Completion criterion: the working source has an authority class and export path, each requested source document has one exported Markdown file or ZIP member, and the source `.sy` files are unchanged.

## Deliver Markdown to SiYuan

When the user asks to paste or import one or many Markdown files into a SiYuan directory, read [siyuan-paste.md](references/siyuan-paste.md) and run `scripts/paste_siyuan_markdown.py`. An exported `25-kramdown\...\法考\客观\民诉` folder can be passed directly as the source; use the already-existing SiYuan `/法考/客观/民诉` as `--directory`, so the processing folders are not copied. Use `--title` for one explicit title or `--title-map` for batch titles; otherwise prefer the first H1 before the filename. Never replace this route with direct document-content upload when IAL must survive, because the bundled script delegates each write to a real Protyle paste event. Completion criterion: one batch receipt names every created document and its target path, or the failure names the completed prefix and snapshot.

## Route the request

1. Select **ordinary mode** when the request is note organization, summarization, formatting, or repair and does not explicitly ask for flashcards. Read [ordinary-mode.md](references/ordinary-mode.md). If the source provider is broad or incomplete, also read [topic-resolution.md](references/topic-resolution.md) to complete candidate topic mapping; do not load dedicated card rules. Completion criterion: the note preserves its source contract, records only review candidates with narrow topics or named gaps, and contains no formal `custom-dm-*` card IAL or runtime SRS field.
2. Select **dedicated-card mode** only when the user explicitly asks to make, generate, draft, export, or review flashcards/cards. On this route only, invoke the separately registered `legal-marknote` skill by name; do not assume the two skills share a parent directory. Then read [dedicated-mode.md](references/dedicated-mode.md), [card-design.md](references/card-design.md), [protocol-contract.md](references/protocol-contract.md), [marknote-integration.md](references/marknote-integration.md), [style-inheritance.md](references/style-inheritance.md) when a source note or source range exists, and [naming-and-placement.md](references/naming-and-placement.md) when a file, path, export, or saved deck is requested. If the authoritative export is genuinely plain or its provider palette is sparse, read legal-marknote's rich visual contract and build a semantic augmentation plan before drafting; a sparse export is a trigger to create a documented role dictionary, not a reason to repeat one source color. For medium/complex decks, the GoldQuest rich visual floor is mandatory: carry over provider-scoped styles, actively color every substantive answer line, keep repeated concepts and aliases on stable role colors, color every recurring role/concept occurrence consistently, and use the rich carrier/style plan with `--rich-style`; a deck that only reaches the per-card `E047` minimum is unfinished. `E074`/`E075`/`E076`/`E080`/`E081` rich-density errors, `E078` sequence-carrier errors, and `E079` case/exercise replay errors must be repaired; `W110`, `W116`, and `W117` remain review findings for local richness and auxiliary-style balance. Completion criterion: every source fact has a disposition and every accepted card has one scoring axis, a normative card-kind container, stable identity, source grounding, narrow note-topic provider, provider-scoped source-style inheritance or an explicit MarkNote style plan, every substantive answer line and recurring role occurrence passes the GoldQuest color-density rule, adjacent cards have sufficiently distinct palettes, deck-wide foreground usage is balanced, every sequence uses an ordered carrier, every case-derived card has a neutral reusable front or is rejected, and (when a file is requested) a source-derived title, filename, and dedicated destination exists, or generation stops with a named gap.
3. If the request mixes both modes, finish ordinary organization first and run the dedicated route only for the explicitly selected material. Completion criterion: the output labels the two result sets and no ordinary highlight is silently promoted to a card.

## Shared hand-off

- Treat the source range, existing cards, topic map, and requested card budget as inputs. Do not infer missing IDs, legal exceptions, dates, or source boundaries.
- Resolve incomplete provider maps before card drafting. The agent should self-complete from confirmed repository providers and existing multi-provider mounting patterns; only an evidence-backed unresolved mapping becomes a reported gap.
- Emit the final generation report and provenance as one parseable YAML fenced block (`report.candidates`, `report.accepted`, `report.rejected`, `report.rejection_reasons`, `source.note`, `source.protocol`), never as prose count or source/protocol sentences.
- Build the source-fact ledger, then draft candidates before acceptance. Apply `python -X utf8 scripts/validate_flashcard.py <draft.md> --source <source.md> --require-report` when the source is a file; omit only `--source` when no source file exists. Then report candidate, accepted, rejected counts and rejection reasons. Completion criterion: every ledger row has one disposition, the report reconciles to the candidate records and accepted cards, and the source-aware check passes whenever a source file exists.
- Keep `custom-dm-card-kind` (semantic card kind) separate from `custom-dm-card-renderer` (host container). Schema routing is explicit: read the versioned contract when a schema other than `1` is requested. Completion criterion: no card mixes schema versions or invents future runtime attributes.
- Use the card-unit standard from [card-design.md](references/card-design.md): one scoring axis, one specific expected answer or fixed closed set, a source-shaped back structure, short clozes, source traceability, and non-duplicative sibling variants. DAMO Markdown never emits Anki scheduling fields or runtime state. Completion criterion: the output contains semantic card content only, every complex back preserves its visible legal relationship, and no generated `问题：` or `答案：` prefix appears.

## References

- Ordinary mode: [ordinary-mode.md](references/ordinary-mode.md)
- Atomic topic mapping: [topic-resolution.md](references/topic-resolution.md)
- Dedicated mode: [dedicated-mode.md](references/dedicated-mode.md)
- Recall-unit gate, card kinds, normative examples, variants, and semantic deduplication: [card-design.md](references/card-design.md)
- Complex and linked card backs: read [answer-structure.md](references/answer-structure.md) when the source range contains hierarchy, order, a warning/exception, a true comparison matrix, a recall-sized diagram, or a source-grounded relation to another card or easily confused doctrine.
- Source authority and forced export: read [siyuan-export.md](references/siyuan-export.md) whenever a `20-整理` path, `25-kramdown` path, `.sy` source, SiYuan workspace, or ambiguous footer is involved.
- Rich visual calibration: read [rich-visual-mode.md](examples/rich-visual-mode.md) when drafting or reviewing a medium/complex dedicated deck; it is a passing GoldQuest-level shape, not a template to copy mechanically.
- Question-side Mermaid: read [question-side-mermaid.md](references/question-side-mermaid.md) only when the user requests a front diagram or a complex process, branch, role relation, or many-to-one mapping materially benefits from a retrieval skeleton.
- Portable fields, IAL boundary, and schema routing: [protocol-contract.md](references/protocol-contract.md)
- Source-relative P1-P4 assignment and distribution audit: [priority-calibration.md](references/priority-calibration.md)
- Validation findings and rejection taxonomy: [validation.md](references/validation.md)
- Dedicated-card MarkNote adapter: [marknote-integration.md](references/marknote-integration.md)
- Dedicated source-style map and byte-for-byte inheritance: [style-inheritance.md](references/style-inheritance.md)
- Filename, H1, destination folder, and collision routing: [naming-and-placement.md](references/naming-and-placement.md)
- Repeatable path/title check (including the leading `⚡` H1 role marker): `python -X utf8 scripts/validate_naming.py <output.md> --source <source.md>`
- External flashcard-skill audit: read [anki-compatibility.md](references/anki-compatibility.md) only when revising card-design rules or comparing another Anki/flashcard skill.
- Offline SiYuan `.sy` and batch Markdown ZIP export: [siyuan-export.md](references/siyuan-export.md)
- Real-Protyle single and batch Markdown paste: [siyuan-paste.md](references/siyuan-paste.md)
