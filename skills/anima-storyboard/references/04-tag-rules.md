<!-- Extracted from SKILL.md §五、ANIMA3 分页格式 + 六、标签验证 -->

# 五、ANIMA3 分页格式

## 5.1 单页文件结构

```
[tags]
1girl, mobius \(honkai impact 3rd\), green hair, very long hair, snake eyes, heterochromia, fang, small breasts, latex bodysuit, (stirrup legwear:1.3), (toeless legwear:1.2), arm gloves, high heels
1boy, faceless male, penis, erect, hetero, laboratory, night, from side, full body

[caption]
Full English description paragraph. Captures what the scene depicts.
```

**⚠️ 权重提醒**：`(stirrup legwear:1.3)`、`(toeless legwear:1.2)` 演示了关键服装标签加权重的正确做法。详见 SKILL.md §规则 3。

**⚠️ 丝袜颜色默认规则**：丝袜/legwear 默认使用白色或渐变色，黑色丝袜仅在用户明确指定时使用。详见 SKILL.md 丝袜颜色默认规则。

**⚠️ 多角色标签格式**：2 个及以上女性角色时，每个角色的 tag 独占一行，男主 tag 独占最后一行。参见 §5.1 多女主 tag 分离规则。

```
[tags]
2girls, ffm threesome,
edelgard (isekai maou), dark skin, horns, silver hair, very long hair, grey eyes, flat chest, black choker, ...,
shera l. greenwood, elf, pointy ears, blonde hair, braid, aqua eyes, large breasts, green dress, ...,
1boy, faceless male, penis, erection, size difference, height difference, missionary, from side, full body, bedroom, night

[caption]
Shera: <Shera 的动作描写和体感>
Edelgard: <Edelgard 的动作描写和体感>
The male: <男主的动作描写和体感>
```
### 标签输出格式：禁止下划线

**故事板 `[tags]` 输出中，所有标签必须用空格代替下划线。** 这是强制规则，无例外。

```
❌ 错误: 1girl, black hair, very long hair, ishtar \(fate\), small breasts, from side
✅ 正确: 1girl, black hair, very long hair, ishtar \(fate\), small breasts, from side
```

| 原始 Danbooru tag | 故事板输出 |
|-------------------|-----------|
| `black hair` | `black hair` |
| `very long hair` | `very long hair` |
| `ishtar \(fate\)` | `ishtar \(fate\)` |
| `ishtar \(swimsuit rider\) \(fate\)` | `ishtar \(swimsuit rider\) \(fate\)` |
| `small breasts` | `small breasts` |
| `from side` | `from side` |
| `cowboy shot` | `cowboy shot` |
| `faceless male` | `faceless male` |
| `mating press` | `mating press` |

**保留下划线的例外**（仅限 chara 文件内部和 wiki 查询时使用）：
- chara/prefer/ 下的 `.txt` 文件内部标签仍可用下划线（因为这是 Danbooru 原始格式）
- 向 Danbooru API 查询时使用下划线格式
- 文件名中的 tag 使用下划线

**但故事板页面 `[tags]` 输出必须全部替换为空格。**

