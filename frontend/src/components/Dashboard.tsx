import { useData } from '../contexts/DataContext'
import { Link } from 'react-router-dom'
import { 
  TrendingUp, 
  TrendingDown, 
  Minus, 
  AlertTriangle, 
  RefreshCw, 
  Building2, 
  GitBranch,
  BarChart3
} from 'lucide-react'

const Dashboard: React.FC = () => {
  const { summaryData, loading, error } = useData()

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'added':
        return <TrendingUp style={{ width: '1.5rem', height: '1.5rem', color: '#059669' }} />
      case 'removed':
        return <TrendingDown style={{ width: '1.5rem', height: '1.5rem', color: '#dc2626' }} />
      case 'modified':
        return <AlertTriangle style={{ width: '1.5rem', height: '1.5rem', color: '#d97706' }} />
      default:
        return <Minus style={{ width: '1.5rem', height: '1.5rem', color: '#6b7280' }} />
    }
  }

  const getNodeTypeLabel = (nodeType: string) => {
    // Provide meaningful labels for node types
    switch (nodeType.toLowerCase()) {
      case 'department':
        return 'Government Departments'
      case 'function':
        return 'Administrative Functions'
      case 'law':
        return 'Legal Statutes'
      case 'gazette':
        return 'Official Gazettes'
      case 'minister':
        return 'Ministries'
      default:
        return nodeType.charAt(0).toUpperCase() + nodeType.slice(1)
    }
  }

  const getChangeStatusLabel = (status: string) => {
    // Provide meaningful labels for change statuses
    switch (status.toLowerCase()) {
      case 'added_departments':
        return 'New Departments Added'
      case 'added_laws':
        return 'New Laws Added'
      case 'added_functions':
        return 'New Functions Added'
      case 'removed_departments':
        return 'Departments Removed'
      case 'removed_laws':
        return 'Laws Removed'
      case 'removed_functions':
        return 'Functions Removed'
      case 'modified_departments':
        return 'Departments Modified'
      case 'modified_laws':
        return 'Laws Modified'
      case 'modified_functions':
        return 'Functions Modified'
      default:
        return status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    }
  }

  const handleRefresh = () => {
    // Refresh functionality removed - using mock data
    console.log('Refresh clicked - using mock data');
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '400px' }}>
        <div style={{ textAlign: 'center' }}>
          <RefreshCw style={{ width: '2rem', height: '2rem', color: '#2563eb', animation: 'spin 1s linear infinite' }} />
          <p style={{ color: '#6b7280', marginTop: '1rem' }}>Loading dashboard data...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div style={{
        backgroundColor: 'white',
        borderRadius: '1rem',
        padding: '2rem',
        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
        border: '1px solid #e5e7eb',
        textAlign: 'center'
      }}>
        <AlertTriangle style={{ width: '3rem', height: '3rem', color: '#dc2626', margin: '0 auto 1rem' }} />
        <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827', marginBottom: '0.5rem' }}>Error Loading Data</h3>
        <p style={{ color: '#6b7280', marginBottom: '1rem' }}>{error}</p>
        <button 
          onClick={handleRefresh}
          style={{
            backgroundColor: '#2563eb',
            color: 'white',
            border: 'none',
            padding: '0.75rem 1.5rem',
            borderRadius: '0.75rem',
            fontSize: '0.875rem',
            fontWeight: '600',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            margin: '0 auto',
            transition: 'all 0.2s ease'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = '#1d4ed8'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = '#2563eb'
          }}
        >
          <RefreshCw style={{ width: '1rem', height: '1rem' }} />
          Retry
        </button>
      </div>
    )
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Header */}
      <div style={{ textAlign: 'center' }}>
        <h1 style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#111827', marginBottom: '0.75rem' }}>
          Government Structure Dashboard
        </h1>
        <p style={{ fontSize: '1.25rem', color: '#6b7280', maxWidth: '600px', margin: '0 auto' }}>
          Track and analyze changes in ministerial structures and government departments
        </p>
      </div>

      {/* Quick Actions */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
        <Link 
          to="/tree" 
          style={{
            backgroundColor: 'white',
            borderRadius: '1rem',
            padding: '2rem',
            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
            border: '1px solid #e5e7eb',
            textDecoration: 'none',
            color: 'inherit',
            transition: 'all 0.2s ease',
            cursor: 'pointer'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateY(-4px)'
            e.currentTarget.style.boxShadow = '0 12px 25px -5px rgba(0, 0, 0, 0.1)'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(0)'
            e.currentTarget.style.boxShadow = '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
            <div style={{
              width: '4rem',
              height: '4rem',
              backgroundColor: '#dcfce7',
              borderRadius: '1rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'all 0.2s ease'
            }}>
              <GitBranch style={{ width: '2rem', height: '2rem', color: '#059669' }} />
            </div>
            <div>
              <h3 style={{ fontWeight: '600', color: '#111827', fontSize: '1.25rem', marginBottom: '0.5rem' }}>Ministry Tiles</h3>
              <p style={{ fontSize: '0.875rem', color: '#6b7280', lineHeight: '1.5' }}>Interactive colorful tiles showing all ministries and their departments</p>
            </div>
          </div>
        </Link>

        <Link 
          to="/analytics" 
          style={{
            backgroundColor: 'white',
            borderRadius: '1rem',
            padding: '2rem',
            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
            border: '1px solid #e5e8f0',
            textDecoration: 'none',
            color: 'inherit',
            transition: 'all 0.2s ease',
            cursor: 'pointer'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateY(-4px)'
            e.currentTarget.style.boxShadow = '0 12px 25px -5px rgba(0, 0, 0, 0.1)'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(0)'
            e.currentTarget.style.boxShadow = '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
            <div style={{
              width: '4rem',
              height: '4rem',
              backgroundColor: '#dbeafe',
              borderRadius: '1rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'all 0.2s ease'
            }}>
              <BarChart3 style={{ width: '2rem', height: '2rem', color: '#2563eb' }} />
            </div>
            <div>
              <h3 style={{ fontWeight: '600', color: '#111827', fontSize: '1.25rem', marginBottom: '0.5rem' }}>Analytics Dashboard</h3>
              <p style={{ fontSize: '0.875rem', color: '#6b7280', lineHeight: '1.5' }}>Comprehensive analytics and insights from Neo4j database</p>
            </div>
          </div>
        </Link>

        <Link 
          to="/network" 
          style={{
            backgroundColor: 'white',
            borderRadius: '1rem',
            padding: '2rem',
            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
            border: '1px solid #e5e7eb',
            textDecoration: 'none',
            color: 'inherit',
            transition: 'all 0.2s ease',
            cursor: 'pointer'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateY(-4px)'
            e.currentTarget.style.boxShadow = '0 12px 25px -5px rgba(0, 0, 0, 0.1)'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(0)'
            e.currentTarget.style.boxShadow = '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
            <div style={{
              width: '4rem',
              height: '4rem',
              backgroundColor: '#f3e8ff',
              borderRadius: '1rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'all 0.2s ease'
            }}>
              <GitBranch style={{ width: '2rem', height: '2rem', color: '#7c3aed' }} />
            </div>
            <div>
              <h3 style={{ fontWeight: '600', color: '#111827', fontSize: '1.25rem', marginBottom: '0.5rem' }}>Network Graph</h3>
              <p style={{ fontSize: '0.875rem', color: '#6b7280', lineHeight: '1.5' }}>Interactive network visualization of government relationships</p>
            </div>
          </div>
        </Link>

        <Link 
          to="/departments" 
          style={{
            backgroundColor: 'white',
            borderRadius: '1rem',
            padding: '2rem',
            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
            border: '1px solid #e5e7eb',
            textDecoration: 'none',
            color: 'inherit',
            transition: 'all 0.2s ease',
            cursor: 'pointer'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateY(-4px)'
            e.currentTarget.style.boxShadow = '0 12px 25px -5px rgba(0, 0, 0, 0.1)'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(0)'
            e.currentTarget.style.boxShadow = '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
            <div style={{
              width: '4rem',
              height: '4rem',
              backgroundColor: '#dcfce7',
              borderRadius: '1rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'all 0.2s ease'
            }}>
              <Building2 style={{ width: '2rem', height: '2rem', color: '#059669' }} />
            </div>
            <div>
              <h3 style={{ fontWeight: '600', color: '#111827', fontSize: '1.25rem', marginBottom: '0.5rem' }}>Department Changes</h3>
              <p style={{ fontSize: '0.875rem', color: '#6b7280', lineHeight: '1.5' }}>Detailed analysis of all department modifications and updates</p>
            </div>
          </div>
        </Link>

        <button 
          onClick={handleRefresh}
          style={{
            backgroundColor: 'white',
            borderRadius: '1rem',
            padding: '2rem',
            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
            border: '1px solid #e5e7eb',
            textAlign: 'left',
            cursor: 'pointer',
            transition: 'all 0.2s ease',
            width: '100%'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateY(-4px)'
            e.currentTarget.style.boxShadow = '0 12px 25px -5px rgba(0, 0, 0, 0.1)'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(0)'
            e.currentTarget.style.boxShadow = '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
            <div style={{
              width: '4rem',
              height: '4rem',
              backgroundColor: '#fef3c7',
              borderRadius: '1rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'all 0.2s ease'
            }}>
              <RefreshCw style={{ width: '2rem', height: '2rem', color: '#d97706' }} />
            </div>
            <div>
              <h3 style={{ fontWeight: '600', color: '#111827', fontSize: '1.25rem', marginBottom: '0.5rem' }}>Refresh Data</h3>
              <p style={{ fontSize: '0.875rem', color: '#6b7280', lineHeight: '1.5' }}>Update all data from the database and sync changes</p>
            </div>
          </div>
        </button>
      </div>

      {/* Statistics */}
      {summaryData && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(450px, 1fr))', gap: '2rem' }}>
          {/* Node Counts */}
          <div style={{
            backgroundColor: 'white',
            borderRadius: '1rem',
            padding: '2rem',
            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
            border: '1px solid #e5e7eb'
          }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: '600', color: '#111827', marginBottom: '1.5rem', display: 'flex', alignItems: 'center' }}>
              <BarChart3 style={{ width: '1.5rem', height: '1.5rem', marginRight: '0.75rem', color: '#2563eb' }} />
              Node Counts
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {(() => {
                // Deduplicate and process node counts to avoid repetitive entries
                const processedCounts = new Map();
                
                summaryData.node_counts?.forEach((item) => {
                  const nodeType = item.node_type;
                  const count = item.count;
                  
                  if (processedCounts.has(nodeType)) {
                    // If we already have this type, update with the latest count
                    processedCounts.set(nodeType, count);
                  } else {
                    // First time seeing this type
                    processedCounts.set(nodeType, count);
                  }
                });
                
                // Convert to array and sort by count (descending)
                const sortedCounts = Array.from(processedCounts.entries())
                  .map(([type, count]) => ({ type, count }))
                  .sort((a, b) => (b.count as number) - (a.count as number));
                
                return sortedCounts.map((item, index) => (
                  <div key={index} style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '1rem',
                    backgroundColor: '#f9fafb',
                    borderRadius: '0.75rem',
                    border: '1px solid #e5e7eb'
                  }}>
                    <span style={{ fontWeight: '500', color: '#374151', fontSize: '0.875rem' }}>
                      {getNodeTypeLabel(item.type)}
                    </span>
                    <span style={{ fontSize: '1.75rem', fontWeight: 'bold', color: '#2563eb' }}>
                      {item.count}
                    </span>
                  </div>
                ));
              })()}
            </div>
          </div>

          {/* Changes Summary */}
          <div style={{
            backgroundColor: 'white',
            borderRadius: '1rem',
            padding: '2rem',
            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
            border: '1px solid #e5e7eb'
          }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: '600', color: '#111827', marginBottom: '1.5rem', display: 'flex', alignItems: 'center' }}>
              <TrendingUp style={{ width: '1.5rem', height: '1.5rem', marginRight: '0.75rem', color: '#2563eb' }} />
              Changes Summary
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {(() => {
                // Process changes to avoid repetitive entries and provide better labels
                const processedChanges = new Map();
                
                summaryData.changes?.forEach((item) => {
                  const status = item.status;
                  const count = item.count;
                  
                  if (processedChanges.has(status)) {
                    // If we already have this status, add the counts
                    processedChanges.set(status, (processedChanges.get(status) || 0) + count);
                  } else {
                    // First time seeing this status
                    processedChanges.set(status, count);
                  }
                });
                
                // Convert to array and sort by count (descending)
                const sortedChanges = Array.from(processedChanges.entries())
                  .map(([status, count]) => ({ status, count }))
                  .sort((a, b) => (b.count as number) - (a.count as number));
                
                return sortedChanges.map((item, index) => (
                  <div key={index} style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '1rem',
                    backgroundColor: '#f9fafb',
                    borderRadius: '0.75rem',
                    border: '1px solid #e5e7eb'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                      {getStatusIcon(item.status)}
                      <span style={{ fontWeight: '500', color: '#374151', fontSize: '0.875rem' }}>
                        {getChangeStatusLabel(item.status)}
                      </span>
                    </div>
                    <span style={{ fontSize: '1.75rem', fontWeight: 'bold', color: '#2563eb' }}>
                      {item.count}
                    </span>
                  </div>
                ));
              })()}
            </div>
          </div>
        </div>
      )}

      {/* Legend */}
      <div style={{
        backgroundColor: 'white',
        borderRadius: '1rem',
        padding: '2rem',
        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
        border: '1px solid #e5e7eb'
      }}>
        <h3 style={{ fontSize: '1.25rem', fontWeight: '600', color: '#111827', marginBottom: '1.5rem' }}>Legend & Status Guide</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem' }}>
          {[
            { status: 'Added', description: 'New ministries or departments added to the structure', icon: <TrendingUp style={{ width: '1.25rem', height: '1.25rem' }} /> },
            { status: 'Removed', description: 'Ministries or departments removed from the structure', icon: <TrendingDown style={{ width: '1.25rem', height: '1.25rem' }} /> },
            { status: 'Modified', description: 'Existing ministries or departments with changes', icon: <AlertTriangle style={{ width: '1.25rem', height: '1.25rem' }} /> },
            { status: 'Unchanged', description: 'No modifications detected in these items', icon: <Minus style={{ width: '1.25rem', height: '1.25rem' }} /> }
          ].map((item) => (
            <div key={item.status} style={{ textAlign: 'center' }}>
              <div style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.75rem',
                padding: '0.75rem 1.25rem',
                borderRadius: '9999px',
                fontSize: '0.875rem',
                fontWeight: '600',
                border: '1px solid #d1d5db',
                backgroundColor: '#f9fafb',
                color: '#374151',
                marginBottom: '0.75rem'
              }}>
                {item.icon}
                <span>{item.status}</span>
              </div>
              <p style={{ fontSize: '0.875rem', color: '#6b7280', lineHeight: '1.4' }}>{item.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default Dashboard
