# Visual direction for animation nodes

Treat one MDX carrier and its Remotion directory as one visual node. A node should have one coherent visual language across its scenes, while each new node should deliberately choose a different visual fingerprint from nearby nodes.

## Contents

- Shared/runtime boundary and direction catalog
- Structural anchors, semantic text treatments, and theme rewrites
- Theme-like reuse and manifest contract

## Shared/runtime boundary

Share only frame conversion, scene timing, `Sequence` plumbing, render registration, and optional motion primitives whose appearance is supplied by the node. Keep these decisions local to the node:

- background structure and texture;
- font families, type scale, and headline layout;
- palette and semantic color roles;
- card, node, surface, border, shadow, and icon treatment;
- scene composition and camera/layout grammar;
- scene transitions and the overall art direction.

Use `src/animations/shared/remotion-runtime.tsx` for the neutral runtime. Treat `src/animations/shared/legal-visual.tsx` as a legacy compatibility layer only; do not import it in a new node.

## Direction catalog

Choose a direction because it clarifies the legal structure, not because it is decorative. Record the choice in `visual-direction.json` beside `remotion/`. The fields below are a prompt seed, not a component template:

| Direction | Palette cue | Composition grammar | Motion grammar | Good fit |
|---|---|---|---|---|
| Courtroom blueprint | ink navy, blueprint cyan, one warning red | measured plans, coordinates, gates | orthogonal routing, grid reveals, precise wipes | jurisdiction and procedure |
| Archival dossier | paper white, carbon black, stamp red | folders, evidence strips, marginal notes | stamped entries, clipped reveals, document handoff | documents, proof, remedies |
| Newspaper editorial | off-white, ink black, selective process color | asymmetric columns, pull quotes, cutouts | column assembly, headline crop, editorial cuts | definitions and distinctions |
| Constructivist geometry | black, vermilion, cobalt, raw white | diagonals, wedges, hard blocks, axes | stepped diagonals, snapping blocks, directional cuts | branches and exceptions |
| Ink annotation | warm white, graphite, one saturated marker | hand-drawn arrows, brackets, circled terms | pen trace, underline sweep, erase/reveal | misconceptions and memory cues |
| Evidence board | charcoal, pinned paper, evidence yellow | clusters, strings, pinned artifacts | token placement, string traversal, cluster separation | parties and relationships |
| Transit map | dark field, route colors, station white | lines, stations, interchange nodes | route traversal, station activation, transfer | multi-step paths |
| Kinetic typography | restrained monochrome plus two semantic colors | typographic hierarchy with sparse symbols | baseline shifts, masks, word grouping | short rules and tests |
| Isometric mechanism | slate, steel, safety orange, signal green | parts, chambers, levers, nested mechanisms | rotation only when causal, latch release, transfer | conditions and effects |
| Split-screen comparison | neutral canvas with two clear role colors | aligned lanes and a shared axis | synchronized comparison, divergence, convergence | similar legal concepts |

Avoid repeating the same direction, palette signature, headline placement, and entrance choreography merely because the legal subject is related. Reuse a direction only when the new node's fingerprint is materially different and the semantic benefit is documented.

## Choose the structural anchor before the theme

Start with the legal relationship and choose the scene's visual anchor from that structure. Do not begin with a favorite icon, card layout, or visual effect and force the content into it.

- Use a **concept icon** when one concrete role, document, institution, or legal object genuinely organizes the scene.
- Use a **path or fork** for ordered decisions and alternative conditions.
- Use a **role pair or comparison axis** for identity, attribution, and opposing outcomes.
- Use a **boundary or gate** for authority limits, exclusions, and stage changes.
- Use a **timeline** for procedural order and temporal consequences.
- Use a **typographic sequence** when a short verbal test, rejection, or list of expressly named acts is itself the knowledge structure.

The anchor must make the rule more direct. Reject a scanner, lock, track, machine, or other novel metaphor when the viewer must first decode the metaphor before understanding the legal relationship. A scene may have no dominant icon when its path, boundary, comparison, or typography already provides the correct anchor.

## Give text treatments semantic jobs

Color and bold weight are supporting channels, not a complete typography system. Plan a small node-level vocabulary and assign every treatment a stable job:

- **soft highlight**: core term or accepted proposition;
- **thin underline**: decisive condition, action, or phrase to retrieve;
- **label block**: role, category, stage, or status;
- **stamp**: formal authorization, judgment, rejection, or operative result;
- **external negation**: invalid inference or prohibited route, placed beside the text rather than through it.

For a multi-scene node, normally use at least three appropriate treatment families across the node so every emphasis does not collapse into the same colored highlight. This is a node-level diversity check, not a demand that every scene or phrase use three styles. Keep repeated legal meanings consistent, and omit a treatment when it has no semantic job.

