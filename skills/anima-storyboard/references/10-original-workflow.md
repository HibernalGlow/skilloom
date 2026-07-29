<!-- 从鸣潮菲比×今汐项目中提炼的完整工作流 -->

# 十、无小说源素材时的原创故事板工作流

当**没有现成小说/剧本作为源素材**，需要从零开始创作原创故事板时，使用以下工作流。

## 10.1 总体流程

```
角色选型 → Danbooru数据搜集 → 角色形态文件生成 → 服装改造方案设计 → character_map编写 → 情节线设计 → 大纲编写(含构图模式) → 分页story写作 → 标签校验
```

与有小说源的标准流程（§1-§3）相比，本流程跳过"小说读取→角色画像提取→剧情拆解"环节，改为从角色出发自主构建剧情。新增**情节线设计**步骤，确保页面间有叙事连贯性而非散装场景堆砌。

## 10.1b 情节线设计（灵活指引）

在character_map完成后、大纲编写前，建议先构思情节走向。情节线是**灵活的叙事方向**，不是死板模板——根据角色性格、服装主题、场景氛围自由发挥，以下仅为参考维度。

### 叙事方向参考（非强制）

| 维度 | 可选方向 | 说明 |
|------|---------|------|
| **关系线** | 陌生人→试探 / 上下级→服从 / 恋人→沉溺 / 宿敌→征服 | 角色间的权力/情感关系变化 |
| **场景线** | 封闭→开放 / 暗→明 / 私密→公共 / 室内→户外 | 空间推进暗示心理变化 |
| **节奏线** | 缓起→急收 / 平行交替 / 渐强渐弱 / 突变 | 情绪节奏的呼吸感 |
| **服装线** | 原皮→皮肤 / 正装→凌乱 / 一种款式→另一种 | 服装变化暗示时间/状态推进 |

### 设计原则

1. **有方向即可**：不需要精确到每页，但每组形态（10-13页）应有起承转合
2. **允许偏航**：写作中如果某页情绪自然偏移，跟随直觉而非强行回归预设
3. **留白给分镜**：情节线只管"去哪里"，构图模式决定"怎么展示"，两者独立选择
4. **双人页有化学反应**：不是两个solo拼在一起，而是两人互动产生新的叙事动力

## 10.2 角色选型

确定故事板的角色阵容：

| 决策项 | 说明 |
|--------|------|
| 角色数量 | 2-6人，推荐2-3人（页数可控） |
| 角色来源 | 同一作品优先（标签体系一致） |
| 角色搭配 | 体型/发色/性格差异越大，视觉对比越强 |
| 参考作品 | 选择已有故事板作为风格参考（如卡提希娅坎特蕾拉） |

## 10.3 Danbooru数据搜集

### 步骤1：查询角色Wiki

对每个角色查询Danbooru Wiki页面，获取形态/皮肤信息：

```python
import requests, urllib3
urllib3.disable_warnings()
auth = ("CyberGlow", "bAHhuygFYYuwCbrSswMdiJj7")
headers = {'User-Agent': 'CharaBot/1.0 (CyberGlow)'}

# 查询角色wiki
r = requests.get(f"https://danbooru.donmai.us/wiki_pages/<角色tag>.json",
                 auth=auth, headers=headers, timeout=15, verify=False)
data = r.json()
# 提取: title, other_names, body(wiki内容含Appearance/Costumes段落)
```

### 步骤2：获取高分作品标签

从角色的高分作品中提取完整外观标签：

```python
# 获取top scored帖子
r = requests.get(f"https://danbooru.donmai.us/posts.json?tags=<角色tag>&limit=5&search[order]=score",
                 auth=auth, headers=headers, timeout=15, verify=False)
posts = r.json()

# 获取特定post的完整标签
r = requests.get(f"https://danbooru.donmai.us/posts/<post_id>.json",
                 auth=auth, headers=headers, timeout=15, verify=False)
post = r.json()
# 提取: tag_string_general, tag_string_character
```

### 步骤3：整理角色外观表

将搜集到的数据整理为角色外观表：

```markdown
## 角色外观表

| 角色 | 发色/发型 | 瞳色 | 体型 | 核心服装 | 特殊特征 | 皮肤/形态 |
|------|----------|------|------|---------|---------|----------|
| Phoebe | 金发超长发+侧分刘海 | 紫瞳 | medium breasts | 白帽+白衬衫+白裙+蓝腰带 | 尖耳+X发饰+黑领 | 无独立皮肤tag |
| Jinhsi | 白发超长发+低位双马尾 | 灰瞳白亮瞳 | medium breasts | 黑裙+白外套+高跟靴 | 龙角+眼下痣+发环 | 桃花(Peach Blossom) |
```

