# [08] 分镜（Koma）克制使用规则（非必要不使用）

> ⚠️ **核心原则（2026-09 修订）**：
> - **已停用"默认多格/多帧"！编写 storyboard 时，不再默认使用多个分镜，全篇默认单帧插图构图（Single Frame）。**
> - **只有在绝对必要的时候才使用分镜**（如开宫内部横切面透视 `inset, cross-section`、关键前后对比 `before and after`、同屏必须双重视角 `split screen`、或用户明确要求）。
> - 套弄运动场景（footjob/hairjob/cervical/deepthroat）**优先使用单帧局部特写构图**（如 `close-up, foot focus`），不再强制或默认添加运动多格分镜。
> - 编写 storyboard 时，**不需要完整编一个中文长篇故事**，可以直接列大纲（outline.md），或者直接进行 story 页面创作（输出 tags + caption）。

与 `03-composition.md` §4 单画面构图深度配合。**绝大多数页面保持单帧插图**；分镜仅作为极少数特殊必要视角的补充手段，严禁大面积堆砌。

---

## 一、分镜定位与克制原则

### 1.1 核心原则：非必要不使用

**单帧插图是最高质量的叙事单元。** 模型在编写每一页时，原则上一律采用单帧：

- **默认单帧**：所有常规动作、体位展示、套弄过程、高潮爆发、事后温存全部采用单帧构图。
- **克制加分镜**：仅在单镜头绝对无法表达必要信息（如同时需要主视角与子宫内部透视）时，才允许使用分镜。
- **严禁滥用**：严禁连续或大面积使用 `4koma`/`3koma`/`2koma`。

### 1.2 仅允许使用分镜的必要场景

| 场景 | 推荐分镜 | 说明 |
|------|---------|------|
| **开宫横切面** | `inset, cross-section` | 主场景 + 子宫内部破开透视（画中画） |
| **射精前后对比** | `before and after` | 射精前蓄势待发 vs 射精后灌满白浊的强烈反差 |
| **极端双视角并置** | `split screen` | 仅在男女双方关键神态与动作无法在同一机位展现时偶尔使用 |
| **用户明确指定** | 按要求选用 | 用户明确要求分镜、多格、四格时 |

### 1.3 严禁使用多格分镜的场景

- **常规套弄过程**（足交、口交、抽插等）→ 保持单帧特写，单帧画面更稳定、张力更强。
- **情绪冲击性时刻**（高潮顶点、屈服、破膜、契约成立）→ 单帧集中冲击力最强。
- **体位初次展示** → 需要整页建立清晰的空间关系。
- **结束/后戏页** → 单帧温存比多格更有效。

### 1.4 多格不替代页数

多格分镜**不允许压缩本该多页展开的体位组**。每个体位仍须满足 `03-composition.md` §4.2 的最低 3 页要求。多格仅在同页内提供额外视角，不减少总页数。

---

## 二、分镜形式多样化

### 2.1 标签库（不限于矩形）

| 标签 | 格数 | 说明 | 适用场景 |
|------|------|------|---------|
| `2koma` | 2 | 两格漫画，水平或垂直 | 前后对比、AB面、动作+反应 |
| `3koma` | 3 | 三格漫画 | 情绪递进、起承转 |
| `4koma` | 4 | 四格漫画 | 动作递进、起承转合 |
| `split screen` | 2 | 分屏，无格线边框 | 双场景并行、双视角 |
| `multiple views` | 3-4 | 多视角同帧 | 正面/侧面/俯视同时展示 |
| `before and after` | 2 | 前后对比专用 | 插入前后、射精前后 |
| `inset` | 1主+1角 | 画中画角落 | 主画面+焦点放大/横切面 |
| `comic` | 可变 | 综合漫画分格 | 非标准分格、不规则形状 |

### 2.2 气泡与不规则形状

分镜不限于矩形格子。模型可以使用：

- **圆形/椭圆形气泡**：回忆、幻想、心理活动
- **不规则形状**：爆炸状（高潮）、波浪形（水/液体相关）
- **锯齿边框**：疼痛、冲击、突然动作
- **虚线边框**：想象、梦境、回忆
- **渐变融合**：两个场景自然过渡

在 caption 中用自然语言描述分镜形状：
```
Panel 1 (circular bubble): Shu's memory of the first meeting, framed in a soft circular vignette.
Panel 2 (rectangular): Present day, Shu kneels before the male.
```

### 2.3 标签位置

多格标签放在 camera 槽位末尾，紧接在景别之后：

```
..., from side, full body, 4koma, sound effects, ...
```

### 2.4 使用限制

