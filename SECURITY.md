# Security policy

AgentHound is a defensive tool — but defensive tools have bugs too. Thank you
for reporting them responsibly.

## Reporting a vulnerability

Please **do not** open a public GitHub issue. Instead:

1. Email **security@Dolphinllc.example** (PGP key on request) with:
   - A description of the issue
   - Steps to reproduce, ideally with a minimal config
   - The version (`agenthound --version`) and platform
2. We will acknowledge within **2 business days** and aim for a fix or
   mitigation within **14 days** for high-severity issues.
3. Once a patch is ready we'll coordinate disclosure with you, including a CVE
   request if appropriate.

## Scope

In scope:
- The `agenthound` Python package (parsers, graph engine, server, CLI)
- The Next.js web UI under `frontend/`
- Sample data and configs distributed with releases

Out of scope:
- Vulnerabilities in third-party MCP servers themselves
  (please report those upstream — AgentHound *describes* them, doesn't ship them)
- Issues already tracked in our public issue tracker

## Hall of fame

Researchers who have responsibly disclosed issues:

*(none yet — be the first!)*
