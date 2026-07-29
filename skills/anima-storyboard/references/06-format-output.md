<!-- Extracted from SKILL.md §九、格式转换：批量分页输出 -->

# 九、格式转换：批量分页输出

## 9.1 目录结构

```
Workflow/wild/storyboard/<中文作品名>/
├── character map.md
└── pages/
    ├── IM001—a01谢拉-口交奉仕.txt
    ├── IM002—a01谢拉-深喉特写.txt
    ├── ...
    └── IM253—m41全员-八中出.txt
```

**⚠️ 文件夹命名强制中文**：storyboard 下的作品文件夹必须使用**中文名称**，不得使用英文或罗马音。

| 错误写法 | 正确写法 |
|---------|---------|
| `storyboard/isekai_maou/` | `storyboard/异世界魔王与召唤少女/` |
| `storyboard/kanColle/` | `storyboard/舰队Collection/` |
| `storyboard/fate/` | `storyboard/Fate/`（已有公认缩写可保留）|
| `storyboard/konosuba/` | `storyboard/为美好世界献上祝福/` |

**中文名来源**：萌娘百科/Moegirl 上的官方中文译名，或作品本身的中文官方名。无公认译名时，取作品最常用的中文称呼。

## 9.2 命名规则

`<故事缩写><NNN>—<am编号><角色中文名>-<梗概>.txt`

- **故事缩写**：该 story 统一的英文前缀（如 `KM`、`TB`、`AD`），同一 story 下所有角色共用同一缩写，避免排序混乱
- **am编号**：单人页用 `a` 前缀 + 两位角色编号（`a01`=角色1、`a02`=角色2…），组合页用 `m` 前缀 + 两位组合编号（`m04`=双人组、`m05`=三人组…）
- `—` 为 em dash，连接页码和 am 编号
- `-` 连接角色名和梗概
- NNN 补零至三位数（从 001 开始），**全 story 连续，跨角色不重复**
- 梗概使用中文，2-6 字概括本页核心内容
- **文件按页码数字自然排序**，不可出现重复页码
- **Caption 仅支持英文**：文件名可以用中文（角色名+梗概），但 `[caption]` 内容必须为纯英文段落。Caption 会被送入 LLM 图像生成模型，中文 caption 会导致生成失败或乱码。禁止在 caption 中出现中文汉字（角色名在 caption 中必须使用 Danbooru 英文名）。
- **a/m 编号规则**：
  ```
  单人页: KM001—a01克洛伊-召唤.txt      ← a01-a06 对应6个角色
  双人组: KM181—m04群-克洛伊克洛姆双含.txt  ← m04 双人组合
  三人组: KM256—m05群-克洛伊克洛姆丝朵拉酱三含.txt ← m05 三人组合
  四人组: KM280—m06群-克洛伊蒂芙尼普拉兹瑪魅魔妈妈四含.txt ← m06 四人组合
  全员:   KM292—m07群-克洛伊克洛姆普拉兹瑪魅魔妈妈丝朵拉酱蒂芙尼六含.txt ← m07 全员
  ```

**⚠️ 梗概多样性要求**：每页的中文梗概必须独特，禁止使用模板化的 `<形态><玩法>` 格式（如 `默认手交`→`默认口交`→`默认深喉`）。梗概应描述具体场景和情绪，而非机械的动作分类。参见 §9.3 严禁脚本循环。

## 9.3 严禁脚本循环与模板轮换

**⚠️ 核心禁令：禁止使用脚本/代码批量生成故事板页面。**

以下行为**严格禁止**：

