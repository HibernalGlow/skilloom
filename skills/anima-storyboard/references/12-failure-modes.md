# 补充篇 B：Anima 失败模式与互斥标签矩阵（输出前排障）

> 本节的**方法论**吸收自外部 Anima 生图技能（详见 `11-external-skills.md` 的出处表），
> 文本为本技能自撰并已按**银月 Base INT8 + 故事板分页格式**改写。
> 用途：每页 `[tags]`/`[caption]` 定稿前过一遍，把"已知会崩的画法"提前掐掉。

---

## 12.1 单帧失败模式速查（E001–E011）

| 编号 | 症状 | 根因 | 修正（改标签 / 改 caption） |
|------|------|------|---------------------------|
| **E001** | 画面正中一个小人，四周大片空白 | 写了 `full body` 又配空背景；没主语占幅 | 改用 `upper body` / `cowboy shot` 控制占幅；背景只留 2~3 个 tag；caption 写明主体占据画面视觉中心 |
| **E002** | 双人并排各看各的，零交集 | 只堆了两个角色 tag | 至少给一处绑定：`looking at another` / `holding hands` / 共享道具；caption 写明视线与接触关系 |
| **E003** | 仰俯角下脸崩（下巴过尖、眼睛歪） | 极端角度 + 简单背景 + 本体是小脸 | 降角度强度：`slight low angle` 取代极端角度；先降角度再谈修脸，不要硬扛 |
| **E004** | 前景角色的头/手正好挡住主角的脸 | 3 人以上没写层次 | 主角放中景；前景角色只露肩/背影；caption 写死层次（主角居中景，前景为失焦剪影） |
| **E005** | 背景比主体抢眼，主体被淹没 | 背景 tag 过多（≥4 个就容易抢戏） | 背景减到 2~3 个 tag；用暗背景 + `rim light` + 浅景深；把细节预算还给主体 |
| **E006** | 人物轮廓线与背景线刚好相切，视觉粘连 | 没有明确"重叠"或"分离" | 二选一说清楚：要么明确前后遮挡，要么明确留空隙；caption 写"保持明确间隔" |
| **E007** | 人物背光但背景晴空万里；窗光在左，树影在右 | 一景多光源方向 | 一个场景只定义一个主光方向；背光必须补面部补光或轮廓保护；`backlighting` 不与正午强光混用 |
| **E008** | 3 人以上肢体归属混乱，分不清谁的手在谁身上 | 多处身体接触交叉 | 3 人最多写两组身体接触；caption 逐条写死归属（左女的手在中间女腰上……）；其余四肢保持分离 |
| **E009** | 战斗场景在笑、拥抱场景苦脸 | 表情与场景情绪不匹配 | 定稿后通读一遍：场景情绪 ↔ 表情是否违和 |
| **E010** | 人物比例与环境失调（人只到门框一半高、比桌子矮） | 环境元素无参照尺度 | caption 写死比例参照：桌沿到腰、门框明显高过头顶 |
| **E011** | 极端比例导致解剖崩坏 | 幼小体型 + 巨乳 / 极细腰 同页 | 不要全身同框；改用胸部以上构图；极端比例与写实解剖本质冲突，**选其一**。<br>⚠️ 本技能本就**禁止胸围标签**，E011 主要防"用其他标签间接堆胸围" |

---

## 12.2 互斥标签矩阵（组装前必过）

以下标签对**不可同页出现**。命中即为硬错误，必须二选一。

### 视角 / 景别

| A | B | 原因 |
|---|---|---|
| `from front` | `from behind` | 物理矛盾 |
| `from above` | `from below` | 物理矛盾 |
| `looking at viewer` | `facing away` | 视线矛盾 |
| `pov` | `full body` | POV 看不到自己全身 |
| `close-up` | `full body` | 景别矛盾（本技能 §5.4-D 已列） |
| `closed eyes` | `looking at viewer` | 视线矛盾 |

### 身份 / 关系

| A | B | 原因 |
|---|---|---|
| `solo` | `1boy` / `hetero` / `yuri` | 单人不存在互动 |
| `femdom` | `male-on-female rape` | 主导方冲突 |
| `sleeping` / `unconscious` | `looking at viewer` | 无意识不可能直视 |
| `blindfold` | `heart-shaped pupils` / `rolling eyes` | 蒙眼看不清眼 |

### 服装 / 状态

| A | B | 原因 |
|---|---|---|
| `completely nude` | 任何具体服装 tag | 全裸不穿衣 |
| `pantyhose` / `thighhighs` | `barefoot` | 穿了丝袜不可能光脚（除非 `torn pantyhose` + 脚部撕开） |
| `blindfold` | `glasses` | 物理冲突 |
| 内衣套装（`cat lingerie` / `lace lingerie` / `babydoll` / `negligee` / `chemise`） | `no panties` / `bottomless` | 套装隐含包含内裤，模型优先解析套装而忽略暴露标签。需暴露则**拆成单件**：`cat bra` + `no panties` |

