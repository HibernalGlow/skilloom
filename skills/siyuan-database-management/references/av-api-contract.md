# AV API Contract

Schemas and transactions for SiYuan Attribute View columns. Reach from the main skill only when a column or payload uses it.

## Purging detached rows

Remove detached / duplicate rows through the kernel transaction `removeAttrViewBlock`, in kernel and memory. Adding real blocks with `addAttributeViewBlocks` never overwrites a detached placeholder — it appends, which doubles the row count. Purge first, then bind:

```python
sy_req('/api/transactions', {
    'app': 'siyuan-agent',
    'session': 'siyuan-agent',
    'reqId': int(time.time() * 1000),
    'transactions': [{
        'doOperations': [{
            'action': 'removeAttrViewBlock',
            'srcIDs': detached_block_ids,
            'avID': av_id
        }]
    }]
})
```

Only after the purge, bind real blocks so every `blockID` maps to a real document.

## Special columns

### mAsset (resource / asset)

Column definition: `type: "mAsset"`, `icon: "1f468-200d-1f393"` (or `"1f4ce"`). A cell value is an `mAsset` array wrapping `file` objects whose content is the `siyuan://blocks/<id>` protocol — never a raw path:

```json
{
  "id": "<cell_id>",
  "keyID": "<resource_key_id>",
  "blockID": "<row_item_id>",
  "type": "mAsset",
  "mAsset": [
    {"type": "file", "name": "50 保证", "content": "siyuan://blocks/20260422211144-kfxe564"},
    {"type": "file", "name": "44 共同担保", "content": "siyuan://blocks/20260413235017-vh12it2"}
  ]
}
```

**Leaf resolution.** When matching a topic to its resource, do not stop at a parent folder block (`专题`, `第13讲 担保概述`, `讲义`). Recursively traverse to the deepest `.sy` child nodes, parse `Properties.title` and `ID`, and build a semantic keyword dictionary (e.g. map `保证合同` directly to `50 保证` and `44 共同担保`). Verify the physical disk path to settle an ambiguous subject category. Never mount a parent folder as the asset; placeholder fallback is forbidden.

### template

Column definition: `type: "template"`, `icon: "1f9e9"`, `template: "<go template text>"`. Register with `updateAttrViewColTemplate`:

```python
sy_req('/api/transactions', {
    'transactions': [{
        'doOperations': [{
            'action': 'updateAttrViewColTemplate',
            'id': template_col_key_id,
            'avID': av_id,
            'data': template_code_string,
            'type': 'template'
        }]
    }]
})
```

Template arithmetic rules and proven templates live in [the Go template guide](go-template-guide.md).

### relation

A relation cell value:

```json
{
  "type": "relation",
  "relation": {
    "blockIDs": ["<target_block_id_1>", "<target_block_id_2>"],
    "contents": []
  }
}
```

### rollup

Configured in `key.rollup`: the source relation column, the target attribute column, and the aggregation. Operator `Sum` shows the summed value in the kanban row:

```json
{
  "relationKeyID": "<relation_col_key_id>",
  "keyID": "<target_db_col_key_id>",
  "calc": {
    "operator": "Sum",
    "result": null
  },
  "filters": []
}
```

Push it to the kernel by sending the JSON string as `data`:

```json
{"action": "updateAttrViewColRollup", "id": rollup_col_id, "avID": db1_av_id, "data": json_str, "type": "rollup"}
```

## Batching

Always chunk `batchSetAttributeViewBlockAttrs` payloads to **100 rows** so a large table never ships one oversized request:

```python
for i in range(0, len(payload), 100):
    sy_req('/api/av/batchSetAttributeViewBlockAttrs', {
        'avID': av_id,
        'values': payload[i:i+100]
    })
```