"use client";

import { Star, Radar } from "lucide-react";

export function Topbar({ onRescan, scanning }: { onRescan: () => void; scanning: boolean }) {
  return (
    <header className="flex h-14 items-center justify-between border-b border-border bg-background/80 px-4 backdrop-blur">
      <div className="flex items-center gap-3">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-soft text-brand">
          <Radar size={18} strokeWidth={2.4} />
        </div>
        <div>
          <h1 className="text-sm font-semibold leading-none">
            AgentHound
          </h1>
          <p className="text-[10px] uppercase tracking-[0.2em] text-text-dim">
            BloodHound for AI agents
          </p>
        </div>
      </div>
      <div className="flex items-center gap-2">
        <button
          onClick={onRescan}
          disabled={scanning}
          className="inline-flex items-center gap-2 rounded-md border border-border bg-surface px-3 py-1.5 text-[12px] font-medium text-text transition-colors hover:bg-surface-2 disabled:opacity-50"
        >
          <span
            className={
              scanning
                ? "h-1.5 w-1.5 rounded-full bg-brand animate-pulse-soft"
                : "h-1.5 w-1.5 rounded-full bg-brand"
            }
          />
          {scanning ? "Scanning…" : "Re-scan"}
        </button>
        <a
          href="https://github.com/dolphin-llc/agenthound"
          target="_blank"
          rel="noreferrer"
          className="inline-flex h-8 w-8 items-center justify-center rounded-md border border-border bg-surface text-text-muted transition-colors hover:bg-surface-2 hover:text-text"
          aria-label="GitHub"
        >
          <Star size={14} />
        </a>
      </div>
    </header>
  );
}
