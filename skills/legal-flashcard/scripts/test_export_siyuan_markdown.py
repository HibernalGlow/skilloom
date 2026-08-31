import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch

from export_siyuan_markdown import (
    IalOptions,
    collect_sources,
    convert_html_tables,
    filter_kramdown_ial,
    export_with_kernel,
    write_output,
)


class SiyuanMarkdownExportTests(unittest.TestCase):
    def test_filters_portable_ial_without_touching_code(self) -> None:
        source = "\n".join(
            (
                "```md",
                '{: id="example" updated="example"}',
                "```",
                '# Title {: id="block" updated="time" custom-dm-card-id="card-1"}',
            )
        )
        result = filter_kramdown_ial(source, IalOptions("portable"))
        self.assertIn('{: id="example" updated="example"}', result)
        self.assertIn('{: custom-dm-card-id="card-1"}', result)
        self.assertNotIn('id="block"', result)

    def test_uses_portable_ial_by_default_and_requires_explicit_none(self) -> None:
        source = '{: id="block" updated="time" custom-dm-card-id="card-1"}'
        self.assertEqual(
            filter_kramdown_ial(source, IalOptions()),
            '{: custom-dm-card-id="card-1"}',
        )
        self.assertEqual(filter_kramdown_ial(source, IalOptions("all")), source)
        self.assertEqual(filter_kramdown_ial(source, IalOptions("none")), "")

    def test_drops_lines_that_only_hold_filtered_ial(self) -> None:
        source = "\n".join(
            (
                "```text",
                '{: id="in-code" updated="x"}',
                "```",
                '{: id="after-code" updated="x"}',
                "Para {: id=\"para\"}",
                '{: id="kept" updated="x" custom-dm-card-id="card-1"}',
            )
        )
        self.assertEqual(
            filter_kramdown_ial(source, IalOptions("portable")),
            "\n".join(
                (
                    "```text",
                    '{: id="in-code" updated="x"}',
                    "```",
                    "Para ",
                    '{: custom-dm-card-id="card-1"}',
                )
            ),
        )

    def test_keeps_pure_ial_lines_when_nothing_is_filtered(self) -> None:
        source = "Para {: id=\"para\"}\n{: id=\"block\" updated=\"time\"}"
        self.assertEqual(filter_kramdown_ial(source, IalOptions("all")), source)

    def test_converts_merged_table_to_markdown(self) -> None:
        source = (
            '<table><colgroup><col /><col /><col /></colgroup>'
            '<thead><tr><th colspan="2">{: colspan="2"}Merged</th><th>B</th></tr></thead>'
            '<tbody><tr><td rowspan="2">{: rowspan="2"}A</td><td>C</td><td>D</td></tr>'
            '<tr><td>E</td><td>F | G</td></tr></tbody></table>'
        )
        self.assertEqual(
            convert_html_tables(source),
            "\n".join(
                (
                    '| Merged {: colspan="2"} | {: class="fn__none"} | B |',
                    "| --- | --- | --- |",
                    '| A {: rowspan="2"} | C | D |',
                    '| {: class="fn__none"} | E | F \\| G |',
                    '{: colgroup="||"}',
                )
            ),
        )

    def test_collects_directory_and_uses_human_titles(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            notebook = root / "data" / "notebook"
            child_dir = notebook / "20260101000000-parent1"
            child_dir.mkdir(parents=True)
            (notebook / "20260101000000-parent1.sy").write_text(
                json.dumps({"ID": "20260101000000-parent1", "Properties": {"title": "Parent"}}),
                encoding="utf-8",
            )
            child = child_dir / "20260101000001-child01.sy"
            child.write_text(
                json.dumps({"ID": child.stem, "Properties": {"title": "Child"}}),
                encoding="utf-8",
            )
            documents = collect_sources([notebook])
            self.assertEqual([str(item.archive_path) for item in documents], ["Parent.md", "Parent/Child.md"])

    def test_writes_multiple_documents_to_zip(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            notebook = root / "data" / "notebook"
            notebook.mkdir(parents=True)
            source = notebook / "20260101000000-parent1.sy"
            source.write_text(
                json.dumps({"ID": source.stem, "Properties": {"title": "Parent"}}),
                encoding="utf-8",
            )
            document = collect_sources([source])[0]
            target = root / "export.zip"
            write_output([document], {source.resolve(): "# Parent\n"}, None, target, False)
            with zipfile.ZipFile(target) as archive:
                self.assertEqual(archive.namelist(), ["Parent.md"])
                self.assertEqual(archive.read("Parent.md").decode("utf-8"), "# Parent\n")

    def test_preserves_selected_directory_tree_and_can_flatten_explicitly(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            notebook = root / "data" / "notebook"
            child_dir = notebook / "20260101000000-parent1"
            child_dir.mkdir(parents=True)
            parent = notebook / "20260101000000-parent1.sy"
            child = child_dir / "20260100000001-child01.sy"
            parent.write_text(
                json.dumps({"ID": parent.stem, "Properties": {"title": "Parent"}}),
                encoding="utf-8",
            )
            child.write_text(
                json.dumps({"ID": child.stem, "Properties": {"title": "Child"}}),
                encoding="utf-8",
            )
            documents = collect_sources([notebook])
            markdown = {document.path: f"# {document.archive_path.stem}\n" for document in documents}

            flat_target = root / "flat"
            write_output(documents, markdown, flat_target, None, False)
            self.assertTrue((flat_target / "Parent.md").is_file())
            self.assertTrue((flat_target / "Parent" / "Child.md").is_file())

            flattened_target = root / "flattened"
            write_output(documents, markdown, flattened_target, None, False, True)
            self.assertEqual(sorted(path.name for path in flattened_target.iterdir()), ["Child.md", "Parent.md"])

    def test_crops_ancestors_before_selected_source_but_keeps_descendants(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            notebook = root / "data" / "notebook"
            outer_id = "20260101000000-outer001"
            selected_id = "20260101000001-subject1"
            parent_id = "20260101000002-parent01"
            child_id = "20260101000003-child001"
            selected = notebook / outer_id / selected_id
            child_dir = selected / parent_id
            child_dir.mkdir(parents=True)
            (notebook / f"{outer_id}.sy").write_text(
                json.dumps({"ID": outer_id, "Properties": {"title": "Long Prefix"}}), encoding="utf-8"
            )
            (notebook / outer_id / f"{selected_id}.sy").write_text(
                json.dumps({"ID": selected_id, "Properties": {"title": "Selected"}}), encoding="utf-8"
            )
            parent = selected / f"{parent_id}.sy"
            parent.write_text(
                json.dumps({"ID": parent_id, "Properties": {"title": "Concrete Note"}}), encoding="utf-8"
            )
            child = child_dir / f"{child_id}.sy"
            child.write_text(
                json.dumps({"ID": child_id, "Properties": {"title": "Nested Note"}}), encoding="utf-8"
            )

            documents = collect_sources([selected])
            self.assertEqual(
                [str(document.archive_path) for document in documents],
                ["Concrete Note.md", "Concrete Note/Nested Note.md"],
            )

    def test_calls_the_offline_kernel_batch_command(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            notebook = root / "data" / "notebook"
            notebook.mkdir(parents=True)
            source = notebook / "20260101000000-parent1.sy"
            source.write_text(
                json.dumps({"ID": source.stem, "Properties": {"title": "Parent"}}),
                encoding="utf-8",
            )
            document = collect_sources([source])[0]
            response = json.dumps({document.document_id: '# Parent\n{: id="block" custom-dm-card-id="card-1"}'})
            with patch(
                "export_siyuan_markdown.subprocess.run",
                return_value=CompletedProcess([], 0, response, ""),
            ) as run:
                result = export_with_kernel(Path("SiYuan-Kernel.exe"), [document], IalOptions())
            command = run.call_args.args[0]
            self.assertIn("batch-kramdown", command)
            self.assertIn(document.document_id, command)
            self.assertEqual(result[source.resolve()], '# Parent\n{: custom-dm-card-id="card-1"}\n')


if __name__ == "__main__":
    unittest.main()
