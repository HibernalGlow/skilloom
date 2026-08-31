---
name: inkloom-embed
description: 把已发布的 InkLoom 动画（AVIF）嵌入思源笔记、真金题、闪卡的方法论——落点铁律、逐知识点锚定、真金题首次出现原则、一图多变、缺动画派子智能体补做、思源 API 通道与陷阱
---

# InkLoom 动画嵌入

把 `InkLoom/public/animation-avif/<动画id>/<场景id>.avif`（jsDelivr 已发布）插入到用户的法考笔记体系中。**本技能管"嵌入"，制作动画用 `inkloom-dev` / `produce-inkloom-animation`。**

## 何 时 用

- 用户要求"把动画插入笔记/真金题/闪卡"
- 每小时追新循环：扫描 `InkLoom/src/animations/**/animation.meta.ts`（有 sourceReference）且 manifest scenes 非空的动画，与基线（`客观/动画嵌入数据/动画源引用.json`）比对找新增
- 用户报告"某文件看不到动画"→ 先做覆盖审计（见 references/audit.md）

## 落点铁律（用户 2026-08-31 明确）

1. **思源有对应笔记**（getChildBlocks 实测有实质内容）→ 只插思源，**不插 md**
2. **思源无笔记/占位壳** → 插**对应的 20-整理 md**（真金题/背诵卷的 20-整理是用户工作文件）
3. **25-kramdown 永远禁止插入**——它是思源导出产物，重新导出会覆盖
4. 占位壳判定必须用 `getChildBlocks` 二次核实；**CLI 的 SQL 计数可能陈旧产生假壳**（实测第6讲 12/13 被误判 7/3 块，实际 200/40+ 块）

## 插入图片行格式

```
![InkLoom 动图：<manifest 场景 title>](https://gcore.jsdelivr.net/gh/inkloomer/inkloom@main/public/animation-avif/<动画id>/<场景id>.avif)
```

- URL 必须逐字对照 manifest（场景 id 错拼 = 404 死链；历史错拼例：intervener-two-steps、summons-gate-decision）
- md 里插入用 Edit 工具逐个插入（用户规则：禁脚本批量改内容；纯死链清理等删除性批量操作可用脚本）

## 嵌入原则（详见 references/）

| 场景 | 原则 | 参考 |
|---|---|---|
| 讲义思源/md | 逐知识点锚定：插到解释该知识点的标题/列表项后，同锚 ≤2 张，溢出上移节标题 | anchor-rules.md |
| 真金题 md | **首次出现原则** + 考点必背小节锚 + 题目解析中的首现插入 | quiz-embed.md |
| 真金题思源 | 题号N末块锚（下一题标题前块）、考点必背小节锚；讲次错位表见台账 | quiz-embed.md |
| 闪卡 md | 按知识点插入（卡片 IAL `custom-dm-card-id` 锚或节前动画带） | flashcard-embed.md |
| 缺动画 | 现存动画没覆盖的知识点 → 派子智能体按 inkloom-dev 规范补做（含一图多变） | missing-animations.md |

## 通道选择（思源）

- GUI 开着（tasklist 有 SiYuan.exe）→ **HTTP API** `http://127.0.0.1:6806`，token 在 `D:\1STUDY\SIYUAN\conf\conf.json`；insertBlock 用 previousID、getChildBlocks 读结构
- GUI 关闭 → CLI（`siyuan -w %SIYUAN_WORKSPACE%`）可用，但 **SQL 判壳不可信**，children 走 CLI、判壳重开 HTTP 或直接看文件
- 报 tree not found / children 空 → GUI/CLI 双内核冲突，改 HTTP API 重试

## 已知陷阱速查

1. 思源 SQL `blocks.markdown` 列**截断长块**——URL 后半段（动画 id）like 不到，全库审计用宽 like + Python 解析或 children 实测
2. insertBlock 返回 code 0 但块没出现 = previousID 为 None（锚 id 拼错）——插后必须 getChildBlocks 复测
3. SQL 索引对新插块滞后——验证用 getChildBlocks
4. 标题可能带 riff 标记词（如"3. 顺序监护 亲疏"）——SQL 精确匹配失败时 like 兜底
5. 中文数字专题号（专题十五）+ 文件名序号（15）双轨——映射按**标题关键词**而非序号
6. 同名场景 id 存在于多个动画（如 retrial）——拼 URL 时动画 id 必须与场景同源 manifest 核对
