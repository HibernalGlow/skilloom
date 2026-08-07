#!/usr/bin/env python3
"""Regression tests for the SiYuan topic manifest workflow."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("siyuan_topic_manifest.py")
SPEC = importlib.util.spec_from_file_location("siyuan_topic_manifest", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class TopicManifestTests(unittest.TestCase):
    def test_flattens_outline_with_paths_and_quick_links(self) -> None:
        outline = [{
            "id": "20260807120000-abcdefg",
            "name": "第一章&nbsp;总论",
            "subType": "h1",
            "blocks": [{
                "id": "20260807120001-abcdefg",
                "content": "善意取得",
                "subType": "h2",
                "children": [],
            }],
        }]

        entries = MODULE.outline_entries(outline)

        self.assertEqual(entries[1]["heading_path"], ["第一章 总论", "善意取得"])
        self.assertEqual(entries[1]["quick_link"], "siyuan://blocks/20260807120001-abcdefg")

    def test_manifest_requires_explicit_actions_and_valid_topic_ids(self) -> None:
        manifest = {
            "entries": [
                {"block_id": "20260807120000-abcdefg", "action": "skip", "topic_id": ""},
                {"block_id": "20260807120001-abcdefg", "action": "set", "topic_id": "civil-good-faith"},
            ],
        }

        self.assertEqual(len(MODULE.planned_entries(manifest)), 1)
        manifest["entries"][1]["topic_id"] = "Invalid Topic"
        with self.assertRaises(MODULE.ManifestError):
            MODULE.planned_entries(manifest)

    def test_load_manifest_rejects_wrong_attribute_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "topic.json"
            path.write_text('{"schema_version": 1, "attribute": "wrong", "entries": []}', encoding="utf-8")

            with self.assertRaises(MODULE.ManifestError):
                MODULE.load_manifest(path)

    def test_markdown_keeps_verified_and_planned_topic_ids_visible(self) -> None:
        manifest = {
            "manifest_file": "note.topic-map.json",
            "document": {"id": "20260807120000-abcdefg", "title": "笔记", "hpath": "/笔记"},
            "entries": [{
                "block_id": "20260807120001-abcdefg",
                "level": 2,
                "title": "善意取得",
                "quick_link": "siyuan://blocks/20260807120001-abcdefg",
                "current_topic_id": "civil-old-topic",
                "action": "set",
                "topic_id": "civil-good-faith",
            }],
        }

        markdown = MODULE.render_markdown(manifest)

        self.assertIn("当前 `civil-old-topic`", markdown)
        self.assertIn("计划 `set:civil-good-faith`", markdown)


if __name__ == "__main__":
    unittest.main()
