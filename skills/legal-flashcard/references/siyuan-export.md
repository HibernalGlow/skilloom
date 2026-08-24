# SiYuan source export

Use this route when the requested flashcard source is one or more `.sy` files, a SiYuan document directory, or an offline SiYuan workspace. The exporter calls the installed `SiYuan-Kernel` in read-only batch mode, so the SiYuan desktop application may remain closed and the source files are not modified.

## Source priority and style authority

Resolve source candidates in this order before drafting a dedicated card:

1. A fresh Markdown snapshot exported from the authoritative `.sy` file or SiYuan workspace.
2. A matching `25-kramdown` export whose path, title, IAL and export provenance are identifiable.
3. Another explicitly named export snapshot.
4. `20-整理` only as a content-navigation aid when no exported source is available. It is never the style authority for a formal deck.

When a requested card file or footer points to `20-整理`, search for the matching source in `25-kramdown`, the SiYuan workspace, or `.sy` files before reading the `20-整理` body as a style source. If an authoritative export exists, run the exporter or use the matching export snapshot and rebuild the provider-scoped style map from that result. Do not silently fall back to the unstyled `20-整理` note merely because it is easier to open.

If an authoritative `.sy`/workspace source is discoverable but export cannot be completed, stop formal card generation with `missing-exported-source` and report the command or path gap. A content-only fallback is allowed only for an explicit ordinary-mode request, never for dedicated-card style inheritance.

Completion criterion: the working source records `fresh-export`, `25-kramdown`, or another named export as its authority class; it is not `20-整理` when an export is available; and the source `.sy` files remain unchanged.

## Export

Run from the `legal-flashcard` skill directory:

```powershell
python -X utf8 scripts/export_siyuan_markdown.py D:\path\to\document.sy --output D:\exports\document.md
python -X utf8 scripts/export_siyuan_markdown.py D:\path\to\one.sy D:\path\to\two.sy --output D:\exports\markdown
python -X utf8 scripts/export_siyuan_markdown.py D:\SiYuan\data\notebook-id --zip D:\exports\notebook-md.zip
python -X utf8 scripts/export_siyuan_markdown.py D:\SiYuan\data\notebook-id --output D:\exports\25-kramdown
python -X utf8 scripts/export_siyuan_markdown.py D:\SiYuan\data\notebook-id --output D:\exports\25-kramdown --flat
```

- File and directory sources must remain under `<workspace>/data/<notebook-id>/...`; pass `--workspace` only when automatic discovery is insufficient.
- Pass `--kernel` or set `SIYUAN_KERNEL_PATH` when the installed kernel is outside the standard Windows locations.
- IAL has three explicit ranges. `portable` is the default: it removes block IDs, timestamps, and database bindings while retaining DAMO fields, table layout, and inline presentation. Use `--ial all` for the complete SiYuan attributes, or `--ial none` only when the user explicitly requests clean Kramdown without attributes. `--include` and `--exclude` accept comma-separated names or `*` patterns; exclusion wins.
- When a directory is selected, its concrete notes are written under `--output` or at the ZIP root while preserving folders and nested documents inside that selected directory. The long path before the selected source directory is not reproduced. Use `--flat` only when a fully flat output is explicitly wanted. Duplicate titles receive a `[document-id]` suffix instead of overwriting another export.
- Existing output is protected. Pass `--force` only after confirming replacement is intended.

Completion criterion: every requested `.sy` source has one `.md` member, the reported count matches the output, and the source `.sy` modification times are unchanged.