Apply the vocabulary at container level, not only at scene level. A card, side panel, note box, or callout whose body is a bare default-ink run under a title or label fails QA even when the rest of the scene is well treated. Segment copied prose at its semantic joints before rendering: an enumeration becomes chips, rows, or mini-cards that can enter staggered; a multi-clause sentence becomes a condition → action, term → expansion, or claim → negation structure with every clause visibly treated. Text that still reads top-to-bottom like the source note after recoloring, reordering, or re-boxing has not been visualized.

## Segmenting prose: joint types, width budget, and motion

Cut the prose at its semantic joints. Enumeration, abbreviation → expansion, condition → consequence, named variants, and rule-plus-negation are common joints, not a closed set and not visual templates. After cutting, design each unit's rendering from the node's own direction—palette, surfaces, composition grammar, motion vocabulary. The same joint must not converge on one shared rendering across nodes: if two nodes realize a joint with near-identical chips, rows, or cards, that is fingerprint reuse and fails `pnpm animation:styles` exactly like a copied theme. Name treatments by their semantic job, and let each node invent its own visuals for that job.

Width budget before writing the JSX:

- Compute the inner width first: container width − horizontal padding − borders − per-unit (text ≈ fontSize × CJK char count + padding + border) − gaps. WenKai advance is ~1× fontSize; leave ≥10px slack.
- Space-separated interpuncts (` · `) cost ~22px each in a 22px row; use tight `·` inside constrained rows.
- Set `whiteSpace: 'nowrap'` on chip and label text and `flexWrap: 'wrap'` on the group, so overflow degrades into a clean second row instead of breaking a label mid-word.
- Never solve overflow by dropping below the 22px knowledge-text floor; shrink padding, gaps, or glyph size first, or split the row. An orphan single character wrapped onto its own line, or a name broken after its third character, fails page QA.
- Keep new entry beats inside the scene's existing frame budget from `storyboard.ts`: the last delay plus its span must finish before the scene end; do not extend `SCENES` to accommodate decoration.

Keep the declaration surfaces in sync when a segment design introduces a new treatment family, icon, or container: `ALLOWED_TEXT_TREATMENTS` in the InkLoom `scripts/validate-animation-structure.mjs`, the scene's `data-text-treatments` hook, `textTreatments` in `visual-structure.json`, the `tokens` list for newly rendered icons, and `finalKnowledge` plus the scene's `data-final-knowledge` comment for new containers. Authoring `chip` without registering it in the validator fails `pnpm animation:styles` with "unsupported text treatment"; a marker declared in JSON but missing from TSX fails the same audit in the other direction.

Never draw a thick circle, cross, or strike-through over readable glyphs. Keep underlines thin, backgrounds translucent, and negation marks outside the text bounds. Text must remain fully readable at every motion checkpoint. When the repository's structure descriptor is present, declare the chosen scene anchor and treatments there and keep its `data-visual-anchor` and `data-text-treatments` hooks aligned with the rendered source.

## Recurring concepts become recurring tokens

At outline time, before any scene is authored, list the concepts that will recur across the node — recurring procedures, operative verdicts, key documents, parties — and assign each one a single compact, semantically accurate pictogram from the node's own direction vocabulary. From then on the token travels with the word: every heading, chip, stamp, condition row, and terminal state that names the concept repeats the same glyph beside or inside the label. A viewer should be able to follow where 补正, 解释, or 定案根据 appear on a frame by shape and color alone, because the token carries the concept between occurrences and turns repetition into memory. A token that shows up once at a concept's first appearance and then disappears throws the audience back to reading every later occurrence; that regression is the contact-sheet failure this rule exists to prevent.

Keep the mapping node-local. The same concept may take a different glyph in a neighboring node — the glyph is part of the node's fingerprint — and copying another node's token map is fingerprint reuse like any copied theme. Record the map in `visual-direction.json` so audits can verify it:

```json
{
  "conceptTokens": {
    "补正": "Wrench",
    "合理解释": "MessageSquareText",
    "定案根据": "FileCheck"
  }
}
```

`pnpm animation:styles` validates the field's shape when present, and the structure audit verifies that each named pictogram actually renders in the node's Remotion source. The field is optional so existing nodes stay valid; declare it for every new node that has recurring concepts.

## Anchor every knowledge row; add a watermark totem

Highlights, colored pills, and underline styling are text treatments, not graphics. A scene whose teaching content reads as stacked text pills is a text wall and fails page QA no matter how well the text is styled. Two graphic layers are mandatory in every scene:

- **Row anchors.** Every knowledge-bearing row or card carries its own compact semantic icon beside the label — an icon chip with the pictogram on the node's tone color, a role glyph, or a document mark that participates in the row's entrance. One icon on the panel title does not anchor the rows beneath it. Declare the row-anchor components in the scene's `tokens` so audits pin them.
- **Watermark totem.** Each scene renders one large translucent pictogram (90 px or more at reduced opacity) behind a panel or in a corner — the panel's totem, chosen from the node's direction vocabulary. The totem is a background graphic layer for image-based recall; it does not replace row anchors, and it must never obscure text.

