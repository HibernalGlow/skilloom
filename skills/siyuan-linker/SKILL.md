---
name: siyuan-linker
description: Discover, audit, preview, create, and verify semantic connections between SiYuan notes or blocks using block references or block-query embeds. Use for SiYuan backlink cleanup, orphan-block connection, related-note discovery, broken or ambiguous block references, knowledge-graph curation, adding links between existing notes, or choosing between a reference and an embed. Stores one link edge by default and relies on SiYuan's automatic backlink/link-block views; explicit reciprocal links are opt-in only.
---

# SiYuan Linker

Build useful SiYuan connections from exact block-level evidence. Treat the source content as read-only and the link block as the only writable surface unless the user explicitly authorizes a content edit.

Read [the SiYuan link contract](references/siyuan-link-contract.md) before proposing or writing any connection.

## Knowledge Target Policy

Choose targets from contextual knowledge notes, regardless of whether the source is a note or a question. Prefer an atomic knowledge-point block whose ancestors show its place in the subject hierarchy and whose nearby content explains the rule, conditions, exceptions, or consequences.

Treat blocks as question material when metadata, path, or structure identifies a question bank, past exam, exercise, stem, options, answer, or question-specific analysis. Use question material to infer the tested proposition and as evidence that a link is needed; exclude it from target candidates. A question's analysis is still question-local and does not become a reusable knowledge provider merely because it contains an explanation.

If no exact knowledge-note target exists, report a knowledge-provider gap. Do not fall back to another question or a broad chapter container.

## 1. Resolve Scope

Resolve the workspace from the user's command, `$env:SIYUAN_WORKSPACE`, or the known task context. Assign it once and pass it explicitly on every command:

```powershell
$siyuanWorkspace = "D:\1STUDY\SIYUAN"
siyuan -w $siyuanWorkspace ...
```

Identify:

- source blocks or documents to curate;
- candidate notebooks, paths, or the whole workspace;
- audit-only or apply mode;
- automatic backlink/link-block navigation or explicit reciprocal mode;
- permitted link forms: reference, embed, or either.

Default to audit-only. Store one source-to-target edge unless the user explicitly asks for a second edge in the target content. For references, rely on SiYuan's computed backlink; for embeds, rely on SiYuan's link-block views and verify the stored embed edge. A broad request such as "整理这些笔记的双链" authorizes discovery and a write preview, not writes.

For a notebook or path scope, enumerate it before sampling content:

```powershell
siyuan -w $siyuanWorkspace notebook list -f json
siyuan -w $siyuanWorkspace document search "<scope name>" -f json
siyuan -w $siyuanWorkspace sql "select id, hpath from blocks where box='<notebook-id>' and type='d' and hpath like '<escaped-path>%' escape '\' and id > '<cursor>' order by id limit 100" -f json -l 100
```

Start with an empty cursor and continue with the last returned ID until a page is empty. Bind every path scan to the notebook `box`. Escape SQL apostrophes as `''`; escape literal LIKE `\`, `%`, and `_` as `\\`, `\%`, and `\_`, then append the intended `%` wildcard. Verify the first and last human paths. Then enumerate linkable content blocks inside each document with the same cursor rule:

```sql
select id, root_id, parent_id, hpath, type
from blocks
where root_id = '<document-id>'
  and type in ('h', 'p', 'i', 'b', 'callout', 't')
  and id > '<cursor>'
order by id
limit 100;
```

For a single document, use `document get`, `outline get`, and `block children` first, then the block query when full descendant coverage is required. Record document and block counts plus any exclusions or scan cap; never describe a capped or sampled pass as complete.

Completion criterion: every in-scope source has an exact block ID and human-readable path, scope pagination is exhausted or explicitly capped, and all write permissions are explicit.

## 2. Inventory the Existing Graph

For every source block:

```powershell
siyuan -w $siyuanWorkspace block get --id <source-id> -f json
siyuan -w $siyuanWorkspace block breadcrumb --id <source-id> -f json
siyuan -w $siyuanWorkspace block kramdown --id <source-id>
siyuan -w $siyuanWorkspace ref backlinks --id <source-id> -f json
siyuan -w $siyuanWorkspace ref mentions --id <source-id> -f json
```

Read the smallest block that preserves meaning. Expand to siblings, a heading subtree, or the document root only when the narrow block is insufficient. Record existing outbound references and embeds so the plan never duplicates a live edge.

Inventory stored outbound edges with read-only SQL. For one exact source block, filter `block_id`; for a whole document, filter `root_id`:

```sql
select id, block_id, root_id, def_block_id, type
from refs
where block_id = '<source-id>'
  and id > '<cursor>'
order by id
limit 100;
```

```sql
select id, block_id, root_id, def_block_id, type
from refs
where root_id = '<document-id>'
  and id > '<cursor>'