## 10.4 角色形态文件生成

按§1.4规则，为每个角色+形态组合生成`chara/prefer/<系列>/`下的标签文件。

### 服装改造方案设计

**核心原则：全白配色，仅款式不同**

当用户要求"取消一彩一白，全部白色"时，丝袜和手套的差异化通过**款式**而非**颜色**实现：

| 差异维度 | 可选款式 | 标签 |
|---------|---------|------|
| 长度 | 裤袜/过膝袜/及膝袜 | `pantyhose` / `thighhighs` / `knee-high socks` |
| 纹理 | 纯色/网袜/蕾丝边/竖条纹/菱格纹 | `fishnet pantyhose` / `lace-trimmed thighhighs` / `vertical-striped` / `argyle` |
| 叠穿 | 网袜叠穿裤袜 | `layered fishnet, fishnet pantyhose, pantyhose` |
| 渐变 | 色彩渐变（唯一彩色例外） | `pink to white gradient, gradient pantyhose` |
| 袜口 | 荷叶边/蕾丝边/普通 | `frilled thighhighs` / `lace-trimmed legwear` |

**渐变规则**：渐变色仅用于有明确主题的皮肤（如桃花皮肤→粉白渐变），原皮形态保持纯白。

### 形态文件命名

```
chara/prefer/<系列>/(<中文名#款式描述>) <角色tag>.txt
```

示例：
```
chara/prefer/wuthering_waves/(菲比#纯白裤袜) phoebe_(wuthering_waves).txt
chara/prefer/wuthering_waves/(菲比#白丝过膝) phoebe_(wuthering_waves).txt
chara/prefer/wuthering_waves/(菲比#白网叠穿) phoebe_(wuthering_waves).txt
chara/prefer/wuthering_waves/(今汐#纯白裤袜) jinhsi_(wuthering_waves).txt
chara/prefer/wuthering_waves/(今汐#白蕾丝边) jinhsi_(wuthering_waves).txt
chara/prefer/wuthering_waves/(今汐#桃花渐变) jinhsi_(peach_blossom)_(wuthering_waves).txt
```

### 形态文件内容

每个形态文件包含完整角色外观标签 + 该款式特有的丝袜/手套标签：

```
phoebe \(wuthering waves\), blonde hair, very long hair, sidelocks, parted bangs, purple eyes, pointy ears, medium breasts, black collar, collar, hair bow, black bow, hair ornament, x hair ornament, hat, white hat, sun hat, large hat, striped bow, blue gem, blue sash, sash, pendant, jewelry, earrings, white shirt, shirt, long sleeves, frilled sleeves, frills, white skirt, skirt, high-waist skirt, blue scarf, scarf, tacet mark \(wuthering waves\), white pantyhose, pantyhose, white stirrup legwear, stirrup legwear, toeless legwear, skindentation, white elbow gloves, elbow gloves, v-shaped fabric on back of hand, seams, arm seams, finger seams, high heels, staff, holding staff
```

## 10.5 character_map编写

`character_map.md`是故事板的核心规划文档，包含以下章节：

### 必含章节

```markdown
# Character Map — <作品名> <角色名>

## 角色映射表
| 小说本名 | Caption映射名 | Danbooru Tag |

## 形态款式方案
| 角色 | 形态中文名 | 丝袜款式 | 手套 | 标签后缀 |

## 设计原则
- 配色规则说明
- 款式区分方式
- 渐变例外说明

## 双人款式防撞
| 场景组 | 角色1款式 | 角色2款式 | 对比 |

## FB编号
- a01 = 角色1
- a02 = 角色2
- m01 = 双人组

## 二. 幼化形态（age regression 追加）
| 角色 | 形态中文名 | 服装 | 丝袜/标签特征 | am编号 |

### 幼化形态通用标签
- 共享标签列表
- 禁加标签列表
- 外貌特征保留规则
- 踩脚袜与手套规则

## 三. 双人组编号补充
| 编号 | 组合 | 说明 |

### m02 服装混搭组合
| 范围 | 角色1服装 | 角色2服装 | 页数 |

## 四. 页面分布
| 范围 | 角色 | 说明 | 页数 |
```

