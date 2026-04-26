# Architecture

AgentHound is a **stateless analysis pipeline** wrapped in a thin REST API
and a Next.js UI. Every scan is independent, every result is JSON, and the
graph engine is in-memory NetworkX — no database required.

## High-level flow

```
config / catalog → parsers → graph builder → analyzer → ScanResult (JSON)
                                                           │
                                                           ├─► CLI (rich)
                                                           ├─► REST (FastAPI)
                                                           └─► Web UI (Next.js + React Flow)
```

## Modules

| Path                                       | Responsibility |
|--------------------------------------------|----------------|
| `src/agenthound/models/schema.py`          | Pydantic v2 schema for nodes, edges, attack paths, scan results. |
| `src/agenthound/parsers/`                  | One module per ingestion source (Claude Desktop config, MCP tool catalog, …). Each returns `(list[Node], list[Edge])`. |
| `src/agenthound/catalog/attack_patterns.py`| Capability rules (tool name → READS/WRITES/CALLS), tool-poisoning regexes, sensitive-path inventory. |
| `src/agenthound/graph/builder.py`          | Assembles a `nx.MultiDiGraph` and wires canonical threat sources into every Agent. |
| `src/agenthound/graph/analyzer.py`         | All-pairs simple-path search, classification, severity scoring, mitigation lookup. |
| `src/agenthound/scan.py`                   | Orchestrator: parse → build → analyze → ScanResult. |
| `src/agenthound/server/app.py`             | FastAPI app exposing `/api/scan/sample`, `/api/scan` (upload), `/api/health`. |
| `src/agenthound/cli.py`                    | Typer CLI: `scan`, `paths`, `serve`, `sample-config`. |
| `frontend/src/components/graph/`           | React Flow canvas + custom node renderer. |
| `frontend/src/components/`                 | Topbar, summary bar, path list, path detail. |

## Why graphs?

A flat findings list cannot express the **combinatorial** danger of an agent
environment. A `read_file` tool is benign on its own. A `send_email` tool is
benign on its own. Together with an injected user input, they're a
data-exfiltration pipe. The natural representation is a graph; the natural
question is "is there a path?".

This is the same insight that made BloodHound the standard for Active
Directory red teaming. AgentHound applies it to the AI agent layer.

## Data model

```python
NodeKind   = source | agent | mcp_server | tool | resource | secret | sink
EdgeKind   = injects_into | uses | exposes | reads | writes | calls | contains
TrustLevel = trusted | partial | untrusted
```

Threat sources injected automatically:

- `src:chat-input` — direct prompt injection vector
- `src:web-page` — indirect prompt injection vector (via fetch tools)
- `src:tool-description` — tool poisoning vector

## Severity scoring

Severity is a function of attack class and path length:

```
score = base_score(attack_type) - 0.4 * max(0, length - 3)
```

| Attack class                  | Base score |
|-------------------------------|:----------:|
| credential_theft              | 9.5        |
| tool_poisoning                | 9.0        |
| command_injection             | 9.0        |
| data_exfiltration             | 8.0        |
| indirect_prompt_injection     | 7.5        |
| privilege_escalation          | 6.0        |

Categories: `critical (≥ 9)`, `high (≥ 7)`, `medium (≥ 4)`, `low`.

This is intentionally simple. A future version will incorporate exploitability
weights from the OWASP MCP Top 10 risk model.

## Performance notes

- Single-source single-sink Dijkstra: O(V + E)
- All-pairs `simple_paths` with cutoff: O(V! / (V-k)!) worst case — bounded
  by `MAX_PATH_LENGTH = 6`.
- For 100 nodes / 200 edges / cutoff 6, scans complete in < 100 ms on an M-series Mac.
- Optimizing for very large environments (10k+ nodes) is on the roadmap;
  we'll switch to a real graph DB at that point.

## Extending

Add a new parser:

```python
# src/agenthound/parsers/cursor.py
def parse_cursor_config(path) -> tuple[list[Node], list[Edge]]:
    ...
```

Add a new capability rule:

```python
# src/agenthound/catalog/attack_patterns.py
CapabilityRule(EdgeKind.CALLS, "sink:webhook", "Outbound webhook", "sink",
               ("post_webhook", "trigger_webhook"))
```

That's it — re-run `agenthound scan` and the new edges appear in the graph.
