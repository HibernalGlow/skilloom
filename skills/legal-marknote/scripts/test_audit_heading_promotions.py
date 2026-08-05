from __future__ import annotations

import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))

from audit_heading_promotions import audit_heading_promotions  # noqa: E402


def codes(source: str, output: str, minimum_added_level: int = 4) -> set[str]:
    return {
        finding.code
        for finding in audit_heading_promotions(
            source,
            output,
            minimum_added_level=minimum_added_level,
        )
    }


class HeadingPromotionAuditTests(unittest.TestCase):
    def test_accepts_lower_level_promotions_and_preserves_source_headings(self) -> None:
        source = """# 民事诉讼
## 既判力
### 深度拓展
[深度拓展一] **既判力**

**概念**
| 项目 | 具体规定 |
| --- | --- |
| 概念 | 禁止再诉 |
"""
        output = """# 民事诉讼
## 既判力
### 深度拓展
#### [深度拓展一] **既判力**
##### **概念**
| 项目 | 具体规定 |
| --- | --- |
| 概念 | 禁止再诉 |
"""
        self.assertEqual(codes(source, output), set())

    def test_rejects_removed_or_releveled_original_heading(self) -> None:
        source = "# 民事诉讼\n## 既判力\n### 概念\n"
        output = "# 民事诉讼\n### 既判力\n#### 概念\n"
        self.assertTrue({"701", "703", "702"} <= codes(source, output))

    def test_rejects_new_high_level_heading(self) -> None:
        source = "# 民事诉讼\n## 既判力\n"
        output = "# 民事诉讼\n## 既判力\n### 新增大标题\n"
        self.assertIn("702", codes(source, output))

    def test_ignores_headings_inside_code_fences_and_quotes(self) -> None:
        source = "# 民事诉讼\n````md\n# 示例\n````\n> ## 引用标题\n"
        output = "# 民事诉讼\n````md\n#### 示例\n````\n> #### 引用标题\n"
        self.assertEqual(codes(source, output), set())

    def test_reports_promoted_heading_without_parent(self) -> None:
        source = "普通正文\n"
        output = "#### [深度拓展一] **既判力**\n"
        self.assertIn("704", codes(source, output))


if __name__ == "__main__":
    unittest.main()
