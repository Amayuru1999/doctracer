import React, { useState, useEffect, useMemo } from 'react';
import { Search, Download, Eye, EyeOff, Zap } from 'lucide-react';
import { 
  getGazettes, 
  getGazetteStructure, 
  getGazetteFullDetails,
  type GazetteStructure,
  type GazetteFullDetails 
} from '../services/api';

interface GraphNode {
  id: string;
  label: string;
  type: 'gazette' | 'minister';
  level: number;
  size: number;
  color: string;
  x?: number;
  y?: number;
  details?: any;
}

interface GraphLink {
  source: string | GraphNode;
  target: string | GraphNode;
  type: string;
  color: string;
  width: number;
}

interface RadialVisualizationProps {
  gazetteId?: string;
}

export default function RadialVisualization({ gazetteId }: RadialVisualizationProps) {
  const [gazetteStructure, setGazetteStructure] = useState<GazetteStructure | null>(null);
  const [gazetteDetails, setGazetteDetails] = useState<GazetteFullDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedGazette, setSelectedGazette] = useState<string>(gazetteId || '');
  const [searchTerm, setSearchTerm] = useState('');
  const [showLabels, setShowLabels] = useState(true);
  const [showPerformanceMode, setShowPerformanceMode] = useState(false);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [graphDimensions, setGraphDimensions] = useState({ width: 800, height: 600 });
  const [zoomLevel, setZoomLevel] = useState(1);
  const [panOffset, setPanOffset] = useState({ x: 0, y: 0 });

  // Color scheme for radial segments
  const colors = {
    gazette: '#3b82f6',
    minister: [
      '#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57',
      '#ff9ff3', '#54a0ff', '#5f27cd', '#00d2d3', '#ff9f43',
      '#10ac84', '#ee5a24', '#0984e3', '#6c5ce7', '#a29bfe',
      '#fd79a8', '#fdcb6e', '#e17055', '#74b9ff', '#00b894',
      '#e84393', '#00cec9', '#6c5ce7', '#a29bfe', '#fd79a8',
      '#fdcb6e', '#e17055', '#74b9ff', '#00b894', '#e84393',
      '#00cec9'
    ]
  };

  useEffect(() => {
    if (selectedGazette.trim()) {
      loadGazetteData();
    } else {
      setLoading(false);
    }
  }, [selectedGazette]);

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

  const radialGraphData = useMemo(() => {
    if (!gazetteStructure) return { nodes: [], links: [] };

    const nodes: GraphNode[] = [];
    const links: GraphLink[] = [];
    
    // Limit ministers in performance mode
    const ministersToShow = showPerformanceMode 
      ? gazetteStructure.ministers.slice(0, 15) 
      : gazetteStructure.ministers;

    // Add central gazette node
    const gazetteNode: GraphNode = {
      id: gazetteStructure.gazette_id,
      label: `Gazette ${gazetteStructure.gazette_id}`,
      type: 'gazette',
      level: 0,
      size: 30,
      color: colors.gazette,
      x: graphDimensions.width / 2,
      y: graphDimensions.height / 2,
      details: {
        published_date: gazetteDetails?.gazette.published_date,
        type: gazetteDetails?.gazette.type
      }
    };
    nodes.push(gazetteNode);

    // Calculate radial positions for ministers with better spacing
    const centerX = graphDimensions.width / 2;
    const centerY = graphDimensions.height / 2;
    const radius = Math.min(centerX, centerY) * 0.7; // Increased radius for better spacing
    
    ministersToShow.forEach((minister, index) => {
      const angle = (2 * Math.PI * index) / ministersToShow.length;
      const x = centerX + radius * Math.cos(angle);
      const y = centerY + radius * Math.sin(angle);
      
      const ministerNode: GraphNode = {
        id: `minister-${index}`,
        label: minister.name,
        type: 'minister',
        level: 1,
        size: 15, // Smaller nodes to reduce overlap
        color: colors.minister[index % colors.minister.length],
        x,
        y,
        details: {
          departments: minister.departments,
          laws: minister.laws
        }
      };
      nodes.push(ministerNode);

      // Create curved link to center
      links.push({
        source: gazetteNode,
        target: ministerNode,
        type: 'has_minister',
        color: colors.minister[index % colors.minister.length],
        width: 2
      });
    });

    return { nodes, links };
  }, [gazetteStructure, showPerformanceMode, gazetteDetails, graphDimensions]);

  const filteredGraphData = useMemo(() => {
    const { nodes, links } = radialGraphData;
    
    if (!searchTerm) return { nodes, links };

    // Filter nodes based on search term
    const filteredNodes = nodes.filter(node => 
      node.label.toLowerCase().includes(searchTerm.toLowerCase())
    );

    // Filter links to only include those connecting filtered nodes
    const filteredNodeIds = new Set(filteredNodes.map(n => n.id));
    const filteredLinks = links.filter(link => 
      filteredNodeIds.has((link.source as GraphNode).id) && 
      filteredNodeIds.has((link.target as GraphNode).id)
    );

    return { nodes: filteredNodes, links: filteredLinks };
  }, [radialGraphData, searchTerm]);

  const handleNodeClick = (node: GraphNode) => {
    setSelectedNode(node);
  };

  const handleNodeHover = (node: GraphNode | null) => {
    // Optional: Add hover effects
  };

  const exportGraph = () => {
    const canvas = document.getElementById('radial-canvas') as HTMLCanvasElement;
    if (canvas) {
      const link = document.createElement('a');
      link.download = `radial-visualization-${selectedGazette}.png`;
      link.href = canvas.toDataURL();
      link.click();
    }
  };

  const handleZoomIn = () => {
    setZoomLevel(prev => Math.min(prev * 1.2, 3));
  };

  const handleZoomOut = () => {
    setZoomLevel(prev => Math.max(prev / 1.2, 0.3));
  };

  const handleResetZoom = () => {
    setZoomLevel(1);
    setPanOffset({ x: 0, y: 0 });
  };

  // Canvas rendering effect
  useEffect(() => {
    const canvas = document.getElementById('radial-canvas') as HTMLCanvasElement;
    if (!canvas || !filteredGraphData.nodes.length) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    canvas.width = graphDimensions.width;
    canvas.height = graphDimensions.height;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Apply zoom and pan transformations
    ctx.save();
    ctx.translate(panOffset.x, panOffset.y);
    ctx.scale(zoomLevel, zoomLevel);

    // Draw links first (so they appear behind nodes)
    filteredGraphData.links.forEach(link => {
      const source = link.source as GraphNode;
      const target = link.target as GraphNode;
      
      if (source.x !== undefined && source.y !== undefined && 
          target.x !== undefined && target.y !== undefined) {
        
        // Create curved path
        const midX = (source.x + target.x) / 2;
        const midY = (source.y + target.y) / 2;
        const controlX = midX + (Math.random() - 0.5) * 50;
        const controlY = midY + (Math.random() - 0.5) * 50;
        
        ctx.strokeStyle = link.color;
        ctx.lineWidth = link.width;
        ctx.beginPath();
        ctx.moveTo(source.x, source.y);
        ctx.quadraticCurveTo(controlX, controlY, target.x, target.y);
        ctx.stroke();
      }
    });

    // Draw nodes
    filteredGraphData.nodes.forEach(node => {
      if (node.x !== undefined && node.y !== undefined) {
        // Draw node circle
        ctx.fillStyle = node.color;
        ctx.beginPath();
        ctx.arc(node.x, node.y, node.size, 0, 2 * Math.PI);
        ctx.fill();
        
        // Add glow effect
        ctx.shadowColor = node.color;
        ctx.shadowBlur = 15;
        ctx.fill();
        ctx.shadowBlur = 0;
        
        // Add white border
        ctx.strokeStyle = 'white';
        ctx.lineWidth = 2;
        ctx.stroke();
        
        // Draw label if enabled
        if (showLabels) {
          ctx.fillStyle = 'white';
          ctx.font = `${12 / zoomLevel}px Arial`; // Scale font with zoom
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          
          // Position label outside the node with better spacing
          const labelDistance = node.size + 20 / zoomLevel;
          const labelY = node.y + labelDistance;
          
          // Add background for better readability
          const textWidth = ctx.measureText(node.label).width;
          const padding = 4 / zoomLevel;
          ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
          ctx.fillRect(
            node.x - textWidth/2 - padding, 
            labelY - 8/zoomLevel, 
            textWidth + 2*padding, 
            16/zoomLevel
          );
          
          ctx.fillStyle = 'white';
          ctx.fillText(node.label, node.x, labelY);
        }
      }
    });

    // Restore context
    ctx.restore();

    // Add click handlers
    const handleCanvasClick = (event: MouseEvent) => {
      const rect = canvas.getBoundingClientRect();
      const x = (event.clientX - rect.left - panOffset.x) / zoomLevel;
      const y = (event.clientY - rect.top - panOffset.y) / zoomLevel;
      
      // Find clicked node
      const clickedNode = filteredGraphData.nodes.find(node => {
        if (node.x !== undefined && node.y !== undefined) {
          const distance = Math.sqrt((x - node.x) ** 2 + (y - node.y) ** 2);
          return distance <= node.size + 10; // Add some padding for easier clicking
        }
        return false;
      });
      
      if (clickedNode) {
        handleNodeClick(clickedNode);
      }
    };

    // Add mouse wheel zoom
    const handleWheel = (event: WheelEvent) => {
      event.preventDefault();
      const delta = event.deltaY > 0 ? 0.9 : 1.1;
      setZoomLevel(prev => Math.max(0.3, Math.min(3, prev * delta)));
    };

    // Add mouse drag for panning
    let isDragging = false;
    let lastMousePos = { x: 0, y: 0 };

    const handleMouseDown = (event: MouseEvent) => {
      isDragging = true;
      lastMousePos = { x: event.clientX, y: event.clientY };
    };

    const handleMouseMove = (event: MouseEvent) => {
      if (isDragging) {
        const deltaX = event.clientX - lastMousePos.x;
        const deltaY = event.clientY - lastMousePos.y;
        setPanOffset(prev => ({
          x: prev.x + deltaX,
          y: prev.y + deltaY
        }));
        lastMousePos = { x: event.clientX, y: event.clientY };
      }
    };

    const handleMouseUp = () => {
      isDragging = false;
    };

    canvas.addEventListener('click', handleCanvasClick);
    canvas.addEventListener('wheel', handleWheel);
    canvas.addEventListener('mousedown', handleMouseDown);
    canvas.addEventListener('mousemove', handleMouseMove);
    canvas.addEventListener('mouseup', handleMouseUp);
    canvas.addEventListener('mouseleave', handleMouseUp);
    
    return () => {
      canvas.removeEventListener('click', handleCanvasClick);
      canvas.removeEventListener('wheel', handleWheel);
      canvas.removeEventListener('mousedown', handleMouseDown);
      canvas.removeEventListener('mousemove', handleMouseMove);
      canvas.removeEventListener('mouseup', handleMouseUp);
      canvas.removeEventListener('mouseleave', handleMouseUp);
    };
  }, [filteredGraphData, showLabels, graphDimensions, zoomLevel, panOffset]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="bg-white/10 backdrop-blur-sm rounded-xl border border-white/20 shadow-2xl p-8 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white mx-auto mb-4"></div>
            <div className="text-white mb-2">Loading radial visualization...</div>
            <div className="text-white/70 text-sm">Querying Neo4j database for: {selectedGazette}</div>
            <div className="text-white/50 text-xs mt-2">This may take up to 30 seconds for complex queries</div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="bg-white/10 backdrop-blur-sm rounded-xl border border-white/20 shadow-2xl p-8 text-center">
            <div className="text-red-400 mb-4">Error: {error}</div>
            <button
              onClick={() => {
                setError(null);
                loadGazetteData();
              }}
              className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Retry Loading
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!gazetteStructure) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-6 text-white shadow-lg mb-6">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                <Zap className="h-5 w-5" />
              </div>
              <div>
                <h1 className="text-2xl font-bold">Radial Ministry Visualization</h1>
                <p className="text-blue-100">Explore ministry relationships in a radial network layout</p>
              </div>
            </div>
            <div className="bg-green-500/20 border border-green-300/30 rounded-lg p-2 mt-3">
              <p className="text-sm text-green-100">
                🗄️ <strong>Live Data:</strong> Loading actual government structure data from Neo4j database.
              </p>
            </div>
          </div>

          {/* Welcome State */}
          <div className="bg-white/10 backdrop-blur-sm rounded-xl border border-white/20 shadow-2xl p-8 text-center">
            <div className="text-6xl mb-4">🌐</div>
            <h3 className="text-xl font-semibold text-white mb-2">Welcome to Radial Visualization</h3>
            <p className="text-white/70 mb-4">
              Enter a gazette ID below to explore the ministry structure in a beautiful radial layout.
            </p>
            <div className="bg-green-500/20 border border-green-300/30 rounded-lg p-3 mb-6">
              <p className="text-sm text-green-100">
                <strong>Real Data:</strong> Loading actual government structure data from Neo4j database.
              </p>
            </div>

            {/* Input Controls */}
            <div className="max-w-md mx-auto space-y-4">
              <div className="flex gap-3">
                <input
                  type="text"
                  value={selectedGazette}
                  onChange={(e) => setSelectedGazette(e.target.value)}
                  placeholder="Enter Gazette ID (e.g., 1897/15)"
                  className="flex-1 px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                  onClick={loadGazetteData}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Load
                </button>
              </div>
              
              <div className="text-sm text-white/60">
                <p>Quick start with sample gazettes:</p>
                <div className="flex gap-2 mt-2 justify-center">
                  <button
                    onClick={() => {
                      setSelectedGazette('1897/15');
                      loadGazetteData();
                    }}
                    className="px-3 py-1 bg-white/10 text-white rounded text-xs hover:bg-white/20 transition-colors"
                  >
                    1897/15
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-6 text-white shadow-lg mb-6">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
              <Zap className="h-5 w-5" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">Radial Ministry Visualization</h1>
              <p className="text-blue-100">Explore ministry relationships in a radial network layout</p>
            </div>
          </div>
          <div className="bg-green-500/20 border border-green-300/30 rounded-lg p-2 mt-3">
            <p className="text-sm text-green-100">
              🗄️ <strong>Live Data:</strong> Showing real government structure data from Neo4j for {selectedGazette}
            </p>
          </div>
        </div>

        {/* Controls */}
        <div className="bg-white/10 backdrop-blur-sm rounded-xl border border-white/20 shadow-2xl p-4 mb-6">
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-2">
              <label className="text-white text-sm">Gazette:</label>
              <input
                type="text"
                value={selectedGazette}
                onChange={(e) => setSelectedGazette(e.target.value)}
                className="px-3 py-1 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                onClick={loadGazetteData}
                className="px-4 py-1 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
              >
                Load
              </button>
            </div>

            <div className="flex items-center gap-2">
              <Search className="h-4 w-4 text-white/70" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search nodes..."
                className="px-3 py-1 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
              />
            </div>

            <label className="flex items-center gap-2 text-sm text-white">
              <input
                type="checkbox"
                checked={showPerformanceMode}
                onChange={(e) => setShowPerformanceMode(e.target.checked)}
                className="rounded"
              />
              Performance Mode
            </label>

            <label className="flex items-center gap-2 text-sm text-white">
              <input
                type="checkbox"
                checked={showLabels}
                onChange={(e) => setShowLabels(e.target.checked)}
                className="rounded"
              />
              Show Labels
            </label>

            {/* Zoom Controls */}
            <div className="flex items-center gap-2">
              <button
                onClick={handleZoomOut}
                className="px-3 py-1 bg-white/10 border border-white/20 text-white rounded-lg hover:bg-white/20 transition-colors text-sm"
              >
                −
              </button>
              <span className="text-white text-sm min-w-[60px] text-center">
                {Math.round(zoomLevel * 100)}%
              </span>
              <button
                onClick={handleZoomIn}
                className="px-3 py-1 bg-white/10 border border-white/20 text-white rounded-lg hover:bg-white/20 transition-colors text-sm"
              >
                +
              </button>
              <button
                onClick={handleResetZoom}
                className="px-3 py-1 bg-white/10 border border-white/20 text-white rounded-lg hover:bg-white/20 transition-colors text-sm"
              >
                Reset
              </button>
            </div>

            <button
              onClick={exportGraph}
              className="flex items-center gap-2 px-3 py-1 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm"
            >
              <Download className="h-4 w-4" />
              Export
            </button>
          </div>
        </div>

        {/* Radial Visualization */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <div className="lg:col-span-3">
            <div className="bg-white/10 backdrop-blur-sm rounded-xl border border-white/20 shadow-2xl p-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">Radial Network</h3>
                <div className="flex items-center gap-3">
                  {showPerformanceMode && (
                    <span className="text-xs bg-yellow-500/20 text-yellow-200 px-2 py-1 rounded">
                      Performance Mode (15 ministers)
                    </span>
                  )}
                  <div className="text-sm text-white/70">
                    {filteredGraphData.nodes.length} nodes, {filteredGraphData.links.length} links
                  </div>
                </div>
              </div>
              
              <div className="relative">
                <canvas
                  id="radial-canvas"
                  width={graphDimensions.width}
                  height={graphDimensions.height}
                  className="border border-white/20 rounded-lg bg-black/20 cursor-grab active:cursor-grabbing"
                  style={{ width: '100%', height: '600px' }}
                />
                <div className="absolute top-2 left-2 bg-black/50 text-white text-xs p-2 rounded">
                  <div>🖱️ Mouse wheel: Zoom in/out</div>
                  <div>🖱️ Drag: Pan around</div>
                  <div>👆 Click: Select node</div>
                </div>
              </div>
            </div>
          </div>

          {/* Details Panel */}
          <div className="space-y-4">
            {/* Legend */}
            <div className="bg-white/10 backdrop-blur-sm rounded-xl border border-white/20 shadow-2xl p-4">
              <h3 className="text-lg font-semibold text-white mb-3">Legend</h3>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded-full bg-blue-500"></div>
                  <span className="text-sm text-white">Gazette</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded-full bg-gradient-to-r from-red-500 to-purple-500"></div>
                  <span className="text-sm text-white">Ministers</span>
                </div>
              </div>
            </div>

            {/* Selected Node Details */}
            {selectedNode && (
              <div className="bg-white/10 backdrop-blur-sm rounded-xl border border-white/20 shadow-2xl p-4">
                <h3 className="text-lg font-semibold text-white mb-3">Node Details</h3>
                <div className="space-y-2 text-sm">
                  <div>
                    <span className="font-medium text-white">Name:</span>
                    <span className="ml-2 text-white/80">{selectedNode.label}</span>
                  </div>
                  <div>
                    <span className="font-medium text-white">Type:</span>
                    <span className="ml-2 text-white/80 capitalize">{selectedNode.type}</span>
                  </div>
                  {selectedNode.details && Object.entries(selectedNode.details).map(([key, value]) => (
                    <div key={key}>
                      <span className="font-medium text-white capitalize">{key.replace('_', ' ')}:</span>
                      <span className="ml-2 text-white/80">
                        {Array.isArray(value) ? value.join(', ') : String(value)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Statistics */}
            <div className="bg-white/10 backdrop-blur-sm rounded-xl border border-white/20 shadow-2xl p-4">
              <h3 className="text-lg font-semibold text-white mb-3">Statistics</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-white/70">Total Ministers:</span>
                  <span className="font-medium text-white">{gazetteStructure.ministers.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/70">Gazette ID:</span>
                  <span className="font-medium text-white">{gazetteStructure.gazette_id}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/70">Published:</span>
                  <span className="font-medium text-white">{gazetteDetails?.gazette.published_date || 'N/A'}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
