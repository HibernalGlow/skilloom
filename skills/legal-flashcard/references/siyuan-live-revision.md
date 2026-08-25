# 已写入思源文档的一次性自适应修订

本 reference 只在用户明确授权修改已写入的 SiYuan 文档时读取。目标是一次导出、一次本地编辑、一次 CLI 写回、一次复导校验。

## 最短路径

1. 用 [`siyuan-export.md`](siyuan-export.md) 的脚本以 `--ial all` 导出 `before.md`。
2. 复制为 `after.md`，按用户要求自由增删、重排和改写普通内容；保留需要继续存在的特殊块 `id` IAL。
3. 先运行 dry-run；它会列出同 ID 变更，或重建中的普通增删、无 ID 新块行和特殊 ID 保留情况：

```powershell
python -X utf8 skills/legal-flashcard/scripts/siyuan_live_patch.py `
  --workspace "$SIYUAN_WORKSPACE" --before <work>/before.md --after <work>/after.md
```

4. 对最终 portable 导出运行适用的 MarkNote、Flashcard 或 GoldQuest validator，再追加 `--confirm` 执行一次：

```powershell

python -X utf8 skills/legal-flashcard/scripts/siyuan_live_patch.py `
  --workspace "$SIYUAN_WORKSPACE" --before <work>/before.md --after <work>/after.md --confirm
```

5. 重新导出 portable Markdown，复跑同一组 validator。full-IAL 快照供脚本识别块身份，不直接交给只接受 DAMO 语义字段的卡片 validator。

## 风险分层

- **普通块**：只有 SiYuan 基础 `id`、`updated` 和结构信息，且没有外部身份、数据库绑定、引用或 DAMO/Riff 属性。它们可在一次文档重建中新增、删除、重排和改写。
- **特殊块**：有 `custom-*`、`custom-dm-*`、`custom-qb-*`、Riff/复习/数据库/引用相关属性，或是这些块的必要祖先。结构重建必须保留其原 `id`；脚本会在写回前检查。

`custom-dm-card-id` 是可编辑的 DAMO 业务身份，不等同于 SiYuan 块 `id`，默认允许修订。需要冻结时显式传 `--protect-attr custom-dm-card-id`；需要冻结全部 `custom-*` 时传 `--protect-custom-attrs`。复习调度、设备状态和未来运行时字段不由本技能生成或猜测。

完整 IAL 未携带的反链或数据库成员信息可从 `siyuan block get`、`attr get` 或数据库查询中发现；把这些块以重复的 `--special-id <id>` 交给脚本，无需把查询结果放进 Agent 上下文。

## 结构变化边界

`after.md` 中新增块不要手写来自 `before.md` 的 `id`；让 SiYuan 分配新 ID。删除特殊块必须传 `--allow-delete-special <id>`，否则脚本拒绝整篇重建。若只是正文、颜色、标签、优先级或属性变化且 ID 集合不变，脚本按块调用 `block update` 与 `attr set`，不重建文档。

脚本不会编辑 `.sy`、不会整篇 `import md`，也不会把 `custom-dm-card-id`、标签或样式误当作基础身份覆盖。`style` 和行内样式均随正文/属性写回。

完成条件：dry-run 计划只涉及授权范围；特殊块 ID 未被意外删除；新增普通块由 SiYuan 生成 ID；confirm 执行成功；复导后的 Markdown 通过适用 validator。
