# SiYuan Link Contract

## Relationship Model

Distinguish the semantic relationship from its physical rendering:

```text
semantic edge: source block -> target block
rendering: block reference | block-query embed
reverse discovery: SiYuan-computed backlink
optional second edge: target block -> source block
```

A block reference plus its computed backlink is already bidirectional navigation: one stored source-to-target reference appears as an inbound backlink on the target. A query embed is a live display edge stored in the `refs` table as `type='query_embed'`, but the current `ref backlinks` command does not reliably display it. An explicit reciprocal connection stores two independent edges and therefore requires two independent placement decisions.

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
- Preserve meaningful one-way relationships. Reciprocal mode represents two useful reading paths, not compulsory graph symmetry.
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

For a reference, require the intended source in the target's backlink results and a matching `refs` row. For an embed, require `NodeBlockQueryEmbed` or equivalent embed-block type from `block get`, the exact target ID in the round-tripped query, and a `refs` row with `type='query_embed'`. If the user requested bidirectional embed navigation, verify the separately inserted reverse edge instead of relying on the backlink command.
