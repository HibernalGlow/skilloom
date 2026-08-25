# Flashcard unit and card-type standard

Read this file only in dedicated-card mode. It is the source of truth for recall-unit design and the normative Markdown shape of each schema 1 card kind. Use [protocol-contract.md](protocol-contract.md) for fields and IAL syntax; use [validation.md](validation.md) for rejection codes.

## Build the source-fact ledger

Before drafting, enumerate every independently testable source proposition, fixed closed list, distinction, exception, trap, date, **case-derived new rule/application**, and source-written mnemonic in a working ledger. Treat the original case narrative, party names, fact chronology, and question stem as source evidence, not as flashcard targets. Create a card only when the case contributes a new legal rule, exception, distinction, application path, or trap that is independently reusable; otherwise record `case-narrative` and reject it. Record:

An original exercise front is never itself a card target. Do not copy a source question containing its case parties, option labels, or exercise wording into a formal card. If the exercise reveals a reusable rule, rewrite the front as a party-neutral legal relation (for example, `“代为调解”的特别授权包括哪些行为？`), retain only the general rule, and record the original exercise as `case-narrative` evidence. If that rewrite would lose the point, reject the candidate instead of replaying the question.

| Field | Required value |
| --- | --- |
| `fact-key` | stable working key within the source range |
| `source-locator` | heading plus line, block, page, or quoted fragment |
| `recall-axis` | one of definition, composition, status, policy, condition, procedure, exception, legal-effect, distinction, authority/date, mnemonic, or another named single relation |
| `topic-id` | one confirmed atomic note-topic provider or `missing-topic` |
| `tags` | one source-grounded knowledge tag and one P1-P4 priority, or a named gap |
| `disposition` | candidate ID, `duplicate`, `duplicate-summary`, `unsupported`, `uncertain-law`, `ambiguous-boundary`, `missing-topic`, `missing-tag`, `missing-priority`, or `over-budget` |

Keep the ledger in working context; do not emit it as a deck preamble. Completion criterion: every independently testable source proposition has exactly one disposition, and every accepted card points back to one or more adjacent ledger rows on the same recall axis.

If the user did not provide a numerical card budget, do not reject a valid source fact as `over-budget`. Source completeness controls the quantity; only duplicate, unsupported, uncertain, missing metadata, or an explicit user budget can remove a candidate. Apply a budget cap only after the ledger and candidate-coverage pass.

## Pass the recall-unit gate

A card is atomic when all of these checks pass:

1. **One scoring axis.** The front asks for one relation. Definition, composition, status, policy, condition, procedure, exception, legal effect, distinction, and historical source are separate axes unless the source defines them as one inseparable formula.
2. **Direct answers.** Every child item answers the exact front. Remove an unsolicited definition from a status card and remove a policy from a composition card.
3. **One grading decision.** A learner can mark the card correct or incorrect against one expected fact or one fixed closed set. Split independently gradable branches.
4. **Closed-list exception.** Multiple child items may remain together only when the front names the closed class or cardinality and every item is a peer on the same axis, such as “三大基本原则”. Four items is a ceiling, not evidence of atomicity.
5. **Prompt sufficiency.** The front supplies enough legal context to identify one answer without leaking it. Avoid vague prompts such as “有哪些要点？” when several dimensions are possible.
6. **Answer economy.** Keep the direct answer before optional context. If an answer needs explanation from another axis, make another card.
7. **Semantic back structure.** Reuse the source note's wording, hierarchy, order, and suitable containers. A simple answer may stay as first-level children. Route a non-simple back through [answer-structure.md](answer-structure.md) when the source contains hierarchy, sequence, warning/exception, a true comparison matrix, or a recall-sized relationship diagram. A procedure, chronology, priority, or source-significant sequence uses ordered `1.` children; a peer set remains unordered.

Completion criterion: for every accepted card, write one short expected-answer statement; no other accepted card has the same statement or a superset that merely summarizes it, and every non-simple back uses the source-grounded structure selected by [answer-structure.md](answer-structure.md).

## Choose the semantic kind

| Kind | Use when | Default renderer | Front/back behavior |
| --- | --- | --- | --- |
| `basic` | A direct question has one specific answer or one fixed closed set. | `list` | The first list-item paragraph is the question and ends in `？` or `?`; its child list starts the answer. Do not add `问题：` or `答案：`. |
| `cloze` | Hiding one short term, date, actor, threshold, or contrast is more natural than asking a question. | `mark` | Root is a complete source-grounded statement with one short `==target==`; add context only when needed to disambiguate. |
| `mnemonic` | The source supplies a口诀, compact sequence, or auditable character/segment mapping. | `list` | Root names the exact recall subject and highlights the complete source-written cue; children decode its segments. It is not a fake question. |

Use `blockquote` only when the quotation itself is the retrieval unit. Use a `callout` root when an inherent warning, exception, trap, or decisive boundary is the whole retrieval unit; otherwise keep the list root and place a short nested Callout around the local exception, conclusion peak, or memory relation. Changing renderer never changes `custom-dm-card-kind`.

## Normative schema 1 examples

