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

        > [!MNEMONIC] <题源或 06-口诀 的标签>
        >
        > - 原句：<来自 06-口诀 或题源的口诀/技巧原句，逐字>
        > - ==<七字以内取字简写>== → <短展开>

      - 决断口径：<一句>
        - <一句>
      - <em>联系记忆</em>：与<兄弟卡或题源规则>同轴
        - <一句轴>
        - <与某规则同形：一句>

      ```yml          ← 起始列 = 背面直接项的内容列，见 E138
      cc:
        schema: cc-1
      qb_id: <本题块 id>
      source_qb_id: <原题 id>
      tier: flame | reinforce | prime | fuzzy | lucky
      origin: wrong | bookmark
      bookmark: classic | trap | hard | cramming | none
      trap: <陷阱短语>
      decision: <决策点短语>
      roles: "丙公司→担保人, 甲公司→原告"        # 没有主体替换就写 none
      variant: "none" | "<换皮说明：改了什么，为何与答案无关>"
      verified: "遮答案重做：<逐项推导> → 与 custom-qb-answer <答案> 一致"
      mnemonic: "<口诀原句>"
      mnemonic_from: "<06-口诀 或题源路径#行号>"
      animation: "<题源动图文件名>"
      links: "<兄弟卡 custom-dm-card-id 或 note-topic-id>（同轴｜同形｜反向：<轴>）"
      history: "<真实作答：日期 选项>"
      focus: "<已打的考前聚焦考点，无则 none>"
      # variant ≠ none 时，正确答案项下要有一行「题面对照：换皮自 <真题号>」
    ```
{: custom-dm-source-key="…" custom-dm-card-id="…" custom-dm-card-schema="1" custom-dm-card-kind="basic" custom-dm-card-renderer="list" custom-qb-note-topic-id="…"}
```

## Why the front keeps its options

SiYuan hides a card's answer with `.card__block--hideli .li[custom-riff-decks] > .list`, i.e. only the root item's child **lists**. A Callout at the root item's own column is therefore front content, which is why the options live in `> [!SELECTION]` and the reasoning lives in the first child list. This needs two question-bank scanner capabilities (present in the current Damophus build, covered by `scanner.test.ts`):

- the kramdown stripper removes a block's inline `{: id="…" updated="…"}` after a **whole** marker chain (`> - `, `  - `), and blanking a standalone IAL line keeps that line's `> ` prefix, otherwise one callout splits into one quote per option and every option disappears;
- a marked card block is split at its first child list, so the stem keeps the 题干 plus the option carrier and the child list onward becomes the solution — the answer never appears in the practice stem.

If a build lacks them, the exercise silently indexes zero options; re-check with the plugin's own scanner against `/api/block/getBlockKramdown` output, not against the authored `.md`.

## Case rules the generic card contract does not state

1. **Options keep the provider's wording; only declared swaps are allowed.** Keep every option exactly as the source wrote it — modal words (`可以/应当/不得/必须/有权/只能/一律/视为`), numeric thresholds and deadlines are the diagnostic signal, so a rewritten distractor destroys the card's value. Party and role names may be neutralized (丙公司 → 担保人) only when every swap is declared in the visible block as `roles:`; the gate applies precisely those swaps and then requires character-for-character equality (`E139`). Undeclared swaps, added or dropped options, and polished phrasing all fail. A top-level task list directly above the 正确答案 line merges into one CommonMark list and loses all options — keep the `> [!SELECTION]` carrier.
2. **The front carries zero hints, and may be re-skinned to defeat answer memory.** No `作答：＿＿＿`, no `先想清楚…`, no 考点 name, no answer word. The stem may be compressed, given neutral parties, and — where that helps — re-skinned: new subject and industry, plus invented detail that is provably irrelevant to the answer (合同标的、签订日、与争点无关的第三人), which often raises the distractor load and deepens understanding. Three hard limits:
   - **模型完全一致** — 主体—行为—时点—效果、每一个决定性事实与每一个陷阱事实都要一一对应；换皮不换骨。新增细节不得带入新的法律意义（不能顺手把“经常居住地”换成另一个城市，还顺带改变了管辖结论）。
   - **没把握就不要动** — 拿不准换皮后答案是否不变、干扰细节是否真的无关，就保留原题面并写 `variant: none`。宁可不出变式，也不出模型被动过的题。
   - **二次校验后才交** — 改完遮住答案重做一遍，把推导写进 `verified:`；推导与 `custom-qb-answer` 不一致时，要么改回原题，要么不出卡。
   `E092` still caps the front at 70 visible characters, and `E079`'s "no exercise replay" is satisfied by compression and role-neutral parties (原告/被告/担保人/申请人), not by deleting the trap facts.

   A re-skinned stem is recorded in three layers; only the filter layer is optional:
   - **machine layer (required)** — `roles` / `variant` / `verified` in the `cc:` block. `E137` refuses a Case card without the last two, and `E139` trusts only the declared `roles`.
   - **learner layer (required when `variant` is not `none`)** — one short child under 正确答案: `- 题面对照：换皮自 <真题号>`. A variant must stay traceable to the paper question, otherwise the card trains a case the learner will never meet again; keep it inside the 20-character item budget.
   - **filter layer (optional)** — a neutral front tag `#题库/题面/变式#`, and only when the deck is actually filtered that way. Never tag the change itself, never put original party names on the front, and never write 变式/原题 wording into the stem: the front stays hint-free.
