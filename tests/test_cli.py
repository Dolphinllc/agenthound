"""CLI smoke tests."""

from __future__ import annotations

from typer.testing import CliRunner

from agenthound.cli import app


def test_scan_renders_summary() -> None:
    runner = CliRunner()
    res = runner.invoke(app, ["scan"])
    assert res.exit_code == 0
    assert "AgentHound scan summary" in res.output


def test_scan_json_emits_parseable_json() -> None:
    import json

    runner = CliRunner()
    res = runner.invoke(app, ["scan", "--json"])
    assert res.exit_code == 0
    parsed = json.loads(res.output)
    assert parsed["schema_version"] == "1"


def test_paths_filter_critical() -> None:
    runner = CliRunner()
    res = runner.invoke(app, ["paths", "--severity", "critical"])
    assert res.exit_code == 0
    assert "critical" in res.output.lower()
