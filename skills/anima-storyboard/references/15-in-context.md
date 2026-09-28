# 补充篇 E：In-Context 参考图出图（无角色 LoRA 时的外观搬运）

> 2026-09-28 引入。来源：`碧蓝航线_拉菲II` 和服皮肤（LF042–LF060）实跑全过程。
>
> **解决的问题**：角色/服装在 anima 线**没有任何角色 LoRA**（只有 illus/SDXL 线的 LoRA，架构不通用）时，
> 怎么把官方服装结构搬进画面 —— **不训 LoRA、不写角色触发词**。
>
> ⚠️ **但先读 §15.1b**：这套皮肤最后**证明根本不需要 in-context**（底模原生就认识）。
> 建装置之前先花 25 秒做那个测试 —— 本轮整套装置（参考图支路、`end_percent` 逐页表、
> 参考图卫生、3 倍 token、每页 57s、3.8 GB 显存残留）事后看有相当一部分可以省掉。
>
> **一句话结论**：in-context 是「用参考图代替角色 LoRA」的手段 ——
> **只在「模型确实不认识这个皮肤」时才需要**。机制 LoRA 必须挂（但漏挂不报错，见 §15.3）；
> 参考帧会被**拼进注意力序列**（2 张参考 = 3 倍 token），所以显存与耗时都由
> **参考张数 × 生成分辨率**决定，而不是由你调什么“参考图分辨率参数”决定。

---

## 15.1 何时用 in-context（与规则 0c 的分工）

> ⛔ **先用 §15.1b 验证「是不是真的需要」。** 下表只回答“没有角色 LoRA 时用什么”，
> 不回答“模型是不是已经认识了”—— 后者得测。

| 情形 | 手段 |
|------|------|
| 第 1/2 批老角色（底模原生认识） | 不挂角色 LoRA，标签直接写 |
| 第 3 批新角色，**有** anima 线角色 LoRA | 挂角色 LoRA（§14.1） |
| 角色/服装**没有** anima 线 LoRA（新皮肤、新形态、冷门角色） | **先做 §15.1b 测试**；确实不认识才上 in-context 参考图 |
| 只需要**风格** | 画师 LoRA（`quality_prefix` 里的 `@artist`） |

**边界**：
- in-context 负责**外观（角色长相 + 服装结构 + 配饰颜色）**，不负责风格 → 画师 LoRA 照常挂。
- in-context **不是「角色 LoRA」**，页面 `[tags]` 里**不写**任何“in-context 触发词”（**它没有触发词**）。
  但它自带一个**机制 LoRA**（`anima-incontext-character.safetensors`，权重 1.0）——
  这个**必须挂**，见 §15.3。
- 参考图能搬来的东西**有上限**：想还原的每一件衣服/配饰/颜色，**必须至少出现在一张参考图里**。
  参考图里没有的元素，模型只能靠标签自己编。

---

## 15.1b ⭐ 建装置之前：先花 25 秒测「模型是不是本来就认识这个皮肤」

**这是本篇最重要的一条流程改进。** 本轮为拉菲II 和服皮肤搭了整套 in-context（2 张参考图、
逐页 `end_percent` 表、参考图裁切与防复印、3 倍 token、每页 57s、3.8 GB 显存残留）——
**最后发现底模原生就认识这套皮肤，参考图不是必需的。**

### 怎么测（一次 ~25 秒，零风险）

把这一页**照原样跑一遍，但不给参考图** —— 不需要改图结构，只要把 `AnimaInContextApply` 的
**`strength` 设为 0**。节点作者已实机验证：`strength <= 0` 会**整个跳过拼接**，
输出与普通 T2I **bit 级一致**。所以这是一个干净的「无参考图」模式。

```bash
# 与正式跑批完全相同的参数，只加 --strength 0
tools/run_xxx.py --only LF052 --mode single17 --sampler-node fls --artist <画师> \
                 --strength 0 --model-tag noref
```

**至少跑 3~4 个不同 seed**（单 seed 的“对了”可能只是运气；本轮 4 个 seed 全对才算数）。
无参考图 = 没有 3 倍 token，一次约 **25 秒**（有参考图是 57 秒）。