1. **单页最多 4 格**（`4koma`），禁止 6 格/8 格
2. 多格页的 tag 行**只写最主导的景别/视角**，不需要为每格单独写标签
3. `inset` 的角落横切面**仅适用于 cerpe 场景**，footjob 场景禁用
4. **多格页面不加 LoRA 触发词**（`uxsFJ`/`cerpe` 等必须独占一页）
5. 同一故事板中多格页不超过总页数的 **15%**

---

## 三、多格页 Caption 规则

### 3.1 分格标注

使用多格时必须写明每格内容归属：

| 分格类型 | Caption 格式 |
|---------|-------------|
| `2koma` / `split screen` | `Panel 1: ... Panel 2: ...` |
| `3koma` | `Panel A: ... Panel B: ... Panel C: ...` |
| `4koma` | `Panel A: ... Panel B: ... Panel C: ... Panel D: ...` |
| `multiple views` | `Front view: ... Side view: ... Top view: ...` |
| `inset` | `Main scene: ... Corner inset: ...` |
| `before and after` | `Before: ... After: ...` |
| `comic`（不规则） | `Top panel: ... Bottom-left: ... Bottom-right: ...` |

### 3.2 角色标注规则

每格内角色标注规则**与 SKILL.md §5.1 一致**：
- 始终使用角色映射名（Danbooru 角色名），禁止代词
- 如 `Panel 1: Mutsuki sits on the male's lap. Panel 2: Chise watches from the doorway.`

### 3.3 每格必须有独立信息量

**关键原则：每一格都必须提供新的视觉信息，禁止重复描述。**

| 格序 | 信息类型 | 示例 |
|------|---------|------|
| 格1 | 全景/建立空间 | `from side, full body` 全身展示角色位置 |
| 格2 | 近景/聚焦表情 | `from front, cowboy shot` 正面表情和上半身 |
| 格3 | 特写/局部细节 | `close-up` 足部、手部、面部特写 |
| 格4 | 补充视角 | `from behind` / `pov` 背身或主观视角 |

**每格的镜头方向应不同**，以增加信息量：
```
Panel A: from side, full body (全景建立空间)
Panel B: from front, close-up (正面特写表情)
Panel C: close-up, foot focus (足部细节)
Panel D: from behind (背身补充视角)
```

### 3.4 音效（SFX）嵌入

分镜页面应主动添加音效标签 `sound effects`，并在 caption 中嵌入 `[SFX: ...]`：

```
[tags]
..., 4koma, sound effects, ...

[caption]
Panel A: ... [SFX: haa]
Panel B: ... [SFX: lick]
Panel C: ... [SFX: glk glk]
Panel D: ... [SFX: glk—!]
```

音效应**自然嵌入**在动作描述中，而非机械地附加在句尾。

---

## 四、镜头方向算法（多格专用）

多格页内各格使用不同的镜头方向以增加信息量：

| 格序 | 推荐方向 | 说明 |
|------|---------|------|
| 格1（远景） | `from side` | 全景建立空间 |
| 格2（近景） | `from front` | 正面聚焦表情/细节 |
| 格3（特写） | `close-up` | 局部细节 |
| 格4（可选） | `from behind` / `pov` | 背身或主观视角 |

> tag 行仅写入最主导的方向（格1的），其余格的方向在 caption 中描写。

---

## 五、冲突解决

当本文件与其他规则冲突时，按以下优先级处理：

1. **SKILL.md §4.0 / 03-composition.md §4.0 单画面优先** — 多格分镜不可作为默认构图方式
2. **SKILL.md §4.2 / 03-composition.md §4.2 体位分解** — 每个体位仍须 ≥3 页，不因多格而压缩
3. **SKILL.md §5.1 Tag 格式** — 禁止下划线标签，必须用空格替换
4. **SKILL.md §9.3 严禁脚本循环** — 多格页同样禁止使用脚本批量生成
5. **SKILL.md §7 / 05-plugin-lora.md 插件规则** — 多格页同样必须注入对应的场景类型标签

---

## 六、示例

### 6.1 双格示例（2koma）— 动作+反应

```
[tags]
1girl, 1boy, ..., from side, full body, 2koma, sound effects

[caption]
Panel 1: Mutsuki pulls the male's hand onto Mutsuki's thigh, a teasing smile on Mutsuki's face. [SFX: rustle]
Panel 2: The male's hand grips Mutsuki's thigh, fingers pressing into the sheer fabric of Mutsuki's thighhighs. Mutsuki's breath catches. [SFX: squeeze]
```

### 6.2 三格示例（3koma）— 情绪递进

```
[tags]
1girl, 1boy, ..., from front, cowboy shot, 3koma, sound effects

[caption]
Panel A: Mutsuki kneels, eyes closed, a calm smile, bridal gauntlets resting on the male's thighs. [SFX: haa]
Panel B: Mutsuki's eyes open half-lidded, blush spreading, lips parting. [SFX: ah...]
Panel C: Mutsuki's eyes roll back, mouth open in a cry, tears forming. [SFX: aaaah!]
```

