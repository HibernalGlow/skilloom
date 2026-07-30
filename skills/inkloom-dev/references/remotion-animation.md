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
3. Build a reusable visual vocabulary for concrete legal concepts. Pair people and roles, groups, institutions, documents or decisions, remedies or measures, procedural actions, and legal outcomes with semantically recognizable icons or compact pictograms. Prefer the project's existing icon library, keep stroke weight and color roles consistent, and retain a short adjacent label when the symbol is not universally clear.
4. Make icons perform within the explanation. Let a person token move into a branch, a document receive a decision mark, a measure act on its target, or an outcome token emerge from the causing step. Do not scatter unrelated icons beside sentences or use icons merely to fill empty space.
5. Reject text-only teaching surfaces. A heading such as “核心原理” followed by a sentence or paragraph is not an animation scene; decorative icons, borders, or highlighted words do not turn prose into a diagram.
6. Reject plain tables and table-like grids. Do not reproduce the source table, even with animated rows, colored cells, rounded borders, or icon headers. Recompose comparisons into lanes, paired or grouped modules, axes, relationship maps, or progressive state changes whose motion exposes the differences.
7. Use the 16:9 canvas deliberately. Let the main teaching structure occupy and balance most of the usable frame instead of forming a small island in one corner or half. Retain whitespace only when it creates hierarchy, focus, movement space, or a planned reveal.
8. Do not simulate canvas usage by stretching cards, enlarging paragraphs, or adding unrelated decoration. Improve utilization by showing the actual branch, containment, sequence, comparison, or causal structure more clearly.

## Emphasize focal rules

1. Designate one primary focal rule and at most one secondary focal rule per scene. A high-priority phrase such as a jurisdictional connecting factor must not rely only on red text, bold weight, a solid background, or a colored border.
2. Give each focal rule at least two co-located semantic channels. Combine an icon or pictogram with one or more of: a locator pin or target, distinctive enclosure, connector landing point, bracket or underline, spatial promotion, contrast pair, status badge, or purposeful motion cue. A distant icon elsewhere in the card does not strengthen the phrase itself.
3. Keep the glyphs stable after entry. Direct sustained attention through the annotation or relationship around the text: trace a boundary, sweep an underline, move a dot along the incoming connector, rotate a small status arc, or periodically revisit a locator. Limit this to one or two focal elements and keep amplitude low enough that reading never shifts.
4. Use a recurring cue only when it communicates location, status, direction, priority, or an active relationship. Include a readable hold before the cue begins and quiet intervals between repetitions. Do not disguise decorative breathing, glow pulsing, or scale wobble as emphasis.
5. Reserve layout space for conclusions. An authored summary bar, subtitle, badge, or final callout must never sit over existing teaching content. Reflow, shrink nonessential spacing, dock the conclusion in a dedicated region, or transform earlier nodes into the conclusion. Keep critical content outside the bottom player-control safe zone.

## Direct motion as legal reasoning

1. Build a continuous argument, not a stack of isolated slides. Let one concrete carrier persist or transform across adjacent scenes: a party node, legal relationship line, decision path, color role, spatial direction, or camera move. Use a clean conceptual cut when the next scene is genuinely a new model and a shared carrier would imply a false relationship.
2. Make motion causal. A condition appearing should launch its branch; a decision should trigger its consequence; a transfer should visibly move the relevant right, duty, or procedural position. Start reactions on the causing beat instead of adding an unrelated delay.
3. Maintain a dominant spatial current across ordinary scene handoffs. Do not ping-pong left/right, up/down, or zoom directions for variety. Change direction only when a visible cause, exception, reversal, hierarchy change, or chapter boundary gives that change meaning.
4. Ban idle ambient motion used as filler. Do not keep cards breathing, icons floating, borders pulsing, or backgrounds drifting after the information has landed. Sustain the scene through staged reveals, purposeful traversal, comparison changes, causal action, or one restrained focal-rule cue defined above; otherwise let the frame become still.
5. Choreograph by reasoning hierarchy. Reveal prerequisites before consequences, shared rules before exceptions, and the dominant distinction before supporting details. The first and strongest movement receives the most attention; do not animate all elements simultaneously or follow source/DOM order blindly.
6. Give important conclusions a readable hold. Insert a short still pause before a restrained annotation resumes; keep the text itself stationary and do not let the conclusion morph or compete with decorative action.
7. Keep a small, consistent transition vocabulary. Use direction, cuts, or shared carriers according to meaning rather than novelty, and avoid repeating the same card-grid entrance for every scene. Visual variety should come from the legal structure, not random effects.
8. Audit semantic implications. A shared-element morph implies identity or continuity; nesting implies inclusion; arrows imply direction or causation; order and z-position imply priority. Do not use any of these when the legal source does not support that meaning.

