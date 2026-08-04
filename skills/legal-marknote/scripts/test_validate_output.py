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


if __name__ == "__main__":
    unittest.main()