3. **Analyze every option the learner did not already get right.** A stable mis-selection needs 规则 + 错因 + 判断链; an option that was once *missed* needs the reason for the doubt ("把签收当成当事人本人的事"); an option selected correctly every time gets one line and the note 不必重记. Skipping a missed option is the same defect as skipping a wrong one.
4. **The back carries its own reasoning Mermaid** with the learner's 误判入口 as a `wrong`-classed node feeding the decision node, and it keeps the provider's own visual: when the source range already has an InkLoom animation or diagram for this rule, copy that image under the governing child instead of drawing a rival one (`W126`).
5. **Carry the mnemonic on the back — only what the source already has.** Mount it as a `> [!MNEMONIC]` block, the back-side sibling of the front `SELECTION` carrier, whose first line quotes the 06-口诀 or provider sentence **verbatim**, and — only when that sentence is too long to recall — adds a second line with a `==取字简写==` of at most seven characters plus its short expansion after `→`. If no sentence was actually found in the provider or in `客观/06-口诀`, emit no `MNEMONIC` block: an extracted-then-compressed cue is allowed, an invented one is not, and `W128` only fires when the source really carries mnemonic material. Record the verbatim original and its path in the `yml` block (`mnemonic`, `mnemonic_from`). The whole block is the card's mnemonic region: the validator exempts it from the six-character highlight cap (`E029`), from the Callout-must-not-restate-the-answer gate (`E095`), and from the back Callout depth rule (`E086`), and it answers `W128` without a second card. Keep the wording on source vocabulary so provider styles still line up (`E041`).
6. **Link the siblings both ways.** A Case card is filed under one decision axis, so the other cards on that axis are its memory net: name each one under 联系记忆 with the axis label 同轴 / 同形 / 反向, and write the reciprocal line into every linked card (A 里写 B、C；B 里写 A、C；C 里写 A、B). Cross-专题 links inside one subject are in scope; cross-subject links follow `客观/06-口诀/**/三诉对比记忆表` rows only, where a cell reading `同民诉` is a 同轴 statement — see [answer-structure.md](answer-structure.md#reciprocal-and-cross-scope-links). Targets are a `custom-dm-card-id` or a note/question-topic id, never "对比记忆". No verified relation, no link line.
7. **Attributes split three ways.** The root IAL carries only the six schema-1 fields; Case identity, tier, trap, decision, mnemonic source, animation, links and attempt history live in the last visible ` ```yml ` block; runtime state (`custom-riff-decks`, due, interval, review log) is never written.
8. **Tags live on the front line.** `E097` counts tag characters, so the 题库 题型/年份 tags sit on the front with the knowledge and priority tags instead of on the 正确答案 line.
9. **Tag every 考前聚焦 考点 the card touches.** Build the index with `focus_index.py --build` (考点 names are harvested from the `#法考/<科>/<考点>#` tags inside `客观/04-考前聚焦`), then add `#考前聚焦/<科目>/<考点名>#` to the front line for **any** same-subject 考点 the card mentions — 题干、选项、解析、口诀 里出现都算，不要求它是本题主考点。跨科目的同名考点（民诉的委托代理 vs 三国法的委托代理）只作提示，人工确认后才打；只在 tag、内联样式或代码块里出现的词不算涉及（`E140` 只读卡面散文）。没有涉及就不打，不得为凑 tag 硬连。
10. **Inherit the priority from the existing decks.** Before assigning `#闪卡/优先级/P#`, read the provider's own `30-闪卡` directory (and the ledger's recorded decks) and take that 考点's base tier — the mode of the P levels already used for the same knowledge tag or `custom-qb-note-topic-id`. Reusing the base tier keeps one 考点 reviewable as one group and keeps `E089` honest across a growing deck; only when nothing exists to reference may the level be judged from the 解析 under [priority-calibration.md](priority-calibration.md), and then the reason goes into the delivery note. Deviating from the base tier is allowed but must be stated.
10. **No sibling walls: indent by logic, not by habit.** Four or more consecutive same-level items that own no children (`E141`) are a wall — the reader cannot tell what governs what. Give the run a governing parent and push the details one level in, split the run by axis (e.g. `规则：…` + its sub-points, then `你的状态：…`), or nest the sequential steps under the rule they instantiate. A genuine closed peer set of three (大前提/小前提/结论, or three parallel verdicts) still passes because the reasoning-slot labels break the run. Keep every parent and child inside its own budget: parent ≤20 visible characters (`E097`), and any line of 14+ visible characters needs a provider anchor (`E074`) — which is why `你的状态：两次都选对🎯` beats a bare long sentence.
11. **Style and emoji follow the MarkNote contract, per concept.** A Case card is dense study material, not a bullet memo: anchor the emoji to the *concept word it modifies* and label parallel concepts one by one (`签收📮、签署🖊、发言🗣`), never as a row of line-head labels; keep every auxiliary family inside each card (inline code, `==highlight==`, `~~strike~~`, `<u>`, `<em>`); give every substantive answer line at least two short provider anchors; keep one emoji under nine uses per deck (`E094`) and off the front/back overlap (`E100`). Emoji are placed mid-line next to the term — head-piling fails `E132`, tail-piling fails `E131`.
12. **The 正确答案 line stays literally plain.** The question bank reads the solution boundary from that line's raw text, so styling `正确`, `答案`, or the bare answer letter inside it destroys the boundary and the whole question silently drops out of the index (`missing-solution-boundary`). Put the answer letter's provider color on the verdict item instead (`✅ A 项：…`).
13. **`reinforce` cards get a second question.** When two wrong attempts fell into different traps, emit a variant card whose changed fact pattern flips the answer, and name the flip on the back.

