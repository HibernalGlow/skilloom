---
name: legal-question-bank
description: 将法考客观题和主观题整理为可被 Damophus 思源题库、未来网站和 Markdown 构建流程共同消费的题库源文件。为题目、考点引用和解析边界写入稳定的 `custom-qb-*` IAL 元数据，保留题干、选项、答案和完整解析；需要创建、迁移或校验可同步的题库 Markdown 时使用。
---

# Legal Question Bank

生成可移植的题库源 Markdown。Markdown 和 IAL 是题目内容与静态属性的唯一事实来源；不要生成思源数据库记录、作答记录、Riff 状态或插件 UI。

## Workflow

1. 保留原始标题、题干、选项、答案、完整解析、图片和表格。不得改写题干、选项、答案或解析的法律含义。
2. 先识别一个或多个考点，再为每道题确定稳定 ID、题型、标准答案和解析开始块。
3. 写入或补齐本技能定义的 IAL；不得改动现有稳定 ID。只有在原 ID 明显错误且用户明确同意时才迁移，并记录旧 ID。
4. 客观题作答区只放题干和选项。答案、解析结论、状态色、高亮和答案遮罩都从 `custom-qb-section="solution"` 起开始出现。
5. 在提交前运行 `python -X utf8 scripts/validate_question_bank.py <output.md> --strict`。有原始文件时追加 `--source <source.md> --require-source`。

## Source Contract

### Topic directions

普通笔记提供材料、题目引用考点，使用两个不同属性直接表达方向：

```md
### 意定担保物权的流押流质条款
{: custom-qb-note-topic-id="civil-security-flow-clause"}
```

- `custom-qb-note-topic-id` 只用于 MarkNote 等普通笔记提供方；一个块只提供一个考点，可以在不同笔记中重复。
- 题库题目不继承该属性。题目使用 `custom-qb-question-topic-ids` 显式引用一个或多个 Topic Index 稳定 ID。
- 两种属性通过相同 ID 值关联，但不使用 `custom-qb-role` 判断方向。

### Questions

每题使用五级标题，标题的紧后 IAL 必须包含：

```md
##### 108.
{: custom-qb-id="civil-gold-objective-2020-2-1-14" custom-qb-question-topic-ids="civil-security-flow-clause,civil-mortgage-registration" custom-qb-type="multiple" custom-qb-answer="A,B,D"}
```

- `custom-qb-id` 全库唯一、稳定、仅使用小写 ASCII 字母、数字和连字符。
- `custom-qb-question-topic-ids` 必填；使用英文逗号分隔一个或多个小写 ASCII kebab-case ID，不得重复。
- `custom-qb-type` 只能为 `single`、`multiple`、`true-false` 或 `subjective`。
- `single` 必须有一个 `custom-qb-answer` 选项 ID；`multiple` 必须用英文逗号列出至少两个选项 ID；`true-false` 使用 `true` 或 `false`；`subjective` 不写 `custom-qb-answer`。
- 选项身份优先通过 `A.`、`A、`、`（A）` 或任务列表前缀识别。不要为普通选项逐项写 IAL。
- 仅当选项无法稳定识别时，在该选项块写 `custom-qb-option="A"`。

### Solution Boundary

解析开始的第一个块必须写：

```md
- 综合考向：本题综合考查区分原则、流押条款效力及不动产抵押权设立。
{: custom-qb-section="solution"}
```

`custom-qb-section="solution"` 到下一题之前均为提交后内容。该区域保留完整答案与解析，可使用 GoldQuest 的列表、Callout、表格和语义颜色规则，但不要放置悬停答案遮罩 HTML。

## Objective Question Example

```md
##### 108.
{: custom-qb-id="civil-gold-objective-2020-2-1-14" custom-qb-question-topic-ids="civil-security-flow-clause,civil-mortgage-registration" custom-qb-type="multiple" custom-qb-answer="A,B,D"}

- 甲向乙借款100万元，同时签订房屋抵押合同，约定到期不能偿还时乙取得房屋所有权。对此，下列哪些说法正确？
    - [ ] A. 双方关于乙取得房屋所有权的约定不发生相应效力。
    - [ ] B. 乙可以请求拍卖房屋而从中优先受偿。
    - [ ] C. 抵押合同因属虚假行为而无效。
    - [ ] D. 抵押合同应认定有效。

- 综合考向：本题综合考查区分原则、流押条款效力及不动产抵押权设立。
{: custom-qb-section="solution"}

- 正确答案：A、B、D。
- 流押条款不发生直接转移所有权的效力；抵押登记有效时，抵押权人仍享有优先受偿权。
```

## Subjective Question Example

```md
##### 12.
{: custom-qb-id="civil-case-analysis-2024-12" custom-qb-question-topic-ids="civil-security-flow-clause" custom-qb-type="subjective"}

- 说明抵押合同中的流押条款无效后，对抵押合同效力和抵押权实现的影响。

- 参考答案与评分要点。
{: custom-qb-section="solution"}

- 应区分流押条款与抵押合同；流押条款不发生所有权直接转移效力，不当然影响抵押合同效力。
```

## Prohibitions

- 不要将题目统计、作答次数、正确率、闪卡状态、数据库列 ID、块 ID 或设备信息写进题目 IAL。
- 不要把正确答案写入题干、选项文本、已勾选任务列表、题面高亮、状态色或题面 Callout。
- 不要依赖 `###### 答案与解析` 或“答案/解析/综合考向”等文字作为唯一边界；必须写 `custom-qb-section="solution"`。
- 不要根据选项顺序推断答案；答案始终引用原始选项 ID。
- 不要为同步而重写正文层级、移动块、删除材料或生成独立错题文档。
- 新输出不要使用 `custom-qb-role`、`custom-qb-topic-id` 或 `custom-qb-topic-ids`；旧属性只能作为迁移输入并必须给出转换预览。

阅读 [references/question-contract.md](references/question-contract.md) 以处理旧稿迁移、异常选项和与未来网站的兼容约束。
