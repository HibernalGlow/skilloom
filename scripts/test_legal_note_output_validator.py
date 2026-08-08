from __future__ import annotations

import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))

from legal_note_output_validator import validate_text  # noqa: E402


def codes(text: str, profile: str = "legal-marknote", source: str | None = None) -> set[str]:
    return {finding.code for finding in validate_text(text, profile, source)}


class LegalNoteOutputValidatorTests(unittest.TestCase):
    def test_accepts_semantically_styled_table_and_callout(self) -> None:
        text = (
            "> [!NOTE] 法条\n"
            "> \n"
            "> **要件**是==主体资格==。\n\n"
            "| 审查 | 规则 |\n"
            "| :--- | :--- |\n"
            "| 主体 | **资格**{: style=\"color: var(--b3-font-color10);\"}：==适格==。 |\n"
            "| 后果 | **责任**{: style=\"color: var(--b3-font-color13);\"}：_承担责任_。 |\n"
        )
        self.assertEqual(codes(text), set())

    def test_rejects_long_adjacent_and_escaped_highlights(self) -> None:
        text = "==这是一个明显过长的高亮==\n==主体====结果==\n\\=错误"
        self.assertTrue({"101", "102", "103"} <= codes(text))

    def test_rejects_invalid_color_attachment_range_and_drift(self) -> None:
        text = """主体{: style=\"color: var(--b3-font-color14);\"}
**甲**{: style=\"color: var(--b3-font-color10);\"}
**甲**{: style=\"color: var(--b3-font-color11);\"}
"""
        self.assertTrue({"201", "202", "203"} <= codes(text))

    def test_rejects_invalid_callout_and_unquoted_body(self) -> None:
        text = "> [!note] 提示\n> 第一行\n- 遗漏引用符"
        self.assertTrue({"303", "304"} <= codes(text))

    def test_rejects_unbroken_enumeration_and_plain_long_cell(self) -> None:
        text = "| 项目 | 1. 要件一 2. 要件二 3. 要件三 4. 要件四 |\n| 长文 | " + "普通说明。" * 24 + " |"
        self.assertTrue({"412", "402"} <= codes(text))

    def test_rejects_unbacked_merge_placeholder(self) -> None:
        text = """| 分类 | 期间 | 依据 | 细分 | 规则 |
| --- | --- | --- | --- | --- |
| {: rowspan='3'}分类 | {: rowspan='2'}法定期间 | 法律明文规定的期间 | 绝对不可变期 | 不得变更 |
| {: class='fn__none'} | {: class='fn__none'} | {: class='fn__none'} | 相对不可变期 | 可以依法变更 |
"""
        self.assertIn("406", codes(text))

    def test_accepts_complete_merge_grid(self) -> None:
        text = """| 分类 | 期间 | 依据 | 细分 | 规则 |
| --- | --- | --- | --- | --- |
| {: rowspan='3'}分类 | {: rowspan='2'}法定期间 | {: rowspan='2'}法律明文规定的期间 | 绝对不可变期 | 不得变更 |
| {: class='fn__none'} | {: class='fn__none'} | {: class='fn__none'} | 相对不可变期 | 可以依法变更 |
| {: class='fn__none'} | 指定期间 | {: colspan='3'}法院依职权指定期间 | {: class='fn__none'} | {: class='fn__none'} |
"""
        self.assertFalse({"404", "406", "407", "408", "409", "410"} & codes(text))

    def test_compares_source_images_tables_merge_tokens_and_headings(self) -> None:
        source = "# 原标题\n![](assets/a.png)\n| {: colspan='2'}内容 | 空格 |"
        output = "# 新标题\n普通正文"
        self.assertTrue({"701", "702", "703", "704"} <= codes(output, source=source))

    def test_accepts_simple_label_rule_table_converted_to_list(self) -> None:
        source = """| 启动方式 | 具体规定 |
| --- | --- |
| 本院启动 | 院长认为裁判确有错误时，提交审判委员会讨论决定再审。 |
| 上级法院启动 | 上级法院认为下级法院裁判确有错误时，有权启动再审。 |
"""
        output = """- **本院启动**
    - 院长认为裁判确有错误时，提交审判委员会讨论决定再审。
- **上级法院启动**
    - 上级法院认为下级法院裁判确有错误时，有权启动再审。
"""

        self.assertNotIn("702", codes(output, source=source))

    def test_rejects_label_rule_list_conversion_when_rule_is_missing(self) -> None:
        source = """| 启动方式 | 具体规定 |
| --- | --- |
| 本院启动 | 院长认为裁判确有错误时，提交审判委员会讨论决定再审。 |
| 上级法院启动 | 上级法院认为下级法院裁判确有错误时，有权启动再审。 |
"""
        output = "- **本院启动**\n    - 院长认为裁判确有错误时，提交审判委员会讨论决定再审。\n"

        self.assertIn("702", codes(output, source=source))

    def test_keeps_multi_axis_table_preservation_gate(self) -> None:
        source = """| 启动方式 | 启动主体 | 处理方式 |
| --- | --- | --- |
| 本院启动 | 院长 | 提交审判委员会讨论 |
| 上级法院启动 | 上级法院 | 直接启动再审 |
"""
        output = """- **本院启动**：院长提交审判委员会讨论。
- **上级法院启动**：上级法院直接启动再审。
"""

        self.assertIn("702", codes(output, source=source))

    def test_rejects_numeric_only_heading_before_short_concept_definition(self) -> None:
        text = "### 1.\n\n六赃：六种非法获取公私财物的犯罪。\n"

        self.assertIn("705", codes(text))

    def test_rejects_styled_concept_after_heading_ial(self) -> None:
        text = """### 1.
{: custom-qb-note-topic-id="criminal-property-six-illegal-gains"}

**六赃**{: style="color: var(--b3-font-color10);"}：六种非法获取公私财物的犯罪。
"""

        self.assertIn("705", codes(text))

    def test_accepts_short_concept_promoted_into_numbered_heading(self) -> None:
        text = "### 1. 六赃\n\n六种非法获取公私财物的犯罪。\n"

        self.assertNotIn("705", codes(text))

    def test_keeps_exercise_counter_heading_without_question_stem(self) -> None:
        text = """###### 习题
### 1.
合同效力：甲与乙签订合同，该合同是否有效？

###### 回答与解析
1. 合同有效。
"""

        self.assertNotIn("705", codes(text))

    def test_goldquest_does_not_apply_marknote_concept_heading_gate(self) -> None:
        text = "### 1.\n六赃：六种非法获取公私财物的犯罪。\n"

        self.assertNotIn("705", codes(text, "legal-goldquest"))

    def test_rejects_goldquest_answer_leak_and_checked_option(self) -> None:
        text = """##### 1题
* 题干含==正确答案==
    - [x] A. 选项
**成立**{: style=\"color: var(--b3-font-color8);\"}
"""
        self.assertTrue({"601", "603"} <= codes(text, "legal-goldquest"))

    def test_requires_an_answer_boundary_for_each_goldquest_question(self) -> None:
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

        findings = validate_text(text, "legal-goldquest")
        result = {(finding.code, finding.line) for finding in findings}

        self.assertIn(("613", 1), result)
        self.assertIn("609", {finding.code for finding in findings})
        self.assertIn("615", {finding.code for finding in findings})
        self.assertIn("606", {finding.code for finding in findings})

    def test_rejects_flat_multi_branch_goldquest_analysis(self) -> None:
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

        self.assertIn("615", codes(text, "legal-goldquest"))

    def test_rejects_one_color_anchor_for_a_long_analysis_line(self) -> None:
        text = f"""##### 1.
{{: custom-qb-id="civil-gold-1" custom-qb-question-topic-ids="civil-topic"}}
* 题干。
###### 答案与解析
- 正确答案：A。
{{: custom-qb-section="solution"}}
**规则**{{: style="color: var(--b3-font-color10);"}}适用于本案。首先审查主体资格。其次审查程序条件。最后确定法律后果。
"""

        self.assertIn("616", codes(text, "legal-goldquest"))

    def test_accepts_goldquest_question_answer_boundary(self) -> None:
        text = """##### 1题
{: custom-qb-id="civil-question-1" custom-qb-question-topic-ids="civil-topic" custom-qb-answer="A"}
* **甲**{: style=\"color: var(--b3-font-color10);\"}实施某行为，如何判断？
    - [ ] A. 选项甲
    - [ ] B. 选项乙

###### 答案与解析

- 正确答案：A。
{: custom-qb-section="solution"}

**答案**为==选项甲==。
"""
        self.assertEqual(codes(text, "legal-goldquest"), set())

    def test_rejects_legacy_answer_mask_and_overlong_color_anchor(self) -> None:
        mask = "<div><style>b{background:#c9cdd3;color:transparent;border-radius:4px;padding:0 6px}b:hover{background:#fff2c2;color:#c0392b}</style>答案：<b>A</b></div>"
        text = f"""##### 1.
{{: custom-qb-id="civil-question-1" custom-qb-question-topic-ids="civil-topic"}}
* 题干。
###### 答案与解析
{mask}
**法院受理后发现条件欠缺**{{: style="color: var(--b3-font-color10);"}}。
"""

        result = codes(text, "legal-goldquest")

        self.assertIn("607", result)
        self.assertIn("617", result)

    def test_requires_custom_answer_for_objective_goldquest_question(self) -> None:
        text = """##### 1.
{: custom-qb-id="civil-question-1" custom-qb-question-topic-ids="civil-topic"}
* 题干。
    - [ ] A. 选项
###### 答案与解析
- 正确答案：A。
{: custom-qb-section="solution"}
"""

        self.assertIn("619", codes(text, "legal-goldquest"))

    def test_rejects_goldquest_highlight_and_status_color_before_answer(self) -> None:
        text = """##### 1题
* 题干提前标出==正确项==
    - [ ] A. **成立**{: style=\"color: var(--b3-font-color8);\"}

###### 答案与解析

**答案**为==选项甲==。
"""
        self.assertTrue({"604", "605"} <= codes(text, "legal-goldquest"))


if __name__ == "__main__":
    unittest.main()