### 双人防撞规则

多人场景中，同页两角色的丝袜款式**必须不同**，通过款式差异而非颜色差异区分：

| 策略 | 示例 | 视觉效果 |
|------|------|---------|
| 长度对比 | 裤袜 vs 过膝 | 全包裹 vs 袜口露肤 |
| 纹理对比 | 网袜 vs 蕾丝边 | 菱形网格 vs 精致花边 |
| 材质对比 | 纯色 vs 渐变 | 均匀白 vs 粉白过渡 |
| 叠穿对比 | 网袜叠穿 vs 纯色 | 双层纹理 vs 单层光滑 |

## 10.6 大纲编写

`outline.md`是页面级别的详细规划，每页指定：

### 大纲格式

```markdown
| 页码 | 梗概 | 体位/玩法 | 构图模式 | 镜头 | 场景 | 表情弧线 |
```

### 构图模式——视觉叙事工具箱

**核心原则：单帧是基础，多帧是增强——优先选择多帧构图来承载更多信息**

每页从以下工具箱中自由组合，不局限于koma分格：

#### A. 页面结构类（决定单页怎么切分）

| 模式 | 标签 | post_count | 说明 | 适用 |
|------|------|-----------|------|------|
| 单帧 | 无额外标签 | — | 一页一画面，冲击力最强 | 高潮爆发、情感聚焦、体位定场 |
| 双格 | `2koma` | 46K | 两格递进/对比 | 动作→反应、前→后、起→伏 |
| 三格 | `3koma` | 25K | 三格递进 | 浅→深→极限、试探→接受→沉溺 |
| 四格 | `4koma` | 115K | 起承转合完整微叙事 | 动作分解、情绪四段式 |
| 分屏 | `split screen` | 2.8K | 左右/上下并行视角 | 表情+动作、双人对比、内外同时 |
| 画中画 | `inset` | 2.7K | 主景+角落细节 | 全身+结合部、表情+局部放大 |
| 前后对比 | `before and after` | 2.5K | 两个时间点 | 射精前/后、插入前/后、服装完整/凌乱 |
| 多视角 | `multiple views` | 254K | 同一动作多角度 | 正面+侧面+背面、全身+特写组合 |
| 漫画页 | `comic` | 701K | 自由分格布局 | 复杂叙事、多角色互动 |

#### B. 音效类（增强临场感）

| 模式 | 标签 | post_count | 说明 | 适用 |
|------|------|-----------|------|------|
| 音效 | `sound effects` | 48K | 拟声词 | 抽送声、拍打声、液体声、心跳声 |

> **注意**：不使用 speech bubble / thought bubble / narration，因为模型输出文字容易出错。音效以拟声词形式在caption中用 `[SFX: *plap*]` 标注，不依赖模型生成可读文字。

#### C. 视觉效果类（增强动态感和情绪表达）

| 模式 | 标签 | post_count | 说明 | 适用 |
|------|------|-----------|------|------|
| 动作线 | `motion lines` | 116K | 运动轨迹线 | 抽送动作、身体摆动、快速位移 |
| 速度线 | `speed lines` | 14K | 集中方向的速度感 | 猛烈冲刺、瞬间插入、高潮瞬间 |
| 汗滴 | `sweatdrop` | 313K | 紧张/尴尬/兴奋 | 羞涩时刻、过载反应、紧张感 |
| 倾斜构图 | `dutch angle` | 156K | 画面倾斜 | 失控感、眩晕、高潮恍惚 |
| 剪影 | `silhouette` | 22K | 轮廓剪影 | 体位全景、氛围渲染、过渡 |
| 镜像 | `mirror` | 39K | 镜中倒影 | 自我审视、双重视角、前后同时 |
| 倒影 | `reflection` | 54K | 水面/地面倒影 | 场景氛围、空间延伸 |

#### D. 内部透视类（展示不可见细节）

| 模式 | 标签 | post_count | 说明 | 适用 |
|------|------|-----------|------|------|
| 横切面 | `cross-section` | 18K | 内部结构剖面 | 开宫细节、结合部内部、子宫状态 |
| X光 | `x-ray` | 17K | 透视内部 | 深度指示、射精内部、宫颈状态 |
| 放大层 | `zoom layer` | 36K | 局部放大叠加 | 足部细节、手部细节、表情放大 |

#### E. 边框/氛围类

