# Wrong-answer Case card (cc-1)

Read this reference in dedicated-card mode when the retrieval unit is a question the learner already answered wrong (错题/重犯/题库记录) and the file must work as a question-bank exercise *and* as a flashcard. Everything in [protocol-contract.md](protocol-contract.md), [card-design.md](card-design.md), [answer-structure.md](answer-structure.md), [style-inheritance.md](style-inheritance.md) and [validation.md](validation.md) still applies; this file adds the Case overlay.

## One question = one card

The card root is the compressed stem item. Its `> [!SELECTION]` option carrier stays on the **front**, and its first child list is the **back**. Do not emit a second "exercise block": the same list is what the question bank indexes, so 做题, grading, wrong-answer history and FSRS review all read one block.

```text
##### [考点·题型] N.
{: custom-qb-id="<source-qb-id>-cc" custom-qb-type="multiple" custom-qb-answer="A,B,C" custom-qb-question-topic-ids="…"}

- ⚖️ <压缩题干：决定性事实 + 触发原错的事实>，<需要作答的问句>？ #法考/<科>/<考点># #题库/题型/<多选># #题库/年份/<年>金题# #闪卡/优先级/P#

  > [!SELECTION]
  >
  > - [ ] A. <原选项逐字>
  > - [ ] B. <原选项逐字>

    - 正确答案：ABC。
    - ✅ <可选项短裁决，≤20 可见字符>
      - <该项为什么成立：源解析的关键规则，复用题源 emoji（⭐ 特别授权 / 📝 一般授权 / 📉 视为一般授权）>
    - ❌ <误选项短裁决>
      - <规则> / <错因：这次为什么又选它> / <判断链>
      - 判断链：

        ```mermaid
        flowchart LR
            …
            M["误判入口：<学习者稳定的越界理由>"]:::wrong --> J
            classDef wrong fill:#fdecec,stroke:#c0392b,color:#7b241c,stroke-dasharray:4 3;
        ```

        ![InkLoom 动图：<题源已有的动图名>](<题源已有的 avif 链接>)

        > [!WARNING] <陷阱标题，plain，≤13 可见字符>
        >
        > - <真实误选记录>🧨：<误选项>
        > - <边界一句话>
        > - 口诀📌：<来自 06-口诀 或题源的口诀/技巧原句>

      - 决断口径：<一句>
        - <一句>

    ```yml
    cc:
      schema: cc-1
      qb_id: <本题块 id>
      source_qb_id: <原题 id>
      tier: flame | reinforce
      trap: <陷阱短语>
      decision: <决策点短语>
      mnemonic: "<口诀原句>"
      mnemonic_from: "<06-口诀 或题源路径#行号>"
      animation: "<题源动图文件名>"
      history: "<真实作答：日期 选项>"
    ```
{: custom-dm-source-key="…" custom-dm-card-id="…" custom-dm-card-schema="1" custom-dm-card-kind="basic" custom-dm-card-renderer="list" custom-qb-note-topic-id="…"}
```

## Why the front keeps its options

SiYuan hides a card's answer with `.card__block--hideli .li[custom-riff-decks] > .list`, i.e. only the root item's child **lists**. A Callout at the root item's own column is therefore front content, which is why the options live in `> [!SELECTION]` and the reasoning lives in the first child list. This needs two question-bank scanner capabilities (present in the current Damophus build, covered by `scanner.test.ts`):

- the kramdown stripper removes a block's inline `{: id="…" updated="…"}` after a **whole** marker chain (`> - `, `  - `), and blanking a standalone IAL line keeps that line's `> ` prefix, otherwise one callout splits into one quote per option and every option disappears;
- a marked card block is split at its first child list, so the stem keeps the 题干 plus the option carrier and the child list onward becomes the solution — the answer never appears in the practice stem.

If a build lacks them, the exercise silently indexes zero options; re-check with the plugin's own scanner against `/api/block/getBlockKramdown` output, not against the authored `.md`.

## Case rules the generic card contract does not state

