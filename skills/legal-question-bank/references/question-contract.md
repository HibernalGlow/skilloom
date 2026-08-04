# Question Bank Contract

## Ownership

| Layer | Owns | Must not own |
| --- | --- | --- |
| Markdown + IAL | Question content, stable ID, type, answer, topic, solution boundary | Attempt history, derived statistics, device state |
| SiYuan adapter | Blocks, attribute views, Riff integration | Portable `Question` model rules |
| Damophus core | Parsing, answer checking, option mapping, aggregation | SiYuan API calls and UI state |
| Web adapter | Rendering and web attempt storage | Markdown mutation |

## Legacy Migration

1. Infer a topic only when a clear enclosing heading exists; otherwise leave the topic unset and report it.
2. Infer option IDs from a standard option prefix. Do not infer bare paragraphs as options.
3. Infer the solution start from an existing answer/analysis heading only as a migration preview. Write the explicit IAL after confirmation.
4. If IAL and visible answer text conflict, stop the migration for that question. Do not silently choose either value.
5. Preserve all source blocks and existing user attributes. Only add the minimum `custom-qb-*` attributes.

## Stable IDs

Use an ID based on the authoritative source and question identity, not display order. Prefer:

```text
{subject}-{source}-{kind}-{year}-{paper}-{question}
```

For example: `civil-gold-objective-2020-2-1-14`.

Display numbers may change after an insertion. Stable IDs must not.

## Answer Rules

- `single`: one original option ID, for example `A`.
- `multiple`: comma-separated original option IDs in original order, for example `A,B,D`.
- `true-false`: lowercase `true` or `false`.
- `subjective`: do not set a machine-scored answer.

The player may shuffle displayed options and relabel them for a single attempt, but it must map the selection back to original IDs before checking the answer. The solution always uses original ordering and IDs.

## Parser Expectations

The parser reads each question heading until the next question heading. Text before the solution marker is the prompt area; the marker and all following blocks are the solution area. It supports task lists, regular lists and standalone option paragraphs with a recognizable option prefix. `custom-qb-option` is only an exception escape hatch.

## Validation

Run the bundled validator in strict mode. Its structural checks do not prove legal correctness. Manually compare all IDs, answers and solution boundaries with the authoritative source before syncing.
