# 已有思源闪卡的一次性安全修订

当闪卡已经写入思源并产生复习记录，而用户要求调整优先级、标签、样式、措辞或答案排版时，保留原卡片根块和 `custom-dm-card-id`，使用一次性原位修订：

1. 用 [`siyuan-export.md`](siyuan-export.md) 的脚本以 `--ial all` 导出 `before.md`。
2. 在副本 `after.md` 中完成全部修订；不改变任何块 `id`，不删除或改写稳定 `custom-dm-card-id`。
3. 用 `validate_flashcard.py` 的 dedicated 模式校验 `after.md`。样式修订追加 `--rich-style`；有来源时追加 `--source`；既有文档没有生成报告时不强加 `--require-report`，除非本次同时重做整副卡组报告。
4. 调用 `scripts/siyuan_live_patch.py --before before.md --after after.md` 预览；确认 ID 集合、卡片 ID、属性和根块类型稳定后，追加 `--confirm` 一次写回。
5. 再导出一次 portable Markdown 并复跑同一 validator。

脚本通过原生 `siyuan block update --lock-type` 更新已有块正文，并通过 `siyuan attr set` 更新允许的块级 `style`；不会整篇导入或直接编辑 `.sy`。正文中的 `**锚点**{: style="..."}` 会写入，优先级标签所在正文和其他行内 Markdown 会保留；独立 IAL 的身份属性由原块保留。

优先级调整只替换卡片根块上的一个 `#闪卡/优先级/P1#` 至 `P4` 标签。它不改 `custom-dm-card-id`、Riff 状态、复习记录或调度字段。需要新增/删除/移动卡片根块时停止使用本脚本，改走显式结构迁移并单独验证复习记录影响。

完成条件：写回报告中的变更块均属于用户授权范围；卡片 ID、块 ID 和根块类型前后一致；复导出后 dedicated validator 通过。
