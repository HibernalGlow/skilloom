# SiYuan Link Contract

## Relationship Model

Distinguish the semantic relationship from its physical rendering:

```text
semantic edge: source block -> target block
rendering: block reference | block-query embed
reverse discovery: SiYuan-computed backlink
optional second edge: target block -> source block
```

A block reference plus its computed backlink is already bidirectional navigation: one stored source-to-target reference appears as an inbound backlink on the target. A query embed is one live display edge stored in the `refs` table as `type='query_embed'`; use SiYuan's link-block views to navigate it. Store one edge by default. An explicit reciprocal connection stores two independent edges and is only used when the user asks for a reverse link in the target content, with two independent placement decisions.

## Block References

Use SiYuan's native Kramdown block-reference syntax with a verified block ID:

```markdown
((20240102123456-abcdefg 'Dynamic anchor'))
((20240102123456-abcdefg "Static anchor"))
```

- Prefer a dynamic anchor when the visible anchor should follow the target's current content.
- Prefer a static anchor when the surrounding sentence requires stable wording.
- Keep custom anchor text factual; avoid silently changing the relationship into a stronger claim.
- Verify the parsed result with `block kramdown`; quoting and subtype details are parser-sensitive.

## Anchor Text

Use a controlled anchor, not free-form prose. The anchor names the target knowledge point; the surrounding text names the relationship.

Choose in this order:

1. Use the target's concise canonical knowledge-point heading as a dynamic anchor.
2. Use a verified note alias or established doctrinal term when the heading is not the ordinary name.
3. Preserve an exact natural mention from the source sentence when a contextual inline edit is explicitly authorized and the mention identifies the target unambiguously.
4. Generate a static anchor only when the target is a paragraph, the heading contains source numbering or editorial noise, or the canonical name is too broad without one operative qualifier.

Construct a generated static anchor as a short noun phrase:

```text
<doctrine, procedure, or legal object> + <decisive condition, exception, or consequence>
```

Examples:

```markdown
适用条件：((20240102123456-abcdefg "善意取得的构成要件"))
例外：((20240102123456-abcdefg "无权处分不影响合同效力"))
程序阶段：((20240102123456-abcdefg "二审中的反诉处理"))
```

Keep relationship labels such as `适用条件`、`例外`、`对比`、`依据`、`程序阶段` outside the anchor. Preserve exact legal terminology. Remove question numbers, years, source-volume names, chapter numbering, emojis, and editorial prefixes from generated anchors. Reject generic labels such as `相关内容`、`点击查看`、`本题考点`、`详见`、`该知识点`.

### Controlled Emoji Labels

Emoji are allowed as a compact visual cue, but they belong to the relationship label, never to the knowledge-point anchor. Use at most one leading emoji per link paragraph or embed label and choose from this stable vocabulary:

| Emoji | Label meaning | Example |
| --- | --- | --- |
| `📚` | 依据、法条、权威来源 | `📚 依据：((... "合同效力"))` |
| `✅` | 适用条件、构成要件、成立标准 | `✅ 适用条件：((... "善意取得的构成要件"))` |
| `⚠️` | 例外、限制、风险提示 | `⚠️ 例外：((... "无权处分不影响合同效力"))` |
| `↔️` | 对比、区分、相反规则 | `↔️ 对比：((... "诉讼时效与除斥期间"))` |
| `🧭` | 程序阶段、路径、操作顺序 | `🧭 程序阶段：((... "二审中的反诉处理"))` |
| `🧩` | 组成部分、关联知识点 | `🧩 组成要件：((... "意思表示"))` |

Do not invent decorative emoji, stack multiple emoji, or use an emoji to make a weak relationship look stronger. If no controlled label fits, omit the emoji and use a plain factual label. Normalize headings by stripping decorative emoji before using them as anchors; do not alter the target block itself.

Prefer the shortest phrase that remains unique in the local subject context. Add one domain or procedure qualifier only when needed to distinguish homonyms. Reuse the same anchor for the same target within one curated scope unless the source uses a verified established synonym.

Record anchor provenance as `heading`, `alias`, `natural mention`, or `generated`. For `generated`, include the target text that supports every term. Use a dynamic anchor for `heading`; use a static anchor for the other cases when stable wording matters.

