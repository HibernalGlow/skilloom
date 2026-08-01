---
name: inkloom-dev
description: "Develop and maintain the InkLoom Astro Starlight legal-learning site: create and publish independent Remotion explainers from completed Markdown notes or a supplied SiYuan block ID, insert a published animated image immediately after that exact SiYuan block, and maintain the site MDX carriers, components, routes, and responsive styles. Use when working inside the InkLoom repository or its src/content/docs, src/animations, src/components, notes, SiYuan notes, and .agents/skills areas."
---

# InkLoom development

Use this skill before editing InkLoom animation pages, Remotion sources, Astro components, layout overrides, or custom CSS. Treat the repository's existing components and content conventions as the source of truth; do not replace them with generic Starlight patterns without checking the surrounding implementation.

## Remotion skill routing

Use the installed Remotion skills as the default implementation toolkit for InkLoom animations. Do not hand-roll a familiar animation pattern before checking whether the relevant skill or Remotion Bits example already provides it.

- Load `$remotion-best-practices` first for every task that touches Remotion. It is the routing entry point, not an optional reading list.
- Load `$remotion-create` when scaffolding a new Remotion project or composition. Existing InkLoom pages already have their project structure, so do not scaffold a second project inside the site.
- Load `$remotion-markup` when writing or refactoring Remotion React markup, timing, layout, effects, or transitions.
- Strongly prefer `$remotion-bits` for reusable motion patterns, especially its **Text Animations**. Use its example-first discovery flow before writing custom frame math, then adapt `AnimatedText` for short headings, legal terms, section labels, and key callouts; use `TypeWriter` for terminal-like sequences and `StaggeredMotion` for repeated labels, cards, or nodes. Keep text concise and readable, and do not animate every paragraph merely because a text primitive is available.
- Use `@remotion/transitions` and `@remotion/effects` when the scene needs their specific capabilities, while keeping the semantic diagram and legal meaning primary. Do not add custom equivalents when an installed package or Remotion Bits primitive already covers the behavior.

## Visual direction and node boundaries

- Treat one MDX carrier and its Remotion directory as one visual node. Keep one coherent visual language across that node's scenes; choose a materially different visual fingerprint for each new neighboring node.
- Read [visual-direction.md](references/visual-direction.md) before authoring a new node. Choose a direction because it makes the legal relationship easier to understand, then record the choice in `visual-direction.json` beside `remotion/`.
- When a node introduces a direction that is not yet represented in `/demo/`, add the original node to the demo catalog. Reuse its existing composition for the preview and link to its existing MDX route; do not create a second demo-only composition or MDX page. Give the catalog entry a visual-style name that is independent from the node's legal topic, and record this relationship and style name in the manifest's `catalog` field.
- Share only frame conversion, scene timing, `Sequence` plumbing, render registration, and optional style-neutral motion primitives. Keep background, fonts, palette, surfaces, cards, headings, composition grammar, transitions, and art direction inside the node.
- Use `src/animations/shared/remotion-runtime.tsx` for new neutral runtime mechanics. Treat `src/animations/shared/legal-visual.tsx` as legacy compatibility and do not import it for a new node.
- Choose each scene's visual anchor from its legal structure: a concept icon is only one option beside a path, fork, role pair, boundary, timeline, comparison axis, or typographic sequence. Never force every scene into a main-icon template.
- Make typography carry semantics beyond color. Across a multi-scene node, use a deliberate mix such as soft highlight, thin underline, label block, stamp, and external negation; never place thick circles or strike-through marks over glyphs.
- Prefer the most direct legal diagram over a novel metaphor that needs prose to explain. Read [visual-direction.md](references/visual-direction.md) for the full anchor, theme, and text-treatment contract.
- Run `pnpm animation:styles` before page QA. Exact visual fingerprints must be unique; a repeated family requires an explicit visual distinction review.

## Direct SiYuan block ID workflow

Treat a bare SiYuan block ID such as `20260729232455-l0z16r1` as authorization to complete the matching animation and insert its published animated image immediately after that exact block.