> **不算互斥**：外衣/制服（`maid outfit` / `school uniform` / `bunny suit` / `sailor uniform`）与
> `no panties` / `bottomless` 完全兼容——穿制服不穿内裤是合理场景。

### 动作 / 体位

| A | B | 原因 |
|---|---|---|
| `standing sex` | `lying` / `on back` | 体位矛盾 |
| `missionary` | `doggystyle` | 不可能同时两个体位 |
| `cowgirl position` | `prone bone` | 体位矛盾 |
| `fellatio` | `cunnilingus`（同一人执行） | 嘴只有一张 |

---

## 12.3 细节标签过度（同部位状态标签）

同一身体部位堆叠**互斥**状态标签，会让模型过度渲染该部位并产生畸形。

**铁律**：每部位细节标签 ≤2 个，且**状态必须一致**。

| 部位 | 矛盾组合 | 原因 |
|------|---------|------|
| 脚趾 | `spread toes` + `toe scrunch` / `toes curling` | 舒展 vs 蜷缩 |
| 脚趾 | `spread toes` + `feet together` | 分趾需空间，合拢即压缩 |
| 手指 | `spread fingers` + `clenched fist` / `gripping` | 张开 vs 握拳 |
| 胸部 | `bouncing breasts` + `breasts squeeze together` | 弹跳 vs 挤压 |
| 嘴 | `open mouth` + `clenched teeth` / `closed mouth` | 张开 vs 闭合 |
| 眼 | `rolling eyes` + `looking at viewer` | 翻白眼 vs 直视 |
| 腿 | `spread legs` + `legs together` | 分开 vs 并拢 |
| **足部整体** | 3 个以上足部标签（`foot focus` + `footjob` + `toe scrunch` + `spread toes`） | 过度细化 → 脚趾/脚掌畸形 |

**判定原则**：数量不是问题，**状态一致性**才是。
`barefoot` + `feet focus` + `soles` + `toe scrunch` 四个兼容标签没问题；`spread toes` + `toe scrunch` 两个就已经矛盾。

> ⚠️ 足交页（本技能高频玩法）必须重点过这一条：足部状态标签最容易随手堆。

---

## 12.4 手 / 足 / 肢体崩坏防护

- **正向轻推**：适度强调 `nail` 或 `finger detail`，手脚更不容易坏（不要过度，避免喧宾夺主）。
- **负面参考**（排障用，不写入 story 页）：
  `bad hands, bad arm, bad knees, missing fingers, extra fingers, anatomical nonsense, bad perspective, bad anatomy`
- **兽耳娘防变异**：排障时负面加 `anthro`。
- **手部接触 / 持物页**：必须同时防 `fused fingers`、`fused hands`、`malformed hands`。
- **3 人以上页**：必须防 `merged bodies`、`extra arms`、`cloned face`、`same outfit`、`duplicate`。

---

## 12.5 多角色属性污染（本技能 §5.4 已有，此处补强）

- 每个角色的**发色/瞳色/服装**必须绑定到本角色所属的 `1girl`/`1boy` 行，禁止跨行混写。
- 角色 A 的固有外观标签不得出现在角色 B 区块**附近**（模型会把邻近 tag 归给最近的主体）。
- 3 人以上：每个角色只能有 **2~4 个**身份锚点，锚点多反而互相覆盖。
- caption 中**绝对禁止代词**（`she`/`her`/`he`/`his`），一律用角色映射名——这条同时也是防串脸的语言层保险。

---

## 12.6 定稿自检（每页逐条打勾）

| # | 检查项 | 通过标准 |
|---|--------|---------|
| 1 | 人数一致性 | `count/gender` 与 caption 中的角色数一致，无 `1boy, 2boys` 矛盾 |
| 2 | 互斥矩阵 | §12.2 全部通过 |
| 3 | 同部位状态 | §12.3 每部位 ≤2 且状态一致 |
| 4 | 重复标签 | 同一标签不出现两次（强调靠权重与位置，不靠重复） |
| 5 | 场景物理合理性 | 场景与动作物理兼容（如 `underwater` 不配 `cigarette`） |
| 6 | 视角 / 光源唯一 | 一个场景一个主光方向；E007 |
| 7 | 占幅 | 主体占画面有足够比例；无 E001 |
| 8 | 归属绑定 | 多角色/多格有前缀或 caption 绑定；无 E008 |
| 9 | 本技能规则 | 下划线已替换、括号已转义、关键标签已加权重、无胸围标签、颜色为白/浅色 |