### 6.3 四格示例（4koma）— 动作递进

```
[tags]
1girl, 1boy, ..., from side, cowboy shot, 4koma, sound effects

[caption]
Panel A: The male's tip presses against Mutsuki's entrance, both bodies still. [SFX: pshh]
Panel B: The male pushes forward, the head of the penis parting Mutsuki's labia. [SFX: schlp]
Panel C: Halfway in, Mutsuki's fingers grip the bedsheet, a sharp intake of breath. [SFX: push]
Panel D: Fully seated, the male's pelvis flush against Mutsuki's thighs, both pause. [SFX: aahn]
```

### 6.4 画中画示例（inset, cerpe 场景）

```
[tags]
1girl, cerpe, ..., missionary, legs up, from side, close-up, inset, cross-section, dutch angle

[caption]
Main scene: A dutch angle view of Mutsuki beneath the male, deep penetration creating a stomach bulge, ahegao with rolled eyes, tongue out, tears streaming. Bridal gauntlets flail, trembling.
Cross-section: An inset cross-section shows the male's glans forcing through Mutsuki's cervix, lodged deep inside Mutsuki's uterus, the stomach bulge visible from inside.
```

### 6.5 分屏示例（split screen）— 双视角

```
[tags]
1girl, 1boy, ..., from side, full body, split screen, sound effects

[caption]
Left panel: Mutsuki on the bed, legs spread, mouth open in pleasure, eyes closed. [SFX: aaaah]
Right panel: The male thrusting from behind, hands gripping Mutsuki's hips, face hidden. [SFX: slap slap]
```

### 6.6 不规则气泡示例（comic）— 回忆+现实

```
[tags]
1girl, 1boy, ..., from side, full body, comic, sound effects

[caption]
Main scene (rectangular): Present day, Mutsuki kneels before the male in the bedroom at night.
Top-left bubble (circular, faded): A memory of Mutsuki's first meeting with the male, framed in soft vignette.
Bottom-right (jagged border): Mutsuki's shocked expression, the moment of realization.
```

---

## 七、套弄运动场景处理（单帧优先，多格仅为备用）

### 7.1 核心概念（单帧呈现优先）

> ⚠️ **重要修订**：重复性动作（足交套弄、口交吞吐、开宫顶弄、长发缠绕等）**原则上一律使用单帧插图构图**。
> 单帧通过局部景别（`close-up, foot focus` / `close-up, face focus`）、动态姿态、音效标签 `sound effects` 以及精练的动作描写即可完美传达张力。
> **不再默认使用 4koma 多格分镜**。以下多格运动分镜模板仅在**用户明确要求多格/分镜展示动作过程**时作为参考。

### 7.2 运动线标签（Motion Lines）

在 tag 行添加运动线标签，辅助表达动态感：

| 标签 | 说明 | 适用场景 |
|------|------|---------|
| `motion lines` | 通用运动线 | 所有运动场景 |
| `speed lines` | 速度线（放射状） | 快速动作、冲刺 |
| `emphasis lines` | 强调线（集中线） | 冲击、重点突出 |
| `action lines` | 动作线（平行） | 方向性运动 |

**标签位置**：与 `sound effects` 一起放在 koma 标签附近：
```
..., 4koma, motion lines, sound effects, ...
```

### 7.3 运动分镜的 Caption 格式

运动分镜的 caption 必须**描述每一帧的运动状态**，包括：
1. **动作方向**（向上/向下/向前/向后/旋转）
2. **运动线描述**（运动线从哪里到哪里）
3. **身体反应随运动变化**（表情、肌肉紧张度、液体状态）
4. **SFX 嵌入**（运动音效）

**Caption 模板**：
```
Panel A: [起始位置] + [运动线描述] + [SFX]
Panel B: [运动中段] + [运动线方向变化] + [身体反应] + [SFX]
Panel C: [运动终点] + [运动线汇聚] + [高潮反应] + [SFX]
Panel D: [返回/重复] + [运动线再次展开] + [累积效果] + [SFX]
```

### 7.4 Footjob 套弄分镜示例

#### 4koma 足交套弄（完整过程）

```
[tags]
1girl, 1boy, ..., footjob, (under-stirrup footjob:1.3), (stirrup legwear:1.3), unworn shoes, close-up, 4koma, motion lines, sound effects

[caption]
Panel A: Close-up of Mutsuki's foot in stirrup legwear, the sole pressed flat against the male's shaft at the base, toes curled slightly. Motion lines radiate outward from the point of contact. [SFX: squish]
Panel B: The foot slides upward along the shaft, sole wrinkling as it grips, motion lines following the upward trajectory. Mutsuki's toes spread, then clamp down near the tip. [SFX: slide]
Panel C: The foot pauses at the tip, sole cupping the glans, motion lines converging at the apex. Precum glistens on the sole of Mutsuki's foot. [SFX: drip]
Panel D: The foot slides back down in a rapid stroke, motion lines streaking downward, the stirrup legwear's sheer fabric stretched taut over the sole. [SFX: fwp fwp]
```

