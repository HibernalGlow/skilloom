---
name: siyuan-export
description: 思源笔记的文档级导出与导入：把 .sy 文档/文档目录/工作区导出为 Markdown（只读、可配置 IAL），并把 UTF-8 Markdown 导入回思源文档（真实 Protyle 粘贴、保留 IAL）。触发于任何"导出思源笔记"或"把 Markdown 导入思源"的任务；是 legal-flashcard、legal-marknote、inkloom-dev 等技能共用脚本的权威来源。
---

# SiYuan export and import

文档级的思源笔记搬运都走本技能，不要再在其它技能里逐份拷贝脚本。单块的读写（block get/kramdown/children/insert）不走这里，用 `$siyuan-cli`。

## Export route

把思源笔记导出为 Markdown：`.sy` 文件、文档目录或离线工作区 → `.md`（调用已安装的 `SiYuan-Kernel` 只读批量模式，桌面端可以不开，源文件不被修改）。

- 读 [references/siyuan-export.md](references/siyuan-export.md) 再执行。
- 命令（从 `siyuan-export` 技能目录）：
  ```powershell
  python -X utf8 scripts/export_siyuan_markdown.py D:\path\to\document.sy --output D:\exports\document.md
  python -X utf8 scripts/export_siyuan_markdown.py D:\SiYuan\data\notebook-id --output D:\exports\kramdown
  python -X utf8 scripts/export_siyuan_markdown.py D:\SiYuan\data\notebook-id --zip D:\exports\notebook-md.zip
  ```
- IAL 三档：`portable`（默认，去块 ID/时间戳/库绑定，保留 DAMO 字段与行内样式）、`all`（完整属性）、`none`（干净 Kramdown，仅当用户明确要求）；`--include`/`--exclude` 支持逗号名或 `*` 模式，排除优先。
- 完成标准：每个 `.sy` 源有一个 `.md` 输出、数量对得上、源 `.sy` 修改时间不变。

## Import route

把 Markdown 导入回思源：UTF-8 Markdown → 一个或多个思源文档，保留 IAL。需要思源与 Damophus Agent Bridge 在运行（真实 Protyle 粘贴事件，不走 Damophus 命令行、不直接上传块内容）。

- 读 [references/siyuan-paste.md](references/siyuan-paste.md) 再执行。
- 命令（从 `siyuan-export` 技能目录）：
  ```powershell
  python -X utf8 scripts/paste_siyuan_markdown.py note.md --notebook 20260101000000-notebook --directory "/法考/闪卡" --title "标题"
  python -X utf8 scripts/paste_siyuan_markdown.py D:\exports\markdown --notebook 20260101000000-notebook --directory "/法考/客观/民诉"
  ```
- 标题优先级：`--title`（单文件）→ `--title-map` → 首个 Markdown H1 → 文件名。已有目标路径绝不覆盖；`--dry-run` 只打印请求。
- 完成标准：收据里每个源对应一个文档 ID 与目标路径，思源导出的 Kramdown 保留请求的 IAL。

## Canonical copy discipline

本技能是导出/导入脚本的**权威副本**。`legal-flashcard/scripts/` 下的同名脚本（`export_siyuan_markdown.py`、`paste_siyuan_markdown.py` 及其测试）必须与本目录逐字节一致：改动后 `cp` 过去并 `diff` 验证。其它技能只按名加载 `$siyuan-export`，不再各自维护副本。

验证：`python -X utf8 scripts/test_export_siyuan_markdown.py` 与 `python -X utf8 scripts/test_paste_siyuan_markdown.py`。
