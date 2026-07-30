# SiYuan published-animation embedding

Use this reference only when the user explicitly authorizes adding published InkLoom animations to an existing SiYuan note. Existing SiYuan content remains read-only for all other InkLoom tasks.

## Preconditions

1. Complete the two Remotion explainers, commit and push the InkLoom website work, and verify each public page at `https://inkloomer.github.io/inkloom/<page-route>/`.
2. Use only those verified production URLs. Never embed `localhost`, an Astro development URL, a GitHub branch or preview URL, or a repository URL.
3. Use `$siyuan-cli`; do not use the HTTP API or manually edit workspace files.

## Locate the exact insertion points

1. Search the existing note with `$siyuan-cli` and identify the document ID, notebook ID, human path, parent block ID, and the two source-point blocks that each animation explains.
2. Read each candidate with `siyuan block kramdown --id <block-id>` and inspect the nearby headings or sibling blocks. Do not insert based on a search snippet alone.
3. Preserve the source note's narrative order: insert the first animation immediately after the block explaining its first key or difficult point, then insert the second immediately after the later block explaining its second point.
4. If the two positions are not unambiguous, stop and ask for the intended anchors. Do not append both animations to the document end as a fallback.

## Insert without rewriting source blocks

1. Build one iframe block per verified production page, for example:

```html
<iframe src="https://inkloomer.github.io/inkloom/<page-route>/" width="100%" height="640" style="border: 0;" loading="lazy" allowfullscreen></iframe>
```

2. Use `siyuan block insert --parent <parent-block-id> --previous <source-point-block-id> --data <iframe-markdown> --dry-run` before the write.
3. Run the same command without `--dry-run` only after the target parent and preceding sibling are confirmed. Insert a new sibling block; do not use `block update` on the original legal-content block.
4. Read the inserted block and its surrounding siblings to verify the iframe follows the correct source point, preserves the two-animation order, and retains the exact production URL.
5. Report the SiYuan human path, document ID, original source-point block IDs, inserted iframe block IDs, and public InkLoom URLs.