### 看什么：提示词各层各负责什么

| 层级 | 负责什么 | 本轮的实测答案 |
|---|---|---|
| **皮肤名标签**（`角色 (皮肤名) (作品)`） | 服装**整体结构**（和服/腰带/里衬/袜鞋） | ✅ **主要靠它**。去掉它 → 退化成近似款（金圆花没了） |
| **补充服装标签**（`black kimono / obi / pom pom / fur trim / clog sandals`） | 补充结构名词 | ✅ 提供骨架 |
| **服装 NL（自然语言段）** | **单件配饰**的精确形状/颜色 | ✅ **兔子面具靠它**：去掉 NL → 面具变黑；有 NL → 白面红颊 **4/4 seed 正确** |
| **参考图** | 贴近官方立绘的**画风与比例** | ⚠️ 只是增量，**不是必需** |

### 判定

- **4 个 seed 服装都对** → 🎉 **不要建 in-context**。省掉：参考图支路、逐页 `end_percent`、
  参考图卫生、3 倍 token、更高的显存峰值、每页 57s → **25s（2.3×）**。
- **服装结构错 / 缺件** → 才需要参考图，再按 §15.2 往下搭。
- **只有单件配饰错**（如面具颜色）→ 先补**那件配饰的 NL 句子** + 加权标签 + 负面，
  **不要**为了一件配饰去挂 2 张参考图。

### 三个必须注意的前提

1. **结论是逐「底模 × 画师 LoRA × 皮肤」的，不能推广。** 同一套标签换底模就变
   —— 本轮同一页在 silvermoon 上与 kirazuri 上表现完全不同（见 §15.3 的失效形态表）。
   **必须在你真正要用的底模 + 画师 LoRA 上测。**
2. **画师 LoRA 会跟皮肤知识打架。** 实测 `@atdan` 会给这套皮肤加官方没有的品红里衬、
   把袖面圆花画成花草纹。所以“模型认识”要连同画师 LoRA 一起测。
3. **别拿历史产物当证据。** 本项目早先那批“纯标签出成深蓝樱花和服”的图，实际用的是
   **另一个底模（silvermoon INT8）+ @atdan + 一个动作 LoRA + 双层采样 + 固定 seed**，
   与现行配置**不可比**。要下结论必须读出旧图的**内嵌工作流**核对变量
   （PNG 的 `tEXt` chunk 里 `prompt` 字段），否则会把“配置差异”误判成“模型不认识”。

> 证据：`Outputs/拉菲II/incontext_kimono_double/_evidence/cmp_noref_decomp.png`（四层拆解）
> + `_evidence/cmp_noref_seeds.png` / `cmp_noref_nl_seeds.png`（各 4 seed）。

---

## 15.2 机制（源码级事实，`comfyui-anima-incontext`）

节点三件套：`AnimaRefEncode` → `AnimaRefLatentBatch` → `AnimaInContextApply`。

### 参考帧是拼进序列的，不是旁路

```python
x_cat = torch.cat([x, r], dim=2)            # 生成帧 + N 张参考帧
state.total_tokens = (T + n_ref) * tpf      # tpf = 每帧 latent token 数
```

**这就是 3 倍注意力开销、也是它比普通出图慢的根因。**

| 生成分辨率 | 每帧 token `tpf = (W/16)×(H/16)` | 1 张参考 | 2 张参考 | 普通出图 |
|---|---|---|---|---|
| 832×1216 | 52×76 = **3952** | 7904 | **11856（3×）** | 3952 |
| 704×1024 | 44×64 = **2816** | 5632 | **8448（2.1×）** | 2816 |
| 640×936 | 40×58 = **2320** | 4640 | **6960（1.8×）** | 2320 |

### `target_width/height`：不影响显存/速度，但设错会白丢细节

`AnimaInContextApply` 会把参考 latent **双线性插值到生成网格**
（`incontext.py`：`F.interpolate(r, size=(H, W))`），而 `target_width/height` 是在**像素层**
先缩放再 VAE 编码（`nodes.py`：`_fit_pixels_white_pad`）。

