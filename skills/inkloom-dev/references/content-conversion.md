# InkLoom note-to-MDX conversion

Use this reference when importing material from `notes/` into `src/content/docs/`.

## Required source-to-site placement

1. Run `legal-marknote` on legal source text before writing InkLoom MDX. Its source-preservation, table, statutory-text, and legal-accuracy rules remain binding.
2. Treat the original source directory as the placement anchor. Map its topic and chapter path to the equivalent `src/content/docs/` path; do not flatten separate chapters into a generic import folder.
3. Keep the generated MDX, copied `assets/`, and any Remotion topic slug aligned with that mapped page. For example, a source chapter mapped to `src/content/docs/objective/civil-procedure/03/` keeps its page-local assets there and uses `src/animations/legal-jurisdiction/remotion/` only for that chapter's animation topic.
4. Do not leave the finished MDX, assets, animation source, or generated player in a temporary directory. The finished artifacts must be committed at their mapped project paths.

## Preserve semantic source structures

1. Treat native note tables as data structures. Keep them as standard `<table>` elements when `rowspan` or `colspan` is required; otherwise use a normal Markdown table.
2. Identify hand-written custom HTML by layout intent: inline `display: flex`, `flex`, custom borders, box shadows, colored panels, or named case callouts are presentation structures.
3. Convert hand-written layouts into the existing InkLoom components or a clean Starlight card/grid. Keep legal wording and conclusion semantics separate from visual styling.
4. Do not add a custom component solely to avoid a small, readable Markdown structure.

## Resolve assets

- Copy referenced images from the source note's `assets/` folder into the target page's local `assets/` folder.
- Reference those images with relative paths such as `./assets/example.png` so Astro's image pipeline can resolve them.
- Check every copied asset exists after the move and remains within the target page tree.
- Do not convert a source image into a remote URL when the page needs to build offline or on GitHub Pages.

## Preserve routing and metadata

- Keep the target directory's `_meta.yml` conventions intact; the `starlight-auto-sidebar` plugin uses them for labels and order.
- Use `/inkloom/...` for absolute links because the site is built with `base: '/inkloom'`.
- Prefer relative links between adjacent note pages when the target is structurally local and the existing section uses that convention.
- Check headings, frontmatter, tables, callouts, and imported components after conversion before changing copy.