- `[tags]` 和 `[caption]` 之间空一行
- **男女分列**：`1girl` 开头行放女主外观/服装 tag；`1boy` 开头行放男主标签 + 共有标签（场景/镜头/体位/H/hetero）。禁止将 `1boy` tag 混入 `1girl` 行
- 禁止 `1girl` 行出现 `hetero`、`faceless male`、`penis`、镜头/场景等非女主专属 tag
- 禁止 `1boy` 行出现女主外观 tag（`green hair`、`snake eyes`、`fang`、`stirrup legwear` 等）
 - caption 采用**客观描述风格**（非小说叙事）：直接描述画面中可见的内容——角色位置、动作、服装材质、表情、身体反应、体液状态。禁用修辞手法、比喻、心理描写、情绪推演
 - **Caption 禁对话引用**：禁止在 caption 中使用直接引号对话（`"xxx" she said`），使用间接叙述描述角色话语（`Mutsuki demands`/`the male commands`/`Chise whispers` 等）
 - **Caption 禁止代词**：caption 中**严格禁止**使用 `she`/`her`/`hers`/`he`/`him`/`his` 等代词。始终使用角色名（如 `Mutsuki`、`Chise`）或角色标识语（`the girl`、`the female`、`the male`）。每句主语必须明确到具体角色
 - **Caption 聚焦画面**：仅描写画面中直接可见的元素——角色表情、肢体语言、服装材质、动作过程、体液状态。不写内心独白、情绪推演、背景故事
 - **每页独立**：每页 tag 和 caption 完全自包含。禁止跨页指涉（如 "after last night"、"still"、"again"、"as before"），每页 caption 如同独立图片说明
 - **Tag 必须包含玩法细节**：每页 tag 必须包含具体性行为/体位标签（如 `edging`/`cowgirl position`/`paizuri`/`footjob` 等），不能仅有外观服装标签。tag 行优先展示玩法标签」
 - **多人场景特殊规则**：当 `3girls`+ 时，**禁止** 使用 `1boy` tag，改为仅保留 `penis` + `erection`（及体位标签如 `vaginal`、`doggystyle` 等）在 boy 行。此举避免 Stable Diffusion 在多人构图中画出错误肢体的概率。
   - ✅ 3girls 正确示例：`penis, erection, large penis, vaginal, threesome`
   - ❌ 3girls 错误示例：`1boy, faceless male, penis, erection, ...`
   - `2girls` 场景仍可使用 `1boy`（两人 + 一男共三体，风险可控）

- **多女主 tag 分离规则**：`2girls` 场景中，每个女性角色的外观标签必须在 tag 行中明确分区块排列，不得混合堆叠。格式：`第一女主 tag..., 第二女主 tag...`
  - 在单人字符标签（如 `shun (blue archive)`）之后紧跟其专属外观标签，再换下一个角色
  - 示例：`2girls, shun (blue archive), white stirrup leggings, white pantyhose, ..., shun (small) (blue archive), see-through white bodystocking, taut bodystocking, ...`
  - 带有区别性服装的角色（如小瞬的连体白丝、花边手套），其专属服装 tag 必须紧贴其角色 tag，避免被模型分配到另一角色

- **⚠️ 属性污染防止规则（3+ 角色强制）**：当页面包含 2 个及以上女性角色时，每个角色的**外观属性标签**（发色、瞳色、肤色、体型、种族特征等）必须**严格限定在该角色的 tag 区块内**，禁止跨角色混写。

  **属性污染的定义**：角色 A 的固有外观标签（如 `dark skin`、`horns`、`animal ears`）出现在角色 B 的 tag 区块附近，导致 AI 模型将该属性错误分配给角色 B。

  **正确格式**（每个角色独立一行或明确分隔）：
  ```
  ✅ 正确:
  2girls, edelgard (isekai maou), dark skin, horns, silver hair, very long hair, grey eyes, flat chest, black choker, ..., shera l. greenwood, elf, pointy ears, blonde hair, braid, aqua eyes, large breasts, green dress, ...
  ```
  每个角色的 tag 区块内**只包含该角色自身的外观属性**，不得混入其他角色的属性。

  **错误格式**（属性混写导致污染）：
  ```
  ❌ 错误:
  2girls, edelgard (isekai maou), shera l. greenwood, dark skin, horns, silver hair, blonde hair, ...
  ```
  `dark skin` 出现在两个角色之间，模型可能将其分配给 Shera。

  **错误格式**（所有属性堆在一起）：
  ```
  ❌ 错误:
  2girls, edelgard (isekai maou), shera l. greenwood, dark skin, horns, silver hair, blonde hair, grey eyes, aqua eyes, flat chest, large breasts, ...
  ```
  两种肤色、两种瞳色、两种体型混在一起，模型无法区分归属。

  **3+ 角色格式**（每个角色独立一行）：
  ```
  ✅ 正确:
  3girls, edelgard (isekai maou), dark skin, horns, silver hair, very long hair, grey eyes, flat chest, black choker, ...
  shera l. greenwood, elf, pointy ears, blonde hair, braid, aqua eyes, large breasts, green dress, ...
  rem (isekai maou), cat girl, cat ears, black hair, very long hair, green eyes, small breasts, flat chest, fang, ...
  ```

  **禁止的属性混写模式**：
  | 错误模式 | 说明 | 后果 |
  |---------|------|------|
  | `dark skin` 出现在非暗肤色角色附近 | 肤色属性污染 | 模型给浅肤色角色画上暗肤色 |
  | `animal ears` 出现在非兽耳角色附近 | 种族特征污染 | 模型给普通角色加上兽耳 |
  | `flat chest` 和 `large breasts` 混在同一区块 | 体型属性冲突 | 模型随机分配体型 |
  | `blonde hair` 和 `black hair` 混写 | 发色属性冲突 | 模型给角色画错发色 |
  | 所有角色的 tag 堆在同一行无分隔 | 全部属性混合 | 模型随机组合属性，角色外观不可控 |

  **核心原则**：每个角色的 tag 区块 = 角色标签 + 该角色的全部外观属性 + 该角色的服装。其他角色的任何属性不得出现在此区块内。

