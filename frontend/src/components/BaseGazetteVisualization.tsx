import { useEffect, useState, useMemo } from "react";
import Tree, { CustomNodeElementProps, RawNodeDatum } from "react-d3-tree";
import {
  getGazettes,
  getGazetteStructure,
  getGazetteFullDetails,
  type GazetteStructure,
  type GazetteFullDetails,
} from "../services/api";
import {
  Building2,
  Search,
  Download,
  ChevronDown,
  ChevronUp,
} from "lucide-react";

interface BaseGazetteVisualizationProps {
  gazetteId?: string;
}

interface GraphNode {
  id: string;
  label: string;
  type: "gazette" | "minister" | "department" | "law";
  level: number;
  size: number;
  color: string;
  details?: any;
  x?: number;
  y?: number;
}

enum NodeType {
  Gazette = "gazette",
  Minister = "minister",
  Department = "department",
  Law = "law",
}

const nodeStyleConfig: {
  [key in NodeType]: {
    bg: string;
    border: string;
    text: string;
    padding: string;
  };
} = {
  [NodeType.Gazette]: {
    bg: "bg-blue-600/10",
    border: "border-blue-600/30",
    text: "text-blue-700 font-bold text-lg",
    padding: "px-4 py-2",
  },
  [NodeType.Minister]: {
    bg: "bg-emerald-600/10",
    border: "border-emerald-600/30",
    text: "text-emerald-700 font-medium",
    padding: "px-3 py-1.5",
  },
  [NodeType.Department]: {
    bg: "bg-amber-600/10",
    border: "border-amber-600/30",
    text: "text-amber-700",
    padding: "px-3 py-1",
  },
  [NodeType.Law]: {
    bg: "bg-purple-600/10",
    border: "border-purple-600/30",
    text: "text-purple-700",
    padding: "px-3 py-1",
  },
};

