#!/usr/bin/env python3
"""Regression tests for legal-goldquest color and Callout density gates."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("validate_output.py")
SPEC = importlib.util.spec_from_file_location("validate_output", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


ANSWER_BLOCK = "###### 答案与解析\n- 正确答案：A。\n{: custom-qb-section=\"solution\"}"
LEGACY_MASK = "<div><style>b{background:#c9cdd3;color:transparent;border-radius:4px;padding:0 6px}b:hover{background:#fff2c2;color:#c0392b}</style>答案：<b>A</b></div>"


def codes(text: str) -> set[str]:
    return {finding.code for finding in MODULE.validate_goldquest(text)}


class GoldquestDensityValidationTests(unittest.TestCase):
    def test_rejects_verdict_only_option_reasons(self) -> None:
        question_lines = [
            "    - [ ] A. 村委会应当返还所得收益",
            "    - [ ] B. 村委会无需承担责任",
        ]
        analysis_lines = [
            "- ❌ A. 村委会~~应当返还所得收益~~",
            "    - **破绽**：A项应排除，**不当选**。",
            "- ✅ B. 村委会==无需承担责任==",
            "    - <u>依据</u>：由综合推理，本项**当选**。",
        ]

        result = MODULE.validate_option_analysis(question_lines, analysis_lines, 1, "B")

        self.assertEqual(["632", "632"], [finding.code for finding in result.findings])

    def test_rejects_whole_option_strikethrough(self) -> None:
        question_lines = [
            "    - [ ] A. 村委会应当返还所得收益",
            "    - [ ] B. 村委会无需承担责任",
        ]
        analysis_lines = [
            "- ❌ A. ~~村委会应当返还所得收益~~",
            "    - **破绽**：A项应予返还，**不当选**。",
            "- ✅ B. 村委会==无需承担责任==",
            "    - <u>依据</u>：村委会以自己名义处分财产，**当选**。",
        ]

        result = MODULE.validate_option_analysis(question_lines, analysis_lines, 1, "B")

        self.assertIn("646", [finding.code for finding in result.findings])

    def test_rejects_wrong_option_marked_by_color_only(self) -> None:
        question_lines = [
            "    - [ ] A. 村委会应当返还所得收益",
            "    - [ ] B. 村委会无需承担责任",
        ]
        analysis_lines = [
            "- ❌ A. 村委会**应当返还**{: style=\"color: var(--b3-font-color13);\"}所得收益",
            "    - **破绽**：A项应予返还，**不当选**。",
            "- ✅ B. 村委会==无需承担责任==",
            "    - <u>依据</u>：村委会自己处分财产，**当选**。",
        ]

        result = MODULE.validate_option_analysis(question_lines, analysis_lines, 1, "B")

        self.assertIn("631", [finding.code for finding in result.findings])

    def test_requires_topic_summary_for_multi_question_provider_document(self) -> None:
        text = """# 专题
{: custom-qb-note-topic-id="civil-procedure-topic"}

##### 1.
{: custom-qb-id="q-1" custom-qb-question-topic-ids="topic-a"}

##### 2.
{: custom-qb-id="q-2" custom-qb-question-topic-ids="topic-b"}
"""

        self.assertIn("634", codes(text))

    def test_warns_when_multi_question_topic_h1_has_no_sortable_number(self) -> None:
        unnumbered = """# 专题六 共同诉讼
{: custom-qb-note-topic-id="civil-procedure-topic"}
## 📌 考点必背
- 共同诉讼规则。
##### 1.
{: custom-qb-id="q-1" custom-qb-question-topic-ids="topic-a"}
##### 2.
{: custom-qb-id="q-2" custom-qb-question-topic-ids="topic-b"}
"""
        numbered = unnumbered.replace("# 专题六", "# 06 专题六", 1)

        self.assertIn("638", codes(unnumbered))
        self.assertNotIn("638", codes(numbered))

    def test_accepts_topic_summary_between_provider_and_first_question(self) -> None:
        text = """# 专题
{: custom-qb-note-topic-id="civil-procedure-topic"}

## 📌 考点必背

### 1. 共同诉讼