- **⚠️ 男主标签独立行规则（防止男主消失/futa 化）**：多角色场景中，男主的 tag **必须独占一行**，不得与任何女性角色的 tag 混写在同一行。

  **男主消失/futa 化的原因**：当 `1boy, faceless male, penis` 与女性角色的 tag 混在同一行时，模型可能：
  1. 将 `penis` 错误分配给某个女性角色 → 该女性变成 futa
  2. 忽略 `1boy` → 男主从画面中消失
  3. 将 `faceless male` 的无脸特征与女性面部混合 → 产生畸形面部

  **正确格式**（男主独占一行）：
  ```
  ✅ 正确:
  2girls, ffm threesome,
  edelgard (isekai maou), dark skin, horns, silver hair, very long hair, grey eyes, flat chest, black choker, ...,
  shera l. greenwood, elf, pointy ears, blonde hair, braid, aqua eyes, large breasts, green dress, ...,
  1boy, faceless male, penis, erection, size difference, height difference, missionary, from side, full body, bedroom, night
  ```
  女性角色 tag → 女性角色 tag → 男主 tag（独占最后一行）

  **3+ 角色格式**：
  ```
  ✅ 正确:
  3girls, ffm threesome,
  edelgard (isekai maou), dark skin, horns, silver hair, very long hair, grey eyes, flat chest, black choker, ...,
  shera l. greenwood, elf, pointy ears, blonde hair, braid, aqua eyes, large breasts, green dress, ...,
  rem (isekai maou), cat girl, cat ears, black hair, very long hair, green eyes, small breasts, flat chest, fang, ...,
  1boy, faceless male, penis, erection, size difference, height difference, doggystyle, from behind, full body, bedroom, night
  ```

  **错误格式**（男主 tag 与女性混写）：
  ```
  ❌ 错误:
  2girls, edelgard (isekai maou), dark skin, ..., shera l. greenwood, blonde hair, ..., 1boy, faceless male, penis, ...
  ```
  男主 tag 夹在两个女性之间，模型容易丢失男主或错误分配属性。

  **错误格式**（缺少 1boy）：
  ```
  ❌ 错误:
  2girls, edelgard (isekai maou), dark skin, ..., shera l. greenwood, blonde hair, ..., penis, erection, ...
  ```
  缺少 `1boy, faceless male`，模型可能将 `penis` 分配给某个女性角色。

  **强制检查清单**（每个多角色页输出前）：
  - [ ] `1boy, faceless male` 是否存在于 tag 行？
  - [ ] 男主 tag 是否独占一行（或在所有女性角色之后）？
  - [ ] `penis` 是否仅出现在男主 tag 区块内？
  - [ ] 每个女性角色的外观属性是否仅在该角色的 tag 区块内？
- **多女主 caption 分离规则**：`2girls` 场景的 caption 必须按角色分段写，格式：
  ```
  大瞬: <大瞬的动作描写和体感>
  小瞬: <小瞬的动作描写和体感，强调其专属服装>
  男主: <男主的动作描写和体感>
  ```
  - 每个角色分段**必须**描写其性行为动作和身体感觉
  - 角色服装材质（如 bodystocking 的透明紧绷感、手套的丝滑感）必须在对应角色的分段中描写
  - 分段顺序：女1 → 女2 → 男主（按画面中从左到右或从主到次的顺序）
  - 单人页（1girl + 1boy）不受此限，但仍需使用角色名而非纯代词

