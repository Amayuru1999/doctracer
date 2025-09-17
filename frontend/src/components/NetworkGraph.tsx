import { useEffect, useMemo, useState } from "react";
import ForceGraph2D from "react-force-graph-2d";
import { 
  getAmendments, 
  getAmendmentGraph, 
  getCompleteGraph,
  getGazettes,
  searchGazettes,
  getGovernmentStructureEvolution,
  getGovernmentEvolutionFromBase,
  compareGazetteStructures,
  debugDatabaseStructure,
  type Amendment, 
  type GraphData,
  type Gazette,
  type GovernmentEvolution,
  type GovernmentEvolutionFromBase,
  type GazetteComparison
} from "../services/api";
import MinistryStructureGraph from "./MinistryStructureGraph";
import AmendmentTracker from "./AmendmentTracker";

const colors: Record<string, string> = {
  amendment: "#0ea5e9",
  base: "#64748b",
  minister: "#1d4ed8",
  department: "#16a34a",
  law: "#f59e0b",
  INSERTION: "#16a34a",
  UPDATE: "#f59e0b",
  DELETION: "#ef4444",
  CHANGE: "#6b7280",
  item: "#6b7280",
  has_minister: "#3b82f6",
  manages: "#10b981",
  oversees: "#f59e0b",
};

type ViewMode = 'complete' | 'amendment' | 'base' | 'government-evolution' | 'comparison' | 'ministry-structure' | 'amendment-tracking';