#### 2koma 足交特写 + 全景

```
[tags]
1girl, 1boy, ..., footjob, (under-stirrup footjob:1.3), (stirrup legwear:1.3), unworn shoes, 2koma, motion lines, sound effects, zoom layer

[caption]
Top panel (close-up zoom): Mutsuki's foot wraps around the male's shaft, motion lines showing the circular stroking motion, stirrup legwear's sole stretched, toes gripping. [SFX: squish slide]
Bottom panel (full body): Mutsuki lies back, one foot working the male's penis in a rhythmic motion, motion lines trailing from the foot's arc. Bridal gauntlets grip the sheets, mouth open, face flushed. [SFX: fwp fwp]
```

### 7.5 Hairjob 缠绕分镜示例

#### 4koma 头发缠绕套弄

```
[tags]
1girl, 1boy, ..., hairjob, very long hair, handjob, close-up, 4koma, motion lines, sound effects

[caption]
Panel A: Mutsuki gathers a thick lock of very long multicolored hair, wrapping it around the base of the male's shaft. Motion lines spiral outward from the wrap point. [SFX: rustle]
Panel B: Mutsuki's hand twists the hair tighter, the strands compressing the shaft, motion lines showing the tightening spiral. Mutsuki's eyes focus with concentration. [SFX: tighten]
Panel C: Mutsuki's hand slides upward along the hair-wrapped shaft, motion lines following the upward pull, the hair strands glistening with precum. [SFX: slide]
Panel D: The hand reaches the tip and reverses, sliding back down with a flick of the wrist, motion lines streaking downward, hair strands loosening slightly before the next wrap. [SFX: fwp]
```

### 7.6 Cervical Penetration 顶弄分镜示例

#### 4koma 开宫顶弄（深插运动）

```
[tags]
1girl, cerpe, ..., (cervical penetration:1.3), (uterus:1.2), (deep penetration:1.2), (stomach bulge:1.2), from side, close-up, 4koma, motion lines, sound effects

[caption]
Panel A: Close-up of the male's shaft fully inserted, the tip pressed against Mutsuki's cervix. Motion lines radiate from the point of cervical contact, indicating pressure. Mutsuki's eyes widen. [SFX: press]
Panel B: The male thrusts forward, the cervix parting slightly, motion lines converging inward showing the deep penetration. Mutsuki's mouth opens in a gasp, stomach visibly bulging. [SFX: push]
Panel C: The male withdraws slightly, the cervix contracting, motion lines expanding outward showing the retreat. Mutsuki's body trembles, a whimper escaping. [SFX: schlp]
Panel D: The male thrusts deep again, harder this time, motion lines slamming inward, the stomach bulge more pronounced. Mutsuki's eyes roll back, ahegao forming. [SFX: thud]
```

### 7.7 Deepthroat 吞吐分镜示例

#### 4koma 深喉吞吐运动

```
[tags]
1girl, 1boy, ..., fellatio, deepthroat, oral, kneeling, close-up, 4koma, motion lines, sound effects

[caption]
Panel A: Mutsuki's mouth at the tip, lips parting, motion lines showing the initial descent. Yellow eyes look up, cheeks already flushed. [SFX: haa]
Panel B: Halfway in, Mutsuki's cheeks hollow, motion lines compressing inward as the shaft fills the mouth. Tears form at the corners of Mutsuki's eyes. [SFX: glk]
Panel C: Fully deepthroated, Mutsuki's nose against the male's pelvis, motion lines converging at the deepest point. Tears stream, drool escapes. [SFX: glk—!]
Panel D: Mutsuki pulls back to the tip, cheeks expanding as air rushes in, motion lines radiating outward. A strand of saliva connects Mutsuki's lips to the glans. [SFX: ha...]
```

### 7.8 运动分镜的关键原则

1. **每格必须描述运动方向**：用 "upward" / "downward" / "forward" / "backward" / "spiraling" 明确方向
2. **运动线必须在 caption 中描写**：如 "motion lines radiate from..." / "motion lines streak downward"
3. **SFX 与运动节奏匹配**：快速运动用 "fwp fwp"，慢速用 "slide"，冲击用 "thud"
4. **身体反应随运动递进**：起始→中段→终点→返回，每格表情/紧张度不同
5. **Tag 行添加 `motion lines`**：让生成模型知道需要绘制运动线
