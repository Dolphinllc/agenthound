# Contributing to AgentHound

Thanks for considering contributing! AgentHound aims to become the canonical
attack-path tool for AI agent environments — that only happens if researchers,
defenders, and red-teamers all push it forward.

## Where help is most welcome

1. **New attack patterns.** Edit [`catalog/attack_patterns.py`](src/agenthound/catalog/attack_patterns.py) — add keyword rules, poisoning regexes, or new sensitive paths.
2. **New parsers.** Cursor, Cline, Continue, Claude Agent SDK, LangChain, OpenAI Assistants — anything that exposes a tool list.
3. **UI polish.** React Flow layouts, custom node renderers, accessibility, docs site.
4. **Real-world MCP server fingerprints.** If you've audited a public MCP server, open a PR adding it to `data/known_servers.json`.

## Local development

```bash
git clone https://github.com/Dolphinllc/agenthound
cd agenthound

# Backend
uv sync
uv run agenthound scan          # smoke test
uv run pytest                   # tests

# Frontend
cd frontend
pnpm install
pnpm dev                        # http://localhost:3000
```

## Code conventions

- Python: `ruff format`, `ruff check`, type hints required, Pydantic for IO boundaries.
- TypeScript: strict mode, `bun run lint`, no `any`.
- Tests: pytest for backend, target ≥ 80% coverage on `parsers/`, `graph/`, `catalog/`.

## Pull request flow

1. Fork → branch (`feat/parse-cursor`, `fix/path-dedup`, etc.)
2. `uv run pytest` and `uv run ruff check` must pass.
3. Open the PR with: what, why, and a screenshot if UI is touched.
4. We review within 3 business days.

## Code of conduct

Be kind. Assume good intent. Disagree on technical grounds, never personal.
We follow the [Contributor Covenant 2.1](https://www.contributor-covenant.org/version/2/1/code_of_conduct/).

## License of contributions

By contributing, you agree your work is released under the project's [MIT License](LICENSE).
