from __future__ import annotations

import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))

from legal_note_output_validator import validate_text  # noqa: E402


def codes(
    text: str,
    profile: str = "legal-marknote",
    source: str | None = None,
    *,
    allow_structural_repair: bool = False,
    max_table_columns: int = 3,
    max_table_rows: int = 3,
) -> set[str]:
    return {
        finding.code
        for finding in validate_text(
            text,
            profile,
            source,
            allow_structural_repair=allow_structural_repair,
            max_table_columns=max_table_columns,
            max_table_rows=max_table_rows,
        )
    }


def goldquest_options(analysis: str, *, option_a: str = "要约一经发出，即不得撤回。") -> str:
    return f"""##### 1.
{{: custom-qb-id="civil-option-1" custom-qb-question-topic-ids="civil-offer" custom-qb-answer="B"}}
* **问题**：关于要约与承诺，下列说法正确的是？
    - [ ] A. {option_a}
    - [ ] B. 承诺在到达要约人时生效。
###### 答案与解析
- 正确答案：B。
{{: custom-qb-section="solution"}}
{analysis}
"""


class LegalNoteOutputValidatorTests(unittest.TestCase):
    def test_flags_repeated_paragraph_plus_short_list_groups(self) -> None:
        text = """适用情形：
- 情形一
- 情形二
- 情形三

法律后果：
- 后果一
- 后果二
"""

        self.assertIn("504", codes(text))

    def test_accepts_parentified_short_list_groups(self) -> None:
        text = """- **适用情形**
  - 情形一
  - 情形二
  - 情形三
- **法律后果**
  - 后果一
  - 后果二
"""

        self.assertNotIn("504", codes(text))

    def test_rejects_mechanical_line_breaks_and_dangling_color_anchor(self) -> None:
        text = """**行政强制执行**{: style="color: var(--b3-font-color10);"}，
是指**行政机关**{: style="color: var(--b3-font-color10);"}或者**行政机关**{: style="color: var(--b3-font-color10);"}向人民**法院**{: style="color: var(--b3-font-color12);"}申请，
**对不履行**{: style="background-color: var(--b3-font-background11);"}行政决定的`公民、法人或者其他组织`，
依法强制其履行义务的<u>行为</u>。**强制执行**{: style="color: var(--b3-font-color12);"}
"""

        self.assertTrue({"505", "506"} <= codes(text))

    def test_accepts_semantically_structured_definition(self) -> None:
        text = """**行政强制执行**{: style="color: var(--b3-font-color10);"}是指：

- **执行路径**
    - 由**行政机关**{: style="color: var(--b3-font-color10);"}直接实施；
    - 由**行政机关**{: style="color: var(--b3-font-color10);"}向人民**法院**{: style="color: var(--b3-font-color12);"}申请执行。
- **执行对象**
    - **不履行**{: style="background-color: var(--b3-font-background11);"}行政决定的`公民、法人或者其他组织`。
- **执行内容**
    - 依法强制其==履行义务==。
"""

        self.assertFalse({"505", "506"} & codes(text))

    def test_rejects_adjacent_complete_sentences_as_a_soft_break(self) -> None:
        text = """**行政机关**{: style="color: var(--b3-font-color10);"}依法作出决定。
**相对人**{: style="color: var(--b3-font-color11);"}应当履行义务。
"""

        self.assertIn("505", codes(text))

    def test_accepts_blank_separated_paragraphs(self) -> None:
        text = """**行政机关**{: style="color: var(--b3-font-color10);"}依法作出决定。

**相对人**{: style="color: var(--b3-font-color11);"}应当履行义务。
"""

        self.assertNotIn("505", codes(text))

    def test_accepts_a_plain_lead_followed_by_a_list(self) -> None:
        text = """**执行路径**{: style="color: var(--b3-font-color10);"}包括：
- 行政机关直接实施。
- 行政机关申请法院执行。
"""

        self.assertNotIn("505", codes(text))

    def test_rejects_fragmented_plain_prose_inside_callout(self) -> None:
        text = """> [!NOTE] 定义
> **行政强制执行**{: style="color: var(--b3-font-color10);"}，
> 是指行政机关依法采取措施，
> 强制相对人履行义务的行为。
"""

        self.assertIn("505", codes(text))

    def test_accepts_callout_directive_then_one_body_line(self) -> None:
        text = """> [!IMPORTANT] ❗ 一句话定案
> 处罚看**制裁性**{: style="color: var(--b3-font-color12); background-color: var(--b3-font-background12);"}与**惩戒**{: style="color: var(--b3-font-color12);"}；**注销**{: style="color: var(--b3-font-color10);"}、**强制隔离**{: style="color: var(--b3-font-color10);"}、**责令召回**{: style="color: var(--b3-font-color10);"}均无制裁性。
"""

        self.assertNotIn("505", codes(text))

    def test_ignores_fragment_like_text_inside_fence(self) -> None:
        text = """```md
行政强制执行，
是指行政机关依法采取措施，
强制相对人履行义务的行为。
```
"""

        self.assertNotIn("505", codes(text))

    def test_rejects_siyuan_ial_inside_plain_or_quoted_code_fence(self) -> None:
        cases = (
            "```md\n**行政机关**{: style=\"color: var(--b3-font-color10);\"}\n```",
            "> ```md\n> {: custom-qb-section=\"solution\"}\n> ```",
        )

        for text in cases:
            with self.subTest(text=text):
                self.assertIn("508", codes(text))

    def test_allows_standard_markdown_inside_a_code_fence(self) -> None:
        text = "```md\n**行政机关**应当作出决定。\n```"

        self.assertNotIn("508", codes(text))

    def test_allows_a_single_unpunctuated_prose_line(self) -> None:
        text = "**行政机关**{: style=\"color: var(--b3-font-color10);\"}仍需继续说明的条件"

        self.assertNotIn("505", codes(text))

    def test_does_not_misclassify_color_or_block_ial_as_a_soft_break(self) -> None:
        cases = (
            "**行政机关**{: style=\"color: var(--b3-font-color10);\"}依法履职。",
            "行政机关依法履职。\n{: style=\"color: var(--b3-font-color10);\"}",
            "> [!NOTE] 提示\n> **行政机关**{: style=\"color: var(--b3-font-color10);\"}依法履职。",
        )

        for text in cases:
            with self.subTest(text=text):
                self.assertFalse({"505", "506", "508"} & codes(text))

    def test_reports_a_real_soft_break_without_invalidating_color_anchors(self) -> None:
        text = """**行政机关**{: style="color: var(--b3-font-color10);"}依法作出决定，
**相对人**{: style="color: var(--b3-font-color11);"}应当履行义务。
"""

        self.assertIn("505", codes(text))
        self.assertFalse({"506", "508"} & codes(text))

    def test_rejects_bare_list_continuation(self) -> None:
        text = """- **执行路径**{: style="color: var(--b3-font-color10);"}
    行政机关可以直接实施。
"""

        self.assertIn("505", codes(text))

    def test_rejects_inline_enumeration_inside_a_list_item(self) -> None:
        cases = (
            "- **现场笔录**{: style=\"color: var(--b3-font-color10);\"}：1. 由执法人员和当事人签名。",
            "- **审查顺序**。2) 再判断程序是否完备。",
            "- **法定条件**（1）主体适格；（2）程序完备。",
        )

        for text in cases:
            with self.subTest(text=text):
                self.assertIn("507", codes(text))

    def test_accepts_indented_ordered_sublist(self) -> None:
        text = """- **现场笔录**{: style="color: var(--b3-font-color10);"}：
    1. 由执法人员和当事人签名。
    2. 当事人有异议时，执法人员应出庭。
"""

        self.assertNotIn("507", codes(text))

    def test_allows_a_statutory_article_number_inside_a_list_item(self) -> None:
        text = "- **法源**：依《行政处罚法》第1条适用。\n"

        self.assertNotIn("507", codes(text))

    def test_goldquest_also_rejects_plain_soft_breaks(self) -> None:
        text = """第一句完整。
第二句完整。
"""

        self.assertIn("505", codes(text, "legal-goldquest"))

    def test_ignores_yaml_frontmatter(self) -> None:
        text = """---
title: 行政强制执行
tags: 行政法, 强制执行
---
**行政机关**{: style="color: var(--b3-font-color10);"}依法作出决定。
"""

        self.assertNotIn("505", codes(text))

    def test_default_table_gate_accepts_three_by_three(self) -> None:
        text = """| 维度 | 概念甲 | 概念乙 |
| --- | --- | --- |
| 主体 | 甲 | 乙 |
| 要件 | A | B |
| 后果 | 有效 | 无效 |
"""

        self.assertNotIn("411", codes(text))

    def test_strict_table_gate_rejects_more_than_two_by_two(self) -> None:
        text = """| 维度 | 概念甲 | 概念乙 |
| --- | --- | --- |
| 主体 | 甲 | 乙 |
| 要件 | A | B |
| 后果 | 有效 | 无效 |
"""

        self.assertIn("411", codes(text, max_table_columns=2, max_table_rows=2))

    def test_table_gate_can_be_explicitly_relaxed(self) -> None:
        text = """| 维度 | 甲 | 乙 | 丙 |
| --- | --- | --- | --- |
| 主体 | A | B | C |
| 要件 | A | B | C |
| 程序 | A | B | C |
| 后果 | A | B | C |
"""

        self.assertNotIn("411", codes(text, max_table_columns=4, max_table_rows=4))

    def test_source_table_is_exempt_from_size_gate(self) -> None:
        source = """| 维度 | 甲 | 乙 | 丙 |
| --- | --- | --- | --- |
| 主体 | A | B | C |
| 要件 | A | B | C |
| 程序 | A | B | C |
| 后果 | A | B | C |
"""

        self.assertNotIn("411", codes(source, source=source, max_table_columns=2, max_table_rows=2))

    def test_flags_monotonous_peer_concept_list_palette(self) -> None:
        text = "\n".join([
            '- **权利能力**{: style="color: var(--b3-font-color10);"}：主体资格。',
            '- **行为能力**{: style="color: var(--b3-font-color10);"}：行为门槛。',
            '- **责任能力**{: style="color: var(--b3-font-color10);"}：责任后果。',
        ])

        self.assertIn("503", codes(text))

    def test_accepts_functionally_varied_concept_list_palette(self) -> None:
        text = "\n".join([
            '- **权利能力**{: style="color: var(--b3-font-color10);"}：主体资格。',
            '- **行为能力**{: style="color: var(--b3-font-color11);"}：行为门槛。',
            '- **责任能力**{: style="background-color: var(--b3-font-background13);"}：责任后果。',
        ])

        self.assertNotIn("503", codes(text))

    def test_accepts_semantically_styled_table_and_callout(self) -> None:
        text = (
            "> [!NOTE] 法条\n"
            "> \n"
            "> **要件**是==主体资格==。\n\n"
            "| 审查 | 规则 | 结果 |\n"
            "| :--- | :--- | :--- |\n"
            "| 主体 | **资格**{: style=\"color: var(--b3-font-color10);\"} | ==适格==。 |\n"
            "| 后果 | **责任**{: style=\"color: var(--b3-font-color13);\"} | <em>承担责任</em>。 |\n"
        )
        self.assertEqual(codes(text), set())

    def test_rejects_generated_label_rule_table(self) -> None:
        text = """| 启动方式 | 具体规定 |
| --- | --- |
| 本院启动 | 院长认为裁判确有错误时，提交审判委员会讨论决定再审。 |
| 上级法院启动 | 上级法院认为下级法院裁判确有错误时，有权启动再审。 |
"""

        self.assertIn("413", codes(text))

    def test_allows_unchanged_source_label_rule_table(self) -> None:
        source = """| 启动方式 | 具体规定 |
| --- | --- |
| 本院启动 | 院长认为裁判确有错误时，提交审判委员会讨论决定再审。 |
| 上级法院启动 | 上级法院认为下级法院裁判确有错误时，有权启动再审。 |
"""

        self.assertNotIn("413", codes(source, source=source))

    def test_rejects_long_adjacent_and_escaped_highlights(self) -> None:
        text = "==这是一个明显过长的高亮==\n==主体====结果==\n\\=错误"
        self.assertTrue({"101", "102", "103"} <= codes(text))

    def test_rejects_markdown_italic_and_underscore_bold(self) -> None:
        text = "*星号斜体*\n_下划线斜体_\n__下划线加粗__"

        self.assertTrue({"104", "105"} <= codes(text))

    def test_accepts_sparse_em_italic_and_double_asterisk_bold(self) -> None:
        text = "<em>轻旁注</em>与**关键结论**。"

        self.assertFalse({"104", "105"} & codes(text))

    def test_accepts_colored_underline_inside_tag(self) -> None:
        text = '**重点**{: style="color: var(--b3-font-color10);"}：<u style="color: var(--b3-font-color11);">短语</u>'

        self.assertNotIn("205", codes(text))

    def test_rejects_external_style_ial_after_underline(self) -> None:
        text = '**重点**{: style="color: var(--b3-font-color10);"}：<u>短语</u>{: style="color: var(--b3-font-color11);"}'

        self.assertIn("205", codes(text))

    def test_ignores_emphasis_examples_in_code_and_question_fences(self) -> None:
        text = "`*foo* _foo_ __foo__`\n> ```md\n> *原题字符*\n> ```"

        self.assertFalse({"104", "105"} & codes(text))

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
        self.assertNotIn("105", codes(text))

    def test_rejects_split_table_without_real_header(self) -> None:
        text = """| 本院启动 | 院长 | 提交审判委员会讨论 |
| 上级法院启动 | 上级法院 | 直接启动再审 |
"""

        self.assertIn("414", codes(text))

    def test_rejects_merged_data_row_used_as_markdown_header(self) -> None:
        text = """| {: rowspan='2'}确认调解协议效力 | 符合条件 | 裁定确认效力 |
| --- | --- | --- |
| {: class='fn__none'} | 不符合条件 | 裁定驳回申请 |
"""

        self.assertIn("416", codes(text))

    def test_accepts_real_header_before_merged_data_rows(self) -> None:
        text = """| 程序 | 审查结果 | 法律后果 |
| --- | --- | --- |
| {: rowspan='2'}确认调解协议效力 | 符合条件 | 裁定确认效力 |
| {: class='fn__none'} | 不符合条件 | 裁定驳回申请 |
"""

        self.assertFalse({"414", "415", "416"} & codes(text))

    def test_allows_unchanged_legacy_merged_header_with_source(self) -> None:
        source = """| {: rowspan='2'}确认调解协议效力 | 符合条件 | 裁定确认效力 |
| --- | --- | --- |
| {: class='fn__none'} | 不符合条件 | 裁定驳回申请 |
"""

        self.assertNotIn("416", codes(source, source=source))

    def test_compares_source_images_tables_merge_tokens_and_headings(self) -> None:
        source = "# 原标题\n![](assets/a.png)\n| {: colspan='2'}内容 | 空格 |"
        output = "# 新标题\n普通正文"
        self.assertTrue({"701", "702", "703", "704"} <= codes(output, source=source))

    def test_source_shell_headings_need_explicit_repair_mode(self) -> None:
        source = "# 商法\n### 热点\n##### 1.\n正文\n#### 例1：\n例子\n"
        output = "# 商法\n正文\n例子\n"

        self.assertIn("704", codes(output, source=source))
        self.assertNotIn(
            "704",
            codes(output, source=source, allow_structural_repair=True),
        )

    def test_source_heading_spacing_and_trailing_colon_are_normalized(self) -> None:
        source = "# 商法\n### 3出资责任：\n"
        output = "# 商法\n#### 3 出资责任\n"

        self.assertNotIn("704", codes(output, source=source))

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

    def test_accepts_table_converted_with_horizontal_columns_as_parents(self) -> None:
        source = """| 比较维度 | 概念A | 概念B |
| --- | --- | --- |
| 要件 | 要件甲 | 要件乙 |
| 后果 | 后果甲 | 后果乙 |
"""
        output = """- **概念A**
    - **比较维度**
    - **要件**：要件甲
    - **后果**：后果甲
- **概念B**
    - **要件**：要件乙
    - **后果**：后果乙
"""

        self.assertNotIn("702", codes(output, source=source))

    def test_accepts_table_converted_with_vertical_rows_as_parents(self) -> None:
        source = """| 制度 | 要件 | 后果 |
| --- | --- | --- |
| 制度A | 要件甲 | 后果甲 |
| 制度B | 要件乙 | 后果乙 |
"""
        output = """- **制度A**
    - **要件**：要件甲
    - **后果**：后果甲
- **制度B**
    - **要件**：要件乙
    - **后果**：后果乙
"""

        self.assertNotIn("702", codes(output, source=source))

    def test_axis_list_conversion_still_requires_every_labeled_cell(self) -> None:
        source = """| 比较维度 | 概念A | 概念B |
| --- | --- | --- |
| 要件 | 要件甲 | 要件乙 |
| 后果 | 后果甲 | 后果乙 |
"""
        output = """- **概念A**
    - **要件**：要件甲
    - **后果**：后果甲
- **概念B**
    - **要件**：要件乙
"""

        self.assertIn("702", codes(output, source=source))

    def test_rejects_generated_simple_label_rule_table(self) -> None:
        text = """| 启动方式 | 具体规定 |
| --- | --- |
| 本院启动 | 院长认为裁判确有错误时，提交审判委员会讨论决定再审。 |
| 上级法院启动 | 上级法院认为下级法院裁判确有错误时，有权启动再审。 |
"""

        self.assertIn("413", codes(text))

    def test_allows_unchanged_source_label_rule_table(self) -> None:
        source = """| 启动方式 | 具体规定 |
| --- | --- |
| 本院启动 | 院长认为裁判确有错误时，提交审判委员会讨论决定再审。 |
| 上级法院启动 | 上级法院认为下级法院裁判确有错误时，有权启动再审。 |
"""

        self.assertNotIn("413", codes(source, source=source))

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

    def test_medium_marknote_accepts_div_wrapped_html_visual(self) -> None:
        text = """### 程序
**申请人**{: style="color: var(--b3-font-color10);"}提出申请。
- **受理**{: style="background-color: var(--b3-font-background11);"}
    - **法院**{: style="color: var(--b3-font-color8);"}审查。
- **驳回**{: style="background-color: var(--b3-font-background13);"}
    - **申请人**{: style="color: var(--b3-font-color10);"}补正。
> ```html
> <div class="legal-visual"><strong>申请</strong><span>→</span><strong>审查</strong></div>
> ```
"""

        self.assertNotIn("624", codes(text))

    def test_medium_marknote_accepts_labeled_static_svg_visual(self) -> None:
        text = """### 程序
**申请人**{: style="color: var(--b3-font-color10);"}提出申请。
- **受理**{: style="background-color: var(--b3-font-background11);"}
    - **法院**{: style="color: var(--b3-font-color8);"}审查。
- **驳回**{: style="background-color: var(--b3-font-background13);"}
    - **申请人**{: style="color: var(--b3-font-color10);"}补正。
![申请审查流程图](assets/application-review.svg)
"""

        self.assertNotIn("624", codes(text))

    def test_medium_marknote_requires_a_semantic_emoji_label(self) -> None:
        text = """### 程序
- **申请**{: style="color: var(--b3-font-color10);"}
    - **法院**{: style="color: var(--b3-font-color8);"}审查。
- **补正**{: style="background-color: var(--b3-font-background11);"}
    - **申请人**{: style="color: var(--b3-font-color10);"}补充材料。
- **驳回**{: style="background-color: var(--b3-font-background13);"}
    - **申请人**{: style="color: var(--b3-font-color10);"}承担不利后果。
"""

        self.assertIn("509", codes(text))
        self.assertNotIn("509", codes(text.replace("- **申请**", "- 🧭 **申请**")))
        self.assertNotIn("509", codes(text.replace("- **申请**", "- 🧭⚠️ **申请**")))
        self.assertNotIn("509", codes(text.replace("- **申请**", "- 🧱 **申请**")))

    def test_ordinary_png_does_not_satisfy_visual_gate(self) -> None:
        text = """### 程序
**申请人**{: style="color: var(--b3-font-color10);"}提出申请。
- **受理**{: style="background-color: var(--b3-font-background11);"}
    - **法院**{: style="color: var(--b3-font-color8);"}审查。
- **驳回**{: style="background-color: var(--b3-font-background13);"}
    - **申请人**{: style="color: var(--b3-font-color10);"}补正。
![教材截图](assets/source-page.png)
"""

        self.assertIn("624", codes(text))

    def test_rejects_goldquest_answer_leak_and_checked_option(self) -> None:
        text = """##### 1题
* 题干含==正确答案==
    - [x] A. 选项
**成立**{: style=\"color: var(--b3-font-color8);\"}
"""
        self.assertTrue({"601", "603"} <= codes(text, "legal-goldquest"))

    def test_rejects_stem_and_multiple_subquestions_on_one_line(self) -> None:
        text = """##### 1. 发起人责任·判断
{: custom-qb-id="commercial-company-promoter-001" custom-qb-question-topic-ids="commercial-company-promoter-liability"}
* 甲、乙设立公司，甲与丙签订仓库租赁合同。（1）公司成立后由谁负责？（2）公司未成立时由谁负责？
###### 答案与解析
- 正确答案：第一问甲与公司，第二问甲。
{: custom-qb-section="solution"}
"""

        self.assertTrue({"628", "629"} <= codes(text, "legal-goldquest"))

    def test_accepts_separate_stem_and_one_line_subquestions(self) -> None:
        text = """##### 1. 发起人责任·判断
{: custom-qb-id="commercial-company-promoter-001" custom-qb-question-topic-ids="commercial-company-promoter-liability"}
* **题干**：甲、乙设立公司，甲与丙签订仓库租赁合同。
* **问题**：
    1. 公司成立后由谁负责？
    2. 公司未成立时由谁负责？
###### 答案与解析
- 正确答案：第一问甲与公司，第二问甲。
{: custom-qb-section="solution"}
"""

        self.assertFalse({"628", "629"} & codes(text, "legal-goldquest"))

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


