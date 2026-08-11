#!/usr/bin/env python3
"""Regression tests for MarkNote fenced-question identity auditing."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("audit_question_groups.py")
SPEC = importlib.util.spec_from_file_location("audit_question_groups", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


SOURCE = """> ###### 习题
>
> ```md
> 37. 第一题
> 题干：共同事实。
> 问题：
> (1) 第一小问
> ```
>
> 37. 答案与解析。
>
> ```md
> 42. 第二题
> 问题：第二题问句？
> ```
>
> 42. 答案与解析。
"""


class FencedQuestionIdentityTests(unittest.TestCase):
    def audit_pair(self, output: str):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source_path = root / "source.md"
            output_path = root / "output.md"
            source_path.write_text(SOURCE, encoding="utf-8")
            output_path.write_text(output, encoding="utf-8")
            return MODULE.audit(output_path, source_path)

    def test_accepts_split_blocks_with_original_identifiers(self) -> None:
        errors, _ = self.audit_pair(SOURCE)
        self.assertFalse(any("identifiers changed" in error.message for error in errors))

    def test_rejects_renumbered_question_blocks(self) -> None:
        output = SOURCE.replace("> 37. 第一题", "> 1. 第一题").replace("> 42. 第二题", "> 2. 第二题")
        errors, _ = self.audit_pair(output)
        self.assertTrue(any("identifiers changed" in error.message for error in errors))

    def test_rejects_normalized_subquestion_marker(self) -> None:
        output = SOURCE.replace("> (1) 第一小问", "> 1. 第一小问")
        errors, _ = self.audit_pair(output)
        self.assertTrue(any("identifiers changed" in error.message for error in errors))

    def test_rejects_stem_and_multiple_subquestions_on_one_line(self) -> None:
        output = SOURCE.replace(
            "> 题干：共同事实。\n> 问题：\n> (1) 第一小问",
            "> 题干：共同事实。(1) 第一小问(2) 第二小问",
        )
        errors, _ = self.audit_pair(output)

        self.assertTrue(any("crowded onto one line" in error.message for error in errors))
        self.assertTrue(any("separate 题干： and 问题：" in error.message for error in errors))

    def test_accepts_labeled_stem_and_one_subquestion_per_line(self) -> None:
        output = SOURCE.replace(
            "> (1) 第一小问",
            "> (1) 第一小问\n> (2) 第二小问",
        )
        source = SOURCE.replace(
            "> 题干：共同事实。\n> 问题：\n> (1) 第一小问",
            "> 题干：共同事实。(1) 第一小问(2) 第二小问",
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source_path = root / "source.md"
            output_path = root / "output.md"
            source_path.write_text(source, encoding="utf-8")
            output_path.write_text(output, encoding="utf-8")
            errors, _ = MODULE.audit(output_path, source_path)

        self.assertFalse(any("identifiers changed" in error.message for error in errors))
        self.assertFalse(any("crowded onto one line" in error.message for error in errors))

    def test_accepts_one_exercise_label_for_multiple_question_fences(self) -> None:
        errors, _ = self.audit_pair(SOURCE)
        self.assertFalse(any("repeats the '###### 习题' label" in error.message for error in errors))

    def test_rejects_repeated_exercise_label_in_one_quote_group(self) -> None:
        output = SOURCE.replace(
            "> ```md\n> 42. 第二题",
            "> ###### 习题\n>\n> ```md\n> 42. 第二题",
        )
        errors, _ = self.audit_pair(output)
        self.assertTrue(any("repeats the '###### 习题' label" in error.message for error in errors))


if __name__ == "__main__":
    unittest.main()