- 核心规则来自题目解析。

##### 1.
{: custom-qb-id="q-1" custom-qb-question-topic-ids="topic-a"}

##### 2.
{: custom-qb-id="q-2" custom-qb-question-topic-ids="topic-b"}
"""

        self.assertFalse({"634", "635", "636", "637"} & codes(text))

    def test_rejects_misplaced_or_metadata_bearing_topic_summary(self) -> None:
        misplaced = """# 专题
## 📌 考点必背
{: custom-qb-note-topic-id="civil-procedure-topic"}
##### 1.
{: custom-qb-id="q-1" custom-qb-question-topic-ids="topic-a"}
##### 2.
{: custom-qb-id="q-2" custom-qb-question-topic-ids="topic-b"}
"""
        metadata_bearing = """# 专题
{: custom-qb-note-topic-id="civil-procedure-topic"}
## 📌 考点必背
- 导航
{: custom-dm-card-id="fc-invalid"}
##### 1.
{: custom-qb-id="q-1" custom-qb-question-topic-ids="topic-a"}
##### 2.
{: custom-qb-id="q-2" custom-qb-question-topic-ids="topic-b"}
"""

        self.assertIn("635", codes(misplaced))
        self.assertIn("636", codes(metadata_bearing))

    def test_rejects_topic_summary_that_labels_specific_questions(self) -> None:
        spoilers = {
            "本题": "- 本题考察必要共同诉讼与普通共同诉讼的区分。",
            "题号": "- 第 73 题对应代表人诉讼的程序路径。",
            "上题": "- 如上一题所述，诉讼标的是否同一决定合并审理。",
            "下题": "- 下题将进入代表人诉讼。",
        }
        for label, summary_line in spoilers.items():
            with self.subTest(label=label):
                text = f"""# 专题
{{: custom-qb-note-topic-id="civil-procedure-topic"}}
## 📌 考点必背
{summary_line}
##### 1.
{{: custom-qb-id="q-1" custom-qb-question-topic-ids="topic-a"}}
##### 2.
{{: custom-qb-id="q-2" custom-qb-question-topic-ids="topic-b"}}
"""
                self.assertIn("813", codes(text))

    def test_accepts_topic_summary_grouped_by_exam_point_without_question_pointers(self) -> None:
        text = """# 专题
{: custom-qb-note-topic-id="civil-procedure-topic"}
## 📌 考点必背
### 1. 必要共同诉讼与普通共同诉讼
- **核心区分**：诉讼标的是否同一。
### 2. 代表人诉讼的程序路径
- 本题组覆盖的程序路径按公告、登记、推选顺序展开。
##### 1.
{: custom-qb-id="q-1" custom-qb-question-topic-ids="topic-a"}
##### 2.
{: custom-qb-id="q-2" custom-qb-question-topic-ids="topic-b"}
"""
        self.assertNotIn("813", codes(text))

    def test_rejects_markdown_emphasis_and_accepts_em_tag(self) -> None:
        rejected = "*星号斜体*\n_下划线斜体_\n__下划线加粗__"
        accepted = "<em>轻旁注</em>与**关键结论**。"
        rejected_codes = {finding.code for finding in MODULE.validate_text(rejected, "legal-goldquest")}
        accepted_codes = {finding.code for finding in MODULE.validate_text(accepted, "legal-goldquest")}

        self.assertTrue({"104", "105"} <= rejected_codes)
        self.assertFalse({"104", "105"} & accepted_codes)

    def test_rejects_three_uncolored_analysis_sentences(self) -> None:
        text = (
            f"##### 1.\n* 题干。\n{ANSWER_BLOCK}\n"
            "第一项规则应适用于本案。\n"
            "第二项规则需要审查主体资格。\n"
            "第三项规则最终决定法律后果。\n"
        )

        self.assertIn("609", codes(text))

    def test_accepts_color_anchor_every_one_or_two_sentences(self) -> None:
        text = (
            f"##### 1.\n* 题干。\n{ANSWER_BLOCK}\n"
            "**规则**{: style=\"color: var(--b3-font-color10);\"}适用于本案。\n"
            "因此应审查构成要件。\n"
            "**例外**{: style=\"color: var(--b3-font-color5);\"}不适用于该情形。\n"
            "故该选项错误。\n"
        )

        self.assertNotIn("609", codes(text))

    def test_rejects_plain_text_pseudo_callout(self) -> None:
        text = f"{ANSWER_BLOCK}\n📌[总结与归纳] 规则应结合例外理解。\n"

        self.assertIn("608", codes(text))

    def test_rejects_goldquest_table_over_three_by_three(self) -> None:
        text = (
            "| 项目 | 规则 | 后果 | 备注 |\n"
            "| --- | --- | --- | --- |\n"
            "| A | 规则 | 后果 | 备注 |\n"
        )
        self.assertIn("411", {finding.code for finding in MODULE.validate_text(text, "legal-goldquest")})

    def test_rejects_large_numbered_list_inside_table_cell(self) -> None:
        text = "| 类别 | 法定情形 |\n| --- | --- |\n| 证据问题 | 1. 新证据<br />2. 原判缺乏证据<br />3. 伪造证据<br />4. 主要证据未经质证 |\n"
        findings = MODULE.validate_tables(text)

        self.assertIn("412", {finding.code for finding in findings})

    def test_allows_a_few_short_numbered_items_inside_table_cell(self) -> None:
        text = "| 类别 | 法定情形 |\n| --- | --- |\n| 证据问题 | 1. 新证据<br />2. 原判缺乏证据 |\n"
        findings = MODULE.validate_tables(text)

        self.assertNotIn("412", {finding.code for finding in findings})

    def test_rejects_generated_label_rule_table(self) -> None:
        text = """| 启动方式 | 具体规定 |
