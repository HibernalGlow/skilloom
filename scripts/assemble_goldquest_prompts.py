#!/usr/bin/env python3
"""Assemble 8 subject-specific GoldQuest prompts from SKILL.md.

Enhances the emoji section with hard density quotas and a cross-subject
concept->emoji mapping table so agents cannot treat emoji as an afterthought.
"""

from pathlib import Path

SKILL_PATH = Path(r"D:\1VSCODE\Projects\Xiranite\skilloom\skills\legal-goldquest\SKILL.md")
OUTDIR = Path(r"D:\1STUDY\3-Resource\法考\_工具\goldquest-prompts")

OLD_EMOJI_SECTION_START = "## Emoji 路由"
NEXT_SECTION = "## 颜色硬规则"

WORKFLOW_STEP2_OLD = "颜色是阅读索引，不是装饰。详见 [`references/color-system.md`](references/color-system.md)。"
WORKFLOW_STEP2_NEW = (
    "颜色是阅读索引，不是装饰。**同一步同步建立本题图标表**：为本题的关键概念逐个选语义 emoji——"
    "每个概念单独判断、单独选型，没有全局固定映射（见下方「Emoji 路由」）；"
    "进入正文前 emoji 与颜色一样必须先有词典——写成正文后再回头补 emoji 就会漏"
    "（这是历史文件密度上不去的头号原因）。"
    "详见 [`references/color-system.md`](references/color-system.md) 与下方「Emoji 路由」。"
)

NEW_EMOJI_SECTION = r'''## Emoji 路由（密度配额）

emoji 是解析区的第二套索引系统，与颜色同级——不是装饰、不是可选项。**写每一题前先建本题图标表，写完立即落位**；事后补 emoji 是禁手，历史上所有低密度文件都是这么来的。

### 密度配额（硬性数字，不是建议）

- **每道题的「答案与解析」区：至少 2 个语义 emoji**（`E509` 的下限是 1，本提示词要求 ≥2；两判断分支的题各分支至少 1 个）。
- **每个够格大区（H2-H4、≥6 列表项或 200 字）：至少 3 个语义 emoji**（`E516` 在 >40% 大区无 emoji 时整档报错——不要贴着 40% 红线走，按每个大区 3+ 写）。
- **中等及以上复杂度的解析**：每个独立判断分支、规则句、例外、法条、结论都应考虑配一个锚定 emoji，通常一道题 3-6 个。
- **长文档重做**：全文档不同 emoji 种类 ≥6 种；单一 emoji 全文档 ≤8 次（`E510`）。
- 数一下再交付：每题解析区 emoji 数 <2 就回工，这不是样式偏好，是密度门禁。

### 语义选型（每个图标单独判断，禁止批量、禁止固定映射）

- **不搞全局"某词=某图标"的词典**：同一图标贴到 ≥6 个不同概念词即 `E512` 拒绝——查表式批量插入就是这条门禁的靶子。每个概念问一句"它的独特性质是什么"，为这个性质选可视形象：交付方式看"物怎么移动"（🚚现实交付、📦指示交付、⛓占有改定——同类概念、三个不同图标，这正是语义判断的样子）；期间看流逝（⏳）、自动续期看循环（🔁）、法条看文书（📜）。
- 本题图标表随主体色表一起建：列"关键概念 → 图标 → 为什么是它"，落位时逐个对照。
- 表外概念选语义最贴的图标；实在没有贴切的不硬塞——硬塞的装饰 emoji 与漏加同样是错误。

### 位置规则（硬门禁）

`✅/❌` 只标记选项对错；**正确答案行尾是唯一的结构位豁免**（随答案一起揭示、不剧透，只计 `E510` 预算，豁免 `E513/E514/E515`）。其余位置是硬门禁：不许堆行首当标签（≥70% 被 `E514` 拒绝）、不许堆句尾点缀（≥70% 被 `E513` 拒绝）、不许悬空（两侧都不是概念词、≥50% 被 `E515` 拒绝）——emoji 必须紧贴它锚定的概念词（词前或词后），句中、词后、结论处都应有。不贴"注意/重点/难点/要点/考点/提示/陷阱"这类通用占位词（`W511`）。两个角色支配同一范围可以组合（如 `🧭⚠️`）。

'''