1. Load `$siyuan-cli`. Read the block with `siyuan block get` and `siyuan block kramdown`, then use its legal content to identify the matching InkLoom animation and semantic scene. Nearby content may be read only when the block itself is insufficient to understand the rule.
2. Do not expand the insertion anchor into a heading section, quote container, list, or descendant range. The supplied ID is always the source anchor, regardless of block type.
3. If a matching animation exists, add or improve the semantic scene that explains this block. If none exists, create the required animation node, thin MDX carrier, and semantic scene under the established subject/chapter hierarchy. Author the legal visualization and choose the scene manually; do not delegate those judgments to an insertion script.
4. Complete visual QA, publish the scene AVIF, commit and push the InkLoom work, and verify its production URL before changing SiYuan. Use the durable image URL `https://inkloomer.github.io/inkloom/animation-avif/<animation-id>/<scene-id>.avif`.
5. Follow the direct-ID procedure in [siyuan-embed.md](references/siyuan-embed.md). Insert one Markdown image block as the immediate next sibling of the supplied block ID, then verify actual sibling order with `siyuan block children`.
6. Use `pnpm siyuan:embed-scene -- --target-id <block-id> --animation-id <animation-id> --scene-id <scene-id>` for block lookup, parent-ID extraction, duplicate detection, CLI dry-run, insertion, and final order verification. Add `--apply` only after the production AVIF is deployed. Keep animation creation and the choice of semantic scene outside the script.

## Working sequence

1. Locate the user-supplied Markdown source file at its existing path and the intended independent animation and website areas. The note may live outside InkLoom; it is source evidence, not InkLoom MDX input.
2. Determine whether the note is raw material or already processed by `legal-marknote`. Use `legal-marknote` only for raw material and edit its result in that original file; do not process an already structured note again.
   - **If the Markdown has not yet been processed by `legal-marknote`**: after processing is complete, extract the key points and difficult points (重点与难点) from the structured note. For each topic (专题), create a separate summary file named `<topic-name>.important.md` (e.g., `专题一 民事诉讼与民事诉讼法.important.md`) in the same directory as the source note. This file should contain a concise list of key and difficult points so that future animation work can reference these highlights without re-reading the full text.
   - **If the Markdown is already processed but no `.important.md` file exists**: proceed to extract key points and difficult points and create the corresponding `.important.md` file before starting animation work.
3. Preserve the site's base route: `base: '/inkloom'`. Every absolute MDX or Astro link must begin with `/inkloom/`; use relative asset paths such as `./assets/cover.png` for page-local images.
4. Read the source note, the target website page, its nearest `_meta.yml`, imported components, and relevant styles before editing. Choose two important or difficult points without copying the note into the site.
5. Before creating or modifying any Remotion file, read and follow `$remotion-best-practices`. Then load its relevant reference: React Markup for compositions or player components, Rendering for output or publishing, and Multimedia for image, audio, or video work. Do not write Remotion source before completing this step.
6. Follow [content-boundaries.md](references/content-boundaries.md) and [visual-direction.md](references/visual-direction.md). Keep the Markdown note and its assets in place, then create two independent Remotion explainers using [remotion-animation.md](references/remotion-animation.md). Give each animation node its own `visual-direction.json`.
7. Give each explainer a stable ID, a separate `src/animations/` directory, and its own thin MDX carrier page. The MDX exists only to route and embed the animation on InkLoom; it must not reproduce, convert, or relocate the note. If this node adds a new visual direction, register that original player and MDX route in the `/demo/` catalog instead of building a parallel demo node. Name the Demo entry after the visual style, not the legal concept taught by the source node.
8. Complete the mandatory iterative page-still QA in [validation.md](references/validation.md) before calling any animation finished. Capture each changed animation with `pnpm animation:pages <animation-id>` and run `pnpm animation:pages <animation-id> --motion` whenever sustained emphasis is present or changed; after a batch or all animations are complete, run `pnpm animation:pages`. Inspect every contact sheet and full-resolution page, fix the animation source, and repeat until every page is visually correct.
9. Preserve any existing full-length video composition and the `SCENES` pagination contract. When rewriting a published animation's theme, keep its `animation-id`, semantic scene IDs, scene order, public AVIF filenames, MDX route, and deep-link format stable so existing SiYuan and resource-document references continue to resolve. Do not create new public identities merely to replace the visual implementation.
10. After page-still QA passes, follow [animated-avif.md](references/animated-avif.md) and run `pnpm animation:publish-avif <animation-id>`. Publish one q45 (AV1 CRF 35), 2560x1440, once-playing animated AVIF per existing semantic scene under `public/animation-avif/<animation-id>/`; never restore the retired static final-frame publishing flow.
11. Validate the responsive video/AVIF switcher, replay and loop behavior, copy actions, persisted media preference, public assets, and production build only after page-still QA and animated-AVIF publication pass. Commit and push the animation sources, player components, metadata, MDX carriers, animated AVIFs, manifests, and SiYuan controller script to InkLoom. Verify the production page and direct AVIF URLs before reporting them as published.
12. For interactive iframe embedding requests that are not the bare block-ID animated-image workflow, map each knowledge-point anchor to its matching animation scene and use its semantic deep link, such as `?scene=first-instance`; do not insert only one generic first-page player when several distinct points are explained. For SiYuan, follow [siyuan-embed.md](references/siyuan-embed.md), use `$siyuan-cli`, and do not edit unrelated note content.
13. Validate the changed pages and any SiYuan embeds with [validation.md](references/validation.md). Report any unverified route, animation page, animated-AVIF asset, deployment URL, or SiYuan block insertion.