`pnpm animation:styles` enforces the per-scene floors mechanically: at least 4 row-anchor icon instances, at least 3 distinct semantic icons, and at least 1 watermark totem. The floors are a minimum, not the standard — the contact-sheet review still fails a scene where most rows remain un-anchored text or where the counted icons are decorative. The preferred realization is the row-chip pattern: each row is a labeled chip whose pictogram sits on the row's tone color, with the panel's watermark totem behind the group.

## Make a theme more than a recolor

A new theme or a complete visual rewrite must change the visible design system, not merely palette values. Establish a coherent combination of typography, composition grammar, surfaces, spatial rhythm, icon treatment, motion vocabulary, and transition behavior. Preserve the node's legal content and public identity while replacing its internal art direction.

Neighboring nodes in one topic should not become light and dark skins of the same template. Give each node a theme suited to its own knowledge structure, while keeping all scenes inside one node recognizably related.

## Theme-like reuse without a shared visual factory

Use a catalog direction as an authoring preset, not as a global React theme. A direction may provide a name, semantic palette roles, typography intent, composition grammar, surface vocabulary, and motion principles. Materialize those decisions inside the new node, then adapt them to its legal structure.

- Reuse `directionId` only when the family still clarifies the new legal relationship.
- Record the reference node in `derivedFrom` and describe the material variation in `variation`.
- Keep the new node's palette values, font loading, backgrounds, surfaces, headings, and transitions local even when they derive from a catalog direction.
- Share typed interfaces, validation, timing, interpolation, registration, and style-neutral motion primitives; do not share a theme object that renders the visual identity for every node.
- Treat Remotion composition props or a Zod schema as a way to parameterize content and intentional variants, not as proof that two nodes have distinct art direction.

Remotion's official model is React composition plus props/schema parameterization and reusable components. Its project templates scaffold applications and render stacks; they are not a framework-level visual theme API. Use third-party packages at their real scope: Remotion Bits and `remotion-animated` provide motion primitives, while packages such as caption-theme libraries cover one surface only. A style-kit scaffold may be useful as reference material, but do not adopt it as InkLoom's cross-node visual owner without inspecting its code, license, render determinism, and node-local ownership.

This gives agents a theme-like selector while preserving node ownership. A reused family must still have a visibly different fingerprint and will receive the normal `pnpm animation:styles` review.

## Manifest contract

Every new node must add `visual-direction.json` beside `remotion/`:

```json
{
  "directionId": "courtroom-blueprint",
  "family": "blueprint",
  "palette": "ink navy + blueprint cyan + warning red",
  "typography": "condensed sans headings + monospaced coordinates",
  "composition": "orthogonal gates across a measured plan",
  "surface": "flat drafting lines, no rounded cards",
  "motion": "station-by-station route reveal with one causal checkpoint",
  "transition": "hard vertical wipe at chapter boundary",
  "catalog": {
    "status": "featured",
    "source": "original-node",
    "route": "/inkloom/objective/civil-procedure/04/territorial-jurisdiction/",
    "title": "法庭蓝图"
  }
}
```

Use `catalog.status: "featured"` only for the original node selected to demonstrate a direction. `catalog.title` is the localized name of the visual style, not the legal subject demonstrated by the node. The `/demo/` gallery must use the same style name, preview that node's existing composition, and link to `catalog.route`; it must not create a duplicate demo composition or carrier. For a later node that derives from a catalog direction, use fields such as:

```json
{
  "directionId": "courtroom-blueprint",
  "derivedFrom": "territorial-jurisdiction",
  "variation": "radial jurisdiction checkpoints on a pale survey sheet",
  "catalog": {
    "status": "variant",
    "sourceDirectionId": "courtroom-blueprint"
  }
}
```

An optional `conceptTokens` object (concept → pictogram component name) records the node's recurring-concept tokens; see "Recurring concepts become recurring tokens" above.

When a genuinely new direction is authored, complete these steps in the same change:

1. Set its manifest to `catalog.status: "featured"`, `catalog.source: "original-node"`, its existing `/inkloom/.../` MDX route, and a `catalog.title` that names the visual style independently from the legal node.
2. Add it to the existing `/demo/` registry or discovery mechanism using the original composition and player metadata. Use the same visual-style name as the card title; keep the node's legal title on its original MDX page.
3. Make the gallery card open the original MDX route. Do not add a new route under `/demo/<direction>/` unless the user explicitly requests a separate curated page.
4. Verify the root gallery preview and the original route at narrow and wide widths.

Do not treat the manifest as proof by itself. The page-still review must confirm the declared fingerprint is visible in the rendered node. Run `pnpm animation:styles`; exact duplicate fingerprints fail, while family reuse produces a warning for deliberate review.
