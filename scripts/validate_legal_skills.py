#!/usr/bin/env python3
"""Validate the local legal-study skill contracts with line-local diagnostics."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SkillContract:
    directory: str
    required_rules: tuple[tuple[str, str], ...]
    requires_color_table: bool = False


# Keep independently installed skills self-contained while preventing shared formatting rules from drifting.
SHARED_TABLE_RULES = (
    ("枚举项强制软换行", "表格绝对保留"),
    ("表格单元格排版", "表格绝对保留"),
)


CONTRACTS = (
    SkillContract(
        "legal-marknote",
        (
            ("颜色不是可选装饰，而是信息结构的一部分", "9.  🎨 思源笔记行内文本颜色语法"),
            ("先做颜色计划，再输出正文", "9.  🎨 思源笔记行内文本颜色语法"),
            ("主动覆盖规则", "9.  🎨 思源笔记行内文本颜色语法"),
            ("密度与边界", "9.  🎨 思源笔记行内文本颜色语法"),
            *SHARED_TABLE_RULES,
        ),
        True,
    ),
    SkillContract(
        "legal-goldquest",
        (
            ("题目区域", "1. 标题结构与原格式保持"),
            ("###### 答案与解析", "习题格式规范"),
            ("禁止大块文本", "2. 闪卡化表述与隐形提示法"),
            ("颜色是必做的阅读索引", "7. 🎨 思源笔记行内文本颜色语法"),
            ("题面边界", "7. 🎨 思源笔记行内文本颜色语法"),
            ("主动使用检查", "7. 🎨 思源笔记行内文本颜色语法"),
            *SHARED_TABLE_RULES,
        ),
        True,
    ),
    SkillContract(
        "legal-imagen",
        (
            ("标准输出格式", "五、输出格式规范"),
            ("质量控制", "六、使用建议"),
            ("颜色编码系统", "七、高级技巧"),
        ),
    ),
)


@dataclass(frozen=True)
class Finding:
    path: Path
    line: int
    code: str
    message: str

    def render(self) -> str:
        return f"{self.path}:{self.line}: {self.code}: {self.message}"


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, max(offset, 0)) + 1


def first_line(lines: list[str], matcher: re.Pattern[str]) -> int | None:
    for number, line in enumerate(lines, start=1):
        if matcher.search(line):
            return number
    return None


def validate_frontmatter(path: Path, text: str, expected_name: str) -> list[Finding]:
    findings: list[Finding] = []
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return [Finding(path, 1, "E001", "SKILL.md must start with YAML frontmatter delimiter '---'.")]

    try:
        close_line = lines.index("---", 1)
    except ValueError:
        return [Finding(path, 1, "E002", "YAML frontmatter has no closing '---' delimiter.")]

    frontmatter = lines[1:close_line]
    name_line = first_line(frontmatter, re.compile(r"^name:\s*"))
    if name_line is None:
        findings.append(Finding(path, 2, "E003", "Frontmatter must declare the skill name."))
    elif frontmatter[name_line - 1].removeprefix("name:").strip() != expected_name:
        findings.append(
            Finding(path, name_line + 1, "E004", f"Expected name: {expected_name}."),
        )

    description_line = first_line(frontmatter, re.compile(r"^description:\s*\S"))
    if description_line is None:
        findings.append(Finding(path, 2, "E005", "Frontmatter must declare a non-empty description."))
    return findings


def validate_contract(path: Path, contract: SkillContract) -> list[Finding]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        return [
            Finding(
                path,
                line_number(path.read_bytes().decode("utf-8", errors="replace"), error.start),
                "E006",
                "SKILL.md must be valid UTF-8.",
            ),
        ]

    findings = validate_frontmatter(path, text, contract.directory)
    searchable_text = text
    for reference in sorted(path.parent.rglob("*.md")):
        if reference == path:
            continue
        try:
            searchable_text += "\n" + reference.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            findings.append(Finding(reference, 1, "E007", "Markdown references must be valid UTF-8."))
    for phrase, anchor in contract.required_rules:
        if phrase not in searchable_text:
            anchor_offset = searchable_text.find(anchor)
            findings.append(
                Finding(
                    path,
                    line_number(searchable_text, anchor_offset),
                    "E101",
                    f"Missing required contract near this section: {phrase}",
                ),
            )

    if contract.requires_color_table:
        for color in range(2, 14):
            if not re.search(rf"^\s*\|\s*{color}\s*\|", searchable_text, re.MULTILINE):
                anchor = text.find("13种可用颜色变量")
                findings.append(
                    Finding(path, line_number(searchable_text, anchor), "E102", f"Missing color-{color} semantic mapping."),
                )
        if "**文本内容**{: style=\"color: var(--b3-font-color数字);" not in searchable_text:
            anchor = searchable_text.find("思源笔记行内文本颜色语法")
            findings.append(
                Finding(
                    path,
                    line_number(searchable_text, anchor),
                    "E103",
                    "Missing the canonical bold-first Siyuan color syntax example.",
                ),
            )
    return findings


def run_generic_validator(validator: Path, directories: list[Path]) -> int:
    result_code = 0
    for directory in directories:
        result = subprocess.run(
            [sys.executable, "-X", "utf8", str(validator), str(directory)],
            text=True,
            capture_output=True,
        )
        output = (result.stdout + result.stderr).strip()
        if result.returncode:
            result_code = 1
            print(f"{directory / 'SKILL.md'}:1: E200: Generic skill validation failed: {output}")
        elif output:
            print(f"PASS generic {directory.name}: {output}")
    return result_code


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--quick-validator",
        type=Path,
        default=os.environ.get("SKILL_CREATOR_QUICK_VALIDATE"),
        help="Path to skill-creator's existing quick_validate.py. May also be set with SKILL_CREATOR_QUICK_VALIDATE.",
    )
    parser.add_argument(
        "--skills-root",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "skills",
        help="Directory containing the legal skill folders.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    directories = [args.skills_root / contract.directory for contract in CONTRACTS]
    findings: list[Finding] = []
    for contract, directory in zip(CONTRACTS, directories, strict=True):
        skill_md = directory / "SKILL.md"
        if not skill_md.exists():
            findings.append(Finding(skill_md, 1, "E000", "Required skill file is missing."))
            continue
        findings.extend(validate_contract(skill_md, contract))

    for finding in findings:
        print(finding.render())
    if findings:
        return 1

    generic_validator = Path(args.quick_validator) if args.quick_validator else None
    if generic_validator is None:
        print("PASS legal contracts (generic validation skipped; set SKILL_CREATOR_QUICK_VALIDATE to enable it).")
        return 0
    if not generic_validator.is_file():
        print(f"{generic_validator}:1: E201: quick_validate.py was not found.")
        return 1
    generic_status = run_generic_validator(generic_validator, directories)
    if generic_status:
        return generic_status
    print("PASS legal contracts and generic skill validation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
