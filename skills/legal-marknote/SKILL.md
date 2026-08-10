---
name: legal-marknote
description: Convert legal study material into structured SiYuan Markdown while preserving legal substance, tables, images, and explanations. Repair clearly misrecognized headings, broken heading fragments, and semantic heading nesting; add equivalent, easier-to-review Markdown summaries below unwieldy memorization-sheet tables without replacing them. Also use for targeted repairs to text produced by an earlier legal-marknote version.
---

# Legal Marknote

Use this skill when法考教材、题目、解析或笔记需要整理成可复习的思源笔记。

## Workflow

1. Preserve legal substance, wording, images, statutory text, explanations, and the intended hierarchy. Preserve title wording and order, but repair a title marker or title level when the source has clearly misrecognized the structure. When the user authorizes removal of non-standard headings, remove only the false heading marker or duplicate heading wrapper; preserve the answer, explanation, and legal content. Retain tables that carry genuine horizontal comparison, mapping, numerical alignment, or merge relationships. Do not create or retain a **单轴名称—说明表** merely because the source has two columns: when the first column is only a short category/name and the second column is that item's complete rule, with no second comparison dimension, cross-row alignment, merge relationship, or numerical axis, replace the complete table with a Markdown parent list whose bold item names lead their preserved rule text. A few short numbered items may use `<br />` inside a genuine comparison cell. When a cell becomes a large list, normally four or more independent items, or three long items totaling about 100 visible characters, either leave an existing source table unchanged or replace the complete table content with real Markdown lists outside the table. A converted list must obey every ordinary MarkNote style gate, including semantic colors, 42-character lines, nesting, rich styles, and the visualization route when triggered. For a retained SiYuan merged table, first map its logical grid: every `rowspan`/`colspan` must have exactly matching `fn__none` cells, and every `fn__none` must be covered by an actual merge. Do not emit redundant `colspan='1'` or `rowspan='1'`.
2. Run a heading-repair pass before formatting body content. Treat every source heading marker as a candidate, then keep, merge, demote, or convert it only from its role in the surrounding structure. Also inspect top-level bold classification leads: when `**短分类词**：说明` governs a following list, table, Callout, diagram, or multiple sibling rule blocks, promote the short term to the next heading level and move the text after the colon into its own paragraph. Under an existing H2 `考查角度`, this normally creates H3 headings such as `### 权利能力和行为能力` and `### 经营范围`; do not leave the governing label as an isolated styled paragraph. First identify question-and-answer regions: from `###### 习题` through the fenced question and `**回答与解析：**` answers, a numbered line is answer content, not a heading. In that region, an existing `#### 1. ...`, `#### (1) ...`, `#### ① ...`, or equivalent numeric marker is a batch-recognition error, not evidence of a real heading; demote it to the corresponding quoted ordered-list item or body text. Never carry such a marker into the output heading hierarchy. Outside question-and-answer regions, when a numeric-only heading is immediately followed by a short legal term and its colon-led definition, move the term into the heading, retain the number, and begin the body with the definition after the colon. Follow the decision rules in [the detailed guide](references/note-guide-original.md#标题识别与修复).
3. Format question-and-answer groups before styling body content. A short question must occupy its own fenced `md` block, even when another short question tests the same topic. Only one continuous large problem may share a block with its `(1)`–`(3)` subquestions; do not group independent short questions merely because there are no more than three. A continuous quoted exercise group has exactly one `> ###### 习题` label, placed before its first question fence; later fences in that group do not repeat the label and do not rename it to `习题1`–`习题3`. Splitting changes containers only: inside each fenced question block, preserve every original question number, subquestion marker, punctuation form, and sequence exactly. Never restart fenced-question numbering from `1` or renumber it by the new block order. Put the matching answer immediately after its block and never place answers for one block after a later question block. Outside the fenced question text, ordinary explanatory enumerations may still be normalized into standard Markdown lists. `**回答与解析：**` is optional and may appear at most once for the whole outer question quotation; do not repeat it for every block.
4. Declare note-topic providers. Attach `custom-qb-note-topic-id` directly to every atomic topic heading that provides reusable explanation material. When a suitable heading would distort the source hierarchy, add one standalone `**考点：显示名**` paragraph anchor and attach the IAL to it. One provider IAL contains exactly one topic ID; the same ID may appear in different lecture, recitation, or review notes.
5. Separate source content from added summaries or study prompts.
6. Break long prose at semantic boundaries: a definition or explanation introduced by words such as “是” may begin a child list even without punctuation. Decide child lists from semantic independence, not labels or punctuation: split parallel branches that each retain their own applicable situation, object, judgment, or legal effect; keep the prerequisites, procedure, and consequence of one inseparable rule in one item. Use indentation only for containment or progression, then dedent when that relationship ends.
7. Plan semantic colors before writing the final Markdown. Source/question material may remain uncolored when that is faithful to the source, but every generated explanation, summary, or study prompt must actively color recurring subjects and key concepts. Keep one subject and its aliases on one stable color throughout the note; color short semantic anchors only, never a whole clause, sentence, or punctuation span. Use foreground color, background color, or both. Every SiYuan style IAL must follow bold text (`**短锚点**{: style="..."}`); a style attached to plain text is invalid.
8. Apply the active-coverage, density, boundary, callout, and visualization-routing rules in [the detailed guide](references/note-guide-original.md). Keep ordinary prose lines within 42 visible characters and split longer reasoning at semantic boundaries into nested lists. For medium or complex material, use a rich presentation selected from the content: at least four auxiliary style families (highlight, optional low-frequency `<em>` italic, strikethrough, inline code, underline), at least four structural families (nested lists, Callout, subheadings, tables, one suitable visual, dividers), and at least three short background-color anchors. Bold uses `**text**`; italic uses only `<em>text</em>`. Do not generate `*text*`, `_text_`, or `__text__`. Choose editable SiYuan Mermaid, div-wrapped HTML, or static SVG/PNG from the real relationship and delivery need; do not force a fixed section template or renderer.
9. Audit tables by information shape. **真实表头先行**：每张保留或拆出的表都从一行无 `rowspan`、`colspan`、`fn__none` 的真实列名开始，第二行必须是 Markdown 分隔行，合并数据只能从第三行开始；拆成多张表时，每张都重复必要表头。Keep concise comparison cells in tables, and use `<br />` for a few short numbered items when that improves scanning. Convert a two-column label/rule structure to a list when each row can be read independently as `**名称** -> 完整说明`; split the explanation into child items only when it contains genuinely independent branches. Keep the table when readers must compare the same additional fields across rows, align numbers or periods, or follow merged-cell scope. When a cell contains a large list, normally four or more independently reviewable items, or three long items totaling about 100 visible characters, move the category and every item into a real nested Markdown list; remove the generated table, or leave an existing source table unchanged and place the usable list beside it. Keep one inseparable prerequisite-to-procedure-to-consequence rule in one list item. Apply the full active-color, line-length, hierarchy, and rich-visual contract to every converted list.
10. Run `python -X utf8 scripts/validate_output.py <output.md> --strict --require-topic-ial` and `python -X utf8 scripts/audit_question_groups.py <output.md>`. When the original material is available as a file or snapshot, run all source-aware gates: add `--source <source.md> --require-source` to `validate_output.py`, run `python -X utf8 scripts/audit_question_groups.py <output.md> --source <source.md>`, and run `python -X utf8 scripts/audit_heading_promotions.py <source.md> <output.md> --strict`. The heading audit allows a new H3 beneath an existing H2 but rejects a new H2 peer. Promoting a classification does not itself create a topic ID: retain the nearest parent provider unless a known independently maintained ID exists. Treat `E404`–`E410` as the merge-grid audit, `E414`–`E416` as the real-header audit, and `E706` as the missed-classification-heading gate; all are mandatory before delivery.
11. Fix every reported error and review every advisory. Then manually confirm legal accuracy, source completeness, repaired hierarchy, semantic color choices, provider IAL placement, and whether each Callout category is substantively justified; syntax checks cannot decide those legal judgments.

## Note-topic provider IAL

Use a direction-specific attribute; no `role` discriminator is needed:

```md
### 善意取得
{: custom-qb-note-topic-id="civil-property-good-faith-acquisition"}
```

If the note needs an anchor without a new heading:

```md
**考点：善意取得**
{: custom-qb-note-topic-id="civil-property-good-faith-acquisition"}
```

The value is one lowercase ASCII kebab-case ID. This IAL marks the block as a provider of material for that topic. It must not coexist with `custom-qb-id` or `custom-qb-question-topic-ids`; do not use `custom-qb-role`, `custom-qb-topic-id`, or `custom-qb-topic-ids` for new output. Topic Index resolves the shared value later, so this metadata does not store a SiYuan block ID and does not alter Markdown references or backlinks.

## Question-answer heading guardrail

Inside a `习题` block, treat `回答与解析` as a hard boundary: the answer sequence belongs to the question and must remain list/body content. During batch processing, do not treat an existing `####` or `#####` before an answer number as a structural fact. Demote that batch-recognition error, preserve the substantive text, and merge a duplicate marked line into the matching answer item when the same answer is already listed below. Keep `###### 习题` itself as the question label, but do not retain numeric answer headings such as `#### 1. (1)正确...`.

## Question-answer formatting

For a question set with many assertions, do not use one large fenced block for all questions. Write `> ###### 习题` once at the top of the continuous quoted exercise group. Each short question then gets its own `> ```md` block and its own immediately following answer list without another `习题` heading. Do not create `习题1`, `习题2`, or `习题3`; the immutable source numbers inside the fences already identify the questions. Only a continuous large problem with `(1)`–`(3)` subquestions may share one block. Do not group independent short questions merely because there are two or three of them. Keep all groups inside the same outer `> ` quotation; do not start a new outer quotation for each group. The fence is for the learner's question prompt only; answers and explanations remain ordinary Markdown inside that one surrounding quote block. `**回答与解析：**` may be written once before the first answer list when it improves scanning, but never repeat that label after every question block.

Question identity inside the `md` fences is immutable. If the source question blocks contain `37.` and `42.`, the split blocks remain `37.` and `42.`; they do not become `1.` and `2.`. Preserve fenced subquestion tokens exactly as written, including `(1)`, `（1）`, `①`, `一、`, full-width punctuation, and skipped numbers. This restriction does not prevent ordinary explanation lists outside the question fences from using standard Markdown numbering.

Answer sections require the same semantic care as the question section:

- Start each answer with a concise conclusion marked with `==高亮==`, then attach the reason to that answer number. Preserve the original answer mapping and legal substance.
- When an explanation contains independent branches with their own subject, condition, procedure, exception, comparison, or legal effect, turn them into an indented Markdown sublist. Keep an inseparable prerequisite-to-procedure-to-consequence chain in one item instead of splitting it merely at punctuation.
- Convert source forms such as `(1)` and `(2)` into a standard indented ordered sublist when they are sub-points of one answer; do not leave duplicated numbering in a flat paragraph. Use a sublist for multiple reasons when each reason can be reviewed independently.
- Apply semantic color anchors in answer explanations just as in the surrounding note: use consistent colors for recurring parties or objects, procedural actions and the court, and contrasting results such as acceptance/rejection or valid/invalid. Color only short retrieval anchors, and always use the required bold form, for example `**法院**{: style="color: var(--b3-font-color4);"}`. Combine color with `==高亮==` and bold cues without coloring whole sentences.
- Do not put a whole answer section into a Callout by default. Use a small `NOTE`, `CAUTION`, or `WARNING` only when the content has that substantive property, and keep the answer-to-question correspondence visible.

## Split-table heading guardrail

Before splitting a table, build the heading skeleton for the parent topic and each independent category. Each split table must be immediately preceded by a valid Markdown heading such as `### 保全措施` or `#### 诉前保全的适用情形`; choose the level from the surrounding hierarchy. Do not output:

```md
诉前保全
| 项目 | 规则 |
| --- | --- |
```

If the source provides only a category cell or plain label, promote that label into a concise heading while retaining the category and all legal content in the table. The heading must describe the table's complete rule group, not merely repeat an arbitrary first cell. Do not add a heading for every row when rows belong to one category, and do not use bold text alone as a substitute for a heading.

## Legacy Output Revision

When the user states that a text was already processed by an earlier `legal-marknote` version and asks only for corrections, use [the revision-only guide](references/legacy-output-revision.md). Do not rerun the full workflow or load `references/note-guide-original.md` by default; inspect only the affected fragment and its local context, then preserve every unrelated part of the existing output. Add or migrate note-topic IAL only inside the authorized fragment; if topic metadata is outside the requested repair scope, omit `--require-topic-ial` for that revision-only validation and report the remaining migration separately.

## Existing SiYuan documents

When a finished SiYuan document already contains manual edits, references, or backlinks, keep the existing blocks in place. Use [the manifest migration workflow](references/siyuan-topic-migration.md): export the heading outline and block IDs beside the corresponding `20-整理` file, review topic IDs in JSON, preview all mutations, then set `custom-qb-note-topic-id` directly on the selected block IDs and verify each write. Never replace this workflow with Markdown re-import.

## Accuracy

- Never replace a legal rule with an unsupported paraphrase.
- Keep answer bases and explanations attached to the material they justify.
- Use highlights and colors as retrieval cues, not decoration.
- Mark uncertain or incomplete source material for review.

## Rich visual contract

MarkNote is a reading aid, not a plain transcription. Apply this contract to generated explanations and summaries according to their real semantic complexity. 源/题目内容可以保持无色，但新增解析必须主动着色：

- **Color mapping**: build a local vocabulary before writing. Repeated parties, institutions, objects, concepts, states, and aliases keep the same color. Use short bold anchors; foreground-only, background-only, and combined styles are all valid. 背景色：可以单独使用。Background-only example: `**诉讼中**{: style="background-color: var(--b3-font-background11);"}`.
- **Dense reasoning**: 每条普通正文行最多 42 个可见字符。Turn independent conditions, branches, exceptions, and consequences into nested lists so the reader can scan the logic.
- **Rich mode**: when a block is medium or complex, 至少四类辅助样式 from `==高亮==`, optional low-frequency `<em>斜体</em>`, `~~删除线~~`, inline code, and `<u>下划线</u>`; 至少四类结构载体 from nested lists, Callout, subheadings, tables, one suitable visual, and dividers; 至少三个短背景色锚点。斜体不是必选项。
- **可视化路由**: medium or complex material needs one intentional visual when it contains procedures, sequences, branches, comparisons, or subject relationships, but the format follows the content. For in-note editability, use SiYuan's Mermaid.js and allow `%%{init}%%`, `classDef`, `style`, and `linkStyle`; do not call Beautiful Mermaid on this branch. For richer spatial/object composition, use HTML with exactly one outer `<div>`. For stable themed output, insert a rendered SVG/PNG with alt text containing 可视化、图解、流程图、关系图、决策图、时间线, or `diagram`. Beautiful Mermaid is only a static renderer for its supported Mermaid subset: it drops `%%{init}%%`, applies edge-label color globally, and cannot color edge labels individually. Check semantic colors, labels, direction, connectors, and mobile width for the chosen format.
- **Audit**: run the MarkNote validator in strict mode and fix every E620-E627 finding before delivery.

The reference guide contains the complete formatting contract, color syntax, templates, and examples.
