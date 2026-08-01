# Knowledge-point animation embedding

Use this reference when the user supplies a SiYuan block ID for animated-image insertion or explicitly authorizes scene-specific iframe insertion into an existing SiYuan note or Markdown file. Existing note content remains read-only for all other InkLoom tasks.

## Direct block-ID animated-image mode

A bare block ID matching `^[0-9]{14}-[a-z0-9]{7}$`, for example `20260729232455-l0z16r1`, selects one exact insertion anchor. Do not infer a heading range or traverse a quote/list container to choose another anchor.

1. Read the target and record its `id`, `parentID`, `rootID`, `hPath`, `type`, `subType`, `markdown`, and `content`:

   ```bash
   siyuan -w "$SIYUAN_WORKSPACE" block get --id <target-id> -f json
   siyuan -w "$SIYUAN_WORKSPACE" block kramdown --id <target-id> -f json
   ```

2. Match the legal point to one semantic InkLoom scene. Improve or add that scene when the animation exists; otherwise create the animation node and its thin MDX carrier. Finish page-still QA and animated-AVIF publication before insertion.
3. Verify the production asset directly, then construct exactly one image block:

   ```markdown
   ![InkLoom 动图：<scene-title>](https://inkloomer.github.io/inkloom/animation-avif/<animation-id>/<scene-id>.avif)
   ```

4. Treat `--previous <target-id>` as the preceding-sibling anchor, so the new block becomes the target's immediate next sibling. Validate first, then apply the identical command:

   ```bash
   siyuan -w "$SIYUAN_WORKSPACE" --dry-run block insert --parent <parent-id> --previous <target-id> --data '<image-markdown>'
   siyuan -w "$SIYUAN_WORKSPACE" block insert --parent <parent-id> --previous <target-id> --data '<image-markdown>' -f json
   ```

5. Read `siyuan block children --id <parent-id> -f json` and require the inserted block to immediately follow `<target-id>`. Confirm the image URL occurs exactly once in the document and the original target block is unchanged.
6. Make the operation idempotent. If the exact URL already occupies the next sibling, report success without inserting another block. If an existing generated InkLoom image with that URL is elsewhere, move only that generated block after a dry-run instead of duplicating it; never move or rewrite the user's legal-content blocks.
7. Automate steps 1 and 3-6 with a maintained InkLoom script when possible. The script may accept `--target-id`, `--animation-id`, and `--scene-id`, but it must not decide what the legal animation should teach or which scene is the semantic match.

## Preconditions

1. Complete the Remotion explainers, commit and push the InkLoom website work, and verify each public page at `https://inkloomer.github.io/inkloom/<page-route>/`.
2. Use verified production URLs for durable SiYuan embeds. A localhost URL may be used only as an explicitly requested temporary pre-publication placeholder; report it as temporary and replace it with the production host before calling the note finished or portable. Never use a GitHub branch, preview, or repository URL.
3. Use `$siyuan-cli`; do not use the HTTP API or manually edit workspace files.

## Address the matching scene

1. Append `?scene=<semantic-id>` to open a specific animation page, for example `https://inkloomer.github.io/inkloom/objective/civil-procedure/03/trial-organization-path/?scene=first-instance`. The same query works on the local Astro route during verification.
2. Use the stable semantic kebab-case ID exposed by the player, such as `first-instance`; it survives scene insertion, reordering, and display-number changes. Use a zero-padded number such as `02` only for a legacy animation that has no semantic ID, and migrate that animation when it is next edited.
3. Treat the parameter as an exact key. Do not append surrounding prose to it. An unknown value silently opens the first scene, so load every final URL and confirm the visible page number and title.
4. Reuse one animation route with different `scene` values when separate knowledge points map to separate pages. This is preferable to repeating a generic URL that always starts at page 01.

## Locate the exact insertion points

1. Search the existing note with `$siyuan-cli` and identify the document ID, notebook ID, human path, parent block ID, and every source-point block that an animation scene explains.
2. Read each candidate with `siyuan block kramdown --id <block-id>` and inspect the nearby headings or sibling blocks. Do not insert based on a search snippet alone.
3. Build an explicit mapping of `source-point block ID -> animation route -> scene key -> scene title`. Preserve narrative order and insert each iframe immediately after the block explaining that exact point.
4. If the positions or scene matches are not unambiguous, stop and ask for the intended anchors. Do not append all animations to the document end or substitute one generic first-page iframe.

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

1. Apply the same knowledge-point mapping when the user explicitly requests iframe insertion into a Markdown file: place each scene-specific iframe immediately after the paragraph, list, heading section, or callout it explains.
2. Preserve the Markdown source and surrounding content. Add new iframe blocks only; do not move sections, convert the note into MDX, or duplicate the whole animation page.
3. Use production URLs for portable or published Markdown. For an explicitly temporary local workflow, `http://localhost:4321/inkloom/<page-route>/?scene=first-instance` is allowed, but mark it temporary and replace the host before publication or cross-device use.
