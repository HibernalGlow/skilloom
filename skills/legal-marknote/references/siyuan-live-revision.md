# 思源已写入文档的修订

本 reference 只在用户明确授权修改已写入的 SiYuan 文档时读取。正文整理沿用 `legal-marknote`。

## 数据主权与修改方向

**SiYuan 是笔记数据的唯一主存储，本地的 Markdown 只是导出镜像。** 笔记数据很重要，不能因为整理或优化而在资源里被删除或覆盖。任何修改都只能按下面的方向进行：

1. **通过思源命令行修改思源中的数据**（唯一入口）。
2. **（可选）把修改好的内容通过导出脚本覆盖到本地文件**——本地文件只是镜像，只在导出时被覆盖。

**例外**：只有当思源中的目标文档是空的、或只有一些无关记录时，才允许只修改本地的 Markdown 文件；之后如需进思源再走创建流程，而不是覆盖。

**红线**：不得从本地文件反向覆盖思源数据——不用整篇 `import md` 覆盖、不用本地编辑结果整体回写删除思源块、不编辑 `.sy`。一切写操作都经 `siyuan` CLI 以块为单位进行。

## 步骤一：CLI 修改思源

1. **定位目标块**：用检索或块读取拿到精确的块 ID，优先精确到段落/listItem：
   ```powershell
   siyuan -w "$SIYUAN_WORKSPACE" search "<关键词>" -f json --type heading --type paragraph --type listItem --page-size 3
   siyuan -w "$SIYUAN_WORKSPACE" block kramdown --id <block-id>
   ```
2. **改正文**：`siyuan block update --id <id> [--data "<markdown>" | --file <path>]`。`block update` 只替换该块内容，不重建它的子孙块；块类型不允许改变时加 `--lock-type`。
3. **结构变化**：新增用 `block append --parent <id>` / `block prepend --parent <id>` / `block insert --parent <id> [--previous <sibling-id>]`；删除用 `block delete --id <id>`；移动用 `block move`。新块 ID 由内核分配，不需要手写。
4. **改属性**：`siyuan attr set --id <id> --attr <name>=<value>`，例如 `--attr custom-qb-note-topic-id=civil-elements`。改属性前先 `attr get --id <id>` 复核现值。
5. **逐条复核**：每次写回后用 `block kramdown --id <id>` 核对；需要交付校验时导出 portable Markdown 跑适用 validator。范围较广或批量修改前先 `--dry-run`。

### 身份与风险

- **普通块**：只有基础 `id`、`updated` 和结构信息，无数据库绑定、引用或 DAMO/Riff 属性，可自由改写、删除、重排。
- **特殊块**：带 DAMO/Riff/题库/数据库/引用相关属性，或是这些块的祖先。逐块 `update` / `attr set` 天然保留块 ID 与子孙结构；删除特殊块前必须确认其外部身份不再被引用。
- `custom-dm-card-id` 与其他 `custom-*` 是可编辑业务属性，默认不冻结；需要冻结的属性不要用 `attr set` 覆盖。SiYuan 块 `id` 是基础设施身份，由内核维护。

## 步骤二（可选）：导出刷新本地镜像

CLI 修改完成并复核后，若本地文件需要同步：用 `legal-flashcard/scripts/export_siyuan_markdown.py` 以 portable IAL 导出该文档，输出覆盖到本地对应文件；`--ial all` 仅用于需要完整块身份的归档快照。导出后对结果运行适用 validator（MarkNote / Flashcard / GoldQuest）。

## 写回完整性红线（2026-08-30 批量事故沉淀）

批量修订（含 `siyuan_live_patch.py` 重建路径）完成后，必须复导出并用 SQL 自检以下五类，发现即修，全部清零才允许交付快照：

0. **内核必须在线（最高优先）**：所有 `siyuan` CLI 命令都要求桌面端 SiYuan 正在运行同一 workspace。应用未运行时 CLI 会以 headless 模式启动内核，其启动逻辑会 drop/重建 blocks 索引表——曾把整个工作区索引清空（`temp/siyuan.db` 变 4KB 空库，`blocktree.go: drop table [blocks]`）。每次批量操作前先探测：`SELECT count(*) FROM blocks` 应返回与工作区规模相符的量级（数十万级）；返回 0 视为内核离线/索引被清，**立即停止一切读写**，等用户重开应用让内核自动重建索引。禁止在应用关闭期间用 CLI「试试看」。

1. **活块不可围栏**：`{{select ...}}` 嵌入块（query_embed）是活块，绝不能为规避 E621/E622 而包 ` ```md ` 围栏——围栏会把嵌入变成字面代码文本，嵌入彻底失效。E621/E622 命中嵌入/查询行与 E304 同属可接受残留，在 STATUS 里记录即可。发现已被围栏的嵌入块：拆除围栏与 callout 外壳，把 `{{...}}` 作为独立块的 markdown 写回，内核会重建 query_embed 类型。
2. **块引用语法必须闭合规范**：复导出正文里出现字面 `((2026… "锚文本"))` 即为泄漏（正常解析后 DB content 只含锚文本）。常见根因是 `))` 前多一个空格（`"锚文本" ))`）——删掉空格修成 `((id "锚文本"))` 即可恢复解析；若目标块已不存在，按锚文本检索存活块的新 ID 重指，不得留死链。
3. **空块清零**：写回后查 `SELECT id FROM blocks WHERE root_id='<root>' AND type='p' AND content=''`；rebuild 路径极易产生空段落。复导出中它们的形态是「IAL 叠行且缩进不小于上一 IAL 行」，逐个删除。
4. **IAL/样式泄漏清零**：SQL `content LIKE '%{: id=%'` / `content LIKE '%{: style=%'`（排除代码块与围栏内内容；list/callout 容器的 content 是子块聚合，判定以子块为准）。p/h 块 content 含 IAL 即为泄漏：把 `{: id=…}` 从正文文本剥除；`{: style=…}` 若附着在术语上改写为 `**术语**{: style=…}`，否则剥除。
5. **删除块前查引用**：rebuild 会删除 after 缺席的块，被删除块的 ID 若被其他文档的块引用或嵌入指向，会立刻变成死链。删除前查 `refs` 表确认无外部引用；被引用的块即使为空也保留，或先把引用重指到新块。

同时提醒（属于 `legal-marknote` 正文契约，批量路线同样适用）：遗留 `###### 习题` / `###### 试一试` 标题必须替换为 `> [!QUESTION] ✏️ <具体考点标题>` callout，`> 回答：` 一律写为 `**回答与解析：**`；不得以「过门禁」为由保留旧壳。

## 例外：思源文档为空或只有无关记录

仅当思源中的目标文档为空、或其中只有无关记录时，才允许直接修改本地的 Markdown 文件，此时不需要也不应当回写思源；之后若需进思源再走创建/导入流程。

完成条件：CLI 路径每次写回都针对已确认的块，特殊块 ID 与未授权属性未改变，写回后经 `block kramdown` 复核或导出校验；本地文件只在导出步骤被覆盖，不存在从本地编辑反向覆盖思源数据的情况。