| 禁止行为 | 说明 | 反面案例 |
|---------|------|---------|
| 形态×玩法笛卡尔积循环 | 每个形态都写同样的8个玩法（手交/口交/深喉/骑乘/后入/传教/内射/后戏）| 光辉系舰船：默认手交→默认口交→默认深喉→…→婚纱手交→婚纱口交→… |
| 双人组合模板复制 | 每对组合都用相同的10页模板（共侍/双口/深喉/骑乘/后入/夹心/双传/内射/磨镜/同眠）| 每对双人都是同样的页面序列 |
| 代码批量写入 | 用 JS/Python 循环 + 模板字符串生成所有页面 | `forms.forEach(f => actions.forEach(a => write(...)))` |
| 固定玩法序列 | 所有角色/组合都使用完全相同的玩法顺序 | 每个组合都是：口交→骑乘→后入→传教→内射 |

**正确做法**：每一页必须**手写**，确保：
1. **玩法不重复**：相邻页不使用相同玩法，同一组合内不出现重复的体位/场景
2. **情绪有弧线**：从羞涩→信任→探索→激情→归属，不是零散场景堆砌
3. **场景有变化**：卧室/浴室/户外/桌边/窗前等，不是全在同一张床上
4. **角度有切换**：full body → close-up → cowboy shot → from side → from behind 循环
5. **角色有个性**：不同角色的 caption 描述不同的反应和性格，不是千篇一律

**反面教材（光辉系舰船）**：
```
UI001-默认手交.txt  ← 形态1 × 玩法1
UI002-默认口交.txt  ← 形态1 × 玩法2
UI003-默认深喉.txt  ← 形态1 × 玩法3
...
UI009-改造手交.txt  ← 形态2 × 玩法1（完全重复玩法序列）
UI010-改造口交.txt  ← 形态2 × 玩法2
...
UI017-婚纱手交.txt  ← 形态3 × 玩法1（再次重复）
```
300页中有200+页是模板循环的产物，每页的 tag 和 caption 高度雷同，仅替换服装标签。**这是故事板质量的最差实践。**

## 9.4 角色服装形态轮换

每个角色定义多个服装形态（`forms: ['default', 'bikini', 'leotard', ...]`），在单人页和组合页中**自然穿插**，而非机械轮换。

**⚠️ 核心原则：形态变化服务于剧情，不是数学公式。**

**禁止的机械轮换**：
```
❌ 前10页default → 中间10页bikini → 后10页leotard（等分块轮换）
❌ A角色 forms[i % len], B角色 forms[(i+1) % len]（取模公式）
```

**正确做法**：
- 根据小说剧情决定何时换装（如：日常→海滩场景→换泳装；战斗→受伤→换绷带装）
- 同一组合内不同角色可穿不同服装，但变化要有剧情理由
- 不是每个形态都要出场——如果形态与当前剧情无关，可以跳过
- 每页的 caption 必须自然提及服装（如 "Shera adjusts the green dress"），而非机械标注 "Shera wears the bikini outfit for this encounter"

**单人页规则**：
- 服装变化跟随剧情推进，不是按页数等分
- tag line 中增加该形态的专属标签
- caption 描述中自然体现服装（融入场景描写，非机械标注）

**组合页规则**：
- 同一组合内不同角色穿不同服装时，caption 必须描写服装差异（如对比材质、颜色、暴露度）
- 服装变化要有场景理由（如派对→礼服，温泉→浴衣，战斗→盔甲）

**形态标签映射表**：
```
default: ''（无额外标签）
bikini: 'bikini, white fishnet thighhighs, garter straps'
leotard: 'leotard, white leotard, white pantyhose, fishnet pantyhose'
babydoll: 'babydoll, white babydoll, white thighhighs, frills'
maid: 'maid apron, maid headdress, miniskirt, white thighhighs'
sweater: 'sweater, brown sweater, white thighhighs'
school: 'school uniform, white shirt, pleated skirt, white thighhighs'
```

## 9.5 丝袜规则

**⚠️ 关键标签必须加权重（强化规则）**：本节表中所有 `stirrup legwear`、`toeless legwear`、`elbow gloves`、`open-toe boots`、`open-toe shoes` 等关键服装标签在 [tags] 中**必须**按 SKILL.md §规则 3 的权重分级加权重（踩脚袜系列 1.3、鞋袜手套系列 1.2）。表内仅展示原始标签形式，实际输出时需包裹为 `(tag:权重)` 格式。

