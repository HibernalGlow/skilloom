<!-- Extracted from SKILL.md §七、插件规则注入 + 八、LoRA 触发词系统 -->

# 七、插件规则注入

## 7.1 场景类型模板

根据不同的小说内容类型，选择需注入的强制标签集：

| 场景类型 | 强制标签集 | 触发条件 |
|---------|-----------|---------|
| 常规性爱 | `hetero, 1girl, 1boy` | 默认 |
| 多人（1男多女） | `ffm threesome, threesome, 2girls, 1boy` | 第3人加入 |
| 多人（多男1女） | `mmf threesome, threesome, 2boys, 1girl` | 第3人加入 |
| 母子/母女 | `mother and daughter, parent and child, age difference, incest` + `2girls` | 亲子关系确立 |
| 父女 | `father and daughter, parent and child, age difference, incest` | 父女关系确立 |
| 主奴 | `domination, submission, slave, master` | 权力关系确立 |
| 调教 | `bondage, bdsm, discipline, training` | 调教场景 |
| 恶堕 | `mind break, corruption, ahegao, brainwashing` | 精神崩溃 |
| 足交 | `footjob, foot fetish` | 脚部场景 |
| 肛交 | `anal, anal penetration` | 肛门场景 |
| 口交 | `fellatio, deepthroat, irrumatio, oral` | 口交场景 |
| 孕妇 | `pregnant, belly` | 怀孕场景 |
| 内射 | `creampie, cum inside` | 体内射精 |
| 排泄 | `urination, watersports` | 排尿场景 |
| Bridal 薄丝袜 + Elbow 手套 | `(bridal gauntlets:1.3), (elbow gloves:1.2), (sheer gloves:1.2), (sheer legwear:1.2), lace-trimmed gloves` | 用户要求 bridal/薄丝袜/elbow 手套 |
| 不对称丝袜 | `asymmetrical legwear, mismatched legwear, single thighhigh, single leg pantyhose` | 用户要求不对称/不同款式丝袜 |

### 组合规则
- 同页可叠加多个类型模板的标签集
- 标注的角色关系标签必须与剧情一致（如未揭示亲子关系前不注入 `incest`）

## 7.2 体位/场景标签参考

| 场景类型 | 可选标签 |
|---------|---------|
| 双人口交 | `fellatio, deepthroat, irrumatio, oral, cum_in_mouth` |
| 双人手交 | `handjob, double handjob` |
| 足交 | `footjob, two-footed footjob, toe job, presenting own foot, foot focus, sole focus` |
| 乳交 | `paizuri, breast pillow` |
| 发交 | `hairjob, head hair job` |
| 插入式 | `missionary, cowgirl position, doggystyle, mating press, spooning` |
| 后庭 | `anal, anal penetration, anal creampie` |
| 口爆 | `cum in mouth, cum swap, bukkake` |
| 群体 | `sandwiched, girl sandwich, stacked, spitroast` |
| 道具 | `vibrator, dildo, butt plug` |
| 高潮 | `ahegao, orgasm, female orgasm, multiple orgasms, squirting, urination` |
| 后戏 | `after sex, cleaning, cunnilingus, kissing` |
---

# 八、LoRA 触发词系统

## 8.1 概述

ANIMA3 工作流通过 LoRA（Low-Rank Adaptation）模型实现特定性行为/服装触发。每个 LoRA 有专属触发词，**必须**在 tag 行指定位置注入才能激活对应效果。

| LoRA 类型 | 触发词 | 用途 | 互斥规则 |
|-----------|--------|------|---------|
| Footjob | `uxsFJ` + `(under-stirrup footjob:1.3)` | 踩脚袜/足交场景 | 与 `vaginal` / `anal` / `sex` 不兼容 |
| 开宫/Cerpe | `cerpe` + `(cervical penetration:1.3)` + `(uterus:1.2)` | 宫颈穿透/深度内射场景 | 仅阴道插入 |

**注意**：`uxsFJ`, `uncensored`, `no mosaic` 由脚本自动注入 tag 行首，但 `uxsFJ` 仅在 footjob 页才自动出现。Cerpe 场景的 `cerpe` 需要手动置入。


### 触发条件
- 场景涉及踩脚袜（stirrup legwear）足交
- 角色穿踩脚袜 + 鞋脱一旁
## 8.2 Footjob LoRA — uxsFJ
### 强制标签位置
```
1girl, uxsFJ, (under-stirrup footjob:1.3), footjob, (stirrup legwear:1.3), unworn shoes, 1boy, ...
```
- `uxsFJ` **必须紧接** `1girl` 后
- `(stirrup legwear:1.3)` 加权重防误识别为普通袜，不得写为 `thighhighs`
- 必须同时加入 `unworn shoes`（鞋脱一旁）
- 不得使用 `vaginal` / `anal` / `sex` 标签（与 uxsFJ LoRA 冲突）

### 全标签序列
```
1girl, uxsFJ, (under-stirrup footjob:1.3), footjob, presenting own foot, 1boy, <角色tag>, <发色> hair, <眼>, <身体特征>, <上衣>, <下装>, (stirrup legwear:1.3), (elbow gloves:1.2), (bridal gauntlets:1.3), <鞋类:unworn shoes / open-toe boots / open-toe shoes>, penis/penis focus, foot focus, <体位>, <镜头>, <表情>, <场景>, <细节>
```

