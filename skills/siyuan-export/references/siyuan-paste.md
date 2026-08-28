# Paste Markdown into SiYuan

Use this route to create one or many SiYuan documents from UTF-8 Markdown while preserving IAL — for InkLoom this is how an animation's companion note, scene script, or a batch of authored note pages is imported back into SiYuan. SiYuan and the Damophus Agent Bridge module must be running because the bridge opens a real Protyle editor and dispatches a browser paste event. The script does not call the Damophus command-line program and does not upload block content directly.

## Paste

Run from the `siyuan-export` skill directory:

```powershell
python -X utf8 scripts/paste_siyuan_markdown.py note.md `
  --notebook 20260101000000-notebook `
  --directory "/法考/闪卡" `
  --title "善意取得"

python -X utf8 scripts/paste_siyuan_markdown.py one.md two.md `
  --notebook 20260101000000-notebook `
  --directory "/法考/闪卡" `
  --title-map titles.json

python -X utf8 scripts/paste_siyuan_markdown.py D:\exports\markdown `
  --notebook 20260101000000-notebook `
  --directory "/法考/闪卡"

# 直接导入 export_siyuan_markdown.py 生成的目录
python -X utf8 scripts/paste_siyuan_markdown.py `
  "D:\客观\02-背诵卷\民诉\2026-戴鹏\25-kramdown\Note-3.2\法考\客观\民诉" `
  --notebook 20260101000000-notebook `
  --directory "/法考/客观/民诉"
```

A title map is a JSON object. Keys may be paths relative to the map file or unique filenames:

```json
{
  "one.md": "善意取得",
  "chapter/two.md": "无权处分"
}
```

Title priority is explicit `--title` for one file, then `--title-map`, then the first Markdown H1, then the filename stem. A title must be one path segment; `/` and `\` are rejected instead of silently creating an unintended subdirectory. Directory sources are scanned recursively, and duplicate inputs are pasted only once.

For a `25-kramdown\...\法考\客观\民诉` export, pass the final local folder as the source and the already-existing SiYuan folder as `--directory`. The local `Note-3.2` and earlier processing folders are not copied into SiYuan. The script imports every Markdown file below the source folder into that one existing target directory; it does not create or overwrite the parent hierarchy.

The script validates a heartbeat no older than 30 seconds, requires protocol version 1 with `paste` and `create` support, atomically publishes one batch request, prints progress, and waits up to 10 minutes by default. The bridge creates one workspace snapshot before the first document and stops the batch on the first failure. Existing target paths are never overwritten. Use `--dry-run` to inspect the exact request without contacting or writing to SiYuan.

Completion criterion: the final receipt contains one document ID and target path for every source, and SiYuan's exported Kramdown retains the requested IAL.
