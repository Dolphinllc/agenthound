export type NodeKind =
  | "source"
  | "agent"
  | "mcp_server"
  | "tool"
  | "resource"
  | "secret"
  | "sink";

export type EdgeKind =
  | "injects_into"
  | "uses"
  | "exposes"
  | "reads"
  | "writes"
  | "calls"
  | "contains";

export type TrustLevel = "untrusted" | "partial" | "trusted";

export type Severity = "critical" | "high" | "medium" | "low";

export type AttackType =
  | "data_exfiltration"
  | "credential_theft"
  | "tool_poisoning"
  | "indirect_prompt_injection"
  | "command_injection"
  | "privilege_escalation";

export type GraphNode = {
  id: string;
  kind: NodeKind;
  label: string;
  trust: TrustLevel;
  metadata: Record<string, string | number | boolean | null>;
};

export type GraphEdge = {
  id: string;
  source: string;
  target: string;
  kind: EdgeKind;
  metadata: Record<string, string | number | boolean | null>;
};

export type Graph = {
  nodes: GraphNode[];
  edges: GraphEdge[];
};

export type AttackPathStep = {
  node: GraphNode;
  incoming_edge: GraphEdge | null;
};

export type AttackPath = {
  id: string;
  title: string;
  description: string;
  attack_type: AttackType;
  severity: Severity;
  risk_score: number;
  steps: AttackPathStep[];
  mitigation: string | null;
};

export type ScanSummary = {
  total_nodes: number;
  total_edges: number;
  total_paths: number;
  by_severity: Record<string, number>;
  by_attack_type: Record<string, number>;
};

export type ScanResult = {
  schema_version: "1";
  graph: Graph;
  paths: AttackPath[];
  summary: ScanSummary;
};
