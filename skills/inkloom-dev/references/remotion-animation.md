# InkLoom legal-note animation workflow

Use this reference after the legal source has been checked for `legal-marknote` completion. Run `legal-marknote` only for raw material; keep its completed Markdown result in the user-supplied original file and do not reprocess a note that is already structured.

## Mandatory Remotion prerequisite

Before writing or changing any Remotion composition, scene, player, or render command, read and follow `$remotion-best-practices`.

- Load React Markup Best Practices when implementing compositions, scenes, or player components.
- Load Rendering Best Practices when producing video output or publishing a rendered asset.
- Load Remotion Multimedia when using image, audio, or video media.
- Load any additional routed Remotion reference required by the task, such as Captions or Interactivity.

## Choose and scope the animation

1. Create the number of focused explainers warranted by the completed note's important and difficult points; one, two, or more are all valid. Use one node when several points share one coherent learning objective and visual model. Split nodes only when they teach independent objectives, require incompatible visual models, or would otherwise create competing reading paths or excessive scene density. Never add an explainer or MDX carrier merely to reach a preset count.
2. Select a rule definition, decision branch, procedural order, relationship, exception, or recurring misconception. Keep each animation faithful to the completed note; do not introduce legal rules, facts, or conclusions that are not supported by that source.
3. Prefer a short sequence of readable scenes over a decorative summary. Make every scene answer one learning question and expose the resulting rule, branch, or relationship.
4. Set duration per semantic scene from content density, not from a fixed 15-second target and not from a 20-second cap on the complete composition. Count `sequentialBeats` as concepts, relations, or actions that must be understood in order; `denseReadingGroups` as compact knowledge-bearing text groups that need a separate read; and `branchHandoffs` as attention transfers between branches or teaching regions. Use this starting estimate in seconds: `1.2 + 0.9 * sequentialBeats + 0.35 * denseReadingGroups + 0.5 * branchHandoffs`. The base allowance includes entrance and a readable final hold.
5. Calibrate the estimate against `/objective/civil-procedure/04/legal-jurisdiction/?scene=mediation-confirmation`: its 330 frames at 60 fps, about 5.5 seconds, comfortably stage roughly four ordered reasoning beats and leave about one second for the stable result. This is a density reference, not a template or required duration.
6. Inspect the actual motion and adjust: shorten idle lead-in, decorative travel, repeated emphasis, or an unnecessarily long final hold; lengthen only when a knowledge-bearing label, causal handoff, branch comparison, or conclusion is rushed. A single semantic scene must not exceed 20 seconds without explicit approval. The complete composition is the natural sum of its scenes and may exceed 20 seconds. Preserve wording that carries legal conditions, exceptions, roles, or relationships; do not satisfy a number by deleting structure or raising playback speed past comfortable reading.
7. Audit stable-frame density by legal atoms: actors, conditions, actions, relations, results, and exceptions. Split a scene when these require prose paragraphs or competing reading paths. Combine or enlarge the actual relationship when a scene contains only a small label island and unexplained dead canvas; do not fill the frame with decorative cards, icons, or metadata.
8. Keep each scene answerable as one direct legal question. A visually inventive metaphor fails when it makes the answer less immediate than a role diagram, authorization fork, boundary, timeline, or comparison would.

## Choose a node-level visual direction

1. Treat the MDX carrier as the public node boundary: scenes inside that node should share typography, palette roles, surface language, and one restrained transition vocabulary.
2. Before coding, choose a direction from [visual-direction.md](visual-direction.md), compare it with nearby node manifests, and write a unique `visual-direction.json` beside `remotion/`.
3. Keep the visual direction local. Use only neutral runtime helpers for timing and registration; do not import the legacy `createLegalVisualSystem()` factory in new work.
4. Prefer a materially different palette, headline placement, surface grammar, and motion vocabulary for the next node. Do not create variety by randomizing direction or by adding decorative effects that weaken legal meaning.
5. Use a catalog direction as a theme-like design brief when appropriate. Keep its implementation node-local, record `derivedFrom` and `variation`, and never import a shared visual theme object merely to reproduce its look.
6. Give every featured direction its own style name. The Demo label and `catalog.title` describe the visual language, such as `法庭蓝图` or `套色印版`; they must not repeat the legal topic, node title, chapter title, or a scene heading.
7. Before rewriting an already published node, inventory its `animation-id`, semantic scene IDs, order, AVIF filenames, MDX route, and deep links. Preserve those public references while replacing the theme and internal composition. Do not rename scenes or create replacement routes merely to make the rewrite feel new.

## Convert rules into visual grammar

