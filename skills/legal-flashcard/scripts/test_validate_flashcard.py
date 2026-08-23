#!/usr/bin/env python3
import re
import unittest

from validate_flashcard import validate, validate_ordinary


VALID = """- 问题：**成立要件**{: style=\"color: var(--b3-font-color10);\"}是什么？
    - 答案：要件一。
{: custom-dm-source-key=\"civil-08\" custom-dm-card-id=\"fc-civil-elements-v1\" custom-dm-card-schema=\"1\" custom-dm-card-kind=\"basic\" custom-dm-card-renderer=\"list\" custom-qb-note-topic-id=\"civil-elements\"}
"""


class FlashcardValidatorTests(unittest.TestCase):
    def test_valid_dedicated_card(self):
        self.assertEqual(validate(VALID), [])

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
            '- 问题：**成立要件**{: style="color: var(--b3-font-color10);"}是什么？\n    - 答案：要件一。',
            '- **口诀**{: style="color: var(--b3-font-color12);"}：==三分法定、两步审查、先赔后补==\n    - 句一：==三==分法定\n    - 句二：==两==步审查\n    - 组合：==三两先==',
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

    def test_topic_reuse_and_report_reconciliation(self):
        cards = []
        for number in range(1, 6):
            cards.append(VALID.replace("fc-civil-elements-v1", f"fc-civil-elements-v{number}"))
        deck = "\n".join(cards) + "\n生成报告：候选 5；接受 5；拒绝 0。\n"
        self.assertIn("E013", {finding.code for finding in validate(deck, require_report=True)})
        self.assertNotIn("E032", {finding.code for finding in validate(deck, require_report=True)})
        self.assertIn("E032", {finding.code for finding in validate(deck.replace("接受 5", "接受 4"), require_report=True)})


if __name__ == "__main__":
    unittest.main()
