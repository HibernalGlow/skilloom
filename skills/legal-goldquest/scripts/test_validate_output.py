#!/usr/bin/env python3
"""Regression tests for legal-goldquest color and Callout density gates."""

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


MASK = "<div><style>b{background:#c9cdd3;color:transparent;border-radius:4px;padding:0 6px}b:hover{background:#fff2c2;color:#c0392b}</style>答案：<b>A</b></div>"


def codes(text: str) -> set[str]:
    return {finding.code for finding in MODULE.validate_goldquest(text)}


class GoldquestDensityValidationTests(unittest.TestCase):
    def test_rejects_three_uncolored_analysis_sentences(self) -> None:
        text = (
            f"##### 1.\n* 题干。\n###### 答案与解析\n{MASK}\n"
            "第一项规则应适用于本案。\n"
            "第二项规则需要审查主体资格。\n"
            "第三项规则最终决定法律后果。\n"
        )

        self.assertIn("609", codes(text))

    def test_accepts_color_anchor_every_one_or_two_sentences(self) -> None:
        text = (
            f"##### 1.\n* 题干。\n###### 答案与解析\n{MASK}\n"
            "**规则**{: style=\"color: var(--b3-font-color10);\"}适用于本案。\n"
            "因此应审查构成要件。\n"
            "**例外**{: style=\"color: var(--b3-font-color5);\"}不适用于该情形。\n"
            "故该选项错误。\n"
        )

        self.assertNotIn("609", codes(text))

    def test_rejects_plain_text_pseudo_callout(self) -> None:
        text = f"###### 答案与解析\n{MASK}\n📌[总结与归纳] 规则应结合例外理解。\n"

        self.assertIn("608", codes(text))

    def test_rejects_goldquest_table_over_three_by_three(self) -> None:
        text = (
            "| 项目 | 规则 | 后果 | 备注 |\n"
            "| --- | --- | --- | --- |\n"
            "| A | 规则 | 后果 | 备注 |\n"
        )
        self.assertIn("411", {finding.code for finding in MODULE.validate_text(text, "legal-goldquest")})

    def test_rejects_long_semantically_ungrouped_list(self) -> None:
        text = "\n".join(f"- 项目{i}" for i in range(1, 7))
        self.assertIn("610", {finding.code for finding in MODULE.validate_text(text, "legal-goldquest")})

    def test_accepts_div_wrapped_html_block(self) -> None:
        text = "> ```html\n> <div><span>说明</span></div>\n> ```\n"
        self.assertNotIn("306", {finding.code for finding in MODULE.validate_text(text, "legal-goldquest")})

    def test_rejects_unwrapped_html_block(self) -> None:
        text = "> ```html\n> <span>说明</span>\n> ```\n"
        self.assertIn("306", {finding.code for finding in MODULE.validate_text(text, "legal-goldquest")})


if __name__ == "__main__":
    unittest.main()
