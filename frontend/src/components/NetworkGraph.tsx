import React, { useEffect, useRef, useState } from 'react';
import { useData } from '../contexts/DataContext';
import { Network, DataSet } from 'vis-network/standalone';
import { 
  ZoomIn, 
  ZoomOut, 
  RefreshCw,
  Network as NetworkIcon,
  Building2,
  BookOpen,
  Settings,
  MapPin,
  Users,
  GitBranch,
  Filter,
  Search,
  BarChart3,
  Eye,
  EyeOff
} from 'lucide-react';

interface NetworkNode {
  id: string;
  label: string;
  group: 'ministry' | 'department' | 'law' | 'function' | 'region';
  size: number;
  title?: string;
  color?: string;
}

interface NetworkEdge {
  from: string;
  to: string;
  label?: string;
  arrows?: string;
  color?: string;
  width?: number;
}

interface NetworkData {
  nodes: NetworkNode[];
  edges: NetworkEdge[];
}

const NetworkGraph: React.FC = () => {
  const { treeData, loading, error } = useData();
  const networkRef = useRef<HTMLDivElement>(null);
  const networkInstance = useRef<Network | null>(null);
  const [networkData, setNetworkData] = useState<NetworkData | null>(null);
  const [selectedGroup, setSelectedGroup] = useState<string>('all');
  const [zoomLevel, setZoomLevel] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  const [showLabels, setShowLabels] = useState(true);
  const [physicsEnabled, setPhysicsEnabled] = useState(true);

  // Mock network data - replace with actual Neo4j queries
  useEffect(() => {
    if (treeData) {
      // Generate network data from tree structure
      const nodes: NetworkNode[] = [];
      const edges: NetworkEdge[] = [];
      
      // Add root node
      nodes.push({
        id: 'root',
        label: 'Government of Sri Lanka',
        group: 'ministry',
        size: 30,
        color: '#1e40af'
      });

      // Add ministries
      treeData.children?.forEach((minister, index) => {
        const ministryId = `ministry-${index}`;
        nodes.push({
          id: ministryId,
          label: minister.name,
          group: 'ministry',
          size: 25,
          color: '#059669',
          title: `Ministry: ${minister.name}\nStatus: ${minister.status}\nSource: ${minister.source}`
        });

        // Connect to root
        edges.push({
          from: 'root',
          to: ministryId,
          label: 'governs',
          arrows: 'to',
          color: '#6b7280',
          width: 2
        });

        // Add departments
        minister.children?.forEach((dept, deptIndex) => {
          const deptId = `dept-${index}-${deptIndex}`;
          nodes.push({
            id: deptId,
            label: dept.name,
            group: 'department',
            size: 20,
            color: '#7c3aed',
            title: `Department: ${dept.name}\nType: ${dept.type}\nStatus: ${dept.status}`
          });

          // Connect department to ministry
          edges.push({
            from: ministryId,
            to: deptId,
            label: 'has',
            arrows: 'to',
            color: '#10b981',
            width: 1
          });
        });
      });

      // Add some additional relationships (laws, functions, regions)
      const additionalNodes: NetworkNode[] = [
        { id: 'law-1', label: 'Constitution', group: 'law', size: 18, color: '#dc2626' },
        { id: 'law-2', label: 'Public Service Act', group: 'law', size: 18, color: '#dc2626' },
        { id: 'function-1', label: 'Administration', group: 'function', size: 18, color: '#f59e0b' },
        { id: 'function-2', label: 'Policy Making', group: 'function', size: 18, color: '#f59e0b' },
        { id: 'region-1', label: 'Western Province', group: 'region', size: 18, color: '#8b5cf6' },
        { id: 'region-2', label: 'Central Province', group: 'region', size: 18, color: '#8b5cf6' }
      ];

      const additionalEdges: NetworkEdge[] = [
        { from: 'law-1', to: 'ministry-0', label: 'regulates', arrows: 'to', color: '#ef4444' },
        { from: 'law-2', to: 'ministry-1', label: 'regulates', arrows: 'to', color: '#ef4444' },
        { from: 'function-1', to: 'dept-0-0', label: 'performs', arrows: 'to', color: '#f59e0b' },
        { from: 'function-2', to: 'dept-1-0', label: 'performs', arrows: 'to', color: '#f59e0b' },
        { from: 'region-1', to: 'dept-0-0', label: 'located in', arrows: 'to', color: '#8b5cf6' },
        { from: 'region-2', to: 'dept-1-0', label: 'located in', arrows: 'to', color: '#8b5cf6' }
      ];

      nodes.push(...additionalNodes);
      edges.push(...additionalEdges);

      setNetworkData({ nodes, edges });
    }
  }, [treeData]);

  // Initialize network visualization
  useEffect(() => {
    if (networkRef.current && networkData) {
      const container = networkRef.current;
      
      // Create nodes dataset with proper typing
      const nodes = new DataSet(networkData.nodes as any);
      const edges = new DataSet(networkData.edges as any);

      // Network options
      const options = {
        nodes: {
          shape: 'dot',
          font: {
            size: showLabels ? 14 : 0,
            face: 'Inter',
            color: '#1f2937',
            strokeWidth: 2,
            strokeColor: '#ffffff'
          },
          borderWidth: 2,
          shadow: true,
          shadowBlur: 10,
          shadowColor: 'rgba(0, 0, 0, 0.3)',
          shadowOffsetX: 2,
          shadowOffsetY: 2
        },
        edges: {
          font: {
            size: showLabels ? 12 : 0,
            face: 'Inter',
            color: '#6b7280',
            strokeWidth: 1,
            strokeColor: '#ffffff'
          },
          smooth: {
            enabled: true,
            type: 'continuous',
            forceDirection: 'none',
            roundness: 0.5
          },
          shadow: true,
          shadowBlur: 5,
          shadowColor: 'rgba(0, 0, 0, 0.2)'
        },
        physics: {
          enabled: physicsEnabled,
          solver: 'forceAtlas2Based',
          forceAtlas2Based: {
            gravitationalConstant: -50,
            centralGravity: 0.01,
            springLength: 100,
            springConstant: 0.08,
            damping: 0.4,
            avoidOverlap: 0.5
          },
          stabilization: {
            enabled: true,
            iterations: 1000,
            updateInterval: 100
          }
        },
        interaction: {
          hover: true,
          tooltipDelay: 200,
          zoomView: true,
          dragView: true,
          selectConnectedEdges: true
        },
        layout: {
          improvedLayout: true,
          hierarchical: {
            enabled: false,
            direction: 'UD',
            sortMethod: 'directed'
          }
        }
      } as any;

      // Create network
      const network = new Network(container, { nodes: nodes as any, edges: edges as any }, options);
      networkInstance.current = network;

      // Event listeners
      network.on('zoom', (params) => {
        setZoomLevel(params.scale);
      });

      network.on('select', (params) => {
        if (params.nodes.length > 0) {
          const selectedNode = nodes.get(params.nodes[0]);
          console.log('Selected node:', selectedNode);
        }
      });

      // Cleanup
      return () => {
        if (networkInstance.current) {
          networkInstance.current.destroy();
        }
      };
    }
  }, [networkData, showLabels, physicsEnabled]);

  const filterByGroup = (group: string) => {
    setSelectedGroup(group);
    if (networkInstance.current && networkData) {
      const nodes = new DataSet(
        (group === 'all' 
          ? networkData.nodes 
          : networkData.nodes.filter(node => node.group === group)) as any
      );
      
      const edges = new DataSet(
        (group === 'all'
          ? networkData.edges
          : networkData.edges.filter(edge => {
              const fromNode = networkData.nodes.find(n => n.id === edge.from);
              const toNode = networkData.nodes.find(n => n.id === edge.to);
              return fromNode?.group === group || toNode?.group === group;
            })) as any
      );

      networkInstance.current.setData({ nodes: nodes as any, edges: edges as any });
    }
  };

  const resetView = () => {
    if (networkInstance.current) {
      networkInstance.current.fit();
      setZoomLevel(1);
    }
  };

  const zoomIn = () => {
    if (networkInstance.current) {
      networkInstance.current.moveTo({ scale: zoomLevel * 1.2 });
    }
  };

  const zoomOut = () => {
    if (networkInstance.current) {
      networkInstance.current.moveTo({ scale: zoomLevel * 0.8 });
    }
  };

  const toggleLabels = () => {
    setShowLabels(!showLabels);
  };

  const togglePhysics = () => {
    setPhysicsEnabled(!physicsEnabled);
  };

  // Filter nodes based on search
  const filteredNodes = networkData?.nodes.filter(node => 
    node.label.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading network visualization...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <p>Error loading network data: {error}</p>
      </div>
    );
  }

  if (!networkData) {
    return (
      <div className="error-container">
        <p>No network data available</p>
      </div>
    );
  }

  return (
    <div className="network-graph">
      {/* Enhanced Header with Stats */}
      <div className="graph-header">
        <div className="header-content">
          <div className="title-main">
            <h2>Government Structure Network</h2>
            <p>Interactive visualization of relationships between ministries, departments, and entities</p>
          </div>
          <div className="title-stats">
            <div className="stat-item">
              <NetworkIcon size={20} className="stat-icon" />
              <div className="stat-content">
                <span className="stat-value">{networkData.nodes.length}</span>
                <span className="stat-label">Entities</span>
              </div>
            </div>
            <div className="stat-item">
              <GitBranch size={20} className="stat-icon" />
              <div className="stat-content">
                <span className="stat-value">{networkData.edges.length}</span>
                <span className="stat-label">Relationships</span>
              </div>
            </div>
            <div className="stat-item">
              <Users size={20} className="stat-icon" />
              <div className="stat-content">
                <span className="stat-value">{networkData.nodes.filter(n => n.group === 'ministry').length}</span>
                <span className="stat-label">Ministries</span>
              </div>
            </div>
          </div>
        </div>
        <div className="header-actions">
          <div className="control-group">
            <button 
              onClick={togglePhysics}
              className={`btn-control ${physicsEnabled ? 'active' : ''}`}
              title={physicsEnabled ? 'Disable Physics' : 'Enable Physics'}
            >
              <Settings size={18} />
            </button>
            <button 
              onClick={toggleLabels}
              className={`btn-control ${showLabels ? 'active' : ''}`}
              title={showLabels ? 'Hide Labels' : 'Show Labels'}
            >
              {showLabels ? <Eye size={18} /> : <EyeOff size={18} />}
            </button>
            <button onClick={resetView} className="btn-control" title="Reset View">
              <RefreshCw size={18} />
            </button>
          </div>
        </div>
      </div>

      {/* Enhanced Search and Filter Bar */}
      <div className="search-filter-bar">
        <div className="search-container">
          <Search size={20} className="search-icon" />
          <input
            type="text"
            placeholder="Search entities..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>
        <div className="filter-container">
          <Filter size={18} className="filter-icon" />
          <select
            value={selectedGroup}
            onChange={(e) => filterByGroup(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Types</option>
            <option value="ministry">Ministries</option>
            <option value="department">Departments</option>
            <option value="law">Laws</option>
            <option value="function">Functions</option>
            <option value="region">Regions</option>
          </select>
        </div>
        <div className="zoom-controls">
          <button onClick={zoomOut} className="zoom-btn" title="Zoom Out">
            <ZoomOut size={16} />
          </button>
          <span className="zoom-level">{Math.round(zoomLevel * 100)}%</span>
          <button onClick={zoomIn} className="zoom-btn" title="Zoom In">
            <ZoomIn size={16} />
          </button>
        </div>
      </div>

      {/* Enhanced Legend */}
      <div className="graph-legend">
        <div className="legend-section">
          <h4 className="legend-title">Entity Types</h4>
          <div className="legend-items">
            <div className="legend-item">
              <div className="legend-color ministry"></div>
              <span>Ministries</span>
            </div>
            <div className="legend-item">
              <div className="legend-color department"></div>
              <span>Departments</span>
            </div>
            <div className="legend-item">
              <div className="legend-color law"></div>
              <span>Laws</span>
            </div>
            <div className="legend-item">
              <div className="legend-color function"></div>
              <span>Functions</span>
            </div>
            <div className="legend-item">
              <div className="legend-color region"></div>
              <span>Regions</span>
            </div>
          </div>
        </div>
        <div className="legend-section">
          <h4 className="legend-title">Quick Filters</h4>
          <div className="filter-buttons">
            <button 
              className={`filter-btn ${selectedGroup === 'all' ? 'active' : ''}`}
              onClick={() => filterByGroup('all')}
            >
              All
            </button>
            <button 
              className={`filter-btn ${selectedGroup === 'ministry' ? 'active' : ''}`}
              onClick={() => filterByGroup('ministry')}
            >
              Ministries
            </button>
            <button 
              className={`filter-btn ${selectedGroup === 'department' ? 'active' : ''}`}
              onClick={() => filterByGroup('department')}
            >
              Departments
            </button>
          </div>
        </div>
      </div>

      {/* Network Container */}
      <div className="network-container">
        <div ref={networkRef} className="network-canvas"></div>
      </div>

      {/* Enhanced Instructions */}
      <div className="graph-instructions">
        <p>💡 <strong>Tip:</strong> Drag nodes to rearrange, scroll to zoom, and click nodes to see details. Use filters to focus on specific entity types.</p>
        <div className="instruction-details">
          <span>🔍 <strong>Search:</strong> Find specific entities</span>
          <span>🎯 <strong>Filter:</strong> Focus on entity types</span>
          <span>⚡ <strong>Physics:</strong> Toggle automatic layout</span>
          <span>🏷️ <strong>Labels:</strong> Show/hide text labels</span>
        </div>
      </div>
    </div>
  );
};

export default NetworkGraph;
