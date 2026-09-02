#!/usr/bin/env python3
"""Detect perfunctory ("敷衍") Mermaid diagrams in legal-study notes.

A study note diagram must do analysis: a root or shared node with branches,
decision nodes, or edge labels that state the tested relation.  The lazy
vendor format stacks unrelated keyword pairs or bare keyword chains:

    flowchart TD
        A["申请信息公开"] --> B["行使权利=守法"]
        C["环保局败诉"] --> D["承担法律责任=强制作用"]

Such a block has no shared node, no edge label, and no branch: it is a bullet
list wearing a diagram costume.  `validate_mermaid_semantics` rejects that
shape and accepts graphs that reuse nodes, branch, label edges, or use
decision diamonds.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class MermaidGateFinding:
    code: str
    line: int
    message: str


EDGE_SPLIT_RE = re.compile(
    r"(\|[^|\n]*\||-->|---|-\.->|==>|--x|--o|o--|<--|<=>|--|->|\.\.\.-?>)"
)
NODE_ID_RE = re.compile(r"([A-Za-z_][\w\-]*)")
FENCE_RE = re.compile(r"^(?:\s*>\s*)?```mermaid\s*$")
HEADER_SKIP_RE = re.compile(
    r"^(?:%%|flowchart|graph|classDef|class\s+\S|style\s+\S|linkStyle|subgraph|end\b|direction|click\s+\S)"
)
MIN_EDGES_TO_JUDGE = 2
PAIR_EDGE_FRACTION = 0.75
EMPTY_CHAIN_MIN_EDGES = 2
KEYWORD_CHAIN_MAX_AVG_LABEL = 6.0


@dataclass
class MermaidDiagram:
    start_line: int
    nodes: dict[str, tuple[str, str]]  # node id -> (label, shape)
    edges: list[tuple[str, str, str]]  # (tail, head, edge_label)
    plain_lines: list[str]

    @property
    def node_count(self) -> int:
        return len(self.nodes)

    @property
    def edge_count(self) -> int:
        return len(self.edges)

    def degrees(self) -> dict[str, int]:
        degree: dict[str, int] = {}
        for tail, head, _ in self.edges:
            degree[tail] = degree.get(tail, 0) + 1
            degree[head] = degree.get(head, 0) + 1
        return degree

    def labeled_edge_count(self) -> int:
        return sum(1 for _, _, label in self.edges if label.strip())

    def diamond_count(self) -> int:
        return sum(1 for label, shape in self.nodes.values() if shape == "diamond")

    def uses_semantic_style(self) -> bool:
        """True when the block declares semantic roles via classDef/class/linkStyle."""
        return any(
            re.match(r"^(?:classDef|class\s+\S|linkStyle)", line.strip())
            for line in self.plain_lines
        )

    def max_degree(self) -> int:
        degree = self.degrees()
        return max(degree.values(), default=0)

    def pair_edge_count(self) -> int:
        """Edges whose endpoints never appear in any other edge."""
        degree = self.degrees()
        return sum(1 for tail, head, _ in self.edges if degree[tail] == 1 and degree[head] == 1)

    def component_count(self) -> int:
        adjacency: dict[str, set[str]] = {node: set() for node in self.nodes}
        for tail, head, _ in self.edges:
            adjacency[tail].add(head)
            adjacency[head].add(tail)
        seen: set[str] = set()
        components = 0
        for node in self.nodes:
            if node in seen:
                continue
            components += 1
            stack = [node]
            seen.add(node)
            while stack:
                current = stack.pop()
                for neighbor in adjacency[current]:
                    if neighbor not in seen:
                        seen.add(neighbor)
                        stack.append(neighbor)
        return components


def _bracket_label(rest: str, opener: str, closer: str) -> tuple[str, str]:
    """Return (label, shape-token) for a bracketed node shape starting at rest."""
    quoted = rest[1:].lstrip()
    if quoted.startswith(('"', "'")):
        quote = quoted[0]
        end = quoted.find(quote, 1)
        label = quoted[1:end]
        body = quoted[end + 1:]
        if body.lstrip().startswith(closer):
            shape = "stadium" if opener == "[[" else "diamond" if opener == "{" else "circle" if opener == "((" else "default"
            return label, shape
        # quote mismatch: treat the whole bracket content as the label
    if opener == "[[":
        end = rest.find("]]")
        close = "]]"
    else:
        end = rest.find(closer)
        close = closer
    if end < 0:
        end = len(rest)
        close = ""
    label = rest[len(opener):end]
    shape = "stadium" if opener == "[[" else "diamond" if opener == "{" else "circle" if opener == "((" else "default"
    return label.strip().strip('"').strip("'"), shape


def _extract_node(spec: str) -> tuple[str, str, str] | None:
    """Return (node_id, label, shape) for a node spec like `A["label"]`."""
    spec = spec.strip()
    if not spec:
        return None
    match = NODE_ID_RE.match(spec)
    if not match:
        return None
    node_id = match.group(1)
    rest = spec[match.end():].strip()
    if not rest:
        return node_id, node_id, "default"
    if rest.startswith(("[[", "((")):
        opener = rest[:2]
        label, shape = _bracket_label(rest, opener, "]]" if opener == "[[" else "))")
    else:
        opener = rest[0]
        if opener not in {"[", "{", "("}:
            return None
        closer = "]" if opener == "[" else "}" if opener == "{" else ")"
        label, shape = _bracket_label(rest, opener, closer)
    return node_id, label, shape


def _parse_block(lines: list[str], start_line: int) -> MermaidDiagram:
    """Parse a mermaid fence body into a diagram."""
    nodes: dict[str, tuple[str, str]] = {}
    edges: list[tuple[str, str, str]] = []
    for offset, raw in enumerate(lines):
        line = re.sub(r"^\s*>\s?", "", raw).strip()
        if not line or HEADER_SKIP_RE.match(line):
            continue
        parts = EDGE_SPLIT_RE.split(line)
        last_node: str | None = None
        pending_label = ""
        for part in parts:
            if part.startswith("|"):
                pending_label = part.strip("|").strip().strip('"').strip("'")
                continue
            node = _extract_node(part)
            if node is None:
                continue
            node_id, label, shape = node
            nodes.setdefault(node_id, (label, shape))
            if last_node is not None:
                edges.append((last_node, node_id, pending_label))
                pending_label = ""
            last_node = node_id
    return MermaidDiagram(start_line, nodes, edges, [re.sub(r"^\s*>\s?", "", item) for item in lines])


def extract_diagrams(text: str) -> list[MermaidDiagram]:
    """Collect every fenced mermaid diagram with its 1-based opening line."""
    diagrams: list[MermaidDiagram] = []
    lines = text.splitlines()
    index = 0
    while index < len(lines):
        if FENCE_RE.match(lines[index]):
            body: list[str] = []
            start = index + 2  # first content line inside the fence
            index += 1
            while index < len(lines) and not re.match(r"^(?:\s*>\s*)?```", lines[index]):
                body.append(lines[index])
                index += 1
            if body:
                diagrams.append(_parse_block(body, start))
            continue
        index += 1
    return diagrams


def _avg_label_length(diagram: MermaidDiagram) -> float:
    lengths = [len(label) for label, _ in diagram.nodes.values()]
    return sum(lengths) / len(lengths) if lengths else 0.0


def validate_mermaid_semantics(text: str) -> tuple[MermaidGateFinding, ...]:
    """Reject perfunctory Mermaid diagrams.

    - `E901`: a multi-edge block whose edges are almost all isolated keyword
      pairs (`A["x"] --> B["y"]` stacked without shared nodes, labels, or
      branches) — the vendor pair-list format.
    - `E902`: a bare keyword chain or forest (every node degree <= 2, no edge
      labels, no decision diamonds) — keywords strung together with `-->`
      instead of an analysis.
    - `E903`: several independent chains (or orphan nodes) stitched into one
      fence — the block parses as more than one connected component, so it is
      still N separate diagrams, never one integrated reasoning chain.
    """
    findings: list[MermaidGateFinding] = []
    for diagram in extract_diagrams(text):
        if diagram.edge_count < MIN_EDGES_TO_JUDGE:
            continue
        degrees = diagram.degrees()
        pair_edges = diagram.pair_edge_count()
        labeled = diagram.labeled_edge_count()
        diamonds = diagram.diamond_count()
        max_degree = diagram.max_degree()
        semantic_style = diagram.uses_semantic_style()
        if (
            diagram.edge_count >= 3
            and pair_edges / diagram.edge_count >= PAIR_EDGE_FRACTION
            and not semantic_style
        ):
            findings.append(
                MermaidGateFinding(
                    "901",
                    diagram.start_line,
                    f"{pair_edges}/{diagram.edge_count} edges are isolated keyword pairs: the block is a stack of unrelated "
                    "`A --> B` rows (e.g. `A[申请信息公开] --> B[行使权利=守法]`), not an analysis. Rewrite it as one "
                    "connected diagram that reuses nodes — branch from a shared root, add decision diamonds, and state "
                    "each tested relation on the edge label — or drop the fence and use a list.",
                )
            )
            continue
        if (
            diagram.edge_count >= EMPTY_CHAIN_MIN_EDGES
            and labeled == 0
            and diamonds == 0
            and max_degree <= 2
            and not semantic_style
            and _avg_label_length(diagram) < KEYWORD_CHAIN_MAX_AVG_LABEL
        ):
            findings.append(
                MermaidGateFinding(
                    "902",
                    diagram.start_line,
                    "Every node has degree <= 2 with no edge label, no decision diamond, and no branch, and the labels stay "
                    "keyword-length (e.g. `法律 --> 公序良俗 --> 权利`): keyword chains strung with `-->` add no analysis over "
                    "a list. Branch from a shared root or decision node and label each edge with the tested relation, or use a list.",
                )
            )
            continue
        components = diagram.component_count()
        if components > 1:
            findings.append(
                MermaidGateFinding(
                    "903",
                    diagram.start_line,
                    f"The block parses as {components} disconnected components: independent chains (or orphan nodes) stitched into one "
                    "fence are still separate diagrams, not one reasoning chain. Rewire them into a single connected logic chain through "
                    "shared or converging nodes so every node is reachable, or keep genuinely unrelated analyses as lists — never pad a "
                    "diagram out of disjoint `-->` rows.",
                )
            )
    return tuple(findings)


if __name__ == "__main__":
    import sys
    from pathlib import Path

    for path in sys.argv[1:]:
        for finding in validate_mermaid_semantics(Path(path).read_text(encoding="utf-8")):
            print(f"{path}:{finding.line}: E{finding.code}: {finding.message}")