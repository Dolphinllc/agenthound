import type { NodeKind, Severity, AttackType } from "./types";

export const NODE_PALETTE: Record<NodeKind, { fill: string; ring: string; icon: string }> = {
  source: { fill: "#2a1410", ring: "#ff5b3a", icon: "Bug" },
  agent: { fill: "#0e1a2c", ring: "#5fb4ff", icon: "Bot" },
  mcp_server: { fill: "#1d1130", ring: "#b478ff", icon: "Server" },
  tool: { fill: "#0e2517", ring: "#5feaa1", icon: "Wrench" },
  resource: { fill: "#28210a", ring: "#ffd23a", icon: "Database" },
  secret: { fill: "#2a0e0e", ring: "#ff3b3b", icon: "KeyRound" },
  sink: { fill: "#2a1024", ring: "#ff66c4", icon: "Send" },
};

export const SEVERITY_LABEL: Record<Severity, string> = {
  critical: "CRITICAL",
  high: "HIGH",
  medium: "MEDIUM",
  low: "LOW",
};

export const SEVERITY_COLOR: Record<Severity, string> = {
  critical: "#ff3b3b",
  high: "#ff8b3a",
  medium: "#ffd23a",
  low: "#5fb4ff",
};

export const SEVERITY_BG: Record<Severity, string> = {
  critical: "rgba(255, 59, 59, 0.12)",
  high: "rgba(255, 139, 58, 0.12)",
  medium: "rgba(255, 210, 58, 0.12)",
  low: "rgba(95, 180, 255, 0.12)",
};

export const ATTACK_TYPE_LABEL: Record<AttackType, string> = {
  data_exfiltration: "Data Exfiltration",
  credential_theft: "Credential Theft",
  tool_poisoning: "Tool Poisoning",
  indirect_prompt_injection: "Indirect Prompt Injection",
  command_injection: "Command Injection",
  privilege_escalation: "Privilege Escalation",
};

export const KIND_LABEL: Record<NodeKind, string> = {
  source: "Threat Source",
  agent: "AI Agent",
  mcp_server: "MCP Server",
  tool: "Tool",
  resource: "Resource",
  secret: "Secret",
  sink: "Egress Sink",
};