| 条件 | 推荐 | 说明 |
|------|------|------|
| 形态含 fishnet（网袜） | `stirrup legwear, toeless legwear` + 可选 `garter straps` | 网袜可与踏脚袜共存，也可加吊带 |
| 形态无 fishnet（非网袜） | `stirrup legwear, toeless legwear`（踏脚袜） | 不可加 `garter straps` |
| 比基尼形态 | `fishnet thighhighs` + `stirrup legwear` 或裸足 | 比基尼+踏脚袜是合法组合 |
| 露趾靴/鞋 | `open-toe boots` / `open-toe shoes` + 可选 `stirrup legwear` | 露趾鞋靴可独立使用，也可搭配踩脚袜，增强脚趾露出 |
| 角色自带靴/鞋（足交优先） | 将原有 `boots` / `shoes` 替换为 `open-toe boots` / `open-toe shoes` | 足交场景或露脚场景时，优先用露趾版替代普通鞋靴，以便展示脚趾动态 |
| 露趾短袜 | `toeless socks` + `stirrup legwear` 或 `toeless legwear` | 袜头开口露趾，适合足交场景 |
| 五指袜 | `toe socks` + `stirrup legwear` | 五指分开袜+踩脚，视觉新颖 |
| 绑带高跟 | `strappy heels` + `stirrup legwear` | 绑带与踩脚袜可组合使用 |

## 9.6 组合页面数量要求

对于 6 个角色的作品，组合页面的最低要求：

| 组合类型 | 数量 | 每组合页数 | 说明 |
|---------|------|-----------|------|
| 双人（2P） | 所有 C(6,2)=15 对 | 5页（含/骑/前后/足/内） | **必须全排列**，不可遗漏任何一对 |
| 三人（3P） | 至少 8 组 | 3页（含/轮换/浴） | 覆盖主要角色交叉 |
| 四人（4P） | 至少 4 组 | 3页（含/叠骑/浴） | 覆盖主要组合 |
| 全员（6P） | 1 组 | 3页（含/叠/浴） | 全体同框 |

**⚠️ 组合页禁止模板复制**：不同组合之间的 5 页不能使用相同的玩法序列。

| 错误做法 | 正确做法 |
|---------|---------|
| 每对组合都是：口交→骑乘→后入→传教→内射 | 不同组合使用不同的体位/场景/情绪组合 |
| 所有双人页 caption 句式相同 | 每对组合的 caption 反映角色个性差异 |
| A组合和B组合的 tag 行仅替换角色名 | 不同组合的 tag 行应有场景/道具/体位差异 |

**推荐差异化策略**：
- 根据角色性格选择体位（S角色→支配体位，M角色→被支配体位）
- 根据角色关系选择场景（闺蜜→浴室嬉戏，主仆→卧室调教）
- 根据角色外观选择道具（兽耳→尾巴play，机械→冰冷质感）

## 9.7 Caption 个性化要求

**禁止所有角色共用同一套 caption 模板。** 每个角色在同一场景下必须有独立的描述，反映其 Danbooru 玩法特征。

角色个性画像参考（以 kedama milk 为例）：

| 角色 | 氛围 | Caption 关键词 |
|------|------|---------------|
| Chloe（克洛伊） | 冷艳、疏离、异色瞳 | detached, clinical, measuring, raised eyebrow, cool composure |
| Chrome（克洛姆） | 活泼、阳光、犬系 | eager, bouncing, grinning, tail wagging, "more more more" |
| Plasma（普拉兹瑪） | 优雅、害羞、吸血鬼 | formal bow, hesitant, porcelain, shy smile, white gloves |
| Sakyumama（魅魔妈妈） | 母性、温暖、爱心元素 | warm, gentle, heart tail, knowing smile, "we have all night" |
| Sutora（丝朵拉酱） | 清纯、害羞、学生系 | nervous whisper, trembling, clumsy, burning face, tiny wave |
| Tiffany（蒂芙尼） | 暗黑、小S、皮革锁链 | smirk, challenge, o-ring choker, "Is this all?", appraising |