Apply the per-card gate in [style-inheritance.md](style-inheritance.md#card-unit-style-gate) to every example shape: a styled accepted card needs at least two exact source-grounded signatures, and a medium/complex rich card must satisfy GoldQuest line-level semantic color density. A missing foreground or background/highlight dimension remains advisory only when the source/style plan genuinely lacks that dimension.

### Basic/list

```markdown
- 立法的三大**基本原则**{: style="color: var(--b3-font-color12);"}是什么？ #法考/理论法/立法法/基本原则# #闪卡/优先级/P1#
    - **科学性原则**{: style="color: var(--b3-font-color8);"}。
    - **民主性原则**{: style="color: var(--b3-font-color11);"}。
    - **合法性原则**{: style="color: var(--b3-font-color12);"}。
{: custom-dm-source-key="beisong-2026-mafeng-kd23-lifafa" custom-dm-card-id="fc-theory-lifafa-principles-three-recall-v1" custom-dm-card-schema="1" custom-dm-card-kind="basic" custom-dm-card-renderer="list" custom-qb-note-topic-id="theory-law-legislation-basic-principles"}
```

The first list item is the front container. Its first paragraph is the verbal question and its child list starts the back. A question-side Mermaid may appear between them only through [question-side-mermaid.md](question-side-mermaid.md). The adjacent IAL belongs to the complete root list block.

### Cloze/mark

```markdown
- 土地**所有权不得转让**{: style="color: var(--b3-font-color10);"}，可以转让的是土地==使用权==。 #法考/理论法/宪法/土地权利转让# #闪卡/优先级/P1#
{: custom-dm-source-key="beisong-2026-mafeng-kd31-jiben-jingji-zhidu" custom-dm-card-id="fc-theory-xianfa-land-transfer-cloze-v1" custom-dm-card-schema="1" custom-dm-card-kind="cloze" custom-dm-card-renderer="mark" custom-qb-note-topic-id="theory-law-economic-system-prediction-quiz-land-transfer"}
```

The hidden span is the answer. Keep surrounding words sufficient to distinguish it from land ownership.

### Mnemonic/list

```markdown
- **绝对归国家所有**{: style="color: var(--b3-font-color10);"}的资源口诀：==国有城土海水矿== #法考/理论法/宪法/资源归属口诀# #闪卡/优先级/P1#
    - 原文：**国有城土海水矿**{: style="color: var(--b3-font-color10);"}。
    - ==城土==：城市土地。
    - ==海水矿==：海域、水流、矿藏。
{: custom-dm-source-key="beisong-2026-mafeng-kd31-jiben-jingji-zhidu" custom-dm-card-id="fc-theory-xianfa-ownership-state-mnemonic-v1" custom-dm-card-schema="1" custom-dm-card-kind="mnemonic" custom-dm-card-renderer="list" custom-qb-note-topic-id="theory-law-economic-system-ownership-state"}
```

Every highlighted cue and decoded segment must occur verbatim in the source provider range. Preserve a source-written sequence; do not create a shorter reordered “组合”. When each source sentence contributes one character or segment, highlight that exact contribution in every mapping child.

### Optional blockquote and callout renderers

```markdown
> 社会主义公共财产的宪法保护表述是什么？ #法考/理论法/宪法/公共财产保护# #闪卡/优先级/P2#
>
> - **社会主义**{: style="background-color: var(--b3-font-background11);"}的**公共财产**{: style="color: var(--b3-font-color10);"}神圣不可侵犯。
{: custom-dm-source-key="beisong-2026-mafeng-kd31-jiben-jingji-zhidu" custom-dm-card-id="fc-theory-xianfa-public-property-quote-v1" custom-dm-card-schema="1" custom-dm-card-kind="basic" custom-dm-card-renderer="blockquote" custom-qb-note-topic-id="theory-law-economic-system-public-property"}
```

```markdown
> [!WARNING] 土地所有权能否转让？
> #法考/理论法/宪法/土地权利转让# #闪卡/优先级/P1#
>
> - 土地**所有权不得转让**{: style="color: var(--b3-font-color10);"}；可以转让的是**土地使用权**{: style="background-color: var(--b3-font-background11);"}。
{: custom-dm-source-key="beisong-2026-mafeng-kd31-jiben-jingji-zhidu" custom-dm-card-id="fc-theory-xianfa-land-transfer-warning-v1" custom-dm-card-schema="1" custom-dm-card-kind="basic" custom-dm-card-renderer="callout" custom-qb-note-topic-id="theory-law-economic-system-prediction-quiz-land-transfer"}
```

Use these root renderers when losing the quotation, warning, exception, trap, or decisive-boundary role would weaken retrieval. `list` remains the default root, but its back should use a nested Callout when one local semantic peak deserves isolation.

## Deduplicate and route variants

- Compare normalized fronts, expected-answer statements, and answer fact sets within the same source range and against existing cards.
- Reject a card as `duplicate-summary` when its back is only the union or restatement of accepted cards. Keep it only when it tests a new relation, contrast, application, or source-written mnemonic.
- Keep basic, cloze, and mnemonic variants only when each creates a different retrieval direction for the same parent fact. Record a working `parent-id` and stable `variant-key`; render the ID as `<parent-id>-<variant-key>`, for example `fc-theory-xianfa-land-transfer-recall-v1` and `fc-theory-xianfa-land-transfer-cloze-v1`.
- Preserve existing stable IDs and legacy mark cards. Apply the parent/variant pattern to new variants; do not rename old cards merely for consistency.

Completion criterion: every accepted variant has a distinct retrieval direction, every summary whose facts already exist is rejected or justified by a new scoring axis, and no two accepted cards expect the same answer from equivalent prompts.

## Coverage gate

Count candidates from the source-fact ledger, not from the number of drafted cards. Give every ledger fact one disposition: accepted card, named duplicate/duplicate-summary, unsupported or uncertain-law, missing-topic/style/tag/priority, or explicit-budget rejection. A section containing a definition, fixed list, mechanism, solution, sanction, example, and mnemonic therefore yields separate candidate rows unless the source makes them one inseparable relation. Completion criterion: no ledger row is silently absent and the report's candidate count equals the number of ledger rows with a card ID or explicit rejection.