## 5.2 文件名命名规则

每页文件名必须符合以下格式，便于阅读和排序：

```
<项目前缀><3位序号>-<2-4字中文内容梗概>.txt
```

**规则**：
| 要素 | 说明 | 示例 |
|------|------|------|
| **项目前缀** | 英文缩写或中文角色名，全项目统一 | `SS`（瞬）、`AM`（阿米娅）、`NS`（妮芙苏苏洛）、`CF`（长风）|
| **3位序号** | 从 001 开始连续编号 | `001`, `035`, `060` |
| **分隔符** | 序号和梗概之间用半角连字符 `-` | `-` |
| **中文梗概** | 2-4 字概括该页核心行为+场景，不重复前页 | `口交午茶` ❌ → `茶道足奉` ✅ |
| **文件后缀** | `.txt` | |

**内容梗概选词参考**：
```
体位: 正常/骑乘/后入/汤匙/压腹/莲花/蛙位/抱起/蹲位/侧位/坐位
行为: 口交/深喉/手交/足交/乳交/肛交/腿交/性交/舔阴/接吻/温存
道具: 绳缚/蒙眼/冰戏/墨戏/毛笔/折扇/茶道/灯笼
情绪: 初识/试探/挑逗/激情/深情/离别/重逢/温存
场所: 昼/暮/夜 + 寝/厨/庭/廊/台/浴/厅/桥
```

**反面示例**（禁止）：
| 错误 | 原因 |
|------|------|
| `CF1-茶.txt` | 序号不足 3 位 |
| `CF01-茶道足交play.txt` | 梗概超过 4 字 |
| `CF001.txt` | 没有梗概 |
| `amy001-茶道.txt` | 前缀与项目不一致 |
`[caption]` 中**严禁**使用小说原始角色名（如 林琪、林茉、林文）。**必须**使用 `character map.md` 中定义的映射名（Danbooru 角色名）。

```
✅ 正确: Mutsuki sits on the couch, white stirrup socks taut on Mutsuki's feet, watching the male play.
✅ 正确: Chise descends the stairs in a pure white dress, white stirrup socks gripping Chise's arches.
✅ 正确: The male holds Chise's belly as the two bodies drift back to sleep.
❌ 错误: Lin Qi sits on the couch in her black stirrup socks, watching him play.
❌ 错误: Lin Wen holds her belly...
❌ 错误: 林茉坐在沙发上...
```

> 理由：ANIMA3 将 caption 文本送入 LLM 图像生成，使用映射名可确保角色一致性。本名仅用于文件名和 `character map.md`。

**《邻家妻子》映射表（参考）**：
| 小说本名 | Caption 映射名 | Danbooru Tag |
|---------|---------------|-------------|
| 林琪 | **Mutsuki** | `mutsuki \(flowery charms\) \(blue archive\)` |
| 林茉 | **Chise** | `chise \(blue archive\)` |
| 林文 | **he/him/Daddy** | `faceless male` |
| 林璇 | **Hibiki** | `hibiki \(blue archive\)` |
| 林欣 | **Cherino** | `cherino \(blue archive\)` |
| 林竹 | **Natsu** | `natsu \(blue archive\)` |

其他作品请参照各自的 `character map.md`。

### 多人标签强制规则

当页面包含2个及以上女性角色时，tag 行**必须**包含：
- `2girls` — 两人同框
- `threesome` — 三人场景（含男主）
- `ffm threesome` — 女+女+男三人
- `mother and daughter` — 母女关系
- `incest` — 近亲关系

> 例外：当第二位女性仅出现在电话/照片中而**非物理同框**时，tag 行不得包含其角色 tag，不得使用 `2girls`/`threesome`/`ffm threesome`，应使用 `1girl` + 单人角色 tag。

### Caption 角色标注规则

单画面构图的 `[caption]` 中，**必须始终使用角色名**（映射名如 Mutsuki/Chise 等），严禁使用任何代词（she/her/he/him/his）：

