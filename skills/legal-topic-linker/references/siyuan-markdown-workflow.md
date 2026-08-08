# SiYuan and Markdown topic-link workflow

## Shared relationship model

```text
question block
  custom-qb-question-topic-ids="topic-a,topic-b"

note provider block
  custom-qb-note-topic-id="topic-a"
```

The topic value is stable and portable. A SiYuan block ID identifies the current physical block only. Re-pasting or rebuilding a note may change the block ID without changing the topic relationship.

## Search order

Search for semantic fit, not only identical wording:

1. exact current topic value and any existing provider;
2. decisive legal phrase from the answer analysis;
3. the condition, exception, procedural stage, and consequence separately;
4. close doctrinal synonyms;
5. likely corpora, especially 精讲卷 and 背诵卷;
6. the remaining workspace or Markdown archive.

Prefer the smallest exact block. Path labels are ranking hints, not proof that a provider is correct.

## Markdown branch

Question attributes belong in the question IAL:

```markdown
## 题目
{: custom-qb-id="civil-question-1" custom-qb-question-topic-ids="civil-topic-a,civil-topic-b" custom-qb-type="multiple" custom-qb-answer="A,C"}
```

Provider attributes attach directly to an atomic heading or a dedicated paragraph anchor:

```markdown
### 经确认收悉后的电子送达与缺席判决
{: custom-qb-note-topic-id="civil-procedure-summary-service-default-judgment-confirmed-receipt"}
```

```markdown
**考点：经确认收悉后的电子送达与缺席判决**
{: custom-qb-note-topic-id="civil-procedure-summary-service-default-judgment-confirmed-receipt"}
```

Rules:

- Modify only the adjacent IAL unless a separate content edit is authorized.
- Preserve attribute order where practical and preserve every unrelated attribute exactly.
- Do not add `custom-qb-note-topic-id` to a question IAL.
- Do not add `custom-qb-question-topic-ids` to a normal note provider.
- One provider IAL contains one topic ID.
- Validate both question-bank and MarkNote output after changes.

## SiYuan branch

Always select the workspace explicitly:

```powershell
siyuan -w "D:\1STUDY\SIYUAN" ...
```

Read-only phase:

1. Locate the exact question block and read its attributes and content.
2. Read the full question boundary, including analysis, before judging granularity.
3. Search candidate note blocks and inspect their content, parent headings, document path, and existing attributes.
4. Exclude the current question block as its own provider.
5. Record exact block IDs only in the write manifest, never as topic values.

Provider writes:

- Use `legal-marknote/scripts/siyuan_topic_manifest.py` for existing SiYuan note documents.
- Export the outline, review actions, preview without confirmation, then apply with `--confirm`.
- The manifest workflow protects unrelated attributes and detects stale blocks.

Question writes:

- Build a separate exact block-ID manifest containing old and new `custom-qb-question-topic-ids` values.
- Preview every write and stop if the live value differs from the captured old value.
- After explicit confirmation, set only the question-topic attribute.
- Read the attribute back and compare unrelated attributes before and after.

Never export and re-import an existing SiYuan document to apply topic metadata. That can replace blocks and damage references, backlinks, and manual edits.

## Conflict rules

Stop rather than overwrite when:

- a provider already declares a different topic;
- a question's live topic value changed after audit;
- the candidate block is broad or only approximately relevant;
- the proposed split affects other questions or providers not yet reviewed;
- a block disappeared or its content changed materially;
- legal analysis does not support one clear proposition.

## Verification

After writes:

1. Read every changed attribute back by file location or SiYuan block ID.
2. Re-run `audit_topic_links.py` across questions and providers.
3. Run the existing legal-question-bank and legal-marknote validators.
4. Confirm that each question topic has at least one exact provider or is listed as an open provider gap.
5. Review high-fanout topics semantically; high reuse can be valid, but it often reveals a chapter-level ID.
