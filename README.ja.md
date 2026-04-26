<div align="center">

# 🐕 AgentHound

### *AIエージェントのための BloodHound*

**AIエージェントのMCPツールチェーンを通る「攻撃経路」を、攻撃者より先に可視化する。**

[🇺🇸 English](README.md) · 🇯🇵 日本語 (現在のページ) · [🇨🇳 简体中文](README.zh-CN.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-ff5b3a.svg)](LICENSE)
[![Python 3.14+](https://img.shields.io/badge/python-3.14+-5fb4ff.svg)](https://www.python.org/downloads/release/python-3140/)
[![Built by Dolphin LLC](https://img.shields.io/badge/built%20by-Dolphin%20LLC-b478ff.svg)](https://github.com/Dolphinllc)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-5feaa1.svg)](CONTRIBUTING.md)

<img src="docs/hero.png" alt="AgentHoundがチャット入力からClaude DesktopのMCPツールを経由してGitHubトークン漏洩までの攻撃パスを可視化している様子" width="100%" />

</div>

---

## なぜ AgentHound か？

**MCP ツールチェーン**は新しい攻撃面です。一回のプロンプトインジェクション（直接または間接）が `read_file → send_email` を連鎖させ、AWS認証情報を一瞬で外部送信し得る。既存のMCPスキャナはツールを **個別に** 評価しており、**組み合わせ** の危険を見逃します。

**AgentHound** は、AIエージェントの環境をグラフとしてモデル化し、攻撃者が辿りうる **すべての経路** を発見します。

```
[ユーザー入力] ──注入──▶ [Claude Desktop] ──使用──▶ [filesystem]
                                                          │
                                                          ▼
                                          ──読込──▶ [~/.aws/credentials]
                                                          │
                                                          ▼
                                          ──呼出──▶ [send_email] ──▶ attacker@evil
```

> Active Directory の標準解析ツール [BloodHound](https://github.com/SpecterOps/BloodHound) にインスパイアされた、AIエージェント版です。

## 特徴

- 🧭 **攻撃経路グラフ** — 環境内のすべての Source → Sink 経路を可視化
- 🎨 **React Flow UI** — ダークテーマ、インタラクティブ、攻撃経路をアニメーション
- 📊 **重大度スコア** — CVSS型の0–10スコアを各経路に付与
- 🔍 **6種の攻撃クラス** — 認証情報窃取、ツールポイズニング、間接プロンプトインジェクション、データ流出、コマンドインジェクション、権限昇格
- 📦 **MCP対応** — Claude Desktop / Cursor の設定をパース、`tools/list` のJSON-RPCも対応
- 🛠️ **CLI + REST API + Web UI** — 用途で選べる
- 🐍 **Python 3.14, MIT** — `pip install agenthound` で即時利用可能

## クイックスタート（60秒）

```bash
pip install agenthound          # または: uv pip install agenthound
agenthound scan                 # 同梱サンプル環境をスキャン
agenthound paths --severity critical
agenthound serve                # FastAPI を :8765 で起動
```

Web UI を起動：

```bash
git clone https://github.com/Dolphinllc/agenthound
cd agenthound/frontend && pnpm install && pnpm dev
```

→ <http://localhost:3000>

## スキャン対応

| ソース                                         | 状況 |
|----------------------------------------------|:----:|
| Claude Desktop `claude_desktop_config.json`  | ✅   |
| Cursor MCP 設定                               | ✅   |
| MCP `tools/list` JSON-RPC catalog            | ✅   |
| Claude Agent SDK                              | 🚧   |
| LangChain Agent                               | 🚧   |
| OpenAI Assistants / Responses API            | 🚧   |

## アーキテクチャ

```
┌──────────────┐    ┌────────────────┐    ┌──────────────────┐    ┌─────────────┐
│ 設定ファイル │ ─▶ │ Parser         │ ─▶ │ NetworkX グラフ  │ ─▶ │ 経路解析    │
│ (json/yaml)  │    │ (Pydantic)     │    │ + 脅威ソース注入 │    │             │
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

グラフエンジンは **純 NetworkX** — DBなし、すべてJSON。大規模環境向けの永続化（Neo4j/Memgraph）はロードマップにあります。

## サンプル出力

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

## ロードマップ

- [x] MVP: parser → graph → analyzer → CLI/UI
- [x] 脅威ソースのヒューリスティック（chat、web fetch、tool poisoning）
- [ ] MCPサーバの実機プローブ (`agenthound probe stdio://server`)
- [ ] Cypher 風クエリ言語
- [ ] AgentHound Cloud — マネージド・チームダッシュボード
- [ ] CIプラグイン（PR前のゲート用）
- [ ] 攻撃経路コーパスのフェデレーション

## 既存ツールとの比較

|                                | AgentHound | mcp-scan / Snyk Agent Scan | Cisco MCP Scanner | OWASP MCP Top 10 |
|--------------------------------|:----------:|:--------------------------:|:-----------------:|:----------------:|
| 静的ツール検査                 | ✅         | ✅                         | ✅                | ドキュメントのみ |
| **多段攻撃経路解析**           | ✅✨       | ❌                         | ❌                | ❌               |
| **インタラクティブグラフUI**   | ✅✨       | ❌                         | ❌                | ❌               |
| 重大度スコア付き経路           | ✅         | 部分的                     | ❌                | ❌               |
| ローカルファースト             | ✅         | ✅                         | ✅                | n/a              |
| OSS ライセンス                 | MIT        | Apache-2.0                 | Apache-2.0        | CC               |

競合ではなく **協調** を目指します — `mcp-scan` などの結果も追加シグナルとして取り込みます。

## コントリビュート

PR・Issue・新しい攻撃パターンを歓迎します。[CONTRIBUTING.md](CONTRIBUTING.md) と [good first issues](https://github.com/Dolphinllc/agenthound/labels/good%20first%20issue) をご覧ください。

AgentHound 自体の脆弱性報告は [SECURITY.md](SECURITY.md) を参照してください。

## 引用

研究や公開レポートで AgentHound を利用される際は以下のように引用してください：

```bibtex
@software{agenthound2026,
  title  = {AgentHound: BloodHound for AI Agents},
  author = {{Dolphin LLC}},
  year   = {2026},
  url    = {https://github.com/Dolphinllc/agenthound}
}
```

## ライセンス

MIT © 2026 [Dolphin LLC](https://github.com/Dolphinllc) — [LICENSE](LICENSE) を参照。
