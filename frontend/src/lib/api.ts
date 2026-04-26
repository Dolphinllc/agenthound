import type { ScanResult } from "./types";

const DEFAULT_API_BASE =
  process.env.NEXT_PUBLIC_AGENTHOUND_API ?? "http://127.0.0.1:8765";

export async function fetchSampleScan(
  apiBase: string = DEFAULT_API_BASE,
): Promise<ScanResult> {
  const res = await fetch(`${apiBase}/api/scan/sample`, {
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Scan failed: ${res.status} ${res.statusText}`);
  }
  return (await res.json()) as ScanResult;
}
