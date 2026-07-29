---
name: "fakao-mineru-merge"
description: "Merges multi-segment MinerU PDF parse output into a single normalized markdown + images folder for 法考 books. Invoke when processing 法考 PDF books parsed by MinerU into page-range subfolders that need merging, 目录 extraction, and marku pipeline normalization."
---

# 法考 MinerU 多段合并与规范化

本 skill 用于将 MinerU 按页码段切分解析后的多文件夹输出，合并为单一 `full.md` + `images/` + `目录.md` 结构，并通过 marku 管线规范化标题、图片路径、表格等，最终效果参考 `D:\1STUDY\3-Resource\法考\客观\刑法\2026ZH法考专题讲座精讲卷刑法-柏浪涛mineru\full.md`。

## ⚠️ 安全流程（必须严格按顺序，不可跳步）

**用户硬性要求**：处理 MinerU 输出的 markdown 时，必须按以下顺序"先清后建"，否则 MinerU 自带的"menu 标题"会和新处理的标题并存，导致层级污染、专题重复、`title_convert` 失效。

### 步骤 1：先去除目录

从第一个页段的 `full.md` 中，把 `## 目录 Contents` 起到正文起点（如 `# 01 专题一 ...`）之间的目录段抽到独立的 `目录.md`，**不要让它进入正文合并流程**。否则目录里的 `第一节 ...`、`专题一 ...` 会被 `title_convert` 误转成 `## 第一节`、`# 专题一`，污染层级。

### 步骤 2：再去除 menu 中已经识别出来打上的 1 级或 2 级标题

MinerU 解析会给某些行打上 `# `（H1）或 `## `（H2）前缀，但**极不一致**：
- 同一个"专题二"可能是 `## 02 专题二`、`## 专题二`、`# 02 专题二`、甚至 `专题二`（无前缀）
- 可能带数字前缀也可能不带，可能带斜杠 `15/专题十五` 也可能不带
- 有的标题正文是 `专题二十二特别程序`（缺空格），有的是 `专题三 基本原则`（正常）
- 页眉可能出现 `专题二十一 ◎ 审判监督程序`、`专题二十一 ① 审判监督程序` 等带圆圈符号的伪标题

**必须用正则把所有 `^# ` 和 `^## ` 行首前缀剥掉，让所有标题回到纯文本状态**（注意保留 `^### ` 及更深层级，不要误伤）：

```python
def strip_h1_h2(text: str) -> str:
    """剥 H1/H2，保留 H3+。先剥 ## 再剥 #，两者都不会匹配 ### （第三字符是 # 不是空格）。"""
    text = re.sub(r'^## ', '', text, flags=re.MULTILINE)
    text = re.sub(r'^# ', '', text, flags=re.MULTILINE)
    return text
```

### 步骤 3：把原来的标题删除干净，然后再重新处理

剥成纯文本后，用统一规则重新生成 专题 标题（marku 的 `title_convert` **没有 `专题X` 模式**，所以必须在合并脚本里预处理）：

```python
def convert_zhuanti(text: str) -> str:
    """统一 专题X 行为 '# XX 专题X 标题' 格式（XX 为两位阿拉伯数字）。

    覆盖 MinerU 的所有变体：
      '01 专题一 民事诉讼...'   → '# 01 专题一 民事诉讼...'
      '专题二 诉的基本理论'     → '# 02 专题二 诉的基本理论'
      '15/专题十五 调解'        → '# 15 专题十五 调解'        (斜杠分隔)
      '22/专题二十二特别程序'   → '# 22 专题二十二 特别程序'  (斜杠+无空格)
    页眉伪标题（rest 首字符是 ◎ 或 ①②③ 等）跳过不转换。
    """
    def repl(m):
        digits = m.group(1)
        chinese = m.group(2)
        rest = (m.group(3) or '').strip()
        if rest and rest[0] in '◎①②③④⑤⑥⑦⑧⑨⑩':
            return m.group(0)  # 页眉伪标题，原样返回
        if not digits:
            try:
                arabic = cn2an.cn2an(chinese, mode='smart')
                digits = f'{arabic:02d}'
            except Exception:
                digits = '00'
        return f'# {digits} 专题{chinese} {rest}'.rstrip()

    pattern = re.compile(
        r'^(?:(\d+)[/\s]*)?专题([一二三四五六七八九十百千万零两]+)\s*(.*)',
        re.MULTILINE
    )
    return pattern.sub(repl, text)
```

