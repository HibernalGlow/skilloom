# 补充篇 A：外部 Anima Prompt 技能协作（调用 + 边界）

> 本节是 2026-09-27 引入的**外部技能协作层**。
> 目的：让本技能在需要时**主动调用**已安装的第三方 Anima prompt 技能，同时**明确谁说了算**，
> 避免外部规则静默覆盖本技能的银月基模基准（规则 0 / 规则 3）。

---

## 11.1 已安装的外部技能

安装方式：Skills Manager（`~/.skills-manager/bin/skills-manager-cli`），库路径 `~/.skills-manager/skills/`。

| 技能名 | 上游 | 提供什么 | 何时调用 |
|--------|------|---------|---------|
| `anima-prompt-crafter` | AI-KSK/anima-prompt-crafter-skill | 通用 Anima prompt crafting；**Regional LLLite / Inpaint / 角色设定表 / 故事板批量**的输出形态；官方 source baseline；`scripts/validate_anima_prompt.py` 结构校验 | 需要 Regional LLlite 分区、inpaint 修复、角色设定表、多版本 prompt 时 |
| `anima-prompt-caption` | Nana7mi0721/anima-prompt-caption | Anima3 v3.0 槽位模板与**标签库正文**（`assets/模板.txt` 2133 行）：发色/发型/服装改造 7 维/体位库/表情强度 L1-L4/镜头/场景/细节、**§14 特殊主题配方（12 类）**、**§3.1 互斥标签表**，以及独有的**「法典验证场景」**（每个子节附出图验证过的具体标签组合） | 需要**查标签库**、查特殊主题配方、查互斥对、找可直接抄用的验证组合时 |
| `comfyui-animatool` | ShiroEirin/comfyui-good-anima | **情境因果锁**、**画面八维补全**、hard_tags/soft_phrases/nltags_block **三层分离**、画布选择表、冲突消解、负面词动态组装、**Anima 特有失败模式 E001–E011** | 单帧 prompt 需要"有灵魂"、需要排障、需要按画面风险组装负面词时 |
| `anima-prompting` | weikinhuang/dotfiles | Anima **模型事实**：qwen text encoder 使自然语言成为一等输入、`@artist` 必带 `@`、权重语义（Anima 对权重反应比 SDXL 弱）、`[tag]` 在 ComfyUI **不是**降权、负向不上评分词、CFG/步数/分辨率区间、常见 anti-pattern | 需要模型技术事实、权重/采样排障、自然语言 vs tag 取舍时 |

调用方式（直接读文件，不要猜内容）：

```
~/.skills-manager/skills/anima-prompt-crafter/SKILL.md
~/.skills-manager/skills/anima-prompt-caption/SKILL.md
~/.skills-manager/skills/anima-prompt-caption/assets/模板.txt
~/.skills-manager/skills/comfyui-animatool/SKILL.md
~/.skills-manager/skills/comfyui-animatool/references/failure-patterns.md
~/.skills-manager/skills/comfyui-animatool/references/artist-style-research.md
~/.skills-manager/skills/anima-prompting/SKILL.md
```

> 已部署到 agent 的技能目录时，也可用 `~/.agents/skills/<name>/`、`~/.claude/skills/<name>/`、
> `~/.codex/skills/<name>/`。以 Skills Manager 库路径为准。

---

## 11.2 优先级铁律（外部技能不得覆盖本技能）

外部技能面向**通用 Anima**（含 Anima 1.0 / 2B / Base），本技能面向**银月 Silvermoon Base INT8 + 故事板交付格式**。
冲突时按下表裁决，**本技能永远优先**：

