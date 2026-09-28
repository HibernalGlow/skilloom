# 补充篇 D：角色识别、触发词分工与配置权威来源

> 2026-09-27 引入。解决三个长期含糊的问题：
> ① 什么时候要在页面 `[tags]` 里写触发词？② 画师触发词写在哪？③ 这些配置以什么为准？
>
> **核心结论：老角色底模原生认识，不写触发词；所有配置以本作品 `batch.toml` 与 Studio 的
> `lora_rules.json` / `gen_presets.json` 为准，禁止自行发明。**

---

## 14.1.1 ⚠️ 角色识别 ≠ 画师风格（两件事，不要混为一谈）

**老角色不挂角色 LoRA，但仍然应该挂画师 LoRA。** 这两件长期被混淆：

| 维度 | 老角色（第 1/2 批） | 新角色（第 3 批） |
|------|-------------------|----------------|
| 角色 LoRA | ❌ 不挂（底模原生认识） | ✅ 必须挂 |
| 页面角色触发词 | ❌ 不写 | ✅ 裸写 |
| **画师 LoRA** | ✅ **照样挂**（风格是独立维度） | ✅ 照样挂 |
| **画师触发词位置** | `batch.toml` 的 `quality_prefix` | 同左 |

**反例警示**：`明日方舟_深靛` 曾因「只查了 `lora_rules.json` 没有画师条目」而错误得出
「无画师 LoRA」的结论，实际本地就有 `zbjlm@zbjlm_anima1.0_v0.1.safetensors`（175.1 MiB）。

### 画师 LoRA 的三个确认动作（缺一不可）

1. **查完整库存**：`Workflows/wild/lora-cleanup-<日期>.md`（**权威**，逐目录列出全部 LoRA 文件 + 大小 + 落地天数）
2. **查画师清单**：`Workflows/wild/artist/list.md`（带 `♥` 的是已有 LoRA 的）、`artist/string.txt`（历史混用串）
3. **对外核实触发词**：Civitai 搜 `https://civitai.com/api/v1/models?query=<名字>&types=LORA`，
   取 `modelVersions[].baseModel == "Anima"` 的版本及其 `trainedWords`

### 本地 LoRA 文件名的触发词约定

本地文件普遍命名为 **`<名字>@<实际文件>.safetensors`**：

```
zbjlm@zbjlm_anima1.0_v0.1.safetensors     → 触发词 @zbjlm
atdan_anima_v1.0_dim64@atdan.safetensors  → 触发词 @atdan
healthyman_v1_epoch28@hea1thy.safetensors → 触发词 @hea1thy
style-Bubutuke-Anima-v01.safetensors      → 触发词 bubutuke（无 @）
```

**触发词以 `@` 分隔**：`@` 后面的就是触发词；写入 `quality_prefix` 时通常配 `@` 前缀
（`@atdan` / `@hea1thy` / `@freng` / `@zbjlm`），也有不带 @ 的（`bubutuke` / `kincora`）。
**不确定时以 Civitai 的 `trainedWords` 为准。**

### 画师 LoRA 权重惯例（实测自 5 部作品）

| 画师 | 权重 |
|------|------|
| Atdan | 0.8 |
| Freng | 0.8 |
| Healthyman | 1.0 |
| Kedama mi1k | 1.0 |
| Bubutuke | 0.85 |

→ **起步取 0.8**；风格不足升 1.0，烧图/伪影降到 0.6~0.7。

---

## 14.1 角色识别分工（老角色 vs 新角色）

Anima 底模的知识截止约为 **2025 年 9 月**（2.9B 增量训练后延到 **2026 年 7 月**）。
因此按技能已有的「角色时间批次分类」直接推导出触发词策略：

