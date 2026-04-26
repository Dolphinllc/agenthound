"use client";

import { ChevronRight, ShieldAlert } from "lucide-react";

import type { AttackPath } from "@/lib/types";
import { ATTACK_TYPE_LABEL, SEVERITY_BG, SEVERITY_COLOR, SEVERITY_LABEL } from "@/lib/visual";
import { cn, formatScore } from "@/lib/utils";

type Props = {
  paths: AttackPath[];
  selectedId: string | null;
  onSelect: (path: AttackPath) => void;
};

export function PathList({ paths, selectedId, onSelect }: Props) {
  const sorted = [...paths].sort((a, b) => b.risk_score - a.risk_score);

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between border-b border-border px-4 py-3">
        <div className="flex items-center gap-2">
          <ShieldAlert size={16} className="text-brand" />
          <h2 className="text-sm font-semibold uppercase tracking-wider text-text-muted">
            Attack Paths
          </h2>
        </div>
        <span className="rounded-full border border-border bg-surface px-2 py-0.5 text-[11px] font-mono text-text-muted">
          {paths.length}
        </span>
      </div>
      <div className="flex-1 overflow-y-auto">
        {sorted.map((path) => {
          const selected = path.id === selectedId;
          return (
            <button
              key={path.id}
              onClick={() => onSelect(path)}
              className={cn(
                "group block w-full border-b border-border px-4 py-3 text-left transition-colors",
                "hover:bg-surface",
                selected && "bg-surface-2",
              )}
              style={
                selected
                  ? { boxShadow: `inset 3px 0 0 0 ${SEVERITY_COLOR[path.severity]}` }
                  : undefined
              }
            >
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <span
                      className="inline-flex items-center rounded-md px-1.5 py-0.5 text-[10px] font-mono font-semibold tracking-wider"
                      style={{
                        background: SEVERITY_BG[path.severity],
                        color: SEVERITY_COLOR[path.severity],
                        border: `1px solid ${SEVERITY_COLOR[path.severity]}40`,
                      }}
                    >
                      {SEVERITY_LABEL[path.severity]}
                    </span>
                    <span className="font-mono text-[11px] text-text-muted">
                      {formatScore(path.risk_score)}
                    </span>
                    <span className="ml-auto text-[10px] uppercase tracking-wider text-text-dim">
                      {ATTACK_TYPE_LABEL[path.attack_type]}
                    </span>
                  </div>
                  <p className="mt-1.5 line-clamp-2 text-[12.5px] leading-snug text-text">
                    {path.title}
                  </p>
                  <p className="mt-1 line-clamp-1 text-[11px] text-text-dim">
                    {path.steps.length} hops · {path.id}
                  </p>
                </div>
                <ChevronRight
                  size={14}
                  className={cn(
                    "mt-1 shrink-0 text-text-dim transition-transform",
                    selected && "translate-x-0.5 text-text",
                  )}
                />
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
