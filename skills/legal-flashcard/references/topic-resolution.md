# Atomic topic resolution

Read this reference in both ordinary and dedicated modes whenever a source note has no topic provider, only a broad file-level provider, or a provider map that is visibly less detailed than the source's atomic sections. Do not load it for a note whose provider already matches each atomic range.

## Evidence order

Resolve a topic ID in this order and record the evidence used:

1. Read every `custom-qb-note-topic-id` in the source note and its adjacent `*.topic-map.json` manifest, if present. A provider attached to a real `##`/`###` heading or standalone `**考点：...**` anchor owns the following range until the next sibling provider.
2. If the source has only one broad provider, inspect the same subject/teacher directory for completed multi-provider notes. Reuse the established ID vocabulary when a heading or anchor has the same legal scope.
3. Search the repository's confirmed provider catalog and existing notes for exact or near-exact heading/topic matches. Prefer an existing ID over creating a synonym. The catalog is an evidence source, not a reason to attach its broad parent ID to every child range.
4. Check the source's own headings, tables, mnemonic labels, and question boundaries. Split a file into atomic ranges only where each range has an independently reviewable legal subject, rule, procedure, exception, result, or mnemonic.

## Self-completion rule

The agent must complete an incomplete map itself when the evidence order yields a stable existing ID. It should add the resolved mapping to its working topic map and use that ID for ordinary candidates and dedicated card metadata; it does not need to ask the user merely because the original file had one broad provider.

Do not invent an ID by translating a heading when no confirmed match exists. Instead report `missing-topic` with the unresolved heading, the broad provider found, the catalog/sibling searches performed, and the exact evidence needed to confirm it. Do not emit a card with the broad provider as a fallback.

## Mounting patterns

Use the existing note style:

```markdown
## 一、证据保全
{: custom-qb-note-topic-id="civil-procedure-evidence-preservation"}

## 二、举证期限与逾期举证
{: custom-qb-note-topic-id="civil-procedure-evidence-deadline"}
```

If a heading would distort the source hierarchy, use an independent anchor immediately before its range:

```markdown
**考点：附条件不起诉**
{: custom-qb-note-topic-id="criminal-procedure-minor-conditional-nonprosecution"}
```

One topic ID may provide multiple notes, but in a single flashcard output it may own at most four accepted cards by default. When a fifth card is useful, split the recall target into another confirmed atomic topic or reject it under the card budget; do not silently raise the limit.

## Completion checklist

- Every source range used by a candidate has one narrow topic ID or an explicit gap record.
- The ID is confirmed by a manifest, an existing note, a maintained catalog, or an exact same-scope mapping; the evidence is recorded.
- No broad file-level ID is reused as a child-card fallback.
- The final card report includes topic-mapping gaps separately from ordinary rejection reasons.
