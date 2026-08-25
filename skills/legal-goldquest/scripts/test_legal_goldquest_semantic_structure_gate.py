#!/usr/bin/env python3
"""Regression tests for content-bearing GoldQuest reasoning structures."""

from __future__ import annotations

import unittest

from legal_goldquest_semantic_structure_gate import validate_semantic_structure


def codes(text: str, *, medium: bool = True, complex_reasoning: bool = False) -> set[str]:
    return {
        finding.code
        for finding in validate_semantic_structure(
            text.splitlines(),
            1,
            medium_complexity=medium,
            complex_reasoning=complex_reasoning,
        )
    }


class SemanticStructureGateTests(unittest.TestCase):
    def test_rejects_option_result_mermaid(self) -> None:
        text = """> ```mermaid
> flowchart TD
> Q["题干"] --> D{"逐项判断"}
> D -->|A| A["排除"]
> D -->|B| B["正确"]
> ```
"""

        self.assertIn("639", codes(text, medium=False))

    def test_accepts_mermaid_grounded_in_legal_reasoning(self) -> None:
        text = """- **审查链**：先确认资格欠缺，再定位已经受理，最终裁定驳回起诉。
> ```mermaid
> flowchart LR
> A["资格欠缺"] --> B["已经受理"] --> C["驳回起诉"]
> ```
"""

        self.assertNotIn("639", codes(text, medium=False))
        self.assertNotIn("645", codes(text, medium=False, complex_reasoning=True))

    def test_requires_substantive_callout_for_medium_analysis(self) -> None:
        text = """- **条件**：已经受理。
    - **后果**：驳回起诉。
"""

        self.assertIn("640", codes(text))

    def test_rejects_boilerplate_callout(self) -> None:
        text = """> [!CAUTION] 陷阱
> - 偷换概念或以偏概全常为错误项，须回到题干限定并回放原文。
"""

        result = codes(text)
        self.assertIn("643", result)
        self.assertIn("640", result)

    def test_accepts_rule_bearing_callout(self) -> None:
        text = """> [!IMPORTANT] 责任归属
> - **医院**{: style="color: var(--b3-font-color11);"}承担替代责任；有重大过失时，才可以向医生追偿。
"""

        self.assertNotIn("640", codes(text))
        self.assertNotIn("643", codes(text))

    def test_rejects_punctuation_fragment_and_mechanical_label(self) -> None:
        text = """- 推理环节2：
    - 财团法人的本质是财产集合，
    - 因此没有意思机关。
"""

        result = codes(text, medium=False)
        self.assertIn("641", result)
        self.assertIn("642", result)

    def test_rejects_deferred_comprehensive_reasoning(self) -> None:
        text = """###### 逐项辨析
- ❌ A. 错误选项。
###### 综合推理
- 这里才给出真正理由。
"""

        self.assertIn("644", codes(text, medium=False))

    def test_complex_reasoning_requires_mermaid(self) -> None:
        text = """> [!NOTE] 法律效果
> - **规则**{: style="color: var(--b3-font-color10);"}适用于本案，因此由法人承担责任。
"""

        self.assertIn("645", codes(text, complex_reasoning=True))


if __name__ == "__main__":
    unittest.main()
