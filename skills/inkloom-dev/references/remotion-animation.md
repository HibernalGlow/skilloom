# InkLoom legal-note animation workflow

Use this reference after the legal source has been checked for `legal-marknote` completion. Run `legal-marknote` only for raw material; keep its completed Markdown result in the user-supplied original file and do not reprocess a note that is already structured.

## Mandatory Remotion prerequisite

Before writing or changing any Remotion composition, scene, player, or render command, read and follow `$remotion-best-practices`.

- Load React Markup Best Practices when implementing compositions, scenes, or player components.
- Load Rendering Best Practices when producing video output or publishing a rendered asset.
- Load Remotion Multimedia when using image, audio, or video media.
- Load any additional routed Remotion reference required by the task, such as Captions or Interactivity.

## Choose and scope the animation

1. Create exactly two focused explainers from the completed note's important and difficult points. Cover two distinct points where possible; for one especially complex point, use two complementary explainers only when each has a separate learning objective.
2. Select a rule definition, decision branch, procedural order, relationship, exception, or recurring misconception. Keep each animation faithful to the completed note; do not introduce legal rules, facts, or conclusions that are not supported by that source.
3. Prefer a short sequence of readable scenes over a decorative summary. Make every scene answer one learning question and expose the resulting rule, branch, or relationship.

## Put each artifact in its independent project location

1. Leave the Markdown note and all note-local assets at their original location. `legal-marknote` may have edited the note in place; after that, read it as evidence only.
2. Create one source directory for each explainer at `src/animations/<subject>/<chapter>/<animation-id>/remotion/`, with `animation.meta.ts` beside it. Keep `Root.tsx`, `index.ts`, composition, storyboard, scene modules, and visual tokens together there.
3. Reuse `src/animations/legal-jurisdiction/remotion/` as the structural reference. Keep FPS, duration, scene boundaries, composition dimensions, and the stable animation ID explicit.
4. Add a focused React player component under `src/components/` that passes the composition and scene metadata to the shared `RemotionDeck` pattern. Add an Astro wrapper when the page needs the existing `AnimationSource` presentation.
5. Create a thin, dedicated MDX carrier under `src/content/docs/` for each animation. Import that Astro wrapper directly; never paste the source note into the carrier or leave the user to copy iframe markup.

## Publish as one finished flow

1. Build the site and verify the player in the target page.
2. Commit both Remotion explainers, their metadata, player components, and thin MDX carriers as one feature, then push them to the InkLoom repository. Do not include source-note rewrites or relocations unless separately requested.
3. Push to the branch that deploys the website. Once GitHub Pages finishes, verify `https://inkloomer.github.io/inkloom/<page-route>/`.
4. Return the deployed page URL as the completed embedded result. Do not return an iframe snippet as a manual follow-up task.
