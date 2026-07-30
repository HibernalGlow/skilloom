# Knowledge-point animation embedding

Use this reference only when the user explicitly authorizes scene-specific iframe insertion into an existing SiYuan note or Markdown file. Existing note content remains read-only for all other InkLoom tasks.

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