| 批次 | 时间范围 | 底模是否原生认识 | 页面 `[tags]` 是否写角色触发词 | 是否挂角色 LoRA |
|------|---------|----------------|---------------------------|---------------|
| **第 1 批** | ≈2025-09 之前 | ✅ 认识 | **不写** | **不挂** |
| **第 2 批** | 2025-09 ~ 2026-06 | ✅ 基本认识 | **不写** | **不挂**（识别失败再试） |
| **第 3 批** | 2026-06 之后 | ❌ 不认识（如终末地/Endfield 系） | **必须写**（裸写，不加权重） | **必须挂** |

### 判定流程

```
角色拿来
  ├─ 属第 1/2 批（≈2026-06 之前）？→ 底模原生识别 → 页面只写角色 Danbooru tag，不加任何触发词
  └─ 属第 3 批（2026-06 之后）？  → 页面 [tags] 写角色 LoRA 触发词（裸写）
                                   → batch.toml 用 [[page_rule]] when_triggers 匹配该触发词并挂 LoRA
```

### 判定与验证的实际做法

1. **先查 Danbooru `post_count`**：`indigo (arknights)` 有 **287** 帖 → 底模必然认识，属老角色。
   只有几十帖甚至 0 帖的新角色才需要 LoRA 兜底。
2. **先跑识别测试页**：本作品目录下若已有识别测试（如 `recog/`），以它的结论为准。
3. **不要凭感觉挂 LoRA**：老角色挂角色 LoRA 反而会与底模原生知识打架，拉低识别率。

### 参考样板（已实践成功）

| 作品 | 角色批次 | 做法 |
|------|---------|------|
| `碧蓝航线_拉菲II` | 老角色 | 「先测底模认不认识三个形态（**不挂角色 LoRA**）」，页面无触发词 |
| `明日方舟_深靛` | 老角色（287 帖） | 同拉菲II：只靠底模原生知识 |
| `明日方舟终末地_洛茜` | **新角色** | 挂 `rossi_v2_anima`，触发词 `rossi` 在页面上 |
| `星穹铁道_爻光_火花_花火` | 新角色 | `[[page_rule]] 角色·爻光` `when_triggers = ["yaoguang"]` |
| `原神_至冬` | 混合 | 桑多涅/哥伦比亚/奥黛塔三个角色各设一条 `page_rule` |

> `深靛` 无角色 LoRA、无画师触发词，`quality_prefix` 只保留 preset 基串 —— **这是老角色的标准形态**。

---

## 14.2 触发词的三处落点（不要放错）

| 触发词类型 | 写在哪 | 格式 | 说明 |
|-----------|-------|------|------|
| **画师触发词** | `batch.toml` 的 `[prompt] quality_prefix` | `…, highly detailed, @atdan, uncensored` | **绝不写进页面 `[tags]`**；画师无触发词时就不放该 token |
| **角色触发词**（仅第 3 批） | 页面 `[tags]` 行内 | 裸写 `typhoeusendfield` | 由 `batch.toml` 的 `[[page_rule]] when_triggers` 匹配后挂 LoRA |
| **动作/玩法触发** | 页面 `[tags]` 行内，**只写原生 Danbooru tag** | `(under-stirrup footjob:1.3)` | 由 `when_triggers` 自动挂钩对应 action LoRA |

### ⚠️ 禁止在页面写 LoRA 专有触发词

页面**只写原生 Danbooru tag**，由 toml 去匹配。以下专有触发词**不写进页面**：

| 不写（LoRA 专有） | 改写（原生 Danbooru tag） |
|------------------|------------------------|
| `ustirrup` / `stirrupjob` / `stirrup3` / `uxsFJ` | `footjob`, `under-stirrup footjob` |
| `cerpe` / `cervical` | `cervical penetration` |
| `hairop` | `hairjob`, `hair on penis` |
| `throughfoot` | `footjob through footwear` / `shoejob` |

