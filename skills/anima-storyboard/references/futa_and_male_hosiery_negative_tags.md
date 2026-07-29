# 负面标签参考（禁止词表）

从 `tag.sqlite` / `tag dict.tsv` 检索的应禁止/排除标签。

---

## 一、Futa / 扶她类（必须禁止）

用于 hetero male-on-female 场景，禁止任何扶她内容。

### 核心标签

| 标签 | 中文 | 数量 | 说明 |
|---|---|---|---|
| `futanari` | 扶她 | 47,174 | 核心—有阴茎的女性 |
| `implied futanari` | 暗示扶她 | 3,353 | 暗示有阴茎 |
| `female with penis` | 有阴茎的女性 | — | 同义 tag |
| `dickgirl` | 有鸡鸡的女孩 | — | 同义 tag |
| `shemale` | 人妖 | — | 同义 tag |
| `newhalf` | ニューハーフ | — | 日系同义 |

### 扶她衍生场景

| 标签 | 中文 | 数量 |
|---|---|---|
| `futanari masturbation` | 扶她自慰 | 3,312 |
| `futanari pov` | 扶他第一视角 | 1,228 |
| `full-package futanari` | 全套扶他（阴道+阴茎） | 2,572 |
| `futa without pussy` | 扶他（无阴道） | 2,640 |
| `futa without balls` | 扶他（无睾丸） | 1,876 |
| `intravaginal futanari` | 阴道内扶他 | 379 |
| `futasub` | 扶她受 | 1,506 |

### 扶她互动

| 标签 | 中文 | 数量 |
|---|---|---|
| `futa with female` | 扶她×女性 | 22,514 |
| `futa with male` | 扶她与男性 | 4,315 |
| `futa with futa` | 扶她对扶她 | 3,127 |
| `futa on male` | 扶她对男性 | 2,169 |
| `male on futa` | 男对扶她 | 1,252 |

### 性转类（密切相关）

| 标签 | 中文 | 数量 |
|---|---|---|
| `genderswap` | 性转 | 60,028 |
| `genderswap (mtf)` | 性别转换（男变女） | 45,595 |
| `genderswap (otf)` | 性转（男变女） | 2,568 |
| `genderswap (ftm)` | 性转（女变男） | 12,114 |
| `genderswap on non-genderswap` | 非性转角色的性转 | 1,070 |
| `genderswap on genderswap` | 性转角色的性转 | 908 |

### 伪娘 / 变装类（密切相关）

| 标签 | 中文 | 数量 |
|---|---|---|
| `trap` | 伪娘 | 73,290 |
| `crossdressing` | 伪娘/变装 | 52,984 |
| `crossdressing (mtf)` | 变装（男变女） | 42,693 |
| `crossdressing (ftm)` | 女扮男装 | 4,060 |
| `otokonoko` | 男の娘 | — |
| `male with breasts` | 男性有乳房 | 936 |

### 其他相关

| 标签 | 中文 | 数量 |
|---|---|---|
| `pegging` | 逆肛交（女性用 strap-on 肛交男性） | 682 |
| `strap-on` | 穿戴式假阴茎 | 3,518 |

---

## 二、男性传丝袜类

**tag.sqlite / tag dict.tsv 中没有独立标签**专门标注"男性穿丝袜/过膝袜/裤袜"。

这类内容在 Danbooru 上由组合标签表达，常见链条：

| 组合方式 | 示例 |
|---|---|
| `crossdressing` + `pantyhose` | 变装男性 + 穿裤袜 |
| `crossdressing` + `thighhighs` | 变装男性 + 过膝袜 |
| `trap` + `pantyhose` | 伪娘 + 裤袜 |
| `male with breasts` + `pantyhose` | 男性乳房 + 裤袜 |

因无单一标签可禁止，建议在 **禁止标签规则** 中增加文字说明：

> **禁止对 1boy 行添加** `pantyhose`/`thighhighs`/`stockings`/`stirrup legwear`/`kneehighs` 等袜类标签。袜类标签仅允许出现在 1girl 行。
> 同时禁止组合：上述袜类标签 + `crossdressing`/`trap`/`genderswap` 同时出现。

---

## 三、标签添加示例

在 `SKILL.md` 禁止标签规则中加入：

```markdown
- **禁止扶她类标签**：futanari, implied futanari, female with penis, dickgirl, shemale, newhalf, futanari masturbation, futanari pov, full-package futanari, futa without pussy, futa without balls, futa with female, futa with male, futa with futa, futa on male, male on futa, futasub, intravaginal futanari
- **禁止性转/伪娘标签**：genderswap, genderswap (mtf), genderswap (ftm), genderswap (otf), trap, crossdressing, crossdressing (mtf), otokonoko, male with breasts, pegging, strap-on
- **禁止男性穿丝袜**：1boy 行禁止出现 pantyhose/thighhighs/stockings/stirrup legwear/kneehighs 等袜类标签。袜类标签仅允许在 1girl 行。
```
