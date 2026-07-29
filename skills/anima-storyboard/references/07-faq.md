<!-- Extracted from SKILL.md §十、从小说提取特殊标签 + 十一、通用模板 + 十二、FAQ + 附录 -->

# 十、从小说提取特殊标签（进阶）

## 10.1 Tags 元数据解析

小说头部 `Tags:` 字段已经提供了关键分类标签，映射到 ANIMA3 tag 策略：

| 小说 Tags | → ANIMA3 Tag | 说明 |
|----------|-------------|------|
| 足控/足交/舔足 | `footjob, foot fetish, toe sucking` | 脚部场景标配套 |
| 中出/子宫奸/内射 | `creampie, cum inside, uterus` | 体内射精 |
| 潮吹/漏尿 | `squirting, urination, involuntary urination` | 液体场景 |
| 凌辱 | `humiliation, degradation, verbal abuse` | 羞辱场景 |
| 肛交 | `anal, anal penetration` | 肛门场景 |
| 泄殖腔 | `cloaca` | 特殊器官标签 |
| 踩脚袜 | `stirrup legwear, toeless legwear` | 服装细节 |
| 怀孕 | `pregnant, impregnation` | 怀孕场景 |
| 调教/恶堕 | `mind break, conditioning, brainwashing` | 精神控制 |
| 触手 | `tentacle, tentacle sex` | 触手场景 |
| 薄丝袜/透明丝袜/蕾丝丝袜 | `bridal legwear, sheer legwear, lace-trimmed legwear` | 薄透丝袜 |
| 婚纱头纱 | `bridal veil` | 新娘面纱，婚礼主题配饰 |
| 及肘手套/长手套/蕾丝手套 | `elbow gloves, sheer gloves, lace gloves, bridal gauntlets` | 薄透长手套 |
| 不对称手套/左右不同 | `asymmetrical gloves, mismatched gloves, single elbow glove` | 手套左右差异 |
| 双色手套 | `two-tone gloves, mismatched gloves, white elbow gloves, deep violet to white gradient elbow gloves` | 手套双色 |
| 不对称丝袜/左右不同 | `asymmetrical legwear, mismatched legwear, single thighhigh` | 左右差异 |
| 一彩一白/渐变搭配 | `mismatched legwear, white thighhigh, deep violet to white gradient thighhigh` | 颜色不对称 |
| 手套-丝袜镜像 | `mismatched gloves` + `mismatched legwear`（左右镜像配色） | 手套丝袜双色镜像 |
| 竖条纹丝袜 | `vertical-striped thighhighs, vertical-striped pantyhose` | 竖条纹样式 |
| 横条纹丝袜 | `striped thighhighs, striped pantyhose` | 横条纹样式 |
| 缝线丝袜（前/后/侧） | `seamed legwear, front-seamed, side-seamed` | 缝线样式 |
| 菱格纹 | `argyle thighhighs, argyle pantyhose` | 图案样式 |
| 渐变丝袜 | `{shade} to white gradient pantyhose, {shade} to white gradient thighhighs` | 渐变色 |
| 荷叶边袜口 | `frilled thighhighs, frilled socks, frilled legwear` | 荷叶边装饰 |
| 蕾丝袜口 | `lace-trimmed thighhighs, lace-trimmed legwear` | 蕾丝边装饰 |
| 基础项圈 | `choker, black choker, white choker, ribbon choker` | 按需添加，不强制 |
| 蝴蝶结项圈 | `bow choker, bow choker black bow, bow choker white bow` | 按需添加 |
| 蕾丝项圈 | `lace choker, frilled choker` | 按需添加 |
| 装饰项圈 | `spiked choker, studded choker, o-ring choker, bell choker` | 按需添加 |
| 颈环/项链 | `necklace, pendant, collar, pet collar, slave collar` | 按需添加 |
| 特殊颈饰 | `neck ribbon, neck bell, bandaged neck` | 按需添加 |
| 中式衣领 | `mandarin collar, shanghai neckline` | 按需添加 |
| 分离式衣领（克制使用） | `detached collar, detached sleeves` | 仅在原设已有或需强调正式感/女仆感时添加 |

## 10.2 从正文提取幕/节分隔

检查小说中的分隔符标识：

- `---` 或 `···` 或 `***` 等分隔线：表示场景切换/时间跳跃
- 每段分隔 = 潜在的单画面页面切换点
- 长段连续的对话/动作描写 = 可能需要扩展为多页
- 大段环境/心理描写 = 可压缩为单页过渡

---

# 十一、通用角色 tag 槽位分配模板

```
[count] 1girl / 2girls / solo / 1boy
[series] <角色英文名> \(<作品名>\)
[appearance] <发色> hair, <发型>, <瞳色> eyes, <特殊特征>
[cloth] <服装类型>, <服装颜色>, <配饰>, <鞋>
[pose/sex] <体位>, <性行为标签>
[expression] <表情标签>
[camera] <镜头方向>, <景别>
[scene] <场景>, <时间段>
[detail] <细节标签>
[NL] <英文自然语言补述>
```