| --- | --- |
| 本院启动 | 院长认为裁判确有错误时，提交审判委员会讨论决定再审。 |
| 上级法院启动 | 上级法院认为下级法院裁判确有错误时，有权启动再审。 |
"""
        findings = MODULE.validate_tables(text)

        self.assertIn("413", {finding.code for finding in findings})

    def test_rejects_split_table_without_header(self) -> None:
        text = "| 本院启动 | 院长 | 决定再审 |\n| 上级法院启动 | 上级法院 | 启动再审 |\n"
        findings = MODULE.validate_tables(text)

        self.assertIn("414", {finding.code for finding in findings})

    def test_rejects_rowspan_data_as_header(self) -> None:
        text = """| {: rowspan='2'}确认调解协议效力 | 符合条件 | 裁定确认效力 |
| --- | --- | --- |
| {: class='fn__none'} | 不符合条件 | 裁定驳回申请 |
"""
        findings = MODULE.validate_tables(text)

        self.assertIn("416", {finding.code for finding in findings})

    def test_rejects_long_semantically_ungrouped_list(self) -> None:
        text = "\n".join(f"- 项目{i}" for i in range(1, 7))
        self.assertIn("610", {finding.code for finding in MODULE.validate_text(text, "legal-goldquest")})

    def test_accepts_div_wrapped_html_block(self) -> None:
        text = "> ```html\n> <div><span>说明</span></div>\n> ```\n"
        self.assertNotIn("306", {finding.code for finding in MODULE.validate_text(text, "legal-goldquest")})

    def test_rejects_unwrapped_html_block(self) -> None:
        text = "> ```html\n> <span>说明</span>\n> ```\n"
        self.assertIn("306", {finding.code for finding in MODULE.validate_text(text, "legal-goldquest")})

    def test_requires_a_boundary_for_each_question(self) -> None:
        text = """##### 1.
* 题干。
    - [ ] A. 选项
- 正确答案：A。
{: custom-qb-section="solution"}
- 第一项规则适用于本案。
- 第二项规则需要审查主体资格。
- 第三项规则最终决定法律后果。

##### 2.
* 题干。
    - [ ] A. 选项