同一场景（如"诱惑"）下各角色 caption 必须不同，不可复用句式。

## 9.8 视觉多样性规则

### 不对称混搭规则

**不对称是选项，非强制。** 若角色原设为对称穿着（如连裤袜、长靴、校服等），保持原样，不必强行不对称。
改造时也禁止全部强制不对称——不对称仅作为增加视觉变化的可选手段。

不对称不只是颜色不同，可选的混搭方式：

| 左腿 | 右腿 | 标签 |
|------|------|------|
| 短袜 `ankle socks` | 过膝袜 `thighhighs` | `asymmetrical legwear` |
| 过膝袜 `thighhighs` | 连裤袜 `pantyhose` | `asymmetrical legwear` |
| 网袜 `fishnet thighhighs` | 裸足 `barefoot`/纯色袜 | `asymmetrical legwear` |
| 吊带袜 `garter straps` | 无吊带 | `asymmetrical legwear` |
| 长靴 `thigh boots` | 短靴/裸足 | `asymmetrical legwear` |
| 露趾靴 `open-toe boots` | 露趾鞋 `open-toe shoes` | `asymmetrical legwear` |
| 露趾短袜 `toeless socks` | 五指袜 `toe socks` | `asymmetrical legwear` |
| 系带靴 `lace-up boots` | 绑带高跟鞋 `strappy heels` | `asymmetrical legwear` |
| 连体衣 `bodysuit` 覆盖单腿 | 分体 | `asymmetrical legwear` + `single leg` |

手套同理：长手套 vs 短手套 vs 无手套 vs 网眼手套等。

关键标签：`asymmetrical legwear`、`asymmetrical gloves`、`single thighhigh`、`single leg pantyhose`、`mismatched legwear`

### 丝袜/手套配色选项

角色丝袜和手套可从以下样式中选择，**非强制**，按形态设计搭配：

| 样式 | 标签 | 适用场景 |
|------|------|---------|
| **纯白** | `white thighhighs, white gloves` | 默认形态，靠上衣区分 |
| **一彩一白** | `white thighhighs, <color> thighhighs, asymmetrical legwear` + `white gloves, <color> gloves, asymmetrical gloves` | 增加视觉变化 |
| **渐变+不对称** | `white thighhighs, gradient thighhighs, asymmetrical legwear` + `white gloves, gradient gloves, asymmetrical gloves` | 进阶变化 |
| **鱼网** | `white fishnet thighhighs, white gloves` | 原有/特殊形态 |

### 露趾鞋靴规则（Open-Toe Footwear）

**核心原则**：当角色穿了靴子（boots）或鞋子（shoes）时，优先考虑替换为露趾版 `open-toe boots` / `open-toe shoes`，特别是足交（footjob）场景：

| 原标签 | 替换为 | 适用场景 |
|--------|--------|---------|
| `black boots` | `(black open-toe boots:1.2)` | 角色穿黑色靴时替换 |
| `white boots` | `(white open-toe boots:1.2)` | 角色穿白靴时替换 |
| `brown boots` | `(brown open-toe boots:1.2)` | 角色穿棕靴时替换 |
| 其他 `boots` | `(<color> open-toe boots:1.2)` | 任意靴子都有露趾版 |
| `shoes` | `(open-toe shoes:1.2)` | 任意鞋子的露趾版 |
| `high heels` | 可选 `(open-toe heels:1.2)` | 高跟露趾版（较少用） |
| `unworn shoes` | 保留不变 | 鞋脱一旁的标签不动 |

**使用时机**：
- **足交/脚部场景必用**：任何涉及 footjob、toe job、foot focus 的页面，角色若有穿鞋靴必须改为露趾版
- **常规场景可选**：非足交场景也可用露趾版，增加脚趾露出和性感度
- **角色原设保留**：如果角色在作品原设中就穿 boot/shoe，可始终使用 open-toe 版替代，保持一致性

