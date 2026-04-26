"use client";

import type { ScanSummary } from "@/lib/types";
import { SEVERITY_COLOR, SEVERITY_LABEL } from "@/lib/visual";

type Props = { summary: ScanSummary };

const SEVERITIES = ["critical", "high", "medium", "low"] as const;

export function SummaryBar({ summary }: Props) {
  return (
    <div className="flex items-center gap-3 px-4 py-2.5 border-b border-border bg-surface/60 backdrop-blur">
      <Stat label="Nodes" value={summary.total_nodes} />
      <Divider />
      <Stat label="Edges" value={summary.total_edges} />
      <Divider />
      <Stat label="Paths" value={summary.total_paths} accent />
      <Divider />
      <div className="flex items-center gap-2">
        {SEVERITIES.map((s) => (
          <Pill
            key={s}
            label={SEVERITY_LABEL[s]}
            color={SEVERITY_COLOR[s]}
            count={summary.by_severity[s] ?? 0}
          />
        ))}
      </div>
    </div>
  );
}

function Stat({ label, value, accent }: { label: string; value: number; accent?: boolean }) {
  return (
    <div className="flex items-baseline gap-1.5">
      <span className="text-[11px] uppercase tracking-wider text-text-muted">{label}</span>
      <span
        className="font-mono text-base font-semibold"
        style={accent ? { color: "var(--color-brand)" } : undefined}
      >
        {value}
      </span>
    </div>
  );
}

function Divider() {
  return <div className="h-4 w-px bg-border" />;
}

function Pill({ label, color, count }: { label: string; color: string; count: number }) {
  return (
    <div
      className="inline-flex items-center gap-1.5 rounded-md border px-1.5 py-0.5 text-[10px] font-mono font-semibold tracking-wider"
      style={{
        background: `${color}12`,
        borderColor: `${color}40`,
        color,
      }}
    >
      <span>{label}</span>
      <span className="opacity-80">{count}</span>
    </div>
  );
}