```
✅ 正确: Mutsuki sits on the male's lap, Mutsuki's white stirrup socks taut against the soles of Mutsuki's feet. Mutsuki looks up at the male with a teasing smile.
✅ 正确: Chise watches from the doorway, the white dress on Chise fluttering slightly.
✅ 正确: The male holds Chise's belly as the two bodies drift back to sleep.
❌ 错误: She sits on his lap.（代词指代不清）
❌ 错误: Mutsuki sits on his lap in her black stirrup socks, watching him play.（混用 her/him）
❌ 错误: 仅开头交代角色名后后续全用 she/her（角色混淆风险）
```
> 每条 caption 中每个角色的每次出场都必须用角色名或标识语指代，不可使用代词。

## 5.3 ANIMA3 Tag 插槽顺序

```
count/gender → series\(角色/作品\) → appearance\(发/眼/特殊器官\) → clothing\(服装/配件/裸露\) → pose/sex\(姿势/性行为\) → expression\(表情\) → camera\(镜头\) → scene\(场景\) → detail\(细节补充\) → NL supplement\(自然语言补述\)
```

### 各槽位说明

| 槽位 | 内容 | 示例 |
|------|------|------|
| count | 人物计数 | `1girl, 1boy` / `2girls` / `solo` |
| series | 作品+角色标签 | `mobius \(honkai impact 3rd\)` |
| appearance | 外貌特征 | `green hair, very long hair, heterochromia, snake eyes, fang` |
| clothing | 服装、配饰、裸露 | `latex, bodysuit, thighhighs, arm gloves, high heels` |
| pose/sex | 姿势、性行为类型 | `missionary, fellatio, footjob, doggystyle` |
| expression | 表情 | `ahegao, blush, closed eyes, tongue out, open mouth, sweat` |
| camera | 镜头方向和景别 | `from side, from front, from above, close-up, full body, cowboy shot` |
| scene | 场景和时间 | `bedroom, bathroom, laboratory, night, daytime` |
| detail | 细节补充 | `wet, shiny, dripping, cum on body, glowing, steam` |
| NL | 自然语言补述 | tag 行末尾一段英文描述（逗号前仍是 tag 语法，最后一段纯英文） |
## 5.4 强制标签覆盖规则（每次输出前逐条检查）

### A. 角色外观标签全覆盖
每页必须包含角色全套外观标签，不得因上一页已写而省略：
| 类别 | 强制标签 | 梅比乌斯示例 |
|------|---------|-------------|
| 发色/发型 | hair color + length + style | `green hair, very long hair` |
| 瞳色/瞳形 | eye color + special shape | `heterochromia, snake eyes` |
| 特殊器官 | fangs, tail, scales | `fang` |
| 体型 | breast size, height | `small breasts` |
| 服装 | full outfit described | `latex bodysuit, stirrup legwear, toeless legwear, elbow gloves, high heels` |

**禁止**：因角色已在前页出现过就省略服装/外貌标签。生成模型无"跨页记忆"。

### B. 场景-行为标签全覆盖
| 场景 | 必须包含的标签集 |
|------|----------------|
| 足交 | `uxsFJ, under-stirrup footjob, footjob, stirrup legwear, unworn shoes` + 体位（`two-footed footjob`/`one-footed footjob`）+ `sole focus`/`foot focus`/`presenting own foot` |
| 口交 | `fellatio, deepthroat, irrumatio, oral` + 体位（`kneeling`/`lying`/`sixty nine`）+ 需要时 `cum_in_mouth, swallowing` |
| 肛交 | `anal, anal penetration, anal sex` + 体位 + `cloaca`（梅比乌斯特有）+ 内射时 `anal creampie, cum inside, cum inflation` |
| 阴道/开宫 | `vaginal, insertion, deep penetration, cerpe, cervical penetration, uterus, stomach bulge, bulge` + `cloaca`（梅比乌斯特有）+ `defloration`（初入）+ `vaginal creampie, cum inside` |
| 足交+开宫过渡 | 过渡页不加任何 LoRA 触发词，仅写常规体位标签 |
| 手指插入 | `fingering, cloaca, fingers inside` |
| 怀孕/分娩 | `pregnant, pregnancy, giving birth, labor, contractions` + `cloaca`（梅比乌斯特有）|
| 母子/轮回 | `incest, mother and son, parent and child, age difference, time loop, mind break` |
| 死亡/缩小 | `dying, death, shrinking, resurrection, time loop` |