Implement these direction rules through `$remotion-best-practices`; do not duplicate or replace its frame-driven timing, sequencing, transition, measurement, asset, or deterministic-render guidance here.

## Web-page end state

Treat `SCENES` as the shared timing contract for the composition, the embedded Player, and page QA. Every scene must explicitly declare `previewEndTrimFrames` in final playback-frame units: use the exact tail length from the first authored exit frame to the scene end, or write `0` when no exit occurs. The shared Player uses this field to stop on the last stable teaching frame without changing the full-video timeline. Do not infer it from scene duration or use a generic fractional trim; derive it from the authored exit interpolation and remeasure after changing the exit.

## Put each artifact in its independent project location

1. Leave the Markdown note and all note-local assets at their original location. `legal-marknote` may have edited the note in place; after that, read it as evidence only.
2. Create one source directory for each explainer at `src/animations/<subject>/<chapter>/<animation-id>/remotion/`, with `animation.meta.ts` beside it. Keep `Root.tsx`, `index.ts`, composition, storyboard, scene modules, and visual tokens together there.
3. Reuse `src/animations/legal-jurisdiction/remotion/` as the structural reference. Keep FPS, duration, scene boundaries, composition dimensions, and the stable animation ID explicit.
4. Add a focused React player component under `src/components/` that passes the composition and scene metadata to the shared `RemotionDeck` pattern. Add an Astro wrapper when the page needs the existing `AnimationSource` presentation.
5. Create a thin, dedicated MDX carrier under `src/content/docs/` for each animation. Import that Astro wrapper directly; never paste the source note into the carrier or leave the user to copy iframe markup.
6. Keep each player scene addressable through the shared `scene` query. Every new `RemotionScene` entry must define a stable, descriptive, kebab-case `id` such as `first-instance`, `emergency-measures`, or `review-remedy`; never derive that ID from the page number or mutable display title. Preserve IDs across page insertion, reordering, and title edits. Use numeric keys only as backward-compatible aliases for legacy animations, and record which source-note concept maps to which semantic ID.

## Publish final-frame stills with the carrier

1. Export one full-resolution PNG from the approved readable final frame of every semantic scene. Use the same stable scene ID as the filename, such as `first-instance.png`; do not publish only a contact sheet or an arbitrary frame near the end.
2. Resolve the carrier path first. For `src/content/docs/.../trial-organization-path.mdx`, publish into `src/content/docs/.../animation/trial-organization-path/<version>/`. Apply the same `<md-dir>/animation/<md-basename>/<version>/` rule to a `.md` carrier.
3. Use a sortable UTC timestamp version such as `20260730T143214Z`. Write `manifest.json` in that version directory with at least the version, generation time, animation ID, composition dimensions, and each scene's semantic ID, title, source frame, and PNG filename.
4. Treat published version directories as immutable. For an animation update, generate and validate a new version directory, update every carrier image reference together, and retain the prior version for traceability unless the user explicitly requests cleanup.
5. Render every scene PNG directly in the MD/MDX with a relative Markdown image or equivalent accessible image element. Use the scene title as meaningful alt text, preserve scene order, and do not hide the images in `<details>`, replace them with filename links, or point the carrier at `.artifacts`.
6. Keep the interactive player as the primary motion surface and the final-frame images as inspectable static states. Do not replace the player unless the user explicitly requests a static-only carrier.

## Publish as one finished flow

1. Run the blocking iterative Remotion page-still QA in [validation.md](validation.md). Fix and recapture every defective page until all full-resolution stills pass; run the all-animation command after a batch is complete.
2. Promote the approved scene final frames into the carrier-local version directory, write its manifest, and render all of them directly in the carrier.
3. Build the site and verify the responsive player and every rendered final-frame image in the target page.
4. Commit both Remotion explainers, their metadata, player components, versioned final-frame assets, and thin MDX carriers as one feature, then push them to the InkLoom repository. Do not include source-note rewrites or relocations unless separately requested.
5. Push to the branch that deploys the website. Once GitHub Pages finishes, verify `https://inkloomer.github.io/inkloom/<page-route>/`.
6. When the user explicitly requests an existing SiYuan-note embed, use [siyuan-embed.md](siyuan-embed.md) after the production URL is verified. Do not return an iframe snippet as a manual follow-up task.
