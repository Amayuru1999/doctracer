
import { useState, useEffect } from 'react'
import { 
  getDashboardSummary, 
  getGazettes, 
  getAmendments, 
  getGazetteStructure,
  compareGazetteStructures,
  type DashboardSummary,
  type Gazette,
  type Amendment,
  type GazetteStructure,
  type GazetteComparison
} from '../services/api'
import AmendmentTracker from './AmendmentTracker'

export default function Dashboard() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null)
  const [gazettes, setGazettes] = useState<Gazette[]>([])
  const [amendments, setAmendments] = useState<Amendment[]>([])
  const [selectedGazette, setSelectedGazette] = useState<Gazette | null>(null)
  const [selectedAmendment, setSelectedAmendment] = useState<Amendment | null>(null)
  const [gazetteStructure, setGazetteStructure] = useState<GazetteStructure | null>(null)
  const [comparison, setComparison] = useState<GazetteComparison | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [viewMode, setViewMode] = useState<'structure' | 'comparison' | 'amendment-tracker'>('structure')

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      setError(null)
      const [summaryData, gazettesData, amendmentsData] = await Promise.all([
        getDashboardSummary(),
        getGazettes(),
        getAmendments()
      ])
      setSummary(summaryData)
      setGazettes(gazettesData)
      setAmendments(amendmentsData)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleGazetteSelect = async (gazetteId: string) => {
    const gazette = gazettes.find(g => g.gazette_id === gazetteId)
    if (gazette) {
      setSelectedGazette(gazette)
      setComparison(null)
      setError(null)
      try {
        const structure = await getGazetteStructure(gazetteId)
        setGazetteStructure(structure)
      } catch (err: any) {
        console.error('Failed to load gazette structure:', err)
        setError(`Failed to load gazette structure: ${err.message}`)
        setGazetteStructure(null)
      }
    }
  }

  const handleAmendmentSelect = async (amendmentId: string) => {
    const amendment = amendments.find(a => a.gazette_id === amendmentId)
    if (amendment) {
      setSelectedAmendment(amendment)
      setGazetteStructure(null)
      setComparison(null)
      
      // If we have a base gazette selected, automatically compare
      if (selectedGazette) {
        try {
          const comparisonData = await compareGazetteStructures(selectedGazette.gazette_id, amendmentId)
          setComparison(comparisonData)
          setViewMode('comparison')
        } catch (err: any) {
          console.error('Failed to load comparison:', err)
        }
      }
    }
  }

  const handleCompare = async () => {
    if (selectedGazette && selectedAmendment) {
      try {
        setLoading(true)
        const comparisonData = await compareGazetteStructures(selectedGazette.gazette_id, selectedAmendment.gazette_id)
        setComparison(comparisonData)
        setViewMode('comparison')
      } catch (err: any) {
        console.error('Failed to load comparison:', err)
        setError('Failed to load comparison data')
      } finally {
        setLoading(false)
      }
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-slate-500">Loading dashboard data...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-red-600 bg-red-50 p-4 rounded-lg">
        Error loading dashboard: {error}
      </div>
    )
  }

  const renderGovernmentStructure = (structure: GazetteStructure, title: string) => (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-slate-800 border-b pb-2">{title}</h3>
      
      {/* Ministers */}
      {structure.ministers.length > 0 && (
        <div>
          <h4 className="font-medium text-slate-700 mb-3 flex items-center gap-2">
            <span className="w-3 h-3 bg-blue-500 rounded-full"></span>
            Ministers ({structure.ministers.length})
          </h4>
          <div className="space-y-3">
            {structure.ministers.map((minister, index) => (
              <div key={index} className="bg-slate-50 rounded-lg p-4 border">
                <h5 className="font-medium text-slate-800 mb-2">{minister.name}</h5>
                
                {minister.departments.length > 0 && (
                  <div className="mb-2">
                    <span className="text-sm font-medium text-slate-600">Departments:</span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {minister.departments.map((dept, i) => (
                        <span key={i} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                          {dept}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                
                {minister.laws.length > 0 && (
                  <div>
                    <span className="text-sm font-medium text-slate-600">Laws:</span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {minister.laws.map((law, i) => (
                        <span key={i} className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
                          {law}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Standalone Departments */}
      {structure.departments.length > 0 && (
        <div>
          <h4 className="font-medium text-slate-700 mb-3 flex items-center gap-2">
            <span className="w-3 h-3 bg-green-500 rounded-full"></span>
            Departments ({structure.departments.length})
          </h4>
          <div className="flex flex-wrap gap-2">
            {structure.departments.map((dept, i) => (
              <span key={i} className="px-3 py-1 bg-green-100 text-green-800 text-sm rounded">
                {dept}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Standalone Laws */}
      {structure.laws.length > 0 && (
        <div>
          <h4 className="font-medium text-slate-700 mb-3 flex items-center gap-2">
            <span className="w-3 h-3 bg-orange-500 rounded-full"></span>
            Laws ({structure.laws.length})
          </h4>
          <div className="flex flex-wrap gap-2">
            {structure.laws.map((law, i) => (
              <span key={i} className="px-3 py-1 bg-orange-100 text-orange-800 text-sm rounded">
                {law}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Raw Entities Debug */}
      {structure.raw_entities.length > 0 && (
        <details className="mt-4">
          <summary className="text-sm font-medium text-slate-600 cursor-pointer">Debug: Raw Entities ({structure.raw_entities.length})</summary>
          <div className="mt-2 p-3 bg-gray-100 rounded text-xs">
            <pre>{JSON.stringify(structure.raw_entities, null, 2)}</pre>
          </div>
        </details>
      )}
    </div>
  )

  const renderComparison = (comparison: GazetteComparison) => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-slate-800">Government Structure Comparison</h3>
          <div className="text-sm text-slate-600 mt-1">
            <span className="font-medium">{comparison.base_gazette.president}</span> → <span className="font-medium">{comparison.amendment_gazette.president}</span>
          </div>
        </div>
        <div className="flex gap-2">
          <span className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded">
            Base: {comparison.base_gazette.id} ({comparison.base_gazette.published_date})
          </span>
          <span className="px-3 py-1 bg-green-100 text-green-800 text-sm rounded">
            Amendment: {comparison.amendment_gazette.id} ({comparison.amendment_gazette.published_date})
          </span>
        </div>
      </div>

      {/* Changes Summary */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <h4 className="font-medium text-green-800 mb-2">Added</h4>
          <div className="text-sm text-green-700 space-y-1">
            <div>Ministers: {comparison.changes.added_ministers.length}</div>
            {comparison.changes.added_ministers.length > 0 && (
              <div className="mt-2">
                {comparison.changes.added_ministers.map((minister, i) => (
                  <div key={i} className="text-xs bg-green-100 px-2 py-1 rounded mb-1">
                    {minister.name}
                  </div>
                ))}
              </div>
            )}
            <div>Departments: {comparison.changes.added_departments.length}</div>
            <div>Laws: {comparison.changes.added_laws.length}</div>
          </div>
        </div>
        
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h4 className="font-medium text-red-800 mb-2">Removed</h4>
          <div className="text-sm text-red-700 space-y-1">
            <div>Ministers: {comparison.changes.removed_ministers.length}</div>
            {comparison.changes.removed_ministers.length > 0 && (
              <div className="mt-2 max-h-32 overflow-y-auto">
                {comparison.changes.removed_ministers.map((minister, i) => (
                  <div key={i} className="text-xs bg-red-100 px-2 py-1 rounded mb-1">
                    {minister.name}
                  </div>
                ))}
              </div>
            )}
            <div>Departments: {comparison.changes.removed_departments.length}</div>
            <div>Laws: {comparison.changes.removed_laws.length}</div>
          </div>
        </div>
        
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <h4 className="font-medium text-yellow-800 mb-2">Modified</h4>
          <div className="text-sm text-yellow-700 space-y-1">
            <div>Ministers: {comparison.changes.modified_ministers.length}</div>
            {comparison.changes.modified_ministers.length > 0 && (
              <div className="mt-2">
                {comparison.changes.modified_ministers.map((minister, i) => (
                  <div key={i} className="text-xs bg-yellow-100 px-2 py-1 rounded mb-1">
                    {minister.name}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
        
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="font-medium text-blue-800 mb-2">Total Changes</h4>
          <div className="text-sm text-blue-700">
            <div>All Changes: {
              comparison.changes.added_ministers.length +
              comparison.changes.removed_ministers.length +
              comparison.changes.modified_ministers.length +
              comparison.changes.added_departments.length +
              comparison.changes.removed_departments.length +
              comparison.changes.added_laws.length +
              comparison.changes.removed_laws.length
            }</div>
          </div>
        </div>
      </div>

      {/* Detailed Changes */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <div className="mb-3">
            <h4 className="font-medium text-slate-700">Base Gazette Structure</h4>
            <div className="text-sm text-slate-600">
              <span className="font-medium">{comparison.base_gazette.president}</span> - {comparison.base_gazette.id} ({comparison.base_gazette.published_date})
            </div>
          </div>
          {renderGovernmentStructure(comparison.base_gazette.structure, `Base: ${comparison.base_gazette.id}`)}
        </div>
        
        <div>
          <div className="mb-3">
            <h4 className="font-medium text-slate-700">Amendment Gazette Structure</h4>
            <div className="text-sm text-slate-600">
              <span className="font-medium">{comparison.amendment_gazette.president}</span> - {comparison.amendment_gazette.id} ({comparison.amendment_gazette.published_date})
            </div>
          </div>
          {renderGovernmentStructure(comparison.amendment_gazette.structure, `Amendment: ${comparison.amendment_gazette.id}`)}
        </div>
      </div>
    </div>
  )

  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-800">Government Gazette Dashboard</h1>
        <p className="text-slate-600 mt-2">Track and analyze government structure changes through gazettes</p>
      </div>

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-600">Base Gazettes</p>
                <p className="text-2xl font-bold text-slate-900">{summary.counts.BaseGazette || 0}</p>
              </div>
              <div className="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <span className="text-2xl">📄</span>
              </div>
            </div>
          </div>
          
          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-600">Amendment Gazettes</p>
                <p className="text-2xl font-bold text-slate-900">{summary.counts.AmendmentGazette || 0}</p>
              </div>
              <div className="h-12 w-12 bg-green-100 rounded-lg flex items-center justify-center">
                <span className="text-2xl">📝</span>
              </div>
            </div>
          </div>
          
          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-600">Total Gazettes</p>
                <p className="text-2xl font-bold text-slate-900">
                  {(summary.counts.BaseGazette || 0) + (summary.counts.AmendmentGazette || 0)}
                </p>
              </div>
              <div className="h-12 w-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <span className="text-2xl">📊</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Gazette Selection */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Select Base Gazette</label>
        <select
              value={selectedGazette?.gazette_id || ''}
              onChange={(e) => handleGazetteSelect(e.target.value)}
          className="w-full rounded-lg border-slate-300"
        >
              <option value="">Select a base gazette...</option>
          {gazettes.map(g => (
            <option key={g.gazette_id} value={g.gazette_id}>
              {g.gazette_id} — {g.published_date}
            </option>
          ))}
        </select>
      </div>
          
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Select Amendment Gazette</label>
            <select
              value={selectedAmendment?.gazette_id || ''}
              onChange={(e) => handleAmendmentSelect(e.target.value)}
              className="w-full rounded-lg border-slate-300"
            >
              <option value="">Select an amendment gazette...</option>
              {amendments.map(a => (
                <option key={a.gazette_id} value={a.gazette_id}>
                  {a.gazette_id} — {a.published_date}
                </option>
              ))}
            </select>
          </div>
        </div>
        
        {selectedGazette && selectedAmendment && (
          <div className="mt-4 flex gap-3">
            <button
              onClick={() => setViewMode('structure')}
              className={`px-4 py-2 rounded-lg text-sm font-medium ${
                viewMode === 'structure' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              View Structure
            </button>
            <button
              onClick={handleCompare}
              className={`px-4 py-2 rounded-lg text-sm font-medium ${
                viewMode === 'comparison' 
                  ? 'bg-green-600 text-white' 
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              Compare Structures
            </button>
            <button
              onClick={() => setViewMode('amendment-tracker')}
              className={`px-4 py-2 rounded-lg text-sm font-medium ${
                viewMode === 'amendment-tracker' 
                  ? 'bg-purple-600 text-white' 
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              Enhanced Comparison
            </button>
          </div>
        )}
      </div>

      {/* Main Content */}
      {viewMode === 'structure' && selectedGazette && (
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
          {gazetteStructure ? (
            renderGovernmentStructure(gazetteStructure, `Government Structure: ${gazetteStructure.gazette_id}`)
          ) : (
            <div className="text-center py-8">
              <div className="text-slate-500 mb-4">
                {error ? (
                  <div className="text-red-600">
                    <p className="font-medium">Error loading structure</p>
                    <p className="text-sm">{error}</p>
                  </div>
                ) : (
                  <div>
                    <p className="font-medium">No government structure data found</p>
                    <p className="text-sm">This gazette may not have any ministers, departments, or laws defined in the database.</p>
                  </div>
                )}
              </div>
              <div className="text-xs text-slate-400">
                Gazette ID: {selectedGazette.gazette_id} | Published: {selectedGazette.published_date}
              </div>
            </div>
          )}
        </div>
      )}

      {viewMode === 'comparison' && comparison && (
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
          {renderComparison(comparison)}
        </div>
      )}

      {viewMode === 'amendment-tracker' && selectedGazette && selectedAmendment && (
        <AmendmentTracker 
          baseGazetteId={selectedGazette.gazette_id}
        />
      )}

      {/* Recent Gazettes */}
      {summary && summary.recent_gazettes.length > 0 && (
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
          <h2 className="text-xl font-semibold text-slate-800 mb-4">Recent Gazettes</h2>
          <div className="space-y-2">
            {summary.recent_gazettes.map((gazette, index) => (
              <div key={`${gazette.gazette_id}-${index}`} className="flex items-center justify-between py-2 px-3 bg-slate-50 rounded-lg">
                <div>
                  <span className="font-medium text-slate-800">{gazette.gazette_id}</span>
                  <span className="text-sm text-slate-600 ml-2">
                    {gazette.gazette_id.includes('1897') ? 'Base' : 'Amendment'}
                  </span>
                </div>
                <div className="text-sm text-slate-600">{gazette.published_date}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  )
}
