# Knowledge-point animation embedding

Use this reference when the user supplies a SiYuan block ID for animated-image insertion, asks to embed animations into or refresh animation embeds across documents (SiYuan or local Markdown), or explicitly authorizes scene-specific iframe insertion into an existing SiYuan note or Markdown file. Existing note content remains read-only for all other InkLoom tasks.

## Embed by document scenario

Use this mode when the user asks to embed animations into a document, refresh its existing embeds, or catch it up with newly published scenes. Classify each document first, then edit only its live copy — the side the user actually reads and maintains:

- **SiYuan-resident:** a matching document exists in the workspace (locate it by title or human path with `$siyuan-cli`). Edit that SiYuan document only; leave the corresponding local Markdown file untouched.
- **Markdown-only:** no matching SiYuan document exists and the MD file lives in the local library. Edit the MD file directly with image syntax; run no SiYuan writes. The URL embeds carry over when the note is later imported through `$siyuan-export`.

Then, per document:

1. Serve every embed from the online jsDelivr proxy URL defined in [animated-avif.md](animated-avif.md): insert `![](<proxy-url>)` blocks and let the AVIF stay on the CDN. When both the proxy and the production host are unreachable, report that instead of downloading the asset into the workspace.
2. Verify each candidate proxy URL with a real GET before editing, and read the animation's manifest to enumerate every scene AVIF, because an already-embedded document may predate scenes that were added later.
3. Refresh stale embeds: an existing InkLoom image that references a local asset (`assets/…<scene-id>.avif`) or the production host keeps its alt text and position and swaps only its URL to the proxy form. Update only the generated image block; surrounding legal content stays untouched.
4. Insert missing embeds: build the knowledge-point → scene mapping, then insert one proxy-URL image block immediately after the most precise block that states that exact point, following the anchor discipline of Locate the exact insertion points — one image per anchor, and never two image blocks adjacent. When no animation matches the document, report that instead of forcing an insert.
5. Completion: every manifest scene is either embedded at its matching point or reported as intentionally absent, no InkLoom image in the document still references a local asset or the production host, and every embedded URL passed the GET check.

## Direct block-ID animated-image mode

A bare block ID matching `^[0-9]{14}-[a-z0-9]{7}$`, for example `20260729232455-l0z16r1`, selects one exact insertion anchor. Do not infer a heading range or traverse a quote/list container to choose another anchor.

1. Read the target and record its `id`, `parentID`, `rootID`, `hPath`, `type`, `subType`, `markdown`, and `content`:

   ```bash
   siyuan -w "$SIYUAN_WORKSPACE" block get --id <target-id> -f json
   siyuan -w "$SIYUAN_WORKSPACE" block kramdown --id <target-id> -f json
   ```

2. Match the legal point to one semantic InkLoom scene, then run a fast placement preflight before any animation render, page capture, publication, build, or broad repository scan:

   - Read the matching local manifest and confirm the semantic scene and its image embed URL (the jsDelivr form defined in [animated-avif.md](animated-avif.md)).
   - Search the target document for that exact URL.
   - Read `siyuan block children --id <target-parent-id> -f json`; if the URL already exists, also read the generated image block and its reported parent.
   - If the same generated InkLoom image exists but is not the target's immediate next sibling, immediately send a commentary update stating that the animation already exists and is merely misplaced. Say that it will be moved, not rebuilt. Do not postpone this user-visible diagnosis until after visual QA, rendering, build, or deployment checks.

3. Take the shortest valid path after the preflight:

   - **Existing adequate scene, correct position:** report success without writes.
   - **Existing adequate scene, wrong position:** skip Remotion regeneration. Use the maintained helper to verify the image asset at its embed URL, move only the generated image block, and verify final order.
   - **Missing or inadequate scene:** improve or add the scene, or create the animation node and thin MDX carrier when none exists. Finish page-still QA and animated-AVIF publication before insertion.

4. Verify the asset directly at its embed URL, then construct exactly one image block. Note-side image embeds use the jsDelivr front, never the production host (see [animated-avif.md](animated-avif.md)):

   ```markdown
   ![InkLoom 动图：<scene-title>](https://gcore.jsdelivr.net/gh/inkloomer/inkloom@main/public/animation-avif/<animation-id>/<scene-id>.avif)
   ```

5. Treat `--previous <target-id>` as the preceding-sibling anchor, so the new block becomes the target's immediate next sibling. The target must be the precise text block that states the point; refuse to insert when the target is itself an image block or its next sibling already is one — stacking images is prohibited (the helper rejects both cases). Validate first, then apply the identical command:

   ```bash
   siyuan -w "$SIYUAN_WORKSPACE" --dry-run block insert --parent <parent-id> --previous <target-id> --data '<image-markdown>'
   siyuan -w "$SIYUAN_WORKSPACE" block insert --parent <parent-id> --previous <target-id> --data '<image-markdown>' -f json
   ```

