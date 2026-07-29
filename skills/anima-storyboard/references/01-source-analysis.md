<!-- Extracted from SKILL.md §一、源素材读取与分析 -->

# 一、源素材读取与分析

## 1.1 小说读取

从指定路径读取 `.txt` 小说文件。文件格式特征：

```
标题
RawTitle: <raw title>
Date: <publish date>
Length: <character count>
Name: <author> \(URL\)
Source: <pixiv URL>
Tags: [tag1, tag2, tag3, ...]
Caption: <description>

<正文>
```

### 元数据提取
- **作品名称** — RawTitle / 标题行
- **作品系列** — Tags 中提取（如 `崩坏3rd/崩坏三`, `原神`）
- **角色** — Tags 中提取（如 `梅比乌斯`, `甘雨`）
- **性向/标签** — Tags 中提取（如 `R-18`, `足控/足交`, `中出`, `凌辱` 等分类标签）
- **作者** — Name + URL
- **正文** — 标题/元数据后的全部内容

## 1.2 角色画像提取

从小说文本中提取每个关键角色的视觉与性格特征：

| 维度 | 提取要点 |
|------|---------|
| 发 | 颜色、长度、发型（直/卷/双马尾/单马尾）、装饰（发饰/冠/耳环） |
| 眼 | 颜色、瞳形（竖瞳/圆瞳）、眼型 |
| 身体 | 身高、胸围（巨乳/平胸/中等）、肤色、特殊特征（鳞/尾/角/耳） |
| 服装 | 材质（漆皮/网格/丝质）、颜色、款式（裙/旗袍/制服/裸露度）、配件（手套/颈饰/袜） |
| 性格 | S/M、抖S/抖M、温柔/冷酷、母性/冷血等关键 trait |
| 系列标签 | 推测 Danbooru 用系列 tag（如 `mobius \(honkai impact 3rd\)`） |

### 关键：外观标签到 ANIMA3 系列 tag 的映射

从文本描述 + Tags 推测正确的 Danbooru 系列标签：

```
honkai impact 3rd / honkai 3rd → 崩坏3
mobius \(honkai impact 3rd\) → 梅比乌斯角色标签
genshin impact → 原神
blue archive → 蔚蓝档案
azur lane → 碧蓝航线
```

### 1.3 角色形态与服装查表（Danbooru Wiki）

**在编写故事板之前，必须先查询角色 Danbooru Wiki 页面，获取所有有独立 tag 的形态（Appearance）和服装（Costumes/Skins）。**

#### 为什么必须先查表

同一角色在 Danbooru 上可能有多个独立 tag 的形态/服装变体（如灵基再临、泳装、礼装等）。这些变体**已有官方 Danbooru tag**，直接使用即可，无需手动从文本推测服装标签。跳过此步骤会导致：
- 手动描述服装标签不准确或冗长
- 错过已有的精确 costume tag
- 同一角色不同服装页面标签不一致

#### 查询方法

**⚠️ 关键：User-Agent 必须使用 Bot 格式，禁止伪装浏览器。** Danbooru 的 Cloudflare 防护会拦截所有伪装浏览器的请求（返回 403 "Just a moment"）。正确的 User-Agent 格式为 `YourBotName/1.0 (your-danbooru-username)`。

```python
import requests, urllib3
urllib3.disable_warnings()

auth = ("CyberGlow", "bAHhuygFYYuwCbrSswMdiJj7")
headers = {'User-Agent': 'CharaBot/1.0 (CyberGlow)'}  # ✅ 正确：Bot 格式
# headers = {'User-Agent': 'Mozilla/5.0 ...'}          # ❌ 错误：浏览器伪装，会被 Cloudflare 403

# 获取角色 wiki 页面 JSON
r = requests.get(f"https://danbooru.donmai.us/wiki_pages/<角色tag>.json",
                 auth=auth, headers=headers, timeout=15, verify=False)

# 获取帖子标签（按分数排序取 top）
r = requests.get(f"https://danbooru.donmai.us/posts.json?tags=<角色tag>&limit=3&search[order]=score",
                 auth=auth, headers=headers, timeout=15, verify=False)

# 获取特定 post 的完整标签
r = requests.get(f"https://danbooru.donmai.us/posts/<post_id>.json",
                 auth=auth, headers=headers, timeout=15, verify=False)
```

**认证方式**（按 Danbooru API 文档 `help:api`）：
- HTTP Basic Auth：`login:api_key` 或 URL 参数 `?login=username&api_key=key`
- 当前账号：`CyberGlow` / `bAHhuygFYYuwCbrSswMdiJj7`

**速率限制**：全局 10 请求/秒，建议每次请求间隔 1 秒。

**Cloudflare 绕过失败时的回退方案**：
1. **yande.re API**：`https://yande.re/post.json?tags=<角色tag>&limit=5`（无 Cloudflare，但标签不如 Danbooru 完整）
2. **tag.sqlite 本地数据库**：`Workflow/wild/script/ffdkj-Danbooru_Tag-Chinese-English-Translation-Table/tag.sqlite`，可查询角色 tag 是否存在及 post_count
3. **萌娘百科**：`https://moegirl.icu/<角色名>` 获取基础外观信息（发色、瞳色、萌点）

#### Wiki 页面结构解析

角色 wiki 页面的 `body` 字段包含结构化信息，关键段落以 `h4.` 标记：

