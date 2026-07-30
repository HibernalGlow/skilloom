---
name: inkloom-dev
description: "Develop and maintain the InkLoom Astro Starlight legal-learning site: create and publish independent Remotion explainers from completed Markdown notes, embed published explainers into explicitly requested existing SiYuan notes, and maintain the site MDX carriers, components, routes, and responsive styles. Use when working inside the InkLoom repository or its src/content/docs, src/animations, src/components, notes, SiYuan notes, and .agents/skills areas."
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

## Working sequence

1. Locate the user-supplied Markdown source file at its existing path and the intended independent animation and website areas. The note may live outside InkLoom; it is source evidence, not InkLoom MDX input.
2. Determine whether the note is raw material or already processed by `legal-marknote`. Use `legal-marknote` only for raw material and edit its result in that original file; do not process an already structured note again.
   - **If the Markdown has not yet been processed by `legal-marknote`**: after processing is complete, extract the key points and difficult points (重点与难点) from the structured note. For each topic (专题), create a separate summary file named `<topic-name>.important.md` (e.g., `专题一 民事诉讼与民事诉讼法.important.md`) in the same directory as the source note. This file should contain a concise list of key and difficult points so that future animation work can reference these highlights without re-reading the full text.
   - **If the Markdown is already processed but no `.important.md` file exists**: proceed to extract key points and difficult points and create the corresponding `.important.md` file before starting animation work.
3. Preserve the site's base route: `base: '/inkloom'`. Every absolute MDX or Astro link must begin with `/inkloom/`; use relative asset paths such as `./assets/cover.png` for page-local images.
4. Read the source note, the target website page, its nearest `_meta.yml`, imported components, and relevant styles before editing. Choose two important or difficult points without copying the note into the site.
5. Before creating or modifying any Remotion file, read and follow `$remotion-best-practices`. Then load its relevant reference: React Markup for compositions or player components, Rendering for output or publishing, and Multimedia for image, audio, or video work. Do not write Remotion source before completing this step.
6. Follow [content-boundaries.md](references/content-boundaries.md). Keep the Markdown note and its assets in place, then create two independent Remotion explainers using [remotion-animation.md](references/remotion-animation.md).
7. Give each explainer a stable ID, a separate `src/animations/` directory, and its own thin MDX carrier page. The MDX exists only to route and embed the animation on InkLoom; it must not reproduce, convert, or relocate the note.
8. Complete the mandatory iterative page-still QA in [validation.md](references/validation.md) before calling any animation finished. Capture each changed animation with `pnpm animation:pages <animation-id>` and run `pnpm animation:pages <animation-id> --motion` whenever sustained emphasis is present or changed; after a batch or all animations are complete, run `pnpm animation:pages`. Inspect every contact sheet and full-resolution page, fix the animation source, and repeat until every page is visually correct.
9. After page-still QA passes, publish one readable final-frame PNG for every semantic scene beside its Markdown or MDX carrier. Use `<md-dir>/animation/<md-basename>/<version>/<scene-id>.png`, render every image directly in the carrier with a relative path, and keep a timestamped version manifest as defined in [remotion-animation.md](references/remotion-animation.md). Do not expose `.artifacts` paths as content assets.
10. Validate the responsive player, rendered final-frame images, and production build only after the page-still loop passes. Commit and push the animation sources, player components, versioned final-frame assets, metadata, and MDX carriers to the InkLoom repository. Verify the production page URL before reporting it as published.
11. When the user explicitly asks to embed animations in an existing SiYuan note or Markdown file, map each knowledge-point anchor to its matching animation scene and use its semantic deep link, such as `?scene=first-instance`; do not insert only one generic first-page player when several distinct points are explained. For SiYuan, follow [siyuan-embed.md](references/siyuan-embed.md), use `$siyuan-cli`, and do not edit unrelated note content.
12. Validate the changed pages and any SiYuan embeds with [validation.md](references/validation.md). Report any unverified route, animation page, final-frame asset version, deployment URL, or SiYuan block insertion.

## Repository conventions

- Framework: Astro Starlight; content is authored as MDX.
- Markdown notes: remain independent files at the user-supplied original path. `legal-marknote` may edit that file in place, but this skill never converts or relocates it as website content.
- Website carriers: `src/content/docs/`; each animation page is a thin MDX route and not a copy of its source note.
- Sidebar: `starlight-auto-sidebar`; directory labels and ordering live in `_meta.yml` files.
- Animation runtime: Remotion 4 with `@remotion/player`, embedded through Astro and React components. Keep each explainer in `src/animations/<subject>/<chapter>/<animation-id>/remotion/` and its metadata beside `remotion/`.
- Layout overrides: `src/components/overrides/PageTitle.astro` and `src/styles/custom.css`.
- Local development: `astro dev --background`.
- Animation page QA: `pnpm animation:pages <animation-id>` for changed animations and `pnpm animation:pages` for a completed batch.
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
- Do not move source-note images into `src/content/docs/` or a shared global folder. Animation-specific media belongs with its own animation source.
- Do not put animation sources or player components in a generic scratch folder. Use stable animation IDs and the independent directory contract in [content-boundaries.md](references/content-boundaries.md).
- Do not generate a generic video merely because an animation was requested. The animation must teach a specific completed legal note's key point or difficult point and must not add unsupported legal conclusions.
- Do not create or modify a Remotion composition, scene, player, or render command before reading `$remotion-best-practices` and the task-relevant React Markup, Rendering, or Multimedia reference.
- Do not treat a successful build, render command, or contact-sheet generation as visual proof. Inspect every captured page at full resolution, fix all visible or semantic defects, and rerun the capture until no defect remains.
- Do not leave approved final-frame screenshots only in `.artifacts`, hide them behind links or disclosure widgets, or reference a mutable unversioned filename from the carrier. Publish and directly render one versioned final frame per semantic scene beside the MD/MDX file.
- Do not accept low canvas utilization. Treat a page as failed when the primary teaching structure is clustered into one corner, side, or narrow band while a large region has no semantic, pacing, or focus function. Enlarge, redistribute, or restructure the visual relationships across the usable 16:9 canvas while preserving intentional breathing room.
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
- Do not report an uploaded website or public URL before the relevant commit is deployed successfully.
- Do not insert an iframe into an existing SiYuan note or Markdown file unless the user explicitly requests that exact edit. Use `$siyuan-cli` for SiYuan and add new iframe blocks instead of rewriting legal-content blocks. Use verified production URLs for durable embeds; allow localhost only for an explicitly temporary pre-publication workflow and replace it before calling the note portable, published, or finished. Never use branch, preview, or repository URLs.
- Do not omit the `scene` query when an iframe is intended to explain one specific knowledge point. New animations must expose stable semantic kebab-case IDs such as `first-instance`; use a displayed number such as `?scene=02` only for a legacy animation that has not yet been migrated. Verify the link opens the intended page because an invalid key silently falls back to the first scene.
- Keep legal conclusions and source wording intact unless the user explicitly asks for substantive editing.

## References

- [components.md](references/components.md): component props and interaction hooks.
- [content-boundaries.md](references/content-boundaries.md): Markdown-note, animation-source, and MDX-carrier separation and move-safe IDs.
- [remotion-animation.md](references/remotion-animation.md): legal-note-to-Remotion workflow, independent source placement, page embedding, and deployment handoff.
- [siyuan-embed.md](references/siyuan-embed.md): explicit note-edit authorization, knowledge-point-to-scene mapping, semantic iframe deep links, and SiYuan/Markdown verification.
- [validation.md](references/validation.md): mandatory iterative page-still QA, responsive player, build, route, and compatibility checks.
