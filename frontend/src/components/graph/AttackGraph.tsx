"use client";

import {
  Background,
  BackgroundVariant,
  Controls,
  type Edge as RFEdge,
  MiniMap,
  type Node as RFNode,
  ReactFlow,
  ReactFlowProvider,
  useReactFlow,
} from "@xyflow/react";
import { useEffect, useMemo } from "react";

import type { AttackPath, Graph } from "@/lib/types";
import { NODE_PALETTE, SEVERITY_COLOR } from "@/lib/visual";
import { GraphNodeCard } from "./GraphNodeCard";

const NODE_TYPES = { agentNode: GraphNodeCard };

type Props = {
  graph: Graph;
  selectedPath: AttackPath | null;
  onSelectNode?: (nodeId: string) => void;
};

export function AttackGraph({ graph, selectedPath, onSelectNode }: Props) {
  const layout = useMemo(() => layoutGraph(graph), [graph]);

  const nodes: RFNode[] = useMemo(() => {
    const highlighted = new Set(selectedPath?.steps.map((s) => s.node.id) ?? []);
    return layout.nodes.map((n) => ({
      id: n.id,
      type: "agentNode",
      position: n.position,
      data: {
        label: n.label,
        kind: n.kind,
        trust: n.trust,
        highlighted: highlighted.has(n.id),
        severity: selectedPath?.severity ?? null,
        metadata: n.metadata,
      },
      draggable: true,
    }));
  }, [layout, selectedPath]);

  const edges: RFEdge[] = useMemo(() => {
    const pathEdgeIds = new Set(
      (selectedPath?.steps
        .map((s) => s.incoming_edge?.id)
        .filter(Boolean) as string[]) ?? [],
    );
    return graph.edges.map((e) => {
      const isOnPath = pathEdgeIds.has(e.id);
      const sevClass = selectedPath
        ? selectedPath.severity === "critical"
          ? "attack-path"
          : selectedPath.severity === "high"
            ? "attack-high"
            : "attack-medium"
        : "";
      return {
        id: e.id,
        source: e.source,
        target: e.target,
        type: "default",
        animated: false,
        className: isOnPath ? sevClass : "",
        style: isOnPath
          ? { stroke: SEVERITY_COLOR[selectedPath!.severity] }
          : undefined,
        label: e.kind.replace(/_/g, " "),
        labelStyle: {
          fill: isOnPath ? SEVERITY_COLOR[selectedPath!.severity] : "#5b6275",
          fontSize: 10,
          fontFamily: "var(--font-mono)",
        },
        labelBgStyle: { fill: "transparent" },
        labelShowBg: false,
      } satisfies RFEdge;
    });
  }, [graph, selectedPath]);

  return (
    <ReactFlowProvider>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={NODE_TYPES}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        minZoom={0.2}
        maxZoom={2}
        proOptions={{ hideAttribution: true }}
        onNodeClick={(_, n) => onSelectNode?.(n.id)}
      >
        <Background variant={BackgroundVariant.Dots} gap={28} size={1.2} color="#1c2030" />
        <Controls position="bottom-left" />
        <MiniMap
          position="bottom-right"
          pannable
          zoomable
          nodeColor={(n) =>
            NODE_PALETTE[(n.data?.kind as keyof typeof NODE_PALETTE) ?? "agent"].ring
          }
          maskColor="rgba(7,8,12,0.8)"
        />
        <FitOnPathChange selectedPathId={selectedPath?.id ?? null} />
      </ReactFlow>
    </ReactFlowProvider>
  );
}

function FitOnPathChange({ selectedPathId }: { selectedPathId: string | null }) {
  const rf = useReactFlow();
  useEffect(() => {
    if (!selectedPathId) return;
    const t = window.setTimeout(() => rf.fitView({ padding: 0.25, duration: 600 }), 50);
    return () => window.clearTimeout(t);
  }, [selectedPathId, rf]);
  return null;
}

// Layout ------------------------------------------------------------

const COL_X: Record<string, number> = {
  source: 0,
  agent: 320,
  mcp_server: 640,
  tool: 960,
  resource: 1280,
  sink: 1600,
  secret: 1600,
};
const ROW_GAP = 110;

function layoutGraph(graph: Graph) {
  const groups = new Map<string, typeof graph.nodes>();
  for (const n of graph.nodes) {
    const list = groups.get(n.kind) ?? [];
    list.push(n);
    groups.set(n.kind, list);
  }
  const nodes = graph.nodes.map((n) => {
    const list = groups.get(n.kind) ?? [];
    const i = list.indexOf(n);
    const total = list.length;
    const y = (i - (total - 1) / 2) * ROW_GAP;
    return {
      ...n,
      position: { x: COL_X[n.kind] ?? 0, y },
    };
  });
  return { nodes };
}