```
h4. Appearance          ← 基础外观/灵基再临形态
* !post #9147551: [[Ishtar (First Ascension) (fate)|First Ascension]]
* !post #9147552: Second Ascension
* !post #9147553: Third Ascension
* !post #9158886: [[Ishtar (Swimsuit Rider) (fate)|Swimsuit Rider]]

h4. Costumes / Skins    ← 皮肤/礼装/合作服装
* !post #3408637: [[Ishtar (Bitter Sweet) (fate)|Bitter Sweet]]
* !post #9001802: [[Ishtar (Formal Dress) (fate)|Formal Dress]]
* !post #9648660: [[Ishtar (Grand Journey) (fate)|Grand Journey]]
```

#### 提取规则

| 模式 | 提取方式 | 示例 |
|------|---------|------|
| `!post #ID: [[Tag Name\|Display Name]]` | 提取 `Tag Name`，转为下划线格式即为 Danbooru tag | `Ishtar \(First Ascension\) \(fate\)` → `ishtar \(first ascension\) \(fate\)` |
| `!post #ID: [[Tag Name\|]]` | 同上，`Tag Name` 即为 tag | `Space Ishtar \(fate\)` → `space ishtar \(fate\)` |
| `!post #ID` （无链接） | 仅有 post ID，无独立 tag，需从 post 提取外观标签 | 用 `/posts/{ID}.json` 获取 `tag string` |
| `!asset #ID` | 资产图（非公开帖子），无法直接获取标签 | 跳过或用其他来源 |

#### Tag 格式转换

从 wiki 链接文本转为 Danbooru tag 的规则：

```
1. 取 [[ ... ]] 中 | 前的部分（如无 | 则取全部）
2. 空格 → 下划线
3. 括号保留，内部空格也转下划线
4. 全部小写

例: "Ishtar \(First Ascension\) \(fate\)"
  → "ishtar \(first ascension\) \(fate\)"

例: "PA-15 \(High School Thrills\) \(girls' frontline\)"
  → "pa-15 \(high school thrills\) \(girls' frontline\)"
```

#### 输出：角色形态表

查询完成后，整理为以下格式的**角色形态表**，供后续分页编写时引用：

```markdown
## 角色形态表：<角色名>

| 形态 tag | 中文名 | 类型 | 引用图 post ID |
|---------|--------|------|---------------|
| `ishtar \(fate\)` | 伊什塔尔（默认/一破） | Appearance | #9147551 |
| `ishtar \(first ascension\) \(fate\)` | 伊什塔尔（一破） | Appearance | #9147551 |
| `ishtar \(swimsuit rider\) \(fate\)` | 伊什塔尔（泳装 Rider） | Appearance | #9158886 |
| `ishtar \(bitter sweet\) \(fate\)` | 伊什塔尔（Bitter Sweet） | Costume | #3408637 |
| `ishtar \(formal dress\) \(fate\)` | 伊什塔尔（正装） | Costume | #9001802 |
```

#### 形态 tag 在故事板中的使用

1. **默认形态**：使用角色基础 tag（如 `ishtar \(fate\)`），从 Appearance 第一张引用图提取外观标签
2. **特定服装/灵基**：使用对应 costume tag（如 `ishtar \(bitter sweet\) \(fate\)`），替换基础角色 tag
3. **同一页面只使用一个角色 tag**：基础 tag 或 costume tag 二选一，不要同时写两个
4. **costume tag 已包含服装信息**：使用 costume tag 时，仍需从引用图提取完整外观标签（发色、瞳色等），但服装部分以引用图为准

#### 特殊情况

| 情况 | 处理方式 |
|------|---------|
| 角色 wiki 页面无 Appearance/Costumes 段落 | 仅用基础角色 tag + 从高分作品提取外观标签 |
| 服装无独立 tag（`!post #ID` 无链接） | 用基础角色 tag + 从该 post 提取服装标签手动写入 |
| 子角色/变体有独立 wiki（如 Space Ishtar） | 单独查询其 wiki 页面，视为独立角色处理 |
| `!asset #ID`（资产图） | 无法直接获取，跳过，改用 `order:score` 高分作品回退 |

#### 与 §1.2 角色画像提取的关系

- §1.2 从**小说文本**提取角色视觉特征 → 生成外观标签
- §1.3 从**Danbooru Wiki** 查询角色所有形态 → 获取精确 tag
- **两者结合**：用 §1.3 确定有哪些形态可用，用 §1.2 确定小说中每页应使用哪个形态

---

### 1.4 角色形态文件生成

**在 §1.3 查询完角色形态表后，必须为每个形态生成对应的角色标签文件（`.txt`），存放到 `chara/prefer/<系列>/` 目录。**

#### 生成流程

```
§1.3 形态表 → 遍历每个形态 tag → 检查 chara/prefer/ 是否已有 → 已有则复制 / 无则从 wiki post 抓取并过滤 → 写入 .txt
```

#### 步骤 1：检查已有文件

在 `chara/prefer/<系列>/` 目录下查找是否已有该形态的 `.txt` 文件：

```
命名规则: \(<中文名>#<皮肤中文名>\) <形态tag>.txt
         \(<中文名>\) <形态tag>.txt          ← 默认形态无 # 部分

已有示例:
  chara/prefer/fate/\(梅柳齐娜\) melusine \(fate\).txt
  chara/prefer/fate/\(梅柳齐娜\) melusine \(first ascension\) \(fate\).txt
  chara/prefer/fate/\(英灵博装\) melusine \(exhibition attire\) \(fate\).txt
  chara/prefer/azur lane/\(埃吉尔#铁血龙女仆\) aegir \(iron blood's dragon maid\) \(azur lane\).txt
```

