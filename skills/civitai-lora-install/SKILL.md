---
name: civitai-lora-install
description: Find, verify, download and install Civitai LoRAs into the ComfyUI Anima library, then fill their trigger sidecars and preview images. Use when the user gives a civitai.com or civitai.red model link (optionally with a local downloaded file path), asks to search for a character or artist LoRA, says 装/找 LoRA, 补预览图, or needs a LoRA's base model, version, trigger words or AIR checked. Covers the DNS-poisoned network, login-gated downloads, the library's folder and sidecar conventions, and the bundled tool scripts.
---

# Civitai LoRA 安装

## Overview

把 Civitai 上的 LoRA 变成 ComfyUI 库里"能被加载器识别、有触发词、有预览图"的一员。
核心不是下载本身，而是**身份核对**与**目录/sidecar 约定**：装错 base、触发词丢失、
预览图与模型不匹配，都要到出图时才暴露。

## 适用机器

下例路径是本机（Windows 算力机）的路径。若在其他机器上执行，先确认 ComfyUI 运行时目录、
代理端口与 python 解释器位置，不要照抄。

## 硬性前提

- **网络**：`civitai.com` / `api.civitai.com` / `mcp.civitai.com` 在本机被 DNS 污染
  （解析到 `192.168.123.1` 黑洞或 Meta 段假 IP），直连表现为 `curl http=000` 超时。
  一切请求走 `http://127.0.0.1:7890`。github.com 正常，所以超时≠断网。
- **base 策略**：只装 **Anima**，不装 Illustrious/Pony/SDXL。同一角色若上游同时提供
  `Remapped Anima 2.9B` 和普通 `Anima`，**两个都装**（主力底模两条线都有）。
