#!/usr/bin/env python3
"""cc-1 错题 Case 卡的结构门禁（`references/case-card.md`）。

三条门禁都对应"看起来正常、实际坏掉"的形状，纯文本判定，不改内容：

- `E136` 答案标记行被着色：`- 正确答案：ABC。` 里出现 `{: style=}` 内联样式后，
  Damophus 的 `isLikelySolutionStart` 按字面文本判分界会失败，整题从题库索引消失
  （`missing-solution-boundary`），闪卡侧却完全看不出异常。
- `E137` Case 卡缺件：卡体里既有 `> [!SELECTION]` 选项载体又找不到 `cc:` 元数据块
  （或反过来），说明双形态只做了一半——要么题库认不到选项，要么错题身份不可见。
- `E138` 载体跑到正面：`list` 卡的背面是根项的直接子列表，缩进不到子列表内容列的
  围栏/图片会成为根项的直接子块，SiYuan 的 `--hideli` 只隐藏 `.li > .list`，
  于是 Mermaid、动图和 `cc:` 块在翻面之前就露出来（答案泄漏）。
"""

from __future__ import annotations

import re

CARD_IAL = re.compile(r"^\{: custom-dm-")
ANSWER_MARKER = re.compile(r"^\s*(?:>\s*)?-\s*(?:\*\*)?正确答案")
STYLE_IAL = re.compile(r"\{: style=")
SELECTION = re.compile(r"^\s*>\s*\[!SELECTION\]", re.IGNORECASE)
OPTION_ITEM = re.compile(r"^\s*>\s*-\s+\[[ xX]\]\s+\S")
CC_BLOCK = re.compile(r"^\s*cc:\s*$")
LIST_ITEM = re.compile(r"^(?P<indent> *)(?P<marker>-|\*|\d+[.)])(?P<gap>[ ]+)\S")
# 一段推理的三个槽位属于同一轴，按契约就是并列子项，不算“墙”
REASONING_LABEL = re.compile(
    r"^\s*(?:>\s*)?(?:-|\*|\d+[.)])\s+\*{0,2}(?:大前提|小前提|结论|推论|涵摄|补强|规则|例外|本案|关键|前提|判断链)")
WALL_RUN = 4
_WALL_LINES: list[str] = []


def card_blocks(lines: list[str]) -> list[tuple[int, int, dict[str, str]]]:
    """Yield (start, end, attributes) for each card block ending at its root IAL line."""
    blocks: list[tuple[int, int, dict[str, str]]] = []
    for index, line in enumerate(lines):
        if not CARD_IAL.match(line):
            continue
        attributes = dict(re.findall(r'([A-Za-z][\w-]*)="([^"]*)"', line))
        start, root = index - 1, None
        while start >= 0:
            line = lines[start]
            if CARD_IAL.match(line) or re.match(r"^#{1,6}\s", line):
                break
            if root is None and re.match(r"^-\s", line):
                root = start
            start -= 1
        blocks.append((root if root is not None else start + 1, index, attributes))
    return blocks


def find_styled_answer_markers(lines: list[str]) -> list[tuple[int, str]]:
    """Answer-marker lines carrying inline styles: the question bank loses the boundary.

    The match runs on markup-stripped text, because the failure mode is exactly a style
    inserted inside the marker (`**正确**{: style=..}答案：A。`).
    """
    findings: list[tuple[int, str]] = []
    for index, line in enumerate(lines):
        if not STYLE_IAL.search(line):
            continue
        plain = re.sub(r"\{: [^}\n]*\}", "", line).replace("*", "")
        if ANSWER_MARKER.match(plain):
            findings.append((index + 1, line.strip()))
    return findings


