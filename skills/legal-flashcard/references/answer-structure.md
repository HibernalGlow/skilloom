# Source-shaped card backs

Read this reference only in dedicated-card mode when a back is not a single short fact, direct contrast, or explicit closed set, or when its source range contains meaningful hierarchy, order, Callout, table, or Mermaid. This file selects the back carrier; [question-side-mermaid.md](question-side-mermaid.md) separately owns front retrieval skeletons, [card-design.md](card-design.md) remains authoritative for atomicity, and [protocol-contract.md](protocol-contract.md) owns the root IAL.

## Build the source slice

1. Isolate the smallest provider-scoped range that supports the card's one scoring axis. Record its exact wording, list depth and order, styled fragments, Callout role, table axes, and diagram nodes/edges. Completion criterion: every proposed back fragment and relationship has a source locator inside that range.
2. Remove structures that belong only to the surrounding chapter. A chapter overview Mermaid, multi-topic summary table, or neighboring Callout is not part of the card merely because it is nearby. Completion criterion: hiding the back leaves one answerable front, and revealing it does not introduce another independently gradable axis.
3. Prefer inheritance. Copy source wording, peer order, semantic depth, table headers/cells, Mermaid labels/edges, and substantive Callout category; change only the indentation needed to mount the content beneath the card root. Keep a shared subject or governing action with its compound objects in one source sentence, such as `论证为什么适用该规范及其后果`; a conjunction is not a child boundary. Transform the carrier only when the source carrier obscures this card-sized relationship. Completion criterion: every transformation has a one-to-one source mapping and no legal category, sequence, comparison, edge, or clause split was added.
4. Assign one primary carrier to each expected-answer statement. A list, table, and Mermaid that expose the same mapping are presentation alternatives, not separate candidates. Reject the redundant carrier as `duplicate` or `duplicate-summary` unless it creates a genuinely different retrieval direction under the variant rule. Completion criterion: no accepted summary merely unions accepted detail cards, and no accepted pair differs only by carrier.

Before rendering, run the **clause split**: an answer line longer than roughly 42 visible characters, or one that joins conditions, actions, effects, alternatives, exceptions, or contrast with `，并`、`，但`、`或者`、`；`、`分别`、`否则`, needs a governing parent and source-shaped child items. Keep one inseparable legal proposition together, but do not make the reader recover multiple recall axes from one long sentence. Completion criterion: every long or multi-clause answer has either a documented reason to remain atomic or a parent/child structure whose children each answer one sub-axis.

## Select the carrier

| Source relationship | Card-back carrier | Gate |
| --- | --- | --- |
| one short fact, direct two-item contrast, or explicit closed set | first-level unordered children | every child is a peer and directly answers the front |
| governing proposition with dependent conditions, reasons, exceptions, examples, or effects | nested unordered tree | each deeper item qualifies its parent; punctuation alone creates no depth |
| procedure, chronology, priority, or source-significant sequence | ordered list, nested when a step has detail | changing the order would change the rule or its retrieval value; source numbering alone is insufficient, and the front cannot invent an order cue to authorize numbering |
| inherent warning, exception, trap, or source quotation | `callout` or `blockquote` root | the semantic role survives without decorative relabeling |
| true cross-axis comparison, mapping, aligned period/number, or scope matrix | small table beneath one governing child | simultaneous row/column scanning is necessary; apply MarkNote's table-size gate |
| process, branching decision, or many-to-one relationship | small Mermaid beneath one governing child | every node and edge is source-grounded and the complete graph tests one axis |

Do not distribute formats for variety. Repeated unordered lists are correct when the material is a set of peers; ordered lists, Callouts, tables, and Mermaid earn their use only through the relationship above.

**Ordered-list hard gate:** When the front contains `步骤`, `顺序`, `依次`, `阶段`, `流程`, `先后`, or an explicit numbered step, inspect the source relationship before rendering. If the answer is a procedure, chronology, priority, or source-significant sequence, render its direct children as `1.`, `2.`, `3.` in the source order; nest explanatory details beneath the relevant numbered step. Do not use peer `-` bullets for a sequence merely because the source was parsed as bullets. The validator emits `E078` when a sequence front has neither ordered children nor a genuinely necessary table/Mermaid carrier.

The normative structures below demonstrate alternative carrier decisions. Do not emit both the ordered and Mermaid versions of the same fact in one deck merely because both templates exist.

## Normative structures

### Nested semantic tree

