# 缺动画的补做流程（子智能体）

真金题/闪卡映射时发现某专题/考点**没有对应动画**（现存动画的 sourceReference 都不覆盖），派子智能体到 InkLoom 补做。

## 流程

1. **生成缺口清单**：映射分配后，列出"目标文件 ↔ 缺失考点（含期望场景数与视角建议）"
2. **派发**：每个子智能体负责 1-2 个专题的动画制作，prompt 指明：
   - 参照 `inkloom-dev` 技能的规范（场景设计、图形语法、图标密度、禁主题衍生词、animation:styles 门禁）
   - sourceReference 写**用户工作文件**的路径（真金题→20-整理 md；闪卡→30-闪卡 md；笔记→20-整理/思源对应文档）——**不要**指向 25-kramdown（导出产物）或 10-mineru（OCR 原稿）
   - 遵循一图多变：同一考点若有多个难度层次，出 2-3 个视角变体（标准/标注/极端）
3. **验收**：manifest 生成且 scenes 非空、animation:styles 门禁 exit 0、AVIF 已发布（public/animation-avif/<id>/）
4. **登记**：加入 `客观/动画嵌入数据/动画源引用.json` 基线，再按本技能的嵌入流程插入

## 历史教训（务必写进 prompt）

- 商经知 38 个真金题动画被用户删除（2026-08-31）：制作基准搞错（用户在整理背诵卷笔记，工具却按真金题做了）。补做前**确认用户的整理基准**：用户当前整理哪个目录，动画 sourceReference 就指向哪个目录
- 场景 id 命名后必须在 manifest 核对拼写——历史上出现 md 引用与 manifest 不一致的死链（intervener-two-steps vs intervener-two-step、summons-gate-decision vs summons-gate-checkline）
- 并行会话可能同时在 InkLoom 提交——registry/场景文件冲突时 autostash rebase 收敛，提交前 git status 核对