**MinerU 漏识别的兜底**：MinerU 偶尔会把某些 专题 主标题漏掉，只识别了下一级的 `第一节 ...`。需要对照目录.md 检查 专题 数量，对漏掉的 专题 用锚点（第一个 第X节）注入：

```python
# 已知漏识别的 专题（从目录推断）：(中文数字, 阿拉伯数字, 标题, 第一节锚点)
MISSING_ZHUANTI = [
    ("九",  "09", "证明", "第一节 证明对象"),
    ("十",  "10", "证据", "第一节 证据的分类"),
]

def inject_missing_zhuanti(text: str) -> str:
    for chinese, digits, title, anchor in MISSING_ZHUANTI:
        marker = f'# {digits} 专题{chinese} {title}'
        if re.search(rf'^# {digits} 专题{chinese}\b', text, re.MULTILINE):
            continue
        m = re.search(rf'^{re.escape(anchor)}', text, re.MULTILINE)
        if not m:
            continue
        text = text[:m.start()] + marker + "\n\n" + text[m.start():]
    return text
```

### 安全流程总览

```
原 full.md  ──┬── 目录段 ──→ 目录.md（独立保存，不被 marku 处理）
              └── 正文段 ──→ strip_h1_h2 ──→ convert_zhuanti ──→ inject_missing_zhuanti
                                                                       │
                                       合并多段后的 full.md ←──────────┘
                                       │
                                       ↓
                             marku pipeline（title_convert 处理 第X节→H2、一、→H3 等）
```

**核心原则一句话**：先把 MinerU 自己打的所有 H1/H2 标记剥干净，再用统一规则从纯文本重建 专题 H1，最后才让 marku 的 title_convert 处理 第X节/一、/(一)/1. 等更深层级。

## 何时调用

- 用户给出一个 MinerU 解析输出文件夹，里面有多个 `<书名>_<起页>-<止页>.pdf-<uuid>/` 子文件夹
- 用户要求"合并为一个 MD 和一个 image"
- 用户提到"目录清理/移出来"、参考刑法 full.md 的格式、或使用 marku 处理
- 处理对象是法考类 PDF 书籍（民诉/刑法/民法/刑诉/行政法等），结构类似

## 输入约定

源文件夹结构（MinerU 输出）：
```
<源文件夹>/
  <书名>_<起页>-<止页>.pdf-<uuid>/
    full.md                 # 该页段的 markdown
    images/                 # 该页段的图片
    *_content_list.json
    *_model.json
    layout.json
    *_origin.pdf
  ... (多个页段)
```

## 输出约定（参考刑法 mineru 文件夹）

目标文件夹结构：
```
<书名>mineru/
  full.md        # 合并后 + marku 规范化的正文（图片用 file:/// 绝对路径）
  目录.md         # 从正文抽出、未规范化的目录（避免干扰标题处理）
  images/        # 合并所有页段的图片
```

## 关键步骤（必须按顺序）

### 1. 创建目标文件夹

目标文件夹命名规则：在原书名后加 `mineru` 后缀，放在与源文件夹同级目录。
```
源: D:\1STUDY\3-Resource\法考\客观\民诉\2026年ZH法考精讲卷民诉法-戴鹏(1)
目: D:\1STUDY\3-Resource\法考\客观\民诉\2026年ZH法考精讲卷民诉法-戴鹏mineru
```

### 2. 合并 images 文件夹

按页码段顺序，将每个子文件夹的 `images/` 内容复制到目标 `images/`。页段顺序按文件名中的 `<起页>-<止页>` 数字升序排列（1-45, 46-90, 91-135, ...）。同名图片（hash 相同）会被覆盖，这是正常的。

