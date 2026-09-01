# 缺动画的补做流程（派子智能体）

映射时发现某专题/考点**没有对应动画**（现存动画的 sourceReference 都不覆盖）→ 派子智能体到 InkLoom 补做。制作规范本身看 `inkloom-dev` / `produce-inkloom-animation`，本文件只管"补做的流程与教训"。

## 步骤

1. **缺口清单**：列出"目标文件 ↔ 缺失考点（期望场景数、一图变体的视角建议）"
2. **确认整理基准**（先做！）：用户当前整理哪个目录，动画 sourceReference 就指向哪个目录——指向用户工作文件（20-整理 / 30-闪卡 / 思源对应文档），**不指向** 25-kramdown（导出产物）或 10-mineru（OCR 原稿）
3. **派发**：每个子智能体 1-2 个专题；prompt 指明 inkloom-dev 规范（场景设计、图形语法、图标密度、禁主题衍生词、animation:styles 门禁）+ 一图多变视角 + sourceReference 路径
4. **验收**：manifest 生成且 scenes 非空、门禁 exit 0、AVIF 已发布到 public/animation-avif/<id>/
5. **登记**：加入 `客观/动画嵌入数据/动画源引用.json` 基线，再按 SKILL.md 嵌入流程插入

## 教训（写进每个补做 prompt）

- 商经知 38 个真金题动画被用户删除（2026-08-31）：制作基准搞错——用户在整理背诵卷笔记，工具却按真金题做了。教训 = 步骤 2 不可跳过
- 场景 id 拼写必须与 manifest 逐字一致——历史死链都源于 md 引用与 manifest 不一致（intervener-two-steps、summons-gate-decision）
- 并行会话可能同时在 InkLoom 提交——提交前 git status 核对，冲突时 autostash rebase 收敛