export default function NetworkGraph() {
  const [amendments, setAmendments] = useState<Amendment[]>([]);
  const [gazettes, setGazettes] = useState<Gazette[]>([]);
  const [selected, setSelected] = useState<string>("");
  const [viewMode, setViewMode] = useState<ViewMode>('complete');
  const [graph, setGraph] = useState<GraphData>({ nodes: [], links: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | undefined>();
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [evolutionData, setEvolutionData] = useState<GovernmentEvolution | null>(null);
  const [evolutionFromBase, setEvolutionFromBase] = useState<GovernmentEvolutionFromBase | null>(null);
  const [currentTimelineIndex, setCurrentTimelineIndex] = useState<number>(0);
  const [comparisonData, setComparisonData] = useState<any>(null);
  const [baseForComparison, setBaseForComparison] = useState<string>("");
  const [amendmentForComparison, setAmendmentForComparison] = useState<string>("");
  const [debugInfo, setDebugInfo] = useState<any>(null);

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
        
        console.log('Loaded amendments:', amendmentsList.length);
        console.log('Loaded gazettes:', gazettesList.length);
        
        // Set default selection based on view mode
        if (viewMode === 'complete') {
          // Load complete graph immediately
          await loadCompleteGraph();
        } else if (viewMode === 'government-evolution') {
          // Load evolution data immediately
          await loadEvolutionData();
        } else if (viewMode === 'comparison') {
          // Load comparison data if both gazettes are selected
          if (baseForComparison && amendmentForComparison) {
            await loadComparisonData();
          }
        } else if (viewMode === 'amendment' && amendmentsList[0]?.gazette_id) {
          setSelected(amendmentsList[0].gazette_id);
        } else if (viewMode === 'base' && gazettesList[0]?.gazette_id) {
          setSelected(gazettesList[0].gazette_id);
        }
      } catch (e: any) {
        setError(e?.message ?? String(e));
        console.error('Error in initial data load:', e);
        // Set empty graph as fallback
        setGraph({ nodes: [], links: [] });
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  // Load graph data based on view mode and selection
  useEffect(() => {
    if (viewMode === 'complete') {
      loadCompleteGraph();
    } else if (viewMode === 'government-evolution') {
      if (selected) {
        loadEvolutionFromBase(selected);
      } else {
        loadEvolutionData();
      }
    } else if (viewMode === 'comparison') {
      if (baseForComparison && amendmentForComparison) {
        loadComparisonData();
      }
    } else if (selected) {
      loadSelectedGraph();
    }
  }, [selected, viewMode]);

  const loadCompleteGraph = async () => {
    try {
      setError(undefined);
      const g = await getCompleteGraph();
      console.log('Complete graph data:', g);
      setGraph(g);
    } catch (e: any) {
      setError(e?.message ?? String(e));
      console.error('Error loading complete graph:', e);
    }
  };

  const loadSelectedGraph = async () => {
    if (!selected) return;
    try {
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
    }
  };

  const loadEvolutionData = async () => {
    try {
      setError(undefined);
      const evolution = await getGovernmentStructureEvolution();
      console.log('Evolution data:', evolution);
      setEvolutionData(evolution);
      setCurrentTimelineIndex(0);
      
      // Convert first evolution step to graph data
      if (evolution.evolution.length > 0) {
        const graphData = convertEvolutionToGraph(evolution.evolution[0]);
        console.log('Converted graph data:', graphData);
        setGraph(graphData);
      } else {
        console.log('No evolution data found');
        setGraph({ nodes: [], links: [] });
      }
    } catch (e: any) {
      setError(e?.message ?? String(e));
      console.error('Error loading evolution data:', e);
    }
  };

  const loadEvolutionFromBase = async (baseId: string) => {
    try {
      setError(undefined);
      const evolution = await getGovernmentEvolutionFromBase(baseId);
      setEvolutionFromBase(evolution);
      setCurrentTimelineIndex(0);
      
      // Convert first evolution step to graph data
      if (evolution.evolution.length > 0) {
        const graphData = convertEvolutionToGraph(evolution.evolution[0]);
        setGraph(graphData);
      }
    } catch (e: any) {
      setError(e?.message ?? String(e));
    }
  };

  const convertEvolutionToGraph = (evolutionStep: any): GraphData => {
    const nodes: any[] = [];
    const links: any[] = [];
    const nodeIds = new Set();

    // Add gazette node
    const gazette = evolutionStep.gazette;
    nodes.push({
      id: gazette.id,
      label: `${gazette.type === 'base' ? 'Base' : 'Amendment'} ${gazette.id}`,
      kind: gazette.type,
      published_date: gazette.published_date,
      type: 'gazette'
    });
    nodeIds.add(gazette.id);

    // Add minister and department nodes
    evolutionStep.structure.ministers.forEach((minister: any) => {
      if (!nodeIds.has(minister.name)) {
        nodes.push({
          id: minister.name,
          label: minister.name,
          kind: 'minister',
          type: 'minister'
        });
        nodeIds.add(minister.name);
      }

      // Add link from gazette to minister
      links.push({
        source: gazette.id,
        target: minister.name,
        kind: 'has_minister'
      });

      // Add department nodes and links
      minister.departments.forEach((dept: string) => {
        if (!nodeIds.has(dept)) {
          nodes.push({
            id: dept,
            label: dept,
            kind: 'department',
            type: 'department'
          });
          nodeIds.add(dept);
        }

        links.push({
          source: minister.name,
          target: dept,
          kind: 'manages'
        });
      });

      // Add law nodes and links
      minister.laws.forEach((law: string) => {
        if (!nodeIds.has(law)) {
          nodes.push({
            id: law,
            label: law,
            kind: 'law',
            type: 'law'
          });
          nodeIds.add(law);
        }

        links.push({
          source: minister.name,
          target: law,
          kind: 'oversees'
        });
      });
    });

    return { nodes, links };
  };

  const loadComparisonData = async () => {
    if (!baseForComparison || !amendmentForComparison) return;
    
    try {
      setError(undefined);
      const comparison = await compareGazetteStructures(baseForComparison, amendmentForComparison);
      setComparisonData(comparison);
      
      // Create a combined graph showing both structures
      const combinedGraph = createComparisonGraph(comparison);
      setGraph(combinedGraph);
    } catch (e: any) {
      setError(e?.message ?? String(e));
    }
  };

  const createComparisonGraph = (comparison: GazetteComparison): GraphData => {
    const nodes: any[] = [];
    const links: any[] = [];
    const nodeIds = new Set();

    // Add base gazette node
    const baseGazette = comparison.base_gazette;
    nodes.push({
      id: `base-${baseGazette.id}`,
      label: `Base ${baseGazette.id}`,
      kind: 'base',
      type: 'gazette',
      published_date: baseGazette.published_date,
      structure: 'base'
    });
    nodeIds.add(`base-${baseGazette.id}`);

    // Add amendment gazette node
    const amendmentGazette = comparison.amendment_gazette;
    nodes.push({
      id: `amendment-${amendmentGazette.id}`,
      label: `Amendment ${amendmentGazette.id}`,
      kind: 'amendment',
      type: 'gazette',
      published_date: amendmentGazette.published_date,
      structure: 'amendment'
    });
    nodeIds.add(`amendment-${amendmentGazette.id}`);

    // Add ministers from both structures
    const allMinisters = new Set([
      ...baseGazette.structure.ministers.map(m => m.name),
      ...amendmentGazette.structure.ministers.map(m => m.name)
    ]);

    allMinisters.forEach(ministerName => {
      const baseMinister = baseGazette.structure.ministers.find(m => m.name === ministerName);
      const amendmentMinister = amendmentGazette.structure.ministers.find(m => m.name === ministerName);
      
      // Determine minister status
      let status = 'unchanged';
      if (!baseMinister) status = 'added';
      else if (!amendmentMinister) status = 'removed';
      else if (JSON.stringify(baseMinister.departments) !== JSON.stringify(amendmentMinister.departments)) {
        status = 'modified';
      }

      // Add minister node
      nodes.push({
        id: ministerName,
        label: ministerName,
        kind: 'minister',
        type: 'minister',
        status: status
      });
      nodeIds.add(ministerName);

      // Add links to gazettes
      if (baseMinister) {
        links.push({
          source: `base-${baseGazette.id}`,
          target: ministerName,
          kind: 'has_minister',
          structure: 'base'
        });
      }
      if (amendmentMinister) {
        links.push({
          source: `amendment-${amendmentGazette.id}`,
          target: ministerName,
          kind: 'has_minister',
          structure: 'amendment'
        });
      }

      // Add departments
      const allDepartments = new Set([
        ...(baseMinister?.departments || []),
        ...(amendmentMinister?.departments || [])
      ]);

      allDepartments.forEach(deptName => {
        if (!nodeIds.has(deptName)) {
          let deptStatus = 'unchanged';
          const inBase = baseMinister?.departments.includes(deptName);
          const inAmendment = amendmentMinister?.departments.includes(deptName);
          
          if (!inBase && inAmendment) deptStatus = 'added';
          else if (inBase && !inAmendment) deptStatus = 'removed';

          nodes.push({
            id: deptName,
            label: deptName,
            kind: 'department',
            type: 'department',
            status: deptStatus
          });
          nodeIds.add(deptName);
        }

        // Add links to minister
        if (baseMinister?.departments.includes(deptName)) {
          links.push({
            source: ministerName,
            target: deptName,
            kind: 'manages',
            structure: 'base'
          });
        }
        if (amendmentMinister?.departments.includes(deptName)) {
          links.push({
            source: ministerName,
            target: deptName,
            kind: 'manages',
            structure: 'amendment'
          });
        }
      });
    });

    return { nodes, links };
  };

  const loadDebugInfo = async () => {
    try {
      const debug = await debugDatabaseStructure();
      setDebugInfo(debug);
      console.log('Database structure:', debug);
    } catch (e: any) {
      console.error('Error loading debug info:', e);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    try {
      setError(undefined);
      const results = await searchGazettes(searchQuery, viewMode === 'amendment' ? 'amendment' : viewMode === 'base' ? 'base' : 'all');
      
      if (viewMode === 'amendment') {
        setAmendments(results as Amendment[]);
      } else {
        setGazettes(results);
      }
    } catch (e: any) {
      setError(e?.message ?? String(e));
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
          <p className="text-slate-500">Interactive visualization of gazette relationships, amendments, and government structure changes.</p>
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
                setCurrentTimelineIndex(0);
              }}
            >
              <option value="complete">Complete Graph</option>
              <option value="government-evolution">Government Evolution</option>
              <option value="comparison">Structure Comparison</option>
              <option value="ministry-structure">Ministry Structure</option>
              <option value="amendment-tracking">Amendment Tracking</option>
              <option value="amendment">Amendment Focus</option>
              <option value="base">Base Gazette Focus</option>
            </select>
          </div>

          {/* Gazette Selector for Ministry Structure */}
          {viewMode === 'ministry-structure' && (
            <div className="bg-white border border-slate-200 rounded-xl p-3 shadow-sm">
              <label className="block text-sm text-slate-600 mb-1">Base Gazette</label>
              <select
                className="rounded-lg border-slate-300"
                value={selected}
                onChange={(e) => setSelected(e.target.value)}
              >
                <option value="">Select a base gazette...</option>
                {gazettes.map(item => (
                  <option key={item.gazette_id} value={item.gazette_id}>
                    {item.gazette_id} — {item.published_date}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Gazette Selector */}
          {viewMode !== 'complete' && viewMode !== 'government-evolution' && viewMode !== 'comparison' && viewMode !== 'ministry-structure' && viewMode !== 'amendment-tracking' && (
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

          {/* Base Gazette Selector for Evolution */}
          {viewMode === 'government-evolution' && (
            <div className="bg-white border border-slate-200 rounded-xl p-3 shadow-sm">
              <label className="block text-sm text-slate-600 mb-1">Base Gazette</label>
              <select
                className="rounded-lg border-slate-300"
                value={selected}
                onChange={(e) => setSelected(e.target.value)}
              >
                <option value="">All Evolution</option>
                {gazettes.map(item => (
                  <option key={item.gazette_id} value={item.gazette_id}>
                    {item.gazette_id} — {item.published_date}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Comparison Selectors */}
          {viewMode === 'comparison' && (
            <>
              <div className="bg-white border border-slate-200 rounded-xl p-3 shadow-sm">
                <label className="block text-sm text-slate-600 mb-1">Base Gazette</label>
                <select
                  className="rounded-lg border-slate-300"
                  value={baseForComparison}
                  onChange={(e) => setBaseForComparison(e.target.value)}
                >
                  <option value="">Select base gazette...</option>
                  {gazettes.map(item => (
                    <option key={item.gazette_id} value={item.gazette_id}>
                      {item.gazette_id} — {item.published_date}
                    </option>
                  ))}
                </select>
              </div>
              <div className="bg-white border border-slate-200 rounded-xl p-3 shadow-sm">
                <label className="block text-sm text-slate-600 mb-1">Amendment Gazette</label>
                <select
                  className="rounded-lg border-slate-300"
                  value={amendmentForComparison}
                  onChange={(e) => setAmendmentForComparison(e.target.value)}
                >
                  <option value="">Select amendment gazette...</option>
                  {amendments.map(item => (
                    <option key={item.gazette_id} value={item.gazette_id}>
                      {item.gazette_id} — {item.published_date}
                    </option>
                  ))}
                </select>
              </div>
            </>
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
          <button
            onClick={loadDebugInfo}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            Debug DB
          </button>
        </div>
      </div>

      {error && <div className="text-red-600 text-sm bg-red-50 p-3 rounded-lg border border-red-200">
        <div className="flex items-center gap-2">
          <span>⚠️</span>
          <span>Error: {error}</span>
        </div>
      </div>}
      {loading && <div className="text-slate-600 bg-slate-50 p-4 rounded-lg border border-slate-200">
        <div className="flex items-center gap-3">
          <div className="animate-spin h-5 w-5 border-2 border-slate-300 border-t-slate-600 rounded-full"></div>
          <span>Loading graph data...</span>
        </div>
      </div>}

      {/* Debug Information */}
      {debugInfo && (
        <div className="bg-purple-50 border border-purple-200 rounded-xl p-4 shadow-sm">
          <h3 className="text-sm font-semibold text-purple-700 mb-2">Database Structure Debug</h3>
          <div className="text-xs text-purple-600 space-y-1">
            <div><strong>Node Types:</strong></div>
            {debugInfo.node_types?.map((nt: any, i: number) => (
              <div key={i} className="ml-2">• {nt.labels?.join(', ')}: {nt.count} nodes</div>
            ))}
            <div className="mt-2"><strong>Relationship Types:</strong></div>
            {debugInfo.relationship_types?.map((rt: any, i: number) => (
              <div key={i} className="ml-2">• {rt.type}: {rt.count} relationships</div>
            ))}
            <div className="mt-2"><strong>Sample Relationships:</strong></div>
            {debugInfo.sample_relationships?.slice(0, 3).map((sr: any, i: number) => (
              <div key={i} className="ml-2 text-xs">
                • {sr.gazette?.gazette_id} → {sr.relationship?.type} → {sr.entity?.labels?.join(', ')}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Timeline Controls for Evolution View */}
      {viewMode === 'government-evolution' && (evolutionData || evolutionFromBase) && (
        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <button
                onClick={() => {
                  const currentData = evolutionFromBase || evolutionData;
                  if (currentData && currentTimelineIndex > 0) {
                    setCurrentTimelineIndex(currentTimelineIndex - 1);
                    const graphData = convertEvolutionToGraph(currentData.evolution[currentTimelineIndex - 1]);
                    setGraph(graphData);
                  }
                }}
                disabled={currentTimelineIndex === 0}
                className="px-3 py-2 bg-slate-600 text-white rounded-lg hover:bg-slate-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                ← Previous
              </button>
              <span className="text-sm text-slate-600">
                Step {currentTimelineIndex + 1} of {(evolutionFromBase || evolutionData)?.evolution.length || 0}
              </span>
              <button
                onClick={() => {
                  const currentData = evolutionFromBase || evolutionData;
                  if (currentData && currentTimelineIndex < currentData.evolution.length - 1) {
                    setCurrentTimelineIndex(currentTimelineIndex + 1);
                    const graphData = convertEvolutionToGraph(currentData.evolution[currentTimelineIndex + 1]);
                    setGraph(graphData);
                  }
                }}
                disabled={currentTimelineIndex >= ((evolutionFromBase || evolutionData)?.evolution.length || 1) - 1}
                className="px-3 py-2 bg-slate-600 text-white rounded-lg hover:bg-slate-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next →
              </button>
            </div>
            <div className="text-sm text-slate-600">
              {(evolutionFromBase || evolutionData)?.evolution[currentTimelineIndex]?.gazette?.published_date && (
                <span>
                  {(evolutionFromBase || evolutionData)?.evolution[currentTimelineIndex]?.gazette?.type === 'base' ? 'Base' : 'Amendment'} Gazette: 
                  {(evolutionFromBase || evolutionData)?.evolution[currentTimelineIndex]?.gazette?.id} 
                  ({(evolutionFromBase || evolutionData)?.evolution[currentTimelineIndex]?.gazette?.published_date})
                </span>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Ministry Structure View */}
      {viewMode === 'ministry-structure' && (
        <MinistryStructureGraph 
          gazetteId={selected || undefined}
          showAll={!selected}
        />
      )}

      {/* Amendment Tracking View */}
      {viewMode === 'amendment-tracking' && (
        <AmendmentTracker 
          baseGazetteId={selected || undefined}
        />
      )}

      {/* Standard Graph Views */}
      {(viewMode !== 'ministry-structure' && viewMode !== 'amendment-tracking') && (
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-4">
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm h-[680px] overflow-hidden">
            <ForceGraph2D
            graphData={data}
            nodeCanvasObject={(node: any, ctx, scale) => {
              // Dynamic node sizing based on type
              let r = 8;
              if (node.kind === 'gazette' || node.type === 'gazette') {
                r = 12; // Larger for gazettes
              } else if (node.kind === 'minister') {
                r = 10; // Medium for ministers
              } else if (node.kind === 'department') {
                r = 8; // Standard for departments
              } else if (node.kind === 'law') {
                r = 6; // Smaller for laws
              }
              
              let color = colors[node.kind] ?? "#6b7280";
              
              // Special coloring for comparison view
              if (viewMode === 'comparison' && node.status) {
                if (node.status === 'added') color = '#16a34a';
                else if (node.status === 'removed') color = '#ef4444';
                else if (node.status === 'modified') color = '#f59e0b';
              }
              
              // Different colors for base vs amendment entities
              if (node.is_base === false && (node.kind === 'minister' || node.kind === 'department' || node.kind === 'law')) {
                // Amendment entities - lighter colors
                if (node.kind === 'minister') color = '#60a5fa'; // lighter blue
                else if (node.kind === 'department') color = '#4ade80'; // lighter green
                else if (node.kind === 'law') color = '#fbbf24'; // lighter orange
              }
              
              ctx.fillStyle = color;
              ctx.beginPath();
              ctx.arc(node.x, node.y, r, 0, 2*Math.PI, false);
              ctx.fill();

              // Add border for better visibility
              ctx.strokeStyle = "#ffffff";
              ctx.lineWidth = 2;
              ctx.stroke();

              // Add special styling for gazettes
              if (node.kind === 'gazette' || node.type === 'gazette') {
                ctx.strokeStyle = node.kind === 'base' ? "#1e40af" : "#0ea5e9";
                ctx.lineWidth = 3;
                ctx.stroke();
              }

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
              {viewMode === 'comparison' ? [
                ["Base Gazette","base"],
                ["Amendment Gazette","amendment"],
                ["Minister (Unchanged)","minister"],
                ["Minister (Added)","added"],
                ["Minister (Removed)","removed"],
                ["Minister (Modified)","modified"],
                ["Department","department"],
              ] : viewMode === 'government-evolution' ? [
                ["Amendment Gazette","amendment"],
                ["Base Gazette","base"],
                ["Base Minister","minister"],
                ["Amendment Minister","#60a5fa"],
                ["Base Department","department"],
                ["Amendment Department","#4ade80"],
                ["Base Law","law"],
                ["Amendment Law","#fbbf24"],
              ] : [
                ["Amendment Gazette","amendment"],
                ["Base Gazette","base"],
                ["Minister","minister"],
                ["Insertion","INSERTION"],
                ["Update","UPDATE"],
                ["Deletion","DELETION"],
              ].map(([label, key]) => (
                <div key={key} className="flex items-center gap-2">
                  <span className="inline-block h-3 w-3 rounded-full" style={{background: colors[key] || (key === 'added' ? '#16a34a' : key === 'removed' ? '#ef4444' : key === 'modified' ? '#f59e0b' : '#6b7280')}} />
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
              {viewMode === 'government-evolution' && (
                <>
                  <div>Ministers: {graph.nodes.filter(n => n.kind === 'minister').length}</div>
                  <div>Departments: {graph.nodes.filter(n => n.kind === 'department').length}</div>
                  <div>Laws: {graph.nodes.filter(n => n.kind === 'law').length}</div>
                </>
              )}
              {viewMode === 'comparison' && comparisonData && (
                <div className="pt-2 border-t border-slate-200">
                  <div className="text-xs text-slate-500">Changes</div>
                  <div>Added Ministers: {comparisonData.changes.added_ministers.length}</div>
                  <div>Removed Ministers: {comparisonData.changes.removed_ministers.length}</div>
                  <div>Modified Ministers: {comparisonData.changes.modified_ministers.length}</div>
                  <div>Added Departments: {comparisonData.changes.added_departments.length}</div>
                  <div>Removed Departments: {comparisonData.changes.removed_departments.length}</div>
                </div>
              )}
              {viewMode === 'government-evolution' && (evolutionData || evolutionFromBase) && (
                <div className="pt-2 border-t border-slate-200">
                  <div className="text-xs text-slate-500">Timeline</div>
                  <div>Total Steps: {(evolutionFromBase || evolutionData)?.evolution.length || 0}</div>
                  <div>Current Step: {currentTimelineIndex + 1}</div>
                </div>
              )}
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
              {viewMode === 'government-evolution' && selected && `Showing evolution from base gazette ${selected}`}
              {viewMode === 'government-evolution' && !selected && 'Showing government structure evolution over time'}
              {viewMode === 'comparison' && baseForComparison && amendmentForComparison && `Comparing ${baseForComparison} with ${amendmentForComparison}`}
              {viewMode === 'comparison' && (!baseForComparison || !amendmentForComparison) && 'Select base and amendment gazettes to compare'}
              {viewMode === 'amendment' && selected && `Showing amendment ${selected} and related gazettes`}
              {viewMode === 'base' && selected && `Showing base gazette ${selected} and related amendments`}
              {viewMode !== 'complete' && viewMode !== 'government-evolution' && viewMode !== 'comparison' && !selected && 'Select a gazette to view its relationships'}
            </div>
          </div>
        </aside>
        </div>
      )}
    </section>
  );
}