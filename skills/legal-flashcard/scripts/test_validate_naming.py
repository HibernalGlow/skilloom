#!/usr/bin/env python3
import tempfile
import unittest
from pathlib import Path

from validate_naming import validate


class NamingValidatorTests(unittest.TestCase):
    def write_pair(self, source_text: str, output_text: str) -> tuple[Path, Path, tempfile.TemporaryDirectory[str]]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        source_dir = root / "20-整理"
        output_dir = root / "30-闪卡"
        source_dir.mkdir()
        output_dir.mkdir()
        source = source_dir / "01-考点23-立法法.md"
        output = output_dir / "01-考点23-立法法-闪卡.md"
        source.write_text(source_text, encoding="utf-8")
        output.write_text(output_text, encoding="utf-8")
        return source, output, temporary

    def test_flash_marker_leads_source_heading(self):
        source, output, temporary = self.write_pair("# 考点23 立法法\n", "# ⚡01-考点23-立法法\n")
        self.addCleanup(temporary.cleanup)
        self.assertEqual(validate(output, source), [])

    def test_suffix_title_is_rejected(self):
        source, output, temporary = self.write_pair("# 考点23 立法法\n", "# 考点23 立法法 · 闪卡\n")
        self.addCleanup(temporary.cleanup)
        self.assertTrue(any("N005" in finding for finding in validate(output, source)))

    def test_existing_marker_is_not_duplicated(self):
        source, output, temporary = self.write_pair("# ⚡考点23 立法法\n", "# ⚡01-考点23-立法法\n")
        self.addCleanup(temporary.cleanup)
        self.assertEqual(validate(output, source), [])

    def test_headingless_source_uses_filename_fallback(self):
        source, output, temporary = self.write_pair("正文。\n", "# ⚡01-考点23-立法法\n")
        self.addCleanup(temporary.cleanup)
        self.assertEqual(validate(output, source), [])

    def test_output_filename_number_overrides_chinese_source_heading(self):
        source, output, temporary = self.write_pair(
            "# 专题三 民事权利能力、民事行为能力与自然人的监护\n",
            "# ⚡01-考点23-立法法\n",
        )
        self.addCleanup(temporary.cleanup)
        self.assertEqual(validate(output, source), [])

    def test_styled_h1_is_rejected_even_when_visible_text_matches(self):
        source, output, temporary = self.write_pair(
            "# 专题三 民事权利能力、民事行为能力与自然人的监护\n",
            '# ⚡01-**考点23**{: style="color: var(--b3-font-color10);"}-立法法\n',
        )
        self.addCleanup(temporary.cleanup)
        self.assertTrue(any("N005" in finding for finding in validate(output, source)))


if __name__ == "__main__":
    unittest.main()
