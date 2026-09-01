---
name: inkloom-embed
description: 把已发布的 InkLoom 动画（AVIF）嵌入法考笔记、真金题、闪卡。用于：插入动画到思源或 md；每小时追新插入循环；审计某科目/文件为何看不到动画；清理死链。制作新动画用 inkloom-dev 或 produce-inkloom-animation。
---

# InkLoom 动画嵌入

一条嵌入任务的执行序列。事实源：动画 = `InkLoom/public/animation-avif/<动画id>/manifest.json`（场景 id/ title 以它为准，URL 逐字对照，拼错即 404）；基线 = `客观/动画嵌入数据/动画源引用.json`；进度 = `客观/动画嵌入台账.md` 四A段。

## 1. 找目标（三个入口）

- **追新增**：扫描 `InkLoom/src/animations/**/animation.meta.ts`（有 sourceReference）且 manifest scenes 非空，与基线比对；新动画按其 sourceReference 落位
- **按科目补齐**：某科目的真金题/闪卡没有动画 → 现存动画按 sourceReference 的**专题标题关键词**映射到文件（序号会错位：民诉真金题23督促↔讲义22、刑法动画N↔真金题N-1）；生成分配清单 JSON（客观/动画嵌入数据/_*.json，已 gitignore）。清单按**专题**组织三线（讲义思源/闪卡/真金题），见第 3 节三位一体
- **用户点名**：直接审计该文件的动画覆盖（references/audit 配方在 quiz-flashcard-embed.md 第三节）

## 2. 判定落点（落点铁律，每条分支必经）

思源文档判定**只用 getChildBlocks 实测**（CLI 的 SQL 计数可能陈旧出假壳——实测 200 块文档报 7 块）：

- 思源有对应笔记（实质内容）→ 只插思源，md 不动
- 占位壳 / 无思源文档 → 插**对应的 20-整理 md**（用户工作文件）
- 25-kramdown 与 10-mineru 是导出/OCR 产物：**不作为落点**，发现误插即清理

图片行格式（唯一合法形态）：

```
![InkLoom 动图：<manifest 场景 title>](https://gcore.jsdelivr.net/gh/inkloomer/inkloom@main/public/animation-avif/<动画id>/<场景id>.avif)
```

## 3. 插入（三位一体：按专题同时插三线）

用户 2026-08-31 明确：处理一个专题的动画时，**讲义（思源）、闪卡、真金题三条线同时插入**——不要按"线"批量推进（先做完一个科目的真金题再做闪卡），要按"专题"打包，用户复习某专题时三个载体立即全部有动画。每条线各自走落点铁律：思源有内容→思源；壳/无→本地 md。生成分配清单时按专题输出三线任务（讲义思源锚 / 闪卡文件与卡片锚 / 真金题文件与小节锚），派子智能体时每个子智能体拿若干专题的**全套三线任务**。

### 按文件类型的锚定分支

- **讲义/笔记（思源或 md）** → 逐知识点锚定：references/anchor-and-siyuan-api.md
- **真金题** → 考点必背小节锚 + 题目解析首现插入；**防剧透铁律：题目的动图只能插在解析里（###### 答案与解析 之后），绝对不能出现在题干前**（题号后、解析前=剧透；考点标题后=第一题题干前，同样违规）：references/quiz-flashcard-embed.md
- **闪卡** → 按知识点锚卡片：references/quiz-flashcard-embed.md 第二节
- **该知识点没有动画** → 派子智能体补做：references/missing-animations.md（先确认用户的整理基准再定 sourceReference）

插入通道：思源 GUI 开着用 HTTP API（127.0.0.1:6806，token 在 D:\1STUDY\SIYUAN\conf\conf.json）；关着用 CLI。md 一律 Edit 工具逐个插入。通道细节与陷阱实录见 references/anchor-and-siyuan-api.md。

## 4. 验收（完成判据——全部满足才算完成）

- 计数：每文件 `animation-avif` 计数 == 分配场景数；跨文件场景零重复
- 死链：本次插入的每个 URL 的 (动画id, 场景id) 在 manifest 中存在
- 内容：git diff 为纯插入（0 行删除 0 行修改），原有内容未动
- 思源插入：getChildBlocks 复测图在位（SQL 索引滞后不可作验证）
- 防剧透：真金题中每个图行都位于某题"###### 答案与解析"之后（扫描器跟踪 stem 区图行 + 图块贴题号检查，配方在 quiz-flashcard-embed.md）；子智能体插入任务必须先跑此扫描，违规=0 才算完成

## 5. 收尾

- 更新基线 json（新动画登记）、台账四A段（插了什么/剩什么/教训）
- git add **限定路径** 提交（并行会话在同仓工作，宽 add 会扫入他人文件）

## 大规模批次的执行方式

单文件手工插入；超过 ~50 场景的批次生成分配清单后派**子智能体**并行（每组 6-10 文件，prompt 含：清单路径、文件基目录、锚定规则、格式、验收要求、禁脚本改文件），主线程按第 4 节验收——子智能体报告不作数，计数与 diff 为准。已知子智能体失误模式：场景 id 拼错动画 id（同名场景 retrial 跨动画）、漏插、堆叠重复、**把图插在题干前**（2026-08-31 刑诉批次 64 处返工）——所以验收第 4 节的防剧透扫描必跑。