###### 答案与解析
- 正确答案：A。
"""

        findings = MODULE.validate_text(text, "legal-goldquest")
        result = {(finding.code, finding.line) for finding in findings}

        self.assertIn(("613", 1), result)
        self.assertIn("609", {finding.code for finding in findings})
        self.assertIn("615", {finding.code for finding in findings})
        self.assertIn("606", {finding.code for finding in findings})

    def test_rejects_flat_multi_branch_analysis(self) -> None:
        text = f"""##### 1.
{{: custom-qb-id="civil-gold-1" custom-qb-question-topic-ids="civil-topic"}}
* 题干。
    - [ ] A. 选项
###### 答案与解析
- 正确答案：A。
{{: custom-qb-section="solution"}}
- **主体判断**：甲具有资格。
- **程序判断**：法院应当受理。
- **法律后果**：该请求成立。
"""

        self.assertIn("615", codes(text))

    def test_rejects_sparse_color_inside_one_long_analysis_line(self) -> None:
        text = f"""##### 1.
{{: custom-qb-id="civil-gold-1" custom-qb-question-topic-ids="civil-topic"}}
* 题干。
###### 答案与解析
- 正确答案：A。
{{: custom-qb-section="solution"}}
**规则**{{: style="color: var(--b3-font-color10);"}}适用于本案。首先审查主体资格。其次审查程序条件。最后确定法律后果。
"""

        self.assertIn("616", codes(text))

    def test_rejects_legacy_html_answer_mask(self) -> None:
        text = f"""##### 1.
* 题干。
###### 答案与解析
{LEGACY_MASK}
"""

        self.assertIn("607", codes(text))

    def test_rejects_long_or_punctuated_color_anchor(self) -> None:
        text = f"""##### 1.
* 题干。
{ANSWER_BLOCK}
**法院受理后发现条件欠缺**{{: style="color: var(--b3-font-color10);"}}。
**驳回起诉，**{{: style="color: var(--b3-font-color8);"}}是本题结论。
"""

        result = codes(text)

        self.assertIn("617", result)
        self.assertIn("618", result)

    def test_rejects_long_analysis_with_only_bold_and_color(self) -> None:
        text = f"""##### 1.
* 题干。
{ANSWER_BLOCK}
**规则**{{: style="color: var(--b3-font-color10);"}}适用于本案，先审查主体资格，再判断程序阶段，最后确定裁判方式。
**条件**{{: style="color: var(--b3-font-color12);"}}要求案件已经受理，并且法院是在受理之后才发现起诉条件欠缺。
**后果**{{: style="color: var(--b3-font-color8);"}}是裁定驳回起诉，而不是不予受理，也不是实体上的驳回诉讼请求。
为避免混淆，还需要比较死亡发生时间、法院发现问题的阶段，以及案件是否已经进入实体审理。
"""

        self.assertIn("620", codes(text))

    def test_accepts_justified_auxiliary_style_in_long_analysis(self) -> None:
        text = f"""##### 1.
* 题干。
{ANSWER_BLOCK}
**规则**{{: style="color: var(--b3-font-color10);"}}适用于本案，先审查主体资格，再判断程序阶段，最后确定裁判方式。
**条件**{{: style="color: var(--b3-font-color12);"}}要求案件已经受理，并且法院是在受理之后才发现起诉条件欠缺。
**后果**{{: style="color: var(--b3-font-color8);"}}是裁定==驳回起诉==，而不是~~不予受理~~。
<em>复习时</em>还要核对`有明确的被告`，并区分**程序轴**{{: style="text-decoration: underline;"}}。
"""

        self.assertNotIn("620", codes(text))

    def test_requires_four_auxiliary_style_families_for_medium_complexity(self) -> None:
        text = f"""##### 1.
* 题干。
{ANSWER_BLOCK}
**规则**{{: style="color: var(--b3-font-color10);"}}用于判断==程序结果==。
<em>复习时</em>应排除~~实体结论~~。
**条件**{{: style="color: var(--b3-font-color12);"}}需要继续核对。
**后果**{{: style="color: var(--b3-font-color8);"}}最终确定裁判方式。
"""

        self.assertIn("620", codes(text))

    def test_requires_four_structural_families_for_medium_complexity(self) -> None:
        text = f"""##### 1.
* 题干。
{ANSWER_BLOCK}
- **条件**{{: style="color: var(--b3-font-color12);"}}
    - <em>先看</em>`主体资格`。
    - ~~排除实体判断~~。
    - 最终==驳回起诉==。
