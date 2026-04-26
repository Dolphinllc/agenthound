"""Build a NetworkX MultiDiGraph from parsed nodes and edges.

The builder also injects the canonical *threat sources* — pieces of input
that an attacker can plausibly control — and wires them into every Agent
node via INJECTS_INTO edges. This makes downstream attack-path search a
straightforward all-pairs source→sink walk.
"""

from __future__ import annotations

import networkx as nx

from agenthound.models import Edge, EdgeKind, Graph, Node, NodeKind, TrustLevel


THREAT_SOURCES: tuple[Node, ...] = (
    Node(
        id="src:chat-input",
        kind=NodeKind.SOURCE,
        label="User chat input",
        trust=TrustLevel.UNTRUSTED,
        metadata={"vector": "direct_prompt_injection"},
    ),
    Node(
        id="src:web-page",
        kind=NodeKind.SOURCE,
        label="Web page content (via fetch tool)",
        trust=TrustLevel.UNTRUSTED,
        metadata={"vector": "indirect_prompt_injection"},
    ),
    Node(
        id="src:tool-description",
        kind=NodeKind.SOURCE,
        label="MCP tool description (poisoning)",
        trust=TrustLevel.UNTRUSTED,
        metadata={"vector": "tool_poisoning"},
    ),
)


def build_graph(nodes: list[Node], edges: list[Edge]) -> nx.MultiDiGraph:
    g: nx.MultiDiGraph = nx.MultiDiGraph()

    seen_node_ids: set[str] = set()
    for node in nodes:
        if node.id in seen_node_ids:
            continue
        seen_node_ids.add(node.id)
        g.add_node(node.id, model=node)

    for src in THREAT_SOURCES:
        if src.id not in seen_node_ids:
            g.add_node(src.id, model=src)
            seen_node_ids.add(src.id)

    seen_edge_ids: set[str] = set()
    for edge in edges:
        if edge.id in seen_edge_ids:
            continue
        seen_edge_ids.add(edge.id)
        g.add_edge(edge.source, edge.target, key=edge.id, model=edge)

    _wire_threat_sources(g)
    return g


def _wire_threat_sources(g: nx.MultiDiGraph) -> None:
    agents: list[str] = [n for n, data in g.nodes(data=True)
                         if data["model"].kind is NodeKind.AGENT]
    if not agents:
        return

    for agent_id in agents:
        for src in THREAT_SOURCES:
            edge_id = f"e:{src.id}->{agent_id}"
            if g.has_edge(src.id, agent_id, key=edge_id):
                continue
            edge = Edge(id=edge_id, source=src.id, target=agent_id,
                        kind=EdgeKind.INJECTS_INTO,
                        metadata={"vector": str(src.metadata.get("vector", ""))})
            g.add_edge(src.id, agent_id, key=edge_id, model=edge)


def to_serializable(g: nx.MultiDiGraph) -> Graph:
    nodes = [data["model"] for _, data in g.nodes(data=True)]
    edges = [data["model"] for _, _, data in g.edges(data=True)]
    return Graph(nodes=nodes, edges=edges)