- **运行时目录**：真正的 ComfyUI 在 `D:\1Repo\Github\ComfyUI\Library\`，
  LoRA 库是 `Library/models/loras/`（不是仓库根）。
- 工具脚本在 `D:\1Repo\Github\ComfyUI\Workflow\lora\tools\civitai\`，用法见该目录
  `README.md`；改过脚本必须跑 `python -m pytest <该目录> -q`（53 个离线测试）。

## 流程

### 1. 核实身份（别直接按用户给的名字搜）

用户口述的角色名常有出入，先确认官方英文名再搜，否则结果全跑偏：

- 例：`提弗罗斯` → 官方写法**提弗洛斯** → 英文 **Typhoeus**（《明日方舟：终末地》）
- 例：`飞鸟马时` → **飛鳥馬トキ / Asuma Toki**，出自《蔚蓝档案》而非《碧蓝航线》

核实手段：WebSearch 中文名 + 官方 wiki；或先 `search_models` 拉出该作品全部 LoRA，
从标题里反查中英日三语对应。游戏归属错了要如实指出，不要顺着用户的说法搜。

### 2. 检索并选版本

```
python <tools>/mcp/search.py models "<角色名>" Anima 10     # 第三参是 baseModel 硬筛
python <tools>/mcp/search.py ids <modelId>                  # 列全部 version/base/文件/trainedWords
```

选型依据：`baseModel=Anima` 优先，其次下载量、SFW/POI 标记、创建日期、是否明确写了
remap 目标。注意作者的 Anima 版可能是在 **Anima Preview 0.3 / Base v1.0** 上训的——
那对 2.9B 底模需要重映射，要如实提醒。

`search_models` 返回**人类可读文本而非 JSON**；REST `/v2/*` 会返回 HTML（需 key），别用。

### 3. 下载

```
https://civitai.com/api/download/models/<modelVersionId>
```

- `307` + `location: b2.civitai.com/...` → 匿名可下，直接 `curl -L`。
- `401 {"message":"The creator of this asset requires you to be logged in to download it"}`
  → 创作者开了登录门槛。`civitai.red` 镜像 ID 相同、同样受限，**换域名没用**。
- 带 token：`?token=<key>`。

**验证 key 是否有效只能用下载端点**，不能用 `/v1/users/me`——后者对**有效** key 也返回
401，用它做探针会把好 key 误判成无效。

用户自己下好并给本地路径时，接受这条路，不要擅自替他重试下载。
Token 只用于单次请求，不写进任何文件、脚本或仓库。

### 4. 核对身份（装之前必做）

读 safetensors 头部并与 Civitai 元数据比对，任何一项对不上就停下来问：

| 检查项 | 来源 / 判据 |
|---|---|
| 字节数 ↔ `files[].sizeKB` | 换算成 MiB 后必须一致 |
| `modelspec.title` | 应与文件名/版本名呼应 |
| tensors / dtype / rank | `lora_down.weight` 的 shape[0] 即 dim |
| `ss_network_dim` / `ss_network_alpha` | 影响权重手感 |
| `modelspec.architecture` | `anima-preview/lora` = Anima Base v1.0；`stable-diffusion-xl-v1-base/lora` = SDXL 系，说明拿错 base |
| sha256 前 12 位 | 记进 trigger.txt 作凭证 |

### 5. 落盘与命名

从 `D:\Downloads` **移动**（同盘 rename，避免留重复大文件）到：

- 角色：`Library/models/loras/anima/chara/<作品>/`（如 `endfield/`、`azurlane/`）
- 画师/风格：`Library/models/loras/anima/artist/<YYMMDD>/`（按当天日期新建批次目录）

文件名沿用上游名。库里 `@<触发词>` 后缀是**给人看的标记**，加载器不解析它；
若上游名已含触发词（如 `style_imazawa-000026`）就不再重复拼。

### 6. 写 `.trigger.txt`

必须与 `.safetensors` **同名同目录**（`ComfyUI-Workflow-Studio` 的 `scan_trigger_files`
与 GlowLoader 的 `_candidate_lora_trigger_paths` 都按 basename 配对）。
首行是触发词（逗号分隔），`#` 开头是注释：

```
@4x0style
# model = Style - Blinklikeer (ID 2606016) Anima v1.0 by WalkingMeat
# base = Anima (anima-preview/lora) | dim 32 | BF16 | SFW | sha256 360215CC
# source_url = "https://civitai.red/models/2606016/...?modelVersionId=2926184"
```

触发词抄 `trainedWords` 原文，**区分大小写**，不要自己规范化。
没有触发词的写 `<name>.notrigger.txt`。

### 7. 补预览图

```
python <tools>/previews/fill_previews.py <目标目录>      # Civitai 来源
python <tools>/previews/from_dataset.py --dry-run        # 自训产物
```

三级解析，顺序固定：`.trigger.txt` 的 `source_url` → sha256 批量 by-hash
（`POST /v1/model-versions/by-hash`，每批 100，匿名可用，结果进 `.hash_index.json` 含负缓存）
→ 自训项目本地取图（`<项目>/output/sample/*` 验证样张 > `<项目>/dataset/*` >
`finish/<项目>/` 平铺带 caption；同项目多 checkpoint 与样张**按序号配对**）。

必须遵守的两条：

- **后缀按下载字节的魔数决定**，不能信 URL——`original=true` 的路径以 `.jpeg` 结尾，
  但 CDN 对不带 `Accept` 的客户端返回 PNG。
- **过滤 `type != "image"`**——Civitai 示例项可能是 MP4（`ftyp` 开头）。

扩展名 `.preview.png|jpg|jpeg|webp` 都在加载器白名单里；AVIF 用 ffmpeg 转
（本机 Pillow 不可用）。自动挑到的预览可能是露骨内容，主动说明并允许换图。

### 8. 验证

ComfyUI 在跑时（默认 8188）：

```
GET http://127.0.0.1:8188/object_info/LoraLoader   → 确认新路径出现在 lora_name 列表
```

服务没起就**明确说这一项未实测**，不要用"应当可见"代替验证。文件层可自查：
三件套（`.safetensors` / `.trigger.txt` / `.preview.*`）同目录同名、`D:\Downloads` 无残留。

## 汇报要求

每次装完给出：落盘绝对路径、身份核对表（对上了什么）、触发词、预览来源，以及未验证项。
跨 base 的兼容性问题（如 Preview 0.3 训练的件挂 2.9B 需重映射）必须提。
不要顺手安装用户没要的版本或 base。

## Resources

`Workflow/lora/tools/civitai/`（在 ComfyUI 仓库内，不在本技能目录）：
`mcp/search.py`、`previews/fill_previews.py`、`previews/by_hash.py`、
`previews/from_dataset.py`，各带离线 pytest；该目录 `README.md` 记录完整命令行与
已验证的端点行为。
