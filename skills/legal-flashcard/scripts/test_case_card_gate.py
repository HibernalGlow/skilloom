#!/usr/bin/env python3
import unittest

from case_card_gate import check

CARD = """- ⚖️ 题干？ #法考/民诉/调解# #闪卡/优先级/P1#

  > [!SELECTION]
  >
  > - [ ] A. 甲项
  > - [ ] B. 乙项

    - 正确答案：A。
    - ✅ 甲项可代为
      - 判断链：

        ```mermaid
        flowchart LR
            A["甲"] --> B{"阶段"}
            N["误判入口：外推"]:::wrong --> B
        ```

        ```yml
        cc:
          schema: cc-1
          tier: flame
          variant: "none"
          verified: "遮答案重做一致"
        ```
{: custom-dm-source-key="cp-x" custom-dm-card-id="fc-cp-x-v1" custom-dm-card-schema="1" custom-dm-card-kind="basic" custom-dm-card-renderer="list" custom-qb-note-topic-id="cp-topic"}
"""


SOURCE = """##### 1.
{: custom-qb-id="q1" custom-qb-type="single" custom-qb-answer="A"}

* 丙公司诉乙公司货款纠纷。
* 下列哪一选项正确？
    - [ ] A. 调解协议内容尽管超出了当事人诉讼请求，但仍具有合法性
    - [ ] B. 丙公司反悔拒绝签收调解书，法院可以采取留置送达
    - [ ] D. 因丙公司反悔，法院应当及时作出判决
"""

VARIANT_CARD = """- ⚖️ 题干？ #法考/民诉/调解# #闪卡/优先级/P1#

  > [!SELECTION]
  >
  > - [ ] A. 调解协议内容尽管超出了当事人诉讼请求，但仍具有合法性
  > - [ ] B. 担保人反悔拒绝签收调解书，法院可以采取留置送达
  > - [ ] D. 因担保人反悔，法院应当及时作出判决

    - 正确答案：A。
    - ✅ 甲项可代为
      - 判断链：

        ```yml
        cc:
          schema: cc-1
          source_qb_id: q1
          roles: "丙公司→担保人"
          variant: "none"
          verified: "遮答案重做一致"
        ```
{: custom-dm-source-key="cp-y" custom-dm-card-id="fc-cp-y-v1" custom-dm-card-schema="1" custom-dm-card-kind="basic" custom-dm-card-renderer="list" custom-qb-note-topic-id="cp-topic"}
"""


def codes_of(text: str, source: str | None = None) -> set[str]:
    return {code for _line, code, _message in check(text, source)}


class CaseCardOptionDriftTests(unittest.TestCase):
    """E139: a re-skinned stem is fine, a touched option is not."""

    def test_role_neutralised_option_is_not_drift(self):
        self.assertNotIn("E139", codes_of(VARIANT_CARD, SOURCE))

    def test_modal_word_change_is_drift(self):
        broken = VARIANT_CARD.replace("法院可以采取留置送达", "法院应当采取留置送达")
        self.assertIn("E139", codes_of(broken, SOURCE))

    def test_rewritten_option_is_drift(self):
        broken = VARIANT_CARD.replace("A. 调解协议内容尽管超出了当事人诉讼请求，但仍具有合法性",
                                      "A. 调解协议完全合法")
        self.assertIn("E139", codes_of(broken, SOURCE))

    def test_missing_options_are_reported(self):
        self.assertIn("E139", codes_of(VARIANT_CARD, SOURCE + "    - [ ] C. 另有一项\n"))




class CaseCardGateTests(unittest.TestCase):
    """cc-1 gates: styled answer markers, missing carriers, and content that leaks to the front."""

    def test_well_formed_card_is_clean(self):
        self.assertEqual(check(CARD), [])

    def test_variant_and_verified_keys_are_required(self):
        broken = CARD.replace('          variant: "none"\n          verified: "遮答案重做一致"\n', "")
        self.assertIn("E137", codes_of(broken))

    def test_styled_answer_marker_loses_the_solution_boundary(self):
        broken = CARD.replace(
            "    - 正确答案：A。",
            "    - **正确**{: style=\"color: var(--b3-font-color8);\"}答案：A。",
        )
        self.assertIn("E136", codes_of(broken))

    def test_case_card_without_option_carrier_is_flagged(self):
        broken = CARD.replace(
            "  > [!SELECTION]\n  >\n  > - [ ] A. 甲项\n  > - [ ] B. 乙项\n",
            "    - [ ] A. 甲项\n    - [ ] B. 乙项\n",
        )
        self.assertIn("E137", codes_of(broken))

    def test_carrier_without_case_identity_block_is_flagged(self):
        broken = CARD.replace("        cc:\n", "")
        self.assertIn("E137", codes_of(broken))

    def test_fence_at_the_root_column_leaks_to_the_front(self):
        broken = CARD.replace("        ```yml", "  ```yml")
        self.assertIn("E138", codes_of(broken))

    def test_image_at_the_root_column_leaks_to_the_front(self):
        broken = CARD.replace("        ```yml",
                              "  ![动图：泄漏](https://example.invalid/a.avif)\n\n        ```yml")
        self.assertIn("E138", codes_of(broken))


FOCUS_INDEX = {"民诉": [["结案与仲裁/仲裁程序", "仲裁程序"], ["涉外/送达", "涉外基本原则"]]}


class CaseCardFocusTagTests(unittest.TestCase):
    """E140: a same-subject 考前聚焦 考点 discussed anywhere on the card must be tagged."""

    TEXT = VARIANT_CARD.replace(
        "    - 正确答案：A。",
        "    - 正确答案：A。" + chr(10) + "    - ✅ 仲裁程序里也适用同一判据",
    )

    def test_mentioned_focus_topic_without_tag_is_flagged(self):
        self.assertTrue([f for f in check(self.TEXT, None, FOCUS_INDEX) if f[1] == "E140"])

    def test_tag_on_the_front_satisfies_the_gate(self):
        tagged = self.TEXT.replace("#闪卡/优先级/P1#", "#考前聚焦/民诉/仲裁程序# #闪卡/优先级/P1#")
        self.assertFalse([f for f in check(tagged, None, FOCUS_INDEX) if f[1] == "E140"])

    def test_name_only_inside_a_fence_does_not_count(self):
        quoted = VARIANT_CARD.replace('variant: "none"', 'variant: "none 仲裁程序"')
        self.assertFalse([f for f in check(quoted, None, FOCUS_INDEX) if f[1] == "E140"])


if __name__ == "__main__":
    unittest.main()
