"""Parse a Claude Desktop ``claude_desktop_config.json`` file.

The config enumerates each MCP server the user has installed. We turn each
server entry into an :class:`MCPServer` node, hung off a single ``Agent``
node representing the Claude Desktop client itself.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agenthound.models import Edge, EdgeKind, Node, NodeKind, TrustLevel


CLAUDE_DESKTOP_AGENT_ID = "agent:claude-desktop"


def _agent_node() -> Node:
    return Node(
        id=CLAUDE_DESKTOP_AGENT_ID,
        kind=NodeKind.AGENT,
        label="Claude Desktop",
        trust=TrustLevel.PARTIAL,
        metadata={"client": "claude-desktop"},
    )


def parse_claude_desktop_config(path: str | Path) -> tuple[list[Node], list[Edge]]:
    raw: dict[str, Any] = json.loads(Path(path).read_text())
    servers: dict[str, Any] = raw.get("mcpServers", {})

    nodes: list[Node] = [_agent_node()]
    edges: list[Edge] = []

    for name, spec in servers.items():
        server_id = f"mcp:{name}"
        env: dict[str, Any] = spec.get("env", {}) or {}
        nodes.append(Node(
            id=server_id,
            kind=NodeKind.MCP_SERVER,
            label=name,
            trust=_classify_trust(name, spec),
            metadata={
                "command": spec.get("command", ""),
                "args": " ".join(spec.get("args", [])),
                "env_keys": ",".join(env.keys()),
                "description": spec.get("description", ""),
            },
        ))
        edges.append(Edge(
            id=f"e:agent->{server_id}",
            source=CLAUDE_DESKTOP_AGENT_ID,
            target=server_id,
            kind=EdgeKind.USES,
        ))
        for env_key in env:
            secret_id = f"secret:{name}:{env_key}"
            nodes.append(Node(
                id=secret_id,
                kind=NodeKind.SECRET,
                label=env_key,
                metadata={"server": name, "kind": "env_var"},
            ))
            edges.append(Edge(
                id=f"e:{server_id}->{secret_id}",
                source=server_id,
                target=secret_id,
                kind=EdgeKind.CONTAINS,
            ))

    return nodes, edges


_OFFICIAL_PREFIXES = (
    "@modelcontextprotocol/",
    "mcp-server-",
    "@anthropic-ai/",
)


def _classify_trust(name: str, spec: dict[str, Any]) -> TrustLevel:
    """Hand-wavy first-pass trust score based on package origin."""
    args = " ".join(spec.get("args", []))
    if any(prefix in args for prefix in _OFFICIAL_PREFIXES):
        return TrustLevel.TRUSTED
    if "@" in args and "/" in args:
        return TrustLevel.PARTIAL
    return TrustLevel.UNTRUSTED
