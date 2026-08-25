# 已写入思源文档的一次性自适应修订

本 reference 只在用户明确授权修改已写入的 SiYuan 文档时读取。正文整理沿用 `legal-marknote`，写回统一调用 `legal-flashcard/scripts/siyuan_live_patch.py`。

## 流程

1. 使用 `legal-flashcard/scripts/export_siyuan_markdown.py --ial all` 导出一次 `before.md`。
2. 复制为 `after.md`，普通内容可自由改写、增删和重排；需保留的特殊块继续携带原 `id` IAL。
3. 先 dry-run 查看自适应计划，再对最终 portable 导出运行适用 validator，最后 `--confirm` 一次写回。
4. 重新导出 portable Markdown 并复校验；full-IAL 快照只供写回脚本识别块身份。

## 自适应风险模型

只有带外部身份的块需要身份保护：DAMO/Riff/题库/数据库/引用属性，或承载这些块的祖先。普通块可在一次文档重建中自由新增、删除、重排。结构重建前脚本检查特殊块 ID 是否仍在；删除特殊块必须显式 `--allow-delete-special <id>`。

完整 IAL 不包含的反链或数据库成员可由 CLI 查询后通过 `--special-id <id>` 传给脚本；不要把整份查询结果塞进 Agent 上下文。

`custom-dm-card-id` 与其他 `custom-*` 是可编辑业务属性，默认不冻结；需要保护时传 `--protect-attr` 或 `--protect-custom-attrs`。SiYuan 块 `id` 是基础设施身份，由脚本维护。不要编辑 `.sy` 或使用整篇 `import md` 覆盖。

完成条件：一次导出、一次本地修改、一次 CLI 写回和一次复导校验完成；特殊块 ID 与未授权属性未改变；普通区域的增删改已生效。
