"use client";

import { useCallback, useEffect, useState } from "react";

import { AttackGraph } from "@/components/graph/AttackGraph";
import { EmptyState } from "@/components/EmptyState";
import { PathDetail } from "@/components/PathDetail";
import { PathList } from "@/components/PathList";
import { SummaryBar } from "@/components/SummaryBar";
import { Topbar } from "@/components/Topbar";
import { fetchSampleScan } from "@/lib/api";
import type { AttackPath, ScanResult } from "@/lib/types";

export default function Home() {
  const [scan, setScan] = useState<ScanResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [scanning, setScanning] = useState(false);
  const [selectedPath, setSelectedPath] = useState<AttackPath | null>(null);

  const runScan = useCallback(async () => {
    setScanning(true);
    setError(null);
    try {
      const result = await fetchSampleScan();
      setScan(result);
      setSelectedPath(result.paths[0] ?? null);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setScanning(false);
    }
  }, []);

  useEffect(() => {
    runScan();
  }, [runScan]);

  return (
    <div className="flex h-screen w-screen flex-col overflow-hidden">
      <Topbar onRescan={runScan} scanning={scanning} />
      {scan && <SummaryBar summary={scan.summary} />}
      <div className="grid min-h-0 flex-1 grid-cols-[320px_1fr_400px]">
        <section className="min-h-0 border-r border-border bg-surface/60">
          {scan ? (
            <PathList
              paths={scan.paths}
              selectedId={selectedPath?.id ?? null}
              onSelect={setSelectedPath}
            />
          ) : (
            <SkeletonList />
          )}
        </section>
        <main className="relative min-h-0">
          {error && <ErrorBanner message={error} />}
          {scan ? (
            <AttackGraph
              graph={scan.graph}
              selectedPath={selectedPath}
              onSelectNode={() => {}}
            />
          ) : (
            <SkeletonGraph />
          )}
        </main>
        <section className="min-h-0">
          {selectedPath ? (
            <PathDetail path={selectedPath} onClose={() => setSelectedPath(null)} />
          ) : (
            <EmptyState />
          )}
        </section>
      </div>
    </div>
  );
}

function ErrorBanner({ message }: { message: string }) {
  return (
    <div className="absolute left-1/2 top-4 z-10 -translate-x-1/2 rounded-lg border border-sev-critical/50 bg-sev-critical/10 px-4 py-2 text-[12px] text-sev-critical">
      <span className="font-mono uppercase tracking-wider">scan failed</span>
      <span className="ml-2 text-text">{message}</span>
      <span className="ml-2 text-text-muted">— is the API running on :8765?</span>
    </div>
  );
}

function SkeletonList() {
  return (
    <div className="flex h-full flex-col">
      <div className="border-b border-border px-4 py-3 text-[11px] uppercase tracking-wider text-text-muted">
        Loading paths…
      </div>
      <div className="flex-1 space-y-2 px-4 py-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="h-14 animate-pulse-soft rounded-lg border border-border bg-surface" />
        ))}
      </div>
    </div>
  );
}

function SkeletonGraph() {
  return (
    <div className="flex h-full items-center justify-center text-text-muted">
      <div className="flex flex-col items-center gap-3">
        <div className="h-10 w-10 animate-pulse-soft rounded-full border-2 border-brand border-t-transparent" />
        <p className="font-mono text-[11px] uppercase tracking-wider">
          mapping attack surface…
        </p>
      </div>
    </div>
  );
}