6. Read `siyuan block children --id <parent-id> -f json` and require the inserted block to immediately follow `<target-id>`. Confirm the image URL occurs exactly once in the document and the original target block is unchanged.
7. Make the operation idempotent. If the exact URL already occupies the next sibling, report success without inserting another block. If an existing generated InkLoom image with that URL is elsewhere, move only that generated block after a dry-run instead of duplicating it; never move or rewrite the user's legal-content blocks.
8. Run the maintained InkLoom helper yourself after the production AVIF is deployed and reachable. Do not ask the user to execute either phase. A single `--apply` call internally performs the CLI dry-run, production check, write, and final verification:

   ```bash
   pnpm siyuan:embed-scene -- --target-id <block-id> --animation-id <animation-id> --scene-id <scene-id> --apply
   ```

   Running without `--apply` is a diagnostic-only mode for agents developing or debugging the helper; it is not a handoff step for the user. The helper validates the local manifest and AVIF, extracts `parentID`, detects duplicate embed URLs (treating the production and jsDelivr URL of the same asset as one embed), inserts or moves only a generated InkLoom image, verifies the original source block stayed unchanged, and confirms actual sibling order with `block children`. It must not decide what the legal animation should teach or which scene is the semantic match.

## Preconditions

1. Complete the Remotion explainers, commit and push the InkLoom website work, and verify each public page at `https://inkloomer.github.io/inkloom/<page-route>/`.
2. Use verified URLs for durable SiYuan embeds: the jsDelivr front defined in [animated-avif.md](animated-avif.md) for image embeds, and production `inkloomer.github.io` URLs for iframe and page embeds. A localhost URL may be used only as an explicitly requested temporary pre-publication placeholder; report it as temporary and replace it before calling the note finished or portable. Never use a preview deployment or raw repository URL; the jsDelivr `main`-branch CDN front is the only sanctioned repository-derived form.
3. Use `$siyuan-cli`; do not use the HTTP API or manually edit workspace files.

## Address the matching scene

1. Append `?scene=<semantic-id>` to open a specific animation page, for example `https://inkloomer.github.io/inkloom/objective/civil-procedure/03/trial-organization-path/?scene=first-instance`. The same query works on the local Astro route during verification.
2. Use the stable semantic kebab-case ID exposed by the player, such as `first-instance`; it survives scene insertion, reordering, and display-number changes. Use a zero-padded number such as `02` only for a legacy animation that has no semantic ID, and migrate that animation when it is next edited.
3. Treat the parameter as an exact key. Do not append surrounding prose to it. An unknown value silently opens the first scene, so load every final URL and confirm the visible page number and title.
4. Reuse one animation route with different `scene` values when separate knowledge points map to separate pages. This is preferable to repeating a generic URL that always starts at page 01.

## Locate the exact insertion points

1. Search the existing note with `$siyuan-cli` and identify the document ID, notebook ID, human path, parent block ID, and every source-point block that an animation scene explains.
2. Read each candidate with `siyuan block kramdown --id <block-id>` and inspect the nearby headings or sibling blocks. Do not insert based on a search snippet alone.
3. Anchor to the most precise block that states the point — never the loosest container that merely contains it. When the point lives in one list item, one callout's inner paragraph, one table row, or one prose paragraph, that block is the anchor; a heading or parent container is acceptable only when the whole section as a unit is what the scene explains. Do not anchor to a block whose next sibling is already an image block: that would stack two images.
4. One image per anchor. Two scenes must never share one anchor block, and two image blocks must never be adjacent siblings; if two knowledge points collapse onto one block, re-anchor each to its own smaller sub-block, and when the document has no such sub-blocks, stop and ask instead of stacking.
5. Build an explicit mapping of `source-point block ID -> animation route -> scene key -> scene title`. Preserve narrative order and insert each iframe immediately after the block explaining that exact point.
6. If the positions or scene matches are not unambiguous, stop and ask for the intended anchors. Do not append all animations to the document end or substitute one generic first-page iframe.
7. After every insert or move, read `siyuan block children` for each edited parent and verify that no two image blocks are adjacent and each image immediately follows the precise block it explains. Fix a violated placement by re-anchoring, never by leaving the stack.

## Insert without rewriting source blocks

1. Build one iframe block per knowledge-point scene, for example:

```html
<iframe src="https://inkloomer.github.io/inkloom/<page-route>/?scene=first-instance" width="100%" height="640" style="border: 0;" loading="lazy" allowfullscreen></iframe>
```

2. Use `siyuan block insert --parent <parent-block-id> --previous <source-point-block-id> --data <iframe-markdown> --dry-run` before the write.
3. Run the same command without `--dry-run` only after the target parent and preceding sibling are confirmed. Insert a new sibling block; do not use `block update` on the original legal-content block.
4. Read the inserted block and its surrounding siblings, then open its URL to verify the iframe follows the correct source point, preserves note order, retains the exact host and scene query, and displays the expected scene number and title.
5. Report the SiYuan human path, document ID, source-point block IDs, inserted iframe block IDs, and the scene-specific InkLoom URLs.

## Embed in Markdown

1. Apply the same knowledge-point mapping when the user explicitly requests iframe insertion into a Markdown file: place each scene-specific iframe immediately after the paragraph, list item, or callout it explains — tightly attached to that text, with no heading, blank region, or unrelated block between the text and its image.
2. Never stack two images. One image per text block; when two knowledge points live in one block, re-anchor each image to its own smaller sub-block (list item, callout paragraph), and stop to ask when the source has no finer blocks. After editing, re-read the file and verify no two image blocks are adjacent anywhere in the edited region.
3. Preserve the Markdown source and surrounding content. Add new iframe blocks only; do not move sections, convert the note into MDX, or duplicate the whole animation page.
4. Use production URLs for portable or published Markdown. For an explicitly temporary local workflow, `http://localhost:4321/inkloom/<page-route>/?scene=first-instance` is allowed, but mark it temporary and replace the host before publication or cross-device use.
