<a id="top"></a>

<p align="center">
  <img src="./assets/readme/hero.svg" width="100%"
       alt="skilloom —— Agent 技能包与输出质量门禁。标题下方给出技能包、Python 脚本与自测数量；底部机制带：技能规范 → 模型生成 → 门禁（结构 / 语义 / 规范）→ 合格放行落盘、不合格拒收并以非零退出。">
</p>

<p align="center">
  <b>中文</b> · <a href="#english">English</a>
</p>

**把重复的垂直领域任务写成 Agent 技能，再用 Python 门禁在输出落盘前把它拦住。**

22 个技能包 + 12 个仓库级 Python 脚本（门禁、校验、同步，共 4881 行）。技能负责"该怎么做"，脚本负责"没做到就不许留下"。

---

## 为什么需要门禁

大模型生成内容的典型失败方式不是报错，而是**看起来完全正常、结构已经坏了**：标题层级被并列枚举撑成一串同级标题、Mermaid 流程图的节点连到不存在的分支、表格被拆散后丢了合并关系、题目解析里的答案依据被改写成结论。这类问题人工逐篇检查不可持续，等到导入笔记软件或发布出去才发现，返工成本更高。

所以本仓库把约束拆成两半：

- **`skills/`** —— 写给 Agent 读的操作规范（模式路由、判据、完成标准）。
- **`scripts/`** —— 写给机器执行的验收：解析产物、判定结构、命中即非零退出并指出位置。

不合格的输出被拒绝，而不是静默上线。

## 门禁会拒收什么

一份 7 行笔记：一个标题、一句事实、一张三列表格。保存为 `/tmp/reject-demo.md` 后运行仓库级校验器：

```markdown
## 合同

甲未交货。

| A | B | C |
| --- | --- | --- |
| 1 | 2 | 3 |
```

```text
$ python3 scripts/legal_note_output_validator.py /tmp/reject-demo.md --profile legal-marknote; echo "rc=$?"
/tmp/reject-demo.md:1: E625: MarkNote subject '甲' needs an actively assigned semantic color.
/tmp/reject-demo.md:5: E411: legal-marknote tables must be at most 2 columns by 2 data rows; split larger comparisons semantically or explicitly raise --max-table-columns/--max-table-rows when the larger table is necessary.
rc=1
```

两条错误都带行号：主体缺语义颜色；表格有 3 列，超过 2 列的上限。门禁只报可判定的结构问题，不替人做价值判断。

<a id="run"></a>

## 怎么跑

```bash
# 法律技能契约校验（对当前仓库）
python3 scripts/validate_legal_skills.py
# PASS legal contracts (generic validation skipped; set SKILL_CREATOR_QUICK_VALIDATE to enable it).

# 仓库级校验器：按 profile 选择门禁
# legal-marknote：散文 / Mermaid 等
python3 scripts/legal_note_output_validator.py path/to/note.md --profile legal-marknote
# legal-goldquest：含题目块时另含选项 / 语义门禁
python3 scripts/legal_note_output_validator.py path/to/questions.md --profile legal-goldquest

# 批量审计某个笔记目录里的 Mermaid 语义
python3 scripts/audit_mermaid_semantics.py path/to/notes

# 校验器自测（119 项 + 17 子测试）
uv run --with pytest python3 -m pytest scripts/test_legal_note_output_validator.py -q
```

`legal_goldquest_option_gate.py`、`legal_goldquest_semantic_structure_gate.py`、`legal_marknote_prose_gate.py`、`legal_mermaid_semantics_gate.py` 是 `legal_note_output_validator.py` 导入的库模块，不是独立命令：前三份直接运行只会定义函数并以 0 退出，Mermaid 那份需要显式传入文件。`legal-goldquest` profile 在含题目块时会调用选项 / 语义 / 散文 / Mermaid 四份，`legal-marknote` profile 只调用散文 / Mermaid。仓库没有"一键对全仓跑四道门禁"的入口。