PowerShell 示例：
```powershell
$base = "<源文件夹>"
$target = "<目标文件夹>"
$order = @("1-45","46-90","91-135","136-180","181-225","226-270","271-315","316-360","361-386")
foreach($seg in $order){
  $sub = Get-ChildItem -Path $base -Directory | Where-Object { $_.Name -like "*_$seg.pdf-*" }
  if($sub){
    $imgDir = Join-Path $sub.FullName "images"
    if(Test-Path $imgDir){
      Get-ChildItem $imgDir -File | ForEach-Object { Copy-Item $_.FullName -Destination (Join-Path $target "images") -Force }
    }
  }
}
```

### 3. 合并 full.md（执行"安全流程"：先抽目录 → 剥 H1/H2 → 重建 专题 H1 → 注入漏识别）

**这一步最关键，必须严格按"安全流程"4 步执行**。完整 Python 脚本模板（保存为 `merge.py` 运行）：

```python
from __future__ import annotations
from pathlib import Path
import re
import cn2an  # pip install cn2an

BASE = Path(r"<源文件夹>")
TARGET = Path(r"<目标文件夹>")
SEGMENTS = ["1-45","46-90","91-135","136-180","181-225","226-270","271-315","316-360","361-386"]

# 目录边界正则（按需调整）
TOC_START_RE = re.compile(r"^##\s*目录\s*Contents\s*$", re.MULTILINE)
# 正文起点：# 01 专题一 ... 或 # 01 第一讲 ... （根据实际书名调整）
CONTENT_START_RE = re.compile(r"^#\s*01\s*(?:专题一|第一讲)", re.MULTILINE)

def find_folder(seg):
    for d in BASE.iterdir():
        if d.is_dir() and f"_{seg}.pdf-" in d.name:
            return d
    return None

# === 安全流程步骤 2：剥 H1/H2（保留 H3+） ===
def strip_h1_h2(text):
    text = re.sub(r'^## ', '', text, flags=re.MULTILINE)
    text = re.sub(r'^# ', '', text, flags=re.MULTILINE)
    return text

# === 安全流程步骤 3a：重建 专题 H1（title_convert 无 专题 模式，必须预处理） ===
def convert_zhuanti(text):
    def repl(m):
        digits = m.group(1)
        chinese = m.group(2)
        rest = (m.group(3) or '').strip()
        if rest and rest[0] in '◎①②③④⑤⑥⑦⑧⑨⑩':
            return m.group(0)  # 页眉伪标题，跳过
        if not digits:
            try:
                arabic = cn2an.cn2an(chinese, mode='smart')
                digits = f'{arabic:02d}'
            except Exception:
                digits = '00'
        return f'# {digits} 专题{chinese} {rest}'.rstrip()
    pattern = re.compile(
        r'^(?:(\d+)[/\s]*)?专题([一二三四五六七八九十百千万零两]+)\s*(.*)',
        re.MULTILINE
    )
    return pattern.sub(repl, text)

# === 安全流程步骤 3b：MinerU 漏识别兜底（按需补充） ===
MISSING_ZHUANTI = [
    # (中文数字, 阿拉伯数字, 标题, 第一节锚点)
    # ("九", "09", "证明", "第一节 证明对象"),
]
def inject_missing_zhuanti(text):
    for chinese, digits, title, anchor in MISSING_ZHUANTI:
        marker = f'# {digits} 专题{chinese} {title}'
        if re.search(rf'^# {digits} 专题{chinese}\b', text, re.MULTILINE):
            continue
        m = re.search(rf'^{re.escape(anchor)}', text, re.MULTILINE)
        if not m:
            continue
        text = text[:m.start()] + marker + "\n\n" + text[m.start():]
    return text

def split_toc(text):
    ms = TOC_START_RE.search(text)
    mc = CONTENT_START_RE.search(text)
    if not ms or not mc:
        raise RuntimeError("目录或正文起点未找到，需手动检查边界")
    return text[:ms.start()], text[ms.start():mc.start()], text[mc.start():]

# 读取所有页段（跳过空文件夹）
segments = []
for seg in SEGMENTS:
    folder = find_folder(seg)
    if folder and (folder / "full.md").exists():
        segments.append((folder / "full.md").read_text(encoding="utf-8"))
    else:
        print(f"skip {seg}: empty/missing")

# 第一个文件：拆分出目录
front, toc, content = split_toc(segments[0])

# === 安全流程：strip → convert → inject ===
content = strip_h1_h2(content)
content = convert_zhuanti(content)
content = inject_missing_zhuanti(content)

# 后续页段：同样 strip → convert → inject
parts = [front.rstrip() + "\n\n", content.rstrip()]
for text in segments[1:]:
    stripped = strip_h1_h2(text)
    stripped = convert_zhuanti(stripped)
    stripped = inject_missing_zhuanti(stripped)
    parts.append("\n\n" + stripped.rstrip())

full_md = "\n\n".join(parts[:2]) + "\n".join(parts[2:]) + "\n"
full_md = re.sub(r"\n{3,}", "\n\n", full_md)

# 目录.md：保留原始目录文本（不规范化）
toc_md = toc.replace("## 目录 Contents", "# 目录\n\n# Contents", 1)
toc_md = re.sub(r"\n{3,}", "\n\n", toc_md).rstrip() + "\n"

TARGET.mkdir(parents=True, exist_ok=True)
(TARGET / "full.md").write_text(full_md, encoding="utf-8")
(TARGET / "目录.md").write_text(toc_md, encoding="utf-8")

# 自检：专题 数应与目录一致（缺则需补 MISSING_ZHUANTI）
h1 = len(re.findall(r'^# [^\n]+', full_md, re.MULTILINE))
zt = len(re.findall(r'^# \d+ 专题', full_md, re.MULTILINE))
print(f"H1={h1} 专题={zt}")
```

