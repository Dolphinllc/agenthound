"use client";

import { ArrowRight, Lightbulb, X } from "lucide-react";

import type { AttackPath } from "@/lib/types";
import { ATTACK_TYPE_LABEL, KIND_LABEL, NODE_PALETTE, SEVERITY_BG, SEVERITY_COLOR, SEVERITY_LABEL } from "@/lib/visual";
import { formatScore } from "@/lib/utils";

type Props = {
  path: AttackPath | null;
  onClose: () => void;
};

export function PathDetail({ path, onClose }: Props) {
  if (!path) return null;
  const sev = SEVERITY_COLOR[path.severity];
  return (
    <aside className="flex h-full flex-col border-l border-border bg-surface">
      <header className="flex items-start gap-3 border-b border-border px-4 py-3">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <span
              className="inline-flex items-center rounded-md px-2 py-0.5 text-[11px] font-mono font-semibold tracking-wider"
              style={{
                background: SEVERITY_BG[path.severity],
                color: sev,
                border: `1px solid ${sev}55`,
              }}
            >
              {SEVERITY_LABEL[path.severity]} · {formatScore(path.risk_score)}
            </span>
            <span className="text-[11px] uppercase tracking-wider text-text-muted">
              {ATTACK_TYPE_LABEL[path.attack_type]}
            </span>
          </div>
          <h2 className="mt-2 text-[15px] font-semibold leading-snug text-text">
            {path.title}
          </h2>
        </div>
        <button
          onClick={onClose}
          className="rounded-md p-1 text-text-muted transition-colors hover:bg-surface-2 hover:text-text"
          aria-label="Close detail panel"
        >
          <X size={16} />
        </button>
      </header>

      <div className="flex-1 overflow-y-auto px-4 py-4">
        <section>
          <h3 className="mb-2 text-[11px] font-semibold uppercase tracking-wider text-text-muted">
            Path
          </h3>
          <ol className="space-y-2">
            {path.steps.map((step, idx) => {
              const palette = NODE_PALETTE[step.node.kind];
              return (
                <li key={`${step.node.id}-${idx}`} className="relative">
                  <div
                    className="flex items-start gap-3 rounded-lg border px-3 py-2"
                    style={{
                      background: palette.fill,
                      borderColor: `${palette.ring}55`,
                    }}
                  >
                    <div
                      className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-md font-mono text-[10px] font-bold"
                      style={{ background: `${palette.ring}25`, color: palette.ring }}
                    >
                      {idx + 1}
                    </div>
                    <div className="min-w-0 flex-1">
                      <div
                        className="text-[10px] font-mono uppercase tracking-wider"
                        style={{ color: palette.ring }}
                      >
                        {KIND_LABEL[step.node.kind]}
                      </div>
                      <div className="truncate text-[13px] font-medium text-text">
                        {step.node.label}
                      </div>
                      {step.incoming_edge && (
                        <div className="mt-1 flex items-center gap-1 text-[10px] font-mono text-text-dim">
                          <ArrowRight size={10} />
                          <span>{step.incoming_edge.kind.replace(/_/g, " ")}</span>
                        </div>
                      )}
                    </div>
                  </div>
                </li>
              );
            })}
          </ol>
        </section>

        <section className="mt-5">
          <h3 className="mb-2 text-[11px] font-semibold uppercase tracking-wider text-text-muted">
            Description
          </h3>
          <p className="text-[13px] leading-relaxed text-text">{path.description}</p>
        </section>

        {path.mitigation && (
          <section className="mt-5 rounded-lg border border-brand/30 bg-brand-soft/40 px-3 py-3">
            <div className="mb-1.5 flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-brand">
              <Lightbulb size={12} /> Mitigation
            </div>
            <p className="text-[12.5px] leading-relaxed text-text">{path.mitigation}</p>
          </section>
        )}
      </div>
    </aside>
  );
}
