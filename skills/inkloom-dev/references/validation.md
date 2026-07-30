# InkLoom validation checklist

Run the smallest relevant checks after an edit, then run the full build when changing shared components, routing, styles, or many MDX pages.

## Structural checks

- Confirm changed files are under the intended InkLoom area.
- Confirm every imported component exists and its props match the implementation.
- Confirm local images exist and use the intended relative `./assets/...` path.
- Confirm raw legal material was first processed with `legal-marknote`, while an already structured legal note was not processed again. Confirm its final MDX, local assets, and animation paths follow the original source directory's mapped topic/chapter location.
- Confirm there are exactly two Remotion explainers, each with a focused legal learning objective, a source under `src/animations/<topic-slug>/remotion/`, and a direct Astro/React player embed in its target MDX page.
- Search changed MDX/Astro files for bare absolute site links such as `/objective/`; replace them with `/inkloom/...` or a relative link.
- Check nearby `_meta.yml` files when adding, moving, or renaming pages.

## Visual and interaction checks

- Inspect the page at narrow and wide widths.
- Verify tables do not overflow unexpectedly and flow diagrams remain legible.
- Test memory challenge: toggle the checkbox, confirm `.answer-node` blur, and confirm hover reveal.
- Test `trigger-link-1` and `trigger-link-2` hover emphasis when the page uses `VisualFlow`.
- Test the embedded Remotion player at narrow and wide widths; verify its scene navigation, playback, and reduced-size layout without a copied iframe.
- Check PageTitle quick actions, floating TOC, and any widescreen layout override touched by the change.

## Deployment handoff

- After the production build passes, commit and push the changed page, player, and Remotion source together. The `main` branch deploys to GitHub Pages.
- Confirm the deployed page at `https://inkloomer.github.io/inkloom/<page-route>/` before reporting it as uploaded. The page itself is the embed target; do not hand the user iframe markup to paste manually.

## Commands

```bash
astro dev --background
astro dev status
astro dev logs
astro dev stop
pnpm build
```

Use the dev server for route and visual checks. Use `pnpm build` as the final production-oriented gate; capture the first actionable error instead of hiding it behind a generic failure summary.