**⚠️ 中文翻译强制规则**：角色文件名中的中文名/皮肤名必须使用**中文翻译**，不得使用日文罗马音或英文原文。

| 错误写法 | 正确写法 | 说明 |
|---------|---------|------|
| `\(enjo kouhai\) enjo kouhai.txt` | `\(援助交配\) enjo kouhai.txt` | 日文标题必须翻译为中文 |
| `\(senran kagura\) shinobi crisis.txt` | `\(闪乱神乐\) shinobi crisis.txt` | 作品名用中文译名 |
| `\(school days\) true end.txt` | `\(school days\) true end.txt` | 英文名可保留 |
| `\(kanColle\) kaga.txt` | `\(舰队Collection\) kaga.txt` | 缩写展开为中文 |

**中文名来源优先级**：
1. 萌娘百科/Moegirl 上的官方中文译名
2. Danbooru wiki `other names` 中的中文名
3. 作品本身的中文官方名（如《舰队Collection》《闪乱神乐》）
4. 无公认译名时，自行翻译为中文（如 `enjo kouhai` → `援助交配`）

- **已有文件**：直接复制内容，跳过抓取
- **无文件**：进入步骤 2 从 wiki post 抓取

#### 步骤 2：从 Wiki 引用图抓取标签

对 §1.3 形态表中每个**无已有文件**的形态，从其 wiki 引用图 post 获取标签：

```python
# 1. 用 post ID 获取完整标签
post = api get\(f"/posts/{post id}.json"\)

# 2. 使用 tag string general 而非 tag string（更精准）
#    Danbooru post 对象提供分类标签字段：
#      tag string general    ← 通用标签（外观、服装、动作等）
#      tag string character  ← 角色标签
#      tag string artist     ← 画师标签（跳过）
#      tag string copyright  ← 版权/系列标签（跳过）
#      tag string meta       ← 元标签（highres, absurdres 等，跳过）

# 3. 仅取 tag string general + tag string character
raw tags = \(post.get\("tag string general", ""\) + " " + post.get\("tag string character", ""\)\).split\(\)
```

#### 步骤 3：过滤与加工标签

从 wiki 引用图获取的标签需经过过滤和加工，规则如下：

**必须删除的标签**（chara 文件只保留角色固有外观）：
- `solo`（单人限制 — 反推出图不需要）
- `standing`、`clenches fists` 等动作标签
- 全部角度标签（`direct eye contact`、`facing viewer`、`from side` 等 — 现在提示词系统自由指定）
- 场景/背景/镜头/效果标签
- `translucent`、`sheer`、`see-through`
- 其余保留原作设定

**体型与发型调整**：
- `loli`、`flat chest` — 萝莉体型 + 平胸（⚠ 禁加 `child`，会导致模型额外画出一个小孩）
- `age regression` — 可选，幼女化/年龄倒退（适合同人创作中把角色画小时添加）
- `age difference` — 女方幼小 vs 男方成年的年龄差对比
- `super long hair` — 超长发（叠加在 `long hair` / `very long hair` 后）

**条件添加的服装改造标签**（⚠ 仅在不破坏原设服装结构时才加；若原设与之冲突如铠甲/和服/宽松毛衣/泳装/已紧身等，则跳过）：
- 不可能: `impossible clothes`、`impossible leotard`
- 高开叉: `highleg`、`highleg leotard`、`super highleg`、`deep high slit`、`slit to waist`
- 分离式衣领: `detached collar`
- 无趾紧身衣: `toeless bodysuit`
- 大腿饰: `thighlet jewelry`、`thighlet`、`thigh strap`
- `stirrup legwear`
- `v-shaped fabric on back of hand`
- `seams`、`arm seams`、`finger seams`
- `pantyhose-style seams`

**⚠️ 改造标签作用范围判断**：服装改造标签（`highleg leotard`/`highleg`/`super highleg`/`deep high slit`/`slit to waist` 等）**仅当角色原设穿紧身衣/leotard/连体袜/丝袜时添加**。角色穿连衣裙/长袍/宽松衣物/裸足/有鳞片皮毛时，这些标签会强制给角色套上紧身衣效果，反而降低裸露度，必须禁用。拿不准时查原设图确认。

##### 项圈/颈饰标签库（克制使用，按需添加）