**自检要点**：
- 跑完脚本后立即 grep `^# \d+ 专题`，专题号必须 01→25（或对应总数）**连续且不重复**
- 如果某个 专题 出现两次（如正文标题 + 页眉伪标题），检查 `convert_zhuanti` 的 `rest[0] in '◎①②③④⑤⑥⑦⑧⑨⑩'` 是否过滤掉了
- 如果某个 专题 缺失（MinerU 漏识别），把 `(中文数字, 阿拉伯数字, 标题, 第一节锚点)` 加入 `MISSING_ZHUANTI` 列表
- 目录起点 `## 目录 Contents` 和正文起点 `# 01 专题一/第一讲 ...` 的正则要按实际书名调整
- 有些页段文件夹可能为空（MinerU 解析失败），脚本会跳过

### 4. 运行 marku 管线

marku 通过 editable install 已加入 sys.path，源码位于 `D:\1VSCODE\Projects\MarkdownAll\MarkdownWrapper\src\marku`。

```powershell
python -m marku pipeline -c "D:\1VSCODE\Projects\MarkdownAll\MarkdownWrapper\src\marku\marku_pipeline.toml" -i "<目标文件夹>" --no-preview
```

**重要**：管线会同时处理目标文件夹下所有 `.md` 文件，包括 `目录.md`。**推荐做法**：跑管线前先删掉 `目录.md`，跑完管线后用步骤 3 的目录抽取逻辑重新生成 `目录.md`（避免被 `title_convert` 污染）。

### 5. 重新生成 目录.md（避免被管线污染）

跑完 marku 管线后，从源第一个页段的 `full.md` 重新抽取目录段，写入目标 `目录.md`：

```python
# 复用步骤 3 的 TOC_START_RE / CONTENT_START_RE / split_toc 逻辑
# 只写 目录.md，不覆盖已被 marku 处理过的 full.md
for d in BASE.iterdir():
    if d.is_dir() and '_1-45.pdf-' in d.name:
        text = (d / 'full.md').read_text(encoding='utf-8')
        break
front, toc, content = split_toc(text)
toc_md = toc.replace('## 目录 Contents', '# 目录\n\n# Contents', 1)
toc_md = re.sub(r'\n{3,}', '\n\n', toc_md).rstrip() + '\n'
(TARGET / '目录.md').write_text(toc_md, encoding='utf-8')
```

### 6. 验证结果

对照参考文件 `D:\1STUDY\3-Resource\法考\客观\刑法\2026ZH法考专题讲座精讲卷刑法-柏浪涛mineru\full.md` 检查：