> ⚠️ `scripts/gate_legal_skills.py`（聚合入口）**当前故意以退出码 2 结束**，见「已知限制」第 1 条。不要把它的非零退出误读成"仓库坏了"。

## 仓库构成

| 路径 | 内容 |
| --- | --- |
| `skills/<name>/SKILL.md` | 技能主体：frontmatter 的 `name` / `description` 决定何时被加载 |
| `skills/<name>/references/` | 按需加载的细则、词典、判据表 |
| `skills/<name>/scripts/` | 该技能自带的执行与校验脚本 |
| `skills/<name>/agents/` | 面向其他 Agent 运行时的适配清单（YAML） |
| `scripts/` | 仓库级门禁、校验器、自测与安装同步脚本 |

## 技能清单（22）

**法律学习（7）**

| 技能 | 做什么 |
| --- | --- |
| `legal-marknote` | 法考教材与笔记 → 结构化思源 Markdown；表格转为选轴父子列表（题面围栏原文表、行测统计材料表除外），修复误识别标题与层级 |
| `legal-goldquest` | 题目、选项与完整解析 → 闪卡复习用结构化 Markdown，答案区语义颜色保持一致 |
| `legal-flashcard` | 生成 DAMO 兼容闪卡（两种显式模式），并经真实 Protyle 粘贴批量回灌思源 |
| `legal-question-bank` | 客观题/主观题 → 题库源文件，写入稳定的 `custom-qb-*` IAL 元数据供多端消费 |
| `legal-question-author` | 按题库错题、收藏与薄弱考点批量出卷、生成变式题成稿 |
| `legal-topic-linker` | 审计并修复题目与考点笔记之间的点对点链接 |
| `legal-imagen` | 为法律学习资料生成结构化配图提示词（时间线、流程、对比、情境） |

**资料管线（1）**

| 技能 | 做什么 |
| --- | --- |
| `fakao-mineru-merge` | 把分段/分册的 MinerU 解析产物合并成单一 `full.md` + `images/` + `目录.md` |

**题库插件与知识站点（4）**

| 技能 | 做什么 |
| --- | --- |
| `damophus-dev` | 开发 Damophus 思源题库插件：规划、实现、调试、测试、打包、提交 |
| `inkloom-dev` | 维护 InkLoom 法律学习站点，从已完成笔记产出独立 Remotion 讲解动画 |
| `produce-inkloom-animation` | 以主线程为唯一协调者与独立审查方，组织动画生产与修复 |
| `inkloom-embed` | 把已发布动画（AVIF）嵌入法考笔记、真金题与闪卡，并审计死链 |

**思源笔记工具（4）**

| 技能 | 做什么 |
| --- | --- |
| `siyuan-export` | `.sy` 文档/目录/工作区 ↔ Markdown 的双向导出导入（可配 IAL） |
| `siyuan-database-management` | 无幽灵行、无重复行地管理、查询、更新思源属性视图（AV/数据库） |
| `siyuan-linker` | 发现、审计、预览、创建并验证笔记与块之间的语义链接 |
| `siyuan-bazaar-release` | 通过 GitHub Releases 与思源社区市场索引发布和更新插件 |

**出图与偏好训练（3）**

| 技能 | 做什么 |
| --- | --- |
| `civitai-lora-install` | 查找、校验、下载并安装 Civitai LoRA，回填触发词与预览图 |
| `civitai-lora-upload` | 用已登录 Chrome + 本地文件桥批量上传 LoRA 作品 |
| `clipm-preference-training` | 通过 MCP / `xclipm` CLI 读写漫画偏好评分与人工校正 |

**Agent 基建与其他（3）**

| 技能 | 做什么 |
| --- | --- |
| `mcp-discovery` | 先定位 `~/.mcp.json` 里的既有 MCP 服务表，再考虑新增配置 |
| `session-nudge` | 向持久化 Agent 会话注入一条消息，让中断任务继续跑 |
| `trename` | ACG 资源归档：中英文动态翻译 + 文件系统命名规范批量重命名 |

## 一个技能包长什么样

