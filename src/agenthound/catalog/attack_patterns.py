"""Heuristic catalog used during graph construction.

Maps tool descriptions, names, and metadata to canonical *capabilities*
(read, write, network egress, secret access, etc.) so the analyzer can
search the resulting graph for attack-shaped paths.

This is intentionally pragmatic: a small ruleset catches the most common
MCP server categories while keeping the catalog easy to extend.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

from agenthound.models import EdgeKind


@dataclass(frozen=True)
class CapabilityRule:
    capability: EdgeKind
    target: str
    target_label: str
    target_kind: str
    keywords: tuple[str, ...]


_RULES: tuple[CapabilityRule, ...] = (
    CapabilityRule(EdgeKind.READS, "fs:any", "Local filesystem", "resource",
                   ("read_file", "list_directory", "open_file")),
    CapabilityRule(EdgeKind.WRITES, "fs:any", "Local filesystem", "resource",
                   ("write_file", "create_file", "edit_file", "move_file", "delete_file")),
    CapabilityRule(EdgeKind.READS, "git:repo", "GitHub repositories", "resource",
                   ("get_file_contents", "search_code", "list_commits", "search_repositories")),
    CapabilityRule(EdgeKind.WRITES, "git:repo", "GitHub repositories", "resource",
                   ("create_or_update_file", "push_files", "create_pull_request", "merge_pull_request")),
    CapabilityRule(EdgeKind.READS, "mail:inbox", "User Gmail inbox", "resource",
                   ("search_messages", "read_message", "list_messages")),
    CapabilityRule(EdgeKind.CALLS, "sink:email", "Outbound email (any address)", "sink",
                   ("send_email", "send_mail", "compose_email")),
    CapabilityRule(EdgeKind.CALLS, "sink:slack", "Slack workspace messages", "sink",
                   ("post_message", "send_message", "chat_post")),
    CapabilityRule(EdgeKind.CALLS, "sink:http", "Arbitrary external HTTP endpoint", "sink",
                   ("fetch", "http_get", "http_post", "request", "curl", "open_url")),
)


def match_capabilities(tool_name: str, description: str) -> Iterable[CapabilityRule]:
    needle = f"{tool_name.lower()} {description.lower()}"
    for rule in _RULES:
        if any(re.search(rf"\b{re.escape(kw)}\b", needle) for kw in rule.keywords):
            yield rule


# Heuristic patterns for *Tool Poisoning* — hidden instructions in tool
# descriptions targeting the LLM rather than the human user. Source:
# Invariant Labs (Apr 2025) plus follow-up research from Snyk and CSA.
_POISON_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(p, re.IGNORECASE | re.DOTALL) for p in (
        r"<\s*important\s*>.*?<\s*/\s*important\s*>",
        r"do not (?:mention|tell|reveal).{0,80}(?:user|system)",
        r"before using this tool,?\s*(?:read|fetch|load)",
        r"system\s+requirement",
        r"hidden\s+instruction",
        r"ignore (?:previous|prior) (?:instructions|messages)",
    )
)


def detect_tool_poisoning(description: str) -> list[str]:
    matches: list[str] = []
    for pat in _POISON_PATTERNS:
        if pat.search(description):
            matches.append(pat.pattern)
    return matches


# Common locations of secrets that file-reading tools may inadvertently
# expose. Used to plant Secret nodes that hang off the filesystem Resource.
SENSITIVE_PATHS: tuple[tuple[str, str], ...] = (
    ("~/.aws/credentials", "AWS credentials"),
    ("~/.ssh/id_rsa", "SSH private key"),
    ("~/.netrc", "Network credentials"),
    ("~/.env", "Project .env file"),
    ("~/.config/gh/hosts.yml", "GitHub CLI token"),
    ("~/Library/Application Support/Claude/claude_desktop_config.json", "Other MCP server tokens"),
)
