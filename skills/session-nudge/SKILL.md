---
name: session-nudge
description: 向任意 ZCode 持久化会话（sess_…）注入一条消息让它继续干活（如给中断任务发"继续"）。用于：任务看护器续跑中断会话；唤醒睡眠前断掉的战役会话；向指定会话补充指令。制作新动画用 inkloom-dev；看护循环整体用 .watchdog.json 台账。
---

# Session Nudge：给指定会话发消息

一条注入任务的执行序列。原理：`zcode -p "<消息>" --resume sess_xxx --json` 会把消息投进持久化会话并让它接着干活（会话自身历史完整加载，工具默认可用）。**实测有效（2026-09-01），产自远控协议侦察后的 CLI 捷径。**

## 0. 续跑教义（用户 2026-09-01 明确）

- **续跑一个任务，优先给它的原会话发消息**——上下文、配方、战役记忆都在原会话里；派全新子智能体重做是最后手段（仅当原会话无法定位或确认报废）。
- **任务完成情况也可以直接问原会话**：只读探查 = `zcode -p "请只报告你的任务进度：已完成/剩余/卡点，不要使用任何工具" --resume sess_xxx --disallowed-tools "Bash Edit Write CronCreate CronDelete CronUpdate Agent" --json`。
- 注入消息三段式：先要一句进度报告，再布置有界范围，最后说完成后做什么（提交/回写台账）。
- 小时级自动化的会话 idle<60 分钟是轮次间歇常态，不算活跃；`--force` 注入前确认它不在轮次中（离下次定时触发越远越安全）。实测 nudge 小时级自动化会话成功：注入→它干活→它自己按配方提交，全程 1 分钟量级。

## 1. 判定会话可注入（死会话铁律）

- 只注入**已停止**的会话。活跃会话被注入 = 两个进程写同一会话，禁止。
- 判据（满足其一才算死）：`git status`/产物 mtime 停滞超过看护存活判定线（默认 60 分钟）且对应进程已退出；或用户明说该会话已断。
- 会话清单与最后活动时间：sqlite 查 `~/.zcode/cli/db/db.sqlite`：

```sql
SELECT id, title, directory, time_updated FROM session ORDER BY time_updated DESC LIMIT 20;
```

## 2. 查会话原模型（沿用它已有的模型）

```sql
SELECT provider_id, model_id, variant FROM model_usage
WHERE session_id='sess_xxx' ORDER BY started_at DESC LIMIT 3;
```

注入轮默认用 CLI 配置的模型，**不会**自动沿用会话原模型。要沿用就按第 3 节候选链构造凭据。

## 3. 凭据候选链（实测可用为准）

CLI 模型配置在 `~/.zcode/cli/config.json`，**只接受极简 schema**（provider{kind,options{apiKey,baseURL},models} + model.main="provider/model"）；把桌面端 v2/config.json 的 provider 块整体合并会整文件校验失败报 "Model config is missing"。

候选顺序（前一个实测失败才用后一个）：

1. **原 provider 静态 key**：从 `~/.zcode/v2/config.json` 按 provider_id 取 options{apiKey,baseURL}，配 model.main="<别名>/<会话原 model_id>"。注意：app 可能在用 OAuth 动态凭据（v2/credentials.json），静态 key 可能报"余额不足/无效的 API 密钥"——报错即降级。
2. **默认凭据 + 会话原模型**：默认 provider 的 key 配会话的 model_id（不同 key 常可路由同款模型）。
3. **默认凭据 + 默认模型**：tokenrhythm 原账号（d20bde8b）/deepseek-v4-flash-0731，2026-09-01 实测可用。tokenrhythm3 余额不足、0v0 key 失效，勿再试。

**先探针后注入**：每换一个候选，先跑 `zcode -p "1"`（无 --resume，约 200 token）确认凭据可用，避免把无法回答的用户消息写进目标会话。

## 4. 注入（换配置 → 注入 → 必还原）

配置文件是全局的，swap 期间其他 CLI 调用会看到临时配置：用文件锁串行化，try/finally 必还原。机械核心：scripts/nudge_session.py（自动完成 1-4 步：查会话/原模型 → 构造候选 → 探针 → swap → 注入 → 还原 → 输出 --json）。

```bash
python -X utf8 scripts/nudge_session.py --session sess_xxx --message "继续：按 .watchdog.json 你的配方把剩下的文件清到 exit 0" [--force] [--dry-run]
```

注入文本三要素：**接着做什么**（引用台账/配方）、**本轮范围**（防跑飞）、**完成后做什么**（提交/回写台账）。`-p` 默认 yolo 权限，范围必须写清。

## 5. 完成判据与善后

- `--json` 输出含 sessionId/traceId/response 即注入成功；error_type=ProviderBusinessError（余额不足/无效密钥）→ 换候选重试（先探针）。
- 注入后该会话变为活跃：更新看护台账 `.watchdog.json` 该任务状态=运行中、notes 记"已 nudge（时间+模型）"，路径限定 commit。
- 不要连续 nudge 同一会话（上一轮没跑完就别催）；大历史会话一次注入约 20 万 input token，无必要不注入。

## 陷阱清单（单一来源）

- **CLI 注入的消息，桌面端已打开的会话视图不会实时刷新**（2026-09-01 19:00 用户实证）：app 只对它自己运行的 turn 做实时订阅，外部进程写入同一会话库后 UI 停留在旧状态，须重开 app（可能重开会话页也行，待验证）才可见。推论：nudge 适用于**没有 UI 看着的死会话**（隔夜中断场景，UI 迟滞无关紧要）；用户正开着的会话要续跑，最干净的方式是用户自己发。注入内容不会丢，重开后完整可见。
- **探针假阳性：小探针绿≠大请求通**（2026-09-01 17:40 实证）：glm 路由被网关 504 掐死一个多小时，`zcode -p "1"` 的小探针照样通过，候选链永远停在坏路由上看不见 deepseek 备份。已知主路由劣化时直选备用 provider（手动 swap 配置），别迷信自动降级。看 turn 失败根因要查 model_usage 的错误体：504=路由级故障换路，ProviderBusinessError=凭据问题换 key，unknown=可原路重试。
- **turn 失败后立即重试会被存活闸门挡住**：失败 turn 的写入把会话 time_updated 刷新成"0 分钟前"——亲自确认 CLI 进程已随错误退出，就直接 --force 重试（实测 2026-09-01：首 nudge 跑了 12 个请求后遇"模型服务暂时不可用"，重试成功）。
- **巨量历史会话一次 turn 可达数十万至数百万 input token**（实测 60 万-660 万），nudge 前掂量必要性；turn 可能在轻量动作后正常收尾（如只核对状态），不一轮干完全部活。
- **原会话的进度自查比任何外部台账都权威**：看护器引陈旧 checkpoint 让它修 doc53/40，它自查后证伪——任务早已完成。注入消息里永远加一句"先核对你自己的最新 checkpoint 再动手"。
- `--resume` 必须带完整 `sess_…` id；不带 `--resume` 的 `-p` 是新会话，不是注入。
- 注入轮用的是 **CLI config 的模型**，不是会话原模型——沿用必须走第 3 节。
- 会话 id 在 db.sqlite 的 session 表，不在文件名里；agents 目录的 metadata.json 是子智能体的，别混。
- `zcode --help` 没有按次指定模型的 flag/环境变量，换模型只能换配置文件。
- 失败的注入（凭据错误）可能仍把用户消息写进目标会话——所以必须先探针。
- 备份：`config.json.bak-20260901`（实验前原始态）、`config.json.working`（可用态）。