- **基础项圈**：`choker`（项圈）/ `black choker`（黑项圈）/ `white choker`（白项圈）/ `ribbon choker`（缎带项圈）
- **蝴蝶结项圈**：`bow choker`（蝴蝶结项圈）/ `bow choker, black bow`（黑色蝴蝶结）/ `bow choker, white bow`（白色蝴蝶结）
- **蕾丝项圈**：`lace choker`（蕾丝项圈）/ `frilled choker`（荷叶边项圈）
- **装饰项圈**：`spiked choker`（尖刺项圈）/ `studded choker`（铆钉项圈）/ `o-ring choker`（O形环项圈）/ `bell choker`（铃铛项圈）
- **颈环/项链**：`necklace`（项链）/ `pendant`（吊坠）/ `collar`（颈环，偏BDSM风格）/ `pet collar`（宠物项圈）/ `slave collar`（奴隶项圈）
- **特殊颈饰**：`neck ribbon`（颈部缎带）/ `neck bell`（颈部铃铛）/ `bandaged neck`（颈部绷带）
- **中式衣领**：`mandarin collar`（立领）/ `shanghai neckline`（上海领/斜襟）
- **分离式衣领（克制使用）**：`detached collar`（分离式衣领）/ `detached sleeves`（分离式袖子）— 仅在角色原设已有或需要强调正式感/女仆感时添加，不强制
:- **⚠️ 泳装/比基尼特殊规则**：`stirrup legwear`/`toeless legwear` 可以与 bikini/swimsuit 共存（比基尼+踩脚袜是合法组合）。同时 bikini 形态通常为 `barefoot`，无需 `unworn shoes`。
:- **⚠️ 重要澄清**：`covered navel` 不再强制添加或删除，按角色原设处理。若角色原设穿着紧身衣、leotard、连体袜等可遮脐服装，则 `covered navel` 可按原设保留；若原设露脐（如 bikini），则不加。
- **颜色规则（服装改造配色）**：袜子/手套颜色必须与角色本身颜色匹配，原设已标明颜色的不改动。当原设无袜/无手套时，改造添加的袜子和手套颜色按以下规则确定：
  1. **优先取原设袜色**：角色原设定已有袜子/裤袜时，`stirrup legwear`/`pantyhose` 颜色与原设袜色保持一致
  2. **裤子颜色优先**：角色穿裤子（长裤/短裤）但无袜时，`stirrup legwear`/`pantyhose` 颜色与裤子颜色一致（如白裤→白袜，黑裤→黑袜）
  3. **无裤无袜时默认白色**：角色穿裙子/裸腿且原设无袜时，默认使用 `white stirrup legwear` / `white legwear`（白丝）
  4. **手套与外套同色**：`bridal gauntlets`/`elbow gloves` 颜色与外套/上衣主色一致（如黑夹克→黑手套，白大衣→白手套）
  5. **先查后写**：必须从 Danbooru 引用图确认皮肤实际配色后才写颜色前缀
- **⚠️ 光泽材质警告**：`shiny gloves`、`glossy fabric`、`shiny` 在 Danbooru 中特指 **漆皮/乳胶/vinyl/PVC 光泽材质**，AI 模型会渲染出橡胶/塑料质感。除非角色原设就是 latex/leather（如大凤·黯灭龙神通、埃吉尔·铁血龙女仆等明确需要光泽的场景），**普通角色禁止使用**。代之以 `gloves`（不加 `shiny`）+ 可选颜色前缀（如 `white gloves`），或 `silk`（丝绸质感）。规则：`shiny gloves` / `glossy fabric` / `shiny` **已废弃，禁止使用**。
:- **⚠️ 括号转义（ComfyUI 强制性要求）**：ComfyUI 把 `()` 解析为权重标记，因此标签中的括号**必须转义**为 `\(` / `\)`，否则 `(kedama milk)` 会被当成权重放大。
  - **原则**：JS/TS 源码中只存干净字符串（如 `chrome (kedama milk)`），禁止直接在字符串字面量中写 `\(`（JS 严格模式下非法）
  - **写入 .txt 时转义**：输出前对字符串做 `.replace('(', '\\(').replace(')', '\\)')`（注意 JS 字符串字面量中 `\\` 表示一个反斜杠）
  - 或用 **Python** 处理，Python 中 `'\\('` 就是 `\(`，更直观无歧义
- **禁止标签**：`garter straps`（含所有颜色变体）
- **禁止扶她类标签**：`futanari`、`implied futanari`、`female with penis`、`dickgirl`、`shemale`、`newhalf`、`futanari masturbation`、`full-package futanari`、`futa without pussy`、`futa without balls`、`futa with female`、`futa with male`、`futa with futa`、`futa on male`、`male on futa`、`futasub`、`intravaginal futanari`
- **禁止性转/伪娘标签**：`genderswap`、`genderswap (mtf)`、`genderswap (ftm)`、`genderswap (otf)`、`trap`、`crossdressing`、`crossdressing (mtf)`、`otokonoko`、`male with breasts`、`pegging`、`strap-on`
- **单边袜规则**：如果角色有 `single thighhigh`（单边过膝袜），另一只裸足必须改为 `single sock` + `ankle socks` + `stirrup legwear`，不得使用 `single bare leg`
- **踩脚袜穿鞋规则**：踩脚袜出场时，鞋子穿脱按场景区分——不涉及足交的场景，穿鞋/脱鞋各 50%（非强制脱鞋）；足交场景则必须脱鞋（`unworn shoes`），确保踩脚袜袜底露趾结构可用于足交。
- **禁止男性穿袜**：1boy 行禁止出现 `pantyhose`/`thighhighs`/`stockings`/`stirrup legwear`/`kneehighs` 等袜类标签。袜类标签仅允许在 1girl 行出现。

##### 薄丝袜（bridal）与 elbow 手套强制规则

