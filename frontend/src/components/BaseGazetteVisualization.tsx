import { useEffect, useState, useMemo } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { 
  getGazettes,
  getGazetteStructure, 
  getGazetteFullDetails,
  type GazetteStructure,
  type GazetteFullDetails 
} from '../services/api';
import { 
  Building2, 
  Scale, 
  Users, 
  Calendar,
  Search,
  Filter,
  Download,
  Eye,
  EyeOff
} from 'lucide-react';

interface BaseGazetteVisualizationProps {
  gazetteId?: string;
}

interface GraphNode {
  id: string;
  label: string;
  type: 'gazette' | 'minister' | 'department' | 'law';
  level: number;
  size: number;
  color: string;
  details?: any;
  x?: number;
  y?: number;
}

interface GraphLink {
  source: string;
  target: string;
  type: string;
  color: string;
  width: number;
}

export default function BaseGazetteVisualization({ gazetteId }: BaseGazetteVisualizationProps) {
  const [gazetteStructure, setGazetteStructure] = useState<GazetteStructure | null>(null);
  const [gazetteDetails, setGazetteDetails] = useState<GazetteFullDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedGazette, setSelectedGazette] = useState<string>(gazetteId || '');
  const [searchTerm, setSearchTerm] = useState('');
  const [showDepartments, setShowDepartments] = useState(false);
  const [showLaws, setShowLaws] = useState(false);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [graphDimensions, setGraphDimensions] = useState({ width: 800, height: 600 });
  const [graphLoading, setGraphLoading] = useState(false);
  const [showPerformanceMode, setShowPerformanceMode] = useState(false);
  const [showLabels, setShowLabels] = useState(true);

  // Color scheme
  const colors = {
    gazette: '#3b82f6',
    minister: '#10b981',
    department: '#f59e0b',
    law: '#8b5cf6'
  };

  useEffect(() => {
    if (selectedGazette) {
      loadGazetteData();
    } else {
      // If no gazette is selected, stop loading
      setLoading(false);
    }
  }, [selectedGazette]);

  useEffect(() => {
    // Update graph dimensions on window resize
    const updateDimensions = () => {
      const container = document.getElementById('graph-container');
      if (container) {
        setGraphDimensions({
          width: container.offsetWidth - 40,
          height: Math.max(400, window.innerHeight - 300)
        });
      }
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  const loadGazetteData = async () => {
    if (!selectedGazette.trim()) {
      setError('Please enter a gazette ID');
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      // First verify the gazette exists (this is fast)
      const basicGazette = await getGazettes().then(gazettes => 
        gazettes.find(g => g.gazette_id === selectedGazette)
      );
      
      if (!basicGazette) {
        throw new Error(`Gazette ${selectedGazette} not found`);
      }
      
      // Load real data from Neo4j with increased timeout
      const timeoutPromise = new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Backend is taking too long to respond. The Neo4j query might be complex. Please try again or contact support.')), 30000)
      );
      
      const [structure, details] = await Promise.race([
        Promise.all([
          getGazetteStructure(selectedGazette),
          getGazetteFullDetails(selectedGazette)
        ]),
        timeoutPromise
      ]) as [GazetteStructure, GazetteFullDetails];
      
      setGazetteStructure(structure);
      setGazetteDetails(details);
      
    } catch (err) {
      console.error('Failed to load gazette data:', err);
      setError(err instanceof Error ? err.message : 'Failed to load gazette data');
    } finally {
      setLoading(false);
    }
  };

  const graphData = useMemo(() => {
    if (!gazetteStructure) return { nodes: [], links: [] };

    const nodes: GraphNode[] = [];
    const links: GraphLink[] = [];
    
    // Limit ministers in performance mode
    const ministersToShow = showPerformanceMode 
      ? gazetteStructure.ministers.slice(0, 10) 
      : gazetteStructure.ministers;

    // Add gazette node (center)
    const gazetteNode: GraphNode = {
      id: gazetteStructure.gazette_id,
      label: `Gazette ${gazetteStructure.gazette_id}`,
      type: 'gazette',
      level: 0,
      size: 25,
      color: colors.gazette,
      details: {
        published_date: gazetteDetails?.gazette.published_date,
        type: gazetteDetails?.gazette.type
      }
    };
    nodes.push(gazetteNode);

    // Add minister nodes
    ministersToShow.forEach((minister, index) => {
      const ministerNode: GraphNode = {
        id: `minister-${index}`,
        label: minister.name,
        type: 'minister',
        level: 1,
        size: 18,
        color: colors.minister,
        details: {
          departments: minister.departments,
          laws: minister.laws
        }
      };
      nodes.push(ministerNode);

      // Link minister to gazette
      links.push({
        source: gazetteStructure.gazette_id,
        target: `minister-${index}`,
        type: 'has_minister',
        color: '#64748b',
        width: 2
      });

      // Add department nodes if enabled
      if (showDepartments) {
        minister.departments.forEach((dept, deptIndex) => {
          const deptNode: GraphNode = {
            id: `dept-${index}-${deptIndex}`,
            label: dept,
            type: 'department',
            level: 2,
            size: 10,
            color: colors.department,
            details: { minister: minister.name }
          };
          nodes.push(deptNode);

          // Link department to minister
          links.push({
            source: `minister-${index}`,
            target: `dept-${index}-${deptIndex}`,
            type: 'oversees',
            color: '#f59e0b',
            width: 1.5
          });
        });
      }

      // Add law nodes if enabled
      if (showLaws) {
        minister.laws.forEach((law, lawIndex) => {
          const lawNode: GraphNode = {
            id: `law-${index}-${lawIndex}`,
            label: law,
            type: 'law',
            level: 2,
            size: 8,
            color: colors.law,
            details: { minister: minister.name }
          };
          nodes.push(lawNode);

          // Link law to minister
          links.push({
            source: `minister-${index}`,
            target: `law-${index}-${lawIndex}`,
            type: 'responsible_for',
            color: '#8b5cf6',
            width: 1.5
          });
        });
      }
    });

    // Filter nodes based on search term
    const filteredNodes = searchTerm 
      ? nodes.filter(node => 
          node.label.toLowerCase().includes(searchTerm.toLowerCase())
        )
      : nodes;

    // Filter links to only include those connecting filtered nodes
    const filteredNodeIds = new Set(filteredNodes.map(n => n.id));
    const filteredLinks = links.filter(link => 
      filteredNodeIds.has(link.source) && filteredNodeIds.has(link.target)
    );

    return { nodes: filteredNodes, links: filteredLinks };
  }, [gazetteStructure, showDepartments, showLaws, searchTerm, gazetteDetails, showPerformanceMode, showLabels]);

  const handleNodeClick = (node: GraphNode) => {
    setSelectedNode(node);
  };

  const handleNodeHover = (node: GraphNode | null) => {
    // You can add hover effects here
  };

  const exportGraph = () => {
    const dataStr = JSON.stringify(graphData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `gazette-${selectedGazette}-graph.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="space-y-6">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-6 text-white shadow-lg">
          <div className="flex items-center gap-3 mb-2">
            <Building2 className="h-8 w-8" />
            <div>
              <h1 className="text-2xl font-bold">Interactive Base Gazette Visualization</h1>
              <p className="text-blue-100">Explore government structure relationships interactively</p>
            </div>
          </div>
        </div>

        {/* Loading State */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-8 text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sky-600 mx-auto mb-4"></div>
          <div className="text-slate-500 mb-2">Loading ministry structure data...</div>
          <div className="text-sm text-slate-400">Querying Neo4j database for: {selectedGazette}</div>
          <div className="text-xs text-slate-400 mt-2">This may take up to 30 seconds for complex queries</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-6 text-white shadow-lg">
          <div className="flex items-center gap-3 mb-2">
            <Building2 className="h-8 w-8" />
            <div>
              <h1 className="text-2xl font-bold">Interactive Base Gazette Visualization</h1>
              <p className="text-blue-100">Explore government structure relationships interactively</p>
            </div>
          </div>
        </div>

        {/* Error State */}
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
                setSelectedGazette('');
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
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-6 text-white shadow-lg">
          <div className="flex items-center gap-3 mb-2">
            <Building2 className="h-8 w-8" />
            <div>
              <h1 className="text-2xl font-bold">Interactive Base Gazette Visualization</h1>
              <p className="text-blue-100">Explore government structure relationships interactively</p>
            </div>
          </div>
        </div>

        {/* Welcome State */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-8 text-center">
          <div className="text-6xl mb-4">🏛️</div>
          <h3 className="text-xl font-semibold text-slate-800 mb-2">Welcome to Ministry Visualization</h3>
          <p className="text-slate-600 mb-4">
            Enter a gazette ID below to explore the ministry structure interactively.
          </p>
          <div className="bg-green-50 border border-green-200 rounded-lg p-3 mb-6">
            <p className="text-sm text-green-700">
              <strong>Real Data:</strong> Loading actual government structure data from Neo4j database.
            </p>
          </div>
          
          {/* Quick Start */}
          <div className="bg-slate-50 rounded-lg p-4 mb-6">
            <h4 className="font-medium text-slate-800 mb-2">Quick Start:</h4>
            <div className="flex flex-wrap gap-2 justify-center">
              <button
                onClick={() => setSelectedGazette('1897/15')}
                className="px-3 py-1 bg-sky-100 text-sky-700 rounded-lg hover:bg-sky-200 transition-colors text-sm"
              >
                1897/15
              </button>
              <button
                onClick={() => setSelectedGazette('1905/4')}
                className="px-3 py-1 bg-sky-100 text-sky-700 rounded-lg hover:bg-sky-200 transition-colors text-sm"
              >
                1905/4
              </button>
            </div>
          </div>

          {/* Manual Input */}
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
        <div className="text-slate-500">No gazette data available for: {selectedGazette}</div>
        <button
          onClick={() => setSelectedGazette('')}
          className="mt-4 px-4 py-2 bg-sky-600 text-white rounded-lg hover:bg-sky-700 transition-colors"
        >
          Try Another Gazette
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-6 text-white shadow-lg">
        <div className="flex items-center gap-3 mb-2">
          <Building2 className="h-8 w-8" />
          <div>
            <h1 className="text-2xl font-bold">Ministry Structure Visualization</h1>
            <p className="text-blue-100">Explore ministry relationships in government structure</p>
          </div>
        </div>
        <div className="bg-green-500/20 border border-green-300/30 rounded-lg p-2 mt-3">
          <p className="text-sm text-green-100">
            🗄️ <strong>Live Data:</strong> Showing real government structure data from Neo4j for {selectedGazette}
          </p>
        </div>
      </div>

      {/* Controls */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4">
        <div className="flex flex-wrap items-center gap-4">
          {/* Gazette Selection */}
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium text-slate-700">Gazette:</label>
            <input
              type="text"
              value={selectedGazette}
              onChange={(e) => setSelectedGazette(e.target.value)}
              placeholder="Enter gazette ID (e.g., 1897/15)"
              className="px-3 py-1 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-300"
            />
            <button
              onClick={loadGazetteData}
              className="px-3 py-1 bg-sky-600 text-white rounded-lg hover:bg-sky-700 transition-colors text-sm"
            >
              Load
            </button>
          </div>

          {/* Search */}
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


          {/* Performance Mode Toggle */}
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={showPerformanceMode}
              onChange={(e) => setShowPerformanceMode(e.target.checked)}
              className="rounded"
            />
            <span className="text-slate-600">Performance Mode</span>
          </label>

          {/* Show Labels Toggle */}
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={showLabels}
              onChange={(e) => setShowLabels(e.target.checked)}
              className="rounded"
            />
            <span className="text-slate-600">Show Labels</span>
          </label>

          {/* Export */}
          <button
            onClick={exportGraph}
            className="flex items-center gap-2 px-3 py-1 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm"
          >
            <Download className="h-4 w-4" />
            Export
          </button>
        </div>
      </div>

      {/* Graph and Details */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Graph Visualization */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-slate-800">Interactive Graph</h3>
              <div className="flex items-center gap-3">
                {showPerformanceMode && (
                  <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">
                    Performance Mode (10 ministers)
                  </span>
                )}
                <div className="text-sm text-slate-500">
                  {graphData.nodes.length} nodes, {graphData.links.length} links
                </div>
              </div>
            </div>
            
            {/* Performance Warning */}
            {!showPerformanceMode && graphData.nodes.length > 20 && (
              <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                <div className="flex items-center gap-2">
                  <div className="text-yellow-600">⚠️</div>
                  <div className="text-sm text-yellow-800">
                    <strong>Performance Notice:</strong> Large number of nodes detected. 
                    Enable "Performance Mode" for smoother interaction or toggle "Show Labels" to reduce clutter.
                  </div>
                </div>
              </div>
            )}
            
            <div 
              id="graph-container"
              className="border border-slate-200 rounded-lg overflow-hidden"
              style={{ height: graphDimensions.height }}
            >
              <ForceGraph2D
                graphData={graphData}
                width={graphDimensions.width}
                height={graphDimensions.height}
                nodeLabel={(node: GraphNode) => node.label}
                nodeColor={(node: GraphNode) => node.color}
                nodeVal={(node: GraphNode) => node.size}
                linkColor={(link: GraphLink) => link.color}
                linkWidth={(link: GraphLink) => link.width}
                onNodeClick={handleNodeClick}
                onNodeHover={handleNodeHover}
                cooldownTicks={50}
                d3AlphaDecay={0.05}
                d3VelocityDecay={0.4}
                enableZoomInteraction={true}
                enableNodeDrag={true}
                nodeCanvasObject={(node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
                  const label = node.label;
                  const fontSize = Math.max(10/globalScale, 2);
                  const nodeSize = node.size || 5;
                  
                  // Draw node circle
                  ctx.fillStyle = node.color;
                  ctx.beginPath();
                  ctx.arc(node.x || 0, node.y || 0, nodeSize, 0, 2 * Math.PI);
                  ctx.fill();
                  
                  // Add white border for better visibility
                  ctx.strokeStyle = 'white';
                  ctx.lineWidth = 2;
                  ctx.stroke();
                  
                  // Draw label outside the node (only if showLabels is true)
                  if (showLabels) {
                    ctx.font = `${fontSize}px Sans-Serif`;
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillStyle = '#1f2937';
                    
                    // Position text below the node
                    const textY = (node.y || 0) + nodeSize + fontSize + 2;
                    ctx.fillText(label, node.x || 0, textY);
                  }
                }}
                linkCanvasObject={(link: any, ctx: CanvasRenderingContext2D) => {
                  if (!link.source || !link.target) return;
                  ctx.strokeStyle = link.color;
                  ctx.lineWidth = link.width || 1;
                  ctx.beginPath();
                  ctx.moveTo(link.source.x || 0, link.source.y || 0);
                  ctx.lineTo(link.target.x || 0, link.target.y || 0);
                  ctx.stroke();
                }}
              />
            </div>
          </div>
        </div>

        {/* Node Details Panel */}
        <div className="space-y-4">
          {/* Legend */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4">
            <h3 className="text-lg font-semibold text-slate-800 mb-3">Legend</h3>
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded-full" style={{ backgroundColor: colors.gazette }}></div>
                <span className="text-sm">Gazette</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded-full" style={{ backgroundColor: colors.minister }}></div>
                <span className="text-sm">Minister</span>
              </div>
            </div>
          </div>

          {/* Selected Node Details */}
          {selectedNode && (
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4">
              <h3 className="text-lg font-semibold text-slate-800 mb-3">Node Details</h3>
              <div className="space-y-2">
                <div>
                  <span className="font-medium text-slate-700">Name:</span>
                  <span className="ml-2 text-slate-600">{selectedNode.label}</span>
                </div>
                <div>
                  <span className="font-medium text-slate-700">Type:</span>
                  <span className="ml-2 text-slate-600 capitalize">{selectedNode.type}</span>
                </div>
                {selectedNode.details && Object.entries(selectedNode.details).map(([key, value]) => (
                  <div key={key}>
                    <span className="font-medium text-slate-700 capitalize">{key.replace('_', ' ')}:</span>
                    <span className="ml-2 text-slate-600">
                      {Array.isArray(value) ? value.join(', ') : String(value)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Statistics */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4">
            <h3 className="text-lg font-semibold text-slate-800 mb-3">Statistics</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-600">Total Ministers:</span>
                <span className="font-medium">{gazetteStructure.ministers.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">Gazette ID:</span>
                <span className="font-medium">{gazetteStructure.gazette_id}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">Published:</span>
                <span className="font-medium">{gazetteDetails?.gazette.published_date || 'N/A'}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