**证据**：对 4 部已完成作品共 240 页做全量 grep ——
`ustirrup` / `stirrupjob` / `cerpe` / `hairop` / `uxsFJ` / `throughfoot` 命中数**全部为 0**；
`cervical`（原生 tag 的一部分）30 页、`footjob` 37 页。
**唯一被写进页面的触发词是角色 LoRA 触发词**（`typhoeusendfield`，60 页，裸写不加权重）。

---

## 14.3 配置的权威来源（按优先级）

**禁止自行发明触发词、权重、采样参数。** 按以下顺序查：

| 优先级 | 来源 | 内容 |
|-------|------|------|
| 1 | **本作品目录的 `batch.toml`** | 本作品已跑通的画师、preset、`[[page_rule]]`、`[auto_rules]` |
| 2 | `ComfyUI-Workflow-Studio/data/gen_presets.json` | 5 个采样预设的完整参数 + 各自 `quality_prefix` |
| 3 | **`Workflows/wild/lora-cleanup-<日期>.md`** | **LoRA 完整库存**（逐目录 · 文件名 · 大小 · 落地天数）—— 找文件用这个 |
| 4 | `ComfyUI-Workflow-Studio/data/lora_rules.json` | ⚠️ **只是 `[auto_rules]` 的匹配规则表，不是完整库存**（仅 34 条，画师类大多缺失） |
| 5 | `Workflows/wild/artist/list.md` · `artist/string.txt` | 已有 LoRA 的画师清单与历史混用串 |
| 6 | 同批样板作品（`碧蓝航线_拉菲II`、`明日方舟_琴柳`、`蔚蓝档案_妃咲`） | 已实践成功的 toml 写法 |

> ⚠️ **两个易错点**：
> ① `Workflows/wild/lora_rules.json`（6911 B）是**旧副本**，别用。
> ② `Studio/data/lora_rules.json`（9354 B）是权威版，但**仅 34 条、覆盖面窄** ——
> 不要因为它「没查到这个画师」就断定本地没有该 LoRA。**查文件去备份库看 lora-cleanup。**

### 采样预设（`gen_presets.json` 实读值）

| preset id | 模式 | 参数 | 用途 |
|-----------|------|------|------|
| `anima-single-17` | 单层 | 17步 CFG1.6 `dpmpp_2m_sde_gpu`/`beta57` dn1.0 | **默认**（3-seed 对照唯一 0 坏格） |
| `anima-two-stage-standard` | 双层 | Stage1 5步 CFG4.6 `er_sde`/`simple` → Stage2 17步 CFG1.6 `dpmpp_2m_sde_gpu`/`beta57` **@dn0.7** | 要稳定出 6 格 / 要版式多样性时用 |
| `anima-native-30` | 单层 | 30步 CFG4.0 `er_sde`/`beta57` | 足交等精细玩法换用 / 踩脚页 |
| `anima-single-turbo` | 单层 | 12步 CFG1.6 `euler_ancestral`/`beta57` | 极速草稿 |
| `liino-footjob-suite` | 单层 | 12步 CFG1.6 `euler_ancestral`/`beta57` + 6 LoRA | 镫袜足交全套 |

**这五个 preset 里的 `quality_prefix` 统一是**：
`masterpiece, best quality, aesthetic, highly detailed`
作品 toml 在其后追加画师触发词与足部强化词，末尾加 `uncensored`。