- **薄丝袜**：必须使用 `bridal gauntlets` 或 `bridal legwear` 表达薄透丝袜质感；禁止用 `latex`、`leather`、`rubber` 等厚重材质替代
- **头纱**：`bridal veil`（婚纱面纱），用于增强婚礼/新娘主题氛围，按需添加
- **elbow 手套**：必须使用 `elbow gloves`（及肘长度），严禁使用 `latex gloves`、`leather gloves`、`rubber gloves` 等皮质/胶质手套
- **材质强调**：在 tag 中追加 `sheer gloves`、`sheer legwear`、`lace gloves`、`lace-trimmed gloves` 以强化薄透/蕾丝质感
- **caption 强制描写**：每页 caption 必须明确写出 "thin bridal sheer gloves"、"delicate lace elbow gloves"、"translucent pantyhose" 等薄透材质描述，严禁出现 "leather"、"latex"、"rubber"、"plastic" 等厚重/胶质词汇
- **渐变统一**：若角色为渐变发色/服装，手套与丝袜渐变色必须统一，格式 `{shade} to white gradient elbow gloves` / `{shade} to white gradient pantyhose, stirrup legwear`
- **手套-丝袜双色镜像规则**：当手套使用双色/不对称配色时，必须与丝袜左右镜像对应
  - 左手白+右手彩 → 左腿彩+右腿白（镜像对称，彩色优先于黑色）
  - 左手渐变+右手纯色 → 左腿纯色+右腿渐变（镜像对称）
  - tag 示例：`mismatched gloves, white elbow gloves, deep violet to white gradient elbow gloves` + `mismatched legwear, single thighhigh, white thighhigh, deep violet to white gradient thighhigh, stirrup legwear`
  - caption 必须写出镜像关系："the left hand in white elbow gloves mirrors the right leg in white thighhighs, while the right hand in gradient gloves mirrors the left leg in gradient stirrup pantyhose"

##### 手套款式库

- **基础长度**：`elbow gloves`（及肘，主力款）/ `half gloves`（半掌）/ `fingerless gloves`（露指）
- **材质强调**：`sheer gloves` / `lace gloves` / `lace-trimmed gloves` / `bridal gauntlets`
- **装饰样式**：`frilled gloves`（荷叶边袖口）/ `ribbon-trimmed gloves`（缎带装饰）/ `cross-laced gloves`（交叉系带）/ `glove bow`（手套蝴蝶结）
- **图案样式**：`vertical-striped gloves`（竖条纹）/ `striped gloves`（横条纹）/ `gradient gloves`（渐变）/ `argyle gloves`（菱格纹）/ `pinstripe gloves`（细条纹）/ `seamed gloves`（后缝线手套）/ `side-seamed gloves`（侧缝手套）/ `front-seamed gloves`（前缝线手套）
- **层叠**：`layered gloves`（多层手套）/ `gloves over elbow gloves`（短手套叠戴在长手套上）
- **不对称/双色**：`mismatched gloves` / `asymmetrical gloves` / `single elbow glove` / `two-tone gloves`
- **严禁**：`latex gloves` / `leather gloves` / `rubber gloves` / `fur gloves` / `knit gloves`

##### 丝袜标签组合公式

`{颜色} + {基础款式} + {额外样式} + {踩脚属性}`

- 颜色：`white` / `black` / `red` / `deep violet to white gradient` 等
- 基础款式：`pantyhose` / `thighhighs` / `leg wrap` / `knee-high socks` / `crew socks` / `toeless socks` / `toe socks` / `ankle socks`
- 额外样式（可选，可多选）：
  - 竖条纹：`vertical-striped thighhighs` / `vertical-striped pantyhose`
  - 横条纹：`striped thighhighs` / `striped pantyhose`
  - 缝线（前/后/侧）：`seamed legwear`（后缝线）/ `front-seamed` / `side-seamed`
  - 细条纹：`pinstripe thighhighs` / `pinstripe pantyhose`
  - 菱格纹：`argyle thighhighs` / `argyle pantyhose`
  - 渐变：`{shade} to white gradient pantyhose` / `{shade} to white gradient thighhighs`
  - 网袜：`fishnet pantyhose`（必须叠穿 `pantyhose`）
  - 荷叶边袜口：`frilled thighhighs` / `frilled socks` / `frilled legwear`
  - 蕾丝袜口：`lace-trimmed thighhighs` / `lace-trimmed legwear`
- 踩脚属性（必加）：`stirrup legwear` 或 `toeless legwear`

**完整 tag 示例**：
- 白色竖条纹过膝袜+踩脚：`white vertical-striped thighhighs, stirrup legwear`
- 白色后缝线裤袜+踩脚：`white seamed legwear, pantyhose, stirrup legwear`（仅用户指定黑色时使用）
- 渐变菱格纹过膝袜+踩脚：`deep violet to white gradient argyle thighhighs, stirrup legwear`
- 细条纹裤袜+露趾：`pinstripe pantyhose, toeless legwear`
- 前缝线网袜裤袜+踩脚：`front-seamed fishnet pantyhose, pantyhose, stirrup legwear`
- 白色荷叶边过膝袜+踩脚：`white frilled thighhighs, stirrup legwear`
- 白色蕾丝边裤袜+踩脚：`white lace-trimmed pantyhose, stirrup legwear`（仅用户指定黑色时使用）
- 横条纹及膝袜+踩脚：`striped knee-high socks, stirrup legwear`
- 露趾短袜+踩脚：`toeless socks, stirrup legwear`
- 五指袜+踩脚：`toe socks, stirrup legwear`
- 露趾靴+踩脚：`open-toe boots, stirrup legwear`
- 露趾鞋+踩脚：`open-toe shoes, stirrup legwear`
- 绑带高跟鞋+踩脚：`strappy heels, stirrup legwear`

