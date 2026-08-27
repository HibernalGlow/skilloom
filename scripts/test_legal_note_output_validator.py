from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))

from legal_note_output_validator import validate_goldquest_source_content, validate_text  # noqa: E402

VALIDATOR = Path(__file__).resolve().with_name("legal_note_output_validator.py")


def run_validator(flags: list[str], content: str) -> subprocess.CompletedProcess[str]:
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as handle:
        handle.write(content)
        path = handle.name
    try:
        return subprocess.run(
            [sys.executable, "-X", "utf8", str(VALIDATOR), path, "--profile", "legal-marknote", *flags],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    finally:
        Path(path).unlink(missing_ok=True)


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
* 关于要约与承诺，下列说法正确的是？
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

    def test_rejects_list_items_starting_with_an_ordered_marker(self) -> None:
        cases = (
            "- 1. 债务加入生效后。",
            "- 1、第一项。",
            "- （1）主体适格。",
            "- （2） 主体不适格的除外。",
            "- ① 一部单行刑法。",
            "    - ② 嵌套子项同样禁止。",
        )

        for text in cases:
            with self.subTest(text=text):
                self.assertIn("311", codes(text))
                self.assertIn("311", codes(text, "legal-goldquest"))

    def test_accepts_numbers_that_are_not_ordered_markers(self) -> None:
        decimal = "- 利率提高到 1.5 倍。\n"
        self.assertNotIn("311", codes(decimal))
        # A mid-content enumeration stays a W507 warning, not the hard E311.
        mid = "- **现场笔录**{: style=\"color: var(--b3-font-color10);\"}：1. 由执法人员和当事人签名。\n"
        result = codes(mid)
        self.assertNotIn("311", result)
        self.assertIn("507", result)
        # Real indented ordered children are the sanctioned form.
        children = "- **现场笔录**：\n    1. 由执法人员和当事人签名。\n    2. 当事人有异议时，执法人员应出庭。\n"
        self.assertNotIn("311", codes(children))

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

    def test_accepts_question_callout(self) -> None:
        text = """> [!QUESTION] ✏️ 检察院控诉职能与监督职能的区分
> ```md
> [判断] 1.
> 检察院的控诉职能与监督职能如何区分？
> ```
>
> **回答与解析：**
> 1. 控诉职能针对个案，监督职能针对诉讼活动。
"""
        self.assertFalse({"303", "307", "308", "309"} & codes(text))

    def test_rejects_generic_question_callout_title(self) -> None:
        text = """> [!QUESTION] ✏️ 习题1
> ```md
> [判断] 1.
> 检察院的控诉职能与监督职能如何区分？
> ```
>
> **回答与解析：**
> 1. 控诉职能针对个案，监督职能针对诉讼活动。
"""
        self.assertIn("307", codes(text))

    def test_question_callout_requires_stem_code_block(self) -> None:
        text = """> [!QUESTION] ✏️ 表见代理的构成要件
> 表见代理的构成要件包括哪些？
>
> **回答与解析：**
> 1. 行为人无代理权。
"""
        self.assertIn("308", codes(text))

    def test_question_callout_requires_answer_inside_callout_after_stem_block(self) -> None:
        stem_only = """> [!QUESTION] ✏️ 表见代理的构成要件
> ```md
> [判断] 1.
> 表见代理的构成要件包括哪些？
> ```
"""
        answer_outside = stem_only + "\n**回答与解析：**\n1. 行为人无代理权。\n"
        answer_before = """> [!QUESTION] ✏️ 表见代理的构成要件
> **回答与解析：**
> 1. 行为人无代理权。
>
> ```md
> [判断] 1.
> 表见代理的构成要件包括哪些？
> ```
"""
        for label, text in (("stem-only", stem_only), ("answer-outside", answer_outside), ("answer-before", answer_before)):
            with self.subTest(label=label):
                self.assertIn("309", codes(text))

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

    def test_keeps_exercise_counter_heading_inside_question_callout(self) -> None:
        text = """> [!QUESTION] ✏️ 合同效力判断
> ```md
> [判断] 1.
> 合同效力：甲与乙签订合同，该合同是否有效？
> ```
>
> **回答与解析：**
> 1. 合同有效。
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
        self.assertNotIn("509", codes(text.replace("- **申请**", "- **申请** 🧱")))
        self.assertNotIn("509", codes(text.replace("承担不利后果。", "承担不利后果。🧭")))

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
* 甲、乙设立公司，甲与丙签订仓库租赁合同。
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
        self.assertNotIn("509", codes(goldquest_options(analysis.replace("不同生效规则。", "不同生效规则。📜")), "legal-goldquest"))
        self.assertIn("509", codes(goldquest_options(analysis.replace("~~即不得撤回~~。", "~~即不得撤回~~。📜")), "legal-goldquest"))

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


class GoldquestSourceContentGateTests(unittest.TestCase):
    GQ_SOURCE = """### 考点1 测试考点
64.甲向乙交付货物, 乙未付款.下列哪一选项是正确的?(模拟, 单)
A. 乙应当付款
B. 乙无需付款
C. 甲无权请求付款
D. 合同无效

65.丙将房屋出售给丁并办理登记.下列哪一选项是正确的?(模拟, 单)
A. 丁取得房屋所有权
B. 丙仍为所有权人
C. 丁未取得所有权
D. 合同无效
"""

    GQ_ONE = """##### [测试·单选] 64.
{: custom-qb-id="q-64" custom-qb-answer="A" custom-qb-question-topic-ids="t"}
* 甲向乙交付货物, 乙未付款.下列哪一选项是正确的?
    - [ ] A. 乙应当付款
    - [ ] B. 乙无需付款
    - [ ] C. 甲无权请求付款
    - [ ] D. 合同无效
"""

    GQ_BOTH = GQ_ONE + """##### [测试·单选] 65.
{: custom-qb-id="q-65" custom-qb-answer="A" custom-qb-question-topic-ids="t"}
* 丙将房屋出售给丁并办理登记.下列哪一选项是正确的?
    - [ ] A. 丁取得房屋所有权
    - [ ] B. 丙仍为所有权人
    - [ ] C. 丁未取得所有权
    - [ ] D. 合同无效
"""

    def source_gate_codes(self, output: str, source: str) -> set[str]:
        return {finding.code for finding in validate_goldquest_source_content(output, source)}

    def test_rejects_dropped_question_within_covered_scope(self) -> None:
        codes = self.source_gate_codes(self.GQ_ONE, self.GQ_SOURCE)
        self.assertIn("814", codes)

    def test_accepts_full_source_coverage(self) -> None:
        codes = self.source_gate_codes(self.GQ_BOTH, self.GQ_SOURCE)
        self.assertNotIn("814", codes)

    def test_skips_sections_the_output_does_not_cover(self) -> None:
        source = self.GQ_SOURCE + """### 考点2 另一考点
66.戊向己借款.下列哪一选项是正确的?(模拟, 单)
A. 己应当还款
B. 戊无权请求还款
C. 借款合同无效
D. 利息过高
"""
        codes = self.source_gate_codes(self.GQ_ONE, source)
        self.assertIn("814", codes)  # 考点1 内 65 缺失仍报

    def test_skips_partial_scope_with_low_section_coverage(self) -> None:
        expanded = self.GQ_SOURCE + "\n".join(
            f"{num}.模拟题干第{num}题事实充分足以匹配.{num}下列哪一选项是正确的?(模拟, 单)\n"
            f"A. 选项{num}甲\nB. 选项{num}乙\nC. 选项{num}丙\nD. 选项{num}丁\n"
            for num in range(66, 72)
        )
        # 考点1 扩到 8 题, 输出只覆盖 1 → 覆盖 12.5% < 50% → 作用域不确定, 不报缺题
        codes = self.source_gate_codes(self.GQ_ONE, expanded)
        self.assertNotIn("814", codes)

    def test_warns_when_covered_question_analysis_is_heavily_compressed(self) -> None:
        analysis = "\n".join(
            f"解析要点第{i}条: 该规则要求当事人全面履行义务并承担相应责任, 不得擅自变更."
            for i in range(1, 30)
        )
        source = self.GQ_SOURCE.replace("D. 合同无效\n", "D. 合同无效\n" + analysis + "\n")
        codes = self.source_gate_codes(self.GQ_BOTH, source)
        self.assertIn("815", codes)


class EmojiSemanticsGateTests(unittest.TestCase):
    def test_rejects_repeated_same_emoji(self) -> None:
        repeated = "🚨 伪造文件" * 9
        self.assertIn("510", codes(repeated, "legal-marknote"))
        moderate = "🚨 伪造文件" * 6 + " ⚖️ 合同效力 " + "🔍 检索"
        self.assertNotIn("510", codes(moderate, "legal-marknote"))

    def test_warns_when_emoji_anchors_generic_cue_word(self) -> None:
        generic = "🚨 注意：伪造文件不构成表见事由"
        self.assertIn("511", codes(generic, "legal-marknote"))
        concept = "⚖️ 合同效力：双方共同申请"
        self.assertNotIn("511", codes(concept, "legal-marknote"))

    def test_warns_on_batch_like_emoji_word_pair(self) -> None:
        batch = "🚨 注意：伪造" * 6
        self.assertIn("512", codes(batch, "legal-marknote"))
        concept_repeat = "🚚 指示交付" * 5
        self.assertNotIn("512", codes(concept_repeat, "legal-marknote"))

    def test_warns_when_emoji_pile_up_at_sentence_ends(self) -> None:
        tail = "房地一体登记应一并申请无先后顺序🚨。\n住宅用地届满自动续期不丧失所有权🧭。\n过户须由双方共同申请⏳。\n应纳税所得额减原值与费用⚖️。\n本案按全额计税错误📚。\n以户为承包单位不得继承💡。"
        self.assertIn("513", codes(tail, "legal-marknote"))
        attached = "简易交付🚚、指示交付📦、占有改定⛓；\n住宅用地届满**自动续期**⏳；\n双方**共同申请**🧭；\n应纳税所得额**减原值与费用**⚖️。"
        self.assertNotIn("513", codes(attached, "legal-marknote"))

    def test_warns_when_emoji_bunch_up_at_line_heads(self) -> None:
        heads = "- 🚚 **指示交付**：第三人占有动产。\n- ⏳ **自动续期**：届满自动续期。\n- 🧭 **共同申请**：双方共同申请。\n- ⚖️ **合同效力**：合同有效。\n- 📚 **计税口径**：减原值与费用。"
        self.assertIn("514", codes(heads, "legal-marknote"))
        mixed = "简易交付🚚、指示交付📦、占有改定⛓；\n期限届满**自动续期**⏳；\n双方**共同申请**🧭；\n甲将花瓶卖给黄某📦完成交付。\n以户为承包单位**不得继承**💡。"
        self.assertNotIn("514", codes(mixed, "legal-marknote"))

    def test_rejects_dangling_emoji_without_a_concept_neighbor(self) -> None:
        floating = "额外情形。🚨\n、📦、\n；⏳、\n提交。🛑；\n、🎯；\n排除。🧭"
        self.assertIn("515", codes(floating, "legal-marknote"))
        attached = "要件已明确🚨、期限届满⏳、双方共同申请🧭、按约定处理📚、余额计税⚖️。"
        codeset = codes(attached, "legal-marknote")
        self.assertNotIn("515", codeset)
        self.assertNotIn("513", codeset)

    def test_callout_directive_requires_preceding_blank_line(self) -> None:
        no_blank = "- 设立居住权的住宅原则上不得出租。\n> [!CAUTION] 例外\n> 另有约定除外。"
        self.assertIn("310", codes(no_blank, "legal-marknote"))
        with_blank = "- 设立居住权的住宅原则上不得出租。\n\n> [!CAUTION] 例外\n> 另有约定除外。"
        self.assertNotIn("310", codes(with_blank, "legal-marknote"))

    def test_rejects_adjacent_lines_dominated_by_same_color(self) -> None:
        monotone = "- **一个**{: style=\"color: var(--b3-font-color12);\"}、**两个**{: style=\"color: var(--b3-font-color12);\"}。\n- **三个**{: style=\"color: var(--b3-font-color12);\"}都同色。\n- **四个**{: style=\"color: var(--b3-font-color12);\"}仍同色。"
        self.assertIn("204", codes(monotone, "legal-marknote"))
        diverse = "- **一个**{: style=\"color: var(--b3-font-color12);\"}、**两个**{: style=\"color: var(--b3-font-color8);\"}。\n- **三个**{: style=\"color: var(--b3-font-color13);\"}不同色。"
        self.assertNotIn("204", codes(diverse, "legal-marknote"))


class GoldquestKnowledgePlacementGateTests(unittest.TestCase):
    GOOD = """##### [测试·单选] 1.
{: custom-qb-id="q-1" custom-qb-answer="A" custom-qb-question-topic-ids="t"}
* 甲向乙交付货物,乙未付款.下列说法正确的是?
    - [ ] A. 乙应当付款
    - [ ] B. 乙无需付款
###### 答案与解析
- 正确答案：A。
{: custom-qb-section="solution"}
###### 逐项辨析
- ❌ B项 乙无需付款
    - **破绽**：交货后付款是双方约定的主给付义务，乙不履行即违约。
- ✅ A项 乙应当付款
    - **破题点**：乙未付款构成违约，甲有权请求继续履行。
"""

    def test_rejects_fixed_knowledge_map_section(self) -> None:
        separated = self.GOOD.replace(
            "###### 逐项辨析",
            "###### 规则地图\n- **主给付义务**：交货后付款。\n###### 逐项辨析",
        )
        self.assertIn("816", codes(separated, "legal-goldquest"))
        self.assertNotIn("816", codes(self.GOOD, "legal-goldquest"))

    def test_rejects_inline_knowledge_block_before_replays(self) -> None:
        separated = self.GOOD.replace(
            "###### 逐项辨析\n- ❌ B项",
            "###### 逐项辨析\n- 🧭 **设立路径**：交货后付款。\n    - **从约定取得**：合同生效即设立。\n- ❌ B项",
        )
        self.assertIn("816", codes(separated, "legal-goldquest"))

    def test_rejects_callout_that_restates_the_analysis(self) -> None:
        lazy = self.GOOD.replace(
            "\n{: custom-qb-section=\"solution\"}",
            "\n{: custom-qb-section=\"solution\"}\n> [!NOTE] 违约\n> 乙未付款构成违约，甲有权请求继续履行。",
        )
        self.assertIn("817", codes(lazy, "legal-goldquest"))
        good_callout = self.GOOD.replace(
            "\n{: custom-qb-section=\"solution\"}",
            "\n{: custom-qb-section=\"solution\"}\n> [!NOTE] 📚 法条\n> 民法典第579条：当事人一方未支付价款或报酬的，对方可以请求其支付。",
        )
        self.assertNotIn("817", codes(good_callout, "legal-goldquest"))

    def test_goldquest_rejects_generated_label_prefixes(self) -> None:
        labeled = """##### 1.
{: custom-qb-id="q-64" custom-qb-answer="A" custom-qb-question-topic-ids="t"}
* **题干**：甲向乙交付货物, 乙未付款.
* **问题**：下列哪一选项是正确的?
    - [ ] A. 乙应当付款
    - [ ] B. 乙无需付款
###### 答案与解析
- 正确答案：A。
{: custom-qb-section="solution"}
"""
        result = codes(labeled, "legal-goldquest")
        self.assertIn("647", result)
        plain = labeled.replace("* **题干**：甲向乙交付货物, 乙未付款.\n", "* 甲向乙交付货物, 乙未付款.\n").replace(
            "* **问题**：下列哪一选项是正确的?", "* 下列哪一选项是正确的?"
        )
        result = codes(plain, "legal-goldquest")
        self.assertNotIn("647", result)
        # Label variants behind emoji or bold, and on analysis lines, are rejected too.
        sneaky = plain.replace("* 甲向乙交付货物", "* 🔒 问题：甲向乙交付货物").replace(
            "- 正确答案：A。", "- 正确答案：A。\n- 解析：乙未付款无请求权。"
        )
        result = codes(sneaky, "legal-goldquest")
        self.assertIn("647", result)


class CliStrictModeTests(unittest.TestCase):
    WARN_ONLY = '- **现场笔录**{: style="color: var(--b3-font-color10);"}：1. 由执法人员和当事人签名。\n'

    def test_strict_is_the_default_even_without_the_flag(self) -> None:
        result = run_validator([], self.WARN_ONLY)
        self.assertEqual(result.returncode, 1)
        self.assertIn("507", result.stdout)

    def test_explicit_strict_flag_behaves_identically(self) -> None:
        result = run_validator(["--strict"], self.WARN_ONLY)
        self.assertEqual(result.returncode, 1)

    def test_relaxed_mode_requires_the_complete_relaxation_set(self) -> None:
        partial = run_validator(["--lenient"], self.WARN_ONLY)
        self.assertEqual(partial.returncode, 2)
        self.assertIn("--max-table-columns", partial.stderr)
        missing_rows = run_validator(["--lenient", "--max-table-columns", "3"], self.WARN_ONLY)
        self.assertEqual(missing_rows.returncode, 2)
        self.assertIn("--max-table-rows", missing_rows.stderr)

    def test_complete_relaxation_set_passes_warnings(self) -> None:
        result = run_validator(["--lenient", "--max-table-columns", "3", "--max-table-rows", "3"], self.WARN_ONLY)
        self.assertEqual(result.returncode, 0)
        self.assertIn("507", result.stdout)

    def test_strict_lenient_conflict_is_rejected(self) -> None:
        result = run_validator(["--strict", "--lenient", "--max-table-columns", "3", "--max-table-rows", "3"], self.WARN_ONLY)
        self.assertEqual(result.returncode, 2)


class MermaidSemanticsGateTests(unittest.TestCase):
    """Perfunctory Mermaid diagrams (E901 isolated pairs, E902 keyword chains) are hard failures."""

    def test_rejects_stacked_isolated_keyword_pairs(self) -> None:
        text = """> ```mermaid
> flowchart TD
>     A["申请信息公开"] --> B["行使权利=守法"]
>     C["环保局败诉"] --> D["承担法律责任=强制作用"]
>     E["起诉环保局"] --> F["公民监督=社会监督"]
>     G["诉权对象特定"] --> H["相对权利"]
> ```
"""
        self.assertIn("901", codes(text))

    def test_rejects_short_keyword_chain(self) -> None:
        text = """> ```mermaid
> flowchart TD
>     A["法律"] --> B["公序良俗"]
>     B --> C["权利"]
> ```
"""
        self.assertIn("902", codes(text))

    def test_accepts_clause_level_reasoning_chain(self) -> None:
        """A bare chain whose nodes are full propositions does analysis and stays legal."""
        text = """> ```mermaid
> flowchart TD
>     A["代位权成立"] --> B["相对人向债权人履行"]
>     B --> C["申腾公司是权利人"]
>     C --> D["由申腾公司申请执行"]
> ```
"""
        self.assertFalse({"901", "902"} & codes(text))

    def test_accepts_decision_tree_with_edge_labels_and_diamonds(self) -> None:
        text = """> ```mermaid
> flowchart TD
>     A["张某起诉"] --> B{"同一法律关系"}
>     B -->|"同一借款合同关系"| C["一个诉讼标的"]
>     B -->|"不同法律关系"| D["多个诉讼标的"]
> ```
"""
        self.assertFalse({"901", "902"} & codes(text))

    def test_accepts_semantic_classdef_skeleton(self) -> None:
        """Flashcard retrieval skeletons style roles with classDef; role styling is semantics."""
        text = """> ```mermaid
> flowchart LR
>     N[法律规范] --> P1[①]
>     F[法律事实] --> P2[②]
>     P1 --> R[③]
>     P2 --> R
>     classDef known fill:#e8f1ff,stroke:#2563eb;
>     classDef recall fill:#fff3bf,stroke:#d97706;
>     class N,F known;
>     class P1,P2,R recall;
> ```
"""
        self.assertFalse({"901", "902"} & codes(text))

    def test_single_edge_diagram_is_not_judged(self) -> None:
        text = """> ```mermaid
> flowchart TD
>     A["考点4 法律的作用"] --> B["规范作用"]
> ```
"""
        self.assertFalse({"901", "902"} & codes(text))


if __name__ == "__main__":
    unittest.main()
