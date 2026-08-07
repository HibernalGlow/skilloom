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
**后果**{{: style="color: var(--b3-font-color8);"}}是裁定==驳回起诉==，而不是不予受理，也不是实体上的驳回诉讼请求。
为避免混淆，还需要比较死亡发生时间、法院发现问题的阶段，以及案件是否已经进入实体审理。
"""

        self.assertNotIn("620", codes(text))


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
