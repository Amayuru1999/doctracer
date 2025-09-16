import { useEffect, useMemo, useState } from "react";
import ForceGraph2D from "react-force-graph-2d";
import { 
  getAmendments, 
  getAmendmentGraph, 
  getCompleteGraph,
  getGazettes,
  searchGazettes,
  type Amendment, 
  type GraphData,
  type Gazette 
} from "../services/api";

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

type ViewMode = 'complete' | 'amendment' | 'base';

export default function NetworkGraph() {
  const [amendments, setAmendments] = useState<Amendment[]>([]);
  const [gazettes, setGazettes] = useState<Gazette[]>([]);
  const [selected, setSelected] = useState<string>("");
  const [viewMode, setViewMode] = useState<ViewMode>('complete');
  const [graph, setGraph] = useState<GraphData>({ nodes: [], links: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | undefined>();
  const [searchQuery, setSearchQuery] = useState<string>("");

  // Load initial data
  useEffect(() => {
    (async () => {
      try {
        setError(undefined);
        setLoading(true);
        const [amendmentsList, gazettesList] = await Promise.all([
          getAmendments(),
          getGazettes()
        ]);
        setAmendments(amendmentsList);
        setGazettes(gazettesList);
        
        // Set default selection based on view mode
        if (viewMode === 'complete') {
          // Load complete graph immediately
          await loadCompleteGraph();
        } else if (viewMode === 'amendment' && amendmentsList[0]?.gazette_id) {
          setSelected(amendmentsList[0].gazette_id);
        } else if (viewMode === 'base' && gazettesList[0]?.gazette_id) {
          setSelected(gazettesList[0].gazette_id);
        }
      } catch (e: any) {
        setError(e?.message ?? String(e));
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  // Load graph data based on view mode and selection
  useEffect(() => {
    if (viewMode === 'complete') {
      loadCompleteGraph();
    } else if (selected) {
      loadSelectedGraph();
    }
  }, [selected, viewMode]);

  const loadCompleteGraph = async () => {
    try {
      setLoading(true);
      setError(undefined);
      const g = await getCompleteGraph();
      setGraph(g);
    } catch (e: any) {
      setError(e?.message ?? String(e));
    } finally {
      setLoading(false);
    }
  };

  const loadSelectedGraph = async () => {
    if (!selected) return;
    try {
      setLoading(true);
      setError(undefined);
      let g: GraphData;
      
      if (viewMode === 'amendment') {
        g = await getAmendmentGraph(selected);
      } else {
        // For base gazettes, we'll use the complete graph filtered
        g = await getCompleteGraph();
        // Filter to show only related nodes
        const relatedNodes = new Set([selected]);
        const relatedLinks = g.links.filter(link => 
          link.source === selected || link.target === selected
        );
        
        // Add connected nodes
        relatedLinks.forEach(link => {
          relatedNodes.add(link.source);
          relatedNodes.add(link.target);
        });
        
        g = {
          nodes: g.nodes.filter(node => relatedNodes.has(node.id)),
          links: relatedLinks
        };
      }
      
      setGraph(g);
    } catch (e: any) {
      setError(e?.message ?? String(e));
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    try {
      setLoading(true);
      setError(undefined);
      const results = await searchGazettes(searchQuery, viewMode === 'amendment' ? 'amendment' : viewMode === 'base' ? 'base' : 'all');
      
      if (viewMode === 'amendment') {
        setAmendments(results as Amendment[]);
      } else {
        setGazettes(results);
      }
    } catch (e: any) {
      setError(e?.message ?? String(e));
    } finally {
      setLoading(false);
    }
  };

  const data = useMemo(() => ({
    nodes: graph.nodes.map(n => ({ ...n })),
    links: graph.links.map(l => ({ ...l })),
  }), [graph]);

  const currentList = viewMode === 'amendment' ? amendments : gazettes;

  return (
    <section className="space-y-4">
      <div className="flex items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Gazette Network Graph</h1>
          <p className="text-slate-500">Interactive visualization of gazette relationships and amendments.</p>
        </div>
        
        <div className="flex gap-3">
          {/* View Mode Selector */}
          <div className="bg-white border border-slate-200 rounded-xl p-3 shadow-sm">
            <label className="block text-sm text-slate-600 mb-1">View Mode</label>
            <select
              className="rounded-lg border-slate-300"
              value={viewMode}
              onChange={(e) => {
                setViewMode(e.target.value as ViewMode);
                setSelected("");
              }}
            >
              <option value="complete">Complete Graph</option>
              <option value="amendment">Amendment Focus</option>
              <option value="base">Base Gazette Focus</option>
            </select>
          </div>

          {/* Gazette Selector */}
          {viewMode !== 'complete' && (
            <div className="bg-white border border-slate-200 rounded-xl p-3 shadow-sm">
              <label className="block text-sm text-slate-600 mb-1">
                {viewMode === 'amendment' ? 'Amendment' : 'Base'} Gazette
              </label>
              <select
                className="rounded-lg border-slate-300"
                value={selected}
                onChange={(e) => setSelected(e.target.value)}
              >
                <option value="">Select a gazette...</option>
                {currentList.map(item => (
                  <option key={item.gazette_id} value={item.gazette_id}>
                    {item.gazette_id} — {item.published_date}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>
      </div>

      {/* Search Bar */}
      <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
        <div className="flex gap-3">
          <input
            type="text"
            placeholder={`Search ${viewMode === 'amendment' ? 'amendments' : viewMode === 'base' ? 'base gazettes' : 'gazettes'}...`}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="flex-1 rounded-lg border-slate-300 px-3 py-2"
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
          <button
            onClick={handleSearch}
            className="px-4 py-2 bg-sky-600 text-white rounded-lg hover:bg-sky-700 transition-colors"
          >
            Search
          </button>
          <button
            onClick={() => {
              setSearchQuery("");
              // Reload original data
              if (viewMode === 'amendment') {
                getAmendments().then(setAmendments);
              } else {
                getGazettes().then(setGazettes);
              }
            }}
            className="px-4 py-2 bg-slate-600 text-white rounded-lg hover:bg-slate-700 transition-colors"
          >
            Reset
          </button>
        </div>
      </div>

      {error && <div className="text-red-600 text-sm bg-red-50 p-3 rounded-lg">{error}</div>}
      {loading && <div className="text-slate-500 bg-slate-50 p-3 rounded-lg">Loading graph data...</div>}

      <div className="grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-4">
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm h-[680px] overflow-hidden">
          <ForceGraph2D
            graphData={data}
            nodeCanvasObject={(node: any, ctx, scale) => {
              const r = 8;
              const color = colors[node.kind] ?? "#6b7280";
              ctx.fillStyle = color;
              ctx.beginPath();
              ctx.arc(node.x, node.y, r, 0, 2*Math.PI, false);
              ctx.fill();

              // Add border for better visibility
              ctx.strokeStyle = "#ffffff";
              ctx.lineWidth = 2;
              ctx.stroke();

              const label = node.label || node.id;
              const fontSize = Math.max(10, 14 / Math.sqrt(scale));
              ctx.font = `${fontSize}px sans-serif`;
              ctx.fillStyle = "#111827";
              ctx.textAlign = "center";
              ctx.fillText(label, node.x, node.y + r + fontSize + 2);
            }}
            linkColor={(l: any) => colors[l.kind] ?? "#94a3b8"}
            linkWidth={2}
            linkDirectionalParticles={3}
            linkDirectionalParticleWidth={2}
            linkDirectionalParticleSpeed={0.01}
            cooldownTicks={150}
            onNodeClick={(node: any) => {
              console.log('Node clicked:', node);
              // You can add more interactive features here
            }}
            onLinkClick={(link: any) => {
              console.log('Link clicked:', link);
              // You can add more interactive features here
            }}
            onEngineStop={() => {/* layout stabilized */}}
          />
        </div>

        <aside className="bg-white rounded-2xl border border-slate-200 shadow-sm p-4 space-y-6">
          <div>
            <h2 className="text-sm font-semibold text-slate-700 mb-3">Legend</h2>
            <div className="space-y-2 text-sm">
              {[
                ["Amendment Gazette","amendment"],
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
          </div>

          <div>
            <h3 className="text-sm font-semibold text-slate-700 mb-2">Graph Statistics</h3>
            <div className="text-sm text-slate-600 space-y-1">
              <div>Nodes: {graph.nodes.length}</div>
              <div>Links: {graph.links.length}</div>
              <div>Amendments: {graph.nodes.filter(n => n.kind === 'amendment').length}</div>
              <div>Base Gazettes: {graph.nodes.filter(n => n.kind === 'base').length}</div>
            </div>
          </div>

          <div>
            <h3 className="text-sm font-semibold text-slate-700 mb-2">Controls</h3>
            <div className="text-slate-500 text-sm space-y-1">
              <div>• Drag nodes to move them</div>
              <div>• Scroll to zoom in/out</div>
              <div>• Click nodes/links for details</div>
              <div>• Use view modes to filter data</div>
            </div>
          </div>

          <div>
            <h3 className="text-sm font-semibold text-slate-700 mb-2">Current View</h3>
            <div className="text-slate-500 text-sm">
              {viewMode === 'complete' && 'Showing all gazettes and their relationships'}
              {viewMode === 'amendment' && selected && `Showing amendment ${selected} and related gazettes`}
              {viewMode === 'base' && selected && `Showing base gazette ${selected} and related amendments`}
              {viewMode !== 'complete' && !selected && 'Select a gazette to view its relationships'}
            </div>
          </div>
        </aside>
      </div>
    </section>
  );
}