---
name: inkloom-dev
description: "Develop and maintain the InkLoom Astro Starlight legal-learning site: create and publish independent Remotion explainers from completed Markdown notes, embed published explainers into explicitly requested existing SiYuan notes, and maintain the site MDX carriers, components, routes, and responsive styles. Use when working inside the InkLoom repository or its src/content/docs, src/animations, src/components, notes, SiYuan notes, and .agents/skills areas."
---

# InkLoom development

Use this skill before editing InkLoom animation pages, Remotion sources, Astro components, layout overrides, or custom CSS. Treat the repository's existing components and content conventions as the source of truth; do not replace them with generic Starlight patterns without checking the surrounding implementation.

## Working sequence

1. Locate the user-supplied Markdown source file at its existing path and the intended independent animation and website areas. The note may live outside InkLoom; it is source evidence, not InkLoom MDX input.
2. Determine whether the note is raw material or already processed by `legal-marknote`. Use `legal-marknote` only for raw material and edit its result in that original file; do not process an already structured note again.
3. Preserve the site's base route: `base: '/inkloom'`. Every absolute MDX or Astro link must begin with `/inkloom/`; use relative asset paths such as `./assets/cover.png` for page-local images.
4. Read the source note, the target website page, its nearest `_meta.yml`, imported components, and relevant styles before editing. Choose two important or difficult points without copying the note into the site.
5. Before creating or modifying any Remotion file, read and follow `$remotion-best-practices`. Then load its relevant reference: React Markup for compositions or player components, Rendering for output or publishing, and Multimedia for image, audio, or video work. Do not write Remotion source before completing this step.
6. Follow [content-boundaries.md](references/content-boundaries.md). Keep the Markdown note and its assets in place, then create two independent Remotion explainers using [remotion-animation.md](references/remotion-animation.md).
7. Give each explainer a stable ID, a separate `src/animations/` directory, and its own thin MDX carrier page. The MDX exists only to route and embed the animation on InkLoom; it must not reproduce, convert, or relocate the note.
8. Complete the mandatory iterative page-still QA in [validation.md](references/validation.md) before calling any animation finished. Capture each changed animation with `pnpm animation:pages <animation-id>`; after a batch or all animations are complete, run `pnpm animation:pages`. Inspect every contact sheet and full-resolution page, fix the animation source, and repeat until every page is visually correct.
9. Validate the responsive player and production build only after the page-still loop passes. Commit and push the animation sources, player components, metadata, and MDX carriers to the InkLoom repository. Verify the production page URL before reporting it as published.
10. Only when the user explicitly asks to add the published animations to an existing SiYuan note, follow [siyuan-embed.md](references/siyuan-embed.md). Use `$siyuan-cli` to locate the exact source blocks and insert each production iframe in its correct sequence and position; do not edit the note otherwise.
11. Validate the changed pages and any SiYuan embeds with [validation.md](references/validation.md). Report any unverified route, animation page, deployment URL, or SiYuan block insertion.

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
- Do not change `--at` merely to hide unfinished, clipped, overlapping, or mistimed animation content. Change the capture ratio only when the scene's intended stable teaching frame genuinely occurs elsewhere, and still fix defects in the composition itself.
- Do not report an uploaded website or public URL before the relevant commit is deployed successfully.
- Do not insert an iframe into an existing SiYuan note unless the user explicitly requests that exact edit. Use `$siyuan-cli`, insert new sibling blocks instead of rewriting the source blocks, and use only a verified `https://inkloomer.github.io/inkloom/...` production URL. Never insert `localhost`, preview, branch, or repository URLs.
- Keep legal conclusions and source wording intact unless the user explicitly asks for substantive editing.

## References

- [components.md](references/components.md): component props and interaction hooks.
- [content-boundaries.md](references/content-boundaries.md): Markdown-note, animation-source, and MDX-carrier separation and move-safe IDs.
- [remotion-animation.md](references/remotion-animation.md): legal-note-to-Remotion workflow, independent source placement, page embedding, and deployment handoff.
- [siyuan-embed.md](references/siyuan-embed.md): explicit existing-note authorization, ordered production-iframe insertion through `$siyuan-cli`, and verification.
- [validation.md](references/validation.md): mandatory iterative page-still QA, responsive player, build, route, and compatibility checks.
