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
- Preserve the boundary between question content, immutable attempt history, derived statistics, recoverable session state, and question-set assembly.
- Existing question content is read-only by default. Mutate metadata or records only when the request authorizes it.
- For cross-document assembly, consume the exported blueprint and frozen question queue contracts. The user currently permits edits to `assembly/**`, but preserve its public interfaces and coordinate shared-file changes explicitly.

## Mature Implementations First

When implementing a familiar capability, first locate a mature reference implementation or repository. Clone it, inspect its source at a pinned commit, and prefer adapting proven code or an established library over hand-rolled logic. Record useful provenance in the project's reference-sources document when the repository convention provides one. Respect the user's licensing decision while retaining enough provenance to explain what was reused.

## Implementation Loop

1. Define the smallest vertical slice and its observable completion condition.
2. Reuse existing types, schemas, adapters, and UI primitives before adding abstractions.
3. Add or update focused tests with the change. Keep core tests independent of SiYuan and keep browser tests for user-visible workflows.
4. Inspect the diff for accidental content mutation, duplicated state, stale imports, oversized Svelte logic, and unrelated formatting.
5. Discover the repository's current validation scripts from `package.json` and configuration, then run the narrowest relevant checks followed by the full checks required by the change.
6. Commit only this task's files after validation, using a functional commit message. Leave unrelated work unstaged and report it.

## Data Rules

Markdown and IAL remain the authoritative question-content source. Attribute View rows and other append-only events hold attempts and derived data is rebuildable. Plugin data files hold recoverable in-progress state, not the only copy of durable history. Add schema versions and migrations before writing new managed fields.

## Completion Gate

The task is complete only when the requested behaviour is implemented, relevant tests pass, type checking and packaging/build checks appropriate to the change pass, the final diff has been reviewed, and the commit boundary is clear. Report any unrelated failures separately instead of hiding them.

Read [project-contract.md](references/project-contract.md) when the change crosses content, adapter, core, exam, assembly, or UI boundaries.
