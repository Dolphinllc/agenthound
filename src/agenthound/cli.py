"""Typer-powered CLI: ``agenthound scan|serve|paths``.

Designed to mirror the BloodHound experience: a single binary with
discoverable subcommands and JSON-friendly output for piping into
other tools.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from agenthound.scan import sample_paths, scan

app = typer.Typer(
    name="agenthound",
    help="Map and visualize attack paths in your AI agent's tool chain.",
    no_args_is_help=True,
)
console = Console()


@app.command("scan")
def scan_cmd(
    config: Annotated[Path | None, typer.Option("--config", "-c", help="claude_desktop_config.json")] = None,
    catalog: Annotated[Path | None, typer.Option("--catalog", "-t", help="MCP tools catalog JSON")] = None,
    output: Annotated[Path | None, typer.Option("--output", "-o", help="Write JSON ScanResult to path")] = None,
    json_only: Annotated[bool, typer.Option("--json", help="Emit raw JSON to stdout")] = False,
) -> None:
    """Run a scan against the supplied (or bundled sample) configs."""
    result = scan(config, catalog)
    payload = result.model_dump(mode="json")

    if output:
        output.write_text(json.dumps(payload, indent=2))
        console.print(f"[green]✓ wrote[/green] {output}")
        return

    if json_only:
        typer.echo(json.dumps(payload, indent=2))
        return

    _render_summary(result)


@app.command("paths")
def paths_cmd(
    severity: Annotated[str | None, typer.Option("--severity", help="Filter by severity")] = None,
    limit: Annotated[int, typer.Option("--limit", help="Max paths to display")] = 20,
) -> None:
    """List attack paths discovered in the bundled sample environment."""
    result = scan()
    rows = result.paths
    if severity:
        rows = [p for p in rows if p.severity.value == severity.lower()]
    table = Table(title=f"Attack paths (showing {min(limit, len(rows))} of {len(rows)})")
    table.add_column("ID")
    table.add_column("Severity", style="bold")
    table.add_column("Score", justify="right")
    table.add_column("Type")
    table.add_column("Title")
    for path in rows[:limit]:
        sev_style = {"critical": "red", "high": "magenta",
                     "medium": "yellow", "low": "cyan"}[path.severity.value]
        table.add_row(
            path.id,
            f"[{sev_style}]{path.severity.value}[/{sev_style}]",
            f"{path.risk_score:.1f}",
            path.attack_type.value,
            path.title,
        )
    console.print(table)


@app.command("serve")
def serve_cmd(
    host: Annotated[str, typer.Option("--host", help="Bind host")] = "127.0.0.1",
    port: Annotated[int, typer.Option("--port", help="Bind port")] = 8765,
    reload: Annotated[bool, typer.Option("--reload", help="Hot reload (dev)")] = False,
) -> None:
    """Run the AgentHound HTTP API."""
    import uvicorn

    uvicorn.run(
        "agenthound.server.app:app",
        host=host,
        port=port,
        reload=reload,
    )


@app.command("sample-config")
def sample_config_cmd() -> None:
    """Print the path of the bundled sample claude_desktop_config.json."""
    cfg, cat = sample_paths()
    console.print(f"[bold]config[/bold]:  {cfg}")
    console.print(f"[bold]catalog[/bold]: {cat}")


def _render_summary(result) -> None:  # type: ignore[no-untyped-def]
    s = result.summary
    console.rule("[bold cyan]AgentHound scan summary")
    console.print(
        f"[bold]Nodes:[/bold] {s.total_nodes}  "
        f"[bold]Edges:[/bold] {s.total_edges}  "
        f"[bold]Attack paths:[/bold] {s.total_paths}"
    )
    sev_table = Table(show_header=True, header_style="bold")
    sev_table.add_column("Severity")
    sev_table.add_column("Count", justify="right")
    for sev in ("critical", "high", "medium", "low"):
        sev_table.add_row(sev, str(s.by_severity.get(sev, 0)))
    console.print(sev_table)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