| 模式 | 标签 | post_count | 说明 | 适用 |
|------|------|-----------|------|------|
| 白边框 | `white border` | 149K | 漫画式白边 | 分格页默认边框、干净感 |
| 黑边框 | `black border` | 24K | 暗色调边框 | 夜景、暗室、压抑氛围 |
| 特写切入 | `cut-in` | 709 | 突然放大的局部 | 关键瞬间、表情突变、冲击 |

### 构图选择原则

1. **默认多帧**：除非有明确理由用单帧（高潮爆发、情感聚焦），否则优先选择多帧构图
2. **自由组合**：页面结构+音效+视觉效果+内部透视可叠加，如 `4koma + sound effects + motion lines`
3. **音效增强临场**：`sound effects` 让静态画面有"声音"，大幅提升沉浸感
4. **倾斜=失控**：`dutch angle` 在高潮/开宫页使用，倾斜构图暗示角色心理失衡
5. **zoom layer > inset**：zoom layer（36K post）比inset（2.7K post）更常见且更灵活，优先使用

### 构图组合推荐

| 页面类型 | 推荐组合 | 标签示例 |
|---------|---------|---------|
| 足交过程 | 双格+音效+放大层 | `2koma, sound effects, zoom layer` |
| 深喉 | 分屏+音效+动作线 | `split screen, sound effects, motion lines` |
| 骑乘展开 | 四格+音效+速度线 | `4koma, sound effects, speed lines` |
| 开宫 | 画中画+横切面+倾斜 | `inset, cross-section, dutch angle` |
| 内射 | 前后对比+X光+汗滴 | `before and after, x-ray, sweatdrop` |
| 体位过渡 | 双格+剪影+汗滴 | `2koma, silhouette, sweatdrop` |
| 情绪转折 | 三格+汗滴+动作线 | `3koma, sweatdrop, motion lines` |
| 双人互动 | 漫画页+音效+多视角 | `comic, sound effects, multiple views` |
| 高潮爆发 | 单帧+倾斜+速度线 | `dutch angle, speed lines` |
| 余韵温存 | 单帧+镜像+倒影 | `mirror, reflection` |

### 情绪弧线设计

每组形态的页面按情绪递进排列，**每页标注情绪弧线阶段**：

```
Phase 1 羞涩试探: 跪奉/手套奉 (2koma: 低头→偷看)
Phase 2 愉悦接受: 足奉/口奉 (split screen: 表情+动作)
Phase 3 兴奋探索: 骑乘/后入 (4koma: 动作递进)
Phase 4 激情高潮: 开宫/内射 (inset: 全身+特写)
Phase 5 余韵归属: 温存 (单帧: 情感聚焦)
```

### 体位覆盖规则

每组形态至少覆盖4种体位/玩法，推荐覆盖：

| 类别 | 体位 | 标签 |
|------|------|------|
| 口部 | 跪奉/深喉 | `fellatio, kneeling` / `deepthroat, irrumatio` |
| 足部 | 足奉/袜踩 | `uxsFJ, under-stirrup footjob, footjob` / `sole focus` |
| 手部 | 手套奉/榨精 | `gloved handjob` / `handjob, edging` |
| 传教 | 传教/压腹 | `missionary` / `mating press, folded` |
| 骑乘 | 骑乘/反骑 | `cowgirl position` / `reverse cowgirl` |
| 后入 | 后入/俯卧 | `doggystyle` / `prone bone` |
| 深入 | 开宫/宫顶 | `cerpe, cervical penetration, stomach bulge` |
| 终幕 | 内射/余韵 | `vag creampie, cum inside` / `aftercare, cuddling` |

### 场景覆盖规则

每组形态至少覆盖3种场景：

| 场景类型 | 示例 | 氛围 |
|---------|------|------|
| 室内私密 | 卧室/浴室/书房 | 亲密、安静 |
| 室内公共 | 舞台/教室/教堂 | 禁忌、暴露 |
| 户外 | 庭园/桃林/廊下 | 自然、开放 |

### 镜头覆盖规则

每组形态至少覆盖4种镜头：

| 镜头 | 用途 | 标签 |
|------|------|------|
| full body | 全身展示 | `full body, from front/side/behind` |
| cowboy shot | 半身互动 | `cowboy shot, from front/side/above` |
| close-up face | 表情特写 | `close-up, face focus` |
| close-up part | 局部特写 | `close-up, foot/penetration/stomach focus` |