##### 丝袜不对称与多款式搭配规则

- **对称常规款**：`white pantyhose, stirrup legwear` / `white thighhighs, stirrup legwear` / `white pantyhose, toeless legwear`（左右一致，所有款式脚底均为踩脚）
- **一彩一白/渐变搭配**：`mismatched legwear, single thighhigh, white thighhigh, deep violet to white gradient thighhigh, stirrup legwear`（左右不同色，均为踩脚款）
- **不对称款式**：`asymmetrical legwear` + 左右不同长度/款式组合，如：
  - 左腿裤袜 + 右腿过膝袜：`single leg pantyhose, thighhighs, stirrup legwear`
  - 左腿长筒 + 右腿短筒：`mismatched legwear, knee-high socks, thighhighs, stirrup legwear`
  - 左腿网袜叠穿 + 右腿纯色裤袜：`layered fishnet, fishnet pantyhose, pantyhose, single leg pantyhose, stirrup legwear`
- **不同款式库**（可左右混搭，所有款式必须叠加 `stirrup legwear` 或 `toeless legwear`）：
  - 裤袜+踩脚：`pantyhose, stirrup legwear`
  - 过膝袜+踩脚：`thighhighs, stirrup legwear`
  - 腿绑带+踩脚：`leg wrap, stirrup legwear`
  - 及膝袜+踩脚：`knee-high socks, stirrup legwear`
  - 露趾短袜：`toeless socks, stirrup legwear`（袜头露出脚趾）
  - 五指袜：`toe socks, stirrup legwear`（五指分开袜+踩脚）
  - 露趾靴：`open-toe boots, stirrup legwear`（靴头露出脚趾）
  - 露趾鞋：`open-toe shoes, stirrup legwear`（鞋头露出脚趾）
  - 绑带高跟鞋：`strappy heels, stirrup legwear`（绑带高跟可搭配踩脚袜）
  - 小腿袜+踩脚：`crew socks, stirrup legwear`
  - 网袜+踩脚：`fishnet pantyhose, pantyhose, stirrup legwear`（必须叠穿 `pantyhose`）
  - 吊带袜+踩脚：`garter straps, thighhighs, stirrup legwear`（仅在 asymmetrical 搭配中允许）
  - 露趾袜：`toeless legwear`
  - **核心规则**：无论裤袜/长筒/短筒/网袜/吊带，所有 legwear 必须叠加 `stirrup legwear` 或 `toeless legwear`，确保脚底/脚趾可见

- **颜色组合推荐**：
  - 白+彩：`white thighhigh, red thighhigh, stirrup legwear`
  - 黑+白：`black pantyhose, white pantyhose, stirrup legwear`（仅用户指定黑色时使用）
  - 渐变+纯色：`deep violet to white gradient pantyhose, white thighhigh, stirrup legwear`
  - 竖条纹+纯色：`white vertical-striped thighhigh, deep violet to white gradient thighhigh, stirrup legwear`
  - 后缝线+菱格：`deep violet to white gradient seamed legwear, argyle thighhigh, stirrup legwear`
  - 前缝线+蕾丝边：`front-seamed pantyhose, lace-trimmed thighhigh, stirrup legwear`
  - 横条纹+荷叶边：`striped thighhigh, frilled knee-high socks, stirrup legwear`

- **caption 强制描写**：若使用不对称搭配，caption 必须明确写出左右差异 + 踩脚袜底露出，例如 "left leg wrapped in sheer white pantyhose while right leg bared in deep violet to white gradient fishnet thighhighs, both with soles exposed by stirrup legwear"、"one leg in pantyhose, the other in knee-high lace socks, both with stirrup legwear gripping the arches"
- **⚠️ 黑色丝袜仅限用户指定**：black thighhighs / black pantyhose / black stirrup legwear 等黑色丝袜标签仅在用户明确要求时使用，默认使用白色或渐变色

核心过滤原则：**chara 文件只保留角色固有外观标签**，删除一切动作、场景、镜头、效果标签。

```python
# 过滤规则：仅保留以下类别的标签
KEEP CATEGORIES = {
    # 身体特征
    "hair color", "hair length", "hair style", "eye color", "eye type",
    "body size", "body type", "skin", "breast size", "body part",
    # 非人特征
    "animal ears", "horns", "tail", "wings", "fang", "scales",
    # 服装
    "clothing", "dress", "footwear", "headwear", "gloves", "legwear",
    "accessory", "jewelry", "weapon",
    # 角色标签
    "character tag",
}

# 明确排除的标签类别
EXCLUDE PATTERNS = {
    # 动作/姿势（不属于角色固有外观）
    "sitting", "standing", "lying", "kneeling", "walking", "running",
    "from *", "close-up", "full body", "cowboy shot",
    # 场景
    "outdoors", "indoors", "sky", "water", "nature", "city",
    "bedroom", "bathroom", "classroom",
    # 画面质量/元信息
    "highres", "absurdres", "commentary", "translated", "scan",
    "official art", "concept art",
    # 情感/表情（不属于固有外观）
    "smile", "blush", "open mouth", "closed eyes", "crying",
    # 性相关（不属于角色定义）
    "nude", "nsfw", "pussy", "penis", "sex", "cum",
}
```

