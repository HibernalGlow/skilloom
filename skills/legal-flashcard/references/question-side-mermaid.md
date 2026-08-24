# Question-side Mermaid in list cards

Read this reference only in dedicated-card mode when the user requests a diagram on the question side or a complex process, branch, role relation, or many-to-one mapping would materially improve orientation before recall. This file owns the schema 1 front-visual boundary; [answer-structure.md](answer-structure.md) remains authoritative for answer carriers.

## Pass the front-visual gate

Use a question-side Mermaid only when all conditions hold:

1. The card is `basic/list`, the verbal question is independently answerable, and it ends in `？` or `?`.
2. The source relation is card-sized and genuinely structural. A plain definition, short rule, peer list, mnemonic, or single contrast stays text-first.
3. The diagram is a retrieval skeleton: it preserves the source-grounded actors, branches, or topology but replaces the tested labels with visible slots such as `①`, `②`, or `？`.
4. A child list follows the diagram and starts the answer side. The diagram is never the only content after the verbal question.
5. The diagram reduces orientation cost without adding another scoring axis. Every non-placeholder node and every edge maps to the provider-scoped source range.

Completion criterion: removing the diagram leaves a sufficient verbal question, hiding the answer child list leaves no tested label visible, and revealing the answer produces one grading decision.

## Mount the blocks

For a schema 1 list card, the root is the complete list block. The first list item's first paragraph is the verbal question. Non-list child blocks before the first child list remain on the question side; the first child list and its descendants are the answer side.

Mount a front Mermaid as a direct child block of the first list item, immediately before the answer child list. Give the Mermaid fence and the answer child list the same indentation. Attach the one-line IAL after the complete root list block.

```markdown
- **司法三段论**{: style="color: var(--b3-font-color10);"}中法律规范、法律事实与案件裁判如何对应？ #法考/理论法/法理学/法适用/司法三段论# #闪卡/优先级/P1#
    ```mermaid
    flowchart LR
        N[法律规范] --> P1[①]
        F[法律事实] --> P2[②]
        P1 --> R[③]
        P2 --> R
        classDef known fill:#e8f1ff,stroke:#2563eb,color:#0f172a,stroke-width:1.5px;
        classDef recall fill:#fff3bf,stroke:#d97706,color:#7c2d12,stroke-width:2px,stroke-dasharray:5 3;
        class N,F known;
        class P1,P2,R recall;
    ```
    - **完整对应**{: style="background-color: var(--b3-font-background11);"}：
        ```mermaid
        flowchart LR
            N[法律规范] --> P1[大前提]
            F[法律事实] --> P2[小前提]
            P1 --> R[案件裁判：结论]
            P2 --> R
            classDef known fill:#e8f1ff,stroke:#2563eb,color:#0f172a,stroke-width:1.5px;
            classDef answer fill:#e6fcf5,stroke:#059669,color:#064e3b,stroke-width:2px;
            class N,F known;
            class P1,P2,R answer;
        ```
{: custom-dm-source-key="beisong-2026-mafeng-kd15-fa-shiyong" custom-dm-card-id="fc-theory-judicial-syllogism-visual-recall-v1" custom-dm-card-schema="1" custom-dm-card-kind="basic" custom-dm-card-renderer="list" custom-qb-note-topic-id="theory-law-application-judicial-syllogism"}
```

The answer may instead be a semantic list when a second Mermaid would merely repeat it. When both sides use Mermaid, keep the same node IDs and topology: the front replaces only the tested labels, and the back fills those slots. Do not repeat the complete mapping again as a prose list or table.

## Style with Mermaid semantics

- Reuse a source Mermaid's direction, shapes, `classDef`, `class`, and link semantics when it already expresses the same card-sized relationship.
- For a generated front diagram, define and apply at least two semantic classes: `known` for source-grounded orientation nodes and `recall` for hidden slots. Use a stronger border or dashed stroke on `recall`; color alone must not carry the distinction.
- For a generated answer diagram, keep `known` and replace `recall` with `answer`. Reuse the front's node IDs, direction, and edge topology so the reveal is visually stable.
- Keep labels short enough to scan in the review window. Use shapes consistently for roles; do not add decorative icons, animations, gradients, theme initialization, or unrelated colors.
- Treat every `classDef` as presentation and every node/edge label as source-bearing content. Styles may improve hierarchy, but they cannot invent a legal category or imply an unsupported relation.

Completion criterion: every generated front Mermaid defines and uses both `known` and `recall`, the recall role remains distinguishable without hue, and any answer Mermaid preserves the front topology while replacing slots with source-grounded labels.

## Respect renderer boundaries

- Use question-side Mermaid only with `basic/list` in schema 1.
- In `blockquote` and `callout` cards, the first child is the question and later children are answers; a later Mermaid is therefore answer-side.
- A heading uses the heading as the question and following blocks as answers. Heading and superBlock are outside this skill's schema 1 output renderers.
- Keep `custom-dm-card-kind="basic"` and `custom-dm-card-renderer="list"`; Mermaid is a visual block, not a semantic card kind or renderer.
- If the host cannot preserve the direct-child order, move the Mermaid to the answer side or omit it. Do not invent an IAL field to force a front boundary.

Completion criterion: the front Mermaid precedes the first answer child list at the same block depth, no non-list front adjunct appears after that answer boundary, and no unsupported renderer or metadata field is introduced.