## 10.7 分页story写作

### 写作流程

1. **建立标签模板**：从chara/prefer文件提取每个角色的完整标签行
2. **分批并行写作**：按形态/角色分组，每组10-15页，使用子代理并行写作
3. **格式校验**：每批完成后抽检标签格式和caption规则

### 单帧页模板（默认）

```
[tags]
1girl, <角色标签>, <外观标签>, <丝袜标签>, <手套标签>, <鞋/道具>, <体位/玩法标签>, <表情标签>, <镜头标签>, <场景标签>
1boy, faceless male, penis, erect, hetero, large penis, size difference, height difference, <体位标签>

[caption]
<纯英文客观描述段落，禁止代词，必须用角色英文名或the male>
```

### 双格页模板（2koma）

```
[tags]
1girl, <角色标签>, <外观标签>, <丝袜标签>, <手套标签>, <鞋/道具>, <体位/玩法标签>, <表情标签>, <镜头标签>, 2koma, <场景标签>
1boy, faceless male, penis, erect, hetero, large penis, size difference, height difference, <体位标签>

[caption]
Panel 1: <第一个瞬间——动作/起因/前状态>
Panel 2: <第二个瞬间——反应/结果/后状态>
```

### 带音效的双格页

```
[tags]
1girl, <角色标签>, <外观标签>, <丝袜标签>, <手套标签>, <鞋/道具>, <体位/玩法标签>, <表情标签>, <镜头标签>, 2koma, sound effects, <场景标签>
1boy, faceless male, penis, erect, hetero, large penis, size difference, height difference, <体位标签>

[caption]
Panel 1: <描写> [SFX: 拟声词]
Panel 2: <描写>
```

### 带音效的四格页

```
[tags]
1girl, <角色标签>, <外观标签>, <丝袜标签>, <手套标签>, <鞋/道具>, <体位/玩法标签>, <表情标签>, <镜头标签>, 4koma, sound effects, <场景标签>
1boy, faceless male, penis, erect, hetero, large penis, size difference, height difference, <体位标签>

[caption]
Panel A: <起>
Panel B: <承> [SFX: 拟声词]
Panel C: <转>
Panel D: <合> [SFX: 拟声词]
```

### 分屏页模板（split screen）

```
[tags]
1girl, <角色标签>, <外观标签>, <丝袜标签>, <手套标签>, <鞋/道具>, <体位/玩法标签>, <表情标签>, <镜头标签>, split screen, <场景标签>
1boy, faceless male, penis, erect, hetero, large penis, size difference, height difference, <体位标签>

[caption]
Left panel: <视角1——通常是表情/上半身>
Right panel: <视角2——通常是动作/下半身>
```

### 画中画页模板（inset / zoom layer）

```
[tags]
1girl, <角色标签>, <外观标签>, <丝袜标签>, <手套标签>, <鞋/道具>, <体位/玩法标签>, <表情标签>, <镜头标签>, inset, zoom layer, <场景标签>
1boy, faceless male, penis, erect, hetero, large penis, size difference, height difference, <体位标签>

[caption]
Main scene: <主画面——全身/半身整体构图>
Zoom layer: <放大细节——足部/手部/表情放大>
Corner inset: <角落细节——结合部横切面/内部透视>
```

### 前后对比页模板（before and after）

```
[tags]
1girl, <角色标签>, <外观标签>, <丝袜标签>, <手套标签>, <鞋/道具>, <体位/玩法标签>, <表情标签>, <镜头标签>, before and after, <场景标签>
1boy, faceless male, penis, erect, hetero, large penis, size difference, height difference, <体位标签>

[caption]
Before: <前状态——紧绷/即将/边缘>
After: <后状态——释放/溢出/松弛>
```

### 带横切面/X光的开宫页

```
[tags]
1girl, <角色标签>, <外观标签>, <丝袜标签>, <手套标签>, <鞋/道具>, cerpe, cervical penetration, stomach bulge, <表情标签>, <镜头标签>, cross-section, x-ray, dutch angle, <场景标签>
1boy, faceless male, penis, erect, hetero, large penis, size difference, height difference, deep penetration

[caption]
Main scene: <全身构图，倾斜画面暗示失控>
Cross-section: <横切面展示宫颈被穿透>
X-ray: <X光透视展示子宫内深度>
```

### 双人分镜页模板

