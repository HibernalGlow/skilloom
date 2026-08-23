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
