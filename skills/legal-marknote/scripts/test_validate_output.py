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

    def test_rejects_unbacked_merge_placeholder(self) -> None:
        text = """| 分类 | 期间 | 依据 | 细分 | 规则 |
| --- | --- | --- | --- | --- |
| {: rowspan='2'}分类 | 法定期间 | 法律明文规定的期间 | 绝对不可变期 | 不得变更 |
| {: class='fn__none'} | 指定期间 | {: class='fn__none'} | 相对不可变期 | 可以依法变更 |
"""

        findings = MODULE.validate_tables(text)

        self.assertIn("406", {finding.code for finding in findings})



if __name__ == "__main__":
    unittest.main()