1. Express the legal structure spatially and through motion. Use nodes and connectors for relationships, forks for alternative conditions, nested regions for inclusion, timelines for procedure, aligned lanes for comparison, and transformation or causal motion for changes and effects.
2. Make the visual relationship carry the explanation. Use text only for short concept labels, keywords, conditions, outcomes, values, and one brief subordinate caption when unavoidable.
3. Build a reusable visual vocabulary for concrete legal concepts. Pair people and roles, groups, institutions, documents or decisions, remedies or measures, procedural actions, and legal outcomes with semantically recognizable icons or compact pictograms. Prefer the project's existing icon library, keep stroke weight and color roles consistent, and retain a short adjacent label when the symbol is not universally clear.
4. Make icons perform within the explanation. Let a person token move into a branch, a document receive a decision mark, a measure act on its target, or an outcome token emerge from the causing step. Do not scatter unrelated icons beside sentences or use icons merely to fill empty space.
5. Reject text-only teaching surfaces. A heading such as "核心原理" followed by a sentence or paragraph is not an animation scene; decorative icons, borders, or highlighted words do not turn prose into a diagram.
6. Reject plain tables and table-like grids. Do not reproduce the source table, even with animated rows, colored cells, rounded borders, or icon headers. Recompose comparisons into lanes, paired or grouped modules, axes, relationship maps, or progressive state changes whose motion exposes the differences.
7. Use the 16:9 canvas deliberately. Let the main teaching structure occupy and balance most of the usable frame instead of forming a small island in one corner or half. Retain whitespace only when it creates hierarchy, focus, movement space, or a planned reveal.
8. Do not simulate canvas usage by stretching cards, enlarging paragraphs, or adding unrelated decoration. Improve utilization by showing the actual branch, containment, sequence, comparison, or causal structure more clearly.
9. Measure every connector precisely. When drawing directional arrows between nodes with the shared `FlowArrow` component, size the arrow length to the actual gap (`width ≈ targetLeft - sourceLeft - 2`). Reusing a hardcoded default such as `340` px across scenes with different node spacing will either pierce the target node or leave an unsightly gap. Always recalculate `width` from the concrete layout coordinates and verify the result in the page-still QA.
10. Author type for the reduced website player, not only for a full-screen render. At a 1920x1080 canvas, use at least 30 px for focal legal concepts and primary node labels, and at least 22 px for knowledge-bearing conditions, explanations, axis labels, and branch labels. Only non-semantic metadata such as numbers, English eyebrows, coordinates, and `STATION 01` labels may use 15-18 px.
11. Treat those sizes as readability floors, not a request to inflate every label. Preserve visual hierarchy and craft by wrapping deliberately, expanding or relocating the relevant teaching region, moving headings out of the way, and removing low-value metadata. Do not rewrite or remove wording that carries legal structure merely to make the layout easier. Never trade the minimum size for overflow, crowding, clipped text, weak alignment, or a visually top-heavy scene.
12. Use the text-treatment vocabulary in [visual-direction.md](visual-direction.md). Do not rely on a single highlight style throughout a node, and do not force a main concept icon into scenes whose path, boundary, role comparison, timeline, or typographic sequence is the stronger anchor.

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
7. When the node introduces a new direction, add the original composition and existing MDX route to the `/demo/` catalog. Mark the manifest as `catalog.status: "featured"` and `catalog.source: "original-node"`, and use the same visual-style name for the Demo entry and `catalog.title`; do not use the legal node title or create a demo-only Remotion directory or MDX carrier.

## Publish animated AVIF companions

1. Preserve any existing full-length composition/video output and the established `SCENES` pagination format. Publish the required per-scene AVIF files without splitting or re-encoding video.
2. Follow [animated-avif.md](animated-avif.md) after the page-still QA loop passes. Run `pnpm animation:publish-avif <animation-id>` to render every existing semantic scene through its stable preview end and encode one once-playing AVIF at the default q45/CRF35, 2560x1440, 15 fps contract.
3. Publish stable assets to `public/animation-avif/<animation-id>/<scene-id>.avif` with a sibling manifest. Every player scene must explicitly declare its stable kebab-case ID, number, and title before spreading `SCENES.<key>`, and the deck must provide `animationId`.
4. The website keeps the existing full-video Remotion Player and its pagination unchanged, then adds an AVIF tab; it does not add final-frame sections to the MDX carrier. The selected media tab persists in localStorage, and scene navigation chooses the corresponding semantic AVIF.
5. Keep the file once-playing. Replay and infinite loop belong to the website or SiYuan controller, not the encoded loop count. Do not offer pause/resume in SiYuan: keep the native `<img>` untouched and implement replay or manifest-timed looping by reloading it.

## Publish as one finished flow

1. Run the blocking iterative Remotion page-still QA in [validation.md](validation.md). Inspect exactly one all-scenes contact sheet per animation, fix every defective tile, and recapture until that sheet passes. Never open all full-resolution stills; crop and enlarge only a specific questionable region. Run the all-animation command only when a shared change requires recapturing every animation, and treat each newest sheet as the sole review artifact.
2. Run `pnpm animation:publish-avif <animation-id>` for changed animations and `pnpm animation:publish-avif` after the batch to publish every semantic scene and manifest.
3. Build the site and verify the responsive video/AVIF switcher, semantic scene selection, mode persistence, replay/loop controls, copy actions, and direct animated asset URLs.
4. Commit both Remotion explainers, their metadata, player components, thin MDX carriers, public animated AVIFs/manifests, and the SiYuan controller as one feature, then push them to the InkLoom repository. Do not include source-note rewrites or relocations unless separately requested.
5. Push to the branch that deploys the website. Once GitHub Pages finishes, verify `https://inkloomer.github.io/inkloom/<page-route>/`.
6. When the user explicitly requests an existing SiYuan-note embed, use [siyuan-embed.md](siyuan-embed.md) after the production URL is verified. Do not return an iframe snippet as a manual follow-up task.
