# InkLoom validation checklist

Run the smallest relevant checks after an edit, then run the full build when changing shared components, routing, styles, or many MDX pages.

## Structural checks

- Run `pnpm animation:styles`. Every new animation node must have a `visual-direction.json` beside `remotion/`; exact fingerprints must not duplicate another node. A repeated family is allowed only when the palette, typography, composition, surface, motion, or transition is visibly and materially different.
- Confirm new nodes import neutral runtime helpers rather than `src/animations/shared/legal-visual.tsx`; the latter is a legacy compatibility layer.
- Confirm changed files are under the intended InkLoom area.
- Confirm every imported component exists and its props match the implementation.
- Confirm local images exist and use the intended relative `./assets/...` path.
- Confirm raw legal material was first processed with `legal-marknote` in its user-supplied original file, while an already structured Markdown note was not processed again. Confirm the note and its assets remain at that original location and are absent from the website carrier.
- Confirm there are exactly two Remotion explainers, each with a focused legal learning objective, a stable `animation.meta.ts`, a source under `src/animations/<subject>/<chapter>/<animation-id>/remotion/`, and a direct Astro/React player embed in its own thin MDX carrier.
- Confirm AVIF publication has not changed the original full-length video composition, video encoding/publication path, total duration, or the existing scene pagination and semantic deep-link format. Do not accept per-scene video output as a substitute for the original video.
- Confirm the MDX carrier contains only the animation component import and frontmatter. It must not contain `## 动态...` description titles (such as `## 动态判断路径` or `## 动态选择路径`) or `## 场景终帧` sections. Animated AVIF companions belong under the public asset contract, not in carrier prose.
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
  21. Check the rendered node against its `visual-direction.json`: one MDX node should read as one coherent visual language, while a neighboring node should visibly avoid the same background, typography, palette, headline placement, surface, and primary motion fingerprint.
- Do not proceed to publishing or report the animation complete while any captured page is uninspected, defective, or unverified.
- After the page-still loop passes, verify the animated AVIF set before building:
  1. Follow [animated-avif.md](animated-avif.md) and run `pnpm animation:publish-avif <animation-id>` after inspection of the PNG QA captures. Do not hand-build the public directory or manifest.
  2. Confirm `public/animation-avif/<animation-id>/` contains one q45/CRF35 animated AVIF named `<scene-id>.avif` for every existing semantic scene plus `manifest.json`; no numeric-only or title-derived filename is allowed, and no per-scene video is generated by this step.
  3. Confirm the manifest records animation and composition IDs, generation time, `format: "animated-avif"`, `quality: 45`, `crf: 35`, 2560x1440 dimensions, source/target fps, `loopCount: 1`, and exact scene ID/title/frame range/frame count/duration/file-size mappings.
  4. Re-open every file with FFprobe and an AVIF-capable animated-image reader. Verify frame count, dimensions, frame timing, and loop count, then inspect first/middle/final frames at original resolution. Reject blank frames, smeared text, broken connectors, color hierarchy changes, or an exit-tail final frame.
  5. Confirm the shared player maps each unchanged semantic scene ID and page number to its original video range and matching AVIF, remembers the media tab, and exposes working replay, infinite loop, copy Markdown, copy image, and SiYuan script actions. A changed page order/range, split replacement video, missing asset, stale manifest, static AVIF, native `<img>` pause claim, or restored final-frame carrier block is a failure.
- Inspect the page at narrow and wide widths.
- Verify tables do not overflow unexpectedly and flow diagrams remain legible.
- Test memory challenge: toggle the checkbox, confirm `.answer-node` blur, and confirm hover reveal.
- Test `trigger-link-1` and `trigger-link-2` hover emphasis when the page uses `VisualFlow`.
- Test the embedded Remotion player and animated AVIF surface at narrow and wide widths; verify scene navigation, playback, mode persistence, replay/loop behavior, copy actions, image loading, aspect ratio, and reduced-size readability.
- Open every scene-specific iframe URL and verify `?scene=<key>` selects the expected visible page number and title. Test repeated uses of the same route with different scene keys independently; an invalid key silently falling back to page 01 is a failure.
- Check PageTitle quick actions, floating TOC, and any widescreen layout override touched by the change.

## Note-embed checks

- Require every new player scene to expose a unique, stable, descriptive kebab-case ID. Verify durable iframe URLs use semantic keys such as `?scene=first-instance`; allow displayed numbers such as `?scene=02` only for unmigrated legacy animations. Do not append prose or punctuation to the key.
- Require verified `https://inkloomer.github.io/inkloom/.../?scene=<key>` URLs for durable SiYuan, portable Markdown, or published Markdown embeds. Never use branch, preview, or repository URLs.
- Allow `http://localhost:4321/inkloom/.../?scene=<key>` only for an explicitly requested temporary pre-publication workflow. Record every temporary iframe and do not report the note portable, published, or finished until its host is replaced and reverified.
- Read each inserted iframe block and nearby siblings after writing. Confirm knowledge-point order, exact host, route, scene query, visible scene number, and scene title.

## Deployment handoff

- After the production build passes, commit and push the changed page, player, Remotion source, animated AVIFs/manifests, and SiYuan controller together. The `main` branch deploys to GitHub Pages.
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
pnpm animation:publish-avif <animation-id>
pnpm animation:publish-avif
pnpm build
```

Use page-still QA first, then the dev server for responsive route and interaction checks. Use `pnpm build` as the final production-oriented gate; capture the first actionable error instead of hiding it behind a generic failure summary. Report the inspected artifact directory and any non-default capture ratio in the handoff.
