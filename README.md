<div align="center">

# 🐕 AgentHound

### *BloodHound for AI Agents*

**Map and visualize attack paths through your AI agent's MCP tool chain — before an attacker does.**

🇺🇸 English (you are here) · [🇯🇵 日本語](README.ja.md) · [🇨🇳 简体中文](README.zh-CN.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-ff5b3a.svg)](LICENSE)
[![Python 3.14+](https://img.shields.io/badge/python-3.14+-5fb4ff.svg)](https://www.python.org/downloads/release/python-3140/)
[![Built by Dolphin LLC](https://img.shields.io/badge/built%20by-Dolphin%20LLC-b478ff.svg)](https://github.com/Dolphinllc)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-5feaa1.svg)](CONTRIBUTING.md)

<img src="docs/hero.png" alt="AgentHound visualizing an attack path from a chat input through Claude Desktop's MCP tools to a leaked GitHub token" width="100%" />

</div>

---

## Why AgentHound?

The **MCP tool chain** is the new attack surface. A single prompt injection — direct or indirect — can chain through `read_file → send_email` and exfiltrate your AWS credentials before you blink. Existing MCP scanners flag tools in **isolation**. They miss the *combinations*.

**AgentHound** treats your AI agent's environment as a graph and finds every path an attacker could walk:

```
[chat input] ──INJECTS──▶ [Claude Desktop] ──USES──▶ [filesystem]
                                                          │
                                                          ▼
                                          ──READS──▶ [~/.aws/credentials]
                                                          │
                                                          ▼
                                          ──CALLS──▶ [send_email] ──▶ attacker@evil
```

> Inspired by [BloodHound](https://github.com/SpecterOps/BloodHound) — which became the standard for Active Directory attack-path analysis. We're doing the same for the AI agent ecosystem.

## Features

- 🧭 **Attack-path graph** — every Source → Sink walk in your environment
- 🎨 **React Flow UI** — interactive, dark-themed, animated paths
- 📊 **Severity scoring** — CVSS-inspired 0–10 risk score per path
- 🔍 **Six attack classes** — credential theft, tool poisoning, indirect prompt injection, data exfiltration, command injection, privilege escalation
- 📦 **MCP-first** — parses Claude Desktop / Cursor configs, with adapters for `tools/list`
- 🛠️ **CLI + REST API + Web UI** — pick your interface
- 🐍 **Python 3.14, MIT-licensed** — `pip install agenthound` and you're scanning

## Quick start (60 seconds)

```bash
pip install agenthound          # or: uv pip install agenthound
agenthound scan                 # runs against the bundled sample environment
agenthound paths --severity critical
agenthound serve                # FastAPI on :8765
```

Then open the web UI:

```bash
git clone https://github.com/Dolphinllc/agenthound
cd agenthound/frontend && pnpm install && pnpm dev
```

→ <http://localhost:3000>

## What gets scanned

| Source                                          | Status |
|-------------------------------------------------|--------|
| Claude Desktop `claude_desktop_config.json`     | ✅      |
| Cursor MCP settings                             | ✅      |
| MCP `tools/list` JSON-RPC catalogs              | ✅      |
| Claude Agent SDK config                         | 🚧      |
| LangChain agent definitions                     | 🚧      |
| OpenAI Assistants / Responses API tool specs    | 🚧      |

## Architecture

```
┌──────────────┐    ┌────────────────┐    ┌──────────────────┐    ┌─────────────┐
│ Config       │ ─▶ │ Parsers        │ ─▶ │ NetworkX Graph   │ ─▶ │ Path        │
│ (json/yaml)  │    │ (Pydantic)     │    │ + Threat sources │    │ analyzer    │
└──────────────┘    └────────────────┘    └──────────────────┘    └─────────────┘
                                                                          │
                            ┌─────────────────────────────────────────────┘
                            ▼
                ┌──────────────────────────────────┐
                │ FastAPI (REST + JSON ScanResult) │
                └──────────────┬───────────────────┘
                               │
                ┌──────────────┴───────────────────┐
                ▼                                  ▼
        ┌───────────────┐              ┌───────────────────────┐
        │ Typer CLI     │              │ Next.js + React Flow  │
        └───────────────┘              └───────────────────────┘
```

The graph engine is **pure NetworkX** — no database. Everything is JSON-serializable. Persistence (Neo4j/Memgraph) is on the roadmap for large environments.

## Sample output

```
─────────────────── AgentHound scan summary ───────────────────
Nodes: 38   Edges: 41   Attack paths: 72
┏━━━━━━━━━━┳━━━━━━━┓
┃ Severity ┃ Count ┃
┡━━━━━━━━━━╇━━━━━━━┩
│ critical │     3 │
│ high     │    48 │
│ medium   │    21 │
│ low      │     0 │
└──────────┴───────┘
```

## Roadmap

- [x] MVP: parser → graph → analyzer → CLI/UI
- [x] Threat-source heuristics (chat, web fetch, tool poisoning)
- [ ] Live MCP server probing (`agenthound probe stdio://server`)
- [ ] Cypher-style query language for power users
- [ ] AgentHound Cloud — managed scanning + team dashboards
- [ ] CI plugin (`agenthound check` for pre-merge gating)
- [ ] Federation: share anonymized attack-path corpora to grow the catalog

## Comparison

|                          | AgentHound | mcp-scan / Snyk Agent Scan | Cisco MCP Scanner | OWASP MCP Top 10 |
|--------------------------|:----------:|:--------------------------:|:-----------------:|:----------------:|
| Static tool inspection   | ✅          | ✅                          | ✅                 | docs only        |
| **Multi-hop attack paths** | ✅✨        | ❌                          | ❌                 | ❌                |
| **Interactive graph UI** | ✅✨        | ❌                          | ❌                 | ❌                |
| Severity-scored paths    | ✅          | partial                    | ❌                 | ❌                |
| Local-first / no cloud   | ✅          | ✅                          | ✅                 | n/a              |
| OSS license              | MIT        | Apache-2.0                 | Apache-2.0        | CC               |

We **cooperate**, not compete: AgentHound consumes findings from `mcp-scan` and friends as additional graph signal.

## Contributing

We welcome PRs, issues, and new attack patterns. See [CONTRIBUTING.md](CONTRIBUTING.md) and [good first issues](https://github.com/Dolphinllc/agenthound/labels/good%20first%20issue).

To report a vulnerability **in AgentHound itself**, see [SECURITY.md](SECURITY.md).

## Citing AgentHound

If you use AgentHound in research or in a public report, please cite:

```bibtex
@software{agenthound2026,
  title  = {AgentHound: BloodHound for AI Agents},
  author = {{Dolphin LLC}},
  year   = {2026},
  url    = {https://github.com/Dolphinllc/agenthound}
}
```

## License

MIT © 2026 [Dolphin LLC](https://github.com/Dolphinllc) — see [LICENSE](LICENSE).
