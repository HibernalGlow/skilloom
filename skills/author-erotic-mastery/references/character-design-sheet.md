# 跨模态角色设计与描述锚定规范 (Character Consistency & Design Sheets)

> 本文件是 `author-erotic-mastery` 技能的专项深入参考文件。当且仅当需要为角色建立**视觉资产卡、生成转动三视图/表情图、或在 ComfyUI / FLUX / anima-storyboard 中撰写生图提示词**时加载。

---

## 一、角色描述锚定块规范 (Description Anchor Technique)

每个核心女主必须拥有一段 **50+ 字的标准锚定块**。在生成该角色的任何画面（无论是立绘、四向图、还是色情分镜）时，**必须全量复用该锚定块**，仅修改动作、姿势与体位：

```text
[年龄/体型比例] [核心发型: 颜色, 超长发型, 严禁短发] [眼眸颜色]
[肤质: 极白/光滑], [标志性服饰: 兔女郎/逆兔女郎/女仆/连体白丝]
[袜类: (white stirrup legwear:1.3), 露出脚趾与脚跟, 中等厚度]
[配件: (white bridal gauntlets:1.2), 颈部细带choker]
```

---

## 二、角色设计一致性四件套 (Four Consistency Sheets)

为长期创作项目（如《姐姐爱上我》、《棉花糖》、ANIMA3）建立角色视觉档案时，需产出以下四张标准 Sheet：

1. **多向转动视图 (Turnaround Sheet)**：正视 (Front)、侧视 (Side)、3/4 视、背视 (Back)。
2. **六大核心情欲表情图 (Expression Sheet)**：
   - 平静清冷 (Neutral)
   - 羞恼傲娇 (Flustered/Tsundere)
   - 痛楚咬唇 (Lip-biting Pain/First Touch)
   - 突破绝顶/瞳孔失焦 (Ecstasy/Heart-eyes)
   - 断续呜咽 (Sobbing Pleasure)
   - 事后瘫软失神 (Post-coital Bliss)
3. **高色度服饰矩阵 (Outfit Sheet)**：日常居家长卫衣/吊带裙、逆兔女郎装、白丝女仆装、极深开叉连体衣。
4. **标准色彩调色板 (Color Palette)**：指定发色、瞳色、纯白丝袜光泽、微粉足尖色彩 Hex 码。

---

## 三、Prompt 与文学双向映射表

| 小说文学描写意象 | ComfyUI / Danbooru 权重标签映射 | 作用与约束 |
|---|---|---|
| **踩脚白丝（40D-70D）** | `(white stirrup legwear:1.3), (toeless legwear:1.2), unworn shoes` | 强制生成露趾踩脚结构，权重 1.3 避免 AI 漏画系带 |
| **踩脚袜足交（成箍/足穴）** | `(under-stirrup footjob:1.3), footjob, sole` | 原生 Danbooru 动作标签，锁定踩脚带下顶入 |
| **开宫突破与下腹凸起** | `(cervical penetration:1.3), (stomach bulge:1.2), deep penetration` | 锁定子宫口深入与腹部肉包隆起反馈 |
| **白丝长手套（手足同构）** | `(white bridal gauntlets:1.2), finger seams` | 锁定长手套同构成箍，与踩脚袜呼应 |
| **超长发与发交** | `(super long hair:1.2), very long hair, hairjob` | 锁定长发垂地与发丝缠绕互动 |
| **逆兔女郎装 / 乳胯垂帘** | `reverse bunnysuit, (breast curtains:1.1), (pelvic curtain:1.1)` | 高色度大面积露腹与腰部镂空 |
| **第三人推车助攻** | `group, 2girls, assisting, pushing hips` | 多女同场加压体位 |
