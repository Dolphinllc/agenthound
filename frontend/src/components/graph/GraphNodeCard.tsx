"use client";

import { Handle, Position } from "@xyflow/react";
import {
  Bot,
  Bug,
  Database,
  KeyRound,
  Send,
  Server,
  Wrench,
  type LucideIcon,
} from "lucide-react";
import { memo } from "react";

import type { NodeKind, Severity, TrustLevel } from "@/lib/types";
import { KIND_LABEL, NODE_PALETTE, SEVERITY_COLOR } from "@/lib/visual";
import { cn } from "@/lib/utils";

const ICONS: Record<NodeKind, LucideIcon> = {
  source: Bug,
  agent: Bot,
  mcp_server: Server,
  tool: Wrench,
  resource: Database,
  secret: KeyRound,
  sink: Send,
};

type Data = {
  label: string;
  kind: NodeKind;
  trust: TrustLevel;
  highlighted: boolean;
  severity: Severity | null;
  metadata: Record<string, string | number | boolean | null>;
};

export const GraphNodeCard = memo(function GraphNodeCard({ data }: { data: Data }) {
  const palette = NODE_PALETTE[data.kind];
  const Icon = ICONS[data.kind];
  const sevColor = data.severity ? SEVERITY_COLOR[data.severity] : palette.ring;
  const ring = data.highlighted ? sevColor : palette.ring;

  return (
    <div
      className={cn(
        "group relative flex min-w-[160px] max-w-[220px] flex-col gap-1 rounded-xl border px-3 py-2 backdrop-blur",
        "transition-all duration-200",
      )}
      style={{
        background: palette.fill,
        borderColor: ring,
        boxShadow: data.highlighted
          ? `0 0 0 2px ${ring}30, 0 0 24px ${ring}55`
          : `0 0 0 1px ${ring}25`,
      }}
    >
      <Handle type="target" position={Position.Left} style={{ opacity: 0 }} />
      <div className="flex items-center gap-2">
        <div
          className="flex h-6 w-6 shrink-0 items-center justify-center rounded-md"
          style={{ background: `${ring}18`, color: ring }}
        >
          <Icon size={14} strokeWidth={2.2} />
        </div>
        <div className="min-w-0 flex-1">
          <div
            className="truncate text-[10px] font-mono uppercase tracking-wider"
            style={{ color: ring }}
          >
            {KIND_LABEL[data.kind]}
          </div>
          <div className="truncate text-[13px] font-medium leading-tight text-text">
            {data.label}
          </div>
        </div>
      </div>
      {data.trust === "untrusted" && (
        <div className="mt-1 inline-flex w-fit items-center gap-1 rounded-md border border-sev-critical/40 bg-sev-critical/10 px-1.5 py-0.5 text-[9px] font-mono uppercase tracking-wide text-sev-critical">
          untrusted
        </div>
      )}
      <Handle type="source" position={Position.Right} style={{ opacity: 0 }} />
    </div>
  );
});
