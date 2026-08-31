#!/usr/bin/env python3
"""Export SiYuan .sy documents to Markdown with configurable IAL."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath


PORTABLE_EXCLUDES = (
    "id",
    "update",
    "updated",
    "custom-sy-av-*",
    "custom-av-*",
    "av-*",
    "data-av-*",
)
WINDOWS_INVALID = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
TABLE_START = re.compile(r"<table\b", re.IGNORECASE)
TABLE_END = re.compile(r"</table\s*>", re.IGNORECASE)


class ExportError(RuntimeError):
    pass


@dataclass(frozen=True)
class IalOptions:
    mode: str = "portable"
    include: tuple[str, ...] = ()
    exclude: tuple[str, ...] = ()


@dataclass(frozen=True)
class SourceDocument:
    path: Path
    workspace: Path
    notebook: str
    document_id: str
    archive_path: PurePosixPath


@dataclass
class TableCell:
    content: list[str]
    row: int
    column: int
    colspan: int
    rowspan: int
    attrs: dict[str, str]


def _matches(name: str, pattern: str) -> bool:
    expression = re.escape(pattern).replace(r"\*", ".*")
    return re.fullmatch(expression, name) is not None


def _matches_any(name: str, patterns: Sequence[str]) -> bool:
    return any(_matches(name, pattern) for pattern in patterns)


def _ial_tokens(value: str) -> list[tuple[str | None, str]]:
    tokens: list[tuple[str | None, str]] = []
    index = 0
    while index < len(value):
        while index < len(value) and value[index].isspace():
            index += 1
        if index >= len(value):
            break
        start = index
        while index < len(value) and not value[index].isspace() and value[index] != "=":
            index += 1
        name = value[start:index]
        name_end = index
        while index < len(value) and value[index].isspace():
            index += 1
        if index >= len(value) or value[index] != "=":
            raw = value[start:name_end]
            token_name = "id" if raw.startswith("#") else "class" if raw.startswith(".") else None
            tokens.append((token_name, raw))
            index = name_end
            continue
        index += 1
        while index < len(value) and value[index].isspace():
            index += 1
        quote = value[index] if index < len(value) and value[index] in "\"'" else None
        if quote:
            index += 1
            while index < len(value):
                if value[index] == "\\":
                    index += 2
                    continue
                character = value[index]
                index += 1
                if character == quote:
                    break
        else:
            while index < len(value) and not value[index].isspace():
                index += 1
        tokens.append((name, value[start:index]))
    return tokens


def _keep_attribute(name: str | None, options: IalOptions) -> bool:
    if name is None:
        return options.mode != "none"
    if _matches_any(name, options.exclude):
        return False
    if _matches_any(name, options.include):
        return True
    if options.mode == "none":
        return False
    if options.mode == "all":
        return True
    return not _matches_any(name, PORTABLE_EXCLUDES)


def _filter_ial(value: str, options: IalOptions) -> str:
    kept = [raw for name, raw in _ial_tokens(value) if _keep_attribute(name, options)]
    return f"{{: {' '.join(kept)}}}" if kept else ""


def _filter_line(line: str, options: IalOptions) -> str:
    output: list[str] = []
    cursor = 0
    code_ticks = 0
    while cursor < len(line):
        if line[cursor] == "`":
            end = cursor + 1
            while end < len(line) and line[end] == "`":
                end += 1
            count = end - cursor
            code_ticks = count if code_ticks == 0 else 0 if code_ticks == count else code_ticks
            output.append(line[cursor:end])
            cursor = end
            continue
        if code_ticks == 0 and line.startswith("{:", cursor):
            end = cursor + 2
            quote: str | None = None
            while end < len(line):
                character = line[end]
                if quote and character == "\\":
                    end += 2
                    continue
                if character in "\"'":
                    quote = None if quote == character else quote or character
                elif character == "}" and quote is None:
                    break
                end += 1
            if end < len(line):
                output.append(_filter_ial(line[cursor + 2 : end].strip(), options))
                cursor = end + 1
                continue
        output.append(line[cursor])
        cursor += 1
    return "".join(output)


def filter_kramdown_ial(kramdown: str, options: IalOptions) -> str:
    fence: str | None = None
    output: list[str] = []
    for line in kramdown.split("\n"):
        match = re.match(r"^\s*(?:>\s*)*(`{3,}|~{3,})", line)
        if match:
            marker = match.group(1)[0]
            fence = marker if fence is None else None if fence == marker else fence
            output.append(line)
        elif fence:
            output.append(line)
        elif re.fullmatch(r"\s*\{:.*\}\s*", line) and not _filter_line(line, options).strip():
            # A line that held only IAL attributes filtered to nothing must vanish
            # entirely, or pasting the export back leaves an empty block per line.
            continue
        else:
            output.append(_filter_line(line, options))
    return re.sub(r"^[ \t]+$", "", "\n".join(output), flags=re.MULTILINE)


class _TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.rows: list[list[TableCell]] = []
        self.declared_width = 0
        self._table_depth = 0
        self._row: list[TableCell] | None = None
        self._cell: TableCell | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        lowered = tag.lower()
        if lowered == "table":
            self._table_depth += 1
            if self._table_depth > 1 and self._cell:
                self._cell.content.append(self.get_starttag_text())
            return
        if self._table_depth != 1:
            if self._cell:
                self._cell.content.append(self.get_starttag_text())
            return
        if lowered == "col":
            self.declared_width += 1
        elif lowered == "tr":
            self._row = []
        elif lowered in {"td", "th"} and self._row is not None:
            attributes = {key.lower(): value or "" for key, value in attrs}
            self._cell = TableCell(
                content=[],
                row=len(self.rows),
                column=0,
                colspan=_positive_int(attributes.get("colspan")),
                rowspan=_positive_int(attributes.get("rowspan")),
                attrs=attributes,
            )
        elif self._cell:
            self._cell.content.append("<br />" if lowered == "br" else self.get_starttag_text())

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self._cell:
            self._cell.content.append("<br />" if tag.lower() == "br" else self.get_starttag_text())
        elif tag.lower() == "col" and self._table_depth == 1:
            self.declared_width += 1

    def handle_endtag(self, tag: str) -> None:
        lowered = tag.lower()
        if lowered == "table":
            if self._table_depth > 1 and self._cell:
                self._cell.content.append(f"</{tag}>")
            self._table_depth -= 1
        elif lowered in {"td", "th"} and self._cell and self._row is not None:
            self._row.append(self._cell)
            self._cell = None
        elif lowered == "tr" and self._row is not None:
            self.rows.append(self._row)
            self._row = None
        elif self._cell and lowered not in {"thead", "tbody", "tfoot", "colgroup"}:
            self._cell.content.append(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        if self._cell:
            self._cell.content.append(data)

    def handle_entityref(self, name: str) -> None:
        if self._cell:
            self._cell.content.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        if self._cell:
            self._cell.content.append(f"&#{name};")


def _positive_int(value: str | None) -> int:
    try:
        parsed = int(value or "1")
    except ValueError:
        return 1
    return parsed if parsed > 0 else 1


def _cell_content(cell: TableCell) -> str:
    content = re.sub(r"\r?\n", " ", "".join(cell.content)).strip()
    return re.sub(r'^\s*\{:\s*(?=[^}]*\b(?:colspan|rowspan)\b)[^}]*\}\s*', "", content)


def _cell_ial(cell: TableCell) -> str:
    attributes: list[str] = []
    if cell.colspan > 1:
        attributes.append(f'colspan="{cell.colspan}"')
    if cell.rowspan > 1:
        attributes.append(f'rowspan="{cell.rowspan}"')
    for name in ("align", "style", "class"):
        value = cell.attrs.get(name)
        if value:
            attributes.append(f'{name}="{value.replace(chr(34), "&quot;")}"')
    return f" {{: {' '.join(attributes)}}}" if attributes else ""


def _render_table(source: str) -> str:
    parser = _TableParser()
    parser.feed(source)
    occupied: list[list[TableCell | None]] = []
    for row_index, row in enumerate(parser.rows):
        while len(occupied) <= row_index:
            occupied.append([])
        column = 0
        for cell in row:
            while column < len(occupied[row_index]) and occupied[row_index][column] is not None:
                column += 1
            cell.column = column
            for target_row in range(row_index, row_index + cell.rowspan):
                while len(occupied) <= target_row:
                    occupied.append([])
                while len(occupied[target_row]) < column + cell.colspan:
                    occupied[target_row].append(None)
                for target_column in range(column, column + cell.colspan):
                    occupied[target_row][target_column] = cell
            column += cell.colspan
    width = parser.declared_width or max((len(row) for row in occupied), default=0)
    if width == 0 or not parser.rows:
        return ""
    lines: list[str] = []
    for row_index in range(len(parser.rows)):
        cells: list[str] = []
        for column in range(width):
            cell = occupied[row_index][column] if column < len(occupied[row_index]) else None
            if cell is None or cell.row != row_index or cell.column != column:
                cells.append('{: class="fn__none"}')
            else:
                content = _cell_content(cell).replace("|", r"\|")
                cells.append(f"{content}{_cell_ial(cell)}")
        lines.append(f"| {' | '.join(cells)} |")
    lines.insert(1, f"| {' | '.join('---' for _ in range(width))} |")
    lines.append(f'{{: colgroup="{"|" * max(0, width - 1)}"}}')
    return "\n".join(lines)


def convert_html_tables(kramdown: str) -> str:
    lines = kramdown.split("\n")
    output: list[str] = []
    table: list[str] | None = None
    fence: str | None = None
    for line in lines:
        fence_match = re.match(r"^\s*(?:>\s*)*(`{3,}|~{3,})", line)
        if table is None and fence_match:
            marker = fence_match.group(1)[0]
            fence = marker if fence is None else None if fence == marker else fence
            output.append(line)
            continue
        if fence:
            output.append(line)
        elif table is not None:
            table.append(line)
            if TABLE_END.search(line):
                output.append(_render_table("\n".join(table)))
                table = None
        elif TABLE_START.search(line):
            if TABLE_END.search(line):
                output.append(_render_table(line))
            else:
                table = [line]
        else:
            output.append(line)
    if table:
        output.extend(table)
    converted = "\n".join(output)
    return re.sub(
        r'(^|\n)\{: colgroup="[^"]*"\}\n(?=\{: [^}\n]*\bcolgroup="[^"]*"[^}\n]*\})',
        r"\1",
        converted,
    )


def prepare_kramdown(kramdown: str, options: IalOptions) -> str:
    return filter_kramdown_ial(convert_html_tables(kramdown), options)


def discover_kernel(explicit: Path | None = None) -> Path:
    candidates: list[Path] = []
    if explicit:
        candidates.append(explicit)
    if configured := os.environ.get("SIYUAN_KERNEL_PATH"):
        candidates.append(Path(configured))
    for command in ("SiYuan-Kernel.exe", "SiYuan-Kernel", "siyuan.exe"):
        if resolved := shutil.which(command):
            candidates.append(Path(resolved))
    home = Path.home()
    local = Path(os.environ.get("LOCALAPPDATA", home / "AppData/Local"))
    program_files = Path(os.environ.get("ProgramFiles", "C:/Program Files"))
    candidates.extend(
        (
            Path("D:/scoop/apps/B3log.SiYuan/current/app/resources/kernel/SiYuan-Kernel.exe"),
            home / "scoop/apps/B3log.SiYuan/current/app/resources/kernel/SiYuan-Kernel.exe",
            local / "Programs/SiYuan/resources/kernel/SiYuan-Kernel.exe",
            program_files / "SiYuan/resources/kernel/SiYuan-Kernel.exe",
        )
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    raise ExportError("SiYuan-Kernel was not found; pass --kernel or set SIYUAN_KERNEL_PATH")


def find_workspace(sy_path: Path, explicit: Path | None = None) -> tuple[Path, str]:
    resolved = sy_path.resolve()
    if explicit:
        workspace = explicit.resolve()
        try:
            relative = resolved.relative_to(workspace / "data")
        except ValueError as error:
            raise ExportError(f"{resolved} is outside {workspace / 'data'}") from error
        if len(relative.parts) < 2:
            raise ExportError(f"Cannot determine notebook for {resolved}")
        return workspace, relative.parts[0]
    for parent in resolved.parents:
        if parent.name == "data":
            relative = resolved.relative_to(parent)
            if len(relative.parts) >= 2:
                return parent.parent, relative.parts[0]
    raise ExportError(f"{resolved} is not under a SiYuan workspace data directory; pass --workspace")


def _document_title(path: Path) -> str:
    try:
        root = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ExportError(f"Cannot read SiYuan file {path}: {error}") from error
    properties = root.get("Properties") or {}
    return str(properties.get("title") or root.get("ID") or path.stem)


def _sanitize_segment(value: str) -> str:
    sanitized = WINDOWS_INVALID.sub("_", value).rstrip(". ").strip()
    return sanitized or "Untitled"


def _archive_path(path: Path, workspace: Path, notebook: str, source_root: Path) -> PurePosixPath:
    relative = path.resolve().relative_to(source_root.resolve())
    ids = [*relative.parts[:-1], path.stem]
    titles: list[str] = []
    cursor = source_root.resolve()
    for index, document_id in enumerate(ids):
        doc_file = cursor / f"{document_id}.sy"
        titles.append(_sanitize_segment(_document_title(doc_file) if doc_file.is_file() else document_id))
        cursor /= document_id
    titles[-1] = f"{titles[-1]}.md"
    return PurePosixPath(*titles)


def collect_sources(values: Sequence[Path], workspace: Path | None = None) -> list[SourceDocument]:
    files: dict[Path, Path] = {}
    for value in values:
        if value.is_file() and value.suffix.lower() == ".sy":
            resolved = value.resolve()
            files.setdefault(resolved, resolved.parent)
        elif value.is_dir():
            root = value.resolve()
            for path in root.rglob("*.sy"):
                if path.is_file():
                    files.setdefault(path.resolve(), root)
        else:
            raise ExportError(f"Source is not a .sy file or directory: {value}")
    ordered = sorted(files.items(), key=lambda item: str(item[0]).casefold())
    if not ordered:
        raise ExportError("No .sy files were found")
    documents: list[SourceDocument] = []
    for path, source_root in ordered:
        source_workspace, notebook = find_workspace(path, workspace)
        documents.append(
            SourceDocument(
                path=path,
                workspace=source_workspace,
                notebook=notebook,
                document_id=path.stem,
                archive_path=_archive_path(path, source_workspace, notebook, source_root),
            )
        )
    return documents


def _chunks(values: Sequence[SourceDocument], size: int = 128) -> Iterable[Sequence[SourceDocument]]:
    for index in range(0, len(values), size):
        yield values[index : index + size]


def export_with_kernel(kernel: Path, documents: Sequence[SourceDocument], options: IalOptions) -> dict[Path, str]:
    markdown: dict[Path, str] = {}
    workspaces = sorted({document.workspace for document in documents}, key=str)
    for workspace in workspaces:
        workspace_docs = [document for document in documents if document.workspace == workspace]
        for group in _chunks(workspace_docs):
            command = [
                str(kernel),
                "--workspace",
                str(workspace),
                "--format",
                "json",
                "block",
                "batch-kramdown",
                "--ids",
                ",".join(document.document_id for document in group),
            ]
            result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")
            if result.returncode:
                detail = (result.stderr or result.stdout).strip()
                raise ExportError(f"SiYuan-Kernel export failed for {workspace}: {detail}")
            try:
                response = json.loads(result.stdout)
            except json.JSONDecodeError as error:
                raise ExportError(f"SiYuan-Kernel returned invalid JSON: {error}") from error
            for document in group:
                source = response.get(document.document_id)
                if not isinstance(source, str) or not source:
                    raise ExportError(f"SiYuan-Kernel returned no Kramdown for {document.path}")
                markdown[document.path] = f"{prepare_kramdown(source, options).rstrip()}\n"
    return markdown


def _unique_paths(documents: Sequence[SourceDocument], flat: bool = False) -> dict[Path, PurePosixPath]:
    result: dict[Path, PurePosixPath] = {}
    occupied: set[str] = set()
    for document in documents:
        candidate = PurePosixPath(document.archive_path.name) if flat else document.archive_path
        key = str(candidate).casefold()
        if key in occupied:
            candidate = candidate.with_name(f"{candidate.stem} [{document.document_id}].md")
        occupied.add(str(candidate).casefold())
        result[document.path] = candidate
    return result


def write_output(
    documents: Sequence[SourceDocument],
    markdown: dict[Path, str],
    output: Path | None,
    zip_path: Path | None,
    force: bool,
    flat: bool = False,
) -> list[Path]:
    paths = _unique_paths(documents, flat)
    if zip_path:
        if zip_path.exists() and not force:
            raise ExportError(f"Output already exists: {zip_path}; pass --force to replace it")
        zip_path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for document in documents:
                archive.writestr(str(paths[document.path]), markdown[document.path])
        return [zip_path]
    if output is None:
        raise ExportError("Pass --output for Markdown files or --zip for one archive")
    if len(documents) == 1 and output.suffix.lower() == ".md":
        targets = {documents[0].path: output}
    else:
        targets = {document.path: output / Path(str(paths[document.path])) for document in documents}
    existing = [target for target in targets.values() if target.exists()]
    if existing and not force:
        raise ExportError(f"Output already exists: {existing[0]}; pass --force to replace it")
    for document in documents:
        target = targets[document.path]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(markdown[document.path], encoding="utf-8", newline="\n")
    return list(targets.values())


def _patterns(value: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in value.split(",") if item.strip())


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sources", nargs="+", type=Path, help=".sy files or directories to scan recursively")
    destination = parser.add_mutually_exclusive_group(required=True)
    destination.add_argument("--output", type=Path, help="Output .md file for one source, or directory for many")
    destination.add_argument("--zip", dest="zip_path", type=Path, help="Output Markdown ZIP path")
    parser.add_argument("--workspace", type=Path, help="SiYuan workspace when it cannot be inferred from the source path")
    parser.add_argument("--kernel", type=Path, help="Path to SiYuan-Kernel")
    parser.add_argument("--ial", choices=("portable", "all", "none"), default="portable")
    parser.add_argument("--include", default="", help="Comma-separated IAL names or * patterns to keep")
    parser.add_argument("--exclude", default="", help="Comma-separated IAL names or * patterns to remove")
    parser.add_argument(
        "--flat",
        action="store_true",
        help="Flatten nested source documents into the output root instead of preserving their relative folders",
    )
    parser.add_argument("--force", action="store_true", help="Replace existing output files")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        documents = collect_sources(args.sources, args.workspace)
        kernel = discover_kernel(args.kernel)
        options = IalOptions(args.ial, _patterns(args.include), _patterns(args.exclude))
        markdown = export_with_kernel(kernel, documents, options)
        outputs = write_output(documents, markdown, args.output, args.zip_path, args.force, args.flat)
    except ExportError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(f"Exported {len(documents)} SiYuan document(s) to {len(outputs)} output file(s).")
    for output in outputs:
        print(output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