export default function BaseGazetteVisualization({
  gazetteId,
}: BaseGazetteVisualizationProps) {
  const [gazetteStructure, setGazetteStructure] =
    useState<GazetteStructure | null>(null);
  const [gazetteDetails, setGazetteDetails] =
    useState<GazetteFullDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedGazette, setSelectedGazette] = useState<string>(
    gazetteId || ""
  );
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [graphDimensions, setGraphDimensions] = useState({
    width: 800,
    height: 600,
  });
  const [showPerformanceMode, setShowPerformanceMode] = useState(false);
  const [showLabels, setShowLabels] = useState(true);


  const [visibleMinisters, setVisibleMinisters] = useState(10);
  const [activeMinisterId, setActiveMinisterId] = useState<string | null>(null);

  const colors = {
    gazette: "#3b82f6",
    minister: "#10b981",
    department: "#f59e0b",
    law: "#8b5cf6",
  };

  useEffect(() => {
    if (selectedGazette) {
      loadGazetteData();
    } else {
      setLoading(false);
    }
  }, [selectedGazette]);

  useEffect(() => {
    const updateDimensions = () => {
      const container = document.getElementById("graph-container");
      if (container) {
        setGraphDimensions({
          width: Math.max(400, container.offsetWidth - 40),
          height: Math.max(400, window.innerHeight - 300),
        });
      }
    };

    updateDimensions();
    window.addEventListener("resize", updateDimensions);
    return () => window.removeEventListener("resize", updateDimensions);
  }, []);

  const loadGazetteData = async () => {
    if (!selectedGazette.trim()) {
      setError("Please enter a gazette ID");
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const basicGazette = await getGazettes().then((gazettes) =>
        gazettes.find((g) => g.gazette_id === selectedGazette)
      );

      if (!basicGazette) {
        throw new Error(`Gazette ${selectedGazette} not found`);
      }

      const timeoutPromise = new Promise((_, reject) =>
        setTimeout(
          () =>
            reject(
              new Error(
                "Backend is taking too long to respond. The Neo4j query might be complex. Please try again or contact support."
              )
            ),
          30000
        )
      );

      const [structure, details] = (await Promise.race([
        Promise.all([
          getGazetteStructure(selectedGazette),
          getGazetteFullDetails(selectedGazette),
        ]),
        timeoutPromise,
      ])) as [GazetteStructure, GazetteFullDetails];

      setGazetteStructure(structure);
      setGazetteDetails(details);

      setVisibleMinisters(10);
    } catch (err) {
      console.error("Failed to load gazette data:", err);
      setError(
        err instanceof Error ? err.message : "Failed to load gazette data"
      );
    } finally {
      setLoading(false);
    }
  };

  const treeData: RawNodeDatum | undefined = useMemo(() => {
    if (!gazetteStructure) return undefined;

    const displayMinisters = gazetteStructure.ministers.slice(
      0,
      visibleMinisters
    );

    const ministerNodes: RawNodeDatum[] = displayMinisters.map(
      (minister, idx) => {
    
        const ministerId = `minister-${idx}`;


        const isExpanded = activeMinisterId === ministerId;

        return {
          name: minister.name,
          attributes: { id: ministerId, type: "minister" },
      
          _collapsed: !isExpanded,
          children:
            minister.departments?.map((dept: any, dIdx: number) => ({
              name: typeof dept === "string" ? dept : dept.name,
              attributes: { id: `dept-${idx}-${dIdx}`, type: "department" },
              _collapsed: true,
            })) || [],
        };
      }
    );

    return {
      name: `Gazette ${gazetteStructure.gazette_id}`,
      attributes: { id: gazetteStructure.gazette_id, type: "gazette" },
      children: ministerNodes,
      _collapsed: false,
    };
  }, [gazetteStructure, visibleMinisters, activeMinisterId]); 

  const countNodes = (node: RawNodeDatum | undefined): number => {
    if (!node) return 0;
    const children = node.children ?? [];
    return (
      1 + children.reduce((acc, c) => acc + countNodes(c as RawNodeDatum), 0)
    );
  };
  const totalNodes = treeData ? countNodes(treeData) : 0;

  const renderCustomNode = ({
    nodeDatum,
    toggleNode,
  }: CustomNodeElementProps) => {
    const type = (nodeDatum.attributes as any)?.type || NodeType.Minister;
    const styles = nodeStyleConfig[type as NodeType];
    const nodeId = (nodeDatum.attributes as any)?.id;

    return (
      <g
        onClick={(e) => {
          e.stopPropagation();


          setSelectedNode({
            id: nodeId,
            label: nodeDatum.name,
            type: type,
            level: 0,
            size: 0,
            color: "",
            details: nodeDatum.attributes,
          });

        
          if (type === NodeType.Minister) {
     
            setActiveMinisterId((prev) => (prev === nodeId ? null : nodeId));
          } else {
         
            toggleNode?.();
          }
        }}
      >
        <foreignObject width={220} height={90} x={10} y={-45}>
          <div
            className={`
          ${styles.bg} ${styles.border} ${styles.text} ${styles.padding}
          border rounded-xl shadow-sm backdrop-blur-sm
          hover:shadow-md transition-all duration-200 cursor-pointer
          flex items-center gap-2
        `}
          >
            <div className="flex-1 leading-tight ">
              <div className="truncate" title={nodeDatum.name}>
                {nodeDatum.name}
              </div>
              {nodeDatum.children?.length ? (
                <div className="text-[10px] text-slate-500 mt-1">
                  {nodeDatum.children.length} departments
                </div>
              ) : null}
            </div>
          </div>
        </foreignObject>
      </g>
    );
  };

  const exportGraph = () => {
    const dataStr = JSON.stringify(treeData ?? {}, null, 2);
    const dataBlob = new Blob([dataStr], { type: "application/json" });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `gazette-${selectedGazette || "export"}-hierarchy.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  // --- RENDER STATES (Loading, Error, Empty) ---

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-6 text-white shadow-lg">
          <div className="flex items-center gap-3 mb-2">
            <Building2 className="h-8 w-8" />
            <div>
              <h1 className="text-2xl font-bold">
                Interactive Base Gazette Visualization
              </h1>
              <p className="text-blue-100">
                Explore government structure relationships interactively
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-8 text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sky-600 mx-auto mb-4" />
          <div className="text-slate-500 mb-2">
            Loading ministry structure data...
          </div>
          <div className="text-sm text-slate-400">
            Querying Neo4j database for: {selectedGazette}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-6 text-white shadow-lg">
          <div className="flex items-center gap-3 mb-2">
            <Building2 className="h-8 w-8" />
            <div>
              <h1 className="text-2xl font-bold">
                Interactive Base Gazette Visualization
              </h1>
              <p className="text-blue-100">
                Explore government structure relationships interactively
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-8 text-center">
          <div className="text-red-600 mb-4">Error: {error}</div>
          <div className="flex gap-3 justify-center">
            <button
              onClick={loadGazetteData}
              className="px-4 py-2 bg-sky-600 text-white rounded-lg hover:bg-sky-700 transition-colors"
            >
              Retry Loading
            </button>
            <button
              onClick={() => {
                setError(null);
                setSelectedGazette("");
                setGazetteStructure(null);
                setGazetteDetails(null);
              }}
              className="px-4 py-2 bg-slate-600 text-white rounded-lg hover:bg-slate-700 transition-colors"
            >
              Start Over
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!gazetteStructure && !selectedGazette) {
    return (
      <div className="space-y-6">
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-6 text-white shadow-lg">
          <div className="flex items-center gap-3 mb-2">
            <Building2 className="h-8 w-8" />
            <div>
              <h1 className="text-2xl font-bold">
                Interactive Base Gazette Visualization
              </h1>
              <p className="text-blue-100">
                Explore government structure relationships interactively
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-8 text-center">
          <div className="text-6xl mb-4">🏛️</div>
          <h3 className="text-xl font-semibold text-slate-800 mb-2">
            Welcome to Ministry Visualization
          </h3>
          <p className="text-slate-600 mb-4">
            Enter a gazette ID below to explore the ministry structure
            interactively.
          </p>

          <div className="bg-slate-50 rounded-lg p-4 mb-6">
            <h4 className="font-medium text-slate-800 mb-2">Quick Start:</h4>
            <div className="flex flex-wrap gap-2 justify-center">
              {["1897/15", "2153/12", "2289/43", "2412/08"].map((id) => (
                <button
                  key={id}
                  onClick={() => setSelectedGazette(id)}
                  className="px-3 py-1 bg-sky-100 text-sky-700 rounded-lg hover:bg-sky-200 transition-colors text-sm"
                >
                  {id}
                </button>
              ))}
            </div>
          </div>

          <div className="flex items-center justify-center gap-2">
            <input
              type="text"
              value={selectedGazette}
              onChange={(e) => setSelectedGazette(e.target.value)}
              placeholder="Enter gazette ID (e.g., 1897/15)"
              className="px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-300"
            />
            <button
              onClick={loadGazetteData}
              className="px-4 py-2 bg-sky-600 text-white rounded-lg hover:bg-sky-700 transition-colors"
            >
              Load Visualization
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!gazetteStructure) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-8 text-center">
        <div className="text-slate-500">
          No gazette data available for: {selectedGazette}
        </div>
        <button
          onClick={() => setSelectedGazette("")}
          className="mt-4 px-4 py-2 bg-sky-600 text-white rounded-lg hover:bg-sky-700 transition-colors"
        >
          Try Another Gazette
        </button>
      </div>
    );
  }

  // --- MAIN RENDER ---

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-6 text-white shadow-lg">
        <div className="flex items-center gap-3 mb-2">
          <Building2 className="h-8 w-8" />
          <div>
            <h1 className="text-2xl font-bold">
              Ministry Structure Visualization
            </h1>
            <p className="text-blue-100">
              Explore ministry relationships in government structure
            </p>
          </div>
        </div>
        <div className="bg-green-500/20 border border-green-300/30 rounded-lg p-2 mt-3">
          <p className="text-sm text-green-100">
            🗄️ <strong>Live Data:</strong> Showing real government structure
            data from Neo4j for {selectedGazette}
          </p>
        </div>
      </div>

      {/* Control Bar */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium text-slate-700">
              Gazette:
            </label>
            <input
              type="text"
              value={selectedGazette}
              onChange={(e) => setSelectedGazette(e.target.value)}
              placeholder="Enter gazette ID"
              className="px-3 py-1 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-300"
            />
            <button
              onClick={loadGazetteData}
              className="px-3 py-1 bg-sky-600 text-white rounded-lg hover:bg-sky-700 transition-colors text-sm"
            >
              Load
            </button>
          </div>

          <div className="flex items-center gap-2">
            <Search className="h-4 w-4 text-slate-500" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search nodes..."
              className="px-3 py-1 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-300"
            />
          </div>

          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={showPerformanceMode}
              onChange={(e) => setShowPerformanceMode(e.target.checked)}
              className="rounded"
            />
            <span className="text-slate-600">Performance Mode</span>
          </label>

          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={showLabels}
              onChange={(e) => setShowLabels(e.target.checked)}
              className="rounded"
            />
            <span className="text-slate-600">Show Labels</span>
          </label>

          <button
            onClick={exportGraph}
            className="flex items-center gap-2 px-3 py-1 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm"
          >
            <Download className="h-4 w-4" />
            Export
          </button>
        </div>
      </div>

    
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Graph Area */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-slate-800">
                Hierarchy View
              </h3>
              <div className="flex items-center gap-3">
                {showPerformanceMode && (
                  <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">
                    Performance Mode (limited)
                  </span>
                )}
                <div className="text-sm text-slate-500">
                  {totalNodes} visible nodes
                </div>
              </div>
            </div>

            <div
              id="graph-container"
              className="border border-slate-200 rounded-lg overflow-hidden"
              style={{ height: graphDimensions.height }}
            >
              <div
                id="tree-container-wrapper"
                className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden relative"
                style={{ height: "700px" }}
              >
                {!treeData ? (
                  <div className="flex items-center justify-center h-full text-slate-400">
                    Loading Data...
                  </div>
                ) : (
                  <Tree
                    data={treeData}
                    orientation="horizontal"
                    collapsible={true}
                    initialDepth={1} 
                    depthFactor={500}
                    nodeSize={{ x: 300, y: 150 }}
                    pathFunc="diagonal"
                    separation={{ siblings: 0.5, nonSiblings: 20 }}
                    renderCustomNodeElement={renderCustomNode}
                    translate={{ x: 100, y: graphDimensions.height / 2 }}
                    zoomable={true}
                    zoom={0.8}
                  />
                )}
              </div>
            </div>
          </div>
        </div>

 
        <div className="space-y-4">
      
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4">
            <h3 className="text-lg font-semibold text-slate-800 mb-3">
              Legend
            </h3>
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <div
                  className="w-4 h-4 rounded-full"
                  style={{ backgroundColor: colors.gazette }}
                />
                <span className="text-sm">Gazette</span>
              </div>
              <div className="flex items-center gap-2">
                <div
                  className="w-4 h-4 rounded-full"
                  style={{ backgroundColor: colors.minister }}
                />
                <span className="text-sm">Minister</span>
              </div>
              <div className="flex items-center gap-2">
                <div
                  className="w-4 h-4 rounded-full"
                  style={{ backgroundColor: colors.department }}
                />
                <span className="text-sm">Department</span>
              </div>
            </div>
          </div>

    
          {selectedNode && (
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4">
              <h3 className="text-lg font-semibold text-slate-800 mb-3">
                Node Details
              </h3>
              <div className="space-y-2">
                <div>
                  <span className="font-medium text-slate-700">Name:</span>
                  <span className="ml-2 text-slate-600 text-sm block mt-1">
                    {selectedNode.label}
                  </span>
                </div>
                <div>
                  <span className="font-medium text-slate-700">Type:</span>
                  <span className="ml-2 text-slate-600 capitalize">
                    {selectedNode.type}
                  </span>
                </div>
                {selectedNode.details &&
                  Object.entries(selectedNode.details)
                    .filter(
                      ([key]) =>
                        key !== "id" && key !== "type" && !key.startsWith("_")
                    )
                    .map(([key, value]) => (
                      <div key={key}>
                        <span className="font-medium text-slate-700 capitalize">
                          {key.replace("_", " ")}:
                        </span>
                        <span className="ml-2 text-slate-600">
                          {Array.isArray(value)
                            ? value.join(", ")
                            : String(value)}
                        </span>
                      </div>
                    ))}
              </div>
            </div>
          )}

      
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4">
            <h3 className="text-lg font-semibold text-slate-800 mb-3">
              Statistics
            </h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-600">Total Ministers:</span>
                <span className="font-medium">
                  {gazetteStructure.ministers.length}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">Showing:</span>
                <span className="font-medium text-blue-600">
                  {Math.min(
                    visibleMinisters,
                    gazetteStructure.ministers.length
                  )}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">Gazette ID:</span>
                <span className="font-medium">
                  {gazetteStructure.gazette_id}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">Published:</span>
                <span className="font-medium">
                  {gazetteDetails?.gazette.published_date || "N/A"}
                </span>
              </div>

              {/* Show All / Show Less Button */}
              {gazetteStructure.ministers.length > 10 && (
                <div className="pt-4 border-t border-slate-100 mt-2">
                  <button
                    onClick={() => {
                      if (
                        visibleMinisters >= gazetteStructure.ministers.length
                      ) {
                        setVisibleMinisters(10); 
                      } else {
                        setVisibleMinisters(gazetteStructure.ministers.length); 
                      }
                    }}
                    className={`w-full py-2.5 px-3 rounded-lg flex items-center justify-center gap-2 transition-all duration-200 ${
                      visibleMinisters >= gazetteStructure.ministers.length
                        ? "bg-slate-100 text-slate-700 hover:bg-slate-200"
                        : "bg-blue-50 text-blue-700 border border-blue-200 hover:bg-blue-100"
                    }`}
                  >
                    {visibleMinisters >= gazetteStructure.ministers.length ? (
                      <>
                        <ChevronUp className="h-4 w-4" />
                        <span>Show Less (First 10)</span>
                      </>
                    ) : (
                      <>
                        <ChevronDown className="h-4 w-4" />
                        <span>
                          Show All ({gazetteStructure.ministers.length})
                        </span>
                      </>
                    )}
                  </button>
                  <p className="text-xs text-center text-slate-400 mt-2">
                    {visibleMinisters >= gazetteStructure.ministers.length
                      ? "Showing all ministries"
                      : `${
                          gazetteStructure.ministers.length - 10
                        } hidden ministries`}
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
