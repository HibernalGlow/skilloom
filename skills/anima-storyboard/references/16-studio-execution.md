# 补充篇 F：Studio 执行权与批跑 runbook

> 2026-09-28 引入。**本技能负责产出页面 txt，但页面 txt 不接 Studio 就等于没出图。**
> 权威源文件是工作区里的 `ComfyUI-Workflow-Studio/docs/BATCH-DISPATCH.md`
> （本文件是它的**提炼镜像 + 执行权约束**）；两者冲突时以 BATCH-DISPATCH.md 为准，且**改了要同步**。

---

## 16.0 铁律：出图只有一个入口 ⛔

**「出图 / 跑图 / 批跑 / 生成 N 页」= `ComfyUI-Workflow-Studio` 的批量引擎。
不是手写 ComfyUI 图 JSON，不是 `POST /prompt`，不是 `/tmp/xxx.py`。**

手搓能省的那点自由度，代价是绕过引擎里已经长出来的**全部防线** —— 而每一条都是踩出来的：

| 引擎内置 | 手搓会丢什么 |
|---|---|
| `resolve_preset()` 强制 fallback | **预设泄漏**：某页命中了单采预设后，后面所有无规则页都被带偏（真发生过，27 页跑错，见 §6.10） |
| 踩脚页采样闸（干跑告警 + 投递前拦截 + 全仓审计） | **踩脚页跑双彩** → 镫袜 LoRA 糊成一团（§6.12） |
| 逐页规则 + `[auto_rules]` 并集 | 动作 LoRA、`exclude_keywords`（`hairop` / `footrepair`）静默失效 |
| `mirror_output.py` 回传 | 图只在 Windows 落盘，Mac 收不到 |
| 失败保护 + 续跑序号 | 一张失败整批卡死 / 前功尽弃 |
| `wait_and_run.sh` 探针 | 模型根目录缺失时全批 `HTTP 400` 空烧 |

---

## 16.1 拓扑（排错全靠这一张）

| 位置 | 角色 | 跑什么 |
|---|---|---|
| **Mac**（本机） | 开发 / 派发端 | Studio 源码、前端 dev-server、**派发脚本**。**不跑图** |
| **Windows**（`win30902` / hostname `Pterosaur`） | 算力端 | ComfyUI + GPU + 模型库 + **出图落盘** |
| SSH 隧道 | 桥梁 | Mac `127.0.0.1:8188` ← `ssh -L` → Windows `127.0.0.1:8188` |

**图是在 Windows 上生成的**，所以文件天然落在 Windows 磁盘；Mac 永远不自动收到图，
除非走 `[output] mac_dir` 回传。隧道由自愈守护维持（断 5 秒自动重连）；
**但 ComfyUI 本身要手动重启**（Comfy Desktop 不会自动重生）。

---

## 16.2 标准四步（缺一步都不算跑过）

```bash
cd /Users/glow/Base/Works/ComfyUI/ComfyUI-Workflow-Studio

# ① 作品目录写 batch.toml —— 照抄同批样板作品，只改 preset / page_glob / output_subdir
#    Workflows/wild/storyboard/<作品>/batch.toml

# ② 建 3 行 runner —— 复制模板，只改 TOML 一行
cp tools/run_niannian_batch.py tools/run_<作品>_batch.py

# ③ 干跑校验（**必做**：先看闸门与预设路由，别直接投）
tools/run_batch.sh dryrun_batch.py Workflows/wild/storyboard/<作品>/batch.toml

# ④ 等后端就绪再开跑；另一边挂回传
nohup tools/wait_and_run.sh run_<作品>_batch.py 1 > /tmp/<作品>.log 2>&1 &
python3 tools/mirror_output.py <output_subdir> /Users/glow/Base/Works/ComfyUI/Outputs --watch-pid <pid>
```

runner 模板长这样（**只有 TOML 一行是变量**）：

```python
TOML = Path("/Users/glow/Base/Works/ComfyUI/Workflows/wild/storyboard/<作品>/batch.toml")

if __name__ == "__main__":
    rtb, cfg, base_preset = load_story(TOML)
    if "--preset" not in sys.argv and base_preset:
        sys.argv += ["--preset", base_preset]
    rtb.main()
```