## Measured gate behaviour for this shape

- **One ` ```yaml ` fence per file** (`E070`): the deck report owns that name, so the Case metadata fence is ` ```yml `; `source.protocol` must be exactly `"DAMO 闪卡 schema 1"`.
- **`E041` is substring-based and coloring is longest-match.** A provider term that only ever occurs inside a longer colored term (`程序` in `执行程序`, `特别授权` in `特别授权⭐`), inside a fence, or inside the option carrier is reported as a dropped style — give it one independent colored occurrence or reword, and never place an emoji directly after a term whose emoji-suffixed twin exists in the dictionary.
- **`E086` exempts the `SELECTION` carrier** by contract: it is front space, not a back Callout. Any other Callout still has to sit deeper than the direct answer items.
- **`W128` is answered by the `MNEMONIC` carrier** on a Case card: the block needs its `==cue==` and a `→`-decoded segment, must be separated from a neighbouring Callout by a blank line (`E098`), and stays one continuous quote run (`E134`). The block is the card's mnemonic region, so `E029`'s six-character highlight cap, `E095`'s restate-the-answer rule, and `E086`'s depth rule all skip it; a `mnemonic`-kind card is the only other way to satisfy `W128`. Never add the block when the source has no mnemonic material to carry.
- **`E074` skips a carrier image line**; every other answer line of 14+ visible characters needs its provider anchor.
- **`E027`**: at most four direct answer items — the 正确答案 line plus three verdicts; merge verdicts that share one verdict (`✅ A、C 可以代为`) and keep the per-option detail beneath them.
- **Sparse provider palettes** still need three short background anchors (`E062`) and four auxiliary families (`E060`): promote the term's own background variant rather than inventing a color, and keep one style per term (`E076`).
- **`E132`**: verdict prefixes are not enough — anchor semantic emoji inside the content next to the concept (`处分实体权利须⭐特别授权`, `两次误选都多它🧨`), and keep the front emoji off the back (`E100`).
- **The answer marker must stay unstyled.** `- 正确答案：ABC。` carries no inline span at all: the plugin reads the solution boundary from that line's literal text, so styling `正确`, `答案`, or the bare answer letter drops the whole question from the index (`missing-solution-boundary`) while the card still looks fine. Color the answer letter on the verdict item instead (`✅ A 项：…`).
- **`E140` 考前聚焦 tag 缺口**：开启 `--focus-index focus-index.json` 后，卡面散文里出现本科考前聚焦考点而正面没有对应 `#考前聚焦/科/考点#` 就失败。
- **`E139` option drift**: every carrier option must equal the provider's option after exactly the declared `roles:` swaps; anything else — polished phrasing, an extra option, a changed 可以/应当 — fails. The comparison is character-for-character on purpose: no shape guessing, no hardcoded party patterns, only what the card itself declared.
- **`E137` also requires `variant` and `verified`** in the `cc:` block, so an unstemmed variant or an unchecked re-skin cannot pass as a finished card.
- **`E098`/`E134`**: a blank line before every directive, and one continuous `> ` run per quoted passage.

