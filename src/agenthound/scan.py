"""High-level scan orchestration.

Most callers just want a single function: ``scan(config_path, catalog_path)``.
That's what this module provides — wiring parsers, the graph builder, and the
analyzer into a complete :class:`ScanResult`.
"""

from __future__ import annotations

from collections import Counter
from importlib.resources import files
from pathlib import Path

from agenthound.graph import build_graph, find_attack_paths, to_serializable
from agenthound.models import ScanResult, ScanSummary
from agenthound.parsers import parse_claude_desktop_config, parse_tool_catalog


def sample_paths() -> tuple[Path, Path]:
    samples = files("agenthound.data") / "samples"
    return (
        Path(str(samples / "claude_desktop_config.json")),
        Path(str(samples / "mcp_tool_catalog.json")),
    )


def scan(config_path: str | Path | None = None,
         catalog_path: str | Path | None = None) -> ScanResult:
    if config_path is None or catalog_path is None:
        sample_cfg, sample_cat = sample_paths()
        config_path = config_path or sample_cfg
        catalog_path = catalog_path or sample_cat

    cfg_nodes, cfg_edges = parse_claude_desktop_config(config_path)
    cat_nodes, cat_edges = parse_tool_catalog(catalog_path)

    graph_obj = build_graph(cfg_nodes + cat_nodes, cfg_edges + cat_edges)
    paths = find_attack_paths(graph_obj)
    serial = to_serializable(graph_obj)

    by_sev = Counter(p.severity.value for p in paths)
    by_type = Counter(p.attack_type.value for p in paths)
    summary = ScanSummary(
        total_nodes=len(serial.nodes),
        total_edges=len(serial.edges),
        total_paths=len(paths),
        by_severity=dict(by_sev),
        by_attack_type=dict(by_type),
    )
    return ScanResult(graph=serial, paths=paths, summary=summary)
