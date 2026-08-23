#!/usr/bin/env python3
import unittest

from validate_flashcard import validate, validate_ordinary


VALID = """- 问题：成立要件是什么？
    - 答案：要件一。
{: custom-dm-source-key=\"civil-08\"
   custom-dm-card-id=\"fc-civil-elements-v1\"
   custom-dm-card-schema=\"1\"
   custom-dm-card-kind=\"basic\"
   custom-dm-card-renderer=\"list\"
   custom-qb-question-topic-ids=\"civil-elements\"}
"""


class FlashcardValidatorTests(unittest.TestCase):
    def test_valid_dedicated_card(self):
        self.assertEqual(validate(VALID), [])

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
            "- 问题：成立要件是什么？\n    - 答案：要件一。",
            "- 口诀：==三两先==\n    - 句一：==三==分法定\n    - 句二：==两==步审查\n    - 组合：==三两先==",
        )
        self.assertEqual(validate(mnemonic), [])
        self.assertIn("E020", {finding.code for finding in validate(mnemonic.replace("==三两先==", "三两先"))})


if __name__ == "__main__":
    unittest.main()