```markdown
- **法律责任的竞合**{: style="color: var(--b3-font-color10);"}产生机制是什么？ #法考/理论法/法理学/法律责任竞合/产生机制# #闪卡/优先级/P2#
    - **机制**{: style="color: var(--b3-font-color10);"}：不同的法律**规范**{: style="color: var(--b3-font-color10);"}从不同角度对**社会关系**{: style="color: var(--b3-font-color10);"}加以调整。
        - 由于法律**规范**{: style="color: var(--b3-font-color10);"}的**抽象性**以及**社会关系**{: style="color: var(--b3-font-color10);"}的**复杂性**。
        - 不同法律规范调整社会关系时可能产生**重合**{: style="color: var(--b3-font-color12);"}。
            - 从而发生法律**责任**{: style="color: var(--b3-font-color10);"}间的**竞合**{: style="color: var(--b3-font-color10);"}。
{: custom-dm-source-key="beisong-2026-mafeng-kd13-falv-zeren-jinghe" custom-dm-card-id="fc-theory-liability-concurrence-mechanism-recall-v1" custom-dm-card-schema="1" custom-dm-card-kind="basic" custom-dm-card-renderer="list" custom-qb-note-topic-id="theory-law-liability-concurrence-mechanism"}
```

The first-level proposition governs the reason-to-result branches. A detail that instead answers a different front becomes another card.

### Ordered source sequence

```markdown
- 司法三段论按推理顺序如何对应？ #法考/理论法/法理学/法适用/司法三段论# #闪卡/优先级/P1#
    1. **规范只能当大前提**{: style="color: var(--b3-font-color10);"}。
    2. 事实只能当小前提。
    3. **结论只能在第三步**{: style="color: var(--b3-font-color12);"}。
{: custom-dm-source-key="beisong-2026-mafeng-kd15-fa-shiyong" custom-dm-card-id="fc-theory-judicial-syllogism-sequence-recall-v1" custom-dm-card-schema="1" custom-dm-card-kind="basic" custom-dm-card-renderer="list" custom-qb-note-topic-id="theory-law-application-judicial-syllogism"}
```

Use Markdown `1.` numbering. Preserve a legally or mnemonically significant source order; do not turn an arbitrary numbered enumeration into a sequence merely to vary appearance.

### Comparison table inside a list root

```markdown
- 两类可归国家或集体所有的资源，其原则与例外如何对照？ #法考/理论法/宪法/基本经济制度/资源归属对照# #闪卡/优先级/P1#
    - 对应关系：
        | 资源类型 | **原则**{: style="color: var(--b3-font-color10);"} | **例外**{: style="color: var(--b3-font-color5);"} |
        | --- | --- | --- |
        | **森林、山岭、草原、荒地、滩涂** | 归国有 | 归集体 |
        | **农村和城市郊区的土地** | 归集体 | 归国家 |
{: custom-dm-source-key="beisong-2026-mafeng-kd31-jiben-jingji-zhidu" custom-dm-card-id="fc-theory-resource-ownership-principle-exception-table-v1" custom-dm-card-schema="1" custom-dm-card-kind="basic" custom-dm-card-renderer="list" custom-qb-note-topic-id="theory-law-economic-system-ownership-principle-exception-comparison"}
```

Keep a table only when both axes matter during recall. Preserve every relevant header, row label, cell, and mapping. If each row is merely a name plus a self-contained rule, use a semantic list. Follow MarkNote's table-size and real-header rules; a reviewed size exception belongs in working audit, not the saved deck.

### Answer-side Mermaid inside a list root

```markdown
- **司法三段论**{: style="color: var(--b3-font-color10);"}中规范、事实与裁判如何对应？ #法考/理论法/法理学/法适用/司法三段论# #闪卡/优先级/P1#
    - **三段论固定对应**{: style="color: var(--b3-font-color12);"}：
        ```mermaid
        flowchart LR
            A[大前提：法律规范] --> C{司法三段论}
            B[小前提：法律事实] --> C
            C --> D[结论：案件裁判]
        ```
{: custom-dm-source-key="beisong-2026-mafeng-kd15-fa-shiyong" custom-dm-card-id="fc-theory-judicial-syllogism-mapping-diagram-v1" custom-dm-card-schema="1" custom-dm-card-kind="basic" custom-dm-card-renderer="list" custom-qb-note-topic-id="theory-law-application-judicial-syllogism"}
```

Copy a suitable source Mermaid when it already expresses the same card-sized relation. Otherwise generate only from source-grounded nodes and edges. The governing answer child places this Mermaid after the answer boundary. The closing fence remains inside the list root and the one-line card IAL follows the complete root outside the fence.

### Callout or blockquote root

Use the normative Callout and blockquote examples in [card-design.md](card-design.md). Preserve a source Callout's category and title when its warning, exception, or trap is the retrieval role. A plain rule stays a list card even when emphasis would look attractive.

## Completion checklist

- The back carrier follows the source relationship, not a format quota.
- Wording, styles, order, container meaning, table mappings, and Mermaid edges are inherited or have an exact source mapping.
- The card still has one scoring axis; richer structure does not justify a summary card.
- Each expected-answer statement has one primary carrier; carrier-only duplicates are rejected.
- Ordered steps remain ordered, dependent branches remain nested, and peer sets remain peers.
- A table or Mermaid is fully contained beneath one governing answer child; a Callout or blockquote is the root container.
- The complete card root is followed by one schema 1 IAL on one physical line.