### C. 表情-身体反应标签逐页递增
不在每页都写相同表情。按剧情阶段递增：
| 阶段 | 表情标签 | 身体反应标签 |
|------|---------|-------------|
| 冷静/控制 | `smirk, closed eyes, looking down` | — |
| 愉悦/享受 | `blush, parted lips, closed eyes` | `heavy breathing` |
| 兴奋/强烈 | `open mouth, flushed, sweat` | `gripping, arching back, wet` |
| 高潮/崩溃 | `ahegao, rolled eyes, tongue out, tears` | `trembling, twitching, convulsing, crying, drooling` |

**强制规则**：表情标签必须与 caption 描述一致。caption 中写了"the female screams"则标签必须有 `open mouth`；写"the female cries"则标签必须有 `tears`。

### D. 镜头/景别标签全覆盖
| 画面内容 | 强制镜头标签 |
|---------|-------------|
| 全身展示 | `full body` + 方向（`from side`/`from front`/`from behind`） |
| 半身/牛仔 | `cowboy shot` + 方向 |
| 面部特写 | `close-up, face focus` + 方向 |
| 局部特写 | `close-up, <部位> focus`（`foot focus, penetration focus` 等） |
| 动态画面 | 需要时加 `motion lines`/`emphasis lines`/`speed lines`（按 §4.6） |

**禁止 `close-up` + `full body` 同页使用**。

### E. 特殊关系标签
| 剧情阶段 | 强制注入标签 |
|---------|-------------|
| 母亲真相揭露前 | 不写 `incest`/`mother and son`（剧透） |
| 母亲真相揭露后 | `incest, mother and son, parent and child, age difference`（立刻注入，此后全部包含） |
| 权力反转前 | 可写 `domination, submission`（梅比乌斯 dom） |
| 权力反转后 | 可写 `domination reversal, overpowered` |

### F. Tag ↔ Caption 强制对应规则
**每行 tag 必须在 caption 中有对应的自然语言描写**，反之亦然：
| Tag | Caption 必须描写 |
|-----|-----------------|
| `footjob, under-stirrup footjob, uxsFJ` | 脚包茎的具体动态、袜底勒入感 |
| `presenting own foot` | 女性主动抬起/展示自己的脚，足底朝向镜头或阴茎，强调足部的色情展示姿态 |
| `foot focus, sole focus` | 镜头聚焦于足部/足底，足底纹理、趾甲、足弓弧度清晰可见 |
| `cervical penetration, stomach bulge` | 龟头顶入宫颈、小腹隆起、触摸隆起 |
| `cum inflation, pregnant belly` | 腹部胀满感、精液量、手按腹部 |
| `anal creampie, cum inside` | 内射的感觉、流出的精液 |
| `ahegao, rolled eyes, tongue out` | 失神、白眼、流涎的具体描写 |
| `tears, crying` | 眼泪流下、抽泣 |
| `stirrup legwear, unworn shoes` | 袜底勒入、鞋脱一旁的具体状态 |
| `elbow gloves, sheer gloves, lace gloves` | thin bridal elbow gloves, delicate lace-trimmed sheer fabric, not leather or latex |
| `bridal gauntlets, bridal legwear` | translucent bridal pantyhose, sheer thin hosiery, not rubber or plastic |
| `mismatched legwear, asymmetrical legwear` | left leg in sheer white vertical-striped pantyhose while right leg in pale violet to white gradient thighhighs, deliberately mismatched, both with soles exposed by stirrup legwear |
| `single leg pantyhose, single thighhigh` | one leg covered in sheer front-seamed pantyhose, the other in argyle stocking, both with stirrup legwear exposing soles |
| `vertical-striped thighhighs` | vertical stripes running up the thighs, sheer fabric with stirrup bands gripping the arches |
| `striped thighhighs` | horizontal stripes wrapping around the thighs, stirrup legwear exposing the soles |
| `seamed legwear` | classic back-seam running up the back of the legs, stirrup legwear taut against the soles |
| `front-seamed pantyhose` | front seam visible along the shins, stirrup bands holding the sheer fabric in place |
| `frilled thighhighs` | delicate frills at the top of the thighhighs, stirrup legwear gripping the arches |
| `lace-trimmed pantyhose` | lace trim at the waist or cuffs, sheer pantyhose with stirrup bands |
| `mismatched gloves, asymmetrical gloves` | left hand in white lace elbow gloves mirrors the right leg in white thighhighs, while the right hand in pale violet to white gradient gloves mirrors the left leg in gradient stirrup pantyhose |
| `frilled gloves` | delicate frills at the glove cuffs, sheer fabric extending to the elbows |
| `ribbon-trimmed gloves` | satin ribbon trim at the glove cuffs, matching the lace trim on the thighhighs |
| `cross-laced gloves` | cross-laced ribbon detail on the back of the hands, sheer fabric |
| `seamed gloves` | back-seam detail running up the gloves, matching the seamed legwear on the legs |
| `front-seamed gloves` | front seam visible along the gloves, mirroring the front-seamed pantyhose |
| `gradient gloves` | gradient color fading from pale violet to white on the gloves, mirroring the stirrup pantyhose |
| `vertical-striped gloves` | vertical stripes on the gloves matching the vertical-striped thighhighs |
| `layered gloves` | short lace gloves layered over sheer elbow gloves, double sheer texture |

