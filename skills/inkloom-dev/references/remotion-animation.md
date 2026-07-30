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

## Convert rules into visual grammar

1. Express the legal structure spatially and through motion. Use nodes and connectors for relationships, forks for alternative conditions, nested regions for inclusion, timelines for procedure, aligned lanes for comparison, and transformation or causal motion for changes and effects.
2. Make the visual relationship carry the explanation. Use text only for short concept labels, keywords, conditions, outcomes, values, and one brief subordinate caption when unavoidable.
3. Reject text-only teaching surfaces. A heading such as “核心原理” followed by a sentence or paragraph is not an animation scene; decorative icons, borders, or highlighted words do not turn prose into a diagram.
4. Reject plain tables and table-like grids. Do not reproduce the source table, even with animated rows, colored cells, rounded borders, or icon headers. Recompose comparisons into lanes, paired or grouped modules, axes, relationship maps, or progressive state changes whose motion exposes the differences.
5. Use the 16:9 canvas deliberately. Let the main teaching structure occupy and balance most of the usable frame instead of forming a small island in one corner or half. Retain whitespace only when it creates hierarchy, focus, movement space, or a planned reveal.
6. Do not simulate canvas usage by stretching cards, enlarging paragraphs, or adding unrelated decoration. Improve utilization by showing the actual branch, containment, sequence, comparison, or causal structure more clearly.

## Direct motion as legal reasoning

1. Build a continuous argument, not a stack of isolated slides. Let one concrete carrier persist or transform across adjacent scenes: a party node, legal relationship line, decision path, color role, spatial direction, or camera move. Use a clean conceptual cut when the next scene is genuinely a new model and a shared carrier would imply a false relationship.
2. Make motion causal. A condition appearing should launch its branch; a decision should trigger its consequence; a transfer should visibly move the relevant right, duty, or procedural position. Start reactions on the causing beat instead of adding an unrelated delay.
3. Maintain a dominant spatial current across ordinary scene handoffs. Do not ping-pong left/right, up/down, or zoom directions for variety. Change direction only when a visible cause, exception, reversal, hierarchy change, or chapter boundary gives that change meaning.
4. Ban idle ambient motion used as filler. Do not keep cards breathing, icons floating, borders pulsing, or backgrounds drifting after the information has landed. Sustain the scene through staged reveals, purposeful traversal, comparison changes, or causal action; otherwise let the frame become still.
5. Choreograph by reasoning hierarchy. Reveal prerequisites before consequences, shared rules before exceptions, and the dominant distinction before supporting details. The first and strongest movement receives the most attention; do not animate all elements simultaneously or follow source/DOM order blindly.
6. Give important conclusions a readable hold. Insert a short still pause before or after a decisive result so the viewer can register the rule; do not keep the key conclusion moving, morphing, or competing with decorative action.
7. Keep a small, consistent transition vocabulary. Use direction, cuts, or shared carriers according to meaning rather than novelty, and avoid repeating the same card-grid entrance for every scene. Visual variety should come from the legal structure, not random effects.
8. Audit semantic implications. A shared-element morph implies identity or continuity; nesting implies inclusion; arrows imply direction or causation; order and z-position imply priority. Do not use any of these when the legal source does not support that meaning.

Implement these direction rules through `$remotion-best-practices`; do not duplicate or replace its frame-driven timing, sequencing, transition, measurement, asset, or deterministic-render guidance here.

## Put each artifact in its independent project location

1. Leave the Markdown note and all note-local assets at their original location. `legal-marknote` may have edited the note in place; after that, read it as evidence only.
2. Create one source directory for each explainer at `src/animations/<subject>/<chapter>/<animation-id>/remotion/`, with `animation.meta.ts` beside it. Keep `Root.tsx`, `index.ts`, composition, storyboard, scene modules, and visual tokens together there.
3. Reuse `src/animations/legal-jurisdiction/remotion/` as the structural reference. Keep FPS, duration, scene boundaries, composition dimensions, and the stable animation ID explicit.
4. Add a focused React player component under `src/components/` that passes the composition and scene metadata to the shared `RemotionDeck` pattern. Add an Astro wrapper when the page needs the existing `AnimationSource` presentation.
5. Create a thin, dedicated MDX carrier under `src/content/docs/` for each animation. Import that Astro wrapper directly; never paste the source note into the carrier or leave the user to copy iframe markup.

## Publish as one finished flow

1. Run the blocking iterative Remotion page-still QA in [validation.md](validation.md). Fix and recapture every defective page until all full-resolution stills pass; run the all-animation command after a batch is complete.
2. Build the site and verify the responsive player in the target page.
3. Commit both Remotion explainers, their metadata, player components, and thin MDX carriers as one feature, then push them to the InkLoom repository. Do not include source-note rewrites or relocations unless separately requested.
4. Push to the branch that deploys the website. Once GitHub Pages finishes, verify `https://inkloomer.github.io/inkloom/<page-route>/`.
5. When the user explicitly requests an existing SiYuan-note embed, use [siyuan-embed.md](siyuan-embed.md) after the production URL is verified. Do not return an iframe snippet as a manual follow-up task.
