# InkLoom content boundaries

Use this reference whenever a completed Markdown note supplies the legal content for an InkLoom animation.

## Independent artifacts

1. Keep the completed Markdown note at the user-supplied original path, with its existing local assets. `legal-marknote` may organize this file in place. It is the legal source of truth and must not be converted to, copied into, or moved by the website work.
2. Keep each Remotion explainer in `src/animations/<subject>/<chapter>/<animation-id>/remotion/`. Place `animation.meta.ts` next to `remotion/`; it records the stable animation ID, portable source reference, title, and website route.
3. Keep the corresponding thin website carrier in `src/content/docs/<site-section>/<chapter>/<animation-id>.mdx`. It imports the player and supplies a route. It may contain a short animation title and context, but not the source note's prose, tables, callouts, images, or converted Markdown.
4. Keep approved final-frame screenshots beside that carrier under `animation/<md-basename>/<version>/`. These are derived presentation assets for the carrier, not copied source-note assets. Render them directly from the MD/MDX with relative paths.

## Move-safe identity

- Treat `animation-id` as stable after publication. Use a descriptive concept ID such as `jurisdiction-scope` or `arbitration-prerequisite`, not a note filename.
- When a note moves, update only `sourceReference` in `animation.meta.ts`; do not move the animation directory or change its public MDX route just to mirror note filing. Use a repository-relative path or source key; never commit an absolute Windows path for a file outside InkLoom.
- When an animation must change subjects or be retired, perform an intentional animation migration: update metadata, player imports, MDX route, and any backlinks together. Do not leave duplicate sources behind.
- Keep both animations for one note in separate animation directories and separate MDX carrier pages. This gives each published explanation an independent URL and makes later reordering or replacement local.
- Treat the final-frame version directory as immutable after publication. Generate a new sortable timestamp such as `20260730T143214Z`, keep semantic scene filenames stable within it, and update the carrier references only after the new version passes QA.

## Site routing

- Follow the local `_meta.yml` convention for carrier labels and ordering.
- Use `/inkloom/...` for absolute website links and retain the published carrier route when possible.
- Keep source media used by the composition beside its Remotion source. The only carrier-local derived assets are the approved final-frame PNGs and their manifest; do not move note assets into the website just because the animation was derived from that note.
- Keep transient captures and contact sheets in `.artifacts`; promote only approved full-resolution final frames and their manifest into the carrier-local version directory.