**禁止 caption 中出现 tag 行未写的内容**（如 caption 写"the female's belly bulges"但 tag 行无 `stomach bulge`/`bulge`）。

### G. 场景标签完整性
每页必须包含 `laboratory` 场景标签（实验室情节）+ 时间段（`night`/`daytime`）。过渡到外界（4th wall break）时切换为 `bedroom, night, modern`。

### H. 体型差与巨根标签强制规则
当女性角色为 **loli / petite / small stature** 体型时，必须添加体格差标签以突出体型对比：
| 标签 | 位置 | 说明 |
|-----|------|------|
| `size difference` | boy 行或 girl 行 | 体格差，突出女性娇小 vs 男性正常/高大的对比感 |
| `height difference` | boy 行或 girl 行 | 身高差，强化萝莉感的画面比例 |
| `penis` | boy 行 | 阴茎标签，默认普通尺寸，不加 `large`/`huge` 修饰 |

**注意**：`size difference`/`height difference` 仅当作品刻意强调体型差时才使用，非强制。

**例外**：当女性角色为成人/正常体型的作品（如《邻家妻子》的 Mutsuki、Chise）时，不需要 `size difference`/`height difference`。

---

#### H-2. 极致萝莉/幼女 tag 组合规则（2025-06 实测）

当需要将女性角色推向 **幼女/极致萝莉**（约 9 岁）体型时，以下为 Danbooru tag 的最佳组合和反模式：

### 女方 tag 选择

| Tag | post count | 推荐度 | 说明 |
|-----|-----------|--------|------|
| `loli` | 201k | ✅ 必需 | 萝莉核心tag，所有幼女场景必须 |
| `flat chest` | | ✅ 必需 | 扁平胸部，强调未发育 |
| `child` | 75k | ❌ 禁用 | 会导致模型额外生成一个小孩角色，画面出现 2 人。幼女年龄感通过 `loli` + caption 年龄指定实现 |
| `age regression` | 1.9k | ✅ 可选 | 幼女化/年龄倒退，适合同人创作中把角色画小的场景 |
| `age difference` | | ✅ 必需 | 女方幼小 vs 男方成年的年龄差对比 |
| `petite` | | ⚠️ 慎用 | 偏"纤细成熟少女"而非幼女；healthyman 等 幼女系画师不用此 tag |
| `narrow waist` | | ❌ 禁用 | 窄腰暗示发育后体型，与幼女/萝莉的身体特征矛盾。幼女的腰身应不明显/直筒型 |

### 男方 tag

| Tag | post count | 推荐度 | 说明 |
|-----|-----------|--------|------|
  | `faceless male` | | ✅ 默认 | 男主默认无脸 |
  | `kanie seiya` / `藤丸立香` 等男主名 | | ✅ 推荐 | 故事板有指定男主时（即非 NTR 场景），boy tag 行使用男主角色名（如 `kanie seiya`/`ritsuka fujimaru`）+ `faceless male`，明确男主身份。除非用户指定"路人/NTR"，否则默认使用原作男主名 |