SUBJECTS = [
    {"name": "民法", "short": "civil", "id_prefix": "civil",
     "example_tag": "#法考/民法/合同法/合同解释#", "topics": "civil-contract-validity,civil-good-faith"},
    {"name": "刑法", "short": "criminal", "id_prefix": "criminal",
     "example_tag": "#法考/刑法/犯罪构成/正当防卫#", "topics": "criminal-crime-constitution,criminal-justifiable-defense"},
    {"name": "刑诉", "short": "criminal-procedure", "id_prefix": "criminal-proc",
     "example_tag": "#法考/刑诉/证据规则/非法证据排除#", "topics": "criminal-proc-evidence,criminal-proc-exclusion"},
    {"name": "民诉", "short": "civil-procedure", "id_prefix": "civil-proc",
     "example_tag": "#法考/民诉/当事人/诉讼代理#", "topics": "civil-proc-parties,civil-proc-representation"},
    {"name": "商经知", "short": "commercial-economic-knowledge", "id_prefix": "commercial",
     "example_tag": "#法考/商经知/公司法/股东出资#", "topics": "commercial-company-capital,commercial-shareholder"},
    {"name": "行政法", "short": "administrative", "id_prefix": "admin",
     "example_tag": "#法考/行政法/行政处罚/听证程序#", "topics": "admin-penalty,admin-hearing"},
    {"name": "理论法", "short": "theoretical-law", "id_prefix": "theory",
     "example_tag": "#法考/理论法/宪法/基本权利#", "topics": "theory-constitution,theory-rights"},
    {"name": "三国法", "short": "international-law", "id_prefix": "intl",
     "example_tag": "#法考/三国法/国际私法/涉外送达#", "topics": "intl-private-law,intl-service"},
]


def splice_emoji_section(text: str) -> str:
    start = text.index(OLD_EMOJI_SECTION_START)
    end = text.index(NEXT_SECTION)
    return text[:start] + NEW_EMOJI_SECTION + "\n" + text[end:]


def main() -> None:
    OUTDIR.mkdir(exist_ok=True)
    base = SKILL_PATH.read_text(encoding="utf-8")

    # Fold emoji quotas into workflow step 2 so the mapping is built BEFORE writing.
    assert WORKFLOW_STEP2_OLD in base, "workflow step 2 anchor drifted"
    base = base.replace(WORKFLOW_STEP2_OLD, WORKFLOW_STEP2_NEW, 1)

    base = splice_emoji_section(base)

    for sub in SUBJECTS:
        text = base
        # Subject banner with the canonical in-place skill location.
        banner = (
            f"> 本提示词属于 **{sub['name']}** 科目，由 skilloom 技能生成。\n"
            f"> **技能原位文件（权威）**：`D:\\1VSCODE\\Projects\\Xiranite\\skilloom\\skills\\legal-goldquest\\SKILL.md`\n"
            f"> 及其 references（color-system / format-playbook / topic-summary / kaodian-tags）。\n"
        )
        text = text.replace(
            "# Legal GoldQuest\n",
            f"# Legal GoldQuest — {sub['name']}\n\n" + banner + "\n",
            1,
        )
        # Subject-specific examples (plain str.replace; never touch other braces).
        text = text.replace("civil-gold-2020-001", f"{sub['id_prefix']}-gold-2020-001")
        text = text.replace("civil-gold-2020-108", f"{sub['id_prefix']}-gold-2020-108")
        text = text.replace("civil-gold-<年份>-<题号>", f"{sub['id_prefix']}-gold-<年份>-<题号>")
        text = text.replace("civil-contract-validity,civil-good-faith", sub["topics"])
        text = text.replace("civil-property-good-faith-acquisition,civil-property-registration", sub["topics"])
        text = text.replace("#法考/民法/合同法/合同解释#", sub["example_tag"])
        out = OUTDIR / f"{sub['short']}.md"
        out.write_text(text, encoding="utf-8")
        print(f"WROTE {out.name} ({len(text)} chars)")

    print(f"\nAll 8 prompts written to: {OUTDIR}")


if __name__ == "__main__":
    main()