1. **Verbatim options, one carrier.** Keep every option exactly as the source wrote it; never rewrite a distractor, because the distractor is the diagnostic signal. A top-level task list directly above the 正确答案 line merges into one CommonMark list and loses all options — keep the carrier.
2. **The front carries zero hints.** No `作答：＿＿＿`, no `先想清楚…`, no 考点 name, no answer word. The front is the compressed stem plus the question; `E092` still caps it at 70 visible characters, and `E079`'s "no exercise replay" is satisfied by compression and role-neutral parties (原告/被告/担保人/申请人), not by deleting the trap facts.
3. **Analyze every option the learner did not already get right.** A stable mis-selection needs 规则 + 错因 + 判断链; an option that was once *missed* needs the reason for the doubt ("把签收当成当事人本人的事"); an option selected correctly every time gets one line and the note 不必重记. Skipping a missed option is the same defect as skipping a wrong one.
4. **The back carries its own reasoning Mermaid** with the learner's 误判入口 as a `wrong`-classed node feeding the decision node, and it keeps the provider's own visual: when the source range already has an InkLoom animation or diagram for this rule, copy that image under the governing child instead of drawing a rival one (`W126`).
5. **Carry the mnemonic, don't invent one.** Search the 06-口诀 corpus and the provider for an existing 口诀/做题技巧 sentence, quote it verbatim inside the trap Callout, and record its path in the `yml` block (`mnemonic`, `mnemonic_from`). `W128` still wants a dedicated `mnemonic` card when the corpus cue is the retrievable unit; that is a second card, not a rewrite of this one.
6. **Attributes split three ways.** The root IAL carries only the six schema-1 fields; Case identity, tier, trap, decision, mnemonic source, animation and attempt history live in the last visible ` ```yml ` block; runtime state (`custom-riff-decks`, due, interval, review log) is never written.
7. **Tags live on the front line.** `E097` counts tag characters, so the 题库 题型/年份 tags sit on the front with the knowledge and priority tags instead of on the 正确答案 line.
8. **`reinforce` cards get a second question.** When two wrong attempts fell into different traps, emit a variant card whose changed fact pattern flips the answer, and name the flip on the back.

## Measured gate behaviour for this shape

- **One ` ```yaml ` fence per file** (`E070`): the deck report owns that name, so the Case metadata fence is ` ```yml `; `source.protocol` must be exactly `"DAMO 闪卡 schema 1"`.
- **`E041` is substring-based and coloring is longest-match.** A provider term that only ever occurs inside a longer colored term (`程序` in `执行程序`, `特别授权` in `特别授权⭐`), inside a fence, or inside the option carrier is reported as a dropped style — give it one independent colored occurrence or reword, and never place an emoji directly after a term whose emoji-suffixed twin exists in the dictionary.
- **`E086` exempts the `SELECTION` carrier** by contract: it is front space, not a back Callout. Any other Callout still has to sit deeper than the direct answer items.
- **`E074` skips a carrier image line**; every other answer line of 14+ visible characters needs its provider anchor.
- **`E027`**: at most four direct answer items — the 正确答案 line plus three verdicts; merge verdicts that share one verdict (`✅ A、C 可以代为`) and keep the per-option detail beneath them.
- **Sparse provider palettes** still need three short background anchors (`E062`) and four auxiliary families (`E060`): promote the term's own background variant rather than inventing a color, and keep one style per term (`E076`).
- **`E132`**: verdict prefixes are not enough — anchor semantic emoji inside the content next to the concept (`处分实体权利须⭐特别授权`, `两次误选都多它🧨`), and keep the front emoji off the back (`E100`).
- **`E098`/`E134`**: a blank line before every directive, and one continuous `> ` run per quoted passage.

## GoldQuest exemptions of a Case card

Recorded, not defects: `E822` (题库 tags move to the front line), `E802` (`custom-qb-note-topic-id` lives in the card IAL), `E301`/`E302` (the `list` root needs a bare ` ```mermaid ` child and a ` ```yml ` block). The stem and options still carry no conclusion colors and no `题干：`/`答案：` labels.

## Completion criterion

One wrong-answer record produces one heading, one card root, one option carrier with verbatim choices, and one back that answers every option the learner did not reliably pick; the front is hint-free; the back carries the reasoning Mermaid with the learner's own 误判入口, the provider's existing animation, and the corpus 口诀 with its path; the IAL holds only the six schema-1 fields; `validate_flashcard.py --require-report --rich-style --all` reports zero `E`; and `/api/block/getBlockKramdown` of the pasted document scans into the expected options, type, machine answer, and a stem that contains no answer text.
