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

Tags are visible Markdown content, not portable card attributes. In a formal card they stay on the root question or mnemonic line, immediately before the line break that precedes the IAL.

- Preserve existing knowledge tags first. If none exist, compose one stable knowledge tag from source-owned vocabulary in the path, H1, and nearest heading/label. Do not require a hardcoded knowledge namespace and do not introduce a legal category absent from those source locators. Report `missing-tag` only when those locators cannot identify the knowledge scope.
- **Knowledge-tag segments must be stable source-named concepts, never position labels** (`E101`): a segment like `专题二`/`第19讲`/`第三章` or a bare number (`02`) is invalid — the chapter position can shift and says nothing about content. Replace it with the chapter/topic name from the source heading: `#法考/民诉/专题二/诉的分离#` must become `#法考/民诉/诉的基本理论/诉的分离#` (drop `专题二`, keep the named parts; the flashcard filename and H1 may keep their Arabic sort prefix).
- Every accepted card carries exactly one priority tag from `#闪卡/优先级/P1#` through `#闪卡/优先级/P4#`. Assign it by comparing candidates against the supplied source under [priority-calibration.md](priority-calibration.md); no knowledge type or card kind has a fixed level, and P2 is not a fallback — a deck with more than half its cards in P2 fails `E089`. Prefer an explicit user priority when present. Report `missing-priority` only when the source boundary itself is unresolved, not merely because the source omitted a priority tag.

Topic resolution is a separate pre-render step. Use [topic-resolution.md](topic-resolution.md) to complete broad or incomplete provider maps before writing `custom-qb-note-topic-id`; the card protocol never treats a broad file provider as an acceptable child-card fallback.

## Root-container boundary

Read [card-design.md](card-design.md) for the normative `basic`, `cloze`, `mnemonic`, `blockquote`, and `callout` examples. Those examples are the sole template source; this file owns only the portable boundary contract.

- The IAL belongs immediately after the complete card root container. It is outside the list, blockquote, Callout, and any code fence.
- The IAL occupies one physical line, uses exactly one ASCII space after `{:`, uses exactly one ASCII space between attributes, and has no space before `}`.
- A `basic/list` root is the complete list block. The first list item's first paragraph is the direct question. Its first child list starts the back; answer items may contain source-grounded unordered/ordered detail, a small table, or Mermaid. An eligible question-side Mermaid is a non-list direct child block before that first child list and follows [question-side-mermaid.md](question-side-mermaid.md). Generated roots and children carry no `问题：` or `答案：` label.
- Tags stay on the visible front or cue line inside the root container. For a `callout`, keep the plain-text question in the directive title and put knowledge/priority tags on the immediately following quoted line (`> #知识标签# #闪卡/优先级/P1#`), not in the title. Metadata stays in the adjacent IAL; neither may be detached into an ordinary paragraph.
- `blockquote` uses its first child as the question and later children as answers. `callout` uses the directive title itself as the question and its body children as answers; the title must be a plain-text, complete source-grounded question ending in `？` or `?`. A generic title such as “命题陷阱” is not a front, and title styling is forbidden. Neither renderer can carry a question-side Mermaid under this contract. Heading scope never determines the answer boundary; headings and superBlocks are not schema 1 output roots.

Completion criterion: removing the single adjacent IAL leaves one self-contained visible card container, while removing that container leaves no detached card metadata or tags.

## Version route

Schema `1` is the only supported format. If a source requests schema `2`, stop and report that a versioned reference is missing; never silently mix fields or renderers.