**权重**：`(open-toe boots:1.2)`、`(open-toe shoes:1.2)`、`(black open-toe boots:1.2)`（权重 1.2，有颜色前缀时整体包裹，防止 AI 画错为封闭鞋）

**NL 描述**：caption 中应描写脚趾露出：
- "toe claws peek out from the open toe of her boot"
- "bare toes visible through the open-toe design"
- "open-toe shoes leave her toes exposed for his touch"

颜色可参考形态主题，`asymmetrical legwear` 和 `asymmetrical gloves` 标签配对使用。

---

### 多人页防混淆

### 丝袜配色策略

| 策略 | Danbooru 标签 | 适用场景 |
|------|--------------|---------|
| **纯白** | `white thighhighs` | 默认形态，靠上衣/配饰区分角色 |
| **一彩一白（高低袜）** | `white thighhighs, <color> thighhighs, asymmetrical legwear` | 非默认形态，左腿白+右腿彩 |
| **渐变** | `gradient thighhighs` / `<shade> to white gradient thighhighs` | 特定形态，小腿处渐变 |
| **鱼网+纯色混搭** | `fishnet thighhighs` + `white thighhighs` | 一腿网袜一腿白 |

### 颜色分配（防撞色）

多人场景中每对组合的丝袜颜色必须不同。使用 COLOR MAP 分配：

| 角色 | 默认 | 一彩一白配色 | 渐变配色 |
|------|------|------------|---------|
| Chloe | 纯白 | 粉+白 | — |
| Chrome | 纯白 | 蓝+白 | — |
| Plasma | 纯白 | —（新娘手套区分） | — |
| Sakyumama | 纯白 | 紫+白 | — |
| Sutora | 纯白 | 奶油+白 | 渐变+白 |
| Tiffany | 渐变（紫白/蓝白） | 渐变+白 | 深紫到白渐变（默认） |

### 款式差异化

| 款式 | 标签 | 适用角色 |
|------|------|---------|
| 过膝袜 | `thighhighs` | Chloe, Chrome, Sakyumama 默认 |
| 鱼网袜 | `fishnet thighhighs` | Sakyumama/Sutora/Tiffany 比基尼形态 |
| 连裤袜 | `pantyhose` | Chloe/Tiffany 紧身衣形态 |
| 高低袜（一彩一白） | `asymmetrical legwear` | 非默认形态推荐 |
| 渐变袜 | `gradient thighhighs` | Tiffany 默认, Sutora 猫服 |
| 纯白+上衣区分 | `white thighhighs` | Plasma(新娘手套), Sutora(衬衫+蝴蝶结) |

### 手套镜像规则

**⚠️ 关键标签必须加权重（强化规则）**：所有 `bridal gauntlets`（1.3）、`elbow gloves`（1.2）、`shiny gloves`（1.2）以及本节表中涉及的所有踩脚袜/手套/露趾鞋靴标签，在 [tags] 中必须按 SKILL.md §规则 3 的权重分级加权重。`<color> gloves` 有颜色前缀时整体包裹：`(white elbow gloves:1.2)`。

一彩一白形态中，**手套颜色必须与同侧腿饰镜像**——左腿彩色→左手彩色，右腿白→右手白。
使用标签：`<color> gloves, white gloves, asymmetrical gloves`

```
例: Chrome 比基尼形态
  左腿: blue fishnet thighhighs → 左手: blue gloves
  右腿: white fishnet thighhighs → 右手: white gloves
  标签: blue gloves, white gloves, asymmetrical gloves
```

### 组合页 caption 示例

双人页必须描述颜色对比：
```
Chloe and Chrome kneel side by side, contrasting pink and blue thighhighs brushing against each other.
```

三人及以上页枚举各角色袜色：
```
Three pairs of stockings in pink, blue, and white create a rainbow around the male's shaft.
```

---