# 已写入思源文档的一次性原位修订

本 reference 只在用户明确要求修改已经写入思源的文档时读取。目标是一次完成“导出、校验、本地修改、安全写回、复校验”，而不是反复搬运整篇笔记。

## 推荐路径

使用 `legal-flashcard` 的导出脚本生成可编辑快照，再调用共享的安全写回脚本：

```powershell
python -X utf8 skills/legal-flashcard/scripts/export_siyuan_markdown.py `
  <document.sy-or-document-dir> --output <work>/before.md --ial all

# 在 before.md 的副本 after.md 中完成 MarkNote 修订，保留每个 IAL 的 id 属性

python -X utf8 skills/legal-flashcard/scripts/siyuan_live_patch.py `
  --workspace "$SIYUAN_WORKSPACE" --before <work>/before.md --after <work>/after.md --confirm

python -X utf8 skills/legal-flashcard/scripts/export_siyuan_markdown.py `
  <document.sy-or-document-dir> --output <work>/after-portable.md --ial portable
```

`siyuan_live_patch.py` 是薄封装：差异计算、ID 映射和安全检查由脚本完成，实际写入仍调用官方 `siyuan block update --id ... --lock-type` 和 `siyuan attr set`。它只更新已有块的正文、行内样式和明确允许的块级 `style`，不重建块树；现有卡片 IAL、父子关系和反链由 SiYuan 保持。

## 安全边界

- `before.md` 与 `after.md` 的块 ID 集合必须完全相同；新增、删除、移动块或改变层级时拒绝执行，改走显式 CLI 操作。
- 每个变化块必须仍保留原来的 `id` IAL。脚本只把新正文传给目标块，不把 `custom-dm-*`、`custom-qb-*` 或时间属性当成新属性覆盖。
- `**粗体**{: style="..."}` 等行内样式属于正文，会随块正文写回；独立行 IAL 与其余属性不拼进替换正文。
- 不直接编辑 `.sy`，不使用整篇 `import md` 覆盖原文档。写入前创建一次 `siyuan repo create --memo "legal-marknote live patch"`；脚本默认 dry-run，只有显式 `--confirm` 才写入。

## 校验路由

在 `before.md` 与最终 `after-portable.md` 上运行适用门禁：

- 普通 MarkNote 文档：MarkNote validator `--strict --require-topic-ial`，并运行 Flashcard validator `--mode ordinary`；
- 已含 `custom-dm-card-id` 的文档：Flashcard validator 改用 `--mode dedicated`，按来源追加 `--source`、`--rich-style`、`--require-report`；
- 题库内容：追加 GoldQuest validator；
- 只处理用户授权的错误和警告，不为通过门禁删除既有闪卡字段。

完成条件：脚本报告每个变更块的 ID 和结果；最终便携导出通过适用 validator；至少一个含行内样式和一个含独立 IAL 的测试样例确认样式保留；未授权块的 ID、IAL、父子关系和卡片根边界没有变化。
