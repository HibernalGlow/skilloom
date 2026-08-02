---
name: clipm-preference-training
description: Operate the Xiranite ClipM/CM comic preference node through standard MCP or xclipm CLI to read scores, record user-confirmed P/N and 0-1000 corrections, audit or undo feedback, and safely trigger validated automatic training. Use when the user asks an agent to correct doujin/comic preferences, help train ClipM, inspect CM feedback, or check model-training readiness.
---

# ClipM Preference Training

Use ClipM as the authority for comic preference identity, feedback, model training, and artifact synchronization.

## Core contract

- Treat `P`/`N` and the `0-1000` score as the user's personal judgment. Never infer or overwrite either field without an explicit user choice.
- Change only the fields the user supplied. Do not rescore a corrected work to manufacture labels.
- Prefer standard ClipM MCP tools. Use `xclipm` only when MCP is unavailable.
- Let ClipM synchronize SQLite, filename suffix, root metadata, paths, training snapshots, validation, and activation.
- Never force-activate a rejected model. Never resolve identity conflicts, remove metadata, migrate the runtime, or rescore a library without explicit authorization.

Read [MCP and CLI reference](references/mcp-cli-reference.md) before issuing calls. For skill evaluation, read [evaluation scenarios](references/evaluations.md).

## Correction workflow

1. Call `environment_status`; stop on an unhealthy database or missing active model.
2. Call `get_work_score` with the exact current path. If it is unknown, ask before using the mutating `score_work` tool.
3. Restate the proposed change when the user's P/N or score is ambiguous.
4. Call `apply_feedback` with the returned `workId`, `source: "gui"`, and only the confirmed fields:
   - `classification: "P" | "N"`
   - `ranking: 0..1000`
5. Verify the returned label, score, and current path. ClipM may rename the file to update its `[CM...]` suffix.
6. Call `list_feedback_events` with `includeUndone: false` and the `workId`; retain the latest `eventId` for audit or undo.
7. Report the changed fields and synchronized path. Do not manually edit the filename or metadata JSON.

## Training workflow

1. Inspect active feedback with `list_feedback_events(includeUndone: false)` and current bundles with `list_models`.
2. Prefer unattended maintenance. When the user asks to train now, call `run_auto_training` with its normal `batchSize: 20`.
3. Do not lower the batch size merely to force a test. A claimed undersized diagnostic batch can be consumed even when a head correctly skips training.
4. Only when the user explicitly asks to test below the ranking minimum, call `train_heads` with `allowInsufficientRankingCorrections: true`. This does not weaken validation or permit forced activation.
5. Interpret classification and ranking independently:
   - `skipped`: prerequisites are missing; keep collecting the named correction type.
   - `rejected`: validation protected the active model; do not force activation.
   - `accepted`: ClipM persists and activates that head automatically.
6. Confirm the final `activeBundleVersion` with `list_models`.
7. Report exact status/reasons and the remaining correction requirement. Do not claim that a model trained when both heads skipped.

## Recovery and mistakes

- Undo a mistaken correction with `undo_feedback(eventId, source: "gui")`; do not apply a guessed inverse value.
- Use `scan_feedback` only when the user edited CM filename suffixes outside ClipM.
- List pending `recovery_candidate` or identity reviews, but require the user to choose a resolution.
- Perceptual recovery only proposes review candidates. It must never merge works automatically.

## Completion evidence

Return:

- environment health and active bundle version;
- work ID/path and exact corrected fields;
- feedback event ID when a correction was written;
- training status for each head, validation reasons, and final active version;
- any action intentionally deferred for user confirmation.
