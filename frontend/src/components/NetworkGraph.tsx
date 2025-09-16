import { useEffect, useMemo, useState } from "react";
import ForceGraph2D from "react-force-graph-2d";
import { getAmendments, getAmendmentGraph, type Amendment, type GraphPayload } from "../services/api";

const colors: Record<string, string> = {
  amendment: "#0ea5e9",
  base: "#64748b",
  minister: "#1d4ed8",
  INSERTION: "#16a34a",
  UPDATE: "#f59e0b",
  DELETION: "#ef4444",
  CHANGE: "#6b7280",
  item: "#6b7280",
};

export default function NetworkGraph() {
  const [amendments, setAmendments] = useState<Amendment[]>([]);
  const [selected, setSelected] = useState<string>("");
  const [graph, setGraph] = useState<GraphPayload>({ nodes: [], links: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | undefined>();

  useEffect(() => {
    (async () => {
      try {
        setError(undefined);
        const list = await getAmendments();
        setAmendments(list);
        if (list[0]?.gazette_id) setSelected(list[0].gazette_id);
      } catch (e: any) {
        setError(e?.message ?? String(e));
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  useEffect(() => {
    if (!selected) return;
    (async () => {
      try {
        setLoading(true);
        setError(undefined);
        const g = await getAmendmentGraph(selected);
        setGraph(g);
      } catch (e: any) {
        setError(e?.message ?? String(e));
      } finally {
        setLoading(false);
      }
    })();
  }, [selected]);

  const data = useMemo(() => ({
    nodes: graph.nodes.map(n => ({ ...n })),
    links: graph.links.map(l => ({ ...l })),
  }), [graph]);

  return (
    <section className="space-y-4">
      <div className="flex items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Amendment Network</h1>
          <p className="text-slate-500">Inspect inserts, updates, and deletions per amendment.</p>
        </div>
        <div className="bg-white border border-slate-200 rounded-xl p-3 shadow-sm">
          <label className="block text-sm text-slate-600 mb-1">Amendment gazette</label>
          <select
            className="rounded-lg border-slate-300"
            value={selected}
            onChange={(e) => setSelected(e.target.value)}
          >
            {amendments.map(a => (
              <option key={a.gazette_id} value={a.gazette_id}>
                {a.gazette_id} — {a.published_date}
              </option>
            ))}
          </select>
        </div>
      </div>

      {error && <div className="text-red-600 text-sm">{error}</div>}
      {loading && <div className="text-slate-500">Loading…</div>}

      <div className="grid grid-cols-1 lg:grid-cols-[1fr_280px] gap-4">
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm h-[680px] overflow-hidden">
          <ForceGraph2D
            graphData={data}
            nodeCanvasObject={(node: any, ctx, scale) => {
              const r = 6;
              const color = colors[node.kind] ?? "#6b7280";
              ctx.fillStyle = color;
              ctx.beginPath();
              ctx.arc(node.x, node.y, r, 0, 2*Math.PI, false);
              ctx.fill();

              const label = node.label || node.id;
              const fontSize = 12 / Math.sqrt(scale);
              ctx.font = `${fontSize}px sans-serif`;
              ctx.fillStyle = "#111827";
              ctx.fillText(label, node.x + r + 3, node.y + r);
            }}
            linkColor={(l: any) => colors[l.kind] ?? "#94a3b8"}
            linkDirectionalParticles={2}
            linkDirectionalParticleWidth={1}
            cooldownTicks={150}
            onEngineStop={() => {/* layout stabilized */}}
          />
        </div>

        <aside className="bg-white rounded-2xl border border-slate-200 shadow-sm p-4">
          <h2 className="text-sm font-semibold text-slate-700 mb-3">Legend</h2>
          <div className="space-y-2 text-sm">
            {[
              ["Amendment","amendment"],
              ["Base Gazette","base"],
              ["Minister","minister"],
              ["Insertion","INSERTION"],
              ["Update","UPDATE"],
              ["Deletion","DELETION"],
            ].map(([label, key]) => (
              <div key={key} className="flex items-center gap-2">
                <span className="inline-block h-3 w-3 rounded-full" style={{background: colors[key]}} />
                <span className="text-slate-700">{label}</span>
              </div>
            ))}
          </div>
          <div className="mt-6">
            <h3 className="text-sm font-semibold text-slate-700 mb-1">Tip</h3>
            <p className="text-slate-500 text-sm">
              Hover labels show the change text. Use the selector above to switch amendments.
            </p>
          </div>
        </aside>
      </div>
    </section>
  );
}