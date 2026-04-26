# OSS launch plan — AgentHound

## North-star metric

**1,000 GitHub stars in 90 days.** Comparable: BloodHound's first-year arc, Lakera Guard's launch traction.

## T-minus checklist (before announce)

- [ ] `README.md` with hero image / GIF (`docs/hero.png`, `docs/demo.gif`)
- [ ] `LICENSE` (MIT) ✅
- [ ] `CONTRIBUTING.md` ✅
- [ ] `SECURITY.md` ✅
- [ ] `CODE_OF_CONDUCT.md` ✅
- [ ] `CHANGELOG.md` ✅
- [ ] CI: GitHub Actions (`pytest`, `ruff`, `bun run build`)
- [ ] PyPI release (`agenthound 0.1.0`)
- [ ] Docs site (`mkdocs-material`) at `docs.agenthound.dev`
- [ ] 5–10 `good-first-issue` tickets pre-seeded
- [ ] Discord server with #welcome, #showcase, #help, #attack-corpus
- [ ] Twitter/X account `@agenthoundsec`

## Launch day — coordinated drop

1. **08:00 JST** — push `v0.1.0` tag, PyPI release, GitHub release with notes
2. **09:00 JST** — Show HN: *"Show HN: AgentHound – BloodHound for AI agents"*
3. **09:00 JST** — X thread (5 posts): screenshot → problem statement → demo gif → call to action → install snippet
4. **10:00 JST** — Reddit: `r/netsec`, `r/cybersecurity`, `r/MachineLearning` (only if substantive)
5. **11:00 JST** — Submit to `awesome-llm-security`, `awesome-mcp`, `awesome-ai-security`
6. **14:00 JST** — Product Hunt launch
7. **End of day** — post recap + thanks on X / blog

## Companion blog post

**Title**: "We Scanned the 100 Most Popular Public MCP Servers — Here's What We Found"

Outline:
1. The combinatorial-attack problem (visual)
2. Method: ran AgentHound across the catalog of public MCP servers
3. Findings:
   - X% have at least one CRITICAL path to credential theft
   - Y% expose tool descriptions matching known poisoning regexes
   - Top 5 most dangerous combinations
4. What this means for Claude Desktop / Cursor users
5. How to scan your own setup in 60 seconds
6. Roadmap + how to contribute

Designed for HN front page + cited in subsequent vendor research.

## Conference circuit (T+30 to T+180)

- DEFCON AI Village CFP (June)
- BlackHat Arsenal CFP (May for Aug)
- JSAC (Japan Security Analyst Conference) lightning talk
- mcpcon / AI Security Summit (sponsor + booth)

## Partnership angles

- **Anthropic** — Claude Desktop is the primary target → DevRel intro
- **Snyk** — they own `mcp-scan`; co-publish the corpus rather than duplicate
- **OWASP MCP Top 10 working group** — submit AgentHound as the canonical detection toolkit
- **Cloud Security Alliance MCP-Security** — list under `awesome-mcp-security`

## Three-month milestones

| Week | Milestone |
|------|-----------|
| 1    | Launch, 100 stars, first 5 external contributors |
| 4    | 250 stars, 3 new parsers (Cursor, LangChain, OpenAI), first conference talk submitted |
| 8    | 500 stars, blog post 2 ("AgentHound Cypher: Querying Your Agent's Attack Surface") |
| 12   | 1,000 stars, AgentHound Cloud private beta opens for Dolphin LLC clients |

## Anti-goals (avoid)

- ❌ Becoming "yet another MCP scanner" — always lead with **paths**, not findings.
- ❌ Premature monetization — do not gate the analyzer or graph engine.
- ❌ Cloning competitors' rule sets without attribution.