```mermaid
flowchart LR
    A[条件] --> B[结论]
```
"""

        self.assertIn("626", codes(text))

    def test_requires_three_background_anchors_for_medium_complexity(self) -> None:
        text = f"""##### 1.
* 题干。
{ANSWER_BLOCK}
- **条件**{{: style="color: var(--b3-font-color12);"}}
    - <em>先看</em>`主体资格`。
    - ~~排除实体判断~~。
    - 最终==驳回起诉==。
```mermaid
flowchart LR
    A[条件] --> B[结论]
```
"""

        self.assertIn("627", codes(text))

    def test_accepts_three_short_background_anchors(self) -> None:
        text = f"""##### 1.
* 题干。
{ANSWER_BLOCK}
- **起诉前**{{: style="color: var(--b3-font-color12); background-color: var(--b3-font-background12);"}}死亡。
    - **受理后**{{: style="color: var(--b3-font-color11); background-color: var(--b3-font-background11);"}}发现。
    - 最终**驳回起诉**{{: style="color: var(--b3-font-color8); background-color: var(--b3-font-background8);"}}。
"""

        self.assertNotIn("627", codes(text))

    def test_accepts_background_only_after_bold_text(self) -> None:
        text = f"""##### 1.
* 题干。
{ANSWER_BLOCK}
**诉讼中**{{: style="background-color: var(--b3-font-background11);"}}发生死亡。
"""

        result = {finding.code for finding in MODULE.validate_text(text, "legal-goldquest")}
        self.assertNotIn("201", result)
        self.assertNotIn("617", result)

    def test_rejects_unbold_or_overlong_background_anchor(self) -> None:
        text = f"""##### 1.
* 题干。
{ANSWER_BLOCK}
诉讼中{{: style="background-color: var(--b3-font-background11);"}}发生死亡。
**法院受理后发现条件欠缺**{{: style="background-color: var(--b3-font-background12);"}}。
"""

        result = {finding.code for finding in MODULE.validate_text(text, "legal-goldquest")}
        self.assertIn("201", result)
        self.assertIn("617", result)

    def test_rejects_long_analysis_line(self) -> None:
        text = f"""##### 1.
* 题干。
{ANSWER_BLOCK}
**规则**{{: style="color: var(--b3-font-color10);"}}要求先审查主体资格再判断程序阶段并确定裁判形式，同时排除不予受理和驳回诉讼请求这两个相邻制度。
"""

        self.assertIn("621", codes(text))

    def test_requires_color_on_each_substantive_analysis_line(self) -> None:
        text = f"""##### 1.
* 题干。
{ANSWER_BLOCK}
这一行解释案件已经进入受理后的程序阶段。
"""

        self.assertIn("622", codes(text))

    def test_requires_an_intentional_visual_for_medium_complexity(self) -> None:
        text = f"""##### 1.
* 题干。
{ANSWER_BLOCK}
- **条件**{{: style="color: var(--b3-font-color12);"}}
    - **主体**{{: style="color: var(--b3-font-color10);"}}资格欠缺。
    - **阶段**{{: style="color: var(--b3-font-color11);"}}已经受理。
    - **后果**{{: style="color: var(--b3-font-color8);"}}驳回起诉。
"""

        self.assertIn("624", codes(text))

    def test_accepts_mermaid_for_medium_complexity(self) -> None:
        text = f"""##### 1.
* 题干。
{ANSWER_BLOCK}
- **条件**{{: style="color: var(--b3-font-color12);"}}
    - **主体**{{: style="color: var(--b3-font-color10);"}}资格欠缺。
    - **阶段**{{: style="color: var(--b3-font-color11);"}}已经受理。
    - **后果**{{: style="color: var(--b3-font-color8);"}}==驳回起诉==。
```mermaid
flowchart LR
    A[资格欠缺] --> B[已经受理] --> C[驳回起诉]
```
"""

        self.assertNotIn("624", codes(text))

    def test_accepts_div_wrapped_html_for_medium_complexity(self) -> None:
        text = f"""##### 1.
