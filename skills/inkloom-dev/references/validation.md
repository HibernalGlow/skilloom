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
- When an existing SiYuan note was explicitly requested as an embed target, confirm `$siyuan-cli` inserted one new sibling iframe block after every requested source-point block, in source-note order. Verify the explicit mapping from source block to animation route, scene key, and scene title; do not assume only two embeds or one embed per animation.
- When Markdown iframe insertion was explicitly requested, confirm each new iframe follows the exact paragraph, list, section, or callout it explains and that surrounding source content was not moved, rewritten, or converted to MDX.
- Search changed MDX/Astro files for bare absolute site links such as `/objective/`; replace them with `/inkloom/...` or a relative link.
- Check nearby `_meta.yml` files when adding, moving, or renaming pages.

## Visual and interaction checks

- Treat Remotion page-still QA as a blocking iterative loop, not a one-time command:
  - Inspect every `SCENES` entry before rendering: `previewEndTrimFrames` is mandatory. Confirm it is `0` only when the scene has no authored exit; otherwise confirm it reaches the first stable frame immediately before the exit. Verify the embedded Player ends on that stable frame, while the full composition duration remains unchanged.
  1. After creating or changing one animation, run `pnpm animation:pages <animation-id>`. Pass multiple changed IDs when appropriate.
  2. After completing a batch or all animations, run `pnpm animation:pages` with no ID so automatic discovery validates every animation.
  3. Open the generated `.artifacts/animation-pages/<animation-id>/<timestamp>/contact-sheet.png` to check page coverage, then inspect every `page-*.png` at its original resolution. Read `manifest.json` when the captured frame or scene boundary needs diagnosis.
  4. For every page, verify that the frame is nonblank and error-free; all intended teaching content has entered; no text, icon, connector, label, or emphasis is clipped, overlapping, occluded, or outside the canvas; text remains readable; branch, sequence, containment, comparison, and causal relationships are unambiguous; colors and emphasis match their semantics; the page contains no unintended adjacent-scene content; and the legal conclusion remains faithful to the source note.
  5. Mark canvas utilization as failed when the main teaching structure sits in one corner, side, or narrow band and a large unused region has no semantic, pacing, focus, reveal, or motion purpose. As a practical signal, roughly one-third or more dead usable canvas requires explicit justification; otherwise enlarge, rebalance, or redesign the relationship structure rather than merely scaling text or cards.
  6. Mark visual explanation as failed when a core rule, principle, conclusion, condition, or exception is primarily communicated by a prose paragraph or stacked full sentences. A “核心原理” box containing explanatory prose is an automatic failure. Require meaningful nodes, connectors, branches, containers, timelines, comparison lanes, transformations, or causal motion; allow only short labels, keywords, values, and one brief subordinate caption.
  7. Check whether concrete people, roles, groups, institutions, documents, measures, actions, and outcomes have useful semantic icons or compact pictograms instead of relying only on highlighted words. Reject monotonous text-led scenes when recognizable visual tokens could carry those concepts. Require a short label for ambiguous symbols and consistent icon style, scale, stroke weight, and color semantics.
  8. Verify that icons participate in the teaching structure or motion as nodes, actors, targets, causes, results, or persistent carriers. Do not count decorative icons, borders, colored keywords, oversized text, or symbols pasted beside prose as visual explanation or valid canvas utilization.
  9. Mark any plain table or table-like grid as failed, including a source table restyled with colors, icons, rounded cells, or row-by-row entrance animation. Require the comparison to be re-authored as lanes, grouped modules, axes, relationship maps, branches, or progressive transformations where layout and motion explain the difference.
  10. Mark slide-stack choreography as failed when each scene independently resets, enters, waits, and exits without a meaningful carrier or conceptual reason for the cut. Adjacent scenes must preserve the viewer's mental model through a shared node, connector, color role, spatial current, camera path, or visibly caused handoff when legal semantics permit it.
  11. Mark idle or decorative motion as failed when wobble, breathing, floating, pulsing, drifting, or looping effects continue without revealing, comparing, transforming, connecting, causing, or handing off information.
  12. Mark choreography as failed when elements enter simultaneously, in arbitrary source order, or with identical card-grid motion that ignores reasoning hierarchy. Verify that prerequisites lead consequences, rules lead exceptions, and the most important distinction receives the first or strongest movement.
  13. Verify that key results receive a readable still hold and that transitions use a restrained, consistent vocabulary. Reject uncaused direction reversals, ping-pong movement, random zoom/rotation, and novelty transitions that do not communicate a conceptual change.
  14. Reject motion that creates false legal meaning: unsupported morphs suggesting identity, nesting suggesting inclusion, arrows suggesting causation or direction, or animation order suggesting priority or procedure that the source does not establish.
  15. If any page fails, fix the composition, scene timing, information design, choreography, or shared visual system and rerun the affected animation. If the fix touches shared animation behavior or tokens, rerun `pnpm animation:pages` for all animations. Continue until every contact sheet and every full-resolution page passes inspection.
  16. Use `--at <0..1>` only when the default stable frame at `0.82` is not the scene's intended complete teaching state. Record why a different ratio is correct; never use it to conceal an animation defect.
  17. Mark focal emphasis as failed when an important rule or connecting factor is distinguished only by text color, bold weight, solid fill, or border color. Require at least two nearby semantic channels and confirm the icon, locator, annotation, connector, enclosure, or motion cue clearly belongs to that exact phrase.
  18. Mark the stable or final frame as failed when an authored summary bar, subtitle, conclusion card, badge, or other overlay covers, intersects, crowds, or visually suppresses any teaching node. Verify the authored composition with player controls visible and keep essential content outside the bottom control-safe zone.
  19. For a scene with a long stable phase, verify its primary focal rule either retains one restrained semantic attention cue or uses deliberate stillness for a documented climax. Reject motion applied to the text baseline, more than two competing persistent cues, continuous scale/opacity breathing, or movement that has no legal meaning.
  20. Run `pnpm animation:pages <animation-id> --motion` whenever persistent emphasis is added or changed. Inspect the three checkpoint frames for every scene: the teaching layout must remain stable and readable, while at least one authored focal cue changes phase, position, or progress where sustained emphasis is intended.
