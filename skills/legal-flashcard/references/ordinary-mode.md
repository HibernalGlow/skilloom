# Ordinary mode

This mode supplements `legal-marknote`; it does not replace any MarkNote rule. Keep its legal-content, source, title, table, image, color, and structure contract unchanged. Read the existing MarkNote references for those rules instead of copying them here. When a provider is broad or incomplete, load [topic-resolution.md](topic-resolution.md) and complete the candidate mapping before recording candidates.

Load only this ordinary reference on the ordinary path. Do not load the dedicated-card, protocol, or mnemonic references unless the user explicitly requests formal cards.

## Procedure

1. Atomic pass: split only independently recallable definitions, elements, exceptions, procedures, or legal effects. Keep an inseparable legal argument together. Done when every split has a distinct recall target and no source reasoning was lost.
2. Candidate pass: record a candidate when a passage can answer one focused question, has a known source range, and maps to a known topic ID. Compare the complete local candidate set with [priority-calibration.md](priority-calibration.md) before proposing a priority. Done when each candidate has source key, topic ID, source-relative priority with a one-line evidence reason, and a one-line rejection risk.
3. Mark candidates with `#闪卡/优先级/P1#` through `#闪卡/优先级/P4#` only when useful. Preserve the source's knowledge tags in their existing vocabulary; do not force a tag namespace. P2 is not a default for an unexamined candidate. Done when knowledge tags and flashcard priority are visibly separate and the local distribution has been reviewed against the original material.
4. Keep ordinary `==高亮==` as a reading/retrieval cue. Create no `custom-dm-*` card IAL, `custom-riff-decks`, due date, interval, review log, suspend/bury flag, device state, or guessed SiYuan attribute. Done when a scan of the output finds none of these fields.
5. When the source already contains formal card containers or markers, strip them completely: `custom-dm-*` IALs, `custom-riff-*` fields, and `#闪卡/优先级/P1#`-`P4#` tags from already-cardified content are removed so the organized note stays recognizable as prose, not cards. Already-cardified content is not re-marked as a candidate; record it as an ordinary passage or reject it. Done when a scan of the output finds no leftover card container (`O001` catches any that leak).

## Candidate record

Use a short review note or an external working list, not a formal card container:

```text
candidate: civil-subrogation-elements
source: civil-2026-lecture-08#p14
topic: civil-subrogation-elements
priority: P1
reason: three independent statutory elements can be recalled separately
```

Do not split a note merely to manufacture candidates. If the source boundary, topic ID, or legal certainty is unresolved, report the candidate as blocked instead of inventing metadata.
