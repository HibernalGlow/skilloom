# Naming and placement

Read this reference only in dedicated-card mode when the user asks for a Markdown file, path, export, or saved deck. Ordinary mode edits the source note and keeps MarkNote's existing file and title contract.

## Resolve the destination

1. Identify the exact source note path and its first meaningful Markdown heading. Treat the source note's basename, numbering, punctuation, and heading wording as authoritative.
2. Search the same subject/teacher or chapter family for existing flashcard directories or files. Prefer an existing sibling directory whose name clearly denotes flashcards, such as `30-闪卡`, `闪卡`, `flashcards`, or the repository's established equivalent. Completion criterion: the destination directory is recorded and contains at least one comparable existing flashcard file, or the search result is recorded as empty.
3. Place a new flashcard file in that dedicated destination directory, never beside the source note inside `20-整理` or another ordinary-note directory. If no dedicated directory exists, create one as a sibling of the source-note directory using the surrounding numbering convention; default to `30-闪卡` only when the source family uses numbered processing stages. Completion criterion: source and destination have different parent directories, and the destination name is traceable to the discovered convention.

## Derive the name and headings

- Start the output filename from the source basename, preserving its number, title, punctuation, and extension semantics. Add one role suffix only when needed to distinguish the artifact: `01-考点23-立法法.md` -> `01-考点23-立法法-闪卡.md`. If the source basename already contains `闪卡`, `flashcard`, or an established equivalent, do not add a second suffix.
- Use the source note's first meaningful heading text as the output's H1, after removing only the Markdown heading marker and an attached IAL, then append the exact role marker ` · 闪卡`. Preserve the source wording, numbering, and punctuation before that marker; do not rename or translate the subject. This keeps the source identity visible while distinguishing the generated artifact.
- Preserve source section headings and numbering in the card file when headings are needed for grouping. A card container's explicit boundary and topic IAL remain authoritative; headings never implicitly define card answers.
- If the source has no meaningful heading, derive both the filename stem and the H1 from the source basename after removing only the extension and one existing flashcard role suffix, then append ` · 闪卡` to the H1. Record `fallback-title` in the delivery report.

## Existing-file and collision rules

- Before writing, search the resolved destination for the source-derived filename and for files with the same `custom-dm-source-key`. Extend an existing deck only when its source key and title mapping match; otherwise create a stable variant filename and report the collision.
- Keep one source family together in its discovered flashcard directory. Do not scatter cards from the same source across the source directory and a flashcard directory.
- A path or title mismatch is a naming rejection, not a reason to silently rewrite the source note. Report `naming-mismatch`, `placement-mismatch`, `title-mismatch`, or `filename-collision` with the observed and expected values.

## Example

Source:

`.../2026-马峰/20-整理/01-考点23-立法法.md`

Destination:

`.../2026-马峰/30-闪卡/01-考点23-立法法-闪卡.md`

First heading in both files:

```markdown
# 考点23 立法法 · 闪卡
```

The source note's original headings may be reused below that H1. The ` · 闪卡` suffix is the only generated title decoration.
