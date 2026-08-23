#!/usr/bin/env python3
"""Create SiYuan documents by pasting Markdown through Damophus Agent Bridge."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


PROTOCOL_VERSION = 1
DEFAULT_ENDPOINT = os.environ.get("DAMOPHUS_SIYUAN_URL", "http://127.0.0.1:6806")
BRIDGE_RELATIVE_PATH = Path("data/storage/petal/siyuan-damophus/agent-bridge")
MARKDOWN_SUFFIXES = {".md", ".markdown"}
H1_PATTERN = re.compile(r"^#\s+(.+?)\s*$")
TRAILING_IAL_PATTERN = re.compile(r"\s+\{:\s*[^{}\r\n]*\}\s*$")
FENCE_PATTERN = re.compile(r"^\s*(`{3,}|~{3,})")


class PasteError(RuntimeError):
    pass


@dataclass(frozen=True)
class BridgeLocation:
    endpoint: str
    workspace: Path
    root: Path


@dataclass(frozen=True)
class MarkdownSource:
    path: Path
    markdown: str


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def collect_markdown_sources(values: Sequence[Path]) -> list[MarkdownSource]:
    paths: list[Path] = []
    for value in values:
        candidate = value.expanduser()
        if candidate.is_file() and candidate.suffix.lower() in MARKDOWN_SUFFIXES:
            paths.append(candidate.resolve())
        elif candidate.is_dir():
            paths.extend(
                path.resolve()
                for path in candidate.rglob("*")
                if path.is_file() and path.suffix.lower() in MARKDOWN_SUFFIXES
            )
        else:
            raise PasteError(f"Source is not a Markdown file or directory: {value}")
    unique = sorted(set(paths), key=lambda path: str(path).casefold())
    if not unique:
        raise PasteError("No .md or .markdown files were found")
    sources: list[MarkdownSource] = []
    for path in unique:
        try:
            markdown = path.read_bytes().decode("utf-8-sig")
        except UnicodeDecodeError as error:
            raise PasteError(f"Markdown must be UTF-8: {path}") from error
        except OSError as error:
            raise PasteError(f"Cannot read Markdown file {path}: {error}") from error
        sources.append(MarkdownSource(path, markdown))
    return sources


def first_markdown_h1(markdown: str) -> str | None:
    fence: str | None = None
    for line in markdown.splitlines():
        fence_match = FENCE_PATTERN.match(line)
        if fence_match:
            marker = fence_match.group(1)[0]
            if fence is None:
                fence = marker
            elif fence == marker:
                fence = None
            continue
        if fence is not None:
            continue
        match = H1_PATTERN.match(line)
        if match:
            return TRAILING_IAL_PATTERN.sub("", match.group(1)).strip() or None
    return None


def validate_title(value: str, source: Path | None = None) -> str:
    title = value.strip()
    label = f" for {source}" if source else ""
    if not title:
        raise PasteError(f"Document title is empty{label}")
    if title in {".", ".."} or "/" in title or "\\" in title:
        raise PasteError(f"Document title must be one path segment{label}: {title!r}")
    if any(ord(character) < 32 for character in title):
        raise PasteError(f"Document title contains a control character{label}")
    return title


def normalize_directory(value: str) -> str:
    parts = [part for part in value.strip().replace("\\", "/").split("/") if part]
    if any(part in {".", ".."} for part in parts):
        raise PasteError(f"SiYuan directory cannot contain '.' or '..': {value}")
    return f"/{'/'.join(parts)}" if parts else "/"


def target_path(directory: str, title: str) -> str:
    parent = normalize_directory(directory)
    segment = validate_title(title)
    return f"/{segment}" if parent == "/" else f"{parent}/{segment}"


def load_title_map(path: Path) -> dict[str, str]:
    try:
        raw = _read_json(path)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise PasteError(f"Cannot read title map {path}: {error}") from error
    if not isinstance(raw, dict):
        raise PasteError("Title map must be a JSON object whose keys are Markdown paths")
    result: dict[str, str] = {}
    for key, value in raw.items():
        if not isinstance(key, str) or not key.strip() or not isinstance(value, str):
            raise PasteError("Every title-map key and value must be a non-empty string")
        result[key] = validate_title(value)
    return result


def resolve_title_map(
    sources: Sequence[MarkdownSource], mapping: Mapping[str, str], map_path: Path
) -> dict[Path, str]:
    resolved: dict[Path, str] = {}
    for key, title in mapping.items():
        candidate = Path(key).expanduser()
        absolute = candidate if candidate.is_absolute() else map_path.parent / candidate
        matches = [
            source
            for source in sources
            if os.path.normcase(str(absolute.resolve())) == os.path.normcase(str(source.path.resolve()))
        ]
        if not matches:
            matches = [source for source in sources if source.path.name.casefold() == candidate.name.casefold()]
        if not matches:
            raise PasteError(f"Title map entry did not match a source: {key}")
        if len(matches) > 1:
            raise PasteError(f"Title map entry is ambiguous; use a relative or absolute path: {key}")
        source = matches[0]
        if source.path in resolved:
            raise PasteError(f"Title map has multiple entries for {source.path}")
        resolved[source.path] = validate_title(title, source.path)
    return resolved


def select_titles(
    sources: Sequence[MarkdownSource],
    explicit_title: str | None = None,
    title_mapping: Mapping[Path, str] | None = None,
) -> dict[Path, str]:
    if explicit_title is not None and len(sources) != 1:
        raise PasteError("--title can only be used when exactly one Markdown file is selected")
    result: dict[Path, str] = {}
    for source in sources:
        title = explicit_title if explicit_title is not None else (title_mapping or {}).get(source.path)
        title = title or first_markdown_h1(source.markdown) or source.path.stem
        result[source.path] = validate_title(title, source.path)
    return result


def build_request(
    sources: Sequence[MarkdownSource],
    notebook_id: str,
    directory: str,
    titles: Mapping[Path, str],
    request_id: str | None = None,
) -> dict[str, Any]:
    notebook = notebook_id.strip()
    if not notebook:
        raise PasteError("Notebook ID is required")
    items: list[dict[str, Any]] = []
    occupied: set[str] = set()
    for index, source in enumerate(sources, start=1):
        title = titles[source.path]
        destination = target_path(directory, title)
        key = f"{notebook}\0{destination}".casefold()
        if key in occupied:
            raise PasteError(f"Multiple sources resolve to the same SiYuan target: {destination}")
        occupied.add(key)
        items.append({
            "itemId": f"item-{index}",
            "sourceName": source.path.name,
            "markdown": source.markdown,
            "target": {
                "mode": "create",
                "notebookId": notebook,
                "path": destination,
                "title": title,
            },
        })
    return {
        "protocolVersion": PROTOCOL_VERSION,
        "requestId": request_id or str(uuid.uuid4()),
        "createdAt": _iso_now(),
        "command": "paste",
        "closeActive": "never",
        "items": items,
    }


def discover_bridge(endpoint: str = DEFAULT_ENDPOINT, timeout: float = 3.0) -> BridgeLocation:
    normalized = endpoint.rstrip("/")
    request = Request(
        f"{normalized}/api/system/getWorkspaceInfo",
        data=b"{}",
        headers={"content-type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            status = getattr(response, "status", 200)
            payload = json.loads(response.read().decode("utf-8-sig"))
    except HTTPError as error:
        raise PasteError(f"SiYuan returned HTTP {error.code} at {normalized}") from error
    except (URLError, TimeoutError, OSError) as error:
        raise PasteError(f"SiYuan is not reachable at {normalized}: {error}") from error
    except (UnicodeError, json.JSONDecodeError) as error:
        raise PasteError("SiYuan returned invalid workspace information") from error
    data = payload.get("data") if isinstance(payload, dict) else None
    workspace = data.get("workspaceDir") if isinstance(data, dict) else None
    if status != 200 or not isinstance(payload, dict) or payload.get("code") != 0 or not workspace:
        message = payload.get("msg") if isinstance(payload, dict) else None
        raise PasteError(str(message or "SiYuan did not return a workspace path"))
    workspace_path = Path(str(workspace)).resolve()
    return BridgeLocation(normalized, workspace_path, workspace_path / BRIDGE_RELATIVE_PATH)


def require_fresh_heartbeat(
    location: BridgeLocation,
    max_age_seconds: float = 30.0,
    now: datetime | None = None,
) -> dict[str, Any]:
    try:
        heartbeat = _read_json(location.root / "heartbeat.json")
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise PasteError(
            "Damophus Agent Bridge is unavailable; enable its module in SiYuan and keep SiYuan open"
        ) from error
    if not isinstance(heartbeat, dict) or heartbeat.get("protocolVersion") != PROTOCOL_VERSION:
        actual = heartbeat.get("protocolVersion") if isinstance(heartbeat, dict) else None
        raise PasteError(f"Agent Bridge protocol mismatch: expected {PROTOCOL_VERSION}, got {actual}")
    commands = heartbeat.get("supportedCommands")
    modes = heartbeat.get("supportedPasteModes")
    if not isinstance(commands, list) or "paste" not in commands:
        raise PasteError("The installed Agent Bridge does not support paste")
    if not isinstance(modes, list) or "create" not in modes:
        raise PasteError("The installed Agent Bridge does not support document creation")
    workspace = heartbeat.get("workspace")
    expected_workspace = os.path.normcase(os.path.abspath(location.workspace))
    heartbeat_workspace = os.path.normcase(os.path.abspath(workspace)) if isinstance(workspace, str) else ""
    if heartbeat_workspace != expected_workspace:
        raise PasteError("Agent Bridge heartbeat belongs to a different SiYuan workspace")
    updated_raw = heartbeat.get("updatedAt")
    if not isinstance(updated_raw, str):
        raise PasteError("Agent Bridge heartbeat has no valid updatedAt timestamp")
    try:
        updated = datetime.fromisoformat(updated_raw.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError as error:
        raise PasteError(f"Agent Bridge heartbeat has an invalid updatedAt timestamp: {updated_raw}") from error
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    age = (current - updated).total_seconds()
    if age < -1.0 or age > max_age_seconds:
        raise PasteError(f"Damophus Agent Bridge heartbeat is stale ({age:.1f} seconds)")
    return heartbeat


def publish_request(location: BridgeLocation, request: Mapping[str, Any]) -> Path:
    request_id = str(request["requestId"])
    inbox = location.root / "inbox" / f"{request_id}.json"
    completed = location.root / "completed" / f"{request_id}.json"
    if inbox.exists() or completed.exists():
        raise PasteError(f"Agent Bridge request already exists: {request_id}")
    inbox.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{request_id}.", suffix=".tmp", dir=inbox.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(request, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_name, inbox)
    except BaseException as error:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        if isinstance(error, OSError):
            raise PasteError(f"Cannot publish Agent Bridge request: {error}") from error
        raise
    return inbox


def _read_events(path: Path) -> list[dict[str, Any]]:
    try:
        content = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError):
        return []
    events: list[dict[str, Any]] = []
    for line in content.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(event, dict):
            events.append(event)
    return sorted(events, key=lambda event: int(event.get("sequence", -1)))


def wait_for_result(
    location: BridgeLocation,
    request_id: str,
    timeout_seconds: float = 600.0,
    on_event: Callable[[Mapping[str, Any]], None] | None = None,
) -> dict[str, Any]:
    task = location.root / "tasks" / request_id
    deadline = time.monotonic() + timeout_seconds
    last_sequence = -1
    while time.monotonic() < deadline:
        for event in _read_events(task / "events.ndjson"):
            sequence = event.get("sequence")
            if isinstance(sequence, int) and sequence > last_sequence:
                last_sequence = sequence
                if on_event:
                    on_event(event)
        try:
            result = _read_json(task / "result.json")
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            result = None
        if isinstance(result, dict):
            if result.get("protocolVersion") != PROTOCOL_VERSION or result.get("requestId") != request_id:
                raise PasteError("Agent Bridge result does not match this request")
            if result.get("status") not in {"completed", "failed"}:
                raise PasteError("Agent Bridge result has an invalid status")
            return result
        time.sleep(0.2)
    raise PasteError(f"Timed out waiting for request {request_id}; inspect {task}")


def execute_request(
    location: BridgeLocation,
    request: Mapping[str, Any],
    timeout_seconds: float,
    on_event: Callable[[Mapping[str, Any]], None] | None = None,
) -> dict[str, Any]:
    require_fresh_heartbeat(location)
    publish_request(location, request)
    result = wait_for_result(location, str(request["requestId"]), timeout_seconds, on_event)
    if result.get("status") == "failed":
        failure = result.get("failure")
        code = failure.get("code") if isinstance(failure, dict) else "PASTE_FAILED"
        message = failure.get("message") if isinstance(failure, dict) else "Agent Bridge paste failed"
        completed = result.get("completedItems")
        count = len(completed) if isinstance(completed, list) else 0
        raise PasteError(f"{code}: {message} ({count} item(s) completed before failure)")
    return result


def _progress(event: Mapping[str, Any]) -> None:
    completed, total = event.get("completed"), event.get("total")
    progress = f" [{completed}/{total}]" if isinstance(completed, int) and isinstance(total, int) else ""
    print(f"{event.get('type', 'event')}{progress}: {event.get('message', '')}", file=sys.stderr)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sources", nargs="+", type=Path, help="Markdown files or directories to scan recursively")
    parser.add_argument("--notebook", required=True, help="Target SiYuan notebook ID")
    parser.add_argument("--directory", required=True, help="Target human directory path")
    titles = parser.add_mutually_exclusive_group()
    titles.add_argument("--title", help="Explicit title when exactly one Markdown file is selected")
    titles.add_argument("--title-map", type=Path, help="JSON object mapping Markdown paths or filenames to titles")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT, help="SiYuan kernel endpoint")
    parser.add_argument("--timeout", type=float, default=600.0, help="Seconds to wait for the batch")
    parser.add_argument("--dry-run", action="store_true", help="Print the request without writing to SiYuan")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.timeout <= 0:
            raise PasteError("--timeout must be greater than zero")
        sources = collect_markdown_sources(args.sources)
        title_mapping = None
        if args.title_map:
            map_path = args.title_map.resolve()
            title_mapping = resolve_title_map(sources, load_title_map(map_path), map_path)
        titles = select_titles(sources, args.title, title_mapping)
        request = build_request(sources, args.notebook, args.directory, titles)
        if args.dry_run:
            print(json.dumps(request, ensure_ascii=False, indent=2))
            return 0
        result = execute_request(discover_bridge(args.endpoint), request, args.timeout, _progress)
    except PasteError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    receipts = result.get("completedItems")
    if not isinstance(receipts, list) or len(receipts) != len(request["items"]):
        print("error: Agent Bridge returned an incomplete success receipt", file=sys.stderr)
        return 2
    print(f"Pasted {len(receipts)} Markdown document(s) into SiYuan.")
    if snapshot := result.get("snapshotId"):
        print(f"Snapshot: {snapshot}")
    for receipt in receipts:
        if isinstance(receipt, dict):
            print(f"{receipt.get('documentId', '')}\t{receipt.get('targetPath', '')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