**关键区分（容易说错）**：

| 设成 | 影响 token/显存/速度？ | 影响画质？ |
|---|---|---|
| ≠ 生成画布 | ❌ **不影响**（token 数只看生成网格） | ✅ 影响 —— 多付一次 latent 重采样，白丢细节（放大丢不了、缩小丢得掉） |
| = 生成画布 | ❌ 不影响 | ✅ 最优 —— 恰好不用插值 |

```
参考分辨率 < 生成画布 → latent 被放大，白丢细节 + 多一次插值
参考分辨率 > 生成画布 → latent 被缩小，多出的细节被丢掉，只白花编码时间
参考分辨率 = 生成画布 → 恰好不用插值   ← 唯一正解
```

> 所以「降参考图分辨率能提速」是**假的**（实测 512×768 与 832×1216 总耗时无差异，
> 差异来自热漂移）。节点作者原话：*"Set these to the generation resolution to avoid any
> latent-space resampling at sampling time."*（引擎文档 `INCONTEXT-BATCH-REQ.md` 写成
> 「必须等于该页生成分辨率，否则 latent 尺寸错位」—— 说法偏重，机制上不会「错位」，
> 只是白丢一次插值。结论一致：**设成相等**。）
>
> **想降显存只有两条路**：降生成分辨率，或减参考张数。

---

## 15.3 必需接线（漏一个就出黑图）

```
UNETLoader
  → LoraLoaderModelOnly  (anima-incontext-character @1.0)   ← ⛔ 必需！机制 LoRA
  → LoraLoaderModelOnly  (Turbo-v0.2 @0.8)
  → LoraLoaderModelOnly  (Highres Aesthetic Boost @0.48)
  → LoraLoaderModelOnly  (画师 LoRA，如 modare/anime_modare @1.0)
  → AnimaInContextApply  ← ref_latent 来自参考支路；cond_only=true, ref_timestep=0.0
  → KSampler / FLS_SamplerV4

参考支路：
  LoadImage → AnimaRefEncode(target_width/height = 生成画布) ┐
  LoadImage → AnimaRefEncode(target_width/height = 生成画布) ┴→ AnimaRefLatentBatch(fit_mode="pad")
```

### ⚠️ 机制 LoRA：不是「必需件」，是「品质件」—— 但不挂等于白跑（2026-09-28 A/B 实测）

**节点代码从不检查这个 LoRA。** 只接参考帧、不挂机制 LoRA，**照样出图、不报错、不黑屏**。
但输出是**病态**的，而不是"稍微差一点"。

**失效形态随底模而变**（两种都已实测，同页同 seed）：

| 底模（**无**机制 LoRA，2 参考 @704×1024） | 结果 |
|---|---|
| **kirazuri v4 INT8-convrot** | ❌ 整张图被**周期性黑色方块/短棒**覆盖 —— 按 DiT patch 网格排列（约 16 px 周期）+ 白点，像棋盘状盐椒噪声 |
| **silvermoon v23 INT8_fixed** | ❌ 画面**干净但内容错** —— 把参考角色**连姿势带服装整套复印**，官方立绘的**白背景/白毛绒糊满画面**（README 说的「背景崩壊」），提示词里的 `doggystyle / insertion` **完全没发生** |

**这不是采样器/步数/参考张数问题**（已逐一排除）：

| 变量 | 结果 |
|---|---|
| `FLS_SamplerV4` vs 原生 `KSampler` | 都复现同样的黑格 |
| 17 步 `dpmpp_2m_sde/beta57` vs 30 步 `er_sde/simple` CFG 4.0 | 都复现同样的黑格 |
| 2 张参考 vs 1 张参考 | 都复现（黑格与参考张数无关） |
| 同 seed、挂着 LoRA 重复跑两次 | **输出字节完全相同（sha256 一致）** → 证明 A/B 是严格单变量 |

