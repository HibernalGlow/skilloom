---
name: legal-topic-linker
description: Audit and repair point-to-point links between legal questions and reusable note providers. Use when a legal question is missing custom-qb-question-topic-ids, uses chapter- or专题-level topic IDs that are too broad, lacks a matching custom-qb-note-topic-id provider, or needs an exact provider bound in SiYuan or Markdown, especially in 精讲卷 or 背诵卷.
---

# Legal Topic Linker

Build a precise relationship graph from each question to the smallest reusable legal proposition that decides it, then bind that stable topic value to exact note-provider blocks.

## Non-Negotiable Contract

- Treat `custom-qb-question-topic-ids` as question-to-topic references.
- Treat `custom-qb-note-topic-id` as a note block providing one topic.
- Use the same lowercase ASCII kebab-case topic value in both directions.
- Do not store a SiYuan block ID in either topic attribute. Block IDs are navigation and mutation targets only.
- Keep broad chapter, section, and专题 labels as taxonomy, never as point-to-point relationship keys.
- A question may reference multiple atomic topics. A provider block declares exactly one topic; multiple exact providers may reuse the same topic ID.
- Preserve question text, note text, hierarchy, references, backlinks, and unrelated attributes unless the user explicitly authorizes a content edit.

Read [the granularity rubric](references/granularity-rubric.md) before proposing or replacing topic IDs. Read [the SiYuan and Markdown workflow](references/siyuan-markdown-workflow.md) before searching or writing providers.

## Workflow

### 1. Establish Scope

Identify the exact question files, directories, SiYuan documents, or question blocks. Also identify candidate note corpora. Search 精讲卷 and 背诵卷 first when present, but allow any source with the best semantic fit.

Run the structural inventory before semantic edits:

```powershell
python -X utf8 scripts/audit_topic_links.py <question-or-note-path> [more-paths]
```

For machine-readable output:

```powershell
python -X utf8 scripts/audit_topic_links.py <paths> --format json --json-out topic-link-audit.json
```

The script inventories attributes and relationship gaps. It does not decide legal meaning and does not write files.

### 2. Audit Every Question Semantically

For each question, read the stem, options, answer, and analysis. Do not accept an existing topic merely because the attribute is present.

Classify each current topic as:

- `exact`: expresses the decisive legal proposition tested;
- `incomplete`: misses an independently tested condition, exception, consequence, or procedural step;
- `broad`: names only a subject, chapter, system, or专题;
- `wrong`: does not match the answer's controlling proposition.

Produce a review table containing question ID, current topics, proposed atomic topics, disposition, and short legal basis. Do not write until every in-scope question has a reviewed result.

### 3. Design Stable Atomic Topic IDs

Name the rule, not the source. Include the legal domain, doctrine or procedure, and the operative condition, exception, or consequence. Exclude year, source name, question number, and display order.

Reuse an existing ID only when the proposition is genuinely identical. Similar doctrine with a different trigger or consequence requires a different ID. When replacing a coarse ID, show an explicit old-to-new migration preview and every affected question/provider.

### 4. Find Exact Note Providers

Only search providers after question topics are confirmed. For each atomic topic:

1. Search exact legal terms, decisive conditions, consequences, and close doctrinal synonyms.
2. Prefer the smallest stable heading or paragraph block that fully explains the proposition.
3. Rank semantic completeness above source path; use 精讲卷 before 背诵卷 only when both are exact enough.
4. Bind all independently useful exact providers if several notes explain the same proposition.
5. Reject a broad heading that merely contains the answer somewhere in a large subtree.
6. If no exact provider exists, report a provider gap. Propose a dedicated `**考点：显示名**` anchor only when it can attach to existing exact explanatory content without distorting the note.

Never include the current question block itself as its own note provider. A question-containing ancestor may remain discoverable as a source, but it is not the preferred reusable provider for that same question.

### 5. Preview Writes

Separate review from mutation. The write plan must list, for every change:

- source file or SiYuan document;
- exact Markdown IAL location or SiYuan block ID;
- old attribute value;
- new attribute value;
- reason for the change;
- unrelated attributes that must remain unchanged.

Stop on ambiguous legal meaning, conflicting existing attributes, stale SiYuan blocks, or a provider that is only approximately related.

### 6. Apply and Verify

For Markdown, edit only the adjacent IAL and preserve all unrelated attributes. Run the repository's question-bank and MarkNote validators afterward.

For SiYuan, use the workspace explicitly:

```powershell
siyuan -w "D:\1STUDY\SIYUAN" ...
```

Use the existing `legal-marknote/scripts/siyuan_topic_manifest.py` workflow for provider attributes. Preview question-attribute changes by exact block ID, obtain explicit confirmation for the mutation set, then read every changed attribute back. Do not export, edit, and re-import an existing SiYuan document.

### 7. Re-Audit the Graph

Run `audit_topic_links.py` again across the changed question and note corpora. Resolve all structural errors. Review every topic without a provider and every high-fanout topic warning. Report unresolved semantic or provider gaps explicitly; do not hide them by assigning a broad fallback.

## Output

Return four concise sections:

1. `Question audit`: exact, refined, missing, and wrong topics.
2. `Provider bindings`: topic ID to exact note providers.
3. `Applied changes`: files or SiYuan block IDs and verified attributes.
4. `Open gaps`: topics without an exact provider or questions requiring legal judgment.

The deterministic audit can prove attribute structure and graph coverage. It cannot prove that a topic is legally correct or sufficiently fine-grained; that conclusion must come from reading the question and provider content.