def find_case_card_gaps(lines: list[str]) -> list[tuple[int, str]]:
    """cc-1 cards missing either the option carrier or the visible Case identity block."""
    gaps: list[tuple[int, str]] = []
    for start, end, attributes in card_blocks(lines):
        if attributes.get("custom-dm-card-renderer") != "list":
            continue
        body = lines[start:end]
        carrier = any(SELECTION.match(line) for line in body)
        options = sum(1 for line in body if OPTION_ITEM.match(line))
        identity = any(CC_BLOCK.match(line) for line in body)
        has_variant = any(re.match(r"^\s*variant:\s*\S", line) for line in body)
        has_verified = any(re.match(r"^\s*verified:\s*\S", line) for line in body)
        if identity and not carrier:
            gaps.append((start + 1, "Case 卡缺 `> [!SELECTION]` 选项载体：选项若作裸子列表会被当成背面"))
        elif identity and options < 2:
            gaps.append((start + 1, f"选项载体里只有 {options} 个 `- [ ]` 项，题库判分需要完整原选项"))
        elif identity and not (has_variant and has_verified):
            gaps.append((start + 1, "Case 卡的 `cc:` 块缺 `variant` 或 `verified`：换皮题干必须记下改了什么并声明已遮答案重做"))
        elif carrier and not identity:
            gaps.append((start + 1, "有 SELECTION 载体却没有背面可见的 `cc:` 元数据块，错题身份不可见"))
    return gaps


def find_front_leaks(lines: list[str]) -> list[tuple[int, str]]:
    """Fences and images that start left of the answer items' content column (E138).

    The bound is computed, never hard-coded: a child block must start at or to the right of
    its parent item's content column (marker column + marker width + the gap after the
    marker). Answer items at column 4 therefore need ` ```mermaid `/` ```yml `/image at column
    6 or deeper; a deeper back nesting needs deeper indentation. Anything shallower becomes a
    direct child of the root item and SiYuan leaves it visible on the front.
    """
    leaks: list[tuple[int, str]] = []
    for start, end, attributes in card_blocks(lines):
        if attributes.get("custom-dm-card-renderer") != "list":
            continue
        body = lines[start:end]
        root = LIST_ITEM.match(body[0]) if body else None
        root_column = len(root.group("indent")) if root else 0
        columns = [len(match.group("indent")) + len(match.group("marker")) + len(match.group("gap"))
                   for line in body[1:] if (match := LIST_ITEM.match(line)) and line.strip()
                   and len(match.group("indent")) > root_column]
        if not columns:
            continue
        content_column = min(columns)
        in_fence = False
        for offset, line in enumerate(body):
            fence_open = re.match(r"^(?P<indent>\s*)(?:>\s*)?```", line)
            if fence_open:
                if not in_fence and len(fence_open.group("indent")) < content_column:
                    leaks.append((start + offset + 1,
                                  f"围栏起始列 {len(fence_open.group('indent'))} 小于背面项内容列 {content_column}，会成为根项直接子块留在正面"))
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            image = re.match(r"^(?P<indent>\s*)!\[", line)
            if image and len(image.group("indent")) < content_column:
                leaks.append((start + offset + 1,
                              f"图片起始列 {len(image.group('indent'))} 小于背面项内容列 {content_column}，会在翻面前显示在正面"))
    return leaks


MODAL = re.compile(r"可以|应当|不得|必须|有权|只能|一律|不能|无须|禁止|得|视为")
NUMERIC = re.compile(r"\d+")
SOURCE_OPTION = re.compile(r"^\s*-\s+\[[ xX]\]\s*[A-Za-z0-9]+[.、:：)]\s*(.+?)\s*$")
CARD_OPTION = re.compile(r"^\s*>\s*-\s+\[[ xX]\]\s*[A-Za-z0-9]+[.、:：)]\s*(.+?)\s*$")


