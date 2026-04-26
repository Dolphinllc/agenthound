"""Parser unit tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agenthound.models import EdgeKind, NodeKind, TrustLevel
from agenthound.parsers import parse_claude_desktop_config, parse_tool_catalog
from agenthound.scan import sample_paths


@pytest.fixture
def sample_config(tmp_path: Path) -> Path:
    cfg, _ = sample_paths()
    return cfg


def test_parse_claude_desktop_config_returns_agent_and_servers(sample_config: Path) -> None:
    nodes, edges = parse_claude_desktop_config(sample_config)

    kinds = {n.kind for n in nodes}
    assert NodeKind.AGENT in kinds
    assert NodeKind.MCP_SERVER in kinds
    assert any(n.label == "Claude Desktop" for n in nodes)

    server_labels = {n.label for n in nodes if n.kind is NodeKind.MCP_SERVER}
    assert {"filesystem", "github", "slack", "gmail", "fetch"}.issubset(server_labels)

    assert any(e.kind is EdgeKind.USES for e in edges)


def test_env_keys_become_secret_nodes(sample_config: Path) -> None:
    nodes, _ = parse_claude_desktop_config(sample_config)
    secrets = [n.label for n in nodes if n.kind is NodeKind.SECRET]
    assert "GITHUB_PERSONAL_ACCESS_TOKEN" in secrets
    assert "SLACK_BOT_TOKEN" in secrets


def test_unknown_publisher_is_marked_partial_or_untrusted(tmp_path: Path) -> None:
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps({
        "mcpServers": {
            "weird-server": {
                "command": "node",
                "args": ["./totally-local.js"],
            }
        }
    }))
    nodes, _ = parse_claude_desktop_config(cfg)
    server = next(n for n in nodes if n.kind is NodeKind.MCP_SERVER)
    assert server.trust in {TrustLevel.UNTRUSTED, TrustLevel.PARTIAL}


def test_parse_tool_catalog_finds_capability_edges() -> None:
    _, catalog = sample_paths()
    nodes, edges = parse_tool_catalog(catalog)

    tools = [n for n in nodes if n.kind is NodeKind.TOOL]
    assert any(t.label == "filesystem.read_file" for t in tools)

    edge_kinds = {e.kind for e in edges}
    assert EdgeKind.READS in edge_kinds
    assert EdgeKind.CALLS in edge_kinds


def test_tool_poisoning_is_detected_in_helpful_utils() -> None:
    _, catalog = sample_paths()
    nodes, _ = parse_tool_catalog(catalog)
    poisoned = [n for n in nodes if n.kind is NodeKind.TOOL
                and n.metadata.get("poisoning_signals")]
    assert any(t.label == "helpful-utils.format_text" for t in poisoned)


def test_filesystem_capability_creates_sensitive_secrets() -> None:
    _, catalog = sample_paths()
    nodes, _ = parse_tool_catalog(catalog)
    secret_labels = {n.label for n in nodes if n.kind is NodeKind.SECRET}
    assert "AWS credentials" in secret_labels
    assert "SSH private key" in secret_labels
