# Ordinary mode

This mode supplements `legal-marknote`; it does not replace any MarkNote rule. Keep its legal-content, source, title, table, image, color, and structure contract unchanged. Read the existing MarkNote references for those rules instead of copying them here.

Load only this ordinary reference on the ordinary path. Do not load the dedicated-card, protocol, or mnemonic references unless the user explicitly requests formal cards.

## Procedure

1. Atomic pass: split only independently recallable definitions, elements, exceptions, procedures, or legal effects. Keep an inseparable legal argument together. Done when every split has a distinct recall target and no source reasoning was lost.
2. Candidate pass: record a candidate when a passage can answer one focused question, has a known source range, and maps to a known topic ID. Done when each candidate has source key, topic ID, proposed priority, and a one-line rejection risk.
3. Mark candidates with `#闪卡/优先级/P1#` through `#闪卡/优先级/P4#` only when useful. Keep subject tags in `#法考/科目/专题/考点/知识点#`. Done when topic hierarchy and flashcard priority are visibly separate.
4. Keep ordinary `==高亮==` as a reading/retrieval cue. Create no `custom-dm-*` card IAL, `custom-riff-decks`, due date, interval, review log, suspend/bury flag, device state, or guessed SiYuan attribute. Done when a scan of the output finds none of these fields.

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