- Do not proceed to publishing or report the animation complete while any captured page is uninspected, defective, or unverified.
- After the page-still loop passes, verify the published still set before building:
  1. Confirm the carrier-local path is exactly `<md-dir>/animation/<md-basename>/<version>/`, where `<version>` is a sortable timestamp such as `20260730T143214Z`.
  2. Confirm there is one full-resolution PNG per semantic scene, named `<scene-id>.png`, and no scene is represented only by a contact-sheet crop.
  3. Confirm `manifest.json` records the animation ID, dimensions, generation time, and exact scene ID, title, frame, and filename mapping.
  4. Open each published PNG at original resolution and confirm it is byte-for-byte or visually identical to the approved final frame; promotion must not resize, crop, recompress, or change the frame.
  5. Confirm the MD/MDX renders every PNG directly in scene order with meaningful alt text and relative paths. A filename link, hidden disclosure, `.artifacts` reference, broken image, stale version reference, or missing scene is a failure.
  6. When updating an animation, confirm the carrier references only the new fully validated version and that the prior version remains available unless cleanup was explicitly requested.
- Inspect the page at narrow and wide widths.
- Verify tables do not overflow unexpectedly and flow diagrams remain legible.
- Test memory challenge: toggle the checkbox, confirm `.answer-node` blur, and confirm hover reveal.
- Test `trigger-link-1` and `trigger-link-2` hover emphasis when the page uses `VisualFlow`.
- Test the embedded Remotion player and rendered final-frame images at narrow and wide widths; verify scene navigation, playback, reduced-size layout, image loading, aspect ratio, and readable static-state sizing without a copied iframe.
- Open every scene-specific iframe URL and verify `?scene=<key>` selects the expected visible page number and title. Test repeated uses of the same route with different scene keys independently; an invalid key silently falling back to page 01 is a failure.
- Check PageTitle quick actions, floating TOC, and any widescreen layout override touched by the change.

## Note-embed checks

- Require every new player scene to expose a unique, stable, descriptive kebab-case ID. Verify durable iframe URLs use semantic keys such as `?scene=first-instance`; allow displayed numbers such as `?scene=02` only for unmigrated legacy animations. Do not append prose or punctuation to the key.
- Require verified `https://inkloomer.github.io/inkloom/.../?scene=<key>` URLs for durable SiYuan, portable Markdown, or published Markdown embeds. Never use branch, preview, or repository URLs.
- Allow `http://localhost:4321/inkloom/.../?scene=<key>` only for an explicitly requested temporary pre-publication workflow. Record every temporary iframe and do not report the note portable, published, or finished until its host is replaced and reverified.
- Read each inserted iframe block and nearby siblings after writing. Confirm knowledge-point order, exact host, route, scene query, visible scene number, and scene title.

## Deployment handoff

- After the production build passes, commit and push the changed page, player, Remotion source, and carrier-local versioned final-frame assets together. The `main` branch deploys to GitHub Pages.
- Confirm the deployed page at `https://inkloomer.github.io/inkloom/<page-route>/` before reporting it as uploaded. The page itself is the embed target; do not hand the user iframe markup to paste manually.

## Commands

```bash
astro dev --background
astro dev status
astro dev logs
astro dev stop
pnpm animation:pages <animation-id>
pnpm animation:pages <animation-id> --motion
pnpm animation:pages
pnpm build
```

Use page-still QA first, then the dev server for responsive route and interaction checks. Use `pnpm build` as the final production-oriented gate; capture the first actionable error instead of hiding it behind a generic failure summary. Report the inspected artifact directory and any non-default capture ratio in the handoff.
