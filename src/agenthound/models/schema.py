"""Core data model: nodes, edges, and attack paths.

The AgentHound graph models how an AI agent's tool chain can be exploited.
Untrusted **Sources** can inject instructions that flow through **Agents**,
**MCPServers** and **Tools** to ultimately reach **Sinks** (external egress
points), often via **Resources** that hold **Secrets**.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class NodeKind(StrEnum):
    SOURCE = "source"
    AGENT = "agent"
    MCP_SERVER = "mcp_server"
    TOOL = "tool"
    RESOURCE = "resource"
    SECRET = "secret"
    SINK = "sink"


class EdgeKind(StrEnum):
    INJECTS_INTO = "injects_into"
    USES = "uses"
    EXPOSES = "exposes"
    READS = "reads"
    WRITES = "writes"
    CALLS = "calls"
    CONTAINS = "contains"


class TrustLevel(StrEnum):
    UNTRUSTED = "untrusted"
    PARTIAL = "partial"
    TRUSTED = "trusted"


class Node(BaseModel):
    id: str
    kind: NodeKind
    label: str
    trust: TrustLevel = TrustLevel.TRUSTED
    metadata: dict[str, str | int | float | bool | None] = Field(default_factory=dict)


class Edge(BaseModel):
    id: str
    source: str
    target: str
    kind: EdgeKind
    metadata: dict[str, str | int | float | bool | None] = Field(default_factory=dict)


class Graph(BaseModel):
    nodes: list[Node]
    edges: list[Edge]


class AttackPathStep(BaseModel):
    node: Node
    incoming_edge: Edge | None = None


class AttackType(StrEnum):
    DATA_EXFILTRATION = "data_exfiltration"
    CREDENTIAL_THEFT = "credential_theft"
    TOOL_POISONING = "tool_poisoning"
    INDIRECT_PROMPT_INJECTION = "indirect_prompt_injection"
    COMMAND_INJECTION = "command_injection"
    PRIVILEGE_ESCALATION = "privilege_escalation"


class Severity(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AttackPath(BaseModel):
    id: str
    title: str
    description: str
    attack_type: AttackType
    severity: Severity
    risk_score: float = Field(ge=0.0, le=10.0)
    steps: list[AttackPathStep]
    mitigation: str | None = None


class ScanSummary(BaseModel):
    total_nodes: int
    total_edges: int
    total_paths: int
    by_severity: dict[str, int]
    by_attack_type: dict[str, int]


class ScanResult(BaseModel):
    schema_version: Literal["1"] = "1"
    graph: Graph
    paths: list[AttackPath]
    summary: ScanSummary