```
[tags]
2girls, ffm threesome, threesome,
<角色1英文名> \(<系列>\), <角色1外观>, <角色1丝袜>, <角色1手套>,
<角色2英文名> \(<系列>\), <角色2外观>, <角色2丝袜>, <角色2手套>,
<共有体位/玩法标签>, <表情标签>, <镜头标签>, <分镜标签>, <场景标签>
1boy, faceless male, penis, erect, hetero, large penis, size difference, height difference, <体位标签>

[caption]
<按分镜类型标注，如2koma:>
Panel 1: <角色1英文名>: <描写>; <角色2英文名>: <描写>
Panel 2: <角色1英文名>: <描写>; <角色2英文名>: <描写>
```

### 幼化单人页模板

```
[tags]
1girl, white stirrup legwear, stirrup legwear, toeless legwear, white bridal gauntlets, bridal gauntlets, <角色标签>, age regression, loli, flat chest, petite, <外观标签>, <服装标签>, <体位/玩法标签>, <表情标签>, <镜头标签>, <场景标签>
1boy, faceless male, penis, erect, hetero, large penis, size difference, age difference, height difference, <体位标签>

[caption]
<纯英文客观描述，禁止代词，包含"nine-year-old"年龄标识，禁加child tag>
```

### 幼化双人页模板

```
[tags]
2girls
phoebe \(wuthering waves\), age regression, loli, flat chest, petite, <菲比外观>, <菲比服装>, white stirrup legwear, stirrup legwear, toeless legwear, white bridal gauntlets, bridal gauntlets
jinhsi \(wuthering waves\), age regression, loli, flat chest, petite, <今汐外观>, <今汐服装>, white stirrup legwear, stirrup legwear, toeless legwear, white bridal gauntlets, bridal gauntlets
<共有标签>, <表情>, <镜头>, <场景>
1boy, faceless male, penis, erect, hetero, large penis, size difference, age difference, height difference

[caption]
Phoebe: <描写>
Jinhsi: <描写>
The male: <描写>
```

### caption写作规则（强化版——动态漫画思维）

#### 基础规则

| 规则 | 说明 | 错误示例 | 正确示例 |
|------|------|---------|---------|
| 禁代词 | 禁止she/her/he/him/his | "She raises her feet" | "Phoebe raises both feet" |
| 禁对话引用 | 禁止直接引语 | `"More," she whispers` | Phoebe mouths a silent plea |
| 禁心理描写 | 只写画面可见内容 | "She feels overwhelmed" | "Phoebe's whole body trembles" |
| Tag↔Caption对应 | 每行tag在caption有描写 | tag有`stirrup legwear`但caption未提 | caption必须描写踩脚袜细节 |
| 丝袜款式描写 | 必须描写当前形态的丝袜特征 | 仅写"white stockings" | "white pantyhose stretched taut, stirrup loop gripping the arch" |
| 手套质感描写 | 必须描写手套材质和细节 | 仅写"wearing gloves" | "white elbow gloves, v-shaped fabric on the back of each hand, finger seams tracing along" |
| 足部细节 | 足交页必须描写踩脚袜结构 | 仅写"footjob" | "stirrup strap pressing the shaft between bare toes and the stirrup band" |
| 双人对比 | 双人页必须对比两人款式差异 | 两人描述相同 | "Phoebe's fishnet pantyhose vs Jinhsi's lace-trimmed thighhighs" |

#### 连贯性规则（新增——解决情节断裂问题）

| 规则 | 说明 | 示例 |
|------|------|------|
| **页面衔接** | 每页caption末尾暗示下一页走向，或开头承接上一页状态 | "Phoebe's grip tightens, pulling the male closer—" → 下一页开头 "The male responds by pressing deeper" |
| **体液延续** | 射精后的页面必须体现体液状态（cum on body / dripping），不能突然消失 | 内射页后："cum trickles down Phoebe's inner thigh, staining the white pantyhose" |
| **表情递进** | 同一体位组内表情必须递进，不能倒退 | 跪奉: blush → 口奉: blush, parted lips → 深喉: tears, drool, open mouth |
| **服装状态延续** | 脱下的衣物/解开的扣子在后续页保持状态 | "Phoebe's white shirt hangs open from the previous encounter" |
| **场景过渡** | 场景切换需要过渡暗示 | 卧室→浴室: "Phoebe rises from the bed, bare feet padding toward the bathroom" |
| **道具延续** | 前一页出现的道具下一页继续使用或交代去向 | "the staff Phoebe set aside earlier now lies across the bedsheets" |