| 检查项 | 预期 |
|--------|------|
| 图片路径 | `![](file:///D:/.../images/<hash>.jpg)` 格式，中文已 URL 编码 |
| 一级标题 | `# 01 专题一 ...` 或 `# 01 第一讲 ...`，**专题号连续不重复** |
| 二级标题 | `## 第一节 ...`（第X节被 title_convert 规范化） |
| 三级标题 | `### 一、...`（独立的"一、"行被规范化；若原书用 `## 一、` 则保留为二级） |
| 表格 | HTML `<table>` 转为 Markdown 表格（含 `{: colspan rowspan}` 属性） |
| 目录.md | 原始目录文本，未被 title_convert 污染 |
| 连续标题 | consecutive_header 已合并（processing_mode=2 保留最后一个） |
| 残留 images/ | 必须为 0（全部转成 file:///） |

PowerShell 验证命令：
```powershell
python -c "
from pathlib import Path
import re
p = Path(r'<目标文件夹>\full.md')
c = p.read_text(encoding='utf-8')
h1 = len(re.findall(r'^# [^\n]+', c, re.MULTILINE))
h2 = len(re.findall(r'^## [^\n]+', c, re.MULTILINE))
zt = len(re.findall(r'^# \d+ 专题', c, re.MULTILINE))
file_uri = len(re.findall(r'!\[.*?\]\(file:///', c))
old_img = len(re.findall(r'!\[.*?\]\(images/', c))
print(f'H1={h1} H2={h2} 专题={zt} file:/// images={file_uri} leftover images/ refs={old_img}')
"
```

### 7. 清理失效图片链接

用户会**手动删除不需要的图片文件**（如截图、占位图、重复图等），导致 full.md 中残留指向不存在文件的 `file:///` 链接。运行 marku 的 `missing-image` 模块自动清空这些链接：

```powershell
python -m marku pipeline -c "D:\1VSCODE\Projects\MarkdownAll\MarkdownWrapper\src\marku\marku_pipeline.toml" -i "<目标文件夹>" --no-preview --only "missing-image" --include-disabled
```

模块配置（`marku_pipeline.toml` 已包含）：
- `check_file_uri = true`：检查 `file:///` URI 是否指向真实文件
- `check_relative = false`：不检查相对路径（法考 full.md 全部用绝对 `file:///`）

**注意**：
- 该模块默认 `enabled = false`，必须用 `--include-disabled` 才能运行
- 该步骤**会修改 full.md**，将不存在的图片链接替换为空字符串（保留 alt 文本被一并移除）
- 跑完后控制台会打印 `[missing_image_remover] CHANGED (Removed N images) - ...`，N 即清理数量
- 可重复运行：第二次若 N=0，说明已清理干净

### 8. 检查并修复大纲

marku 的 `outline` 模块只读扫描所有标题、构建大纲树、检测三类问题：`level_skip`（父子层级跳跃 > 1）、`sibling_dup`（同级兄弟标题重复）、`deep_nesting`（嵌套深度超过 max_depth=6）。

**步骤 8.1：导出大纲**

```powershell
python -m marku pipeline -c "D:\1VSCODE\Projects\MarkdownAll\MarkdownWrapper\src\marku\marku_pipeline.toml" -i "<目标文件夹>" --no-preview --only "outline" --include-disabled
```

输出 `<目标文件夹>/outline.json`，包含 `tree`、`flat`、`issues` 三个数组。同时控制台会打印每个文件的标题树和问题列表。

> **注意**：若文件夹内同时存在 `目录.md` 和 `full.md`，outline 会按字母顺序处理（`目录.md` 在前），生成的 `outline.json` 可能被后者覆盖。直接解析 `full.md` 或单独检查 `outline.json` 中的 `file` 字段确认来源。

**步骤 8.2：检查 issues**

打开 `outline.json`，按 `kind` 分类查看：
- `level_skip`：父子层级跳跃 > 1（如 H1→H3 缺 H2 中间层）。需判断是否需要补 H2。
- `sibling_dup`：同一父节点下相同文本的兄弟标题重复。**必须修复**。
- `deep_nesting`：嵌套深度超过 `max_depth=6`。需判断是否降级。

