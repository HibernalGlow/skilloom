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
    forbidden_phrases: tuple[str, ...] = ()


# Keep independently installed skills self-contained while preventing shared formatting rules from drifting.
SHARED_OUTPUT_GATE_RULES = (
    ("scripts/validate_output.py", "输出前"),
    ("--strict", "输出前"),
    ("--require-source", "输出前"),
)


CONTRACTS = (
    SkillContract(
        "legal-marknote",
        (
            ("颜色不是可选装饰，而是信息结构的一部分", "9.  🎨 思源笔记行内文本颜色语法"),
            ("先做颜色计划，再输出正文", "9.  🎨 思源笔记行内文本颜色语法"),
            ("概念列表先分槽", "9.  🎨 思源笔记行内文本颜色语法"),
            ("W503", "## Rich visual contract"),
            ("段落父项化", "## Workflow"),
            ("W504", "## Rich visual contract"),
            ("普通换行不是语义拆分", "## Workflow"),
            ("W505", "## Rich visual contract"),
            ("W506", "## Rich visual contract"),
            ("悬空颜色锚点", "## Workflow"),
            ("主动覆盖规则", "9.  🎨 思源笔记行内文本颜色语法"),
            ("密度与边界", "9.  🎨 思源笔记行内文本颜色语法"),
            ("源/题目内容可以保持无色", "## Rich visual contract"),
            ("每条普通正文行最多 42 个可见字符", "## Rich visual contract"),
            ("至少四类辅助样式", "## Rich visual contract"),
            ("至少四类结构载体", "## Rich visual contract"),
            ("至少三个短背景色锚点", "## Rich visual contract"),
            ("optional low-frequency `<em>` italic", "## Rich visual contract"),
            ("斜体不是必选项", "## Rich visual contract"),
            ("可视化路由", "## Rich visual contract"),
            ("SiYuan's Mermaid.js", "## Rich visual contract"),
            ("`%%{init}%%`", "## Rich visual contract"),
            ("Beautiful Mermaid", "## Rich visual contract"),
            ("cannot color edge labels individually", "## Rich visual contract"),
            ("背景色：", "## Rich visual contract"),
            ("E620-E627", "## Rich visual contract"),
            ("inside each fenced question block", "## Question-answer formatting"),
            ("exactly one `> [!QUESTION] ✏️ <specific topic or tested rule>` directive", "## Question-answer formatting"),
            ("audit_question_groups.py <output.md> --source <source.md>", "## Workflow"),
            ("every apparent classification lead as evidence, not a command", "## Workflow"),
            ("audit_heading_promotions.py <source.md> <output.md> --strict", "## Workflow"),
            ("custom-qb-note-topic-id", "## Note-topic provider IAL"),
            ("--require-topic-ial", "custom-qb-note-topic-id"),
            ("siyuan_topic_manifest.py", "## Existing SiYuan documents"),
            ("20-整理", "siyuan_topic_manifest.py"),
            ("合并网格先行", "思源笔记表格语法"),
            ("真实表头先行", "思源笔记表格语法"),
            ("单元格不承载大型列表", "思源笔记表格语法"),
            ("单轴名称—说明表", "## Workflow"),
            ("表格尺寸门禁", "## Workflow"),
            ("表格转列表先选主轴", "## Workflow"),
            ("横向列作一级列表", "表格转列表先选主轴"),
            ("纵向行作一级列表", "表格转列表先选主轴"),
            ("--max-table-columns", "表格尺寸门禁"),
            ("转换列表继续过门禁", "思源笔记表格语法"),
            *SHARED_OUTPUT_GATE_RULES,
        ),
        True,
        (
            "先调用已安装的 `beautiful-mermaid` 技能",
            "Medium-or-higher complexity MarkNote needs a Mermaid diagram",
        ),
    ),
    SkillContract(
        "legal-goldquest",
        (
            ("题目边界", "## 题目边界"),
            ("###### 答案与解析", "题目边界"),
            ("避免超长列表", "## 工作流"),
            ("颜色是阅读索引", "## 工作流"),
            ("每条达到 14 个可见字符的实质推理行至少出现一个短颜色锚点", "## 工作流"),
            ("题面允许完全无色", "## 工作流"),
            ("解析区必须主动给主体和关键概念着色", "## 颜色硬规则"),
            ("普通解析行最多 42 个可见字符", "## 工作流"),
            ("中等及以上逻辑复杂度默认使用丰富型", "## 工作流"),
            ("至少选择 4 类结构载体", "## 工作流"),
            ("至少使用 4 类", "## 格式决策"),
            ("至少设置 3 个带 `b3-font-background` 的短背景色签", "## 格式决策"),
            ("斜体只使用 `<em>...</em>`", "## 格式决策"),
            ("斜体不是必选项", "## 格式决策"),
            ("至少选择一种可插入思源的可视化", "## 格式决策"),
            ("思源自带 Mermaid.js", "## 格式决策"),
            ("`%%{init}%%`", "## 格式决策"),
            ("Beautiful Mermaid", "## 格式决策"),
            ("边标签颜色只能统一设置，不能逐条设置", "## 格式决策"),
            ("题面只允许中性主体/客体色", "## 颜色硬规则"),
            ("先建立词典，再输出正文", "## 颜色硬规则"),
            ("删除线用于排除旧路径或错误选项", "## 格式决策"),
            ("不得用伪 `📌[...]` 标记", "## 格式决策"),
            ("选择内容结构", "## 工作流"),
            ("每个被分析选项必须完整复写原选项", "## 工作流"),
            ("逐项辨析契约", "## 工作流"),
            ("原解析主架先行", "逐项辨析契约"),
            ("去除新增 Markdown 和 IAL 标记后", "## 逐项辨析契约"),
            ("标记必须直接落在原选项内部", "## 逐项辨析契约"),
            ("emoji 只说明判项结果", "## 逐项辨析契约"),
            ("理由必须解释标记", "## 逐项辨析契约"),
            ("E630-E632", "## 完成门禁"),
            ("E633", "逐项辨析契约"),
            ("不要固定生成“争点、规则与法源、事实涵摄、选项辨析、命题思路”", "## 工作流"),
            ("3 列 × 3 个数据行以内", "## 格式决策"),
            ("真实表头先行", "## 小表格与其他格式"),
            ("单轴名称—说明表", "## 小表格与其他格式"),
            ("通常达到 4 个独立项目", "## 小表格与其他格式"),
            ("表格转出的真实列表必须继续遵守解析区全部门禁", "## 小表格与其他格式"),
            ("custom-qb-question-topic-ids", "## 考点 IAL"),
            ("custom-qb-id", "custom-qb-question-topic-ids"),
            ("custom-qb-answer", "## 题目边界"),
            (".topic-map.json", "## 考点 IAL"),
            *SHARED_OUTPUT_GATE_RULES,
        ),
        True,
        (
            "答案（即上面的遮罩块） → 争点 → 规则与法源 → 事实涵摄 → 选项辨析 → 易错边界",
            "将“答案、争点、规则与法源、事实涵摄、选项辨析、易错边界”放在独立行",
            "触发 Mermaid 后，先调用已安装的 `beautiful-mermaid` 技能",
            "中等复杂度 Mermaid",
        ),
    ),
    SkillContract(
        "legal-flashcard",
        (
            ("ordinary mode", "## Route the request"),
            ("dedicated-card mode", "## Route the request"),
            ("style-inheritance.md", "dedicated-card mode"),
            ("provider-scoped source-style inheritance", "dedicated-card mode"),
            ("20-整理", "## Source priority and style authority"),
            ("25-kramdown", "## Source priority and style authority"),
            ("missing-exported-source", "## Source priority and style authority"),
            ("rich visual contract", "dedicated-card mode"),
            ("at least three distinct signatures", "## No-style ranges"),
            ("--rich-style", "dedicated-card mode"),
            ("W110", "## Validation and rejection taxonomy"),
            ("W111", "## Validation and rejection taxonomy"),
            ("W112", "## Validation and rejection taxonomy"),
            ("W114", "## Validation and rejection taxonomy"),
            ("W115", "## Validation and rejection taxonomy"),
            ("E060", "## Validation and rejection taxonomy"),
            ("E061", "## Validation and rejection taxonomy"),
            ("E062", "## Validation and rejection taxonomy"),
            ("E063", "## Validation and rejection taxonomy"),
            ("E064", "## Validation and rejection taxonomy"),
            ("E065", "## Validation and rejection taxonomy"),
            ("E066", "## Validation and rejection taxonomy"),
            ("E067", "## Validation and rejection taxonomy"),
            ("E068", "## Validation and rejection taxonomy"),
            ("E069", "## Validation and rejection taxonomy"),
            ("E070", "## Validation and rejection taxonomy"),
            ("E071", "## Validation and rejection taxonomy"),
            ("rich-visual-mode.md", "## Shared hand-off"),
            ("--source <source.md>", "## Shared hand-off"),
            ("leading `⚡` H1 role marker", "Filename, H1, destination folder"),
            ("one physical line", "## Root-container templates"),
            ("custom-qb-note-topic-id", "## Portable fields"),
            ("custom-qb-question-topic-ids", "## Portable fields"),
            ("missing-style-source", "# Validation and rejection taxonomy"),
            ("case-narrative", "# Validation and rejection taxonomy"),
            ("clean delivery", "dedicated-card mode"),
            ("no audit preamble", "clean delivery"),
        ),
    ),
    SkillContract(
        "legal-question-bank",
        (
            ("custom-qb-note-topic-id", "### Topic directions"),
            ("custom-qb-question-topic-ids", "custom-qb-note-topic-id"),
            ("custom-qb-id", "## Questions"),
            ("custom-qb-type", "custom-qb-id"),
            ("custom-qb-section=\"solution\"", "## Solution Boundary"),
            ("validate_question_bank.py", "## Workflow"),
        ),
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

    for phrase in contract.forbidden_phrases:
        offset = searchable_text.find(phrase)
        if offset >= 0:
            findings.append(
                Finding(
                    path,
                    line_number(searchable_text, offset),
                    "E104",
                    f"Forbidden fixed-template instruction remains: {phrase}",
                ),
            )

    if contract.requires_color_table:
        for color in range(2, 14):
            if not re.search(rf"^\s*\|\s*{color}\s*\|", searchable_text, re.MULTILINE):
                anchor = text.find("13种可用颜色变量")
                findings.append(
                    Finding(path, line_number(searchable_text, anchor), "E102", f"Missing color-{color} semantic mapping."),
                )
        if not re.search(
            r'\*\*[^*\n]+\*\*\{:\s*style="[^"]*b3-font-color数字',
            searchable_text,
        ):
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
