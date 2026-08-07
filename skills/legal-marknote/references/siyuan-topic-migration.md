# Existing SiYuan note topic migration

Use this branch for a SiYuan document that has already been edited in place and must keep its blocks, references, backlinks, and manual changes. Do not export and re-import the document.

## Export the review manifest

Identify the exact document block ID first. Then export its heading outline beside the corresponding organized Markdown file:

```powershell
python -X utf8 skills/legal-marknote/scripts/siyuan_topic_manifest.py export `
  --workspace "D:\1STUDY\SIYUAN" `
  --document-id "<document-block-id>" `
  --organized-file "<20-整理\对应文件.md>"
```

The command creates `<name>.topic-map.json` and `<name>.topic-map.md`. The JSON is authoritative; the Markdown file provides a readable outline with `siyuan://blocks/<id>` quick links.

For each atomic topic heading in JSON, set:

```json
{
  "action": "set",
  "topic_id": "civil-property-good-faith-acquisition"
}
```

Leave structural headings as `"action": "skip"`. Use `"action": "delete"` only for an explicitly reviewed obsolete topic declaration.

## Preview and apply

Run the apply command without confirmation first:

```powershell
python -X utf8 skills/legal-marknote/scripts/siyuan_topic_manifest.py apply "<name>.topic-map.json"
```

The preview must account for every planned set/delete operation. It stops when a block changed after export or its live topic attribute differs from the exported value. Resolve the manifest or re-export; use `--allow-stale` or `--on-conflict overwrite` only after inspecting the changed block.

After review, apply and verify every block by ID:

```powershell
python -X utf8 skills/legal-marknote/scripts/siyuan_topic_manifest.py apply "<name>.topic-map.json" --confirm
```

The script writes only `custom-qb-note-topic-id`, compares every unrelated block attribute before and after the write, reads the topic attribute back, and stores an adjacent `.apply-result.json` journal. After a complete run it refreshes the JSON/Markdown mapping with the verified live values, so the files remain the local topic dictionary for later GoldQuest work. A partial failure is journaled and is not reported as complete.
