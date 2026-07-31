# InkLoom content boundaries

Use this reference whenever a completed Markdown note supplies the legal content for an InkLoom animation.

## Independent artifacts

1. Keep the completed Markdown note at the user-supplied original path, with its existing local assets. `legal-marknote` may organize this file in place. It is the legal source of truth and must not be converted to, copied into, or moved by the website work.
2. Keep each Remotion explainer in `src/animations/<subject>/<chapter>/<animation-id>/remotion/`. Place `animation.meta.ts` next to `remotion/`; it records the stable animation ID, portable source reference, title, and website route.
3. Keep the corresponding thin website carrier in `src/content/docs/<site-section>/<chapter>/<animation-id>.mdx`. It contains only frontmatter and the animation-component import needed to supply the route; do not add explanatory prose, headings, tables, callouts, images, or converted Markdown.
4. Keep the original full-length video output and existing pagination contract unchanged. Keep additive animated AVIF companions under `public/animation-avif/<animation-id>/`, with one stable semantic scene file and a manifest. The MDX carrier must not contain hand-authored image blocks; the shared player renders the original video and AVIF tabs.

## Move-safe identity

- Treat `animation-id` as stable after publication. Use a descriptive concept ID such as `jurisdiction-scope` or `arbitration-prerequisite`, not a note filename.
- When a note moves, update only `sourceReference` in `animation.meta.ts`; do not move the animation directory or change its public MDX route just to mirror note filing. Use a repository-relative path or source key; never commit an absolute Windows path for a file outside InkLoom.
- When an animation must change subjects or be retired, perform an intentional animation migration: update metadata, player imports, MDX route, and any backlinks together. Do not leave duplicate sources behind.
- Keep both animations for one note in separate animation directories and separate MDX carrier pages. This gives each published explanation an independent URL and makes later reordering or replacement local.
- Treat every semantic scene ID as a durable public filename contract. Keep `public/animation-avif/<animation-id>/<scene-id>.avif` stable across title edits and page reordering, and atomically replace a complete animation directory only after every new file and its manifest pass QA.

## Site routing

- Follow the local `_meta.yml` convention for carrier labels and ordering.
- Use `/inkloom/...` for absolute website links and retain the published carrier route when possible.
- Keep source media used by the composition beside its Remotion source. Published animated AVIF companions and manifests live under `public/animation-avif/`; do not move source-note assets into the website just because the animation was derived from that note.
- Keep lossless PNG captures and contact sheets as transient QA artifacts in `.artifacts`; publish only the approved q45 animated AVIF companions and manifests required by [animated-avif.md](animated-avif.md).