**引擎 argv（`run_typhon_batch.py` 系）**

| 参数 | 作用 |
|---|---|
| `<起始序号>`（位置参数，1 基） | 续跑起点 |
| `--only NN022,NN023` | 只跑指定页 |
| `--tag _v2` | 输出子目录后缀，避免覆盖 |
| `--preset <id>` | 覆盖作品 TOML 的基线预设 |
| `--seed N` | 固定种子 |

> 必须用 `run_batch.sh` / `wait_and_run.sh` 包装：**TOML 走标准库 `tomllib`，需要 Python 3.11+**，
> wrapper 会自动挑解释器。

---

## 16.3 `batch.toml` 字段速查

```toml
[story]
id = "qinliu";  name = "琴柳"

[paths]
pages_dir     = "pages"
page_glob     = "SL*.txt"       # 页面统一前缀；**必须与文件名一致**
output_subdir = "琴柳"           # ComfyUI output 下的子目录名

[output]
mac_dir      = "../../../../Outputs"   # 回传根；留空 = 只留 Windows
wait_timeout = 1800                    # 单页等待上限（插队场景必调，见 §16.6）

[prompt]
quality_prefix = "masterpiece, best quality, aesthetic, highly detailed, <画师触发词>, uncensored"
negative       = "worst quality, low quality, bad anatomy, …"

[base]
preset = "anima-single-17"      # 默认采样预设，见 §14.3
arch   = "anima"                # "anima" | "illus" | "anima-incontext"
unet   = "silvermoonmixAnima_v23_INT8.safetensors"
  [[base.loras]]                # 基线 LoRA，每页都挂；顺序 = 入栈顺序
  name = "Turbo-v0.2"; path = 'anima\turbo\anima-turbo-lora-v0.2.safetensors'
  model_weight = 0.8;  clip_weight = 1.0

[[page_rule]]                   # 逐页规则：**命中的全部生效**（一页可命中多条）
name           = "镫袜足交"
when_triggers  = ["ustirrup", "stirrupjob", "footjob", "under-stirrup footjob"]
preset         = "anima-native-30"    # 命中后换预设
bundle_only    = true                 # 只挂「基线 + 本规则」，不叠规则库
exclude_family = ["ustirrup", "stirrupjob", "throughfoot", "stirrup3"]
  [[page_rule.loras]]
  name = "Ustirrup 2000"; path = 'anima\action\footjob\ustirrup\ustirrup-step00002000.safetensors'
  model_weight = 0.88;    clip_weight = 1.0

[auto_rules]                    # 自动补挂动作/修复类 LoRA
enabled          = true
rules_file       = "../../../../ComfyUI-Workflow-Studio/data/lora_rules.json"
categories       = ["action", "repair"]
exclude_keywords = ["hairop", "footrepair"]   # ⚠️ 见下

[runtime]
free_vram = true                # 每页 POST /free 清显存（默认开；多会话共用 GPU 时别关）

[validation]                    # 踩脚页采样闸（§16.4）
foot_allow_presets = ["anima-native-30"]
foot_gate_mode     = "block"    # "block"（默认，拦下不出图）| "warn"

[incontext]                     # 仅 arch = "anima-incontext"
strength    = 1.0               # **设 0 = 完全跳过拼接**，等于无参考图（干净的原生识别测试）
end_percent = 0.90              # 姿势旋钮，见 §15.6
  [[incontext.refs]]
  file = "xxx_ref_fullbody.png" # 必须在 ComfyUI input/ 下

[[page_canvas]]                 # 逐页画幅；in-context 下必须 = 参考图 target 尺寸
code = "LF042"; width = 832; height = 1216; end_percent = 0.80
```

**写法注意**

