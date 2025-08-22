import { useState, useMemo } from 'react'
import { useData } from '../contexts/DataContext'
import { 
  Building2, 
  Search, 
  Filter, 
  TrendingUp, 
  TrendingDown, 
  Minus, 
  AlertTriangle,
  RefreshCw,
  Users,
  FileText,
  Settings
} from 'lucide-react'

const DepartmentChanges: React.FC = () => {
  const { departmentChanges, loading, error } = useData()
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [typeFilter, setTypeFilter] = useState('all')

  const filteredChanges = useMemo(() => {
    return departmentChanges.filter(change => {
      const matchesSearch = change.ministry.toLowerCase().includes(searchTerm.toLowerCase()) ||
                            change.department_name.toLowerCase().includes(searchTerm.toLowerCase())
      const matchesStatus = statusFilter === 'all' || change.change_type === statusFilter
      const matchesType = typeFilter === 'all' || change.change_type === typeFilter
      
      return matchesSearch && matchesStatus && matchesType
    })
  }, [departmentChanges, searchTerm, statusFilter, typeFilter])

  const getStatusIcon = (status: string) => {
    switch (status) {
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

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'added':
        return { backgroundColor: '#dcfce7', color: '#166534', borderColor: '#bbf7d0' }
      case 'removed':
        return { backgroundColor: '#fee2e2', color: '#991b1b', borderColor: '#fecaca' }
      case 'modified':
        return { backgroundColor: '#fef3c7', color: '#92400e', borderColor: '#fed7aa' }
      default:
        return { backgroundColor: '#f3f4f6', color: '#374151', borderColor: '#e5e7eb' }
    }
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'department':
        return <Building2 style={{ width: '1rem', height: '1rem' }} />
      case 'law':
        return <FileText style={{ width: '1rem', height: '1rem' }} />
      case 'function':
        return <Settings style={{ width: '1rem', height: '1rem' }} />
      default:
        return <Users style={{ width: '1rem', height: '1rem' }} />
    }
  }

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'department':
        return { backgroundColor: '#dbeafe', color: '#1e40af', borderColor: '#bfdbfe' }
      case 'law':
        return { backgroundColor: '#dcfce7', color: '#166534', borderColor: '#bbf7d0' }
      case 'function':
        return { backgroundColor: '#f3e8ff', color: '#7c3aed', borderColor: '#ddd6fe' }
      default:
        return { backgroundColor: '#f3f4f6', color: '#374151', borderColor: '#e5e7eb' }
    }
  }

  const getChangeCounts = () => {
    const counts: { [key: string]: number } = { added: 0, removed: 0, modified: 0, unchanged: 0 }
    departmentChanges.forEach(change => {
      counts[change.change_type] = (counts[change.change_type] || 0) + 1
    })
    return counts
  }

  const changeCounts = getChangeCounts()

  const handleRefresh = () => {
    // Refresh functionality removed - using mock data
    console.log('Refresh clicked - using mock data');
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '400px' }}>
        <div style={{ textAlign: 'center' }}>
          <RefreshCw style={{ width: '2rem', height: '2rem', color: '#2563eb', animation: 'spin 1s linear infinite' }} />
          <p style={{ color: '#6b7280', marginTop: '1rem' }}>Loading department changes...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="card">
        <div style={{ textAlign: 'center' }}>
          <AlertTriangle style={{ width: '3rem', height: '3rem', color: '#dc2626', margin: '0 auto 1rem' }} />
          <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827', marginBottom: '0.5rem' }}>Error Loading Data</h3>
          <p style={{ color: '#6b7280', marginBottom: '1rem' }}>{error}</p>
          <button onClick={handleRefresh} className="btn-primary">
            <RefreshCw style={{ width: '1rem', height: '1rem', marginRight: '0.5rem' }} />
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h1 style={{ fontSize: '2rem', fontWeight: 'bold', color: '#111827', marginBottom: '0.5rem' }}>Department Changes</h1>
          <p style={{ fontSize: '1.125rem', color: '#6b7280' }}>Track and analyze all government department modifications</p>
        </div>
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
            transition: 'all 0.2s ease',
            boxShadow: '0 4px 6px -1px rgba(37, 99, 235, 0.2)'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = '#1d4ed8'
            e.currentTarget.style.transform = 'translateY(-1px)'
            e.currentTarget.style.boxShadow = '0 6px 8px -1px rgba(37, 99, 235, 0.3)'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = '#2563eb'
            e.currentTarget.style.transform = 'translateY(0)'
            e.currentTarget.style.boxShadow = '0 4px 6px -1px rgba(37, 99, 235, 0.2)'
          }}
        >
          <RefreshCw style={{ width: '1rem', height: '1rem' }} />
          Refresh Data
        </button>
      </div>

      {/* Summary Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem' }}>
        {Object.entries(changeCounts).map(([status, count]) => (
          <div 
            key={status} 
            style={{
              backgroundColor: 'white',
              borderRadius: '1rem',
              padding: '1.5rem',
              boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
              border: '1px solid #e5e7eb',
              textAlign: 'center',
              transition: 'all 0.2s ease',
              cursor: 'pointer'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-2px)'
              e.currentTarget.style.boxShadow = '0 8px 15px -3px rgba(0, 0, 0, 0.1)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)'
              e.currentTarget.style.boxShadow = '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '1rem' }}>
              {getStatusIcon(status)}
            </div>
            <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#111827', marginBottom: '0.5rem' }}>{count}</div>
            <div style={{ fontSize: '0.875rem', color: '#6b7280', textTransform: 'capitalize', fontWeight: '500' }}>{status}</div>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div style={{
        backgroundColor: 'white',
        borderRadius: '1rem',
        padding: '1.5rem',
        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
        border: '1px solid #e5e7eb'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
          <Filter style={{ width: '1.25rem', height: '1.25rem', color: '#6b7280' }} />
          <h3 style={{ fontWeight: '600', color: '#111827', fontSize: '1.125rem' }}>Search & Filter</h3>
        </div>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {/* Search Bar */}
          <div style={{ position: 'relative' }}>
            <Search style={{ 
              position: 'absolute', 
              left: '1rem', 
              top: '50%', 
              transform: 'translateY(-50%)', 
              width: '1.25rem', 
              height: '1.25rem', 
              color: '#9ca3af' 
            }} />
            <input
              type="text"
              placeholder="Search ministers or departments..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{
                width: '100%',
                padding: '1rem 1rem 1rem 3rem',
                border: '1px solid #d1d5db',
                borderRadius: '0.75rem',
                fontSize: '1rem',
                outline: 'none',
                transition: 'all 0.2s ease',
                backgroundColor: '#f9fafb'
              }}
              onFocus={(e) => {
                e.target.style.borderColor = '#2563eb'
                e.target.style.backgroundColor = 'white'
                e.target.style.boxShadow = '0 0 0 3px rgba(37, 99, 235, 0.1)'
              }}
              onBlur={(e) => {
                e.target.style.borderColor = '#d1d5db'
                e.target.style.backgroundColor = '#f9fafb'
                e.target.style.boxShadow = 'none'
              }}
            />
          </div>

          {/* Filter Dropdowns */}
          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
            <div style={{ minWidth: '150px' }}>
              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', color: '#374151', marginBottom: '0.5rem' }}>
                Status
              </label>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  border: '1px solid #d1d5db',
                  borderRadius: '0.5rem',
                  fontSize: '0.875rem',
                  outline: 'none',
                  backgroundColor: 'white',
                  cursor: 'pointer'
                }}
              >
                <option value="all">All Statuses</option>
                <option value="added">Added</option>
                <option value="removed">Removed</option>
                <option value="modified">Modified</option>
                <option value="unchanged">Unchanged</option>
              </select>
            </div>

            <div style={{ minWidth: '150px' }}>
              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', color: '#374151', marginBottom: '0.5rem' }}>
                Type
              </label>
              <select
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  border: '1px solid #d1d5db',
                  borderRadius: '0.5rem',
                  fontSize: '0.875rem',
                  outline: 'none',
                  backgroundColor: 'white',
                  cursor: 'pointer'
                }}
              >
                <option value="all">All Types</option>
                <option value="department">Department</option>
                <option value="law">Law</option>
                <option value="function">Function</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Results Count */}
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'space-between',
        padding: '1rem 0'
      }}>
        <p style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500' }}>
          Showing <strong>{filteredChanges.length}</strong> of <strong>{departmentChanges.length}</strong> changes
        </p>
        {(searchTerm || statusFilter !== 'all' || typeFilter !== 'all') && (
          <button
            onClick={() => {
              setSearchTerm('')
              setStatusFilter('all')
              setTypeFilter('all')
            }}
            style={{
              backgroundColor: '#f3f4f6',
              color: '#374151',
              border: '1px solid #d1d5db',
              padding: '0.5rem 1rem',
              borderRadius: '0.5rem',
              fontSize: '0.875rem',
              fontWeight: '500',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#e5e7eb'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = '#f3f4f6'
            }}
          >
            Clear Filters
          </button>
        )}
      </div>

      {/* Changes List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {filteredChanges.length === 0 ? (
          <div style={{
            backgroundColor: 'white',
            borderRadius: '1rem',
            padding: '3rem 1.5rem',
            textAlign: 'center',
            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
            border: '1px solid #e5e7eb'
          }}>
            <Building2 style={{ width: '3rem', height: '3rem', color: '#9ca3af', margin: '0 auto 1rem' }} />
            <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827', marginBottom: '0.5rem' }}>No changes found</h3>
            <p style={{ color: '#6b7280' }}>
              {searchTerm || statusFilter !== 'all' || typeFilter !== 'all'
                ? 'Try adjusting your filters or search terms'
                : 'No department changes have been detected'}
            </p>
          </div>
        ) : (
          filteredChanges.map((change, index) => (
            <div 
              key={index} 
              style={{
                backgroundColor: 'white',
                borderRadius: '1rem',
                padding: '1.5rem',
                boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
                border: '1px solid #e5e7eb',
                transition: 'all 0.2s ease',
                cursor: 'pointer'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-1px)'
                e.currentTarget.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)'
                e.currentTarget.style.boxShadow = '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '1rem' }}>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
                    <div style={{
                      width: '2.5rem',
                      height: '2.5rem',
                      backgroundColor: '#f3f4f6',
                      borderRadius: '50%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}>
                      <Users style={{ width: '1.25rem', height: '1.25rem', color: '#6b7280' }} />
                    </div>
                    <div>
                      <h4 style={{ fontWeight: '600', color: '#111827', fontSize: '1rem', marginBottom: '0.25rem' }}>
                        {change.ministry}
                      </h4>
                      <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>
                        → {change.department_name}
                      </p>
                    </div>
                  </div>
                  
                  <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                    <span style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                      padding: '0.375rem 0.75rem',
                      borderRadius: '9999px',
                      fontSize: '0.75rem',
                      fontWeight: '600',
                      border: '1px solid',
                      ...getStatusColor(change.change_type)
                    }}>
                      {getStatusIcon(change.change_type)}
                      <span style={{ textTransform: 'capitalize' }}>{change.change_type}</span>
                    </span>
                    
                    <span style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                      padding: '0.375rem 0.75rem',
                      borderRadius: '9999px',
                      fontSize: '0.75rem',
                      fontWeight: '600',
                      border: '1px solid',
                      ...getTypeColor(change.change_type)
                    }}>
                      {getTypeIcon(change.change_type)}
                      <span style={{ textTransform: 'capitalize' }}>{change.change_type}</span>
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default DepartmentChanges
