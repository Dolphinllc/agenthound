"use client";

import { MousePointerClick } from "lucide-react";

export function EmptyState() {
  return (
    <div className="flex h-full flex-col items-center justify-center gap-3 border-l border-border bg-surface/40 p-8 text-center">
      <div className="flex h-10 w-10 items-center justify-center rounded-full border border-border bg-surface text-text-muted">
        <MousePointerClick size={18} />
      </div>
      <p className="text-[13px] text-text-muted">
        Select an attack path on the left to inspect its hops, severity, and mitigation.
      </p>
    </div>
  );
}
