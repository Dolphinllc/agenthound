"""Graph builder tests."""

from __future__ import annotations

from agenthound.graph import THREAT_SOURCES, build_graph, to_serializable
from agenthound.models import EdgeKind, NodeKind
from agenthound.parsers import parse_claude_desktop_config, parse_tool_catalog
from agenthound.scan import sample_paths


def _full_graph():
    cfg, cat = sample_paths()
    n1, e1 = parse_claude_desktop_config(cfg)
    n2, e2 = parse_tool_catalog(cat)
    return build_graph(n1 + n2, e1 + e2)


def test_threat_sources_are_injected_for_every_agent() -> None:
    g = _full_graph()
    agents = [n for n, d in g.nodes(data=True) if d["model"].kind is NodeKind.AGENT]
    assert agents, "expected at least one agent node"
    for src in THREAT_SOURCES:
        assert g.has_node(src.id)
        for agent in agents:
            assert any(
                d["model"].kind is EdgeKind.INJECTS_INTO
                for _, _, d in g.edges(src.id, data=True)
                if _ == src.id
            ) or g.has_edge(src.id, agent)


def test_to_serializable_round_trips_node_count() -> None:
    g = _full_graph()
    serial = to_serializable(g)
    assert len(serial.nodes) == g.number_of_nodes()
    assert len(serial.edges) == g.number_of_edges()


def test_no_duplicate_node_ids() -> None:
    g = _full_graph()
    ids = [n for n in g.nodes()]
    assert len(ids) == len(set(ids))
