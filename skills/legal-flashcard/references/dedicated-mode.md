# Dedicated-card mode

Read this file only after the user explicitly requests flashcards. First invoke the separately registered `legal-marknote` skill by name, then read [marknote-integration.md](marknote-integration.md) and, when a source note or source range exists, [style-inheritance.md](style-inheritance.md). This is a stricter output contract layered on top of `legal-marknote` or `legal-goldquest`; those skills remain the source of truth for legal formatting and question preservation.

## Deterministic workflow

1. Establish the source range, source key, known providers, existing cards, source knowledge tags, flashcard priorities, and any explicitly requested card budget. When the user requests a file, path, export, or saved deck, resolve its destination and source-derived filename/H1 by following [naming-and-placement.md](naming-and-placement.md). Resolve atomic note-topic IDs by following [topic-resolution.md](topic-resolution.md), including the broad-provider guard: distinct recall axes require distinct confirmed child providers. Completion criterion: every source range has one atomic topic ID or a named mapping gap, every accepted range has a source-grounded knowledge tag and exactly one priority tag, and any requested file has a recorded dedicated destination plus source-derived filename/H1.
2. Build the source-fact ledger from [card-design.md](card-design.md) before drafting. Include each independently testable rule, fixed list, distinction, exception, trap, date, case, and source-written mnemonic, including facts found only in examples or answer explanations. Completion criterion: every fact has one source locator, recall axis, provider, tags, and disposition slot; nothing is silently omitted because it appeared late in the source.
3. Run source grounding and build the provider-scoped source-style map required by [style-inheritance.md](style-inheritance.md). Every answer, citation, cloze target, mnemonic segment, and inherited style must be traceable to supplied material. Mark uncertain statutes, dates, exceptions, and cases as `待核实`; do not fill them from memory. Completion criterion: every ledger fact has a source locator or blocking note, and every candidate range has an exact style map or a named `missing-style-source` gap.
4. Draft candidates by applying the recall-unit gate and normative examples in [card-design.md](card-design.md). Split definition, composition, status, policy, condition, procedure, exception, legal effect, distinction, and historical source into separate cards when they can be graded independently. Keep a multi-item answer only for one fixed closed set on one scoring axis. Completion criterion: every candidate has one expected-answer statement, one semantic kind, one stable parent/variant identity, and no answer child introduces a second scoring axis.
5. Compare existing card IDs, normalized fronts, expected-answer statements, and answer fact sets within the same source range. Reject a summary that only unions accepted answers as `duplicate-summary`; retain a summary only when it tests a new relation, contrast, application, or source-written mnemonic. Completion criterion: every candidate has one accepted or rejected disposition from [validation.md](validation.md), and no accepted pair has equivalent prompts and expected answers.
6. Render accepted cards using [card-design.md](card-design.md) and [protocol-contract.md](protocol-contract.md). Default to `basic/list`: write the question directly as the root list item, end it with `？` or `?`, and write direct answer children without labels. Use `cloze/mark` for one short deletion and `mnemonic/list` for an exact source-written cue with an auditable mapping. Use `blockquote` or `callout` only when quotation, warning, exception, or trap semantics require it. Put knowledge and priority tags on the front/cue line, then attach the complete IAL to the container root on one physical line. Completion criterion: no generated item begins with `问题：` or `答案：`, every basic front ends in a question mark, and each card matches one normative kind example.
7. Apply the MarkNote adapter and source-style map, then run `scripts/validate_flashcard.py <draft.md> --source <source.md> --require-report` when the source is a file. Manually preview each card front in isolation before reading its back; verify the expected answer is specific, the prompt does not leak it, and the card is not a summary duplicate. If no explicit budget was supplied, keep all valid covered candidates; do not use `over-budget` as a convenience filter. Apply an explicit budget only after this pass. Completion criterion: the checker exits 0, every highlighted cloze/mnemonic span and every color/background fragment is source-grounded, every ledger row has a final disposition, and the report reconciles candidate, accepted, and rejected counts.
8. Produce a clean delivery: H1, source-derived grouping headings only when useful, accepted card containers, one count line, an optional compact rejection line, and one final source/protocol line. Keep the source-fact ledger, source key, provider budget, tag rationale, card-kind mix, style audit, and rejection details in working context. Do not call Riff or mutate runtime state. Completion criterion: the last nonblank line is exactly `原笔记：[[<源笔记路径>]] · 协议：DAMO 闪卡 schema 1`, and deleting the cards plus footer leaves only the H1 and useful source-derived grouping headings, with no audit preamble.

## Rendering rules

- Basic cards use one direct question root `- ...？` and unlabeled indented answer items. Attach the card IAL to that root list block, outside any code fence.
- Reuse source-styled fragments exactly within their provider range. A plain source range may remain plain; do not color a question or answer merely to make every card look uniform.
- Cloze cards use `==明确关键术语==` as the deletion target. Keep the cloze short; never highlight an entire conclusion sentence.
- Mnemonic cards do not require a fake question. Put the complete source-grounded口诀 or cue in a visible `==...==` highlight. When each sentence contributes a character or segment, highlight the complete口诀, the corresponding character/segment in every source sentence, and the assembled result; retain the mapping order. Use a child list for the sentence-to-character mapping when it improves auditability.
- A blockquote or callout must carry a substantive property (for example an exception or warning), not decoration.
- Preserve existing mark cards. Do not rewrite them as basic/list cards.
- A new variant ID is `<parent-business-id>-<stable-variant-key>`, such as `-recall-v1`, `-cloze-v1`, or `-mnemonic-v1`. Preserve existing stable IDs; variants share the parent prefix and never use a block ID, Riff ID, or database row ID.
- `custom-qb-note-topic-id` is the card's one narrow atomic provider ID. If a broad file-level ID is the only direct attribute, first perform the self-completion workflow in [topic-resolution.md](topic-resolution.md); stop with `missing-topic` only after the confirmed catalog, sibling multi-provider patterns, and source headings fail to establish a stable mapping. Never attach the broad ID to every card merely to pass validation.
- Keep tags as visible Markdown content on the root line, never as IAL attributes or detached paragraphs. Preserve the source's knowledge-tag vocabulary verbatim; do not require a particular namespace or hierarchy. Add exactly one priority tag: `#闪卡/优先级/P1#` through `#闪卡/优先级/P4#`; keep priority separate from knowledge tags. If the supplied material provides no source-grounded knowledge tag, report `missing-tag`; if no priority can be justified, report `missing-priority` instead of inventing one.

## Clean delivery

Default footer with no rejection:

```text
生成报告：候选 6；接受 6；拒绝 0。
原笔记：[[客观/02-背诵卷/理论法/2026-马峰/20-整理/02-考点25-宪法的制定]] · 协议：DAMO 闪卡 schema 1
```

Footer with rejection:

```text
生成报告：候选 8；接受 6；拒绝 2。
拒绝：duplicate 1；missing-topic 1。
原笔记：[[客观/02-背诵卷/理论法/2026-马峰/20-整理/02-考点25-宪法的制定]] · 协议：DAMO 闪卡 schema 1
```

Do not precede the cards with a source/protocol/style manifest. The combined source/protocol line is the only default provenance note and must be the last nonblank line. Supply expanded provider allocation, style audit, or rejection diagnostics only when the user explicitly asks for them, and keep such diagnostics outside the saved flashcard Markdown unless the user asks to embed them.
