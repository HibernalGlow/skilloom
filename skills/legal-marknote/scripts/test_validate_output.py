#!/usr/bin/env python3
"""Regression tests for legal-marknote table-splitting validation."""

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


SOURCE = """| 类别 | 事项 | 规则 |
| :--- | :--- | :--- |
| {: rowspan='2'}类别甲 | 事项甲一 | 规则甲一 |
| {: class='fn__none'} | 事项甲二 | 规则甲二 |
| {: rowspan='2'}类别乙 | 事项乙一 | 规则乙一 |
| {: class='fn__none'} | 事项乙二 | 规则乙二 |
"""

SPLIT_OUTPUT = """**类别甲**

| 事项 | 规则 |
| :--- | :--- |
| 事项甲一 | 规则甲一 |
| 事项甲二 | 规则甲二 |

**类别乙**

| 事项 | 规则 |
| :--- | :--- |
| 事项乙一 | 规则乙一 |
| 事项乙二 | 规则乙二 |
"""


def codes(output: str) -> set[str]:
    return {
        finding.code
        for finding in MODULE.validate_source_preservation(output, SOURCE, "legal-marknote")
    }


class TableSplitValidationTests(unittest.TestCase):
    def test_allows_expanding_category_rowspans_into_sibling_tables(self) -> None:
        self.assertNotIn("703", codes(SPLIT_OUTPUT))

    def test_rejects_split_table_when_a_source_cell_is_missing(self) -> None:
        incomplete = SPLIT_OUTPUT.replace("| 事项乙二 | 规则乙二 |\n", "")

        self.assertIn("703", codes(incomplete))

    def test_rejects_dense_unbroken_table_cell(self) -> None:
        text = "| 保全措施 | 一般财产 | 查封、扣押、冻结；查封已登记的不动产时，应通知登记机关办理登记手续，未办理的不得对抗已登记的保全行为。 |\n"
        findings = MODULE.validate_tables(text)

        self.assertIn("403", {finding.code for finding in findings})

    def test_accepts_dense_table_cell_after_semantic_breaks(self) -> None:
        text = "| 保全措施 | 一般财产 | **措施**：查封、扣押、冻结。<br />**登记**：应通知登记机关办理登记手续。<br />**后果**：未办理的不得对抗已登记的保全行为。 |\n"
        findings = MODULE.validate_tables(text)

        self.assertNotIn("403", {finding.code for finding in findings})

    def test_rejects_large_numbered_list_inside_table_cell(self) -> None:
        text = "| 类别 | 法定情形 |\n| --- | --- |\n| 证据问题 | 1. 新证据<br />2. 原判缺乏证据<br />3. 伪造证据<br />4. 主要证据未经质证 |\n"
        findings = MODULE.validate_tables(text)

        self.assertIn("412", {finding.code for finding in findings})

    def test_allows_a_few_short_numbered_items_inside_table_cell(self) -> None:
        text = "| 类别 | 法定情形 |\n| --- | --- |\n| 证据问题 | 1. 新证据<br />2. 原判缺乏证据 |\n"
        findings = MODULE.validate_tables(text)

        self.assertNotIn("412", {finding.code for finding in findings})

    def test_allows_unchanged_source_table_with_existing_list_items(self) -> None:
        source = "| 类别 | 法定情形 |\n| --- | --- |\n| 证据问题 | 1. 新证据<br />2. 原判缺乏证据<br />3. 伪造证据<br />4. 主要证据未经质证 |\n"
        findings = MODULE.validate_text(source, "legal-marknote", source_text=source)

        self.assertNotIn("412", {finding.code for finding in findings})

    def test_allows_complete_table_to_real_list_conversion(self) -> None:
        source = "| 类别 | 法定情形 |\n| --- | --- |\n| 证据问题 | 1. 新证据<br />2. 原判缺乏证据<br />3. 伪造证据<br />4. 主要证据未经质证 |\n"
        output = "- **类别**：证据问题\n- **法定情形**：\n    1. 新证据\n    2. 原判缺乏证据\n    3. 伪造证据\n    4. 主要证据未经质证\n"
        findings = MODULE.validate_source_preservation(output, source, "legal-marknote")

        self.assertNotIn("702", {finding.code for finding in findings})

    def test_rejects_converting_a_genuine_comparison_table_to_a_list(self) -> None:
        source = "| 类型 | 效力 |\n| --- | --- |\n| 有效合同 | 有效 |\n| 无效合同 | 无效 |\n"
        output = "- **有效合同**：有效\n- **无效合同**：无效\n- **类型**与**效力**逐项对应。\n"
        findings = MODULE.validate_source_preservation(output, source, "legal-marknote")

        self.assertIn("702", {finding.code for finding in findings})

    def test_rejects_generated_label_rule_table(self) -> None:
        text = """| 启动方式 | 具体规定 |
| --- | --- |
| 本院启动 | 院长认为裁判确有错误时，提交审判委员会讨论决定再审。 |
| 上级法院启动 | 上级法院认为下级法院裁判确有错误时，有权启动再审。 |
"""
        findings = MODULE.validate_tables(text)

        self.assertIn("413", {finding.code for finding in findings})

    def test_rejects_unbacked_merge_placeholder(self) -> None:
        text = """| 分类 | 期间 | 依据 | 细分 | 规则 |
| --- | --- | --- | --- | --- |
| {: rowspan='2'}分类 | 法定期间 | 法律明文规定的期间 | 绝对不可变期 | 不得变更 |
| {: class='fn__none'} | 指定期间 | {: class='fn__none'} | 相对不可变期 | 可以依法变更 |
"""

        findings = MODULE.validate_tables(text)

        self.assertIn("406", {finding.code for finding in findings})

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


