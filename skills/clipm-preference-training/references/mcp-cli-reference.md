# ClipM MCP And CLI Reference

Use MCP when the `xiranite-clipm` server is connected. Field names below match its structured tool schema.

## Routine tools

| Tool | Key input | Effect |
| --- | --- | --- |
| `environment_status` | none | Read-only runtime, GPU, database, archive-tool, and active-model health. |
| `get_work_score` | `path` | Read-only cached identity and score lookup. Does not open or modify the archive. |
| `apply_feedback` | `workId`, `source: "gui"`, `classification?`, `ranking?` | Append the explicit correction and synchronize database, path, filename suffix, and metadata. Supply at least one corrected field. |
| `list_feedback_events` | `workId?`, `includeUndone`, `limit` | Read event IDs, paths, before/after values, and undo applicability. |
| `undo_feedback` | `eventId`, `source: "gui"` | Append a safe inverse for the latest applicable correction and synchronize projections. |
| `run_auto_training` | `batchSize: 20` | Claim at most one ready batch, train both heads independently, validate, and activate only accepted heads. |
| `list_models` | `includeFailed` | Read active, historical, candidate, and failed bundles. |

## Conditional tools

| Tool | Use only when |
| --- | --- |
| `score_work` | The work is not registered and the user authorizes scoring/renaming/metadata writes. |
| `scan_feedback` | The user changed `[CM...]` suffix values outside ClipM. |
| `list_review_items` | Inspecting pending identity or recovery reviews. |
| `resolve_review_item` | The user explicitly chose `use_filename`, `use_json`, `link_existing`, or `new_work`. |
| `perceptual_recovery_status` | Inspecting page-evidence coverage and conservative recovery candidates. |
| `calibrate_perceptual_recovery` | The user requests maintenance now, or unattended maintenance is unavailable and at least 12 eligible works exist. |
| `train_heads` | The user explicitly requests a manual snapshot/training attempt. Set `allowInsufficientRankingCorrections: true` only when the user also explicitly asks to test below the normal 20-correction ranking minimum. |
| `activate_model` | Activating a validated historical/candidate bundle requested by the user. Never set `force: true` without explicit authorization. |
| `rollback_model` | The user selects a known non-failed historical bundle. |
| `remove_work_metadata` | The user explicitly wants ClipM identity and metadata removed from a work. |
| `migrate_environment` | The user explicitly requests a runtime move. |

## Structured examples

Read one work:

```json
{"path":"E:/Comics/example [CM1P0800-ABCD].zip"}
```

Apply only a score correction:

```json
{"workId":"<uuid>","source":"gui","ranking":920}
```

Apply P/N and score together:

```json
{"workId":"<uuid>","source":"gui","classification":"N","ranking":320}
```

Attempt the normal automatic batch:

```json
{"batchSize":20}
```

Explicitly test the ranking head below its normal minimum:

```json
{"allowInsufficientRankingCorrections":true}
```

This still runs the normal candidate validation and never force-activates a rejected result.

## CLI fallback

Run from the Xiranite repository root. Add `--json` for machine-readable results.

```powershell
bun packages/nodes/clipm/src/cli.ts env status --json
bun packages/nodes/clipm/src/cli.ts feedback history --active-only --limit 100 --json
bun packages/nodes/clipm/src/cli.ts feedback apply <work-id> --classification P --ranking 920 --source gui --json
bun packages/nodes/clipm/src/cli.ts feedback undo <event-id> --source gui --json
bun packages/nodes/clipm/src/cli.ts train auto --batch-size 20 --json
bun packages/nodes/clipm/src/cli.ts train --allow-insufficient-ranking-corrections --json
bun packages/nodes/clipm/src/cli.ts model list --json
```

Do not edit the SQLite database, filename suffix, or `xiranite.cm-score.json` directly.