**为什么**：`AnimaInContextApply` 只负责**按契约把参考帧拼进 T 轴**；
模型侧要「读懂多帧序列」靠的是这个 LoRA —— 它是 kohya 格式 rank64/α32，
由 `training/anima_incontext_train_network.py` 按**同一份契约**训练（
参照帧在后、参照帧 t=0、latent 已 `process_latent_in`、损失只算生成帧、
训练对 = 同角色**不同**出典）。没有它，等于给一个只会单帧 T2I 的模型
硬塞多帧序列。

节点自己的文档原话：*"Combine with an in-context reference LoRA trained with the same
contract **for full effect**."* —— **for full effect**，不是「必需」。

**而且降 strength 也换不回中间态**：官方 README 实测
*「strength を下げても中間にはならず画質が劣化するだけ」*（降强度不会变成中间态，只会画质变差）。

> **实战结论**：**必须挂，权重只能是 1.0（它没有触发词）。**
> 但要认清失败现象 —— 它**不会报错、不会黑屏**，只是「图还是出得来，但满屏黑格 / 全在复印」。
> **不能靠报错来发现漏挂**，所以这条必须进定稿自检。
>
> 证据：`Outputs/拉菲II/incontext_kimono_double/_evidence/AB_ctxlora_四联对照.png`
> （① 挂 LoRA ② 不挂·kirazuri ③ 不挂·kirazuri 30 步 ④ 不挂·silvermoon）
> + `_evidence/AB_ctxlora_100pct黑格.png`（100% 黑格放大）。

### 单参考的接法

`AnimaRefLatentBatch` 的**两个槽位都是必填**，不能只填一个。要单参考就**绕过它**，
把单个 `AnimaRefEncode` 的输出直接喂给 `AnimaInContextApply.ref_latent`：

```python
node["inputs"]["ref_latent"] = ["13", 0]   # 直接指向 AnimaRefEncode
# 删除多余节点：LoadImage(脸部)、AnimaRefEncode(脸部)、AnimaRefLatentBatch
```

---

## 15.4 参考图选择的铁律

| # | 规则 | 原因（实测） |
|---|------|-------------|
| 1 | **服装权威源必须用官方立绘** | 同人画师会改设定。第 1 轮用 danbooru 最高分同人图，画师把腿画成裸腿，caption 照抄成 `bare legs`，出图忠实给出裸腿 —— **和官方设定（白镫袜）相反**。分数高 ≠ 设定准。 |
| 2 | 标准组合 = **2 张、不同来源** | ① 全身官方立绘（服装结构权威）② 脸部特写（头饰/五官细节最清楚）。 |
| 3 | 想还原的每一件东西都要在参考图里出现 | 参考图里没有的配饰，模型只会编。 |
| 4 | 参考图分辨率 = 生成画布 | 见 §15.2。 |
| 5 | 先查参考图池有多深 | 冷门皮肤 danbooru 可能只有十几张、官方立绘只有 1000×1500。池浅时别指望高清参考。 |

**官方图来源优先级**：游戏官方 wiki（如 biligame `patchwiki`）→ danbooru `official_art` 标签 →
官方宣传绘。danbooru **API 主机**常需代理（`-x http://127.0.0.1:7890`），但 **cdn.donmai.us 直连**。

---

## 15.5 采样配方与步数/分辨率梯度（8GB 4060 Laptop 实测）

**基线配方** = 线上预设 **`anima-single-17`**（`gen_presets.json`，3 seed 对照里唯一 0 坏格）：

```
steps 17 / cfg 1.6 / dpmpp_2m_sde_gpu / beta57 / denoise 1.0
LoRA = Turbo-v0.2 @0.8 + Highres Aesthetic Boost @0.48
采样器节点 = FLS_SamplerV4（fovea_strength 3.0 / sharpness 0.5 / mask_inertia 0.85）
```

### 步数梯度（同一足部特写页、同 seed、832×1216）

| 步数 | 耗时 | 足部结果 |
|---|---|---|
| 6 | 40s | ❌ 崩 —— 脚是一坨粉色肉块，无脚趾 |
| 8 | 48s | ❌ 崩 —— 无脚趾，与旁边毛绒糊在一起 |
| **10** | 64s | ⚠️ 可用但**脚趾偏软**（下限） |
| 12 | ~70s | ✅ 好，5 个脚趾清晰带光泽（**稳妥线**） |
| 13 / 15 | 64~72s | ✅ 好，与 17 看不出差别 |
| 17 | 96s | ✅ 基线 |

