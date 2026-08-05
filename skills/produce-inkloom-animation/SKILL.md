---
name: produce-inkloom-animation
description: "Coordinate Luna-led production, repair, or completion of InkLoom legal Remotion animations by keeping the current top-level thread as the sole coordinator and independent auditor while delegating every quality-affecting animation decision and revision to one gpt-5.6-sol worker. Use when the user asks Luna to make, supplement, rewrite, repair, render, publish, or place an InkLoom animation through Sol, especially when Sol must finish rather than stop at a timeout or partial status."
---

# Produce InkLoom animation

Use this skill together with $inkloom-dev. Let $inkloom-dev define the legal-animation, repository, QA, publication, and SiYuan contracts. Let this skill exclusively define agent topology, ownership, persistence, and handoffs.

## Fixed topology

- Treat the current top-level thread as Luna, the sole coordinator and final auditor. Do not create a Luna, coordinator, supervisor, or QA subagent.
- From the current thread, create exactly one gpt-5.6-sol worker with medium reasoning for the animation quality write set. Do not ask Luna to create Sol through another child.
- Instruct Sol not to create subagents and not to perform or claim the final independent audit.
- Keep only one live Sol worker for the task. Send every continuation and返工 request to that same worker. Never start concurrent workers on the same animation.
- If delegation tools or the requested model are unavailable, say that Sol was not invoked and stop before quality implementation. Do not substitute Luna work or describe preparation as a successful Sol handoff.

## Ownership boundary

Give Sol exclusive ownership of every choice or edit that can directly affect animation quality:

- legal-rule-to-visual mapping, learning-objective grouping, scene count, scene architecture, and semantic continuity;
- visual direction, visual structure, composition grammar, layout, canvas use, typography, icons, diagrams, connectors, colors, surfaces, and hierarchy;
- Remotion markup, node-local visual components and styles, timing, sequencing, transitions, motion semantics, pacing, stable final frames, and readability;
- all animation-quality fixes arising from legal or visual audit findings;
- node-local visual-direction and visual-structure manifests when required by $inkloom-dev.

Do not let Luna directly repair these files or choices after delegation. Luna may identify defects and prescribe acceptance criteria, but must return quality-affecting changes to the same Sol worker.

Give Luna ownership of preparation, independent audit, and operational work:

- read the exact source block or note, nearby context only when needed, existing node, stable IDs, manifests, routes, repository rules, and concurrent Git state;
- resolve a Markdown insertion target before editing: prefer the matching organized note under `20-整理`; use the matching MinerU note under `10-mineru/content` only when the organized note does not exist. An explicit request for the "original" or "source" note does not override this order. Verify the selected path exists, contains the expected topic, and record the selected path plus whether fallback was used;
- determine whether the request is creation, supplementation, rewrite, placement-only repair, or publication-only work;
- prepare a source-grounded brief containing required legal points, stable public identities, hard constraints, relevant files, and completion evidence without dictating a generic visual solution;
- run style checks, page capture, contact-sheet generation, builds, AVIF publication, production verification, SiYuan insertion or movement, deployment checks, and scoped Git operations;
- inspect the complete all-scenes contact sheet and other evidence independently, record concrete legal and visual defects, decide pass or返工, and send defects back to Sol;
- report only evidence Luna personally verified.

Thin MDX carriers, routing metadata, publication commands, SiYuan operations, and other visually neutral integration work belong to Luna unless changing them would affect the animation's rendered quality.

When the user explicitly requests insertion into a Markdown/source note, Luna must also own that source-note integration. Treat it as a required completion phase after AVIF publication: select the existing organized `20-整理` note first and fall back to the MinerU `10-mineru/content` note only when no organized note exists; verify the selected path before editing; map every semantic scene to its matching section; insert exactly one verified production AVIF image immediately after that section; preserve legal text; and independently verify exact URL counts, legal order, adjacency, and a narrow diff. Report the selected note path and fallback decision. Do not report the animation complete while this requested source-note insertion is pending.

## Workflow

1. Load $inkloom-dev and every task-relevant skill it requires before editing or delegation.
2. Let Luna complete the fast source, placement, stable-ID, repository-state, and existing-artifact preflight.
3. Give the single Sol worker the raw legal source, exact task scope, relevant InkLoom paths, $inkloom-dev quality constraints, stable identities, and explicit completion evidence. Tell Sol that it owns all quality-affecting implementation and revisions.
4. Let Sol work until the requested quality write set is implemented and its focused checks or render inputs are ready. Luna may inspect status and files, but must not compete on the same write set.
5. Let Luna run the required audits and inspect the generated visual evidence independently. A successful build, render, or contact-sheet command is not visual approval.
6. If any quality defect exists, send one concrete defect list to the same Sol worker and require source fixes plus regenerated evidence. Repeat Sol revision and Luna audit until the animation passes.
7. After quality approval, let Luna perform publication, production-URL verification, SiYuan placement, deployment validation, and narrowly scoped Git commit or push work required by $inkloom-dev and the user.

## Completion persistence

- Define Sol's terminal condition as completed requested implementation with the promised files and focused evidence, not elapsed time, token pressure, a quiet wait, or a partial status report.
- Explicitly forbid self-issued shutdown messages such as "implementation timed out", "stop immediately", "do not modify the workspace", or "return current status only" when no genuine external blocker exists.
- Do not impose an arbitrary wall-clock deadline on Sol. Use bounded wait calls only to keep the parent responsive; a wait timeout means check again, not cancel the worker.
- If Sol returns partial work, a progress summary, or a self-declared timeout, reject it as incomplete and immediately send a continuation to the same worker with the remaining acceptance criteria.
- If Sol is still running, keep waiting and monitoring. Do not interrupt it merely to obtain a status message and do not treat silence as failure.
- Accept a blocked result only for a concrete external condition Sol cannot resolve, supported by commands, errors, or missing authority. Luna must independently verify the blocker and exhaust safe in-scope alternatives.
- If the platform irreversibly terminates the original Sol and follow-up is impossible, do not claim completion. Start at most one replacement Sol to continue the remaining work, never concurrently, and disclose that the replacement was forced by platform termination.

## Audit and handoff rules

- Do not ask Sol to approve its own work. Sol may run implementation checks, but Luna owns the pass or返工 decision.
- Do not let Luna rewrite the animation during audit. Preserve reviewer independence by returning all quality changes to Sol.
- Do not publish, embed, push, or call the animation finished until Luna has inspected the required visual evidence and confirmed legal-content coverage.
- Distinguish animation quality completion from unrelated site-wide build or deployment blockers. Preserve completed scoped work and report unrelated blockers separately.
- Preserve unrelated dirty work and commit only owned paths in the correct nested repository.
