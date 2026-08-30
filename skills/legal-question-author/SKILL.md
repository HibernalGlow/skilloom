---
name: legal-question-author
description: >
  根据 Damophus 题库的错题、收藏和题目资料，批量生成可直接导入题库的法考客观题或主观题成文稿；
  适用于需要一次出卷、生成变式题或按个人薄弱考点定制题目的请求，不用于逐题对话训练。
---

# Legal Question Author

把 Damophus 的学习痕迹转成一组**可以独立保存、复核和再次导入的法考题目**。输出是 Markdown 题库源文件，不是聊天问答、HTML 测验或作答记录。

## 边界

- 本技能负责批量成文：题干、选项、答案、完整解析、考点引用和稳定 ID。
- 现有 `bar-prep-questions` 负责一题一题的互动训练；不要把本技能改成逐题等待用户回答的流程。
- 错题、Again/Hard 评分、收藏和标签只影响选题权重与变式方向，不能写入题目 IAL，也不能替代题库原有的 `reviewThreshold` 或作答统计语义。
- 没有足够的权威法条、教材或原题解析时，不要凭空补规则；列出需要补充的资料并暂停对应题目。

## 何时读取参考文件

1. 先读取 [`references/input-contract.md`](references/input-contract.md)，确认用户给出的导出文件能否映射到题目、考点、错题和收藏。
2. 生成或检查题目格式前，读取 [`../legal-question-bank/references/question-contract.md`](../legal-question-bank/references/question-contract.md)。它规定 `custom-qb-*`、答案边界和题目考点引用。
3. 生成解析前，读取 [`../legal-goldquest/references/format-playbook.md`](../legal-goldquest/references/format-playbook.md) 和 [`../legal-goldquest/references/color-system.md`](../legal-goldquest/references/color-system.md)，保持 GoldQuest 的语义排版、颜色和复杂度路由。
4. 需要完整的题目前置考点导航时，再读取 [`../legal-goldquest/references/topic-summary.md`](../legal-goldquest/references/topic-summary.md)；普通批量出题不要强行添加导航。

这些是同一 Skilloom 仓库中的参考资料，不是需要用户另外安装的运行依赖。路径不存在时，保留本技能的最小题库契约，并报告缺失的本地参考。

## 工作流

### 1. 确认出卷参数

在开始生成前，确认或从用户输入中提取：

- 阶段：客观题、主观题或混合；客观题区分单选、多选、判断，主观题区分案例分析、法律文书、论述。
- 科目和数量；未指定科目时按导出数据的薄弱科目排序，不擅自覆盖用户的科目范围。
- 目标考点粒度；优先使用题库中已存在的叶子考点。
- 难度、是否允许复用原题事实、是否需要题目前置考点总结。

如果用户没有提供任何题目资料，只能生成“待补资料的出题框架”，不能交付看似完整的法律题。

### 2. 建立个性化权重

把每道已有题映射为 `question_id -> topic_ids -> subject`，再合并学习记录：

- `Again`、明确答错和重复答错：最高权重，优先生成同一叶考点的变式题，并改变事实结构或设问角度。
- `Hard`、用时明显偏长或主观题评分偏低：次高权重，生成相邻概念辨析题或减少提示的迁移题。
- 收藏题：作为用户主动关注信号；在保持收藏主题的同时生成边界、例外和反向事实题，不把收藏本身当成“不会”。
- 已连续答对或 `Good/Easy`：降低重复率，可用于跨考点综合题或间隔复习题。
- 统计不足时，不伪造精确百分比；只报告样本量和定性排序。

保留原有 `reviewThreshold` 的含义。它是筛选/展示阈值，不得被新技能改写成生成权重；生成权重只作为本次出卷的临时决策。

### 3. 选择题目蓝图

先输出内部蓝图，再写 Markdown。每道题蓝图至少包含：

- `source_question_id`（若是变式题）或 `topic_id`（若是弱点驱动的新题）；
- 目标叶考点、科目、题型、难度和要测的错误模式；
- 适用法源和截止日期；
- 题目要测试的唯一核心判断；
- 正确答案理由、每个干扰项的独立错误理由或主观题评分点。

同一批题要控制覆盖面：不要把所有题都变成原题的同义改写；至少加入事实变体、选项陷阱变体和相邻考点迁移中的适当组合，并记录每题的来源关系。

### 4. 生成成文题

题面和解析严格分区。客观题题面只放事实、问题和未标答案的选项；答案、法条、涵摄、逐项判断和记忆钩子从 `custom-qb-section="solution"` 开始。主观题题面只放案例/任务和问题，参考答案与评分要点进入答案区。

解析按 GoldQuest 风格组织，但不为了装饰硬塞结构：

- 每个选项都要有具体的法律理由，不能只写“正确/错误”；
- 复杂推理使用有实际内容的列表、Callout 或 Mermaid；不能用关键词串联伪造图示；
- 颜色只标记主体、规则、条件、例外和法律效果等短语，并保持同一题内语义一致；
- 题面不泄露答案，不使用悬停遮罩，不把作答统计写进正文。

### 5. 分配稳定 ID 和考点 ID

详细规则见 [`references/input-contract.md`](references/input-contract.md)。核心要求：

- 新题不能占用原题 `custom-qb-id`；变式题 ID 必须能回溯到源题或目标考点，但不能依赖显示题号。
- `custom-qb-id` 和 `custom-qb-question-topic-ids` 使用小写 ASCII kebab-case；多考点用英文逗号分隔。
- 优先复用已验证的叶子考点 ID。确实没有合适考点时，先创建一个带 `custom-qb-note-topic-id` 的普通考点提供块，再让题目引用它；不要在题目上伪造 `custom-qb-role` 或旧属性。
- 可以附加 `custom-qb-source="damophus-generated"`、`custom-qb-subject`、`custom-qb-category` 等静态属性，但不能写题目尝试次数、正确率、Riff 卡片 ID 或设备信息。

### 6. 校验和交付

交付前逐题检查：法律规则有来源、答案和可见答案一致、选项 ID 稳定、题面没有答案、解析没有丢失要件/例外/涵摄。

在 Skilloom 根目录运行：

```bash
python -X utf8 skills/legal-question-bank/scripts/validate_question_bank.py <output.md> --strict
python -X utf8 skills/legal-question-bank/scripts/audit_topic_granularity.py <output.md> --strict
python -X utf8 skills/legal-goldquest/scripts/validate_output.py <output.md> --strict
```

最后两个检查只在对应脚本和格式规则可用时运行；任何退出码非 0 都要修复或明确报告，不能用“题库能识别”替代 GoldQuest 语义复核。输出题库文件与一份简短的生成报告分开保存；报告可以记录权重来源、覆盖考点和未生成原因，但不能混入题目 IAL。

## 最小输出骨架

```md
##### [流押条款·变式] 1.
{: custom-qb-id="civil-damophus-variant-civil-gold-objective-2020-2-1-14-v01" custom-qb-question-topic-ids="civil-security-flow-clause" custom-qb-type="single" custom-qb-answer="B" custom-qb-source="damophus-generated" custom-qb-subject="civil"}

* 甲与乙签订抵押合同并约定到期不还款时直接取得房屋所有权。
* 下列说法正确的是？
    - [ ] A. …
    - [ ] B. …
    - [ ] C. …
    - [ ] D. …

###### 答案与解析
- 正确答案：B。
{: custom-qb-section="solution"}

- 逐项说明规则、事实涵摄和其他选项为何不成立，保持 GoldQuest 的可扫描解析风格。
```

不要把这个骨架当成固定文案；题型、题干层级和解析载体应服从实际法律语义。
