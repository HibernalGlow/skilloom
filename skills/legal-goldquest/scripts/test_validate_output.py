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


if __name__ == "__main__":
    unittest.main()
