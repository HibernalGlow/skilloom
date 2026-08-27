# 思源已写入文档的修订

本 reference 只在用户明确授权修改已写入的 SiYuan 文档时读取。

## 数据主权与修改方向

**SiYuan 是闪卡数据的唯一主存储，本地的 `30-闪卡` Markdown 只是导出镜像。** 闪卡数据很重要，不能因为整理或优化而在资源里被删除或覆盖。因此后续任何优化（例如补充 emoji、改优先级、调整结构）都只能按下面的方向进行：

1. **通过思源命令行修改思源中的数据**（唯一入口）。
2. **（可选）把修改好的内容通过导出脚本覆盖到本地文件**——本地文件永远只是思源数据的镜像，只在导出时被覆盖。

**例外**：只有当思源中的目标文档是空的、或只有一些无关记录时，才允许只修改本地的 Markdown 文件（此时没有主数据需要保护，修改后如需进思源再走创建流程，而不是覆盖）。

**红线**：不得从本地文件反向覆盖思源数据——不用整篇 `import md` 覆盖已写入的文档、不用本地编辑结果整体回写删除思源块、不编辑 `.sy`。一切写操作都经 `siyuan` CLI 以块为单位进行。

## 步骤一：CLI 修改思源

1. **定位目标块**：用检索或块读取拿到精确的块 ID，优先精确到段落/listItem，不整篇读根节点。
   ```powershell
   siyuan -w "$SIYUAN_WORKSPACE" search "<关键词>" -f json --type heading --type paragraph --type listItem --page-size 3
   siyuan -w "$SIYUAN_WORKSPACE" block kramdown --id <block-id>
   ```
2. **改正文**：`siyuan block update --id <id> [--data "<markdown>" | --file <path>]`。`block update` 只替换该块内容，不重建它的子孙块；块类型不允许改变时加 `--lock-type`。
3. **结构变化**：新增用 `block append --parent <id>`（子块末尾）、`block prepend --parent <id>`（子块开头）或 `block insert --parent <id> [--previous <sibling-id>]`（指定位置）；删除用 `block delete --id <id>`；移动用 `block move`。新块 ID 由内核分配，不需要手写。
4. **改属性**：`siyuan attr set --id <id> --attr <name>=<value>`，例如 `--attr custom-qb-note-topic-id=civil-elements`。改属性前先 `attr get --id <id>` 复核现值。
5. **逐条复核**：每次写回后用 `block kramdown --id <id>` 核对修改结果；范围较广或批量修改前先 `--dry-run`。

### 身份与风险

- **普通块**：只有基础 `id`、`updated` 和结构信息，无数据库绑定、引用或 DAMO/Riff 属性，可自由改写、删除、重排。
- **特殊块**：带 `custom-*`、`custom-dm-*`、`custom-qb-*`、Riff/复习/数据库/引用相关属性，或是这些块的必要祖先。逐块 `update` / `attr set` 天然保留块 ID 与子孙结构；删除特殊块前必须确认其外部身份不再被引用。
- `custom-dm-card-id` 是可编辑的 DAMO 业务身份，不等同于 SiYuan 块 `id`，默认允许修订；需要冻结的属性不要用 `attr set` 覆盖。

## 步骤二（可选）：导出刷新本地镜像

CLI 修改完成并复核后，若本地 `30-闪卡` 文件需要同步：

1. 用 [`siyuan-export.md`](siyuan-export.md) 的脚本以 portable IAL 导出该文档（如需完整块身份供归档可用 `--ial all`），输出覆盖到本地对应文件。
2. 对导出结果运行适用 validator（Flashcard / MarkNote / GoldQuest）确认修改未破坏门禁。

## 例外：思源文档为空或只有无关记录

仅当思源中的目标文档为空、或其中只有无关记录（例如从未导入的留档壳）时，才允许直接修改本地的 Markdown 文件，此时不需要也不应当试图回写思源；若之后需要把这份内容放进思源，走创建/导入流程（见 [`siyuan-paste.md`](siyuan-paste.md)），而不是覆盖。

## 完成条件

- 每次写回都针对已确认的块；dry-run（如使用）只涉及授权范围；特殊块与约定冻结的属性未被改动；写回后经 `block kramdown` 复核，或导出后通过适用 validator。
- 本地文件只在导出步骤被覆盖；不存在从本地编辑反向覆盖思源数据的情况。