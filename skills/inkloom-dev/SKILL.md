---
name: inkloom-dev
description: "Develop and maintain the InkLoom Astro Starlight legal-learning site: convert source notes to MDX, preserve source directories and assets, build and embed Remotion animations for key legal concepts, and maintain components, routes, and responsive styles. Use when working inside the InkLoom repository or its src/content/docs, src/animations, src/components, notes, and .agents/skills areas."
---

# InkLoom development

Use this skill before editing InkLoom MDX, Astro components, layout overrides, custom CSS, or imported note content. Treat the repository's existing components and content conventions as the source of truth; do not replace them with generic Starlight patterns without checking the surrounding implementation.

## Working sequence

1. Locate the InkLoom repository root and confirm the target is under `src/content/docs/`, `src/components/`, `src/styles/`, or another intentional project area.
2. Read the target page, its nearest `_meta.yml`, imported components, and relevant styles before editing.
3. Preserve the site's base route: `base: '/inkloom'`. Every absolute MDX or Astro link must begin with `/inkloom/`; use relative asset paths such as `./assets/cover.png` for page-local images.
4. Choose existing primitives from [components.md](references/components.md) before adding a new component. Keep legal meaning in MDX and visual behavior in the shared component or stylesheet.
5. For imported legal notes, first determine whether `legal-marknote` has already completed the source. If it is raw material, use `legal-marknote` before conversion. If it is already a structured legal note, do not run the conversion again; preserve that result and follow [content-conversion.md](references/content-conversion.md). In both cases preserve native tables, source assets, and hierarchy, and convert hand-written layouts into project components.
6. From the completed note's key and difficult points, create two focused Remotion animation explainers using [remotion-animation.md](references/remotion-animation.md). Put them in the mapped source-derived directories, embed their players in the same MDX page, and commit and push the page, sources, and components to the InkLoom repository.
7. Validate the changed page and run the build checklist in [validation.md](references/validation.md). Report any unverified route, asset, responsive behavior, or deployment URL.

## Repository conventions

- Framework: Astro Starlight; content is authored as MDX.
- Content: `src/content/docs/`.
- Legal-source preparation: use `legal-marknote` before converting a source note to InkLoom MDX.
- Sidebar: `starlight-auto-sidebar`; directory labels and ordering live in `_meta.yml` files.
- Animation runtime: Remotion 4 with `@remotion/player`, embedded through Astro and React components. Keep animation sources in `src/animations/<topic-slug>/remotion/`.
- Layout overrides: `src/components/overrides/PageTitle.astro` and `src/styles/custom.css`.
- Local development: `astro dev --background`.
- Build verification: `pnpm build`.

## Interactive page contracts

- Use the memory challenge contract only when the page is intended to support recall: a hidden `#memory-challenge-toggle` checkbox must precede `.note-content-wrapper`, and answer content must use `.answer-node`.
- Keep hover-linked flow classes stable. `trigger-link-1` and `trigger-link-2` are semantic hooks shared by action blocks and visual-flow paths.
- Use `<details class="interactive-card">` for progressive disclosure or self-testing instead of adding page-specific JavaScript.
- Preserve responsive behavior: tables remain readable, flow diagrams may use the provided responsive components, and page-local images must resolve through Astro's asset pipeline.
- Use the existing Remotion player pattern for legal animations. Embed the player in the target MDX page; do not make the user copy, paste, or maintain an iframe.

## Page title and layout boundaries

- `PageTitle.astro` owns the floating tick TOC, quick actions, copy HTML / iframe actions, and memory-toggle affordance.
- `custom.css` owns the widescreen layout override. Keep the full-width rule scoped to the intended breakpoint and do not hide the native content structure without checking mobile behavior.
- When copying content for Obsidian or Notion, keep required styles inline or in the page's established compatibility path; do not assume runtime JavaScript is available.

## Guardrails

- Do not use bare absolute paths such as `/objective/...`; they produce GitHub Pages 404s.
- Do not convert a semantic note table into a decorative flex layout.
- Do not duplicate an existing component's CSS or silently change its props; inspect the component contract first.
- Do not move source images into a shared global folder when they belong to one note; keep them under that note's `assets/` directory.
- Do not write converted MDX, copied assets, animation sources, or player components into a generic scratch folder. Derive their locations from the original note directory and the target content route, preserving the source tree's topic and chapter structure.
- Do not generate a generic video merely because an animation was requested. The animation must teach a specific completed legal note's key point or difficult point and must not add unsupported legal conclusions.
- Do not report an uploaded website or public URL before the relevant commit is deployed successfully.
- Keep legal conclusions and source wording intact unless the user explicitly asks for substantive editing.

## References

- [components.md](references/components.md): component props and interaction hooks.
- [content-conversion.md](references/content-conversion.md): note-to-MDX conversion and asset rules.
- [remotion-animation.md](references/remotion-animation.md): legal-note-to-Remotion workflow, source placement, page embedding, and deployment handoff.
- [validation.md](references/validation.md): build, route, visual, and compatibility checks.