```markdown
---
name: legal-flashcard
description: 一句话说明「做什么」+「什么时候该被加载」，供 Agent 判定触发。
---

正文按「模式路由 → 各模式步骤 → 完成标准」组织。
每条判据都写成可判定的句子，而不是建议。
```

约定：`description` 决定技能是否被载入，因此必须包含触发场景；正文里的每条规则都要能被脚本或人**判真伪**，"尽量""最好"这类词不算判据。

## 已知限制

1. **聚合门禁 `gate_legal_skills.py` 故意退出码 2。** 它现在是一道防误用守卫：`skills/legal-goldquest` 与 `skills/legal-marknote` 各自的 `validate_output.py` 已经分叉（goldquest 拆分 + E 系列门禁），继续从 `scripts/legal_note_output_validator.py` 这份旧副本覆盖会静默删掉两边的规则，所以同步路径被停用。部署技能文件请改用 `scripts/sync_installed_skills.py`。
2. **`scripts/legal_note_output_validator.py` 与技能内的 `validate_output.py` 不再是同一份代码**，前者是仓库级校验器与自测对象，后者按技能需要各自演进。
3. **本仓库不是全量技能库。** 含成人内容的技能包已移出仓库；另有若干小说写作类技能仅存在于本地，由 `.git/info/exclude` 排除。清单以上面的 22 个为准。
4. **技能是给 Agent 读的指令文本，不是可安装的软件包**：没有 `pyproject.toml`、没有依赖声明、没有版本发布流程。
5. **多数技能依赖本地环境**，在别人机器上不可复现：思源内核 API（`127.0.0.1:6806`）、ComfyUI 与 Civitai 登录态、Xiranite 的 ClipM 节点、ZCode 会话台账。
6. **考点 tag 词汇表与法考内容是个人学习资料的衍生物**，其准确性不构成法律意见。

<a id="english"></a>

## English

**skilloom turns repeatable domain tasks into agent skills, then uses Python gates to reject malformed output before it lands.**

22 skill packs and 12 repo-level Python scripts under `scripts/` (4,881 lines). Skills describe *how* the work should be done; scripts parse the result and exit non-zero when the structure, semantics, or note conventions are broken.

- **Skills** live in `skills/<name>/SKILL.md`. The frontmatter `description` decides when an agent loads them.
- **Gates** live in `scripts/`. Four modules — option analysis, semantic structure, prose fragmentation, and Mermaid semantics — are imported by `scripts/legal_note_output_validator.py`. The `legal-goldquest` profile runs all four when question blocks are present; `legal-marknote` runs prose and Mermaid. They are libraries, not standalone repo-wide commands.
- **Validator tests**: 119 passed, 17 subtests passed.

The rejection demo in the Chinese section above is a synthetic seven-line note; the validator reports two line-addressed findings and exits 1. There is no single command that runs all four gate modules across the whole repository; the validator applies them per document and per profile.

The 22 packs cover legal study (7), document pipelines (1), the Damophus question-bank plugin and InkLoom site (4), SiYuan tooling (4), image and preference workflows (3), and agent infrastructure (3). A skill is a Markdown instruction file, not an installable package: there is no `pyproject.toml` or release process. Most skills depend on local services (SiYuan at `127.0.0.1:6806`, ComfyUI and Civitai sessions, ClipM, ZCode session state).

Known limits: `scripts/gate_legal_skills.py` intentionally exits 2 and must not be read as "the repository is broken"; deploy skill files with `scripts/sync_installed_skills.py`. The repository-level validator and the per-skill `validate_output.py` have diverged. Adult-oriented packs were removed, and some private writing skills are excluded locally, so this is not a complete skill library.

First run (commands in [怎么跑](#run) above are language-neutral):

```bash
python3 scripts/validate_legal_skills.py
uv run --with pytest python3 -m pytest scripts/test_legal_note_output_validator.py -q
```

## 许可 · License

MIT —— 见 [LICENSE](./LICENSE)。

<p align="right"><a href="#top">回到顶部 ↑</a></p>