- Windows 路径用**单引号**（TOML 字面串），反斜杠不转义
- `pages_dir` / `rules_file` / `mac_dir` 都**相对 batch.toml 自身**解析（`../../../../` = `Works/ComfyUI`）
- **`exclude_keywords` 里的 `footrepair` 是承重结构，不是画质偏好**：规则库里
  `Foot Repair` 的触发词含裸 `stirrup`，去掉排除会**让全部页面挂上足部修复**

---

## 16.4 三层闸门（已内置，不用记，但别绕）

| 层 | 工具 | 行为 |
|---|---|---|
| 干跑 | `tools/dryrun_batch.py <toml>` | 逐页打印命中规则 / 最终预设 / LoRA 栈；踩脚页采样告警；**退出码 1**（`--warn-only` 降级）；核对 LoRA 是否已注册 |
| 跑批 | `run_typhon_batch.py` 投递前 | 踩脚页跑双彩 → **拦下该页**并打印修法 |
| 审计 | `tools/audit_foot_presets.py -v` | 扫**所有**作品，一次列出全部隐坑 |

```bash
tools/run_batch.sh dryrun_batch.py Workflows/wild/storyboard/<作品>/batch.toml
python3 tools/test_foot_preset_gate.py     # 18 个纯函数用例，不需 GPU
python3 tools/audit_foot_presets.py -v     # 逐页打印所有作品的踩脚页路由
```

**闸门的两层词表，别混**

- **硬门槛**（`foot_keywords`）：`footjob` / `stepping on another` / `foot worship` / `foot on penis` / `toe scrunch`
  —— 真把足部当主体。命中且跑双彩 → 拦。
- **软提醒**（`foot_frame_keywords`）：`foot focus` / `sole focus` —— 只是**镜头语言**，命中只打 `ℹ️`。

> ⚠️ **血泪**：早期把 `foot focus` 塞进硬门槛，全仓 204 页里 82 个无辜页被喊狼来了；
> 把 `stirrup legwear`（每页都有的**服饰**标签）收进来后连发交页都误报。
> **别把服饰标签和取景标签塞进硬门槛。**

---

## 16.5 监控与回传

```bash
# 进度
grep -oE "^\[[0-9]+/[0-9]+\]" /tmp/<作品>.log | tail -1
# 成功 / 回传 / 回传失败
grep -c "✅ 完成"   /tmp/<作品>.log
grep -c "已回传 Mac" /tmp/<作品>.log
grep -c "回传失败"   /tmp/<作品>.log
# 逐页挂了什么
grep -E "⚙️|✅ 完成" /tmp/<作品>.log | tail -20
# 守望：进程退出就汇总
while pgrep -f "run_<作品>_batch.py" >/dev/null; do sleep 30; done; tail -16 /tmp/<作品>.log
```

**后端健康探针**（唯一判据，无副作用）：

```bash
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8188/object_info/OTUNetLoaderW8A8
# 200 = 模型路径全通   500 = 有模型根目录不存在（→ 所有 /prompt 返 400）
```

**回传是「复制」不是「移动」**：Windows 原图始终保留，可随时追补。
反之**一旦把图移出 Windows 就再也取不回来**（`/view` 404）。

```bash
python3 tools/mirror_output.py <output_subdir> /Users/glow/Base/Works/ComfyUI/Outputs --watch-pid <pid>
```

> **别用 ssh 列中文文件名**（GBK 会毁掉编码）。列举一律走 ComfyUI `/history`
> —— `mirror_output.py` 就是这么做的。

---

## 16.6 插队（`tools/run_insert.py`）与超时预算

`POST /prompt` 带 `front: true` → 服务端把任务序号取负 → heapq 排最前，
**在正在执行的节点跑完后就立刻执行**，不打断既有批次（改代码/改配置对已 import 的进程无效，§6.3）。

```bash
tools/run_batch.sh run_insert.py <作品 batch.toml> --only SL003,SL041
tools/run_batch.sh run_insert.py <作品 batch.toml> --only SL001 --dry-run
```

