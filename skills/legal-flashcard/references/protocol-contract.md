# DAMO card protocol schema 1

## Portable fields

| Field | Required on accepted card | Meaning | Constraint |
| --- | --- | --- | --- |
| `custom-dm-source-key` | yes | stable source identity | non-empty ASCII key; not a block/database ID |
| `custom-dm-card-id` | yes | stable business card identity | lowercase ASCII kebab-case; unique in output |
| `custom-dm-card-schema` | yes | protocol version | exactly `"1"`; route another version explicitly |
| `custom-dm-card-kind` | yes | semantic kind | `basic`, `cloze`, or `mnemonic` |
| `custom-dm-card-renderer` | yes | current container | `list`, `mark`, `blockquote`, or `callout` |
| `custom-qb-note-topic-id` | yes | card's atomic note-topic provider | exactly one confirmed lowercase kebab-case ID |
| `custom-qb-question-topic-ids` | forbidden | question-bank reference field | reserved for questions; never emit on flashcards |

`custom-dm-card-kind` and `custom-dm-card-renderer` are independent. The skill does not emit `custom-riff-decks`, due, interval, review log, suspend, bury, device state, or guessed future SiYuan attributes. Topic tags and flashcard priority tags remain separate:

```text
#法考/民法/债法/债权人代位权/成立要件#
#闪卡/优先级/P1#
```

Topic resolution is a separate pre-render step. Use [topic-resolution.md](topic-resolution.md) to complete broad or incomplete provider maps before writing `custom-qb-note-topic-id`; the card protocol never treats a broad file provider as an acceptable child-card fallback.

## Root-container templates

Default basic/list:

```markdown
- 问题：**债权人代位权**{: style="color: var(--b3-font-color10);"}的成立要件是什么？
    - 答案：债权人对债务人享有合法有效的到期债权。
    - 答案：债务人怠于行使权利并影响债权实现。
{: custom-dm-source-key="civil-2026-lecture-08" custom-dm-card-id="fc-civil-subrogation-elements-v1" custom-dm-card-schema="1" custom-dm-card-kind="basic" custom-dm-card-renderer="list" custom-qb-note-topic-id="civil-subrogation-elements"}
```

Cloze/mark, only for a short term:

```markdown
- 问题：**债权人代位权**{: style="color: var(--b3-font-color10);"}针对的是债务人的何种权利？==专属性权利==除外。
{: custom-dm-source-key="civil-2026-lecture-08" custom-dm-card-id="fc-civil-subrogation-excluded-rights-v1" custom-dm-card-schema="1" custom-dm-card-kind="cloze" custom-dm-card-renderer="mark" custom-qb-note-topic-id="civil-subrogation-excluded-rights"}
```

The IAL belongs immediately after the root list block. It must occupy one physical line, use exactly one ASCII space after `{:`, use exactly one ASCII space between attributes, and have no space before `}`. It must not be placed inside a question code fence, in a detached paragraph, or after an unrelated heading.

Mnemonic/list:

```markdown
- **口诀**{: style="color: var(--b3-font-color12);"}：==三分法定、两步审查、先赔后补==
    - 句一：==三==分法定（取首字）
    - 句二：==两==步审查（取首字）
    - 句三：==先==赔后补（取首字）
    - 组合：==三两先==
{: custom-dm-source-key="admin-2026-lecture-12" custom-dm-card-id="fc-admin-review-mnemonic-v1" custom-dm-card-schema="1" custom-dm-card-kind="mnemonic" custom-dm-card-renderer="list" custom-qb-note-topic-id="admin-review-order"}
```

The mnemonic phrase and every source sentence's contributing character or segment are retrieval content, not decoration. If the source does not show the sentence-to-character mapping, stop and report `ambiguous-boundary` or `unsupported` instead of reconstructing it.

## Version route

Schema `1` is the only supported format. If a source requests schema `2`, stop and report that a versioned reference is missing; never silently mix fields or renderers.