## GoldQuest exemptions of a Case card

Recorded, not defects: `E822` (题库 tags move to the front line), `E802` (`custom-qb-note-topic-id` lives in the card IAL), `E301`/`E302` (the `list` root needs a bare ` ```mermaid ` child and a ` ```yml ` block). The stem and options still carry no conclusion colors and no `题干：`/`答案：` labels.

## Batch production and the ledger

Wrong-answer records keep arriving, so card production is incremental and must never re-card what is already out.

- Keep one ledger file (e.g. `错题Case卡/_pipeline/ledger.json`) mapping `source question_id -> {deck, card_id, provider, built_at}`. Read it before drafting; a question already in the ledger is skipped, and a question whose provider deck already exists is **appended to that deck** rather than given a sibling file.
- Dispatch by provider file, one worker per 专题 file: the provider colour dictionary is per file, so a worker that mixes two providers makes `E041` unsatisfiable. Each worker owns exactly one master and one output file.
- Order the queue by diagnosis value, not by volume: repeated errors and wrong-option counts first, then `bookmark`-only questions, then single-error questions; skip questions whose only wrong attempt took under 10 seconds (未思考作答 — a Case card cannot fix it).
- A worker reports only after three gates pass on its own output: `validate_flashcard.py --require-report --rich-style --all` with zero `E`, `validate_naming.py`, and the plugin scanner run over the pasted document's `getBlockKramdown` showing every question indexed with its full option set and no answer text in the stem. Only then may it write the ledger rows.
- Reciprocity is checked against the ledger, not just the current deck: a `links:` target that already has a card must gain the matching 联系记忆 line in that card, otherwise the edge is one-sided and the batch is incomplete.

## Completion criterion

One wrong-answer record produces one heading, one card root, one option carrier with verbatim choices, and one back that answers every option the learner did not reliably pick; the front is hint-free; the back carries the reasoning Mermaid with the learner's own 误判入口, the provider's existing animation, the corpus 口诀 with its path, and reciprocal 联系记忆 lines toward every sibling card on the same axis; the IAL holds only the six schema-1 fields; `validate_flashcard.py --require-report --rich-style --all` reports zero `E`; and `/api/block/getBlockKramdown` of the pasted document scans into the expected options, type, machine answer, and a stem that contains no answer text.
