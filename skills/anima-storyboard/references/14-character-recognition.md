# 补充篇 D：角色识别、触发词分工与配置权威来源

> 2026-09-27 引入。解决三个长期含糊的问题：
> ① 什么时候要在页面 `[tags]` 里写触发词？② 画师触发词写在哪？③ 这些配置以什么为准？
>
> **核心结论：老角色底模原生认识，不写触发词；所有配置以本作品 `batch.toml` 与 Studio 的
> `lora_rules.json` / `gen_presets.json` 为准，禁止自行发明。**

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
| 2 | `ComfyUI-Workflow-Studio/data/gen_presets.json` | 4 个采样预设的完整参数 + 各自 `quality_prefix` |
| 3 | `ComfyUI-Workflow-Studio/data/lora_rules.json` | LoRA 规则库（路径 / 权重 / 触发词），供 `[auto_rules]` 匹配 |
| 4 | 同批样板作品（`碧蓝航线_拉菲II`、`明日方舟_琴柳`、`蔚蓝档案_妃咲`） | 已实践成功的 toml 写法 |

> ⚠️ `Workflows/wild/lora_rules.json` 是**旧副本**（6911 B），与 Studio 的权威版（9354 B）**不一致**。
> 以 `ComfyUI-Workflow-Studio/data/lora_rules.json` 为准。

### 采样预设（`gen_presets.json` 实读值）

| preset id | 模式 | 参数 | 用途 |
|-----------|------|------|------|
| `anima-two-stage-standard` | 双层 | Stage1 5步 CFG4.6 `er_sde`/`simple` → Stage2 12步 CFG1.6 `dpmpp_2m_sde_gpu`/`beta57` | **默认** |
| `anima-native-30` | 单层 | 30步 CFG4.0 `er_sde`/`beta57` | 足交等精细玩法换用 |
| `anima-single-turbo` | 单层 | 12步 CFG1.6 `euler_ancestral`/`beta57` | 极速草稿 |
| `liino-footjob-suite` | 单层 | 12步 CFG1.6 `euler_ancestral`/`beta57` + 6 LoRA | 镫袜足交全套 |

**这四个 preset 里的 `quality_prefix` 统一是**：
`masterpiece, best quality, aesthetic, highly detailed`
作品 toml 在其后追加画师触发词与足部强化词，末尾加 `uncensored`。

> ⚠️ **不要因为看到「12 步 / CFG 1.6」就判定参数异常。** 那是双层预设的 **Stage 2 精修档**
> （Stage 1 用 CFG 4.6 确立骨架），属既定设计，不是配置错误。

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