### 鞋类替换规则（足交场景）
足交页面中，如果角色原设穿 boots/shoes，**必须替换为露趾版**以展示脚趾动态：

| 原标签 | 替换为 | 说明 |
|--------|--------|------|
| `black boots` | `(black open-toe boots:1.2)` | 替换为露趾黑靴 |
| `white boots` | `(white open-toe boots:1.2)` | 替换为露趾白靴 |
| `shoes` / `high heels` | `(open-toe shoes:1.2)` | 替换为露趾鞋 |
| `unworn shoes` | 保留不变 | 鞋脱一旁的标签不动 |

### NL 描述要点（强制）
- 必须写 `her shoes left aside, soles exposed`
- 袜底带勒入脚心（taut/binding/gripping）
- 脚底包裹阴茎的具体动态

### 体位多样性
从 qwen anima footjob.md 的 30 种足交体位选取：
- 后入足交（doggystyle, legs together, two-footed footjob）
- 仰卧抬腿式（missionary, legs up, two-footed footjob）
- 坐姿面对面（sitting, spread legs, two-footed footjob）
- 女上位反向足交（reverse cowgirl, sitting on penis）
- 站姿弯腰（standing, bent over, two-footed footjob）
- 侧躺夹脚（spooning, one leg up, two-footed footjob）
- 69 足交（sixty nine, footjob）
### 8.3+ Bridal 薄丝袜与 Elbow 手套标签注入

**触发条件**：
- 用户明确要求 bridal/薄丝袜/透明手套/蕾丝手套
- 或 caption 中出现 "bridal"、"sheer"、"lace"、"thin pantyhose" 等描述

**强制标签位置**：
```
1girl, (bridal gauntlets:1.3), (bridal veil:1.2), (elbow gloves:1.2), (sheer gloves:1.2), (sheer legwear:1.2), lace-trimmed gloves, ...
```
- `(bridal gauntlets:1.3)` 或 `(bridal legwear:1.3)` 必须出现在服装槽位，加权重防样式错误
- `(bridal veil:1.2)`（婚纱头纱）在 bride/婚礼主题时添加，加权重防止 AI 省略
- `(elbow gloves:1.2)` 必须出现，且不得与 `latex gloves` / `leather gloves` 同页
- `(sheer gloves:1.2)` / `(sheer legwear:1.2)` / `lace gloves` 至少出现一项以强化薄透感

**NL 描述要点（强制）**：
- 必须写 "thin bridal sheer gloves extending to the elbows of the female, delicate lace trim at the cuffs"
- 必须写 "translucent pantyhose clinging to the legs, sheer fabric revealing skin tone beneath"
- 严禁出现 "leather"、"latex"、"rubber"、"plastic"、"shiny synthetic" 等词汇

## 8.3 开宫/Cerpe LoRA — cerpe


### 触发条件
- 场景涉及深度阴道插入、宫颈穿透、子宫内射
- 角色的腹部被阴茎顶起可见隆起

### 强制标签位置
```
1girl, cerpe, (cervical penetration:1.3), (uterus:1.2), deep penetration, (stomach bulge:1.2), bulge, 1boy, ...
```
- `cerpe` **必须紧接** `1girl` 后
- `(cervical penetration:1.3)` 加权重确保宫颈穿透效果正确触发
- `(stomach bulge:1.2), bulge` 在 `deep penetration` 后（龟头顶起腹部轮廓，非圆润孕肚）
- 可选追加：`stomach bulge grab`, `grabbing another's stomach bulge`, `hand on another's stomach`, `hand on own stomach`

### 角落横切面规则
标签行加 `inset`（不用 `cross-section` 标签 - 会污染主画面）

NL 末尾加固定句：
```
A cross-section diagram in the corner of the image shows a side view of the cervical penetration, with the male's glans forcing through the female's cervix and lodging deep inside the uterus. The main scene remains a normal external view with no transparent or diagram overlay.
```

### 适合体位
| 体位 | 标签 | 备注 |
|------|------|------|
| 仰卧抬腿式 | `missionary, legs up, raised hips` | 最推荐 |
| 女上位深插 | `cowgirl position` | 角色掌控深度 |
| 后入深插 | `doggystyle, from behind` | 从后方深入 |
| 压腿式 | `missionary, legs pressed, knees to chest` | 最大化深度 |
| 肩扛式 | `legs over shoulder` | 深度插入 |

### 身体反应标签
- 表情：`ahegao, rolled eyes, pleasure face`
- 呼吸：`heavy breathing, panting`
- 身体：`twitching, shaking, trembling`
## 8.4 双 LoRA 场景


在同一故事线中，足交是前戏，开宫是正戏高潮。两者**不会同时激活**：

1. 足交场景页：使用 `uxsFJ` LoRA，禁用 `vaginal/anal/sex`
2. 过渡页（从足交到插入）：不激活任何 LoRA 或仅用常规标签
3. 开宫场景页：使用 `cerpe` LoRA，启用 `vaginal/sex`

**绝不同页激活两个 LoRA**：`uxsFJ` 与 `cerpe` 在标签语义上冲突（一个禁 vaginal，一个需要 vaginal），同页加载会导致生成结果不可控。

---