## Repository conventions

- Framework: Astro Starlight; content is authored as MDX.
- Markdown notes: remain independent files at the user-supplied original path. `legal-marknote` may edit that file in place, but this skill never converts or relocates it as website content.
- Website carriers: `src/content/docs/`; each animation page is a thin MDX route containing only the animation component import and frontmatter — not a copy of its source note. Do not add `## 动态...` description titles or `## 场景终帧` / final-frame sections; the carrier exists only to route and embed the animation.
- Sidebar: `starlight-auto-sidebar`; directory labels and ordering live in `_meta.yml` files.
- Animation runtime: Remotion 4 with `@remotion/player`, embedded through Astro and React components. Keep each explainer in `src/animations/<subject>/<chapter>/<animation-id>/remotion/` and its metadata beside `remotion/`.
- Animation readability: at a 1920x1080 authoring canvas, focal legal concepts and primary node labels must be at least 30 px; knowledge-bearing conditions, explanations, axis labels, and branch labels must be at least 22 px. Only non-semantic metadata such as scene numbers, English eyebrows, coordinates, and labels like `STATION 01` may use 15-18 px.
- Animation duration: size each semantic scene from its information density rather than targeting a fixed runtime. Start with `1.2 + 0.9 * sequentialBeats + 0.35 * denseReadingGroups + 0.5 * branchHandoffs` seconds, then tune by motion QA; `/objective/civil-procedure/04/legal-jurisdiction/?scene=mediation-confirmation` is the comfort reference at about 5.5 seconds for four ordered reasoning beats and a roughly one-second stable result. A single scene must not exceed 20 seconds without explicit approval, but the complete composition is the natural sum of its scenes and may exceed 20 seconds. Preserve key legal wording and never accelerate entries or reading merely to hit a nominal number.
- Layout overrides: `src/components/overrides/PageTitle.astro` and `src/styles/custom.css`.
- Local development: `astro dev --background`.
- Animation page QA: `pnpm animation:pages <animation-id>` for changed animations and `pnpm animation:pages` for a completed batch.
- Animation style audit: `pnpm animation:styles` before page-still QA; this checks node-level visual fingerprints and legacy exceptions.
- Visual catalog: `/demo/` is an index of visual styles demonstrated by real animation nodes. A featured entry previews the original composition and opens the original MDX carrier; its display title names the visual style, never the node's legal topic, and it does not own a duplicate Remotion source or route.
- Animated AVIF publication: `pnpm animation:publish-avif <animation-id>` for changed animations and `pnpm animation:publish-avif` for a completed batch; the default contract is q45/CRF35, 2560x1440, 15 fps, and one encoded play.
- Build verification: `pnpm build`.

## Interactive page contracts

- Use the memory challenge contract only when the page is intended to support recall: a hidden `#memory-challenge-toggle` checkbox must precede `.note-content-wrapper`, and answer content must use `.answer-node`.
- Keep hover-linked flow classes stable. `trigger-link-1` and `trigger-link-2` are semantic hooks shared by action blocks and visual-flow paths.
- Use `<details class="interactive-card">` for progressive disclosure or self-testing instead of adding page-specific JavaScript.
- Preserve responsive behavior: tables remain readable, flow diagrams may use the provided responsive components, and page-local images must resolve through Astro's asset pipeline.
- Use the existing Remotion player pattern for legal animations. Embed each player in its website-only MDX carrier; do not make the user copy, paste, or maintain an iframe.