**步骤 8.3：修复常见大纲问题**

法考类书籍常见问题与修复脚本（保存为 `fix_outline.py` 运行）：

```python
# 修复脚本：fix_outline.py
from pathlib import Path
import re

p = Path(r"<目标文件夹>\full.md")
text = p.read_text(encoding='utf-8')
lines = text.split('\n')

# ── 修复 1：专题无 第X节 → 提升"知识体系"/"考点精讲"为 H2 ──
# 解决 H1→H3 level_skip（专题直接跟 一、）和 H3 sibling_dup
# （同一"一、xxx"标题在"知识体系"和"考点精讲"两段重复）

zhuanti = []
for i, line in enumerate(lines, 1):
    if re.match(r'^# \d+ 专题', line):
        zhuanti.append({"line": i, "text": line})

jie_lines = {i+1 for i, line in enumerate(lines)
             if re.match(r'^## 第[一二三四五六七八九十]+节', line)}

zt_without_jie = []
for idx, h in enumerate(zhuanti):
    zt_line = h["line"]
    next_zt_line = zhuanti[idx+1]["line"] if idx+1 < len(zhuanti) else len(lines)+1
    has_jie = any(zt_line < jl < next_zt_line for jl in jie_lines)
    if not has_jie:
        zt_without_jie.append(h)

promote_lines = []
for h in zt_without_jie:
    zt_line = h["line"]
    idx = zhuanti.index(h)
    next_zt_line = zhuanti[idx+1]["line"] if idx+1 < len(zhuanti) else len(lines)+1
    for ln in range(zt_line, next_zt_line):
        line = lines[ln-1]
        stripped = line.strip()
        if stripped in ("知识体系", "考点精讲") and not line.startswith("#"):
            promote_lines.append((ln, stripped))

for ln, txt in promote_lines:
    lines[ln-1] = f"## {txt}"
print(f"Promoted {len(promote_lines)} lines to H2")

# ── 修复 2：总结与归纳段落中的 H5 降级为纯文本 ──
# 解决 H5 sibling_dup（同一"N. xxx"标题在正文和"总结与归纳"段落重复）

in_summary = False
demote_count = 0
for i, line in enumerate(lines):
    stripped = line.strip()
    if re.match(r'^总结与归纳\d*$', stripped) and not line.startswith('#'):
        in_summary = True
        continue
    if in_summary and re.match(r'^#{1,4}\s', line):
        in_summary = False
        continue
    if in_summary and re.match(r'^##### \d+\.', line):
        lines[i] = re.sub(r'^##### ', '', line)
        demote_count += 1
print(f"Demoted {demote_count} H5 to plain text in 总结与归纳")

p.write_text('\n'.join(lines), encoding='utf-8')
```

**步骤 8.4：重跑 outline 验证**

修复后再次运行步骤 8.1 的 outline 命令，确认：
- `sibling_dup` 必须为 0（同一父节点下不能有相同标题）
- `level_skip` 允许剩余无伤大雅的跳跃（如 H3→H5 缺 `(一)` 中间层、H2→H5 缺数字列表层），这些是 marku title_convert 模式的固有局限，不影响阅读
- `deep_nesting` 应为 0

**步骤 8.5：清理 outline.json**

大纲验证通过后，删除 `<目标文件夹>/outline.json`（这是 marku 临时输出，不需要保留在最终交付物中）。

```powershell
Remove-Item "<目标文件夹>\outline.json" -Force
```

## marku 管线步骤说明（marku_pipeline.toml）

按 `sequence` 顺序执行，enabled=false 的跳过：

| 步骤 | 模块 | 作用 |
|------|------|------|
| content-replace | content_replace | 标点全角→半角、去多余空行、`[xxx]`→`` `[xxx]` ``、删除"目录"行等 |
| title-convert | title_convert | `第X章`→`#`、`第X节`→`##`、`一、`→`###`、`(一)`→`####`、`1.`→`#####`（**不处理 `专题X`，需在合并脚本预处理**） |
| consecutive_header | consecutive_header | 合并连续同级标题（mode=2 保留最后一个） |
| tables | html2sy_table | HTML `<table>` → Markdown 表格 |
| single-olist | single_orderlist_remover | 移除单条有序列表 |
| image-path | image_path_replacer | `images/xxx.jpg` → `file:///` 绝对路径（中文 URL 编码） |