class NoteTopicIalValidationTests(unittest.TestCase):
    def test_accepts_heading_provider_and_explicit_anchor(self) -> None:
        text = """### 善意取得
{: custom-qb-note-topic-id="civil-property-good-faith-acquisition"}

**考点：登记对抗**
{: custom-qb-note-topic-id="civil-property-registration"}
"""

        findings = MODULE.validate_topic_ials(text, "legal-marknote", require_note_topic=True)

        self.assertEqual([], findings)

    def test_requires_provider_in_normal_marknote_gate(self) -> None:
        findings = MODULE.validate_topic_ials("### 善意取得\n正文。\n", "legal-marknote", require_note_topic=True)

        self.assertIn("804", {finding.code for finding in findings})

    def test_rejects_multiple_ids_and_question_identity_on_provider(self) -> None:
        text = """### 善意取得
{: custom-qb-note-topic-id="civil-property-good-faith-acquisition,civil-property-registration" custom-qb-id="question-1"}
"""

        findings = MODULE.validate_topic_ials(text, "legal-marknote", require_note_topic=True)
        codes = {finding.code for finding in findings}

        self.assertIn("801", codes)
        self.assertIn("803", codes)

    def test_rejects_provider_ial_detached_from_topic_block(self) -> None:
        text = """### 善意取得
正文。
{: custom-qb-note-topic-id="civil-property-good-faith-acquisition"}
"""

        findings = MODULE.validate_topic_ials(text, "legal-marknote", require_note_topic=True)

        self.assertIn("802", {finding.code for finding in findings})


class ConceptHeadingValidationTests(unittest.TestCase):
    def test_rejects_numeric_only_heading_before_short_concept_definition(self) -> None:
        text = """### 1.
{: custom-qb-note-topic-id="criminal-property-six-illegal-gains"}

**六赃**{: style="color: var(--b3-font-color10);"}：六种非法获取公私财物的犯罪。
"""

        findings = MODULE.validate_text(text, "legal-marknote")

        self.assertIn("705", {finding.code for finding in findings})

    def test_accepts_promoted_concept_and_exercise_counter(self) -> None:
        promoted = "### 1. 六赃\n\n六种非法获取公私财物的犯罪。\n"
        exercise = """###### 习题
### 1.
合同效力：甲与乙签订合同，该合同是否有效？
"""

        self.assertNotIn("705", {finding.code for finding in MODULE.validate_text(promoted, "legal-marknote")})
        self.assertNotIn("705", {finding.code for finding in MODULE.validate_text(exercise, "legal-marknote")})


class RichPresentationValidationTests(unittest.TestCase):
    def test_accepts_bold_background_only_anchor(self) -> None:
        text = '**诉讼中**{: style="background-color: var(--b3-font-background11);"}'
        self.assertNotIn("201", {finding.code for finding in MODULE.validate_colors(text)})

    def test_rejects_background_only_anchor_without_bold(self) -> None:
        text = '诉讼中{: style="background-color: var(--b3-font-background11);"}'
        self.assertIn("201", {finding.code for finding in MODULE.validate_colors(text)})

    def test_rejects_long_marknote_prose_line(self) -> None:
        text = "甲应当向法院提交全部证据并在法定期间内完成举证，否则将承担不利后果，且不得在庭审结束后再次补交同一组证明材料。"
        self.assertIn("621", {finding.code for finding in MODULE.validate_text(text, "legal-marknote")})

    def test_medium_marknote_requires_mermaid(self) -> None:
        text = "\n".join([
            "### 规则",
            "**甲**{: style=\"color: var(--b3-font-color10);\"}提出申请。",
            "- **受理**{: style=\"background-color: var(--b3-font-background11);\"}",
            "  - **法院**{: style=\"color: var(--b3-font-color8);\"}审查材料。",
            "- **不受理**{: style=\"color: var(--b3-font-color13);\"}",
            "  - **甲**{: style=\"color: var(--b3-font-color10);\"}补正。",
        ])
        self.assertIn("624", {finding.code for finding in MODULE.validate_text(text, "legal-marknote")})

    def test_medium_marknote_requires_four_auxiliary_styles(self) -> None:
        text = "\n".join([
            "### 规则",
            "**甲**{: style=\"color: var(--b3-font-color10); background-color: var(--b3-font-background10);\"}提出申请。",
            "- **法院**{: style=\"color: var(--b3-font-color8); background-color: var(--b3-font-background8);\"}审查。",
            "- **结果**{: style=\"color: var(--b3-font-color13); background-color: var(--b3-font-background13);\"}确定。",
            "- **期限**{: style=\"color: var(--b3-font-color12);\"}届满。",
            "```mermaid",
            "flowchart LR",
            "A[申请] --> B[审查]",
            "```",
        ])
        self.assertIn("620", {finding.code for finding in MODULE.validate_text(text, "legal-marknote")})

    def test_medium_marknote_requires_three_background_anchors(self) -> None:
        text = "\n".join([
            "### 规则",
            "**甲**{: style=\"background-color: var(--b3-font-background10);\"}提出申请。",
            "- ==受理==并审查。",
            "  - _法院_作出判断。",
            "- ~~错误路径~~应排除。",
            "  - `期限`届满后处理。",
            "```mermaid",
            "flowchart LR",
            "A[申请] --> B[审查]",
            "```",
        ])
        self.assertIn("627", {finding.code for finding in MODULE.validate_text(text, "legal-marknote")})

    def test_repeated_subject_requires_active_color(self) -> None:
        text = "甲提出申请，甲随后补正材料。"
        self.assertIn("625", {finding.code for finding in MODULE.validate_text(text, "legal-marknote")})



if __name__ == "__main__":
    unittest.main()
