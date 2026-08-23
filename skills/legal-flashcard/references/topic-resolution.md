# Atomic topic resolution

Read this reference in both ordinary and dedicated modes whenever a source note has no topic provider, only a broad file-level provider, or a provider map that is visibly less detailed than the source's atomic sections. Do not load it for a note whose provider already matches each atomic range.

## Evidence order

Resolve a topic ID in this order and record the evidence used:

1. Read every `custom-qb-note-topic-id` in the source note and its adjacent `*.topic-map.json` manifest, if present. A provider attached to a real `##`/`###` heading or standalone `**考点：...**` anchor owns the following range until the next sibling provider.
2. If the source has only one broad provider, inspect the same subject/teacher directory for completed multi-provider notes. Reuse the established ID vocabulary when a heading or anchor has the same legal scope.
3. Search the repository's confirmed provider catalog and existing notes for exact or near-exact heading/topic matches. Prefer an existing ID over creating a synonym. The catalog is an evidence source, not a reason to attach its broad parent ID to every child range.
4. Check the source's own headings, tables, mnemonic labels, and question boundaries. Split a file into atomic ranges only where each range has an independently reviewable legal subject, rule, procedure, exception, result, or mnemonic.

## Self-completion rule

Complete an incomplete map without asking the user when either route is available:

1. Reuse a stable existing child ID found by the evidence order.
2. When only a confirmed broad parent exists, derive a child ID as `<parent-id>-<atomic-scope-key>`. The scope key must name the source range or relation, remain lowercase ASCII kebab-case, follow vocabulary already used by neighboring providers, and survive repeated generation unchanged. Search the repository for both ID and same-scope collisions before accepting it. Record `derived-child`, parent ID, source heading/range, scope key, and collision-search result in the working map.

The card root's `custom-qb-note-topic-id` mounts that derived child provider; this skill does not need to rewrite the source note. Do not translate or expand legal content to create a topic: the provider name may be derived, but its scope must be verbatim-grounded in a supplied heading, label, or independently testable source relation.

Report `missing-topic` only when there is no confirmed parent, the atomic boundary is ambiguous, a collision cannot be resolved from repository vocabulary, or a stable scope key cannot be formed. Do not emit the broad provider as a fallback.

## Broad-provider guard

A broad provider is not made atomic by card count. If one provider covers two or more independently gradable recall axes (for example definition, composition, policy, procedure, or legal effect), each axis must reuse or derive a child provider before it can be accepted. A child may own multiple cards only when those cards are variants of the same axis or tightly bounded peers in one closed list. Record the axis-to-provider map in working context; never attach the broad ID to several unrelated cards merely because the total is four or fewer.

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

One topic ID may provide multiple notes, but in a single flashcard output it may own at most four accepted cards by default. This is a per-axis cap, not permission to merge axes. When a fifth card is useful, split the recall target into another confirmed atomic topic or reject it under an explicitly requested card budget; do not silently raise the limit.

## Completion checklist

- Every source range used by a candidate has one narrow topic ID or an explicit gap record.
- The ID is reused from a manifest, existing note, or catalog, or is a collision-checked derived child of a confirmed parent; the evidence is recorded.
- No broad file-level ID is reused as a child-card fallback.
- The final card report includes topic-mapping gaps separately from ordinary rejection reasons.