* 题干。
{ANSWER_BLOCK}
- **条件**{{: style="color: var(--b3-font-color12);"}}
    - **主体**{{: style="color: var(--b3-font-color10);"}}资格欠缺。
    - **阶段**{{: style="color: var(--b3-font-color11);"}}已经受理。
    - **后果**{{: style="color: var(--b3-font-color8);"}}驳回起诉。
> ```html
> <div class="legal-visual"><span>资格</span><span>→</span><span>驳回</span></div>
> ```
"""

        self.assertNotIn("624", codes(text))

    def test_accepts_labeled_static_png_for_medium_complexity(self) -> None:
        text = f"""##### 1.
* 题干。
{ANSWER_BLOCK}
- **条件**{{: style="color: var(--b3-font-color12);"}}
    - **主体**{{: style="color: var(--b3-font-color10);"}}资格欠缺。
    - **阶段**{{: style="color: var(--b3-font-color11);"}}已经受理。
    - **后果**{{: style="color: var(--b3-font-color8);"}}驳回起诉。
![裁判路径图解](assets/judgment-path.png)
"""

        self.assertNotIn("624", codes(text))

    def test_requires_colored_analysis_subject_to_stay_colored(self) -> None:
        text = f"""##### 1.
* 甲实施行为。
{ANSWER_BLOCK}
**甲**{{: style="color: var(--b3-font-color10);"}}实施行为。
甲不具备相应资格。
"""

        self.assertIn("623", codes(text))

    def test_requires_colored_person_name_to_stay_colored(self) -> None:
        text = f"""##### 1.
* 王旭在起诉前死亡。
{ANSWER_BLOCK}
**王旭**{{: style="color: var(--b3-font-color4);"}}在起诉前死亡。
王旭不再具有诉讼权利能力。
"""

        self.assertIn("623", codes(text))

    def test_does_not_treat_a_colored_concept_substring_as_a_subject(self) -> None:
        text = f"""##### 1.
* 题干。
{ANSWER_BLOCK}
**受理**{{: style="color: var(--b3-font-color10);"}}之后才发现条件欠缺，因此不适用不予受理。
"""

        self.assertNotIn("623", codes(text))

    def test_does_not_flag_colored_paired_subject_substring(self) -> None:
        text = f"""##### 1.
* 甲申请复议，乙为被申请人。
{ANSWER_BLOCK}
**申请人**{{: style="color: var(--b3-font-color11);"}}不依附**被申请人**{{: style="color: var(--b3-font-color11);"}}。
"""

        self.assertNotIn("623", codes(text))

    def test_still_flags_truly_uncolored_paired_subject(self) -> None:
        text = f"""##### 1.
* 甲申请复议，乙为被申请人。
{ANSWER_BLOCK}
**申请人**{{: style="color: var(--b3-font-color11);"}}不依附**被申请人**{{: style="color: var(--b3-font-color11);"}}。
申请人也可以撤回申请。
"""

        self.assertIn("623", codes(text))

    def test_requires_analysis_subject_to_have_a_color(self) -> None:
        text = f"""##### 1.
* 甲实施行为。
{ANSWER_BLOCK}
甲不具备相应资格。
"""

        self.assertIn("625", codes(text))

    def test_does_not_require_question_subject_color(self) -> None:
        text = f"""##### 1.