## Page title and layout boundaries

- `PageTitle.astro` owns the floating tick TOC, quick actions, copy HTML / iframe actions, and memory-toggle affordance.
- `custom.css` owns the widescreen layout override. Keep the full-width rule scoped to the intended breakpoint and do not hide the native content structure without checking mobile behavior.
- When copying content for Obsidian or Notion, keep required styles inline or in the page's established compatibility path; do not assume runtime JavaScript is available.

## Guardrails

- Do not use bare absolute paths such as `/objective/...`; they produce GitHub Pages 404s.
- Do not convert, copy, or relocate a Markdown note, its tables, or its assets into MDX. The note and the website animation are separate deliverables.
- Do not duplicate an existing component's CSS or silently change its props; inspect the component contract first.
- Do not copy a shared legal visual theme into a new node. Reuse neutral runtime mechanics only, and keep one node's chosen visual language stable across its scenes.
- Do not create a demo-only clone when a real node introduces a new direction. Add the original node to the catalog, mark `catalog.source` as `original-node` in `visual-direction.json`, and give `catalog.title` a genuine style name rather than copying the node title, legal concept, chapter heading, or scene title.
- Do not move source-note images into `src/content/docs/` or a shared global folder. Animation-specific media belongs with its own animation source.
- Do not put animation sources or player components in a generic scratch folder. Use stable animation IDs and the independent directory contract in [content-boundaries.md](references/content-boundaries.md).
- Do not generate a generic video merely because an animation was requested. The animation must teach a specific completed legal note's key point or difficult point and must not add unsupported legal conclusions.
- Do not create or modify a Remotion composition, scene, player, or render command before reading `$remotion-best-practices` and the task-relevant React Markup, Rendering, or Multimedia reference.
- Do not treat a successful build, render command, or contact-sheet generation as visual proof. Inspect every captured page at full resolution, fix all visible or semantic defects, and rerun the capture until no defect remains.
- Do not restore `animation:publish-stills`, versioned q60 final-frame assets, or `## 场景终帧` blocks. Page-still PNGs remain QA-only under `.artifacts`; public companion media is the per-scene animated AVIF set defined in [animated-avif.md](references/animated-avif.md).
- Do not add `## 动态...` description titles (such as `## 动态判断路径` or `## 动态选择路径`) or `## 场景终帧` sections to an MDX carrier. The carrier must contain only the animation component import and frontmatter; the shared player owns video/AVIF presentation and copy actions.
- Do not accept low canvas utilization. Treat a page as failed when the primary teaching structure is clustered into one corner, side, or narrow band while a large region has no semantic, pacing, or focus function. Enlarge, redistribute, or restructure the visual relationships across the usable 16:9 canvas while preserving intentional breathing room.
- Do not shrink knowledge-bearing text to make a layout fit. On a 1920x1080 canvas, keep focal legal concepts and primary node labels at 30 px or larger and supporting legal explanations, conditions, axis labels, and branch labels at 22 px or larger. Reserve 15-18 px for non-semantic metadata only. Preserve visual quality by reflowing the diagram, relocating headings, reallocating underused space, or removing decorative metadata before editing copy. Keep wording that carries legal conditions, exceptions, roles, and relationships intact; trim only redundancy that does not change the knowledge structure. A font-size fix that creates crowding, clipping, weak hierarchy, or visual imbalance still fails QA.
- Do not force every scene toward 15 or 20 seconds, and do not cap the sum of a multi-scene composition at 20 seconds. Estimate each semantic scene from its ordered reasoning beats, dense reading groups, and branch handoffs; then shorten dead holds or lengthen rushed reading after motion QA. A single scene over 20 seconds requires explicit approval and should normally be narrowed or split instead of accelerated past comfortable reading.
- Do not use a prose paragraph, sentence stack, or text-only principle/conclusion card as the main teaching object. Convert every core rule into meaningful visual grammar such as nodes and connectors, branches, nested containers, timelines, comparisons, transformations, or causal motion. Keep text subordinate as short labels, keywords, values, or at most one brief caption; decorative icons around prose do not satisfy this rule.
- Do not rely on highlighted words alone for concrete people, roles, institutions, documents, measures, actions, or outcomes. Pair readily recognizable concepts with semantically accurate icons or compact pictograms and make those visual tokens participate in the diagram or motion. Keep an adjacent short label when an icon could be ambiguous; icons supplement meaning but never substitute for the required relationship structure.
- Do not treat text color, bold weight, a solid fill, or a colored border as sufficient emphasis for a scene's focal rule. Give every high-priority concept at least two nearby semantic channels, such as an icon or pictogram plus a locator, enclosure, connector, annotation, spatial promotion, contrast pair, or purposeful motion cue.
- Do not show a plain table or table-like grid as an animation scene. Treat source tables as analysis input and redesign them as animated comparison lanes, grouped cards, axes, relationship maps, branches, or progressive transformations. Styling, coloring, rounding, or animating a static grid does not make it an acceptable visualization.
- Do not author scenes as an isolated stack of animated slides. Carry the legal argument across scene boundaries through a persistent node, connector, color role, spatial direction, camera path, or visibly caused action; use an intentional conceptual cut only when continuity would mislead.
- Do not add idle wobble, breathing, floating, pulsing, or decorative loops merely to keep the frame moving. A focal rule may retain one restrained semantic cue after entry—such as a locator trace, moving underline, boundary tracer, or connector traversal—while the text itself stays still and readable; otherwise hold still.
- Do not let an authored summary bar, conclusion card, subtitle, badge, or other overlay cover any teaching node in the stable or final frame. Put summaries in reserved layout space, reflow the scene, or replace content intentionally; also keep essential conclusions clear of the player's bottom control-safe zone.
- Do not animate every element at once or in arbitrary DOM order. Stage motion in the order the legal reasoning should be understood, let the most important or causally prior element lead, and give key conclusions a readable still hold.
- Do not use a morph, connector, movement direction, or transition that falsely implies identity, inclusion, causation, priority, or procedural order. Motion semantics must remain legally accurate.
- Do not change `--at` merely to hide unfinished, clipped, overlapping, or mistimed animation content. Change the capture ratio only when the scene's intended stable teaching frame genuinely occurs elsewhere, and still fix defects in the composition itself.
- Do not let connector arrows penetrate target nodes or stop short. When using the project's shared `FlowArrow` component, compute `width` so that `left + width` reaches the target node's left edge minus ~2 px; never reuse a hardcoded `width` from a different scene without recalculating the actual horizontal gap. A common mistake is copying a large default such as `340` px into a scene where the real node spacing is only 50–100 px, causing the arrow to pierce through the target node. Verify every arrow in the page-still QA.
- Do not report an uploaded website or public URL before the relevant commit is deployed successfully.
- Do not insert an iframe into an existing SiYuan note or Markdown file unless the user explicitly requests that exact edit. Use `$siyuan-cli` for SiYuan and add new iframe blocks instead of rewriting legal-content blocks. Use verified production URLs for durable embeds; allow localhost only for an explicitly temporary pre-publication workflow and replace it before calling the note portable, published, or finished. Never use branch, preview, or repository URLs.
- Do not omit the `scene` query when an iframe is intended to explain one specific knowledge point. New animations must expose stable semantic kebab-case IDs such as `first-instance`; use a displayed number such as `?scene=02` only for a legacy animation that has not yet been migrated. Verify the link opens the intended page because an invalid key silently falls back to the first scene.
- Keep legal conclusions and source wording intact unless the user explicitly asks for substantive editing.

## References

- [components.md](references/components.md): component props and interaction hooks.
- [animated-avif.md](references/animated-avif.md): required per-scene q45/CRF35 2560x1440 animated-AVIF publication, bounded parallel rendering, website controls, SiYuan controller, and asset verification without changing existing full video or pagination.
- [content-boundaries.md](references/content-boundaries.md): Markdown-note, animation-source, and MDX-carrier separation and move-safe IDs.
- [remotion-animation.md](references/remotion-animation.md): legal-note-to-Remotion workflow, independent source placement, page embedding, and deployment handoff.
- [siyuan-embed.md](references/siyuan-embed.md): explicit note-edit authorization, knowledge-point-to-scene mapping, semantic iframe deep links, and SiYuan/Markdown verification.
- [validation.md](references/validation.md): mandatory iterative page-still QA, responsive player, build, route, and compatibility checks.
- [visual-direction.md](references/visual-direction.md): node-level visual ownership, direction catalog, manifest contract, and diversity audit.
