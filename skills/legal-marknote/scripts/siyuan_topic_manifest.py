#!/usr/bin/env python3
"""Export a SiYuan heading/topic manifest and safely apply note-topic IAL attributes."""
# ==========================================================================
# ⛔ 内容会话禁读本源码（用户纪律 2026-09-02）
#    校验器源码不供阅读。判定标准与修法的唯一权威渠道：
#    技能正文 + references/ + 运行本工具得到的真实报错
#    （goldquest 校验器另有 --explain <CODE> 权威词条，如 --explain E630）。
#    打开/grep/sed/脚本方式读取本文件属违规——包括动笔前的预防性阅读，
#    会被看护发现并上报用户。看不懂的报错：原样报告错误码与文本，等用户解释。
# ==========================================================================

from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


NODE_ID = re.compile(r"^\d{14}-[a-z0-9]{7}$")
TOPIC_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
TOPIC_ATTR = "custom-qb-note-topic-id"
SCHEMA_VERSION = 1


class ManifestError(RuntimeError):
    pass


@dataclass(frozen=True)
class CommandResult:
    stdout: str


Runner = Callable[[list[str]], CommandResult]


def default_runner(arguments: list[str]) -> CommandResult:
    result = subprocess.run(arguments, check=False, capture_output=True, text=True, encoding="utf-8")
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit code {result.returncode}"
        raise ManifestError(f"Command failed: {' '.join(arguments)}\n{detail}")
    return CommandResult(result.stdout)


def run_json(runner: Runner, arguments: list[str]) -> Any:
    output = runner(arguments).stdout.strip()
    try:
        return json.loads(output)
    except json.JSONDecodeError as error:
        raise ManifestError(f"Command did not return JSON: {' '.join(arguments)}") from error


def clean_title(value: str) -> str:
    value = html.unescape(re.sub(r"<[^>]+>", "", value))
    return re.sub(r"\s+", " ", value).strip()


def outline_entries(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []

    def visit(node: dict[str, Any], parents: list[str]) -> None:
        block_id = str(node.get("id", ""))
        title = clean_title(str(node.get("content") or node.get("name") or ""))
        subtype = str(node.get("subType") or "")
        level_match = re.fullmatch(r"h([1-6])", subtype)
        if NODE_ID.fullmatch(block_id) and title and level_match:
            path = [*parents, title]
            entries.append({
                "block_id": block_id,
                "level": int(level_match.group(1)),
                "title": title,
                "heading_path": path,
                "quick_link": f"siyuan://blocks/{block_id}",
            })
            child_parents = path
        else:
            child_parents = parents
        children = node.get("blocks") or node.get("children") or []
        if isinstance(children, list):
            for child in children:
                if isinstance(child, dict):
                    visit(child, child_parents)

    for root in nodes:
        if isinstance(root, dict):
            visit(root, [])
    return entries


def chunked(values: list[str], size: int = 80) -> list[list[str]]:
    return [values[index:index + size] for index in range(0, len(values), size)]


def batch_attrs(runner: Runner, base: list[str], block_ids: list[str]) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for group in chunked(block_ids):
        payload = run_json(runner, [*base, "attr", "batch-get", "--ids", ",".join(group), "-f", "json"])
        if not isinstance(payload, dict):
            raise ManifestError("SiYuan attr batch-get returned an unexpected shape.")
        for block_id, attributes in payload.items():
            if isinstance(attributes, dict):
                result[str(block_id)] = {str(key): str(value) for key, value in attributes.items()}
    return result


def manifest_paths(args: argparse.Namespace) -> tuple[Path, Path]:
    if args.output_json:
        json_path = args.output_json
    elif args.organized_file:
        json_path = args.organized_file.with_name(f"{args.organized_file.stem}.topic-map.json")
    else:
        raise ManifestError("Export requires --output-json or --organized-file.")
    return json_path, json_path.with_suffix(".md")


def render_markdown(manifest: dict[str, Any]) -> str:
    document = manifest["document"]
    lines = [
        f"# {document.get('title') or document['id']} 考点映射",
        "",
        f"- 思源文档：[{document.get('hpath') or document['id']}](siyuan://blocks/{document['id']})",
        f"- 属性：`{TOPIC_ATTR}`",
        f"- JSON：`{manifest['manifest_file']}`",
        "",
        "## 标题块",
        "",
    ]
    for entry in manifest["entries"]:
        indent = "    " * max(entry["level"] - 1, 0)
        current = entry.get("current_topic_id") or "未设置"
        planned = entry.get("topic_id") or "未设置"
        action = entry.get("action", "skip")
        lines.append(
            f"{indent}- H{entry['level']} [{entry['title']}]({entry['quick_link']}) "
            f"· `{entry['block_id']}` · 当前 `{current}` · 计划 `{action}:{planned}`"
        )
    lines.extend([
        "",
        "> 编辑 JSON 中各条目的 `action` 与 `topic_id`；Markdown 文件只用于浏览和快速跳转。",
        "",
    ])
    return "\n".join(lines)


def export_manifest(args: argparse.Namespace, runner: Runner = default_runner) -> int:
    if not NODE_ID.fullmatch(args.document_id):
        raise ManifestError("--document-id must be a valid SiYuan block ID.")
    base = [args.siyuan_command, "-w", str(args.workspace)]
    document = run_json(runner, [*base, "document", "get", "--id", args.document_id, "-f", "json"])
    outline = run_json(runner, [*base, "outline", "get", "--id", args.document_id, "-f", "json"])
    if not isinstance(document, dict) or not isinstance(outline, list):
        raise ManifestError("SiYuan document/outline output has an unexpected shape.")
    entries = outline_entries(outline)
    if not entries:
        raise ManifestError("The document outline contains no heading blocks.")
    attributes = batch_attrs(runner, base, [entry["block_id"] for entry in entries])
    for entry in entries:
        current = attributes.get(entry["block_id"], {})
        entry["current_topic_id"] = current.get(TOPIC_ATTR, "")
        entry["exported_updated"] = current.get("updated", "")
        entry["action"] = "skip"
        entry["topic_id"] = current.get(TOPIC_ATTR, "")

    json_path, markdown_path = manifest_paths(args)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workspace": str(args.workspace),
        "attribute": TOPIC_ATTR,
        "manifest_file": json_path.name,
        "document": {
            "id": args.document_id,
            "title": clean_title(str(document.get("content") or document.get("title") or "")),
            "hpath": str(document.get("hPath") or document.get("hpath") or ""),
            "notebook_id": str(document.get("box") or ""),
        },
        "entries": entries,
    }
    json_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(manifest), encoding="utf-8")
    print(f"EXPORTED {len(entries)} headings")
    print(f"JSON {json_path}")
    print(f"MARKDOWN {markdown_path}")
    return 0