order by id
limit 100;
```

Treat `type='textmark'` as a block reference and `type='query_embed'` as a query embed. Batch by document and continue until an ID-cursor page is empty. Use `block dom` or `block kramdown` only to establish the exact placement and surrounding meaning; use the `refs` rows as the structural edge inventory.

Classify structural findings as broken target, duplicate edge, self-link, orphan, ambiguous target, or healthy edge. Keep mentions separate from actual references.

Completion criterion: every source has its existing inbound, outbound, and mention state accounted for.

## 3. Discover Candidate Connections

Extract distinctive entities, propositions, conditions, consequences, decisions, sources, and named projects from each source. Search with exact terms first, then close synonyms, then semantic search. Increment `--page` from 1 until a page is empty:

```powershell
siyuan -w $siyuanWorkspace search "<exact phrase>" -f json --type heading --type paragraph --type listItem --page <page> --page-size 20 --order-by 7
siyuan -w $siyuanWorkspace search "<concept query>" -f json --method 4 --type heading --type paragraph --type listItem --page <page> --page-size 20
```

Record the query, pages read, result count, and any explicit cap. A capped candidate search is a ranked candidate sample, not an exhaustive related-block scan.

Inspect each plausible target with `block kramdown`, `block breadcrumb`, and `ref backlinks`. Prefer the smallest stable block that contains the complete related proposition. Exclude the source itself, its trivial ancestor containers, generated indexes, and candidates connected only by a broad keyword.

For each target, read its breadcrumb and enough surrounding note context to prove that it belongs to a reusable knowledge explanation rather than isolated question material. Keep the precise knowledge-point block as the physical target; use its contextual ancestors for interpretation and navigation, not as a broader substitute target.

Score each candidate:

| Signal | Score |
| --- | ---: |
| Exact title, alias, named-entity, or quoted proposition match | +4 |
| Explicit dependency, contrast, cause, exception, support, or parent-child relation | +3 |
| Same stable source, project, case, or decision | +2 |
| Strong semantic match confirmed by reading both blocks | +2 |
| Reusable knowledge point with explanatory note context | +3 |
| Candidate gives an orphan a useful precise hub | +1 |
| Only a shared broad subject or generic keyword | -3 |
| Target is a large container when a precise child exists | -2 |
| Target belongs to a past exam, question bank, exercise, stem, answer, or question-local analysis | reject |

Classify `6+` as high confidence, `3-5` as review, and `2 or less` as reject. Never promote a score without a one-sentence relationship rationale grounded in both blocks.

Completion criterion: every proposed edge has two verified live block IDs, a relationship rationale, a confidence class, and no existing equivalent edge.

## 4. Choose Reference or Embed

Choose the least intrusive form that serves the reading task:

- **Block reference**: navigation, attribution, related-reading pointers, compact inline context, or a stable named proposition.
- **Block-query embed**: the reader must see the target content in place, the target remains authoritative, live updates are valuable, and the target is a self-contained block whose rendered content is safe in the source context.

When the user prefers embeds, use an embed for a high-confidence target that is atomic, semantically complete without hidden siblings, and small enough not to dominate the source reading flow. Fall back to a reference for containers, long or context-dependent blocks, sensitive dynamic content, unstable query results, or navigation-only relationships. Embed only one precise block by ID; avoid broad subtree or multi-result queries unless the user explicitly requests a live collection.

For default bidirectional navigation, create only one source-to-target edge. A block reference lets SiYuan expose the inbound backlink automatically; an embed remains a single live display edge and should be checked through SiYuan's link-block views plus the `refs` row. Do not add a target-to-source edge merely to make navigation look symmetric. Enter explicit reciprocal mode only when the user specifically requests a reverse link in the target content, and decide its placement independently.

For block references, select the anchor under [Anchor Text](references/siyuan-link-contract.md#anchor-text). Include the chosen anchor and its source in the manifest; never generate an unconstrained display label. An optional controlled emoji may prefix the relationship label under [Controlled Emoji Labels](references/siyuan-link-contract.md#controlled-emoji-labels); keep it out of the anchor and use at most one.

Completion criterion: every proposed direction has a selected form and a reading-purpose rationale.

## 5. Preview Exact Writes

Present a manifest before mutation:

| Source path / ID | Target path / ID | Target provenance | Relationship / emoji | Direction | Form / anchor | Placement | Confidence |
| --- | --- | --- | --- | --- | --- | --- | --- |

Include the exact Kramdown payload and the exact parent or preceding sibling. Prefer inserting a new dedicated paragraph or embed block over updating a content-bearing block. If no natural placement exists, report the candidate instead of forcing a `Related` section.

Require explicit confirmation for the manifest. Re-read every parent, preceding sibling, source, and target immediately before writing. Stop if an ID disappeared, content changed materially, placement moved, or an equivalent edge now exists.

Completion criterion: the user has confirmed the exact live manifest and every precondition still matches.

## 6. Apply and Verify

Run the exact insertion with `--dry-run` first, then repeat without it only after confirmation. Use `--previous` whenever semantic order matters.

After each write:

1. Read the inserted block with `block get` and `block kramdown`.
2. Read the destination parent's `block children` and prove placement.
3. For a reference, run `ref refresh --id <target-id>` when backlink state is stale, then confirm the source with `ref backlinks`.
4. For an embed, confirm the inserted type is `NodeBlockQueryEmbed` and the round-tripped query contains the exact target ID; do not require `ref backlinks` to index it.
5. If explicit reciprocal mode was requested, repeat the form-specific checks independently for the separately confirmed reverse edge; otherwise confirm that no extra reverse write was proposed.
6. Compare the source and target content blocks with their pre-write reads; only the newly inserted link blocks may differ.

On partial failure, stop. Report the successful edge and the failed edge separately; never delete or overwrite a successful link merely to make the batch look atomic.

Completion criterion: every applied direction round-trips to the intended block form, occupies the confirmed position, satisfies its form-specific navigation check, and leaves source content unchanged.

## Output

Return:

1. `Graph audit`: healthy, broken, duplicate, ambiguous, and orphan findings.
2. `Candidates`: source, target, rationale, confidence, and rejected alternatives.
3. `Write manifest`: direction, reference/embed form, exact placement, and payload.
4. `Verification`: inserted block IDs, paths, backlinks, and unresolved gaps.
