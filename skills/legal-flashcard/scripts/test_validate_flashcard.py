#!/usr/bin/env python3
import re
import unittest

from validate_flashcard import has_blocking_findings, validate, validate_ordinary


VALID = """- **成立要件**{: style=\"color: var(--b3-font-color10);\"}是什么？ #法考/民法/债法/成立要件# #闪卡/优先级/P1#
    - 要件一。
        - **适用边界**{: style=\"background-color: var(--b3-font-background11);\"}明确。
{: custom-dm-source-key=\"civil-08\" custom-dm-card-id=\"fc-civil-elements-v1\" custom-dm-card-schema=\"1\" custom-dm-card-kind=\"basic\" custom-dm-card-renderer=\"list\" custom-qb-note-topic-id=\"civil-elements\"}
"""

SOURCE = """#### 成立要件
{: custom-qb-note-topic-id=\"civil-elements\"}

- **成立要件**{: style=\"color: var(--b3-font-color10);\"}
    - 要件一。
        - **适用边界**{: style=\"background-color: var(--b3-font-background11);\"}明确。

#### 法律效果
{: custom-qb-note-topic-id=\"civil-effects\"}

- **法律效果**{: style=\"color: var(--b3-font-color12);\"}
"""


class FlashcardValidatorTests(unittest.TestCase):
    def test_valid_dedicated_card(self):
        self.assertEqual(validate(VALID), [])

    def test_rejects_generated_question_and_answer_prefixes(self):
        prefixed = VALID.replace("- **成立要件**", "- 问题：**成立要件**").replace(
            "    - 要件一。", "    - 答案：要件一。"
        )
        self.assertIn("E044", {finding.code for finding in validate(prefixed)})

    def test_basic_front_requires_question_mark(self):
        declarative = VALID.replace("是什么？ #法考", "的规则 #法考")
        self.assertIn("E025", {finding.code for finding in validate(declarative)})

    def test_complex_basic_back_requires_semantic_child_level(self):
        flat = VALID.replace(
            '        - **适用边界**{: style="background-color: var(--b3-font-background11);"}明确。\n',
            "",
        ).replace(
            "    - 要件一。",
            "    - 不同法律规范从不同角度对社会关系加以调整，并形成规范适用范围的交叉。\n"
            "    - 法律规范具有抽象性，社会关系具有复杂性，二者共同造成调整范围重合。\n"
            "    - 一个行为可能同时触犯不同法律规范，因而面临数种相互冲突的法律责任。",
        )
        self.assertIn("E046", {finding.code for finding in validate(flat)})
        nested = flat.replace(
            "    - 法律规范具有抽象性",
            "        - 法律规范具有抽象性",
        ).replace(
            "    - 一个行为可能同时触犯",
            "        - 一个行为可能同时触犯",
        )
        self.assertNotIn("E046", {finding.code for finding in validate(nested)})

    def test_explicit_closed_set_may_remain_flat(self):
        closed = VALID.replace("成立要件", "三项成立要件").replace(
            "    - 要件一。",
            "    - 要件一。\n    - 要件二。\n    - 要件三。",
        )
        self.assertNotIn("E046", {finding.code for finding in validate(closed)})

    def test_style_diversity_error_and_nonblocking_balance_warning(self):
        one_style = VALID.replace(
            '        - **适用边界**{: style="background-color: var(--b3-font-background11);"}明确。\n',
            "",
        )
        findings = validate(one_style)
        codes = {finding.code for finding in findings}
        self.assertIn("E047", codes)
        self.assertIn("W101", codes)
        self.assertTrue(has_blocking_findings(findings))

        foreground_only = VALID.replace("background-color: var(--b3-font-background11)", "color: var(--b3-font-color12)")
        findings = validate(foreground_only)
        codes = {finding.code for finding in findings}
        self.assertNotIn("E047", codes)
        self.assertIn("W101", codes)
        self.assertFalse(has_blocking_findings(findings))

        reordered_same_signature = VALID.replace(
            '**成立要件**{: style="color: var(--b3-font-color10);"}',
            '**成立要件**{: style="color: var(--b3-font-color10); background-color: var(--b3-font-background11);"}',
        ).replace(
            '**适用边界**{: style="background-color: var(--b3-font-background11);"}',
            '**适用边界**{: style="background-color: var(--b3-font-background11); color: var(--b3-font-color10);"}',
        )
        self.assertIn("E047", {finding.code for finding in validate(reordered_same_signature)})

        basic_reading_highlight = one_style.replace("要件一。", "要件一：==法定==。")
        basic_codes = {finding.code for finding in validate(basic_reading_highlight)}
        self.assertIn("E047", basic_codes)
        self.assertIn("W101", basic_codes)

    def test_rich_style_plan_allows_generated_foreground_role_anchor(self):
        generated = VALID.replace(
            '**成立要件**{: style="color: var(--b3-font-color10);"}',
            '**成立要件**{: style="color: var(--b3-font-color6);"}',
        )
        findings = validate(generated, source_text=SOURCE, rich_style=True)
        self.assertNotIn("E039", {finding.code for finding in findings})

    def test_rich_style_requires_recurring_subject_coverage(self):
        sparse_subject = VALID.replace(
            "    - 要件一。",
            "    - **债权人**{: style=\"color: var(--b3-font-color10);\"}与债务人发生关系，并决定规则适用边界。\n"
            "    - 债权人可以主张权利，并要求债务人履行义务。\n"
            "    - 债权人还可以依法采取程序措施。",
        )
        codes = {finding.code for finding in validate(sparse_subject, rich_style=True)}
        self.assertIn("E076", codes)

    def test_mark_highlight_counts_as_background_style_dimension(self):
        cloze = VALID.replace(
            '        - **适用边界**{: style="background-color: var(--b3-font-background11);"}明确。\n',
            "",
        ).replace("要件一。", "要件一：==法定==。").replace(
            'custom-dm-card-kind="basic"', 'custom-dm-card-kind="cloze"'
        ).replace('custom-dm-card-renderer="list"', 'custom-dm-card-renderer="mark"')
        codes = {finding.code for finding in validate(cloze)}
        self.assertNotIn("E047", codes)
        self.assertNotIn("W101", codes)

    def test_ordered_answers_and_advanced_back_content_stay_inside_root(self):
        ordered = VALID.replace(
            "    - 要件一。",
            "    1. 第一步。\n    2. 第二步。",
        )
        ordered_codes = {finding.code for finding in validate(ordered)}
        self.assertNotIn("E026", ordered_codes)
        self.assertIn("W103", ordered_codes)
        self.assertIn("W106", {finding.code for finding in validate(ordered, source_text=SOURCE)})
        ordered_source = SOURCE.replace("    - 要件一。", "    - 要件一。\n    - 依次执行。")
        self.assertNotIn("W106", {finding.code for finding in validate(ordered, source_text=ordered_source)})
        advanced = VALID.replace(
            "    - 要件一。",
            "    - 对应关系：\n"
            "        | 主体 | 规则 |\n"
            "        | --- | --- |\n"
            "        | 甲 | 规则一 |\n"
            "        | 乙 | 规则二 |\n"
            "        ```mermaid\n"
            "        flowchart LR\n"
            "            A[规则一] --> B[规则二]\n"
            "        ```",
        )
        codes = {finding.code for finding in validate(advanced)}
        self.assertNotIn("E008", codes)
        self.assertNotIn("E026", codes)
        self.assertIn("W104", codes)
        self.assertIn("W105", codes)

    def test_question_side_mermaid_is_supported_only_before_answer_list(self):
        visual = VALID.replace(
            "    - 要件一。",
            "    ```mermaid\n"
            "    flowchart LR\n"
            "        A[规范] --> B[①]\n"
            "        classDef known fill:#e8f1ff,stroke:#2563eb;\n"
            "        classDef recall fill:#fff3bf,stroke:#d97706,stroke-dasharray:5 3;\n"
            "        class A known;\n"
            "        class B recall;\n"
            "    ```\n"
            "    - 要件一。",
        )
        self.assertNotIn("E049", {finding.code for finding in validate(visual)})
        self.assertNotIn("E048", {finding.code for finding in validate(visual)})

    def test_mermaid_without_type_is_blocking(self):
        invalid = VALID.replace(
            "    - 要件一。",
            "    ```mermaid\n    dcd\n    ```\n    - 要件一.",
        )
        self.assertIn("E048", {finding.code for finding in validate(invalid)})

    def test_question_side_mermaid_without_recall_slot_warns(self):
        no_slot = VALID.replace(
            "    - 要件一。",
            "    ```mermaid\n"
            "    flowchart LR\n"
            "        A[规范] --> B[事实]\n"
            "        classDef known fill:#e8f1ff;\n"
            "        class A,B known;\n"
            "    ```\n"
            "    - 要件一。",
        )
        self.assertIn("W108", {finding.code for finding in validate(no_slot)})

    def test_rich_style_mode_raises_goldquest_level_gates(self):
        deck = "\n## 共同诉讼关系\n\n" + "\n---\n\n".join(
            VALID.replace("fc-civil-elements-v1", f"fc-civil-elements-v{number}")
            .replace('background-color: var(--b3-font-background11);', 'color: var(--b3-font-color12);')
            for number in range(1, 4)
        )
        codes = {finding.code for finding in validate(deck, rich_style=True)}
        self.assertIn("E060", codes)
        self.assertIn("E061", codes)
        self.assertIn("E062", codes)
        self.assertIn("E063", codes)

    def test_rich_style_mode_accepts_goldquest_level_example(self):
        rich = """# ⚡专题六 共同诉讼

## 制度区分

- **共同诉讼**{: style="color: var(--b3-font-color10);"}的两类基本形态如何区分？ #法考/民诉/共同诉讼/制度区分# #闪卡/优先级/P1#
    - **必要共同诉讼**{: style="color: var(--b3-font-color10);"}：诉讼标的是**共同**{: style="background-color: var(--b3-font-background11);"}的。
        - 处理结果：<em>合一审理、合一判决</em>，最终**统一裁判**{: style="color: var(--b3-font-color8);"}。
    - **普通共同诉讼**{: style="color: var(--b3-font-color12);"}：诉讼标的是<u>同一种类</u>的。
        - 审理方式：可以`合并审理`，也可以**分开审理**{: style="color: var(--b3-font-color9);"}。
        | 制度 | 标的关系 |
        | --- | --- |
        | 必要 | 共同 |
        | 普通 | 同一种类 |
{: custom-dm-source-key="example-rich" custom-dm-card-id="fc-example-rich-basic-v1" custom-dm-card-schema="1" custom-dm-card-kind="basic" custom-dm-card-renderer="list" custom-qb-note-topic-id="example-rich-distinction"}

---

## 代表人诉讼步骤

- 人数不确定的代表人诉讼启动步骤是什么？ #法考/民诉/共同诉讼/代表人诉讼/人数不确定# #闪卡/优先级/P1#
    - 程序步骤：
        1. **公告**{: style="color: var(--b3-font-color12); background-color: var(--b3-font-background12);"}案件情况。
        2. **登记**{: style="color: var(--b3-font-color13); background-color: var(--b3-font-background13);"}权利人。
        3. **推选或商定**{: style="color: var(--b3-font-color8);"}代表人。
        ```mermaid
        flowchart LR
            A[人数尚未确定] --> B[公告]
            B --> C[登记]
            C --> D[推选或商定]
            classDef known fill:#e8f1ff,stroke:#3b6ea8,color:#222;
            classDef answer fill:#e8f5e9,stroke:#4d8b57,color:#222;
            class A known;
            class B,C,D answer;
        ```
    > [!IMPORTANT] 核心边界
    > - <em>起诉时</em>**人数尚未确定**{: style="color: var(--b3-font-color12);"}。
    > - ~~跳过公告、登记直接裁判~~不是**启动方式**{: style="color: var(--b3-font-color13);"}。
{: custom-dm-source-key="example-rich" custom-dm-card-id="fc-example-rich-process-v1" custom-dm-card-schema="1" custom-dm-card-kind="basic" custom-dm-card-renderer="list" custom-qb-note-topic-id="example-rich-process"}

## 区分口诀

- **区分口诀**{: style="color: var(--b3-font-color6);"}：==必要共标的，普通同种类；确定全体推，不定公告登。== #法考/民诉/共同诉讼/区分口诀# #闪卡/优先级/P1#
    - ==必要共标的==：诉讼标的是**共同**{: style="background-color: var(--b3-font-background11);"}的。
    - ==普通同种类==：诉讼标的是<u>同一种类</u>的。
    - ==确定全体推==：全体**当事人**{: style="color: var(--b3-font-color10);"}**推选代表人**{: style="color: var(--b3-font-color12);"}。
    - ==不定公告登==：公告、登记后**推选或商定**{: style="background-color: var(--b3-font-background13);"}代表人。
{: custom-dm-source-key="example-rich" custom-dm-card-id="fc-example-rich-mnemonic-v1" custom-dm-card-schema="1" custom-dm-card-kind="mnemonic" custom-dm-card-renderer="list" custom-qb-note-topic-id="example-rich-mnemonic"}

```yaml
report:
  candidates: 3
  accepted: 3
  rejected: 0
  rejection_reasons: {}
source:
  note: "示例/专题六 共同诉讼"
  protocol: "DAMO 闪卡 schema 1"
```
"""
        findings = validate(rich, require_report=True, rich_style=True)
        self.assertFalse([finding for finding in findings if not finding.code.startswith("W")])

    def test_rich_style_rejects_long_or_punctuated_color_anchor(self):
        long_anchor = VALID.replace("成立要件", "这是一个超过八字的锚点")
        self.assertIn("E064", {finding.code for finding in validate(long_anchor, rich_style=True)})
        punctuated = VALID.replace("**成立要件**", "**成立要件：**")
        self.assertIn("E065", {finding.code for finding in validate(punctuated, rich_style=True)})

    def test_rich_style_requires_background_augmentation_for_sparse_palette(self):
        deck = "\n".join(
            VALID.replace("fc-civil-elements-v1", f"fc-civil-sparse-v{number}")
            for number in range(1, 4)
        )
        self.assertIn("E066", {finding.code for finding in validate(deck, rich_style=True)})

    def test_rich_style_surfaces_sparse_complex_card_without_penalizing_short_definition(self):
        short_codes = {finding.code for finding in validate(VALID, rich_style=True)}
        self.assertNotIn("W110", short_codes)
        complex_card = VALID.replace(
            "    - 要件一。\n",
            "    - 第一项规则适用于一般情形并形成统一适用边界。\n"
            "    - 第二项规则处理例外情形并限制法律效果。\n"
            "    - 第三项规则说明法律后果及其程序影响。\n",
        )
        codes = {finding.code for finding in validate(complex_card, rich_style=True)}
        self.assertIn("W110", codes)
        self.assertIn("W117", codes)
        self.assertIn("E074", codes)

    def test_borderline_flat_back_gets_advisory(self):
        borderline = VALID.replace(
            "    - 要件一。\n"
            '        - **适用边界**{: style="background-color: var(--b3-font-background11);"}明确。',
            "    - 不同法律规范分别调整同一社会关系，可能形成适用范围交叉。\n"
            '    - **适用边界**{: style="background-color: var(--b3-font-background11);"}需要结合规范对象判断。',
        )
        codes = {finding.code for finding in validate(borderline)}
        self.assertIn("W102", codes)
        self.assertNotIn("E046", codes)

    def test_duplicate_summary_gets_advisory(self):
        summary = VALID.replace(
            "    - 要件一。\n"
            '        - **适用边界**{: style="background-color: var(--b3-font-background11);"}明确。',
            "    - 规则甲。\n"
            '    - **规则乙**{: style="background-color: var(--b3-font-background11);"}。',
        ).replace("fc-civil-elements-v1", "fc-civil-summary-v1")
        detail_a = VALID.replace("要件一", "规则甲").replace(
            "fc-civil-elements-v1", "fc-civil-rule-a-v1"
        )
        detail_b = VALID.replace("要件一", "规则乙").replace(
            "fc-civil-elements-v1", "fc-civil-rule-b-v1"
        )
        codes = {finding.code for finding in validate("\n".join((summary, detail_a, detail_b)))}
        self.assertIn("W107", codes)

    def test_source_aware_style_inheritance(self):
        self.assertEqual(validate(VALID, source_text=SOURCE), [])
        recolored = VALID.replace("b3-font-color10", "b3-font-color12")
        self.assertIn("E039", {finding.code for finding in validate(recolored, source_text=SOURCE)})
        plain = VALID.replace('**成立要件**{: style="color: var(--b3-font-color10);"}', "成立要件").replace(
            '**适用边界**{: style="background-color: var(--b3-font-background11);"}', "适用边界"
        )
        self.assertIn("E040", {finding.code for finding in validate(plain, source_text=SOURCE)})

    def test_source_style_must_come_from_matching_provider_range(self):
        wrong_topic_style = VALID.replace(
            '**成立要件**{: style="color: var(--b3-font-color10);"}',
            '**法律效果**{: style="color: var(--b3-font-color12);"}',
        )
        self.assertIn("E039", {finding.code for finding in validate(wrong_topic_style, source_text=SOURCE)})

    def test_inferred_child_topic_uses_nearest_confirmed_parent_source_range(self):
        child = VALID.replace('custom-qb-note-topic-id="civil-elements"', 'custom-qb-note-topic-id="civil-elements-definition"')
        self.assertEqual(validate(child, source_text=SOURCE), [])

    def test_source_styled_text_cannot_drop_its_style(self):
        source = SOURCE.replace(
            "    - 要件一。",
            '    - **要件一**{: style="color: var(--b3-font-color5);"}。',
        )
        self.assertIn("E041", {finding.code for finding in validate(VALID, source_text=source)})

    def test_plain_source_range_allows_plain_card(self):
        source = SOURCE.replace('**成立要件**{: style="color: var(--b3-font-color10);"}', "成立要件").replace(
            '**适用边界**{: style="background-color: var(--b3-font-background11);"}', "适用边界"
        )
        plain = VALID.replace('**成立要件**{: style="color: var(--b3-font-color10);"}', "成立要件").replace(
            '**适用边界**{: style="background-color: var(--b3-font-background11);"}', "适用边界"
        )
        codes = {finding.code for finding in validate(plain, source_text=source)}
        self.assertNotIn("E030", codes)
        self.assertNotIn("E040", codes)

    def test_rejects_multiline_ial_and_question_topic_field(self):
        malformed = VALID.replace(
            ' custom-dm-card-id="fc-civil-elements-v1"',
            '\n   custom-dm-card-id="fc-civil-elements-v1"',
        ).replace(
            'custom-qb-note-topic-id="civil-elements"',
            'custom-qb-question-topic-ids="civil-elements"',
        )
        codes = {finding.code for finding in validate(malformed)}
        self.assertIn("E022", codes)
        self.assertIn("E002", codes)
        self.assertIn("E003", codes)

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
            '- **成立要件**{: style="color: var(--b3-font-color10);"}是什么？ #法考/民法/债法/成立要件# #闪卡/优先级/P1#\n    - 要件一。',
            '- **立法审查主体口诀**{: style="color: var(--b3-font-color12);"}：==三分法定、两步审查、先赔后补== #法考/民法/债法/成立要件# #闪卡/优先级/P1#\n    - 句一：==三==分法定\n    - 句二：==两==步审查\n    - 组合：==三两先==',
        )
        self.assertEqual(validate(mnemonic), [])
        unhighlighted = re.sub(r"==([^=]+)==", r"\1", mnemonic)
        self.assertIn("E020", {finding.code for finding in validate(unhighlighted)})

    def test_requires_marknote_anchor_and_short_non_mnemonic_highlight(self):
        no_style = VALID.replace('**成立要件**{: style="color: var(--b3-font-color10);"}', "成立要件").replace(
            '**适用边界**{: style="background-color: var(--b3-font-background11);"}', "适用边界"
        )
        self.assertIn("E030", {finding.code for finding in validate(no_style)})
        long_cloze = VALID.replace('custom-dm-card-kind="basic"', 'custom-dm-card-kind="cloze"').replace(
            "要件一。", "==这是一个过长的完整结论句==。"
        )
        self.assertIn("E029", {finding.code for finding in validate(long_cloze)})

    def test_basic_question_does_not_use_highlight(self):
        highlighted = VALID.replace("成立要件**{: style", "成立==要件==**{: style")
        self.assertIn("E036", {finding.code for finding in validate(highlighted)})

    def test_mnemonic_is_a_cue_not_a_question(self):
        mnemonic = VALID.replace(
            'custom-dm-card-id="fc-civil-elements-v1"',
            'custom-dm-card-id="fc-civil-mnemonic-v1"',
        ).replace(
            'custom-dm-card-kind="basic"',
            'custom-dm-card-kind="mnemonic"',
        ).replace(
            '- **成立要件**{: style="color: var(--b3-font-color10);"}是什么？ #法考/民法/债法/成立要件# #闪卡/优先级/P1#\n    - 要件一。',
            '- **立法审查主体口诀**{: style="color: var(--b3-font-color12);"}：==三分法定== #法考/民法/债法/成立要件# #闪卡/优先级/P1#\n    - 组合：==三分法定==',
        )
        self.assertEqual(validate(mnemonic), [])
        question_mnemonic = mnemonic.replace(
            "：==三分法定== #法考/民法/债法/成立要件#",
            "是什么？ #法考/民法/债法/成立要件#",
        )
        self.assertIn("E037", {finding.code for finding in validate(question_mnemonic)})
        bare_mnemonic = mnemonic.replace("立法审查主体口诀", "口诀")
        self.assertIn("E038", {finding.code for finding in validate(bare_mnemonic)})

    def test_source_aware_cloze_and_mnemonic_targets_must_be_verbatim(self):
        source = SOURCE.replace("    - 要件一。", "    - 要件一：法定。")
        cloze = VALID.replace('custom-dm-card-kind="basic"', 'custom-dm-card-kind="cloze"').replace(
            "    - 要件一。", "    - 要件一：==法定==。"
        )
        self.assertNotIn("E045", {finding.code for finding in validate(cloze, source_text=source)})
        invented = cloze.replace("==法定==", "==法定先行==")
        self.assertIn("E045", {finding.code for finding in validate(invented, source_text=source)})

    def test_prefixless_basic_blockquote_and_callout_are_valid(self):
        blockquote = """> **成立要件**{: style=\"color: var(--b3-font-color10);\"}是什么？ #法考/民法/债法/成立要件# #闪卡/优先级/P1#
>
> - **要件一**{: style="background-color: var(--b3-font-background11);"}。
{: custom-dm-source-key=\"civil-08\" custom-dm-card-id=\"fc-civil-elements-quote-v1\" custom-dm-card-schema=\"1\" custom-dm-card-kind=\"basic\" custom-dm-card-renderer=\"blockquote\" custom-qb-note-topic-id=\"civil-elements\"}
"""
        self.assertEqual(validate(blockquote), [])
        callout = blockquote.replace(
            "> **成立要件**{: style=\"color: var(--b3-font-color10);\"}是什么？ #法考/民法/债法/成立要件# #闪卡/优先级/P1#",
            "> [!WARNING] 成立要件是什么？\n> #法考/民法/债法/成立要件# #闪卡/优先级/P1#",
        ).replace("quote-v1", "warning-v1").replace('renderer="blockquote"', 'renderer="callout"')
        callout = callout.replace('background-color: var(--b3-font-background11);', 'background-color: var(--b3-font-background11); color: var(--b3-font-color10);')
        callout = callout.replace('> - **要件一**{: style="background-color: var(--b3-font-background11); color: var(--b3-font-color10);"}。', '> - **要件一**{: style="background-color: var(--b3-font-background11); color: var(--b3-font-color10);"}。\n> - **补充**{: style="color: var(--b3-font-color12);"}。')
        self.assertEqual(validate(callout), [])

    def test_callout_title_is_the_question_front(self):
        invalid = VALID.replace(
            '- **成立要件**{: style="color: var(--b3-font-color10);"}是什么？ #法考/民法/债法/成立要件# #闪卡/优先级/P1#\n',
            '> [!WARNING] 成立要件陷阱\n> **成立要件**{: style="color: var(--b3-font-color10);"}是什么？ #法考/民法/债法/成立要件# #闪卡/优先级/P1#\n>\n',
        ).replace('custom-dm-card-renderer="list"', 'custom-dm-card-renderer="callout"')
        self.assertIn("E067", {finding.code for finding in validate(invalid)})

    def test_callout_title_cannot_contain_inline_style(self):
        styled = """> [!WARNING] **成立要件**是什么？ #法考/民法/债法/成立要件# #闪卡/优先级/P1#
>
> - **要件一**{: style="background-color: var(--b3-font-background11); color: var(--b3-font-color10);"}。
{: custom-dm-source-key="civil-08" custom-dm-card-id="fc-civil-elements-warning-v1" custom-dm-card-schema="1" custom-dm-card-kind="basic" custom-dm-card-renderer="callout" custom-qb-note-topic-id="civil-elements"}
"""
        self.assertIn("E068", {finding.code for finding in validate(styled)})

    def test_callout_tags_should_be_on_a_separate_quote_line(self):
        tagged_title = """> [!WARNING] 成立要件是什么？ #法考/民法/债法/成立要件# #闪卡/优先级/P1#
>
> - **要件一**{: style="background-color: var(--b3-font-background11); color: var(--b3-font-color10);"}。
{: custom-dm-source-key="civil-08" custom-dm-card-id="fc-civil-elements-warning-tags-v1" custom-dm-card-schema="1" custom-dm-card-kind="basic" custom-dm-card-renderer="callout" custom-qb-note-topic-id="civil-elements"}
"""
        self.assertIn("W115", {finding.code for finding in validate(tagged_title)})

    def test_long_compound_answer_requires_semantic_children(self):
        compound = VALID.replace(
            "    - 要件一。",
            "    - 认为原、被告的权利主张侵犯了自己的权利，将原告和被告一并作为被告，提起独立的诉讼请求。",
        ).replace(
            '        - **适用边界**{: style="background-color: var(--b3-font-background11);"}明确。\n',
            "",
        )
        self.assertIn("W114", {finding.code for finding in validate(compound)})

    def test_requires_knowledge_tag_and_valid_priority_namespace(self):
        missing = VALID.replace(" #法考/民法/债法/成立要件# #闪卡/优先级/P1#", "")
        self.assertIn("E033", {finding.code for finding in validate(missing)})
        generic = VALID.replace("#法考/民法/债法/成立要件#", "#立法程序#")
        self.assertNotIn("E033", {finding.code for finding in validate(generic)})
        no_priority = VALID.replace(" #闪卡/优先级/P1#", "")
        self.assertIn("E035", {finding.code for finding in validate(no_priority)})
        invalid = VALID.replace("#闪卡/优先级/P1#", "#闪卡/P1#")
        self.assertIn("E034", {finding.code for finding in validate(invalid)})

    def test_topic_reuse_and_report_reconciliation(self):
        cards = []
        for number in range(1, 6):
            cards.append(VALID.replace("fc-civil-elements-v1", f"fc-civil-elements-v{number}"))
        deck = "\n".join(cards) + "\n```yaml\nreport:\n  candidates: 5\n  accepted: 5\n  rejected: 0\n  rejection_reasons: {}\nsource:\n  note: \"民法/成立要件\"\n  protocol: \"DAMO 闪卡 schema 1\"\n```\n"
        self.assertIn("E013", {finding.code for finding in validate(deck, require_report=True)})
        self.assertNotIn("E032", {finding.code for finding in validate(deck, require_report=True)})
        self.assertIn("E032", {finding.code for finding in validate(deck.replace("accepted: 5", "accepted: 4"), require_report=True)})

    def test_rejects_internal_audit_preamble(self):
        preamble = """- 源笔记：[[20-整理/考点25]]
- 协议：DAMO schema 1
- 标签：取自源笔记
- 构成：1 张 = basic 1
- 着色图例：color10＝主体
- 章节：沿用源笔记
- 样式继承：逐字复用
- 源笔记说明：残留单字挖空
- 高亮职责：basic 不挖空

"""
        findings = validate(preamble + VALID)
        self.assertEqual(sum(finding.code == "E042" for finding in findings), 9)

    def test_requires_one_final_source_protocol_line(self):
        report = "```yaml\nreport:\n  candidates: 1\n  accepted: 1\n  rejected: 0\n  rejection_reasons: {}\nsource:\n  note: \"民法/成立要件\"\n  protocol: \"DAMO 闪卡 schema 1\"\n```\n"
        self.assertNotIn("E071", {finding.code for finding in validate(VALID + report, require_report=True)})
        self.assertIn("E070", {finding.code for finding in validate(VALID, require_report=True)})
        misplaced = report + VALID
        self.assertIn("E071", {finding.code for finding in validate(misplaced, require_report=True)})

    def test_plain_text_report_is_rejected(self):
        plain = "生成报告：候选 1；接受 1；拒绝 0。\n"
        self.assertIn("E070", {finding.code for finding in validate(VALID + plain, require_report=True)})


if __name__ == "__main__":
    unittest.main()
