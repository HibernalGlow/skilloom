# InkLoom content boundaries

Use this reference whenever a completed Markdown note supplies the legal content for an InkLoom animation.

## Three independent artifacts

1. Keep the completed Markdown note at the user-supplied original path, with its existing local assets. `legal-marknote` may organize this file in place. It is the legal source of truth and must not be converted to, copied into, or moved by the website work.
2. Keep each Remotion explainer in `src/animations/<subject>/<chapter>/<animation-id>/remotion/`. Place `animation.meta.ts` next to `remotion/`; it records the stable animation ID, portable source reference, title, and website route.
3. Keep the corresponding thin website carrier in `src/content/docs/<site-section>/<chapter>/<animation-id>.mdx`. It imports the player and supplies a route. It may contain a short animation title and context, but not the source note's prose, tables, callouts, images, or converted Markdown.

## Move-safe identity

- Treat `animation-id` as stable after publication. Use a descriptive concept ID such as `jurisdiction-scope` or `arbitration-prerequisite`, not a note filename.
- When a note moves, update only `sourceReference` in `animation.meta.ts`; do not move the animation directory or change its public MDX route just to mirror note filing. Use a repository-relative path or source key; never commit an absolute Windows path for a file outside InkLoom.
- When an animation must change subjects or be retired, perform an intentional animation migration: update metadata, player imports, MDX route, and any backlinks together. Do not leave duplicate sources behind.
- Keep both animations for one note in separate animation directories and separate MDX carrier pages. This gives each published explanation an independent URL and makes later reordering or replacement local.

## Site routing

- Follow the local `_meta.yml` convention for carrier labels and ordering.
- Use `/inkloom/...` for absolute website links and retain the published carrier route when possible.
- Keep animation-only assets beside their Remotion source. Do not move note assets into the website just because the animation was derived from that note.