| 议题 | 本技能（优先） | 外部技能常见写法 | 裁决 |
|------|---------------|-----------------|------|
| 质量前缀 | 规则 0：以银月 Base INT8 基准为准 | `masterpiece, best quality, score_7, safe` / `score_9, score_8` | **以本技能规则 0 / 规则 3 为准**。`score_9/score_8` 属 Anima 1.0 时代写法，不要照搬 |
| 权重语法与幅度 | 规则 3：`(tag:1.3)` / 1.2 / 1.1，1.1~1.5 区间，过高出 artifacts | `anima-prompting` 称"Anima 对权重反应弱，用 `(chibi:2)`"；`anima-prompt-caption` 称"禁止权重语法" | **以规则 3 为准**。权重语义事实可用于排障（见 §11.3），但不得据此把权重拉到 2.0 |
| 输出结构 | `[tags]` + `[caption]`，男女分列，一行一角色 | 单行逗号串 / `Positive prompt`+`Negative prompt` 块 / 结构化字段 | **以本技能分页格式为准**。外部形态仅用于非故事板产物（Regional/inpaint/设定表） |
| 负面词 | 由工作流/预设承担，story 页不写负面 | 大段动态负面词表 | 负面词只在**排障与调优报告**中引用，不写入 story 页 |
| 单帧/分镜 | 默认单帧，分镜克制（§8） | `anima-prompt-caption` 分镜/多格为常规手段 | **以本技能 §8 克制原则为准** |
| 丝袜/手套颜色 | 默认白色/浅色，深色禁止 | 无此约束 | **以本技能规则为准** |
| 胸围标签 | 禁止 `small breasts` / `large breasts` 等 | 常出现 | **以本技能为准，禁止** |
| LoRA 触发词 | 专有触发词加权重 1.3 写入 `[tags]` | 外部多不涉及 | **以本技能为准** |

> 一句话：**结构、权重、格式、颜色、分镜 → 本技能说了算；画面方法论（因果、八维、失败模式、标签库、模型事实）→ 吸收外部。**

---

## 11.3 值得吸收的外部事实（仅作事实，不作规则）

这些是"知道有好处、但不能违反本技能规则"的技术事实，可用于**排障解释**：

1. **Anima 的自然语言是一等输入**（qwen text encoder 适配器）。不是"tag 不够用才用 caption"。
   → 支持本技能把 `[caption]` 写成有内容的英文段落，而不是走过场。
2. **`@artist` 的 `@` 是必需的**，去掉 `@` 风格几乎不生效。同一 `@artist` 可锁定跨 seed 的稳定画风。
3. **ComfyUI 的 `[tag]` 方括号不是降权**，会被解析为 `([tag]:1)`（字面 token）。要降权用 `(tag:0.6)`。
   本技能规则 3 已禁止在 `[]`/`{}` 内再加权重，二者一致。
4. **负向提示词里不要放评分词**（`safe`/`nsfw` 等），评分由正向的 rating tag 承担；在负向写 `nsfw` 会与
   `sensitive` 及以上场景直接对打。
5. **Anima 对短 prompt 敏感**：过短的 prompt 容易产生平淡甚至不安全的结果。info 密度要够。
6. **单角色镜头不要堆大段环境散文**：环境 prose 会稀释角色 tag，明显降低角色细节。人物 prose 可以长，
   场景 prose 要短。整张图不写地点时模型会默认白底。
7. **分辨率/采样参考区间**（仅参考，最终以工作流为准）：分辨率 512~1536；步数 30~50；CFG 4~5（更高会烧图）。
   Cosmos VAE 要求宽高对齐到 16 的倍数。
8. **多主体必须在 prompt 内绑定归属**（前缀链式：格子方位 + 角色名）。否则模型串脸串服装。

---

## 11.4 调用纪律

- **按需调用**：只在命中 §11.1「何时调用」列的条件时读外部文件，不做无差别全量加载。
- **先读再引**：引用外部标签/配方前必须已读对应文件，禁止凭印象复述外部规则。
- **不复制格式**：从外部技能取的是**标签候选与画面方法**，不是输出格式。
- **不复制画师样例**：从外部或 booru 样张提取画师风格时，只提取视觉倾向（线条/上色/构图/背景复杂度/
  光影氛围），**严禁**把样张里的角色、服装、姿势、暴露度或成人向标签并入 prompt。
- **冲突即记录**：发现外部技能与本技能冲突且本表未覆盖时，**停下并向用户报告**，不要自行裁决。
