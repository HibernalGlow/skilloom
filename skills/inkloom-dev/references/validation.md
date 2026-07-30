# InkLoom validation checklist

Run the smallest relevant checks after an edit, then run the full build when changing shared components, routing, styles, or many MDX pages.

## Structural checks

- Confirm changed files are under the intended InkLoom area.
- Confirm every imported component exists and its props match the implementation.
- Confirm local images exist and use the intended relative `./assets/...` path.
- Confirm raw legal material was first processed with `legal-marknote` in its user-supplied original file, while an already structured Markdown note was not processed again. Confirm the note and its assets remain at that original location and are absent from the website carrier.
- Confirm there are exactly two Remotion explainers, each with a focused legal learning objective, a stable `animation.meta.ts`, a source under `src/animations/<subject>/<chapter>/<animation-id>/remotion/`, and a direct Astro/React player embed in its own thin MDX carrier.
- Confirm `$remotion-best-practices` was read before the Remotion edit and that the React Markup, Rendering, Multimedia, or other routed reference was loaded when that task required it.
- Confirm moving a note would require changing only the relevant `sourceReference` metadata field, not the animation ID or published MDX carrier route.
- When an existing SiYuan note was explicitly requested as an embed target, confirm `$siyuan-cli` inserted two new sibling iframe blocks after their respective source-point blocks, in source-note order. Confirm every `src` uses the verified `https://inkloomer.github.io/inkloom/...` production URL and none use a local, preview, branch, or repository URL.
- Search changed MDX/Astro files for bare absolute site links such as `/objective/`; replace them with `/inkloom/...` or a relative link.
- Check nearby `_meta.yml` files when adding, moving, or renaming pages.

## Visual and interaction checks

- Treat Remotion page-still QA as a blocking iterative loop, not a one-time command:
  1. After creating or changing one animation, run `pnpm animation:pages <animation-id>`. Pass multiple changed IDs when appropriate.
  2. After completing a batch or all animations, run `pnpm animation:pages` with no ID so automatic discovery validates every animation.
  3. Open the generated `.artifacts/animation-pages/<animation-id>/<timestamp>/contact-sheet.png` to check page coverage, then inspect every `page-*.png` at its original resolution. Read `manifest.json` when the captured frame or scene boundary needs diagnosis.
  4. For every page, verify that the frame is nonblank and error-free; all intended teaching content has entered; no text, icon, connector, label, or emphasis is clipped, overlapping, occluded, or outside the canvas; text remains readable; branch, sequence, containment, comparison, and causal relationships are unambiguous; colors and emphasis match their semantics; the page contains no unintended adjacent-scene content; and the legal conclusion remains faithful to the source note.
  5. Mark canvas utilization as failed when the main teaching structure sits in one corner, side, or narrow band and a large unused region has no semantic, pacing, focus, reveal, or motion purpose. As a practical signal, roughly one-third or more dead usable canvas requires explicit justification; otherwise enlarge, rebalance, or redesign the relationship structure rather than merely scaling text or cards.
  6. Mark visual explanation as failed when a core rule, principle, conclusion, condition, or exception is primarily communicated by a prose paragraph or stacked full sentences. A “核心原理” box containing explanatory prose is an automatic failure. Require meaningful nodes, connectors, branches, containers, timelines, comparison lanes, transformations, or causal motion; allow only short labels, keywords, values, and one brief subordinate caption.
  7. Do not count decorative icons, borders, colored keywords, or oversized text as visual explanation or as valid canvas utilization when the information remains prose-only.
  8. Mark any plain table or table-like grid as failed, including a source table restyled with colors, icons, rounded cells, or row-by-row entrance animation. Require the comparison to be re-authored as lanes, grouped modules, axes, relationship maps, branches, or progressive transformations where layout and motion explain the difference.
  9. Mark slide-stack choreography as failed when each scene independently resets, enters, waits, and exits without a meaningful carrier or conceptual reason for the cut. Adjacent scenes must preserve the viewer's mental model through a shared node, connector, color role, spatial current, camera path, or visibly caused handoff when legal semantics permit it.
  10. Mark idle or decorative motion as failed when wobble, breathing, floating, pulsing, drifting, or looping effects continue without revealing, comparing, transforming, connecting, causing, or handing off information.
  11. Mark choreography as failed when elements enter simultaneously, in arbitrary source order, or with identical card-grid motion that ignores reasoning hierarchy. Verify that prerequisites lead consequences, rules lead exceptions, and the most important distinction receives the first or strongest movement.
  12. Verify that key results receive a readable still hold and that transitions use a restrained, consistent vocabulary. Reject uncaused direction reversals, ping-pong movement, random zoom/rotation, and novelty transitions that do not communicate a conceptual change.
  13. Reject motion that creates false legal meaning: unsupported morphs suggesting identity, nesting suggesting inclusion, arrows suggesting causation or direction, or animation order suggesting priority or procedure that the source does not establish.
  14. If any page fails, fix the composition, scene timing, information design, choreography, or shared visual system and rerun the affected animation. If the fix touches shared animation behavior or tokens, rerun `pnpm animation:pages` for all animations. Continue until every contact sheet and every full-resolution page passes inspection.
  15. Use `--at <0..1>` only when the default stable frame at `0.82` is not the scene's intended complete teaching state. Record why a different ratio is correct; never use it to conceal an animation defect.
- Do not proceed to publishing or report the animation complete while any captured page is uninspected, defective, or unverified.
- Inspect the page at narrow and wide widths.
- Verify tables do not overflow unexpectedly and flow diagrams remain legible.
- Test memory challenge: toggle the checkbox, confirm `.answer-node` blur, and confirm hover reveal.
- Test `trigger-link-1` and `trigger-link-2` hover emphasis when the page uses `VisualFlow`.
- Test the embedded Remotion player at narrow and wide widths; verify its scene navigation, playback, and reduced-size layout without a copied iframe.
- Check PageTitle quick actions, floating TOC, and any widescreen layout override touched by the change.

## Deployment handoff

- After the production build passes, commit and push the changed page, player, and Remotion source together. The `main` branch deploys to GitHub Pages.
- Confirm the deployed page at `https://inkloomer.github.io/inkloom/<page-route>/` before reporting it as uploaded. The page itself is the embed target; do not hand the user iframe markup to paste manually.

## Commands

```bash
astro dev --background
astro dev status
astro dev logs
astro dev stop
pnpm animation:pages <animation-id>
pnpm animation:pages
pnpm build
```

Use page-still QA first, then the dev server for responsive route and interaction checks. Use `pnpm build` as the final production-oriented gate; capture the first actionable error instead of hiding it behind a generic failure summary. Report the inspected artifact directory and any non-default capture ratio in the handoff.