### 填充示例（通用）

```
1girl, 1boy, hetero, mobius \(honkai impact 3rd\), green hair, very long hair, snake eyes, heterochromia, fang, small breasts, latex bodysuit, carbon fiber armor, stirrup legwear, toeless legwear, arm gloves, high heels, faceless male, fellatio, deep throat, kneeling, closed eyes, blush, from side, cowboy shot, laboratory, night, wet, shiny, saliva dripping
```

---

# 十二、常见问题与约束

## 12.1 角色 file 约定
角色描述文件存放于 `chara/prefer/<作品名>/` 目录，命名格式：
```
\(<中文名>\) <英文名>.txt
\(<中文名#皮肤名>\) <英文名 \(skin\)>.txt
```

## 12.2 优先使用 DB 标签
对每个写入的 tag 应通过 tag.sqlite 验证。如标签不存在于 DB 中，使用最近似替代。

## 12.3 中文翻译标注规则
所有 `chara/prefer/` 下的角色标签文件（`.txt`），每行中的每个标签必须附加其中文翻译，格式为 `tag = 中文名`。

**翻译来源优先级**：
1. `Workflow/wild/tag_dict.tsv` / `tag dict.tsv` 的 `cn name` 列（最权威，优先使用）
2. `tag.sqlite` 的 `cn_name` 列（同上数据源）
3. 自行意译（无 DB 记录时）

**允许的省略**：角色形态 tag（如 `pa-15 \(girls' frontline\)`）可仅标注主名可不逐标签翻译，但**所有 Danbooru 通用标签必须带中文翻译**。

**示例**：
```
# 正确
white hair = 白发, blue eyes = 蓝瞳, medium breasts = 中等胸围, school uniform = 学校制服
# 错误
white hair, blue eyes, medium breasts, school uniform

## 12.4 情节合理性与渐变
- 性爱场景的体位/玩法应从浅到深
- 权力关系的变化应有前因后果（通过过渡页暗示）
- 特殊 tag（如 `cloaca`, `watersports`）只在小说中有对应描述时才注入

## 12.5 分页数量管理
- 单页 tag 控制在 30-50 个，过长压缩
- 100 页分 10-12 个 batch，每 batch 10 页
- 每页 caption 控制在 5-10 句英文

## 12.6 Bridal 薄丝袜 + Elbow 手套 + 不对称丝袜验证清单

- [ ] 若使用 bridal/薄丝袜主题：`bridal gauntlets` 或 `bridal legwear` 已注入 tag 行
- [ ] 若使用 bride/婚礼主题：`bridal veil` 已注入 tag 行
- [ ] 若使用 elbow 手套：`elbow gloves` 已注入，且未出现 `latex gloves` / `leather gloves` / `rubber gloves`
- [ ] caption 中明确描写薄透材质（sheer/lace/translucent/delicate），无皮质/胶质词汇
- [ ] 若使用不对称丝袜：`asymmetrical legwear` 或 `mismatched legwear` 已注入，caption 写出左右差异 + 踩脚袜底露出
- [ ] 所有 legwear 脚底检查：无论 pantyhose/thighhighs/knee-highs，均带 `stirrup` 或 `toeless` 属性
- [ ] 额外样式检查：若使用竖条纹/横条纹/缝线/菱格/渐变/荷叶边/蕾丝边等样式，tag 与 caption 必须对应
- [ ] 手套-丝袜镜像检查：若手套使用双色/不对称，丝袜必须左右镜像对应
- [ ] 手套-丝袜配色协调检查：禁止蓝手套+白丝袜等不协调配色，必须同色/同渐变/同主题色
- [ ] 渐变角色：手套与丝袜渐变色统一

---

# 插件文件参考路径

| 用途 | 路径 |
|------|------|
| ANIMA3 模板 | `Workflow/wild/prompt/example/ANIMA3 提示词生成模板 v3.0.md` |
| 母女插件 | `Workflow/wild/prompt/plugin/qwen anima mother daughter.md` |
| 分镜插件 | `Workflow/wild/prompt/plugin/qwen anima storyboard.md` |
| 插画插件 | `Workflow/wild/prompt/plugin/qwen anima illus.md` |
| Footjob 插件 | `Workflow/wild/prompt/plugin/qwen anima footjob.md` |
| Cerpe 插件 | `Workflow/wild/prompt/plugin/qwen anima cerpe.md` |
| 角色文件目录 | `Workflow/wild/chara/prefer/<作品名>/` |
| 标签库 | `Workflow/wild/script/ffdkj-Danbooru Tag-Chinese-English-Translation-Table/tag.sqlite` |


---

## 附录：角色映射规则

当小说角色无直接 Danbooru 角色 tag 时，必须映射到已有 Danbooru 角色的作品。映射记录见 `storyboard/<作品名>/character map.md`。

《邻家妻子》映射 → `Workflow/wild/storyboard/邻家妻子/character map.md`
