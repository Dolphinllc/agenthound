"""Parse MCP tool catalogs into Tool nodes.

In production the catalog is fetched from each MCP server via the
``tools/list`` JSON-RPC method. For the MVP we accept either a live
catalog (dict[server_name, list[ToolDef]]) or a path to a JSON file
that mirrors that shape.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agenthound.catalog.attack_patterns import (
    SENSITIVE_PATHS,
    detect_tool_poisoning,
    match_capabilities,
)
from agenthound.models import Edge, EdgeKind, Node, NodeKind, TrustLevel


def parse_tool_catalog(
    catalog: dict[str, list[dict[str, Any]]] | str | Path,
) -> tuple[list[Node], list[Edge]]:
    if not isinstance(catalog, dict):
        catalog = json.loads(Path(catalog).read_text())

    nodes: list[Node] = []
    edges: list[Edge] = []
    capability_targets: dict[tuple[str, str], Node] = {}

    for server_name, tools in catalog.items():
        if server_name.startswith("_"):
            continue
        server_id = f"mcp:{server_name}"
        for tool in tools:
            tool_name: str = tool["name"]
            description: str = tool.get("description", "") or ""
            tool_id = f"tool:{server_name}.{tool_name}"

            poisoning = detect_tool_poisoning(description)
            tool_node = Node(
                id=tool_id,
                kind=NodeKind.TOOL,
                label=f"{server_name}.{tool_name}",
                trust=TrustLevel.UNTRUSTED if poisoning else TrustLevel.TRUSTED,
                metadata={
                    "server": server_name,
                    "name": tool_name,
                    "description": description,
                    "poisoning_signals": ", ".join(poisoning) if poisoning else "",
                },
            )
            nodes.append(tool_node)
            edges.append(Edge(
                id=f"e:{server_id}->{tool_id}",
                source=server_id,
                target=tool_id,
                kind=EdgeKind.EXPOSES,
            ))

            for rule in match_capabilities(tool_name, description):
                key = (rule.target, rule.target_kind)
                if key not in capability_targets:
                    target_kind = NodeKind(rule.target_kind)
                    capability_targets[key] = Node(
                        id=rule.target,
                        kind=target_kind,
                        label=rule.target_label,
                        trust=TrustLevel.UNTRUSTED if target_kind is NodeKind.SINK else TrustLevel.TRUSTED,
                    )
                edges.append(Edge(
                    id=f"e:{tool_id}-{rule.capability.value}->{rule.target}",
                    source=tool_id,
                    target=rule.target,
                    kind=rule.capability,
                ))

    nodes.extend(capability_targets.values())

    if any(n.id == "fs:any" for n in nodes):
        nodes.extend(_sensitive_path_secrets())
        edges.extend(_sensitive_path_edges())

    return nodes, edges


def _sensitive_path_secrets() -> list[Node]:
    return [
        Node(
            id=f"secret:fs:{path}",
            kind=NodeKind.SECRET,
            label=label,
            metadata={"path": path, "kind": "file"},
        )
        for path, label in SENSITIVE_PATHS
    ]


def _sensitive_path_edges() -> list[Edge]:
    return [
        Edge(
            id=f"e:fs->{path}",
            source="fs:any",
            target=f"secret:fs:{path}",
            kind=EdgeKind.CONTAINS,
        )
        for path, _ in SENSITIVE_PATHS
    ]