#### 分镜页caption规则（新增）

| 规则 | 说明 |
|------|------|
| **分格标注** | 必须使用 `Panel 1: / Panel 2:` 等分格标注 |
| **格间递进** | 每格必须有变化（动作/表情/角度/时间），禁止两格描写完全相同的内容 |
| **格间连贯** | 后一格必须承接前一格，形成因果或时间递进 |
| **表情变化** | 至少一格展示表情变化（从冷静→泛红、从闭眼→睁眼等） |
| **动作变化** | 至少一格展示动作变化（从静止→运动、从浅→深等） |
| **心理暗示** | 通过表情/肢体语言暗示心理，而非直接描写心理 |

#### 分镜页caption示例

**2koma + sound effects 动作→反应**：
```
Panel 1: Phoebe wraps both feet around the shaft, the white stirrup legwear stretched taut across the soles as the under-stirrup fabric presses the length between bare toes and the stirrup band. [SFX: *squeak*]
Panel 2: The male's hips jerk forward, a thick pulse traveling up the shaft as Phoebe's purple eyes widen, a gasp parting Phoebe's lips at the sudden throb against Phoebe's soles.
```

**split screen + sound effects 表情+动作+音效**：
```
Left panel: Jinhsi's face fills the frame, grey eyes with white pupils half-lidded, the mole under one eye catching the light as Jinhsi bites Jinhsi's lower lip, a deep blush spreading across Jinhsi's cheeks.
Right panel: From the waist down, the male's large penis drives into Jinhsi, Jinhsi's white pantyhose-clad legs splayed wide, the stirrup loops cutting into the arches as Jinhsi's toes curl with each thrust. [SFX: *plap* *plap* *plap*]
```

**4koma + sound effects 动作递进**：
```
Panel A: Phoebe kneels before the male, both white-gloved hands resting on the male's thighs, purple eyes looking up with calm composure, the large penis inches from Phoebe's face.
Panel B: Phoebe leans forward, lips parting around the tip, the black bow in Phoebe's hair bobbing as Phoebe takes the head into Phoebe's mouth, cheeks hollowing. [SFX: *slurp*]
Panel C: Phoebe's throat bulges as the shaft pushes deeper, tears welling in purple eyes, both gloved hands gripping the male's hips for balance, the white elbow gloves taut against Phoebe's forearms.
Panel D: Phoebe pulls back with a wet gasp, a string of saliva connecting Phoebe's lips to the glans, face flushed, eyes dazed, a drop of pre-cum glistening on Phoebe's chin. [SFX: *pop*]
```

**inset + cross-section + dutch angle 全身+特写+倾斜**：
```
Main scene: The frame tilts at a dutch angle as Phoebe lies beneath the male in missionary, legs wrapped around the male's waist, white pantyhose stretched along splayed thighs, the large penis buried to the hilt. Phoebe's back arches off the bed, very long blonde hair a wild halo, purple eyes rolled back.
Cross-section: A cross-section shows the glans forcing through Phoebe's cervix, lodged deep inside Phoebe's uterus, the cervical opening stretched taut around the shaft.
```

**before and after + x-ray + sweatdrop 射精对比**：
```
Before: The male's penis throbs inside Phoebe, the shaft pulsing visibly against the stretched walls, Phoebe's stomach taut with the deep penetration, every muscle in Phoebe's body clenched in anticipation. A sweatdrop rolls down Phoebe's temple.
After: The male's penis twitches as cum floods Phoebe's uterus, Phoebe's abdomen visibly distending with the volume, thick white fluid overflowing around the shaft and dripping down Phoebe's white pantyhose, Phoebe's body going limp in release. X-ray shows the uterus filled to capacity.
```

**mirror + reflection 余韵**：
```
Phoebe lies curled against the male's chest, very long blonde hair spilling across the sheets, the white pantyhose stained and askew. In the mirror on the wardrobe door, the reflection shows Phoebe's peaceful, exhausted face, purple eyes half-closed, a faint smile on Phoebe's lips. The reflection in the polished floor shows the male's arm draped protectively around Phoebe's waist.
```

## 10.8 标签校验

### 校验流程

1. **Danbooru在线校验**：对关键标签查询Danbooru API确认存在性
2. **本地数据库校验**：用tag.sqlite验证标签post_count
3. **参考文件一致性**：与同系列已有角色文件（如卡提）对比，确认服装改造标签一致