def load_manifest(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("schema_version") != SCHEMA_VERSION:
        raise ManifestError(f"Unsupported manifest schema in {path}.")
    if payload.get("attribute") != TOPIC_ATTR or not isinstance(payload.get("entries"), list):
        raise ManifestError(f"Invalid topic manifest contract in {path}.")
    return payload


def planned_entries(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    planned: list[dict[str, Any]] = []
    seen: set[str] = set()
    for entry in manifest["entries"]:
        if not isinstance(entry, dict):
            raise ManifestError("Manifest entries must be objects.")
        action = entry.get("action", "skip")
        if action == "skip":
            continue
        if action not in {"set", "delete"}:
            raise ManifestError(f"Unknown action for {entry.get('block_id')}: {action}")
        block_id = str(entry.get("block_id", ""))
        if not NODE_ID.fullmatch(block_id) or block_id in seen:
            raise ManifestError(f"Invalid or duplicate block ID: {block_id}")
        seen.add(block_id)
        topic_id = str(entry.get("topic_id", ""))
        if action == "set" and not TOPIC_ID.fullmatch(topic_id):
            raise ManifestError(f"Invalid topic ID for {block_id}: {topic_id}")
        planned.append(entry)
    return planned


def apply_manifest(args: argparse.Namespace, runner: Runner = default_runner) -> int:
    manifest = load_manifest(args.manifest)
    markdown_path = args.manifest.with_suffix(".md")
    markdown_path.write_text(render_markdown(manifest), encoding="utf-8")
    planned = planned_entries(manifest)
    workspace = args.workspace or Path(str(manifest.get("workspace", "")))
    if not str(workspace):
        raise ManifestError("Apply requires --workspace or a workspace recorded in the manifest.")
    base = [args.siyuan_command, "-w", str(workspace)]
    current = batch_attrs(runner, base, [str(entry["block_id"]) for entry in planned])
    preflight: list[dict[str, Any]] = []
    errors: list[str] = []

    for entry in planned:
        block_id = str(entry["block_id"])
        attrs = current.get(block_id)
        if attrs is None:
            errors.append(f"Missing block: {block_id}")
            continue
        exported_updated = str(entry.get("exported_updated", ""))
        if exported_updated and attrs.get("updated", "") != exported_updated and not args.allow_stale:
            errors.append(f"Stale block: {block_id} was updated after export")
        exported_topic = str(entry.get("current_topic_id", ""))
        live_topic = attrs.get(TOPIC_ATTR, "")
        if live_topic != exported_topic and args.on_conflict == "abort":
            errors.append(f"Topic conflict: {block_id} exported='{exported_topic}' live='{live_topic}'")
        if live_topic != exported_topic and args.on_conflict == "keep":
            continue
        target = str(entry.get("topic_id", "")) if entry["action"] == "set" else ""
        preserved_attrs = {key: value for key, value in attrs.items() if key not in {TOPIC_ATTR, "updated"}}
        preflight.append({
            "block_id": block_id,
            "action": entry["action"],
            "before": live_topic,
            "after": target,
            "preserved_attrs": preserved_attrs,
        })

    if errors:
        raise ManifestError("Preflight failed:\n" + "\n".join(f"- {error}" for error in errors))
    preview = [{key: value for key, value in item.items() if key != "preserved_attrs"} for item in preflight]
    print(json.dumps({"planned": preview}, ensure_ascii=False, indent=2))
    if not args.confirm:
        print("PREVIEW ONLY: rerun with --confirm after reviewing the plan.")
        return 0

    result_path = args.manifest.with_name(f"{args.manifest.stem}.apply-result.json")
    results: list[dict[str, Any]] = []

    def write_result(status: str, error: str = "") -> None:
        result_path.write_text(json.dumps({
            "status": status,
            "applied_at": datetime.now(timezone.utc).isoformat(),
            "manifest": str(args.manifest),
            "error": error,
            "results": results,
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    for item in preflight:
        try:
            runner([*base, "attr", "set", "--id", item["block_id"], "--attr", f"{TOPIC_ATTR}={item['after']}"])
            verified_attrs = batch_attrs(runner, base, [item["block_id"]]).get(item["block_id"], {})
            verified = verified_attrs.get(TOPIC_ATTR, "")
            if verified != item["after"]:
                raise ManifestError(f"Verification failed for {item['block_id']}: expected '{item['after']}', got '{verified}'")
            changed_unrelated = {
                key: {"before": value, "after": verified_attrs.get(key)}
                for key, value in item["preserved_attrs"].items()
                if verified_attrs.get(key) != value
            }
            if changed_unrelated:
                raise ManifestError(f"Unrelated attributes changed for {item['block_id']}: {changed_unrelated}")
            result_item = {key: value for key, value in item.items() if key != "preserved_attrs"}
            results.append({**result_item, "verified": True})
            entry = next(candidate for candidate in manifest["entries"] if candidate["block_id"] == item["block_id"])
            entry["current_topic_id"] = verified
            entry["exported_updated"] = verified_attrs.get("updated", entry.get("exported_updated", ""))
            entry["topic_id"] = verified
            entry["action"] = "skip"
            write_result("partial")
        except (ManifestError, OSError) as error:
            write_result("partial", str(error))
            raise

    args.manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(manifest), encoding="utf-8")
    write_result("complete")
    print(f"APPLIED {len(results)} attributes")
    print(f"RESULT {result_path}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--siyuan-command", default="siyuan")
    subparsers = parser.add_subparsers(dest="command", required=True)

    export = subparsers.add_parser("export", help="Export heading IDs and current topic attributes.")
    export.add_argument("--workspace", type=Path, required=True)
    export.add_argument("--document-id", required=True)
    export.add_argument("--organized-file", type=Path, help="Save the manifest beside this 20-organized Markdown file.")
    export.add_argument("--output-json", type=Path)

    apply = subparsers.add_parser("apply", help="Preview or apply topic attributes from a manifest.")
    apply.add_argument("manifest", type=Path)
    apply.add_argument("--workspace", type=Path)
    apply.add_argument("--confirm", action="store_true")
    apply.add_argument("--allow-stale", action="store_true")
    apply.add_argument("--on-conflict", choices=("abort", "keep", "overwrite"), default="abort")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.command == "export":
            return export_manifest(args)
        return apply_manifest(args)
    except (ManifestError, OSError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