**更实用的过滤方式**：使用 Danbooru 的 `tag string general` 字段 + 按标签 category 过滤。Danbooru 标签分类：

| Category | 含义 | 处理 |
|----------|------|------|
| 0 | General（通用） | **保留**：外观、服装、身体特征类 |
| 1 | Artist（画师） | **排除** |
| 3 | Copyright（版权/系列） | **排除** |
| 4 | Character（角色） | **保留** |
| 5 | Meta（元信息） | **排除** |

对 General 类标签做二次过滤，排除动作/场景/表情等非角色固有标签：

```python
# 通用标签中需要排除的关键词模式
EXCLUDE GENERAL = [
    # 动作/姿势
    r'^\(sitting|standing|lying|kneeling|walking|running|jumping|flying|falling|dancing\)$',
    r'^\(from |close.up|full.body|cowboy.shot|portrait|group|solo|multiple\)',
    # 场景/环境
    r'^\(outdoors|indoors|sky|water|nature|city|bedroom|bathroom|classroom|night|day\)',
    # 画面质量
    r'^\(highres|absurdres|commentary|translated|scan|official|concept\)',
    # 表情/情感
    r'^\(smile|blush|open.mouth|closed.eyes|crying|tears|angry|surprised\)',
    # 性相关
    r'^\(nude|nsfw|pussy|penis|sex|cum|breasts exposed|topless|bottomless\)',
]
```

##### 个人偏好标签（出图时按需注入 prompt）

以下为出图时可选的增强标签，按需在 storyboard 页面中注入：

- **皮肤/身体**: `shiny skin`、`navel`、`stomach`、`groin` — 光泽肌肤、肚脐、腹部、腹股沟
- **南半球 + 侧乳**: `underboob`（南半球）、`sideboob`（侧乳）— `flat chest`/`loli` 也可用，不影响
- **奶盖**: `breast curtains` — 露出乳晕/乳盖设计
- **胯帘**: `pelvic curtain` — 腰胯间垂帘（常与 `breast curtains` 胸前垂帘搭配使用）
- **眼心**: `heart in eye` — 眼中爱心
- **角度**: `ass visible through thighs` — 大腿间看臀
- **效果**: `motion lines` — 动作线
- **阴茎增强**: `huge penis`、`horse penis`（`huge` 比 `large` 大，`horse` 更夸张）、`veiny penis`（青筋阴茎）
- **阴茎反差**: `penis size difference`、`stomach bulge`、`deep penetration`、`gaping` — 视觉冲击
- **体位 - 体型差强化**: `mating press`、`folded`、`legs up`、`from below`、`suspended congress`、`against wall` — 通过体位突出幼女与男性体型/长度反差
- **性癖标签**（按需）: `armpit sex`、`footjob`、`two-footed footjob`、`under-stirrup footjob`、`cervical penetration`、`cross-section`、`hairjob`、`hair on penis`、`cooperative hairjob`（注：`cooperative hairjob` 需双人）

#### 步骤 4：组装标签行

将过滤后的标签组装为一行，格式与已有 chara 文件一致：

```
<角色形态tag>, <外观标签1>, <外观标签2>, ..., <服装标签1>, <服装标签2>, ...
```

**标签排序规则**（与已有文件保持一致）：
1. 角色形态 tag（首项，空格替换为下划线，全小写）
2. 发色/发型标签
3. 瞳色/瞳形标签
4. 身体特征标签（体型、特殊器官等）
5. 服装标签（从内到外、从上到下）
6. 配饰/武器标签

**中文翻译标注**：每个标签后必须标注其中文翻译，格式为 `tag = 中文名`。中文名优先从 `tag_dict.tsv` 的 `cn name` 列获取，无记录时自行意译。

```
正确格式: white hair = 白发, blue eyes = 蓝瞳, medium breasts = 中等胸部, school uniform = 学校制服
```

**示例**：

```
pa-15 \(high school thrills\) \(girls' frontline\) = PA-15(高中惊魂), white hair = 白发, long hair = 长发, blue eyes = 蓝瞳, medium breasts = 中等胸围, school uniform = 学校制服, white shirt = 白衬衫, neckerchief = 领巾, pleated skirt = 百褶裙, black skirt = 黑裙, black thighhighs = 黑过膝袜, loafers = 乐福鞋
```
> ⚠️ 此处 black thighhighs 为角色原设（Danbooru 原图即为黑丝），属例外情况。新角色设计或用户未指定时，默认使用白色/渐变色丝袜。

#### 步骤 5：写入文件

```
输出路径: chara/prefer/<系列>/\(<中文名>#<皮肤中文名>\) <形态tag>.txt
```

**中文名来源**：
- 优先从 wiki `other names` 提取（排除含假名的日文名）
- 无中文名时使用英文名

**皮肤中文名**：
- 从 wiki 链接的 Display Name（`|` 后的部分）翻译
- 或从 `other names` 中提取

**文件名示例**：

```
chara/prefer/girls frontline/\(PA-15#高中惊魂\) pa-15 \(high school thrills\) \(girls' frontline\).txt
chara/prefer/girls frontline/\(PA-15#迷人翠雀\) pa-15 \(alluring larkspur\) \(girls' frontline\).txt
chara/prefer/fate/\(伊什塔尔#Bitter Sweet\) ishtar \(bitter sweet\) \(fate\).txt
```

#### 回退策略

