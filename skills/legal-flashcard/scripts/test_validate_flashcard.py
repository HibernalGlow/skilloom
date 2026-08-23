#!/usr/bin/env python3
import re
import unittest

from validate_flashcard import validate, validate_ordinary


VALID = """- 问题：**成立要件**{: style=\"color: var(--b3-font-color10);\"}是什么？ #法考/民法/债法/成立要件# #闪卡/优先级/P1#
    - 答案：要件一。
{: custom-dm-source-key=\"civil-08\" custom-dm-card-id=\"fc-civil-elements-v1\" custom-dm-card-schema=\"1\" custom-dm-card-kind=\"basic\" custom-dm-card-renderer=\"list\" custom-qb-note-topic-id=\"civil-elements\"}
"""

SOURCE = """#### 成立要件
{: custom-qb-note-topic-id=\"civil-elements\"}

- **成立要件**{: style=\"color: var(--b3-font-color10);\"}
    - 要件一。

#### 法律效果
{: custom-qb-note-topic-id=\"civil-effects\"}

- **法律效果**{: style=\"color: var(--b3-font-color12);\"}
"""


class FlashcardValidatorTests(unittest.TestCase):
    def test_valid_dedicated_card(self):
        self.assertEqual(validate(VALID), [])

    def test_source_aware_style_inheritance(self):
        self.assertEqual(validate(VALID, source_text=SOURCE), [])
        recolored = VALID.replace("b3-font-color10", "b3-font-color12")
        self.assertIn("E039", {finding.code for finding in validate(recolored, source_text=SOURCE)})
        plain = VALID.replace('**成立要件**{: style="color: var(--b3-font-color10);"}', "成立要件")
        self.assertIn("E040", {finding.code for finding in validate(plain, source_text=SOURCE)})

    def test_source_style_must_come_from_matching_provider_range(self):
        wrong_topic_style = VALID.replace(
            '**成立要件**{: style="color: var(--b3-font-color10);"}',
            '**法律效果**{: style="color: var(--b3-font-color12);"}',
        )
        self.assertIn("E039", {finding.code for finding in validate(wrong_topic_style, source_text=SOURCE)})

    def test_source_styled_text_cannot_drop_its_style(self):
        source = SOURCE.replace(
            "    - 要件一。",
            '    - **要件一**{: style="color: var(--b3-font-color5);"}。',
        )
        self.assertIn("E041", {finding.code for finding in validate(VALID, source_text=source)})

    def test_plain_source_range_allows_plain_card(self):
        source = SOURCE.replace('**成立要件**{: style="color: var(--b3-font-color10);"}', "成立要件")
        plain = VALID.replace('**成立要件**{: style="color: var(--b3-font-color10);"}', "成立要件")
        codes = {finding.code for finding in validate(plain, source_text=source)}
        self.assertNotIn("E030", codes)
        self.assertNotIn("E040", codes)

    def test_rejects_multiline_ial_and_question_topic_field(self):
        malformed = VALID.replace(
            ' custom-dm-card-id="fc-civil-elements-v1"',
            '\n   custom-dm-card-id="fc-civil-elements-v1"',
        ).replace(
            'custom-qb-note-topic-id="civil-elements"',
            'custom-qb-question-topic-ids="civil-elements"',
        )
        codes = {finding.code for finding in validate(malformed)}
        self.assertIn("E022", codes)
        self.assertIn("E002", codes)
        self.assertIn("E003", codes)

    def test_duplicate_id_and_runtime_leakage(self):
        duplicated = VALID + "\n" + VALID.replace("fc-civil-elements-v1", "fc-civil-elements-v1")
        findings = validate(duplicated + "\ninterval=3")
        codes = {finding.code for finding in findings}
        self.assertIn("E005", codes)
        self.assertIn("E014", codes)

    def test_ordinary_mode_rejects_card_metadata(self):
        self.assertTrue(validate_ordinary("- 说明\ncustom-dm-card-id=\"bad\"\n"))
        self.assertEqual(validate_ordinary("- 说明\n#闪卡/优先级/P2#\n"), [])

    def test_mnemonic_card_requires_highlighted_mapping(self):
        mnemonic = VALID.replace(
            'custom-dm-card-id="fc-civil-elements-v1"',
            'custom-dm-card-id="fc-civil-mnemonic-v1"',
        ).replace(
            'custom-dm-card-kind="basic"',
            'custom-dm-card-kind="mnemonic"',
        ).replace(
            '- 问题：**成立要件**{: style="color: var(--b3-font-color10);"}是什么？ #法考/民法/债法/成立要件# #闪卡/优先级/P1#\n    - 答案：要件一。',
            '- **立法审查主体口诀**{: style="color: var(--b3-font-color12);"}：==三分法定、两步审查、先赔后补== #法考/民法/债法/成立要件# #闪卡/优先级/P1#\n    - 句一：==三==分法定\n    - 句二：==两==步审查\n    - 组合：==三两先==',
        )
        self.assertEqual(validate(mnemonic), [])
        unhighlighted = re.sub(r"==([^=]+)==", r"\1", mnemonic)
        self.assertIn("E020", {finding.code for finding in validate(unhighlighted)})

    def test_requires_marknote_anchor_and_short_non_mnemonic_highlight(self):
        no_style = VALID.replace('**成立要件**{: style="color: var(--b3-font-color10);"}', "成立要件")
        self.assertIn("E030", {finding.code for finding in validate(no_style)})
        long_cloze = VALID.replace('custom-dm-card-kind="basic"', 'custom-dm-card-kind="cloze"').replace(
            "要件一。", "==这是一个过长的完整结论句==。"
        )
        self.assertIn("E029", {finding.code for finding in validate(long_cloze)})

    def test_basic_question_does_not_use_highlight(self):
        highlighted = VALID.replace("成立要件**{: style", "成立==要件==**{: style")
        self.assertIn("E036", {finding.code for finding in validate(highlighted)})

    def test_mnemonic_is_a_cue_not_a_question(self):
        mnemonic = VALID.replace(
            'custom-dm-card-id="fc-civil-elements-v1"',
            'custom-dm-card-id="fc-civil-mnemonic-v1"',
        ).replace(
            'custom-dm-card-kind="basic"',
            'custom-dm-card-kind="mnemonic"',
        ).replace(
            '- 问题：**成立要件**{: style="color: var(--b3-font-color10);"}是什么？ #法考/民法/债法/成立要件# #闪卡/优先级/P1#\n    - 答案：要件一。',
            '- **立法审查主体口诀**{: style="color: var(--b3-font-color12);"}：==三分法定== #法考/民法/债法/成立要件# #闪卡/优先级/P1#\n    - 组合：==三分法定==',
        )
        self.assertEqual(validate(mnemonic), [])
        question_mnemonic = mnemonic.replace("- **立法审查主体口诀**", "- 问题：**立法审查主体口诀**")
        self.assertIn("E037", {finding.code for finding in validate(question_mnemonic)})
        bare_mnemonic = mnemonic.replace("立法审查主体口诀", "口诀")
        self.assertIn("E038", {finding.code for finding in validate(bare_mnemonic)})

    def test_requires_knowledge_tag_and_valid_priority_namespace(self):
        missing = VALID.replace(" #法考/民法/债法/成立要件# #闪卡/优先级/P1#", "")
        self.assertIn("E033", {finding.code for finding in validate(missing)})
        generic = VALID.replace("#法考/民法/债法/成立要件#", "#立法程序#")
        self.assertNotIn("E033", {finding.code for finding in validate(generic)})
        no_priority = VALID.replace(" #闪卡/优先级/P1#", "")
        self.assertIn("E035", {finding.code for finding in validate(no_priority)})
        invalid = VALID.replace("#闪卡/优先级/P1#", "#闪卡/P1#")
        self.assertIn("E034", {finding.code for finding in validate(invalid)})

    def test_topic_reuse_and_report_reconciliation(self):
        cards = []
        for number in range(1, 6):
            cards.append(VALID.replace("fc-civil-elements-v1", f"fc-civil-elements-v{number}"))
        deck = "\n".join(cards) + "\n生成报告：候选 5；接受 5；拒绝 0。\n原笔记：[[民法/成立要件]] · 协议：DAMO 闪卡 schema 1\n"
        self.assertIn("E013", {finding.code for finding in validate(deck, require_report=True)})
        self.assertNotIn("E032", {finding.code for finding in validate(deck, require_report=True)})
        self.assertIn("E032", {finding.code for finding in validate(deck.replace("接受 5", "接受 4"), require_report=True)})

    def test_rejects_internal_audit_preamble(self):
        preamble = """- 源笔记：[[20-整理/考点25]]
- 协议：DAMO schema 1
- 标签：取自源笔记
- 构成：1 张 = basic 1
- 着色图例：color10＝主体
- 章节：沿用源笔记
- 样式继承：逐字复用
- 源笔记说明：残留单字挖空
- 高亮职责：basic 不挖空

"""
        findings = validate(preamble + VALID)
        self.assertEqual(sum(finding.code == "E042" for finding in findings), 9)

    def test_requires_one_final_source_protocol_line(self):
        report = "生成报告：候选 1；接受 1；拒绝 0。\n"
        footer = "原笔记：[[民法/成立要件]] · 协议：DAMO 闪卡 schema 1\n"
        self.assertNotIn("E043", {finding.code for finding in validate(VALID + report + footer, require_report=True)})
        self.assertIn("E043", {finding.code for finding in validate(VALID + report, require_report=True)})
        misplaced = footer + VALID + report
        self.assertIn("E043", {finding.code for finding in validate(misplaced, require_report=True)})


if __name__ == "__main__":
    unittest.main()