> **画像结论**：**下限 10、稳妥线 12、15 = 17 且省 25%**。
> ⚠️ 步数掉质**最先暴露在脚趾/手指**上（细节最密的小结构）。**足部特写页（footjob 等）
> 千万不要压到 10 步**，那是唯一肉眼可见掉质的地方。

### 分辨率梯度（15 步）

| 分辨率 | 耗时 | 质量 | token（2 参考） |
|---|---|---|---|
| 832×1216 | 72s | ✅ 最好，发丝/眼睛细节满 | 11856 |
| **704×1024** | **48s** | ✅ **可接受**，脸清晰、无明显掉质 | 8448 |
| 640×936 | 40s | ⚠️ 明显变软，发丝糊、眼睛细节掉 | 6960 |

> **生产建议：15 步 + 704×1024 = 48s/页**（相对 17 步 + 832×1216 的 96s **快一倍**）。
> 保守档：15 步 + 832×1216 = 72s（画质同基线）。
> **640×936 不建议** —— 那是唯一肉眼可见的掉质，而且**面具类配饰开始偏形**（见 §15.8）。

---

## 15.6 `end_percent`：参考图姿势旋钮

`end_percent` 控制 in-context 影响**持续到去噪的百分之几**。

**原则**：参考图是**站姿官方立绘**时 —— 姿态越强的页面越要**压低**，
少"复印"参考姿势、多听页面标签。

| end_percent | 适用页面 |
|---|---|
| **0.85** | cowboy shot / close-up（与参考同尺度，可高） |
| **0.78** | 半身偏强姿态 |
| **0.75** | 全身过渡姿势 |
| **0.72** | full body / 躺姿 / 强姿态（doggy style、mating press、足部特写） |

> 逐页可覆盖：作品配置里用 `[[page_canvas]]` 逐页写 `end_percent`，
> 不写的页沿用 `[incontext].end_percent` 的默认值。改一个数改一行，整段删掉即退回单值。
>
> ⚠️ `end_percent` 太低（< 0.7）参考图的作用会被削掉，服装结构可能搬不过来；
> 太高（≈1.0）则强姿态页会被"钉"在参考的站姿上。

---

## 15.7 显存管理（多会话共用一个 ComfyUI 时的纪律）⛔

### 实测数字（8GB 4060 Laptop / 832×1216）

| 时刻 | 显存 |
|---|---|
| `POST /free` 之后（真·空闲） | **179 MiB** |
| 2 张参考任务峰值 | **5077 MiB** |
| 1 张参考任务峰值 | **4699 MiB** |
| **任务跑完、进程还在** | **3831 MiB 不放** ← 真正的杀手 |

### 三个结论

1. **杀手是「模型常驻」，不是单次峰值**。跑完一页后 UNET 赖在显存里，
   下一个任务进来就要跟它挤 —— 超过 `总量 − reserve-vram` 就开始**部分卸载到内存** →
   你说的"变慢"就是这么来的。
2. **残留量只由 UNET 决定，与参考张数无关**（2 张残留 3831、1 张残留 3885）。
3. **把文本编码器搬到 CPU 没用**。`qwen_3_06b_base` 是 0.6B，只在 prompt 编码那一瞬用，
   在峰值 5 GB 里是零头。

### 修法

| 层级 | 动作 |
|---|---|
| **跑批脚本（必做）** | 每页结束 `POST /free {"unload_models":true,"free_memory":true}` —— 跑批一律开 |
| 服务端（可选） | `--reserve-vram` 从默认 0.5 提到 **1.5** —— ComfyUI 会更"整体卸载"而不是"部分卸载" |
| 可选省时 | **单参考**：峰值 −378 MiB、耗时 80s→48s（−40%）。质量实测未见掉（脸/服装/姿势全对），但样本少 |