A reference may live inline in a newly inserted paragraph:

```markdown
相关：((20240102123456-abcdefg '目标块'))
```

Insert a new paragraph for link-only curation. Updating an existing paragraph replaces that entire block and is reserved for an explicitly authorized contextual edit.

## Block-Query Embeds

Embed one verified target block with an exact-ID query:

```markdown
{{select * from blocks where id='20240102123456-abcdefg'}}
```

The parsed block must round-trip as `NodeBlockQueryEmbed`. Treat the target as the authority; an embed displays live target content and does not copy it into the source.

Use a single-ID equality query by default. Broader queries can change result count and order as the workspace evolves, so they belong only to an explicitly requested live collection.

## Placement Commands

Use exact IDs and JSON output for inspection:

```powershell
siyuan -w $siyuanWorkspace block children --id <parent-id> -f json
siyuan -w $siyuanWorkspace block insert --parent <parent-id> --previous <sibling-id> --data '<kramdown>' --dry-run -f json
siyuan -w $siyuanWorkspace block insert --parent <parent-id> --previous <sibling-id> --data '<kramdown>' -f json
```

When shell quoting is uncertain, place only the proposed payload in a UTF-8 temporary file and pass `--file <path>`. Keep the file outside the SiYuan data directory and remove it after verification.

## Graph Inventory

Use the read-only `blocks` and `refs` tables through `siyuan sql`; never open or mutate `siyuan.db` directly.

```sql
select id, hpath
from blocks
where box = '<notebook-id>'
  and type = 'd'
  and hpath like '<escaped-scope>%' escape '\'
  and id > '<cursor>'
order by id
limit 100;
```

Escape SQL apostrophes as `''`. For the LIKE operand, additionally escape literal `\`, `%`, and `_` as `\\`, `\%`, and `\_`; append only the wildcard that defines the requested descendant scope.

```sql
select id, block_id, root_id, def_block_id, type
from refs
where root_id = '<document-id>'
  and id > '<cursor>'
order by id
limit 100;
```

`refs.block_id` is the source block, `refs.def_block_id` is the target, `textmark` is a block reference, and `query_embed` is an embed edge. Paginate full-scope queries and report counts. Use `ref backlinks` to verify the user-visible backlink behavior of a block reference, not as the sole graph inventory.

## Safety Boundaries

- Treat existing content blocks as immutable unless the confirmed manifest names an exact content edit.
- Insert link blocks through the CLI; do not edit `.sy` files directly.
- Preserve target content; never replace it with a copied excerpt to simulate an embed.
- Verify source and target IDs immediately before mutation.
- Reject self-links, exact duplicate edges, and links whose only evidence is a broad shared topic.
- Select targets from contextual knowledge notes. Treat question and past-exam blocks as sources or evidence, not reusable knowledge targets.
- Keep any emoji in the relationship label, with at most one controlled leading emoji; never put it in the anchor text.
- Preserve meaningful one-way relationships. Automatic backlink/link-block views provide the normal reverse navigation; reciprocal mode represents a separately requested second content edge, not compulsory graph symmetry.
- Keep embeds precise. A large dynamic query can expose unrelated or sensitive content later.
- Use `ref mentions` as discovery evidence only. Plain-text mention does not prove an intentional reference.
- Stop on ambiguous placement, stale blocks, parser changes, or partial writes.

## Verification Commands

```powershell
siyuan -w $siyuanWorkspace block get --id <inserted-id> -f json
siyuan -w $siyuanWorkspace block kramdown --id <inserted-id>
siyuan -w $siyuanWorkspace block children --id <parent-id> -f json
siyuan -w $siyuanWorkspace ref refresh --id <target-id> -f json
siyuan -w $siyuanWorkspace ref backlinks --id <target-id> -f json
```

For a reference, require the intended source in the target's backlink results and a matching `refs` row. For an embed, require `NodeBlockQueryEmbed` or equivalent embed-block type from `block get`, the exact target ID in the round-tripped query, and a `refs` row with `type='query_embed'`; also inspect the available link-block view when user-visible reverse navigation matters. Only if the user requested explicit reciprocal mode, verify the separately inserted reverse edge.