### 校验脚本

```python
import sqlite3
db = sqlite3.connect(r'Workflow/wild/script/ffdkj-Danbooru_Tag-Chinese-English-Translation-Table/tag.sqlite')
c = db.cursor()

# 校验关键标签
tags_to_check = [
    'stirrup_legwear', 'toeless_legwear', 'elbow_gloves',
    'fishnet_pantyhose', 'gradient_pantyhose', 'lace-trimmed_thighhighs',
    '<角色tag>', '<皮肤tag>',
    # ... 按需添加
]

for t in tags_to_check:
    c.execute('SELECT name, post_count FROM tags WHERE name=?', (t,))
    r = c.fetchone()
    print(f'{t}: {r if r else "NOT FOUND"}')
db.close()
```

### 常见问题修正

| 问题 | 修正方式 |
|------|---------|
| 复合标签不存在（如`pink to white gradient pantyhose`） | 拆分为`pink to white gradient, gradient pantyhose` |
| 技能规则标签不在Danbooru（如`v-shaped fabric on back of hand`） | 保留，这是技能约定标签，同系列文件一致使用 |
| 角色皮肤tag缺失 | 确认wiki中是否有独立tag，无则用基础角色tag |

## 10.9 页数规划参考

### 2角色故事板（参考：菲比×今汐，296页）

| 范围 | 内容 | 页数 | 占比 |
|------|------|------|------|
| 角色1 solo原皮 | 3形态×13页 | 39 | 13% |
| 角色2 solo原皮 | 4形态×10页 | 39 | 13% |
| 双人组原皮 | 6种款式混搭 | 42 | 14% |
| 角色1幼化solo初批 | 7服装×1-2页 | 10 | 3% |
| 角色2幼化solo初批 | 7服装×1-2页 | 10 | 3% |
| 幼化双人初批 | 10种搭配×1页 | 10 | 3% |
| 角色1幼化solo追加 | 7服装×8-9页 | 60 | 20% |
| 角色2幼化solo追加 | 7服装×8-9页 | 60 | 20% |
| 幼化双人追加 | 9种搭配×1-5页 | 26 | 9% |
| **总计** | | **296** | |

### 幼化服装库（7套基础）

| 服装 | 标签 | 适用角色 |
|------|------|---------|
| 芭蕾少女 | `ballerina, tutu, leotard, ballet slippers, leg ribbons, bun, tiara` | 通用 |
| 小女仆 | `french maid, frilled headdress, apron` | 通用 |
| 猫娘 | `cat ears, cat tail, cat suit, bell choker, paw gloves` | 通用 |
| 兔女郎 | `playboy bunny, bunny ears, bow tie, fishnet thighhighs` | 通用 |
| 领舞 | `sequined dress, go-go dancer, feather boa, body jewelry, platform heels` | 通用 |
| 修女 | `nun habit, wimple, veil, cross necklace` | 通用 |
| 水手服 | `sailor uniform, sailor collar, pleated skirt` | 菲比系 |
| 旗袍 | `qipao, side slit, high slit, mandarin collar` | 今汐系 |

### 幼化双人混搭组合生成

从两角色的服装库中取笛卡尔积，按视觉对比度排序：

```
菲比服装 × 今汐服装 = 7 × 7 = 49 种组合
```

筛选规则：
1. 同类服装避免搭配（芭蕾×芭蕾 → 跳过）
2. 优先对比度强的组合（女仆×修女、猫娘×兔女郎）
3. 每种组合至少5页duo
4. 总组合数控制在10-20种

## 10.10 与标准流程的映射

| 标准流程步骤 | 无小说流程对应 | 说明 |
|------------|--------------|------|
| §1.1 小说读取 | 跳过 | 无源素材 |
| §1.2 角色画像提取 | §10.3 Danbooru数据搜集 | 从Danbooru wiki/post提取外观 |
| §1.3 角色形态查表 | §10.3 步骤1 | 查询wiki获取形态/皮肤 |
| §1.4 角色形态文件生成 | §10.4 | 同规则，增加款式差异化设计 |
| §2 场景提取 | §10.6 大纲编写 | 自主设计场景和情绪弧线 |
| §3 分章方案 | §10.6 | 自主规划页面分布 |
| §4-§6 分页编写 | §10.7 | 同规则 |
| §6 标签验证 | §10.8 | 同规则 |