> ⚠️ **共用算力端的铁律**：只删**自己**的队列任务，绝不动别人的；
> 跑批前后 `/free`，把显存还给对方。这会直接影响多会话协作的体感。

---

## 15.8 提示词结构与两个必踩的坑

### 正确结构（对齐用户已验证的批）

```
quality_prefix（画师触发词 + masterpiece/best quality/aesthetic/highly detailed + uncensored）
<tags1>     ← 角色外观/服装结构
<tags2>     ← 行为/玩法标签（1boy, faceless male, penis, doggystyle, insertion…）
[caption]   ← 玩法/动作的自然语言描述，永远在最后（最高 recency）
```

### 坑 1：评分词写成了 `safe` → 全篇变 SFW ⛔

`safe` 是 Danbooru 的 **SFW 评分标签**，写在正向里会**压过页面所有露骨标签**。
用户的约定是 **`uncensored`**（由脚本注入到 tag 行首）：

```
✅ master.., best quality, aesthetic, highly detailed, @modare, uncensored
❌ master.., best quality, aesthetic, highly detailed, @modare, safe     ← 全篇变 SFW
```

> 评分由**正向的 rating tag** 承担。`uncensored` 由脚本自动注入，页面的 `[tags]` 里**不写**评分词。

### 坑 2：把整段服装 NL 追加到提示词**末尾** → 玩法消失 ⛔

服装 NL 描述（1000+ 字符）追加在提示词最后，就占住了**最高 recency** 的位置，
模型只画"穿这身衣服的少女"，中间的行为标签被埋掉 → **全篇只有姿势、没有玩法**。

```
❌ quality → tags1 → tags2(玩法) → [1300 字服装 NL] → caption     ← 玩法被压掉
✅ quality → tags1 → tags2(玩法) → caption                        ← 玩法在最后
```

**修法**：把服装 NL 砍成"只留参考图看不出的颜色/材质"（结构词已在 `tags1` 里），
或者干脆关掉（`off`）。**caption 永远在最后**。

> 判断口诀：**画面里"没有玩法"时先看提示词末尾是什么。** 末尾如果是外观描述，
> 那就是它把玩法挤掉了。

---

## 15.9 旋钮代价排序（出图打样必遵）⭐

**在同一 seed 下：**

```
负面  <  标签  <  参考图  <  NL(caption) 描述
（代价小）                              （代价大）
```

- 改 **NL 一句话的代价 ≈ 换一张图**：同一 seed 下改服装 NL，**整张图的构图/配色会重排**。
- 只想动**一个部位**时，优先用**负面词**或**加权标签**，别去改 caption。

### 案例：兔子面具被画成狐面

| 轮次 | 动作 | 结果 |
|---|---|---|
| 第 3 轮 | 改 NL（把 "rabbit mask" 展开成长句 "round rabbit face… clearly a rabbit and not a fox mask"）+ 负面加词 | 形状变兔子 ✅ **但颜色翻成黑色**，肩上白毛围脖缩到袖口、腰带长出红衬带 —— **整张图重排**（同 seed） |
| **第 3b 轮** | **提示词一字不改**，只在负面加 `fox mask, kitsune mask, hannya, oni mask` | 白面具 + 兔形 ✅，袖面金圆花也更贴官方，**其余全部保持** ← **这个旋钮才对** |

> 同理，**头饰必须单独、明确描述**（"round white rabbit mask with dot eyes and a big red cheek patch"），
> 不写就会画成狐面/大白面具。

### 参考图自身带来的偏差（要写进负面或标签）

官方立绘背景里的道具会被画进画面 → 负面压 `stuffed animal, plushie, rabbit plush, toy`。

---

## 15.10 底模 A/B（同 seed，唯一变量）

换底模 = **同 seed 也不同构图**，所以只有**先天倾向**可比（配饰形状、脸型、色调），构图/姿势差异**不算输赢**。