> ⚠️ **2026-09-28 修订 —— `anima-two-stage-standard` 曾经是假的，别照旧文理解。**
> 两个 bug 叠加：
> ① applier 的四个分支**从不写 `denoise`**，Stage 2 用工作流文件里烤死的 `1.0`，直接丢弃 Stage 1
> 的潜空间（实测「保留 Stage 1」vs「删掉 Stage 1」**RMSE = 0.0000**，逐像素相同 —— 那 5 步白烧）；
> ② 节点识别用裸子串 `"KSampler"` 匹配，把 `KSampler Config (rgthree)`（节点 929）当成了 Stage 1，
> **真正的 Stage 1（节点 836）永远保持旁路**。
> 所以历史上的「双层」出图，真实身份是**单层 12 步**。现已修成 `5 + 17@dn0.7`（有效 16 步）。
>
> **因此：**
> - **默认改用 `anima-single-17`** —— 3-seed × 12 张对照里唯一 0 坏格，且速度不吃亏（17.2s）。
> - `anima-two-stage-standard` 只在你**需要稳定出 6 格 / 需要同一提示词掷出不同版式**时用，
>   代价是坏格率更高（3 页里 2–3 页出现「漂浮白底格 / 比例失调」）。
> - 双层的版式多样性确实更高：同提示词换 seed 的低频版式差异 **1.72×**（n=3 seed）。机理是 Stage 1
>   高 CFG(4.6) + 少步数把粗版式早早拍板，Stage 2 `dn0.7` 只能重画噪声表后 70%。同一机制
>   **锁好版式也锁坏版式** —— 这就是坏格来源。实用组合是「**双层滚、单层收**」。
> - **别再用旧的 `5+12 @dn1.0` 配法。**
> - **足部/踩脚页必须单采**（`tools/test_foot_preset_gate.py` 闸门 + `tools/audit_foot_presets.py` 审计）。
>
> 完整证据链：`stage1_fix_report.md`（工作区根目录）与 `references/15-in-context.md` §15.5。

---

## 14.4 本规则与旧文的冲突裁决

技能正文曾有两处互相矛盾的表述，现统一如下（以本节为准）：

| 旧表述 | 位置 | 现状 |
|-------|------|------|
| 「LoRA 触发词必须写入 story 页面」 | 规则 0 后重要政策 | **仅对第 3 批新角色成立**；老角色不写。且指**角色**触发词，不含动作 LoRA 专有词 |
| 「LoRA 触发词不主动添加到 story 页面」 | 规则 3 ① | **对动作/画师类成立**：动作走原生 tag、画师走 toml |

**统一裁决**：

```
角色触发词：第1/2批不写；第3批裸写（不加权重）
画师触发词：只写 batch.toml 的 quality_prefix，永不进页面
动作触发词：页面只写原生 Danbooru tag，专有词一律不写
```

---

## 14.5 新角色接入清单（第 3 批专用）

1. 查 `lora_rules.json` 是否已有该角色 LoRA 与触发词；无则先训练/下载。
2. 页面 `[tags]` 行内**裸写**触发词（如 `rossi`），不加权重。
3. `batch.toml` 增加：

```toml
[[page_rule]]
name          = "角色·<角色名>"
when_triggers = ["<触发词>"]

  [[page_rule.loras]]
  name         = "<LoRA 名>"
  path         = 'anima\chara\<系列>\<文件>.safetensors'
  model_weight = 1.0
  clip_weight  = 1.0
```

4. 跑 3 页识别测试（最小标签 / 加描述标签两版），确认触发率后再全量出图。

---

## 14.6 ⛔ 多人场景与角色 LoRA 互斥（硬约束）

> **只要有一个出场角色依赖 LoRA，就不写多人场景。**
> **多人场景的充要条件：所有出场角色都是底模原生认识的（第 1/2 批）。**

### 为什么

多个角色 LoRA 同时加载会**互相污染**。权重在 UNet 的同一批 cross-attn 层叠加后，
模型无法区分哪个特征属于哪个主体，典型故障：

| 故障 | 表现 |
|------|------|
| **串脸** | A 的瞳色/脸型长到 B 脸上，或两人共用一张脸 |
| **串服装** | A 的踩脚袜/手套/裙子跑到 B 身上 |
| **属性漏出** | 两人都变成 LoRA 角色的样子（克隆人） |
| **多余主体** | 凭空多长出一个人（`extra person`） |

⚠️ **这不是提示词能修的** —— 属于 LoRA 权重叠加机制的固有问题。加 `nltags`、加负向、
换 `split screen` 都只能缓解表象，不能消除。