dedup / t2list / markt 默认关闭；`missing-image` 和 `outline` 默认关闭但**必须按步骤 7、步骤 8 显式启用运行**（`--only <name> --include-disabled`）。

## 常见问题

1. **页段文件夹为空**：MinerU 对某些 PDF 段解析失败会留空文件夹，脚本自动跳过，正文会在该段处截断（无法恢复，需重新解析）。
2. **目录边界找不到**：不同书的目录标题可能是 `## 目录`、`# 目录`、`## Contents` 等，正文起点可能是 `# 01 第一讲`、`# 01 专题一`、`# 第一讲` 等，需手动检查第一个 full.md 确定正则。
3. **图片引用数 < 文件数**：正常现象，部分图片可能未被正文引用，或被多段重复引用。
4. **目录.md 被管线污染**：管线会处理文件夹内所有 .md。解决：跑管线前删 `目录.md`，跑完再从源重新生成。
5. **专题重复**：通常是页眉伪标题（`专题X ◎ 标题`、`专题X ① 标题`）被误转。检查 `convert_zhuanti` 里 `rest[0] in '◎①②③④⑤⑥⑦⑧⑨⑩'` 的过滤是否生效。
6. **专题缺失**：MinerU 偶尔漏识别 专题 主标题（只识别了下一级 第X节）。对照目录.md 检查 专题 数量，把缺失项加入 `MISSING_ZHUANTI`。
7. **`title_convert` 无法处理 专题X**：这是 marku 模块的已知限制（PATTERNS 字典只有 第X章/第X节/一、/(一)/1.），必须在合并脚本里用 `convert_zhuanti` 预处理为 `# XX 专题X 标题` 格式。
8. **大纲 H1→H3 level_skip（专题直接跟 一、）**：说明该专题没有"第X节"中间层。修复：在步骤 8.3 跑 `fix_outline.py` 的"修复 1"，把专题段内的"知识体系"/"考点精讲"纯文本行提升为 `## 知识体系` / `## 考点精讲`，作为 H2 中间层。
9. **大纲 H3 sibling_dup（同一标题在多个段落重复）**：通常是"一、xxx"在"知识体系"和"考点精讲"两段各出现一次，但因没有 H2 父节点分隔被算作兄弟重复。修复：同问题 8，提升"知识体系"/"考点精讲"为 H2 后，这些 H3 自然分属不同父节点。
10. **大纲 H5 sibling_dup（"总结与归纳"段落重复）**：说明"总结与归纳N"段落里混入了 `##### N. xxx` H5，与正文里的同名 H5 重复。修复：在步骤 8.3 跑 `fix_outline.py` 的"修复 2"，把段落内的 `##### N. xxx` 降级为纯文本 `N. xxx`。
11. **大纲剩余 #3→#5 / #2→#5 level_skip**：属于 marku title_convert 的固有局限（`一、`→H3、`1.`→H5 之间漏了 `(一)`→H4 中间层；`第X节`→H2、`1.`→H5 之间漏了 `一、`/`(一)`）。**这些跳跃无伤大雅，不影响阅读，可保留**。
12. **outline.json 内容是 目录.md 的而非 full.md 的**：outline 模块按字母顺序处理文件夹内所有 .md，`目录.md` 排在 `full.md` 前面会被先处理。直接解析 full.md 验证，或删除 `目录.md` 后重跑。

## 参考路径

- marku 源码：`D:\1VSCODE\Projects\MarkdownAll\MarkdownWrapper\src\marku\`（已通过 editable install 加入 sys.path）
- marku 配置：`D:\1VSCODE\Projects\MarkdownAll\MarkdownWrapper\src\marku\marku_pipeline.toml`
- 参考成品：`D:\1STUDY\3-Resource\法考\客观\刑法\2026ZH法考专题讲座精讲卷刑法-柏浪涛mineru\full.md`
- 法考根目录：`D:\1STUDY\3-Resource\法考\`
