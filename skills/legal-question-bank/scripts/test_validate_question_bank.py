#!/usr/bin/env python3
"""Regression tests for the portable question/topic IAL contract."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("validate_question_bank.py")
SPEC = importlib.util.spec_from_file_location("validate_question_bank", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def codes(text: str) -> set[str]:
    return {finding.code for finding in MODULE.validate(text)}


class QuestionTopicContractTests(unittest.TestCase):
    def test_accepts_question_references_and_note_provider(self) -> None:
        text = """### 善意取得
{: custom-qb-note-topic-id="civil-property-good-faith-acquisition"}

##### 1.
{: custom-qb-id="civil-question-1" custom-qb-question-topic-ids="civil-property-good-faith-acquisition,civil-property-registration" custom-qb-type="subjective"}

题干。

参考答案。
{: custom-qb-section="solution"}
"""

        self.assertEqual(set(), codes(text))

    def test_rejects_missing_duplicate_and_legacy_question_topics(self) -> None:
        missing = """##### 1.
{: custom-qb-id="civil-question-1" custom-qb-type="subjective"}
题干。
答案。
{: custom-qb-section="solution"}
"""
        duplicate = missing.replace(
            'custom-qb-type="subjective"',
            'custom-qb-question-topic-ids="civil-topic,civil-topic" custom-qb-type="subjective"',
        )
        legacy = missing.replace(
            'custom-qb-type="subjective"',
            'custom-qb-topic-ids="civil-topic" custom-qb-type="subjective"',
        )

        self.assertIn("116", codes(missing))
        self.assertIn("117", codes(duplicate))
        self.assertIn("112", codes(legacy))

    def test_rejects_mixed_provider_and_question_identity(self) -> None:
        text = """##### 1.
{: custom-qb-id="civil-question-1" custom-qb-question-topic-ids="civil-topic" custom-qb-note-topic-id="civil-topic" custom-qb-type="subjective"}
题干。
答案。
{: custom-qb-section="solution"}
"""

        result = codes(text)
        self.assertIn("118", result)
        self.assertIn("121", result)


if __name__ == "__main__":
    unittest.main()
