import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from siyuan_live_patch import PatchError, apply_patch, changed_blocks, format_plan, parse_blocks


class LivePatchTests(unittest.TestCase):
    def test_parses_block_ial_without_losing_inline_style(self):
        text = '**规则**{: style="color: var(--b3-font-color10);"}。\n{: id="b1" custom-dm-card-id="fc-1" style="font-weight: bold;"}\n'
        blocks = parse_blocks(text)
        self.assertEqual(blocks["b1"].content, '**规则**{: style="color: var(--b3-font-color10);"}。')
        self.assertEqual(dict(blocks["b1"].attrs)["style"], "font-weight: bold;")

    def test_changed_blocks_requires_same_id_set(self):
        before = parse_blocks('# 标题\n{: id="h1"}\n')
        after = parse_blocks('# 新标题\n{: id="h2"}\n')
        with self.assertRaisesRegex(PatchError, "Block ID set changed"):
            changed_blocks(before, after)

    def test_dry_run_writes_inline_style_but_not_block_ial(self):
        before_text = '**规则**{: style="color: var(--b3-font-color10);"}。\n{: id="b1" custom-dm-card-id="fc-1"}\n'
        after_text = '**新规则**{: style="color: var(--b3-font-color11); background-color: var(--b3-font-background11);"}。\n{: id="b1" custom-dm-card-id="fc-1"}\n'
        with TemporaryDirectory() as directory, patch("siyuan_live_patch._run_siyuan") as run:
            root = Path(directory)
            before = root / "before.md"
            after = root / "after.md"
            before.write_text(before_text, encoding="utf-8")
            after.write_text(after_text, encoding="utf-8")
            self.assertEqual(apply_patch("workspace", before, after, confirm=False), ["b1"])
            command = run.call_args.args[1]
            markdown = command[command.index("--data") + 1]
            self.assertIn('style="color: var(--b3-font-color11); background-color: var(--b3-font-background11);"', markdown)
            self.assertNotIn("custom-dm-card-id", markdown)
            self.assertTrue(run.call_args.kwargs["dry_run"])

    def test_block_style_uses_attr_set_and_keeps_card_identity(self):
        before_text = '- 问题？\n{: id="root1" custom-dm-card-id="fc-1" style="color: red;"}\n'
        after_text = '- 问题？\n{: style="background-color: yellow;" custom-dm-card-id="fc-1" id="root1"}\n'
        with TemporaryDirectory() as directory, patch("siyuan_live_patch._run_siyuan") as run:
            root = Path(directory)
            before = root / "before.md"
            after = root / "after.md"
            before.write_text(before_text, encoding="utf-8")
            after.write_text(after_text, encoding="utf-8")
            self.assertEqual(apply_patch("workspace", before, after, confirm=True), ["root1"])
            self.assertEqual(run.call_args.args[1], ["attr", "set", "--id", "root1", "--attr", "style=background-color: yellow;"])
            self.assertFalse(run.call_args.kwargs["dry_run"])

    def test_card_id_change_is_editable_by_default(self):
        before = parse_blocks('- 问题？\n{: id="root1" custom-dm-card-id="fc-1"}\n')
        after = parse_blocks('- 问题？\n{: id="root1" custom-dm-card-id="fc-2"}\n')
        self.assertEqual([item[0].block_id for item in changed_blocks(before, after)], ["root1"])

    def test_card_id_can_be_protected_explicitly(self):
        before = parse_blocks('- 问题？\n{: id="root1" custom-dm-card-id="fc-1"}\n')
        after = parse_blocks('- 问题？\n{: id="root1" custom-dm-card-id="fc-2"}\n')
        with self.assertRaisesRegex(PatchError, "Protected attributes changed"):
            changed_blocks(before, after, protected_attrs={"custom-dm-card-id"})

    def test_priority_tag_change_keeps_same_card_root_id(self):
        before = '- {: id="item1" custom-dm-card-id="fc-procedure-v1"}诉讼行为如何生效？ #闪卡/优先级/P1#\n  {: id="root1"}\n{: id="list1"}\n'
        after = before.replace("/P1#", "/P2#")
        changes = changed_blocks(parse_blocks(before), parse_blocks(after))
        self.assertEqual([(old.block_id, new.content) for old, new in changes], [("root1", '诉讼行为如何生效？ #闪卡/优先级/P2#')])

    def test_list_container_and_item_are_structural_records(self):
        text = '- {: id="item1" custom-dm-card-id="fc-1"}问题？\n  {: id="paragraph1"}\n{: id="list1"}\n'
        blocks = parse_blocks(text)
        self.assertIsNone(blocks["item1"].content)
        self.assertEqual(blocks["paragraph1"].content, "问题？")
        self.assertIsNone(blocks["list1"].content)

    def test_structural_ordinary_rebuild_uses_document_update(self):
        before_text = (
            "- 第一块\n{: id=\"p1\"}\n"
            "{: id=\"doc1\" type=\"doc\" title=\"测试\"}\n"
        )
        after_text = (
            "- 新增块\n"
            "- 第一块改写\n{: id=\"p1\"}\n"
            "{: id=\"doc1\" type=\"doc\" title=\"测试\"}\n"
        )
        with TemporaryDirectory() as directory, patch("siyuan_live_patch._run_siyuan") as run:
            root = Path(directory)
            before = root / "before.md"
            after = root / "after.md"
            before.write_text(before_text, encoding="utf-8")
            after.write_text(after_text, encoding="utf-8")
            self.assertEqual(apply_patch("workspace", before, after, confirm=False), ["doc1"])
            self.assertEqual(run.call_args.args[1][:4], ["block", "update", "--id", "doc1"])
            self.assertIn("--file", run.call_args.args[1])

    def test_structural_rebuild_preserves_special_ids(self):
        before_text = (
            "- 卡片\n{: id=\"card1\" custom-dm-card-id=\"fc-1\"}\n"
            "{: id=\"doc1\" type=\"doc\" title=\"测试\"}\n"
        )
        after_text = (
            "- 新增普通块\n"
            "- 卡片修订\n{: id=\"card1\" custom-dm-card-id=\"fc-2\"}\n"
            "{: id=\"doc1\" type=\"doc\" title=\"测试\"}\n"
        )
        with TemporaryDirectory() as directory, patch("siyuan_live_patch._run_siyuan") as run:
            root = Path(directory)
            before = root / "before.md"
            after = root / "after.md"
            before.write_text(before_text, encoding="utf-8")
            after.write_text(after_text, encoding="utf-8")
            self.assertEqual(apply_patch("workspace", before, after, confirm=False), ["doc1"])
            self.assertIn("--file", run.call_args.args[1])

    def test_structural_rebuild_rejects_missing_special_id(self):
        before = parse_blocks(
            "- 卡片\n{: id=\"card1\" custom-dm-card-id=\"fc-1\"}\n"
            "{: id=\"doc1\" type=\"doc\" title=\"测试\"}\n"
        )
        after = parse_blocks(
            "- 普通块\n{: id=\"doc1\" type=\"doc\" title=\"测试\"}\n"
        )
        with TemporaryDirectory() as directory:
            root = Path(directory)
            before_path = root / "before.md"
            after_path = root / "after.md"
            before_path.write_text(
                "- 卡片\n{: id=\"card1\" custom-dm-card-id=\"fc-1\"}\n"
                "{: id=\"doc1\" type=\"doc\" title=\"测试\"}\n",
                encoding="utf-8",
            )
            after_path.write_text(
                "- 普通块\n{: id=\"doc1\" type=\"doc\" title=\"测试\"}\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(PatchError, "delete special block"):
                apply_patch("workspace", before_path, after_path, confirm=False)

    def test_explicit_special_id_protects_cli_discovered_identity(self):
        before_text = (
            "- 被引用但 IAL 无引用字段\n{: id=\"ref1\"}\n"
            "{: id=\"doc1\" type=\"doc\" title=\"测试\"}\n"
        )
        after_text = "- 新正文\n{: id=\"doc1\" type=\"doc\" title=\"测试\"}\n"
        with TemporaryDirectory() as directory:
            root = Path(directory)
            before_path = root / "before.md"
            after_path = root / "after.md"
            before_path.write_text(before_text, encoding="utf-8")
            after_path.write_text(after_text, encoding="utf-8")
            with self.assertRaisesRegex(PatchError, "delete special block"):
                apply_patch(
                    "workspace",
                    before_path,
                    after_path,
                    confirm=False,
                    special_ids_override={"ref1"},
                )

    def test_format_plan_reports_rebuild_scope(self):
        before_text = (
            "- 普通块\n{: id=\"ordinary1\"}\n"
            "- 卡片\n{: id=\"card1\" custom-dm-card-id=\"fc-1\"}\n"
            "{: id=\"doc1\" type=\"doc\" title=\"测试\"}\n"
        )
        after_text = (
            "- 新增普通块\n"
            "- 卡片\n{: id=\"card1\" custom-dm-card-id=\"fc-2\"}\n"
            "{: id=\"doc1\" type=\"doc\" title=\"测试\"}\n"
        )
        with TemporaryDirectory() as directory:
            root = Path(directory)
            before = root / "before.md"
            after = root / "after.md"
            before.write_text(before_text, encoding="utf-8")
            after.write_text(after_text, encoding="utf-8")
            plan = "\n".join(format_plan(before, after))
            self.assertIn("plan: document rebuild", plan)
            self.assertIn("ordinary-deleted: 1", plan)
            self.assertIn("special-preserved: 1", plan)
            self.assertIn("idless-new-block-lines: 1", plan)
