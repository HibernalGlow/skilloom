---
name: damophus-dev
description: "Use when explicitly invoked as $damophus-dev to develop the Damophus SiYuan question-bank plugin: plan, implement, debug, test, review, package, or commit changes across its portable TypeScript core, SiYuan adapters, exam and question-set features, and Svelte UI."
---

# Damophus Development

Use this skill only after the user explicitly invokes `$damophus-dev`. Treat the repository as a layered plugin whose existing code and tests are the primary source of truth.

## Start With Context

1. Read the repository status, applicable `AGENTS.md` files, recent commits, package scripts, and the target module before editing.
2. Preserve all unrelated user changes. Establish the task boundary from the request and current diff; do not reset, checkout, or broadly reformat the worktree.
3. For an ambiguous or architectural change, run `$grill-me` or `$grill-with-docs` before implementation. Do not invent decisions that require the user's authority.

## Architecture

- Keep domain behaviour, schemas, state machines, scoring, parsing, and storage contracts in framework-independent TypeScript.
- Keep SiYuan kernel calls, Attribute Views, Riff, and plugin data APIs in adapters.
- Keep Svelte thin: render state, collect input, dispatch typed events, and own only transient presentation state.
- Keep each module's user-facing appearance in one module-owned contract. Declare a semantic icon key once, resolve it through surface adapters for SiYuan symbol IDs and Lucide/Svelte components, and make settings, menus, Docks, and tabs consume that same declaration. For icon changes, use Browser Mode to verify the rendered settings icon and ensure registered module icons remain distinct.
- **UI component policy**: For every Svelte UI change, inspect the repository's installed component stack before writing markup. Prefer existing `shadcn-svelte` components first; when a needed primitive is not yet wrapped, use a compatible Svelte primitive/library already in the project, prioritizing `bits-ui`, `melt-ui`, `lucide-svelte`, and other maintained Svelte libraries that preserve the shadcn styling and accessibility model. Compose these primitives into domain-specific views, but do not hand-roll foundational controls or interaction primitives: no custom buttons, inputs, selects, comboboxes, dialogs, popovers, menus, tabs, tooltips, switches, dropdowns, toasts, command palettes, focus traps, keyboard navigation, or modal behavior implemented from raw HTML/CSS/events. Do not draw replacement SVG icons when a library icon exists. If no compatible library component exists, stop and record the gap, then get explicit approval before introducing a new primitive; a bespoke business layout that composes library components is allowed.
- **UI decision record**: Before adding a new UI dependency or component, record the searched component/library, the closest existing shadcn-svelte or compatible primitive, the accessibility/state behavior it supplies, and why reuse is insufficient. A component change is incomplete if its diff contains a new foundational primitive without that record and approval.
- Register centrally managed entry surfaces through the shared entry declaration instead of duplicating desktop Dock, mobile Dock, plugin menu, command, or tab switches inside module settings. The central entry page must render only declared capabilities, preserve existing storage keys, and never hide or reconfigure a SiYuan-native surface that the module does not own.
- Preserve the boundary between question content, immutable attempt history, derived statistics, recoverable session state, and question-set assembly.
- Existing question content is read-only by default. Mutate metadata or records only when the request authorizes it.
- For cross-document assembly, consume the exported blueprint and frozen question queue contracts. The user currently permits edits to `assembly/**`, but preserve its public interfaces and coordinate shared-file changes explicitly.

## Mature Implementations First

When implementing a familiar capability, first locate a mature reference implementation or repository. Clone it, inspect its source at a pinned commit, and prefer adapting proven code or an established library over hand-rolled logic. Record useful provenance in the project's reference-sources document when the repository convention provides one. Respect the user's licensing decision while retaining enough provenance to explain what was reused.

## Implementation Loop

1. Define the smallest vertical slice and its observable completion condition.
2. Reuse existing types, schemas, adapters, and UI primitives before adding abstractions.
3. For UI work, search and reuse the shadcn-svelte/compatible component layer before designing markup; install or add a primitive only after checking the current package manifest and documenting the decision above.
4. Add or update focused tests with the change. Keep core tests independent of SiYuan and keep browser tests for user-visible workflows.
5. For UI or styling work, assume the emitted plugin stylesheet affects the entire SiYuan document. Express descendant-dependent layout through component state, `data-*` attributes, or stable layout rules; do not add relational selectors such as `:has()` to globally injected CSS.
6. Inspect the diff for accidental content mutation, duplicated state, stale imports, oversized Svelte logic, raw foundational controls, replacement SVGs, and unrelated formatting.
7. Discover the repository's current validation scripts from `package.json` and configuration, then run the narrowest relevant checks followed by the full checks required by the change.
8. After every UI or styling build, inspect `dist/index.css` and dynamically injected CSS in `dist/index.js`, then run `pnpm test:package`. The package validation must fail if either artifact contains `:has(`; do not bypass or weaken this gate.
9. When fixing a measured rendering regression, record the real SiYuan Web surface before and after the fix. Use the browser DevTools performance recorder on the same interaction, include an enabled/disabled A/B comparison, and compare style recalculation time, long tasks, and dropped frames before declaring success.
10. Commit only this task's files after validation, using a functional commit message. Leave unrelated work unstaged and report it.

## Native Mobile Review Rendering Gate

For controls injected into SiYuan's native mobile flashcard toolbar, treat SVG painting as the completion criterion:

- Create both the outer `<svg>` and its `<use>` child with `document.createElementNS("http://www.w3.org/2000/svg", ...)`. `document.createElement("svg")` creates an HTML-namespace element that can occupy space while rendering no icon.
- Set both `href` and SVG 1.1 `xlink:href` on every `<use>` symbol. SiYuan 3.8.x mobile templates still use `xlink:href`.
- Browser tests must assert the outer element's `namespaceURI`, both symbol attributes, and action dispatch. A selector count or accessible label alone is not rendering evidence.
- After deployment, reload SiYuan/plugin code, open the native review surface, and capture a real browser screenshot at the affected mobile viewport (use 721x1011 when reproducing the compact mobile layout). Confirm every injected icon is visibly painted and the action group is contiguous with the native filter/more/close controls.
- Record both DOM geometry and screenshot evidence. If an element has a nonzero box but its icon is not visible, the rendering gate is failed and the change is not complete.

## Data Rules

Markdown and IAL remain the authoritative question-content source. Attribute View rows and other append-only events hold attempts and derived data is rebuildable. Plugin data files hold recoverable in-progress state, not the only copy of durable history. Add schema versions and migrations before writing new managed fields.

## Completion Gate

The task is complete only when the requested behaviour is implemented, relevant tests pass, type checking and packaging/build checks appropriate to the change pass, the final diff has been reviewed, and the commit boundary is clear. A rendering-performance fix also requires real-SiYuan before/after evidence and a passing emitted-artifact CSS gate. Report any unrelated failures separately instead of hiding them.

Read [project-contract.md](references/project-contract.md) when the change crosses content, adapter, core, exam, assembly, or UI boundaries.
