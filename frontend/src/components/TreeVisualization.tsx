import React, { useState } from 'react';
import { useData, type Minister } from '../contexts/DataContext';
import { Building2, RefreshCw, TrendingUp, TrendingDown, Minus, X, ZoomIn, ZoomOut, Filter, Search, BarChart3, Users } from 'lucide-react';

const TreeVisualization: React.FC = () => {
  const { treeData, loading, error } = useData();
  const [selectedNode, setSelectedNode] = useState<Minister | null>(null);
  const [showDepartments, setShowDepartments] = useState(false);
  const [selectedMinister, setSelectedMinister] = useState<Minister | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  // Enhanced color schemes with better gradients
  const colorSchemes = [
    { bg: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', icon: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', accent: '#8b5cf6' },
    { bg: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', icon: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', accent: '#ec4899' },
    { bg: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', icon: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)', accent: '#06b6d4' },
    { bg: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)', icon: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)', accent: '#10b981' },
    { bg: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)', icon: 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)', accent: '#f59e0b' },
    { bg: 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)', icon: 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)', accent: '#f97316' },
    { bg: 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)', icon: 'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)', accent: '#fb7185' },
    { bg: 'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)', icon: 'linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%)', accent: '#a855f7' },
    { bg: 'linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%)', icon: 'linear-gradient(135deg, #fad0c4 0%, #ffd1ff 100%)', accent: '#c084fc' },
    { bg: 'linear-gradient(135deg, #fad0c4 0%, #ffd1ff 100%)', icon: 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)', accent: '#fbbf24' }
  ];

  const getStatusIcon = (status?: string) => {
    switch (status) {
      case 'added': return <TrendingUp size={16} className="text-green-600" />;
      case 'removed': return <TrendingDown size={16} className="text-red-600" />;
      case 'unchanged': return <Minus size={16} className="text-gray-600" />;
      case 'modified': return <TrendingUp size={16} className="text-yellow-600" />;
      default: return <Minus size={16} className="text-gray-600" />;
    }
  };

  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'added': return 'bg-green-50 border-green-200 text-green-800';
      case 'removed': return 'bg-red-50 border-red-200 text-red-800';
      case 'unchanged': return 'bg-gray-50 border-gray-200 text-gray-800';
      case 'modified': return 'bg-yellow-50 border-yellow-200 text-yellow-800';
      default: return 'bg-gray-50 border-gray-200 text-gray-800';
    }
  };

  const getSourceColor = (source?: string) => {
    switch (source) {
      case 'base': return 'bg-blue-100 text-blue-800';
      case 'amendment': return 'bg-purple-100 text-purple-800';
      case 'both': return 'bg-indigo-100 text-indigo-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const handleTileClick = (minister: Minister) => {
    setSelectedMinister(minister);
    setShowDepartments(true);
    setSelectedNode(minister);
  };

  const closeDepartmentsModal = () => {
    setShowDepartments(false);
    setSelectedMinister(null);
  };

  const handleRefresh = () => {
    // Refresh functionality removed - using mock data
    console.log('Refresh clicked - using mock data');
  };



  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading government structure...</p>
      </div>
    );
  }

  if (!treeData) {
    return (
      <div className="error-container">
        <p>No tree data available. Please refresh the page.</p>
        <button onClick={handleRefresh} className="btn-primary">
          <RefreshCw size={16} />
          Refresh Data
        </button>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <p>Error loading data: {error}</p>
        <button onClick={handleRefresh} className="btn-primary">
          <RefreshCw size={16} />
          Retry
        </button>
      </div>
    );
  }

  // Filter to get only minister nodes (root level children)
  const ministers = treeData.children?.map(node => ({
    ...node,
    type: 'minister' as const,
    status: node.status || 'unchanged',
    source: node.source || 'base',
    children: node.children?.map(child => ({
      name: child.name,
      type: child.type || 'department',
      status: child.status || 'unchanged',
      source: child.source || 'base'
    }))
  })) as Minister[] || [];

  // Filter ministers based on search and status
  const filteredMinisters = ministers.filter((minister: Minister) => {
    const matchesSearch = minister.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = filterStatus === 'all' || minister.status === filterStatus;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="tree-visualization">
      {/* Enhanced Header with Stats */}
      <div className="tree-header">
        <div className="tree-title">
          <div className="title-main">
            <h2>Government Structure Network</h2>
            <p>Interactive visualization of relationships between ministries, departments, and entities</p>
          </div>
          <div className="title-stats">
            <div className="stat-item">
              <Users size={20} className="stat-icon" />
              <div className="stat-content">
                <span className="stat-value">{ministers.length}</span>
                <span className="stat-label">Ministries</span>
              </div>
            </div>
            <div className="stat-item">
              <Building2 size={20} className="stat-icon" />
              <div className="stat-content">
                <span className="stat-value">{ministers.reduce((acc, m) => acc + (m.children?.length || 0), 0)}</span>
                <span className="stat-label">Departments</span>
              </div>
            </div>
          </div>
        </div>
        <div className="tree-controls">
          <div className="control-group">
            <button 
              onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
              className={`btn-control ${viewMode === 'grid' ? 'active' : ''}`}
              title={`Switch to ${viewMode === 'grid' ? 'list' : 'grid'} view`}
            >
              {viewMode === 'grid' ? <BarChart3 size={18} /> : <Building2 size={18} />}
            </button>
            <button 
              onClick={handleRefresh} 
              className="btn-control"
              title="Refresh data"
            >
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
            placeholder="Search ministries..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>
        <div className="filter-container">
          <Filter size={18} className="filter-icon" />
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Status</option>
            <option value="added">Added</option>
            <option value="removed">Removed</option>
            <option value="modified">Modified</option>
            <option value="unchanged">Unchanged</option>
          </select>
        </div>
        <div className="view-controls">
          <button 
            onClick={() => setViewMode('grid')}
            className={`view-btn ${viewMode === 'grid' ? 'active' : ''}`}
            title="Grid view"
          >
            <Building2 size={16} />
          </button>
          <button 
            onClick={() => setViewMode('list')}
            className={`view-btn ${viewMode === 'list' ? 'active' : ''}`}
            title="List view"
          >
            <BarChart3 size={16} />
          </button>
        </div>
      </div>

      {/* Enhanced Legend */}
      <div className="tree-legend">
        <div className="legend-section">
          <h4 className="legend-title">Status</h4>
          <div className="legend-items">
            <div className="legend-item">
              <div className="legend-color added"></div>
              <span>Added</span>
            </div>
            <div className="legend-item">
              <div className="legend-color removed"></div>
              <span>Removed</span>
            </div>
            <div className="legend-item">
              <div className="legend-color unchanged"></div>
              <span>Unchanged</span>
            </div>
            <div className="legend-item">
              <div className="legend-color modified"></div>
              <span>Modified</span>
            </div>
          </div>
        </div>
        <div className="legend-section">
          <h4 className="legend-title">Source</h4>
          <div className="legend-items">
            <div className="legend-item">
              <div className="legend-color source-base"></div>
              <span>Base</span>
            </div>
            <div className="legend-item">
              <div className="legend-color source-amendment"></div>
              <span>Amendment</span>
            </div>
          </div>
        </div>
      </div>

      <div className="tree-instructions">
        <p>💡 <strong>Tip:</strong> Click on any ministry tile to see departments and detailed information.</p>
      </div>

      {/* Ministries Grid/List */}
      <div className={`ministries-container ${viewMode === 'list' ? 'list-view' : 'grid-view'}`}>
        {filteredMinisters.map((minister, index) => (
          <div
            key={`${minister.name}-${index}`}
            className={`ministry-tile ${selectedNode?.name === minister.name ? 'selected' : ''} ${viewMode === 'list' ? 'list-tile' : ''}`}
            onClick={() => handleTileClick(minister)}
            style={{
              background: colorSchemes[index % colorSchemes.length].bg
            }}
          >
            <div className="tile-header">
              <div className="tile-icon" style={{
                background: colorSchemes[index % colorSchemes.length].icon
              }}>
                <Building2 size={24} className="text-white" />
              </div>
              <div className="tile-status">
                {getStatusIcon(minister.status)}
              </div>
            </div>
            
            <div className="tile-content">
              <h3 className="tile-title">{minister.name}</h3>
              
              <div className="tile-details">
                <div className={`status-badge ${getStatusColor(minister.status)}`}>
                  {minister.status || 'Unknown'}
                </div>
                
                <div className={`source-badge ${getSourceColor(minister.source)}`}>
                  {minister.source || 'Unknown'}
                </div>
              </div>
            </div>

            <div className="tile-footer">
              <span className="tile-type">Ministry</span>
              {minister.children && minister.children.length > 0 && (
                <span className="department-count">{minister.children.length} departments</span>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Enhanced Departments Modal */}
      {showDepartments && selectedMinister && (
        <div className="modal-overlay" onClick={closeDepartmentsModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div className="modal-title">
                <h2>{selectedMinister.name}</h2>
                <p className="modal-subtitle">Department Overview</p>
              </div>
              <button className="modal-close" onClick={closeDepartmentsModal}>
                <X size={24} />
              </button>
            </div>
            
            <div className="modal-body">
              {selectedMinister.children && selectedMinister.children.length > 0 ? (
                <div className="departments-list">
                  {selectedMinister.children.map((dept, index) => (
                    <div key={index} className="department-item">
                      <div className="department-header">
                        <div className="department-icon">
                          <Building2 size={20} className="text-blue-600" />
                        </div>
                        <div className="department-info">
                          <h4 className="department-name">{dept.name}</h4>
                          <div className="department-meta">
                            <span className={`department-type ${getSourceColor(dept.type)}`}>
                              {dept.type}
                            </span>
                            <span className={`department-status ${getStatusColor(dept.status)}`}>
                              {dept.status || 'Unknown'}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="no-departments">
                  <Building2 size={48} className="text-gray-400" />
                  <p>No departments found for this ministry.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {selectedNode && !showDepartments && (
        <div className="node-details">
          <h3>Ministry Details</h3>
          <div className="detail-item">
            <strong>Name:</strong> {selectedNode.name}
          </div>
          <div className="detail-item">
            <strong>Type:</strong> {selectedNode.type || 'Unknown'}
          </div>
          {selectedNode.source && (
            <div className="detail-item">
              <strong>Source:</strong> {selectedNode.source}
            </div>
          )}
          {selectedNode.status && (
            <div className="detail-item">
              <strong>Status:</strong> {selectedNode.status}
            </div>
          )}
          {selectedNode.children && (
            <div className="detail-item">
              <strong>Departments:</strong> {selectedNode.children.length}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default TreeVisualization;
