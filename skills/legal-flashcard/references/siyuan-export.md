# SiYuan source export

Use this route when the requested flashcard source is one or more `.sy` files, a SiYuan document directory, or an offline SiYuan workspace. The exporter calls the installed `SiYuan-Kernel` in read-only batch mode, so the SiYuan desktop application may remain closed and the source files are not modified.

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
