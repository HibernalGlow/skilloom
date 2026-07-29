# [08] 多格分镜（Koma）规则

> ⭐ **本文件是分镜（Koma）的完整参考。编写每一页 story 时，必须判断是否适合加分镜。**
> - 套弄运动场景（footjob/hairjob/cervical/deepthroat）→ **必须**参考本文件 §七
> - 动作递进/多视角/前后对比 → 参考本文件 §一~§六
> - 不确定时 → 默认单帧

与 `03-composition.md` §4 单画面构图配合使用。**默认每页为单帧插图构图**；多格分镜由模型**主动判断**合适时机使用，而非强制每页添加。

---

## 一、多格分镜定位

### 1.1 核心原则：模型主动判断

**分镜是视觉叙事工具，不是格式要求。** 模型在编写每一页时，应自然判断该页是否适合使用分镜：

- 如果单帧能完整表达 → **用单帧**（大多数页面）
- 如果需要展示动作递进/多视角/前后对比 → **主动加分镜**
- 不确定时 → **默认单帧**

> 分镜的目标是**提升画面信息量和观感**，不是增加格式复杂度。

### 1.2 适用场景（模型主动判断）

| 场景 | 分镜类型 | 说明 |
|------|---------|------|
| 动作递进 | 4koma / 3koma | 口交深喉、插入过程、连续动作 |
| 前后对比 | 2koma / before and after | 插入前/后、射精前/后、衣服穿/脱 |
| 双视角并排 | 2koma / split screen | 女方表情 + 男方动作同时呈现 |
| 主画面+局部放大 | inset / 2koma | 全身景 + 角落特写（足交、开宫横切面） |
| 多视角展示 | multiple views | 正面/侧面/俯视同时展示 |
| 情绪递进 | 3koma / 4koma | 从羞涩→享受→高潮的表情变化 |
| 场景切换 | 2koma / split screen | 同一时间不同地点 |

### 1.3 禁止使用的场景

- **情绪冲击性时刻**（高潮顶点、屈服、真相揭露）→ 单帧集中冲击力更强
- **体位初次展示** → 需要整页建立空间关系
- **结束/后戏页** → 单帧温存比多格更有效

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

## 七、套弄运动分镜（Motion Koma）

### 7.1 核心概念

**套弄运动分镜**用于展示重复性动作的**节奏感和过程感**——足交套弄、口交吞吐、开宫顶弄、头发缠绕等。通过多格连续帧 + 运动线，让静态画面产生动态效果。

适用场景：
- **Footjob 套弄**：脚掌包裹阴茎的来回运动
- **Hairjob 缠绕**：长发缠绕阴茎的旋转/拉扯运动
- **Cervical penetration 顶弄**：龟头反复顶入宫颈的深插运动
- **Deepthroat 吞吐**：阴茎在口腔中的进出运动
- **Rhythmic thrusting**：有节奏的抽插运动

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