| 项目 | kirazuri v4 | silvermoon_fixed |
|---|---|---|
| 兔子面具 | ✅ 圆兔脸 | ❌ 又变回狐面/能面 |
| 脸型 | ✅ 圆润，贴官方（幼态角色） | ⚠️ 偏窄偏成熟 |
| 色调 | ✅ 柔和通透 | ⚠️ 对比强 |
| 里衬/腰带/大腿皮带细节 | ⚠️ 弱 | ✅✅ 最贴官方 |

**裁决**：**配饰形状与脸型是底模先天倾向，改词很难扭**；里衬颜色等**细节是提示词层面能补的**。
→ 选先天倾向对的那个，把另一个的强项写进标签/负面。

> A/B 必须核对 PNG 内嵌工作流，确认**除 UNET 外逐项一致**（参考图、seed、采样器、全部 LoRA）。

---

## 15.11 跑批纪律

1. **网络抖动不该杀死 19 页的批**：API 调用加**重试**（6 次 + 退避），
   隧道断了就重开 `ssh -N -L 8188:127.0.0.1:8188 <host>`。
2. **提交前先看队列**：别人的任务在前就排在后面等，**不要**为了自己快而清别人的队列。
3. **失败/废弃产物要隔离**：建 `_broken_<原因>/` 目录挪走，别和成品混在一个文件夹里，
   文件名带上原因（如 `_broken_missing_ctxlora`）。
4. **文件名带口径**：`<页号>_<画师>_s<步数>_<W>x<H>_<采样器节点>[_<底模标签>].png` ——
   事后能一眼看出这张是什么配置。
5. **改口径要整批一致**：中间切参数会导致同一本里混两套口径；要切就整批重跑（或明确记录分界页）。
6. **同页可复现**：`seed = seed_base + 页号`。

---

## 15.12 定稿自检（in-context 专用）

**搭装置之前（先做这个）：**

- [ ] **做过 §15.1b 的「无参考图」测试吗（≥ 3 个 seed）？**
      模型原生就认识 → **就别搭这套装置**（省 2.3× 时间 + 一整套参数与参考图卫生）。
      有单件配饰不对 → 先补该配饰的 NL 句子，而不是上参考图。

**搭了装置之后：**

- [ ] 机制 LoRA `anima-incontext-character` 挂了吗、权重是 1.0 吗（**漏挂不会报错**；现象是黑格或复印机，见 §15.3）？
- [ ] 参考支路接法对吗（2 参考 = 走 `AnimaRefLatentBatch`；1 参考 = 绕过它）？
- [ ] 参考图是**官方立绘**吗（服装权威源）？想还原的每件东西都在参考图里吗？
- [ ] `target_width/height` = 生成画布吗？
- [ ] `end_percent` 与这一页的**姿势强度**匹配吗（强姿态页压低）？
- [ ] 正向评分词是 **`uncensored`** 而不是 `safe` 吗？
- [ ] 提示词**末尾是 caption（玩法）**，不是服装 NL 吗？
- [ ] 跑批开 `--free-between`（每页 `/free`）了吗？
- [ ] 足部/手部特写页的步数 ≥ 12 吗（10 步脚趾会软）？

---

## 15.13 参考实现

| 用途 | 路径 |
|------|------|
| 机制节点源码 | `custom_nodes/comfyui-anima-incontext/incontext.py`、`nodes.py` |
| 机制 LoRA | `models/loras/anima/anima-incontext-character.safetensors`（1.0，无触发词） |
| 作品配置（耐久记录） | `Workflows/wild/storyboard/<作品>/incontext/incontext.toml` |
| 单作品实跑脚本 | `Workflows/wild/storyboard/<作品>/incontext/run_*.py`（图构建 + 提交 + 取回） |
| 产物目录 | `Outputs/<作品>/incontext_<皮肤>/` |
| 采样预设 | `ComfyUI-Workflow-Studio/data/gen_presets.json` → `anima-single-17` |
| 本轮证据（无参考图拆解 + 多 seed） | `Outputs/拉菲II/incontext_kimono_double/_evidence/cmp_noref_*.png` |
| 本轮证据（机制 LoRA A/B） | `Outputs/拉菲II/incontext_kimono_double/_evidence/AB_ctxlora_*.png` |
