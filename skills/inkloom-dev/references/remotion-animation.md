# InkLoom legal-note animation workflow

Use this reference after the legal source has been checked for `legal-marknote` completion and the final note has been mapped into `src/content/docs/`. Run `legal-marknote` only for raw material; do not reprocess a note that is already structured.

## Choose and scope the animation

1. Create exactly two focused explainers from the completed note's important and difficult points. Cover two distinct points where possible; for one especially complex point, use two complementary explainers only when each has a separate learning objective.
2. Select a rule definition, decision branch, procedural order, relationship, exception, or recurring misconception. Keep each animation faithful to the completed note; do not introduce legal rules, facts, or conclusions that are not supported by that source.
3. Prefer a short sequence of readable scenes over a decorative summary. Make every scene answer one learning question and expose the resulting rule, branch, or relationship.

## Put each artifact in its correct project location

1. Keep the converted note and its `assets/` in the source-derived `src/content/docs/<topic>/<chapter>/` directory.
2. Create one source directory for each explainer at `src/animations/<topic-slug>/remotion/`. Keep `Root.tsx`, `index.ts`, composition, storyboard, scene modules, and visual tokens together there.
3. Reuse `src/animations/legal-jurisdiction/remotion/` as the structural reference. Keep FPS, duration, scene boundaries, and composition dimensions explicit.
4. Add a focused React player component under `src/components/` that passes the composition and scene metadata to the shared `RemotionDeck` pattern. Add an Astro wrapper when the page needs the existing `AnimationSource` presentation.
5. Import that Astro wrapper directly in the mapped MDX page. This direct page embed is mandatory; never leave the user to copy or paste iframe markup.

## Publish as one finished flow

1. Build the site and verify the player in the target page.
2. Commit the source note conversion where needed, both Remotion explainers, player components, and MDX embeds as one feature, then push them to the InkLoom repository.
3. Push to the branch that deploys the website. Once GitHub Pages finishes, verify `https://inkloomer.github.io/inkloom/<page-route>/`.
4. Return the deployed page URL as the completed embedded result. Do not return an iframe snippet as a manual follow-up task.