### 判定口径

| 情形 | 算不算「多人」 | 允许？ |
|------|--------------|-------|
| 1 个女角 + `faceless male` / `the doctor`（无需 LoRA） | **不算** | ✅ 照常写 |
| 2 个以上角色，**全部**底模原生认识 | 算 | ✅ 允许 |
| 2 个以上角色，**任一**依赖 LoRA（第 3 批） | 算 | ⛔ **禁止** |
| 2 个以上角色，**全部**依赖 LoRA | 算 | ⛔ **尤其禁止** |

> `faceless male` / `the doctor (arknights)` / 通用路人属「无需 LoRA」的配角，**不计入多人判定**。
> 本技能既往作品（提丰 / 琴柳 / 拉菲II / 深靛）全部是「1 女角 + 博士」结构，天然合规。

### 编写前的强制判定流程

```
列出本页所有出场角色
  └─ 逐个查：属第 1/2 批（底模认识）还是第 3 批（依赖 LoRA）？
       ├─ 全部第 1/2 批 → ✅ 可以写多人
       └─ 任一第 3 批   → ⛔ 退回改写
```

判定依据（任一即可）：
1. **Danbooru `post_count`** —— 几百帖 = 底模必认识；几十帖甚至 0 帖 = 依赖 LoRA
2. **角色时间批次表** —— 第 3 批（2026-06 之后，如终末地/Endfield 系）判定为依赖 LoRA
3. **`recog/` 识别测试结论** —— 本作品若已做过识别测试，以其为准
4. **`lora_rules.json` / `lora-cleanup`** —— 该角色是否登记了角色 LoRA

### 必须同框时的处理（按优先级）

| # | 方案 | 说明 |
|---|------|------|
| 1 | **拆页** | 每个角色单独一页。推荐方案，也与本技能「默认单帧」哲学一致 |
| 2 | **换角色** | 把依赖 LoRA 的角色换成原生认识的替代角色 |
| 3 | **降级为配角** | LoRA 角色只出现背影 / 手脚 / 局部，不与另一角色共享面部特写 |
| 4 | **Regional LLLite 分区挂 LoRA** | 高级方案，需 `anima-prompt-crafter` 技能；**不默认使用** |

### 明确禁止的做法

```toml
# ⛔ 禁止：多个角色 LoRA 同挂，去画同一张多人图 —— 这是串脸的直接成因
[[base.loras]]
  name = "角色A"
[[base.loras]]
  name = "角色B"
```

```toml
# ⛔ 同样禁止：用 page_rule 让两个角色 LoRA 在同一页命中
[[page_rule]]
name          = "双角色"
when_triggers = ["character_a", "character_b"]   # ← 两个角色触发词同页 = 事故
```

### 正确做法

```toml
# ✅ 每个 page_rule 只挂一个角色 LoRA，且 when_triggers 只匹配该角色
[[page_rule]]
name          = "角色·<A>"
when_triggers = ["<A 的触发词>"]

  [[page_rule.loras]]
  name         = "<A 的 LoRA>"
```

```markdown
<!-- ✅ 排版约定：多人页只在「全部原生认识」时出现 -->
| 页码 | 角色 | 是否依赖 LoRA | 允许同框 |
|------|------|--------------|---------|
| XX01 | 深靛（287 帖，原生） + 博士 | 否 | ✅ |
| XX02 | 深靛 + 某新角色（2026-06 后） | **是** | ⛔ 拆成两页 |
```

### 与其它规则的关系

- 与 **规则 0c** 配套：0c 决定「哪些角色要挂 LoRA」，本条决定「挂了 LoRA 的角色不能与谁同框」
- 与 **§8 分镜克制** 不冲突：`split screen` / `2koma` 是**同一张图内分区**，
  **不能**用来绕开本条（LoRA 是按整张图加载的，分区不影响权重叠加）
