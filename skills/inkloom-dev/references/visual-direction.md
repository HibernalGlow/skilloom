# Visual direction for animation nodes

Treat one MDX carrier and its Remotion directory as one visual node. A node should have one coherent visual language across its scenes, while each new node should deliberately choose a different visual fingerprint from nearby nodes.

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
    "title": "地域管辖"
  }
}
```

Use `catalog.status: "featured"` only for the original node selected to demonstrate a direction. The `/demo/` gallery must preview that node's existing composition and link to `catalog.route`; it must not create a duplicate demo composition or carrier. For a later node that derives from a catalog direction, use fields such as:

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

When a genuinely new direction is authored, complete these steps in the same change:

1. Set its manifest to `catalog.status: "featured"`, `catalog.source: "original-node"`, and its existing `/inkloom/.../` MDX route.
2. Add it to the existing `/demo/` registry or discovery mechanism using the original composition and player metadata.
3. Make the gallery card open the original MDX route. Do not add a new route under `/demo/<direction>/` unless the user explicitly requests a separate curated page.
4. Verify the root gallery preview and the original route at narrow and wide widths.

Do not treat the manifest as proof by itself. The page-still review must confirm the declared fingerprint is visible in the rendered node. Run `pnpm animation:styles`; exact duplicate fingerprints fail, while family reuse produces a warning for deliberate review.
