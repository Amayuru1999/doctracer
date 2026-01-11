import { useEffect, useState } from "react";
import ForceGraph2D from "react-force-graph-2d";
import { getGazetteStructure, type GazetteStructure } from "../services/api";

interface MinistryStructureGraphProps {
  gazetteId?: string;
  showAll?: boolean;
}

const colors = {
  gazette: "#0ea5e9",
  minister: "#1d4ed8", 
  department: "#16a34a",
  law: "#f59e0b",
  manages: "#10b981",
  oversees: "#f59e0b",
  has_department: "#3b82f6",
  has_law: "#8b5cf6"
};

export default function MinistryStructureGraph({ gazetteId, showAll = false }: MinistryStructureGraphProps) {
  const [structure, setStructure] = useState<GazetteStructure | null>(null);
  const [graphData, setGraphData] = useState<{ nodes: any[]; links: any[] }>({ nodes: [], links: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | undefined>();

  useEffect(() => {
    loadData();
  }, [gazetteId, showAll]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(undefined);

      if (gazetteId) {
        // Load specific gazette structure
        const structureData = await getGazetteStructure(gazetteId);
        setStructure(structureData);
        
        // Convert structure to graph format
        const graph = convertStructureToGraph(structureData);
        setGraphData(graph);
      } else {
        // No gazette ID provided, show empty state
        setGraphData({ nodes: [], links: [] });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const convertStructureToGraph = (structure: GazetteStructure) => {
    const nodes: any[] = [];
    const links: any[] = [];
    const nodeIds = new Set<string>();

    // Add gazette node
    const gazetteNode = {
      id: structure.gazette_id,
      label: `Gazette ${structure.gazette_id}`,
      kind: 'gazette',
      type: 'gazette'
    };
    nodes.push(gazetteNode);
    nodeIds.add(structure.gazette_id);

    // Add minister nodes and their relationships
    structure.ministers.forEach((minister, index) => {
      const ministerId = `minister_${minister.number}_${minister.name}`;
      nodes.push({
        id: ministerId,
        label: `${minister.number}. ${minister.name}`,
        kind: 'minister',
        type: 'minister',
        departments: minister.departments,
        laws: minister.laws
      });
      nodeIds.add(ministerId);

      // Link gazette to minister
      links.push({
        source: structure.gazette_id,
        target: ministerId,
        kind: 'has_minister'
      });

      // Add department nodes and link to minister
      minister.departments.forEach((dept, deptIndex) => {
        const deptId = `dept_${index}_${deptIndex}_${dept}`;
        if (!nodeIds.has(deptId)) {
          nodes.push({
            id: deptId,
            label: dept,
            kind: 'department',
            type: 'department'
          });
          nodeIds.add(deptId);
        }

        // Link minister to department
        links.push({
          source: ministerId,
          target: deptId,
          kind: 'manages'
        });
      });

      // Add law nodes and link to minister
      minister.laws.forEach((law, lawIndex) => {
        const lawId = `law_${index}_${lawIndex}_${law}`;
        if (!nodeIds.has(lawId)) {
          nodes.push({
            id: lawId,
            label: law,
            kind: 'law',
            type: 'law'
          });
          nodeIds.add(lawId);
        }

        // Link minister to law
        links.push({
          source: ministerId,
          target: lawId,
          kind: 'oversees'
        });
      });
    });

    return { nodes, links };
  };

  if (loading) {
    return (
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-8 text-center">
        <div className="text-slate-500">Loading ministry structure...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-8 text-center">
        <div className="text-red-600">Error: {error}</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-600 to-yellow-500 rounded-xl p-6 text-white shadow-lg">
        <div className="flex items-center gap-3 mb-2">
          <div className="h-8 w-8 rounded-lg bg-white/20 flex items-center justify-center text-lg">
            🇱🇰
          </div>
          <h1 className="text-2xl font-bold">Ministry-Department Structure</h1>
        </div>
        <p className="text-green-100 text-sm">
          {gazetteId 
            ? `Visualizing government structure for Gazette ${gazetteId}` 
            : 'Interactive visualization of Sri Lankan government ministry-department relationships'
          }
        </p>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm h-[600px] overflow-hidden">
        <ForceGraph2D
          graphData={graphData}
          nodeCanvasObject={(node: any, ctx, scale) => {
            // Dynamic node sizing based on type
            let r = 8;
            if (node.kind === 'gazette') {
              r = 15; // Largest for gazettes
            } else if (node.kind === 'minister') {
              r = 12; // Large for ministers
            } else if (node.kind === 'department') {
              r = 10; // Medium for departments
            } else if (node.kind === 'law') {
              r = 8; // Smaller for laws
            }
            
            const color = colors[node.kind as keyof typeof colors] || "#6b7280";
            
            // Draw node
            ctx.fillStyle = color;
            ctx.beginPath();
            ctx.arc(node.x, node.y, r, 0, 2*Math.PI, false);
            ctx.fill();

            // Add border
            ctx.strokeStyle = "#ffffff";
            ctx.lineWidth = 2;
            ctx.stroke();

            // Special styling for gazette
            if (node.kind === 'gazette') {
              ctx.strokeStyle = "#1e40af";
              ctx.lineWidth = 3;
              ctx.stroke();
            }

            // Add label
            const label = node.label || node.id;
            const fontSize = Math.max(10, 14 / Math.sqrt(scale));
            ctx.font = `${fontSize}px sans-serif`;
            ctx.fillStyle = "#111827";
            ctx.textAlign = "center";
            ctx.fillText(label, node.x, node.y + r + fontSize + 2);
          }}
          linkColor={(link: any) => colors[link.kind as keyof typeof colors] || "#94a3b8"}
          linkWidth={2}
          linkDirectionalParticles={2}
          linkDirectionalParticleWidth={2}
          linkDirectionalParticleSpeed={0.01}
          cooldownTicks={150}
          onNodeClick={(node: any) => {
            console.log('Node clicked:', node);
            if (node.kind === 'minister') {
              console.log('Minister departments:', node.departments);
              console.log('Minister laws:', node.laws);
            }
          }}
          onLinkClick={(link: any) => {
            console.log('Link clicked:', link);
          }}
          onEngineStop={() => {/* layout stabilized */}}
        />
      </div>

      {/* Legend and Statistics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Legend */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
          <h3 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
            <span className="h-6 w-6 rounded bg-slate-100 flex items-center justify-center text-slate-600 text-sm">🎨</span>
            Visual Legend
          </h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="flex items-center gap-3 p-2 rounded-lg bg-sky-50">
              <span className="inline-block h-4 w-4 rounded-full bg-sky-500 shadow-sm" />
              <span className="text-slate-700 font-medium">Gazette</span>
            </div>
            <div className="flex items-center gap-3 p-2 rounded-lg bg-blue-50">
              <span className="inline-block h-4 w-4 rounded-full bg-blue-700 shadow-sm" />
              <span className="text-slate-700 font-medium">Minister</span>
            </div>
            <div className="flex items-center gap-3 p-2 rounded-lg bg-green-50">
              <span className="inline-block h-4 w-4 rounded-full bg-green-600 shadow-sm" />
              <span className="text-slate-700 font-medium">Department</span>
            </div>
            <div className="flex items-center gap-3 p-2 rounded-lg bg-amber-50">
              <span className="inline-block h-4 w-4 rounded-full bg-amber-500 shadow-sm" />
              <span className="text-slate-700 font-medium">Law</span>
            </div>
          </div>
        </div>

        {/* Statistics */}
        {structure && (
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
            <h3 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
              <span className="h-6 w-6 rounded bg-slate-100 flex items-center justify-center text-slate-600 text-sm">📊</span>
              Structure Summary
            </h3>
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center p-4 rounded-lg bg-blue-50 border border-blue-200">
                <div className="text-3xl font-bold text-blue-700 mb-1">{structure.ministers.length}</div>
                <div className="text-slate-600 font-medium">Ministries</div>
              </div>
              <div className="text-center p-4 rounded-lg bg-green-50 border border-green-200">
                <div className="text-3xl font-bold text-green-600 mb-1">{structure.departments.length}</div>
                <div className="text-slate-600 font-medium">Departments</div>
              </div>
              <div className="text-center p-4 rounded-lg bg-amber-50 border border-amber-200">
                <div className="text-3xl font-bold text-amber-500 mb-1">{structure.laws.length}</div>
                <div className="text-slate-600 font-medium">Laws</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