* 甲实施行为。
{ANSWER_BLOCK}
**甲**{{: style="color: var(--b3-font-color10);"}}不具备相应资格。
"""

        self.assertNotIn("625", codes(text))


class QuestionTopicIalValidationTests(unittest.TestCase):
    def test_accepts_multiple_question_topic_references(self) -> None:
        text = """##### 108.
{: custom-qb-id="civil-gold-2020-108" custom-qb-question-topic-ids="civil-property-good-faith-acquisition,civil-property-registration"}
* 题干。
"""

        findings = MODULE.validate_topic_ials(text, "legal-goldquest")

        self.assertEqual([], findings)

    def test_rejects_missing_question_topic_references(self) -> None:
        text = """##### 108.
{: custom-qb-id="civil-gold-2020-108"}
* 题干。
"""

        findings = MODULE.validate_topic_ials(text, "legal-goldquest")

        self.assertIn("811", {finding.code for finding in findings})

    def test_rejects_duplicate_and_malformed_topic_ids(self) -> None:
        text = """##### 108.
{: custom-qb-id="civil-gold-2020-108" custom-qb-question-topic-ids="valid-topic,Invalid Topic,valid-topic"}
* 题干。
"""

        findings = MODULE.validate_topic_ials(text, "legal-goldquest")
        codes = {finding.code for finding in findings}

        self.assertIn("806", codes)
        self.assertIn("807", codes)

    def test_rejects_note_provider_and_legacy_topic_attributes_on_question(self) -> None:
        text = """##### 108.
{: custom-qb-id="civil-gold-2020-108" custom-qb-question-topic-ids="valid-topic" custom-qb-note-topic-id="valid-topic" custom-qb-topic-ids="valid-topic"}
* 题干。
"""

        findings = MODULE.validate_topic_ials(text, "legal-goldquest")
        codes = {finding.code for finding in findings}

        self.assertIn("805", codes)
        self.assertIn("809", codes)
        self.assertIn("812", codes)

    def test_rejects_generated_label_prefixes(self) -> None:
        text = f"""##### 1.
* **题干**：甲向乙交付货物, 乙未付款.
* **问题**：下列哪一选项是正确的?
{ANSWER_BLOCK}
"""

        self.assertIn("647", {finding.code for finding in MODULE.validate_text(text, "legal-goldquest")})

    def test_accepts_label_free_question_lines(self) -> None:
        text = f"""##### 1.
* 甲向乙交付货物, 乙未付款.
* 下列哪一选项是正确的?
{ANSWER_BLOCK}
"""

        self.assertNotIn("647", {finding.code for finding in MODULE.validate_text(text, "legal-goldquest")})

    def test_rejects_list_items_starting_with_an_ordered_marker(self) -> None:
        for line in ("- 1. 债务加入生效后。", "- （1）主体适格。", "- ① 一部单行刑法。"):
            with self.subTest(line=line):
                result = {finding.code for finding in MODULE.validate_text(line, "legal-goldquest")}
                self.assertIn("311", result)
        # A decimal and a mid-content enumeration stay clear of the hard gate.
        result = {finding.code for finding in MODULE.validate_text("- 利率提高到 1.5 倍。", "legal-goldquest")}
        self.assertNotIn("311", result)


class MermaidSingleChainGateTests(unittest.TestCase):
    """`E903`: one fence must be one connected reasoning chain."""

    def mermaid_codes(self, diagram: str) -> set[str]:
        return {finding.code for finding in MODULE.validate_mermaid_semantics(diagram)}

    def test_rejects_stitched_independent_chains(self) -> None:
        text = """```mermaid
flowchart TD
    A[不法侵害正在进行] --> B[正当防卫的时间条件]
    C[防卫意图] --> D[防卫过当的认定]
```"""

        self.assertIn("903", self.mermaid_codes(text))

    def test_rejects_chain_plus_orphan_node(self) -> None:
        text = """```mermaid
flowchart LR
    A[不法侵害正在进行时实施的反击行为] --> B[正当防卫的时间条件判断] --> C[事后判断不成立正当防卫]
    D[防卫过当的过失心态认定问题]
```"""

        self.assertIn("903", self.mermaid_codes(text))

    def test_accepts_one_connected_reasoning_chain(self) -> None:
        text = """```mermaid
flowchart TD
    A[不法侵害进行中] --> B{时间条件}
    B -- 行为时判断 --> C[正当防卫成立]
    B -- 事后判断 --> D[防卫不适时]
```"""

        self.assertNotIn("903", self.mermaid_codes(text))

    def test_still_reports_901_for_pair_stack(self) -> None:
        text = """```mermaid
flowchart TD
    A[申请信息公开] --> B[行使权利=守法]
    C[环保局败诉] --> D[承担法律责任=强制作用]
    E[拒绝公开] --> F[救济途径明确]
```"""

        self.assertIn("901", self.mermaid_codes(text))


if __name__ == "__main__":
    unittest.main()
