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
  "transition": "hard vertical wipe at chapter boundary"
}
```

Do not treat the manifest as proof by itself. The page-still review must confirm the declared fingerprint is visible in the rendered node. Run `pnpm animation:styles`; exact duplicate fingerprints fail, while family reuse produces a warning for deliberate review.