| 情况 | 处理方式 |
|------|---------|
| 形态无 wiki 引用图（`!post #ID` 无链接） | 用基础角色 tag + 从该 post 提取服装标签手动写入 |
| 形态仅有 `!asset #ID` | 跳过，改用 `order:score` 高分作品回退（取 top 1-3） |
| wiki 引用图标签过少（< 5 个 general tag） | 补充 `order:score` 高分作品的标签，取交集去重 |
| 高分作品也无该形态 | 仅写角色 tag，外观标签留空，后续手动补充 |

#### 与 §1.3 的关系

- §1.3 输出**角色形态表**（哪些形态可用、对应 tag 和 post ID）
- §1.4 输出**角色形态文件**（每个形态的具体标签内容，写入 `chara/prefer/`）
- §1.4 依赖 §1.3 的形态表来确定需要生成哪些文件

#### 完整示例：PA-15

**§1.3 形态表输出**：

| 形态 tag | 中文名 | 类型 | 引用图 post ID |
|---------|--------|------|---------------|
| `pa-15 \(girls' frontline\)` | PA-15 | Appearance | #3702143 |
| `pa-15 \(high school thrills\) \(girls' frontline\)` | PA-15（高中惊魂） | Skin | #3702150 |
| `pa-15 \(alluring larkspur\) \(girls' frontline\)` | PA-15（迷人翠雀） | Skin | #3977525 |
| `pa-15 \(marvelous yam pastry\) \(girls' frontline\)` | PA-15（妙薯山芋） | Skin | #3977522 |
| `pa-15 \(lady thief of champagne\) \(girls' frontline\)` | PA-15（香槟女贼） | Skin | #4700212 |
| `pa-15 \(dance in the ice sea\) \(girls' frontline\)` | PA-15（冰海之舞） | Skin | #5668078 |
| `pa-15 \(light-treading night\) \(girls' frontline\)` | PA-15（轻踏夜行） | Skin | #6708601 |

**§1.4 文件生成**（假设 `chara/prefer/girls frontline/` 下无已有文件）：

```
chara/prefer/girls frontline/
├── \(PA-15\) pa-15 \(girls' frontline\).txt                    ← 从 post #3702143 抓取
├── \(PA-15#高中惊魂\) pa-15 \(high school thrills\) \(girls' frontline\).txt      ← 从 post #3702150 抓取
├── \(PA-15#迷人翠雀\) pa-15 \(alluring larkspur\) \(girls' frontline\).txt        ← 从 post #3977525 抓取
├── \(PA-15#妙薯山芋\) pa-15 \(marvelous yam pastry\) \(girls' frontline\).txt     ← 从 post #3977522 抓取
├── \(PA-15#香槟女贼\) pa-15 \(lady thief of champagne\) \(girls' frontline\).txt  ← 从 post #4700212 抓取
├── \(PA-15#冰海之舞\) pa-15 \(dance in the ice sea\) \(girls' frontline\).txt     ← 从 post #5668078 抓取
└── \(PA-15#轻踏夜行\) pa-15 \(light-treading night\) \(girls' frontline\).txt     ← 从 post #6708601 抓取
```

每个文件内容格式（标签后须带中文翻译，译名来自 `tag_dict.tsv` 的 `cn name` 列或自行意译）：
```
pa-15 \(girls' frontline\) = PA-15, white hair = 白发, very long hair = 超长发, blue eyes = 蓝瞳, medium breasts = 中等胸围, choker = 项圈, black choker = 黑项圈, collarbone = 锁骨, bare shoulders = 露肩, navel = 肚脐, panties = 内裤, bra = 胸罩, lingerie = 蕾丝内衣, thigh strap = 大腿带, blue nails = 蓝指甲, pale skin = 白皙皮肤, wide hips = 宽臀, slender waist = 细腰
```

---

### 角色分化（多形态/多套服装时）

同一角色在不同阶段可能穿不同服装。根据小说中的场景转换确定每页的服装状态：

- **基础形态**：日常/初始服装 → 使用基础角色 tag
- **变体形态**：特殊场景服装（战斗服/礼服/泳装/裸体）→ 使用对应 costume tag
- **状态变化**：怀孕隆起、精液覆盖、汗湿、捆绑等临时状态 → 在基础/costume tag 上叠加状态标签

### 形态页数分配规则

**每个 chara/prefer/ 下的 .txt 文件算一个独立形态**，必须分配页数。页数根据形态与原皮的差异程度决定：

| 形态类型 | 定义 | 最低页数 | 典型页数 |
|---------|------|---------|---------|
| **原皮（默认形态）** | 角色基础外观 | 10 页 | 10-15 页 |
| **微变形态** | 与原皮差异小（仅露内衣/换色/加外套等） | 10 页 | 10-12 页 |
| **新设计皮肤** | 全新服装设计（泳装/礼装/和服/制服等） | 13 页 | 13-18 页 |
| **独立角色变体** | 同系列但视为独立角色（如 Space Ishtar） | 10 页 | 10-12 页 |

**判断"微变"vs"新设计"的标准**：
- 仅在原皮基础上脱衣/露内衣 → 微变（如二破仅露内衣）
- 换了外套但内搭不变 → 微变（如 Lawson 冬装仅加外套）
- 全新服装轮廓/风格 → 新设计（如泳装、和服、偶像装）
- 新角色 tag → 独立角色变体

**总页数计算**：所有形态页数之和为故事板总页数，必须 ≥ 120 页。

---