class GoldQuestOptionAnalysisGateTests(unittest.TestCase):
    def test_medium_goldquest_analysis_requires_a_non_decision_semantic_emoji(self) -> None:
        analysis = (
            '- ❌ A. **要约**{: style="color: var(--b3-font-color10);"}一经发出，~~即不得撤回~~。\n'
            '    - **破绽**{: style="color: var(--b3-font-color13);"}：撤回取决于通知到达时间。\n'
            '- ✅ B. **承诺**{: style="color: var(--b3-font-color11);"}在==到达要约人时==生效。\n'
            '    - **破题点**{: style="color: var(--b3-font-color8);"}：抓住承诺通知的到达时间。\n'
            '- **规则定位**{: style="color: var(--b3-font-color10);"}：要约与承诺分别适用不同生效规则。'
        )

        self.assertIn("509", codes(goldquest_options(analysis), "legal-goldquest"))
        self.assertNotIn("509", codes(goldquest_options(analysis.replace("- **规则定位**", "- 🧭 **规则定位**")), "legal-goldquest"))
        self.assertNotIn("509", codes(goldquest_options(analysis.replace("- **规则定位**", "- 📜 **规则定位**")), "legal-goldquest"))

    def test_rejects_summary_without_complete_option_or_reason(self) -> None:
        text = goldquest_options("- ❌ A 项错误，因为要约可以撤回。")

        self.assertTrue({"630", "631", "632"} <= codes(text, "legal-goldquest"))

    def test_rejects_emoji_only_without_cue_inside_option(self) -> None:
        text = goldquest_options(
            "- ❌ A. 要约一经发出，即不得撤回。\n"
            "    - **破绽**{: style=\"color: var(--b3-font-color13);\"}：规则并非绝对。"
        )

        result = codes(text, "legal-goldquest")
        self.assertIn("631", result)
        self.assertFalse({"630", "632"} & result)

    def test_rejects_marked_option_without_immediate_reason(self) -> None:
        text = goldquest_options(
            '- ❌ A. **要约**{: style="color: var(--b3-font-color10);"}一经发出，~~即不得撤回~~。'
        )

        result = codes(text, "legal-goldquest")
        self.assertIn("632", result)
        self.assertFalse({"630", "631"} & result)

    def test_accepts_complete_marked_options_with_reasons(self) -> None:
        text = goldquest_options(
            '- ❌ A. **要约**{: style="color: var(--b3-font-color10);"}一经发出，~~即不得撤回~~。\n'
            '    - **破绽**{: style="color: var(--b3-font-color13);"}：撤回取决于通知到达时间。\n'
            '- ✅ B. **承诺**{: style="color: var(--b3-font-color11);"}在==到达要约人时==生效。\n'
            '    - **破题点**{: style="color: var(--b3-font-color8);"}：抓住承诺通知的到达时间。'
        )

        self.assertFalse({"630", "631", "632"} & codes(text, "legal-goldquest"))

    def test_rejects_decision_emoji_that_disagrees_with_answer(self) -> None:
        text = goldquest_options(
            '- ✅ A. **要约**{: style="color: var(--b3-font-color10);"}一经发出，~~即不得撤回~~。\n'
            '    - **破绽**{: style="color: var(--b3-font-color13);"}：撤回取决于通知到达时间。'
        )

        self.assertIn("631", codes(text, "legal-goldquest"))

    def test_rejects_option_reference_without_replay_line(self) -> None:
        text = goldquest_options(
            '**判断**{: style="color: var(--b3-font-color13);"}：本题A项错误，因为要约可以撤回。'
        )

        self.assertIn("630", codes(text, "legal-goldquest"))

    def test_ignores_option_words_inside_fenced_visual_source(self) -> None:
        text = goldquest_options("```mermaid\nflowchart LR\n    A项规则 --> B项结论\n```")

        self.assertNotIn("630", codes(text, "legal-goldquest"))

    def test_long_complete_option_replay_is_not_subject_to_prose_line_limit(self) -> None:
        option = "要约一经发出，无论撤回通知何时到达受要约人，也无论受要约人是否已经知悉，要约人均不得撤回。"
        text = goldquest_options(
            '- ❌ A. **要约**{: style="color: var(--b3-font-color10);"}一经发出，~~无论撤回通知何时到达受要约人，也无论受要约人是否已经知悉，要约人均不得撤回~~。\n'
            '    - **破绽**{: style="color: var(--b3-font-color13);"}：撤回仍取决于通知到达时间。',
            option_a=option,
        )

        result = codes(text, "legal-goldquest")
        self.assertFalse({"505", "621", "630", "631", "632"} & result)

    def test_source_rule_map_must_survive_option_replays(self) -> None:
        source = goldquest_options(
            "- **一高＝组成部门**\n"
            "    - 设立、撤销由全国人大及其常委会决定。\n"
            "- **中间层级＝直属机构**\n"
            "    - 设撤并由国务院决定。\n"
            "- **组织协调**\n"
            "    - 跨机构协调由议事协调机构承担。"
        )
        output = goldquest_options(
            '- ❌ A. **要约**{: style="color: var(--b3-font-color10);"}一经发出，~~即不得撤回~~。\n'
            '    - **破绽**{: style="color: var(--b3-font-color13);"}：撤回取决于通知到达时间。\n'
            '- ✅ B. **承诺**{: style="color: var(--b3-font-color11);"}在==到达要约人时==生效。\n'
            '    - **破题点**{: style="color: var(--b3-font-color8);"}：抓住到达时间。'
        )

        self.assertIn("633", codes(output, "legal-goldquest", source=source))

    def test_source_rule_map_can_coexist_with_option_replays(self) -> None:
        source = goldquest_options(
            "- **一高＝组成部门**\n"
            "    - 设立、撤销由全国人大及其常委会决定。\n"
            "- **中间层级＝直属机构**\n"
            "    - 设撤并由国务院决定。\n"
            "- **组织协调**\n"
            "    - 跨机构协调由议事协调机构承担。"
        )
        output = goldquest_options(
            '- **一高＝组成部门**\n'
            '    - 设立、撤销由全国人大及其常委会决定。\n'
            '- **中间层级＝直属机构**\n'
            '    - 设撤并由国务院决定。\n'
            '- **组织协调**\n'
            '    - 跨机构协调由议事协调机构承担。\n\n'
            '- ❌ A. **要约**{: style="color: var(--b3-font-color10);"}一经发出，~~即不得撤回~~。\n'
            '    - **破绽**{: style="color: var(--b3-font-color13);"}：撤回取决于通知到达时间。\n'
            '- ✅ B. **承诺**{: style="color: var(--b3-font-color11);"}在==到达要约人时==生效。\n'
            '    - **破题点**{: style="color: var(--b3-font-color8);"}：抓住到达时间。'
        )

        self.assertNotIn("633", codes(output, "legal-goldquest", source=source))


if __name__ == "__main__":
    unittest.main()
