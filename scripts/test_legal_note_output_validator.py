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
            "| 内容 | **1. 主体**{: style=\"color: var(--b3-font-color10);\"}：==适格==。"
            "<br />**2. 后果**：_承担责任_。 |\n"
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
        text = "| 项目 | 1. 要件一 2. 要件二 |\n| 长文 | " + "普通说明。" * 24 + " |"
        self.assertTrue({"401", "402"} <= codes(text))

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

    def test_rejects_goldquest_answer_leak_and_checked_option(self) -> None:
        text = """##### 1题
* 题干含==正确答案==
    - [x] A. 选项
**成立**{: style=\"color: var(--b3-font-color8);\"}
"""
        self.assertTrue({"601", "603"} <= codes(text, "legal-goldquest"))

    def test_accepts_goldquest_question_answer_boundary(self) -> None:
        text = """##### 1题
{: custom-qb-id="civil-question-1" custom-qb-question-topic-ids="civil-topic"}
* **甲**{: style=\"color: var(--b3-font-color10);\"}实施某行为，如何判断？
    - [ ] A. 选项甲
    - [ ] B. 选项乙

###### 答案与解析

<div><style>b{background:#c9cdd3;color:transparent;border-radius:4px;padding:0 6px}b:hover{background:#fff2c2;color:#c0392b}</style>答案：<b>A</b></div>

**答案**为==选项甲==。
"""
        self.assertEqual(codes(text, "legal-goldquest"), set())

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