| `size difference` | | ✅ 必需 | 体型差，强调女方娇小 |
| `height difference` | | ✅ 必需 | 身高差 |
| `muscular male` | 133k | ✅ 推荐 | 肌肉男体型，与幼女形成视觉反差 |
| `thick thighs` | 150k | ✅ 推荐 | 粗腿，强化男方厚重感 vs 女方纤细 |
| `thick arms` | 2k | ✅ 推荐 | 粗手臂，强化男方力量感对比 |
| `broad shoulders` | 1.7k | ✅ 可选 | 宽肩，进一步拉大视觉对比 |
| `large hands` | 2.8k | ✅ 可选 | 大手，握持女方时突出娇小感 |
| `mature male` | 44k | ✅ 可选 | 成熟男性，与幼女形成年龄差视觉线索 |

> 参考画师：**healthyman** — 常用 tag 为 `loli` + `flat chest` + `age difference`，**不**用 `petite`/`narrow waist`/`child`。效果已经足够幼。

### Blue Archive 小瞬（shun(small)）对比参考

Danbooru 上 shun(small) 的常用 tag：
`flat chest, loli, shun (blue archive), shun (small) (blue archive)`
无需 `child` 或 `age regression`，角色独立 tag 已隐含年龄设定。

### Caption 年龄直接指定

仅在 tag 行加 `loli` 不够，需在 caption 文本中直接写明年龄（禁加 `child` tag，会导致模型额外画出一个小孩）：

```
# 写法（JS）：
pg.cap.replace(/\bMash\b/, "The nine-year-old Mash")
# 效果："The nine-year-old Mash stands at the door..."

# 多人组合页用"nine-year-old"（不加 The）：
c.cap.replace(/\bMash\b/, "nine-year-old Mash")
# 效果："The armored nine-year-old Mash and..."
```

原则：
- 文本中第一个角色名 → 插入 `the nine-year-old` / `nine-year-old`
- 确保语法通顺（检查 "The the" 重复冠词）
- caption 年龄 + tag 行 `loli` 双层锁定年龄感（禁加 `child` tag）

# 六、标签验证

## 6.1 查询 Danbooru Tag 数据库

```sql
-- 验证标签存在性
SELECT name, cn name, post count FROM tags WHERE name = '<tag name>';

-- 模糊匹配
SELECT name, post count FROM tags WHERE name LIKE '%keyword%' ORDER BY post count DESC LIMIT 10;
```

### 数据库位置
`Workflow/wild/script/ffdkj-Danbooru Tag-Chinese-English-Translation-Table/tag.sqlite`

## 6.2 验证策略

- **角色系列 tag**：确认匹配或使用近似标签；对不存在的标签使用最近似的替代
- **性行为 tag**（`fellatio`, `vaginal`, `footjob` 等）：验证存在后用
- **特殊关系 tag**（`mother and daughter`, `incest`, `age difference`）：验证后用
- **服装/配饰 tag**：优先使用数据库中有记录的术语
- **身体特征 tag**：`snake eyes`, `fang`, `heterochromia`, `green hair` 等

### 常见作品系列 tag 对照表（Danbooru）

| 作品 | Danbooru Tag | 备注 |
|------|-------------|------|
| 崩坏3 | `honkai impact 3rd` 或 `honkai 3rd` | 主标签 |
| 原神 | `genshin impact` | 主标签 |
| 蔚蓝档案 | `blue archive` | 主标签 |
| 碧蓝航线 | `azur lane` | 主标签 |
| 绝区零 | `zenless zone zero` | 主标签 |
| Fate | `fate` 或 `fate grand order` | 视具体作品 |
| 星穹铁道 | `honkai star rail` | 主标签 |

### 常见角色 tag 构造

`<角色英文名> \(<作品tag>\)`

**重要规则：** 所有的 `\(\)` 在标签内容中必须使用 `\` 转义。例如 `francesca prelati \(fate\)`、`ishtar \(first ascension\) \(fate\)`、`mobius \(honkai impact 3rd\)`。标签文件名中的 `\(\)` 不需要转义，仅文件内容中的 `\(\)` 需要。

如：`mobius \(honkai impact 3rd\)`, `laffey ii \(azur lane\)`, `ganyu \(genshin impact\)`

---