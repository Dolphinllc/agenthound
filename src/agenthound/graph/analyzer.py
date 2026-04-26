"""Find attack-shaped paths in the graph and score them.

An *attack path* is any simple path from a Source node (untrusted input
vector) to a Sink/Secret node, optionally constrained by max length.
Each path is classified by the kind of terminal node and the edges it
traverses, then scored on a 0–10 scale.
"""

from __future__ import annotations

import itertools
from collections.abc import Iterator

import networkx as nx

from agenthound.models import (
    AttackPath,
    AttackPathStep,
    AttackType,
    Edge,
    EdgeKind,
    Node,
    NodeKind,
    Severity,
)


MAX_PATH_LENGTH = 6


def find_attack_paths(g: nx.MultiDiGraph, max_length: int = MAX_PATH_LENGTH) -> list[AttackPath]:
    sources = _nodes_of_kind(g, NodeKind.SOURCE)
    targets = _nodes_of_kind(g, NodeKind.SINK) + _nodes_of_kind(g, NodeKind.SECRET)

    raw_paths: list[list[str]] = []
    for src, dst in itertools.product(sources, targets):
        try:
            for path in nx.all_simple_paths(g, src, dst, cutoff=max_length):
                raw_paths.append(path)
        except nx.NodeNotFound:
            continue

    deduped = _dedupe_paths(raw_paths)
    return [_score_path(g, p, idx) for idx, p in enumerate(deduped)]


def _dedupe_paths(paths: list[list[str]]) -> list[list[str]]:
    seen: set[tuple[str, ...]] = set()
    unique: list[list[str]] = []
    for p in sorted(paths, key=len):
        key = tuple(p)
        if key in seen:
            continue
        seen.add(key)
        unique.append(p)
    return unique


def _nodes_of_kind(g: nx.MultiDiGraph, kind: NodeKind) -> list[str]:
    return [n for n, d in g.nodes(data=True) if d["model"].kind is kind]


def _score_path(g: nx.MultiDiGraph, path: list[str], idx: int) -> AttackPath:
    steps: list[AttackPathStep] = []
    edges_kinds: list[EdgeKind] = []
    for prev, curr in _pairwise(path):
        edge = _pick_edge(g, prev, curr)
        edges_kinds.append(edge.kind)
        steps.insert(0, AttackPathStep()) if False else steps.append(
            AttackPathStep(node=g.nodes[curr]["model"], incoming_edge=edge)
        )
    steps.insert(0, AttackPathStep(node=g.nodes[path[0]]["model"]))

    terminal: Node = g.nodes[path[-1]]["model"]
    source: Node = g.nodes[path[0]]["model"]
    attack_type = _classify(source, terminal, edges_kinds)
    severity, score = _severity(attack_type, terminal, len(path))

    return AttackPath(
        id=f"path-{idx:04d}",
        title=_title(source, terminal, attack_type),
        description=_describe(steps, attack_type),
        attack_type=attack_type,
        severity=severity,
        risk_score=score,
        steps=steps,
        mitigation=_mitigation(attack_type),
    )


def _pick_edge(g: nx.MultiDiGraph, u: str, v: str) -> Edge:
    edges = g.get_edge_data(u, v) or {}
    if not edges:
        raise nx.NetworkXError(f"missing edge {u}->{v}")
    first = next(iter(edges.values()))
    return first["model"]


def _pairwise(seq: list[str]) -> Iterator[tuple[str, str]]:
    a, b = itertools.tee(seq)
    next(b, None)
    return zip(a, b)


def _classify(source: Node, terminal: Node, edges: list[EdgeKind]) -> AttackType:
    vector = str(source.metadata.get("vector", ""))
    if vector == "tool_poisoning":
        return AttackType.TOOL_POISONING
    if vector == "indirect_prompt_injection":
        return AttackType.INDIRECT_PROMPT_INJECTION
    if terminal.kind is NodeKind.SECRET:
        return AttackType.CREDENTIAL_THEFT
    if EdgeKind.CALLS in edges:
        return AttackType.DATA_EXFILTRATION
    return AttackType.PRIVILEGE_ESCALATION


def _severity(attack: AttackType, terminal: Node, length: int) -> tuple[Severity, float]:
    base = {
        AttackType.TOOL_POISONING: 9.0,
        AttackType.CREDENTIAL_THEFT: 9.5,
        AttackType.DATA_EXFILTRATION: 8.0,
        AttackType.INDIRECT_PROMPT_INJECTION: 7.5,
        AttackType.COMMAND_INJECTION: 9.0,
        AttackType.PRIVILEGE_ESCALATION: 6.0,
    }[attack]
    length_penalty = max(0.0, (length - 3) * 0.4)
    score = max(1.0, min(10.0, base - length_penalty))
    if score >= 9.0:
        sev = Severity.CRITICAL
    elif score >= 7.0:
        sev = Severity.HIGH
    elif score >= 4.0:
        sev = Severity.MEDIUM
    else:
        sev = Severity.LOW
    return sev, round(score, 1)


def _title(source: Node, terminal: Node, attack: AttackType) -> str:
    return f"{source.label} → {terminal.label} ({attack.value.replace('_', ' ')})"


def _describe(steps: list[AttackPathStep], attack: AttackType) -> str:
    chain = " → ".join(s.node.label for s in steps)
    return f"{attack.value.replace('_', ' ').title()} via: {chain}"


def _mitigation(attack: AttackType) -> str:
    return {
        AttackType.TOOL_POISONING: "Pin trusted MCP server versions; review tool descriptions; isolate untrusted servers.",
        AttackType.CREDENTIAL_THEFT: "Restrict filesystem tool to non-sensitive paths; remove unused tokens from env.",
        AttackType.DATA_EXFILTRATION: "Add an allow-list of outbound destinations; require human-in-the-loop confirmations.",
        AttackType.INDIRECT_PROMPT_INJECTION: "Sanitize fetched content before passing to the model; wrap in delimiters.",
        AttackType.COMMAND_INJECTION: "Validate tool inputs server-side; never pass raw model output to a shell.",
        AttackType.PRIVILEGE_ESCALATION: "Apply principle of least privilege to each MCP server's permissions.",
    }[attack]
