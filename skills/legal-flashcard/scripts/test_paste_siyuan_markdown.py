import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from paste_siyuan_markdown import (
    BridgeLocation,
    MarkdownSource,
    PasteError,
    build_request,
    collect_markdown_sources,
    publish_request,
    require_fresh_heartbeat,
    resolve_title_map,
    select_titles,
    target_path,
    wait_for_result,
)


class SiyuanMarkdownPasteTests(unittest.TestCase):
    def test_collects_files_recursively_and_preserves_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            nested = root / "nested"
            nested.mkdir()
            first = root / "one.md"
            second = nested / "two.markdown"
            first.write_bytes(b"# One\r\n{: id=\"one\"}\r\n")
            second.write_text("# Two\n", encoding="utf-8")
            sources = collect_markdown_sources([root, first])
            self.assertEqual({source.path for source in sources}, {first.resolve(), second.resolve()})
            one = next(source for source in sources if source.path == first.resolve())
            self.assertIn("\r\n{: id=\"one\"}", one.markdown)

    def test_selects_explicit_map_h1_and_filename_titles(self) -> None:
        root = Path("notes")
        one = MarkdownSource(root / "one.md", '# Heading {: id="root"}\n')
        two = MarkdownSource(root / "two.md", "Body\n")
        self.assertEqual(select_titles([one], explicit_title="Manual")[one.path], "Manual")
        self.assertEqual(select_titles([one], title_mapping={one.path: "Mapped"})[one.path], "Mapped")
        self.assertEqual(select_titles([one])[one.path], "Heading")
        self.assertEqual(select_titles([two])[two.path], "two")
        fenced = MarkdownSource(root / "fenced.md", "```md\n# Not a title\n```\n# Actual\n")
        self.assertEqual(select_titles([fenced])[fenced.path], "Actual")
        with self.assertRaises(PasteError):
            select_titles([one, two], explicit_title="Shared")

    def test_resolves_title_map_relative_to_the_map_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            nested = root / "nested"
            nested.mkdir()
            one = MarkdownSource((root / "one.md").resolve(), "")
            two = MarkdownSource((nested / "two.md").resolve(), "")
            result = resolve_title_map(
                [one, two],
                {"one.md": "First", "nested/two.md": "Second"},
                root / "titles.json",
            )
            self.assertEqual(result, {one.path: "First", two.path: "Second"})

    def test_rejects_ambiguous_filename_title_map_entry(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = MarkdownSource((root / "first" / "same.md").resolve(), "")
            second = MarkdownSource((root / "second" / "same.md").resolve(), "")
            with self.assertRaisesRegex(PasteError, "ambiguous"):
                resolve_title_map([first, second], {"same.md": "Shared"}, root / "titles.json")

    def test_builds_create_request_and_rejects_duplicate_targets(self) -> None:
        source = MarkdownSource(Path("one.md"), '# Heading\n{: custom-dm-card-id="card"}')
        request = build_request(
            [source], "notebook-id", "/Legal/Flashcards/", {source.path: "Manual"}, "request_1234"
        )
        self.assertEqual(request["protocolVersion"], 1)
        self.assertEqual(request["command"], "paste")
        self.assertEqual(request["closeActive"], "never")
        self.assertEqual(request["items"][0]["target"], {
            "mode": "create",
            "notebookId": "notebook-id",
            "path": "/Legal/Flashcards/Manual",
            "title": "Manual",
        })
        self.assertIn('custom-dm-card-id="card"', request["items"][0]["markdown"])
        self.assertEqual(target_path("/", "Root"), "/Root")
        with self.assertRaises(PasteError):
            build_request([source, source], "notebook-id", "/", {source.path: "Same"})

    def test_requires_matching_fresh_heartbeat(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            location = BridgeLocation("http://127.0.0.1:6806", root, root / "bridge")
            location.root.mkdir()
            heartbeat = {
                "protocolVersion": 1,
                "pluginVersion": "0.0.4",
                "workspace": str(root),
                "frontend": "desktop",
                "updatedAt": "2026-08-24T00:00:00.000Z",
                "supportedCommands": ["paste", "export"],
                "supportedPasteModes": ["create", "append", "replace"],
            }
            (location.root / "heartbeat.json").write_text(json.dumps(heartbeat), encoding="utf-8")
            now = datetime(2026, 8, 24, 0, 0, 5, tzinfo=timezone.utc)
            self.assertEqual(require_fresh_heartbeat(location, now=now)["pluginVersion"], "0.0.4")
            with self.assertRaisesRegex(PasteError, "stale"):
                require_fresh_heartbeat(location, max_age_seconds=2, now=now)

    def test_publishes_atomically_and_reads_result(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            location = BridgeLocation("", root, root / "bridge")
            request = {"requestId": "request_1234", "items": []}
            inbox = publish_request(location, request)
            self.assertEqual(json.loads(inbox.read_text(encoding="utf-8")), request)
            self.assertEqual(list(inbox.parent.glob("*.tmp")), [])

            task = location.root / "tasks" / "request_1234"
            task.mkdir(parents=True)
            (task / "events.ndjson").write_text(
                '{"sequence":0,"type":"accepted","message":"Accepted"}\n'
                '{"sequence":10000,"type":"completed","message":"Done"}\n',
                encoding="utf-8",
            )
            result = {
                "protocolVersion": 1,
                "requestId": "request_1234",
                "status": "completed",
                "completedItems": [],
            }
            (task / "result.json").write_text(json.dumps(result), encoding="utf-8")
            events: list[str] = []
            self.assertEqual(
                wait_for_result(location, "request_1234", 0.1, lambda event: events.append(str(event["type"]))),
                result,
            )
            self.assertEqual(events, ["accepted", "completed"])


if __name__ == "__main__":
    unittest.main()