| 参数 | 作用 |
|---|---|
| `--only CODE,CODE` | 按页前缀码选 |
| `--index N,N` | 按 1 基序号选（`page_glob` 排序后） |
| `--tag SUFFIX` | 输出子目录后缀，默认 `_jump`（不覆盖正式产物） |
| `--no-front` | 不插队，排到队尾 |
| `--timeout SECONDS` | 单页等待上限，默认取 `[output] wait_timeout`（否则 300） |
| `--dry-run` | 只打印，不投递 |

> ⚠️ **超时陷阱**：插队任务耗时 $T$ **完全占用**批次下一页的等待预算。
> 默认 `WAIT_TIMEOUT=300s`、正常一页约 60s ⇒ $T > 240s$ 就会把下一页误判超时（连续 3 次触发保护停机）。
> 对策：先把 `[output] wait_timeout` 调到 1800（**只对下次启动生效**），或单次只插 1~3 页。

---

## 16.7 排错速查

| 症状 | 先查 | 处置 |
|---|---|---|
| 全批 `HTTP Error 400` | 探针是否 500 | 删掉不存在的模型根目录 + 重启 ComfyUI |
| `🛑 连续 3 张失败` | 后端探针 | 这是**保护不是 bug**；修好后按打印的序号续跑 |
| `Empty reply from server` | Windows 是否在监听 8188 | ComfyUI 没起 → 重启它 |
| 报错找不到类名，但探针 200 | 挂载的 LoRA 路径 | 路径写错（如 `clothes` vs `outfit`） |
| 图片没到 Mac | `grep -c 回传失败` | 0 失败 = 已到过 Mac，是被移走了 |
| `/view` 404 | 图是否还在 Windows | 已移出 → 取不回来 |
| 画风不对 / 发糊 | 权重是否 >1、镫袜页是否换了全扩散预设 | §6.5 / §6.6 / §6.12 |
| 改了配置没生效 | 是否重启了进程 | Python 只在 import 时读一次代码和配置 |
| 某页预设莫名不对 | 是否预设泄漏 | 已由 `resolve_preset()` 根治；回归靠 `dryrun_batch.py` |

---

## 16.8 反模式与唯一例外

**⛔ 禁止**

- 手写 / 手改 ComfyUI 图 JSON 并 `POST /prompt` 出**正式页**
- 把一次性脚本写成 `/tmp/xxx.py` 当交付路径
- 没跑 `dryrun_batch.py` 就投递
- 因「这个作品要特殊参数」而绕开引擎 —— 特殊参数的正确落点是 `batch.toml`
  （`[[page_rule]]` / `[[page_canvas]]` / `[incontext]` / `[validation]`），引擎都已支持

**唯一例外**：用户**显式**要求「先单张打样 / A-B 对照 / 只测一个变量」时可以手搓一次性探测，但必须：

1. 说明这是在打样，不是交付；
2. 探测脚本落在可复用位置（`tools/probe_*.py` / `tools/run_*_artists.py` / `tools/run_recognition_test.py`），
   不放 `/tmp`；
3. 结论**回灌** `batch.toml` 或预设，再走 §16.2 四步跑正式批次。

---

## 16.9 权威源与同步约定

| 用途 | 路径 |
|---|---|
| **权威 runbook** | `ComfyUI-Workflow-Studio/docs/BATCH-DISPATCH.md` |
| 本文件（提炼镜像） | `references/16-studio-execution.md` |
| 共享引擎 | `tools/run_typhon_batch.py` |
| TOML 装载 | `tools/story_config.py` |
| 干跑 / 审计 / 闸门回归 | `tools/dryrun_batch.py` · `tools/audit_foot_presets.py` · `tools/test_foot_preset_gate.py` |
| 插队 | `tools/run_insert.py` |
| 回传 | `tools/mirror_output.py` |
| runner 模板 | `tools/run_niannian_batch.py`（3 行） |
| 采样预设 | `data/gen_presets.json` |
| 规则库 | `data/lora_rules.json` |
| 作品配置 | `Workflows/wild/storyboard/<作品>/batch.toml` |

> **改了 BATCH-DISPATCH.md 就同步本文件**（反之亦然）。这两份已经因为不同步漂移过一次
> —— 正是 §16.0 那张表里「绕过引擎」的同类病根。