def _signature(text: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
    return (tuple(MODAL.findall(text)), tuple(NUMERIC.findall(text)))


def declared_roles(body: list[str]) -> list[tuple[str, str]]:
    """The card's own declaration of which party names were swapped, from `cc: roles:`.

    Nothing is guessed from shape: a card may replace party or role words only by listing
    every swap here, and the gate then applies exactly those swaps to the provider option
    and requires the card option to match it character for character.
    """
    line = next((item for item in body if re.match(r"^\s*roles:\s*\S", item)), "")
    matched = re.match(r"^\s*roles:\s*(.+?)\s*$", line)
    if not matched:
        return []
    pairs: list[tuple[str, str]] = []
    for chunk in re.split(r"[,，]", matched.group(1).strip().strip('"')):
        if "→" not in chunk:
            continue
        left, right = chunk.split("→", 1)
        left, right = left.strip().strip('"'), right.strip().strip('"')
        if left and right:
            pairs.append((left, right))
    return pairs


def _plain_option(text: str) -> str:
    """Strip SiYuan inline styles and bold markers so provider and card options compare fairly."""
    return re.sub(r"\{: [^}\n]*\}", "", text).replace("*", "").strip()


def source_options_for(source_text: str, source_qb_id: str) -> list[str]:
    """The provider question's verbatim option texts, located by its `custom-qb-id`."""
    if not source_text or not source_qb_id:
        return []
    marker = 'custom-qb-id="%s"' % source_qb_id
    position = source_text.find(marker)
    if position < 0:
        return []
    options: list[str] = []
    for line in source_text[position:].splitlines()[1:]:
        match = SOURCE_OPTION.match(line)
        if match:
            options.append(_plain_option(match.group(1)))
        elif options and line.strip() and not line.lstrip().startswith((">", " ", "-")):
            break
        elif len(options) >= 8:
            break
    return options


def find_option_drift(lines: list[str], source_text: str | None) -> list[tuple[int, str]]:
    """cc-1 options that stopped matching the provider's own wording (E139).

    A Case card may re-skin its stem to defeat answer memorization, and it may swap party or
    role names — but only the ones declared in `cc: roles:`. After applying exactly those
    declared swaps, every option must equal the provider's option character for character:
    modal words, numeric thresholds, and every other character are the diagnostic signal.
    """
    if not source_text:
        return []
    drift: list[tuple[int, str]] = []
    for start, end, attributes in card_blocks(lines):
        body = lines[start:end]
        options = [(index, _plain_option(match.group(1))) for index, line in enumerate(body)
                   if (match := CARD_OPTION.match(line))]
        if not options:
            continue
        source_qb_id = next((line.split("source_qb_id:", 1)[1].strip().strip('"')
                             for line in body if "source_qb_id:" in line), "")
        originals = source_options_for(source_text, source_qb_id)
        if not originals:
            continue
        roles = declared_roles(body)
        for position, (index, text) in enumerate(options):
            if position >= len(originals):
                drift.append((start + index + 1, f"选项多于题源第 {position + 1} 项，不得自行加项：{text[:24]}"))
                continue
            expected = originals[position]
            for left, right in roles:
                expected = expected.replace(left, right)
            if text != expected:
                drift.append((start + index + 1,
                              f"选项与题源不一致（允许的主体替换要写进 cc: roles）：{text[:24]}"))
            elif _signature(text) != _signature(expected):
                drift.append((start + index + 1, f"选项的情态词/数字门槛与题源不一致：{text[:24]}"))
        if len(options) < len(originals):
            drift.append((start + 1, f"选项只有 {len(options)} 项，题源有 {len(originals)} 项"))
    return drift


def text_of(line_no: int) -> str:
    return _WALL_LINES[line_no - 1] if 0 < line_no <= len(_WALL_LINES) else ""


def find_sibling_walls(lines: list[str]) -> list[tuple[int, str]]:
    """E141: three or more consecutive leaf items at the same level — a wall, not a structure.

    Peer facts only earn a flat run when each item is a real peer on one axis; once the run
    carries a parent/child, step/condition, or rule/application relation it must be re-indented
    under a governing item. An item that owns children, or a level change, breaks the run, so a
    genuine closed list of four peers still passes while an undifferentiated bullet wall fails.
    """
    global _WALL_LINES
    _WALL_LINES = lines
    walls: list[tuple[int, str]] = []
    for start, end, attributes in card_blocks(lines):
        body = lines[start:end]
        # 只约束 cc-1 Case 卡：普通牌组的同级并列是既定卡形，不在本门禁范围内
        if not any(CC_BLOCK.match(line) for line in body):
            continue
        in_fence = False
        run: list[tuple[int, int]] = []

        def flush() -> None:
            if len(run) >= WALL_RUN and not all(REASONING_LABEL.match(text_of(line_no)) for line_no, _ in run):
                walls.append((run[0][0], "连续 %d 个同级无子项的列表项（列 %d）：按语义改成父项统领或缩进分层"
                              % (len(run), run[0][1])))

        for offset, raw in enumerate(body):
            if re.match(r"^\s*(?:>\s*)?```", raw):
                in_fence = not in_fence
                continue
            if in_fence or not raw.strip() or raw.lstrip().startswith((">", "{:")):
                continue
            match = LIST_ITEM.match(raw)
            if not match:
                continue
            indent = len(match.group("indent"))
            content_column = indent + len(match.group("marker")) + len(match.group("gap"))
            has_child = False
            for follow in body[offset + 1:]:
                if not follow.strip():
                    continue
                nxt = re.match(r"^(\s*)(?:-|\*|\d+[.)])\s+\S", follow)
                fence = re.match(r"^\s*(?:>\s*)?```", follow)
                if (nxt and len(nxt.group(1)) >= content_column) or (fence and len(fence.group(0)) - len(fence.group(0).lstrip()) >= content_column):
                    has_child = True
                break
            if has_child or (run and run[-1][1] != indent):
                flush()
                run.clear()
                continue
            run.append((start + offset + 1, indent))
        flush()
    return walls


def without_fences(text: str) -> str:
    """Drop fenced blocks entirely (fence delimiters plus their content)."""
    kept: list[str] = []
    inside = False
    for line in text.splitlines():
        if re.match(r"^\s*(?:>\s*)?```", line):
            inside = not inside
            continue
        if not inside:
            kept.append(line)
    return "\n".join(kept)


def find_focus_tag_gaps(lines: list[str], focus_index: dict[str, list] | None) -> list[tuple[int, str]]:
    """E140: a 考前聚焦 考点 of the card's own subject is discussed but not tagged.

    The index comes from `focus_index.py --build` (考点 names harvested from the 04-考前聚焦
    knowledge tags). Matching runs on card prose only — tags, inline styles, and code fences
    are metadata, not evidence of 涉及 — and only within the card's own subject, because 考点
    names collide across subjects (民诉 委托代理 vs 三国法 委托代理). Any involvement counts:
    a 考点 named only in an option or in the 解析 still earns the tag.
    """
    if not focus_index:
        return []
    gaps: list[tuple[int, str]] = []
    for start, end, attributes in card_blocks(lines):
        body = "\n".join(lines[start:end])
        prose = without_fences(body)
        prose = re.sub(r"\{: [^}\n]*\}", "", prose)
        prose = re.sub(r"#[^#\s]+#", "", prose)
        subjects = re.findall(r"#法考/([^/\s#]+)/", body)
        if not subjects:
            continue
        subject = max(set(subjects), key=subjects.count)
        tagged = {name for tag_subject, name in re.findall(r"#考前聚焦/([^#\s]+)/([^#\s]+)#", body)
                  if tag_subject == subject}
        for path, leaf in focus_index.get(subject, []):
            if len(leaf) >= 3 and leaf in prose and leaf not in tagged:
                gaps.append((start + 1, f"本题涉及考前聚焦考点「{leaf}」（路径 {path}），正面缺 #考前聚焦/{subject}/{leaf}#"))
    return gaps


def check(text: str, source_text: str | None = None,
          focus_index: dict[str, list] | None = None) -> list[tuple[int, str, str]]:
    """Return (line, code, message) findings for a whole deck file."""
    lines = text.splitlines()
    return ([(line, "E136", message) for line, message in find_styled_answer_markers(lines)]
            + [(line, "E137", message) for line, message in find_case_card_gaps(lines)]
            + [(line, "E138", message) for line, message in find_front_leaks(lines)]
            + [(line, "E139", message) for line, message in find_option_drift(lines, source_text)]
            + [(line, "E140", message) for line, message in find_focus_tag_gaps(lines, focus_index)]
            + [(line, "E141", message) for line, message in find_sibling_walls(lines)])
