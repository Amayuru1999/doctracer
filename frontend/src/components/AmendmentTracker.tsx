import { useEffect, useState } from "react";
import { 
  getGovernmentEvolutionFromBase, 
  compareGazetteStructures,
  getGazettes,
  getAmendments,
  type GovernmentEvolutionFromBase,
  type GazetteComparison,
  type Gazette
} from "../services/api";

interface AmendmentTrackerProps {
  baseGazetteId?: string;
}

export default function AmendmentTracker({ baseGazetteId }: AmendmentTrackerProps) {
  const [evolutionData, setEvolutionData] = useState<GovernmentEvolutionFromBase | null>(null);
  const [comparisonData, setComparisonData] = useState<GazetteComparison | null>(null);
  const [gazettes, setGazettes] = useState<Gazette[]>([]);
  const [amendments, setAmendments] = useState<Gazette[]>([]);
  const [selectedBase, setSelectedBase] = useState<string>(baseGazetteId || "");
  const [selectedAmendment, setSelectedAmendment] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | undefined>();
  const [viewMode, setViewMode] = useState<'evolution' | 'comparison'>('evolution');
  const [activeTab, setActiveTab] = useState<'ministries' | 'departments' | 'laws' | 'functions'>('ministries');

  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    if (selectedBase) {
      loadEvolutionData();
    }
  }, [selectedBase]);

  useEffect(() => {
    if (selectedBase && selectedAmendment) {
      loadComparisonData();
    }
  }, [selectedBase, selectedAmendment]);


  const loadInitialData = async () => {
    try {
      setLoading(true);
      setError(undefined);
      
      // Add timeout to prevent infinite loading
      const timeoutPromise = new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Request timeout')), 10000)
      );
      
      const [gazettesData, amendmentsData] = await Promise.race([
        Promise.all([
          getGazettes(),
          getAmendments()
        ]),
        timeoutPromise
      ]) as [Gazette[], Gazette[]];
      
      setGazettes(gazettesData);
      setAmendments(amendmentsData);
    } catch (err) {
      console.error('Failed to load initial data:', err);
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const loadEvolutionData = async () => {
    try {
      setLoading(true);
      setError(undefined);
      
      // Add longer timeout for evolution data
      const timeoutPromise = new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Evolution data request timeout - backend may be slow')), 15000)
      );
      
      const data = await Promise.race([
        getGovernmentEvolutionFromBase(selectedBase),
        timeoutPromise
      ]) as GovernmentEvolutionFromBase;
      
      setEvolutionData(data);
    } catch (err) {
      console.error('Failed to load evolution data:', err);
      // If evolution data fails, suggest using Direct Comparison instead
      setError(err instanceof Error ? 
        `${err.message}. Try using "Direct Comparison" mode instead.` : 
        'Failed to load evolution data. Try using "Direct Comparison" mode instead.');
    } finally {
      setLoading(false);
    }
  };

  const loadComparisonData = async () => {
    try {
      setLoading(true);
      setError(undefined);
      
      // Add timeout for comparison data
      const timeoutPromise = new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Comparison data request timeout')), 8000)
      );
      
      const data = await Promise.race([
        compareGazetteStructures(selectedBase, selectedAmendment),
        timeoutPromise
      ]) as GazetteComparison;
      
      setComparisonData(data);
    } catch (err) {
      console.error('Failed to load comparison data:', err);
      setError(err instanceof Error ? err.message : 'Failed to load comparison data');
    } finally {
      setLoading(false);
    }
  };


  const getChangeTypeColor = (type: 'added' | 'removed' | 'modified') => {
    switch (type) {
      case 'added': return 'text-green-600 bg-green-50 border-green-200';
      case 'removed': return 'text-red-600 bg-red-50 border-red-200';
      case 'modified': return 'text-amber-600 bg-amber-50 border-amber-200';
      default: return 'text-slate-600 bg-slate-50 border-slate-200';
    }
  };

  const getChangeIcon = (type: 'added' | 'removed' | 'modified') => {
    switch (type) {
      case 'added': return '➕';
      case 'removed': return '➖';
      case 'modified': return '🔄';
      default: return '📝';
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-8 text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sky-600 mx-auto mb-4"></div>
        <div className="text-slate-500 mb-2">Loading amendment tracking data...</div>
        <div className="text-sm text-slate-400">
          {!gazettes.length && !amendments.length ? 'Fetching gazette data...' : 
           selectedBase && !evolutionData ? 'Loading evolution data...' :
           selectedBase && selectedAmendment && !comparisonData ? 'Loading comparison data...' :
           'Processing...'}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-8 text-center">
        <div className="text-red-600 mb-4">Error: {error}</div>
        <div className="flex gap-3 justify-center">
          <button
            onClick={() => {
              setError(undefined);
              loadInitialData();
            }}
            className="px-4 py-2 bg-sky-600 text-white rounded-lg hover:bg-sky-700 transition-colors"
          >
            Retry
          </button>
          {error.includes('Evolution data') && (
            <button
              onClick={() => {
                setError(undefined);
                setViewMode('comparison');
              }}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              Use Direct Comparison
            </button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Sri Lanka branding */}
      <div className="bg-gradient-to-r from-green-600 to-yellow-500 rounded-xl p-6 text-white shadow-lg">
        <div className="flex items-center gap-3 mb-2">
          <div className="h-8 w-8 rounded-lg bg-white/20 flex items-center justify-center text-lg">
            🇱🇰
          </div>
          <h1 className="text-2xl font-bold">Government Structure Amendment Tracker</h1>
        </div>
        <p className="text-green-100 text-sm">Track changes in Sri Lankan government ministries, departments, and laws across gazette publications</p>
      </div>

      {/* Controls */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
        <div className="flex items-center justify-between gap-4 mb-6">
          <h2 className="text-xl font-semibold text-slate-800 flex items-center gap-2">
            <span className="h-6 w-6 rounded bg-sky-100 flex items-center justify-center text-sky-600 text-sm">📊</span>
            Amendment Analysis
          </h2>
          <div className="flex gap-2">
            <button
              onClick={() => setViewMode('evolution')}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                viewMode === 'evolution' 
                  ? 'bg-sky-100 text-sky-700' 
                  : 'text-slate-600 hover:bg-slate-100'
              }`}
            >
              Evolution Timeline
            </button>
            <button
              onClick={() => setViewMode('comparison')}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                viewMode === 'comparison' 
                  ? 'bg-sky-100 text-sky-700' 
                  : 'text-slate-600 hover:bg-slate-100'
              }`}
            >
              Direct Comparison
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-slate-600 mb-1">Base Gazette</label>
            <select
              className="w-full rounded-lg border-slate-300"
              value={selectedBase}
              onChange={(e) => setSelectedBase(e.target.value)}
            >
              <option value="">Select base gazette...</option>
              {gazettes.map(gazette => (
                <option key={gazette.gazette_id} value={gazette.gazette_id}>
                  {gazette.gazette_id} — {gazette.published_date}
                </option>
              ))}
            </select>
          </div>

          {viewMode === 'comparison' && (
            <div>
              <label className="block text-sm text-slate-600 mb-1">Amendment Gazette</label>
              <select
                className="w-full rounded-lg border-slate-300"
                value={selectedAmendment}
                onChange={(e) => setSelectedAmendment(e.target.value)}
              >
                <option value="">Select amendment gazette...</option>
                {amendments.map(amendment => (
                  <option key={amendment.gazette_id} value={amendment.gazette_id}>
                    {amendment.gazette_id} — {amendment.published_date}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>
      </div>

      {/* Evolution Timeline View */}
      {viewMode === 'evolution' && evolutionData && (
        <div className="space-y-4">
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4">
            <h3 className="text-lg font-semibold text-slate-800 mb-4">
              Evolution Timeline: {evolutionData.base_gazette}
            </h3>
            
            <div className="space-y-4">
              {evolutionData.changes.map((change, index) => (
                <div key={index} className="border border-slate-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-medium text-slate-800">
                      Step {index + 1}: {change.from_gazette} → {change.to_gazette}
                    </h4>
                    <span className="text-sm text-slate-500">
                      {evolutionData.evolution[index + 1]?.gazette?.published_date}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {/* Added Changes */}
                    <div className="space-y-2">
                      <h5 className="text-sm font-medium text-green-700 flex items-center gap-1">
                        <span>➕</span> Added
                      </h5>
                      {change.added_ministers.length > 0 && (
                        <div className="text-xs">
                          <div className="font-medium text-slate-600">Ministries:</div>
                          {change.added_ministers.map((minister, i) => (
                            <div key={i} className="text-green-600 ml-2">• {minister.name}</div>
                          ))}
                        </div>
                      )}
                      {change.added_departments.length > 0 && (
                        <div className="text-xs">
                          <div className="font-medium text-slate-600">Departments:</div>
                          {change.added_departments.map((dept, i) => (
                            <div key={i} className="text-green-600 ml-2">• {dept}</div>
                          ))}
                        </div>
                      )}
                      {change.added_laws.length > 0 && (
                        <div className="text-xs">
                          <div className="font-medium text-slate-600">Laws:</div>
                          {change.added_laws.map((law, i) => (
                            <div key={i} className="text-green-600 ml-2">• {law}</div>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* Removed Changes */}
                    <div className="space-y-2">
                      <h5 className="text-sm font-medium text-red-700 flex items-center gap-1">
                        <span>➖</span> Removed
                      </h5>
                      {change.removed_ministers.length > 0 && (
                        <div className="text-xs">
                          <div className="font-medium text-slate-600">Ministries:</div>
                          {change.removed_ministers.map((minister, i) => (
                            <div key={i} className="text-red-600 ml-2">• {minister.name}</div>
                          ))}
                        </div>
                      )}
                      {change.removed_departments.length > 0 && (
                        <div className="text-xs">
                          <div className="font-medium text-slate-600">Departments:</div>
                          {change.removed_departments.map((dept, i) => (
                            <div key={i} className="text-red-600 ml-2">• {dept}</div>
                          ))}
                        </div>
                      )}
                      {change.removed_laws.length > 0 && (
                        <div className="text-xs">
                          <div className="font-medium text-slate-600">Laws:</div>
                          {change.removed_laws.map((law, i) => (
                            <div key={i} className="text-red-600 ml-2">• {law}</div>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* Modified Changes */}
                    <div className="space-y-2">
                      <h5 className="text-sm font-medium text-amber-700 flex items-center gap-1">
                        <span>🔄</span> Modified
                      </h5>
                      {change.modified_ministers.length > 0 && (
                        <div className="text-xs">
                          <div className="font-medium text-slate-600">Ministries:</div>
                          {change.modified_ministers.map((minister, i) => (
                            <div key={i} className="text-amber-600 ml-2">
                              • {minister.name}
                              {minister.departments_added.length > 0 && (
                                <div className="ml-2 text-green-600">
                                  +{minister.departments_added.join(', ')}
                                </div>
                              )}
                              {minister.departments_removed.length > 0 && (
                                <div className="ml-2 text-red-600">
                                  -{minister.departments_removed.join(', ')}
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Direct Comparison View */}
      {viewMode === 'comparison' && comparisonData && (
        <div className="space-y-6">
          {/* Comparison Header */}
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-200 p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="h-10 w-10 rounded-lg bg-blue-100 flex items-center justify-center text-blue-600">
                ⚖️
              </div>
              <div>
                <h3 className="text-xl font-bold text-slate-800">Government Structure Comparison</h3>
                <p className="text-slate-600 text-sm">Detailed analysis of changes between gazette publications</p>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-white rounded-lg p-4 border border-slate-200">
                <div className="flex items-center gap-2 mb-2">
                  <span className="h-3 w-3 rounded-full bg-slate-500"></span>
                  <span className="font-semibold text-slate-700">Base Gazette</span>
                </div>
                <div className="text-lg font-bold text-slate-800">{comparisonData.base_gazette.id}</div>
                <div className="text-sm text-slate-500">{comparisonData.base_gazette.published_date}</div>
              </div>
              <div className="bg-white rounded-lg p-4 border border-slate-200">
                <div className="flex items-center gap-2 mb-2">
                  <span className="h-3 w-3 rounded-full bg-blue-500"></span>
                  <span className="font-semibold text-slate-700">Amendment Gazette</span>
                </div>
                <div className="text-lg font-bold text-slate-800">{comparisonData.amendment_gazette.id}</div>
                <div className="text-sm text-slate-500">{comparisonData.amendment_gazette.published_date}</div>
              </div>
            </div>
          </div>

          {/* Changes Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Added Changes Card */}
            <div className="bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-3">
                <div className="h-8 w-8 rounded-lg bg-green-100 flex items-center justify-center text-green-600">
                  ➕
                </div>
                <span className="font-semibold text-green-800">Added</span>
              </div>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-green-700">Ministries:</span>
                  <span className="font-bold text-green-800">{comparisonData.changes.added_ministers.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-green-700">Departments:</span>
                  <span className="font-bold text-green-800">{comparisonData.changes.added_departments.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-green-700">Laws:</span>
                  <span className="font-bold text-green-800">{comparisonData.changes.added_laws.length}</span>
                </div>
              </div>
            </div>

            {/* Removed Changes Card */}
            <div className="bg-gradient-to-br from-red-50 to-rose-50 border border-red-200 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-3">
                <div className="h-8 w-8 rounded-lg bg-red-100 flex items-center justify-center text-red-600">
                  ➖
                </div>
                <span className="font-semibold text-red-800">Removed</span>
              </div>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-red-700">Ministries:</span>
                  <span className="font-bold text-red-800">{comparisonData.changes.removed_ministers.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-red-700">Departments:</span>
                  <span className="font-bold text-red-800">{comparisonData.changes.removed_departments.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-red-700">Laws:</span>
                  <span className="font-bold text-red-800">{comparisonData.changes.removed_laws.length}</span>
                </div>
              </div>
            </div>

            {/* Modified Changes Card */}
            <div className="bg-gradient-to-br from-amber-50 to-yellow-50 border border-amber-200 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-3">
                <div className="h-8 w-8 rounded-lg bg-amber-100 flex items-center justify-center text-amber-600">
                  🔄
                </div>
                <span className="font-semibold text-amber-800">Modified</span>
              </div>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-amber-700">Ministries:</span>
                  <span className="font-bold text-amber-800">{comparisonData.changes.modified_ministers.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-amber-700">Departments:</span>
                  <span className="font-bold text-amber-800">-</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-amber-700">Laws:</span>
                  <span className="font-bold text-amber-800">-</span>
                </div>
              </div>
            </div>

            {/* Total Changes Card */}
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-3">
                <div className="h-8 w-8 rounded-lg bg-blue-100 flex items-center justify-center text-blue-600">
                  📊
                </div>
                <span className="font-semibold text-blue-800">Total</span>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-800">
                  {comparisonData.changes.added_ministers.length + 
                   comparisonData.changes.added_departments.length + 
                   comparisonData.changes.added_laws.length +
                   comparisonData.changes.removed_ministers.length + 
                   comparisonData.changes.removed_departments.length + 
                   comparisonData.changes.removed_laws.length +
                   comparisonData.changes.modified_ministers.length}
                </div>
                <div className="text-sm text-blue-600">Changes</div>
              </div>
            </div>
          </div>

          {/* Detailed Changes */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
            <h4 className="text-lg font-semibold text-slate-800 mb-6 flex items-center gap-2">
              <span className="h-6 w-6 rounded bg-slate-100 flex items-center justify-center text-slate-600 text-sm">📋</span>
              Detailed Changes Analysis
            </h4>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Base Gazette Structure */}
              <div className="space-y-3">
                <h4 className="font-medium text-slate-800 flex items-center gap-2">
                  <span className="w-3 h-3 rounded-full bg-slate-500"></span>
                  Base Gazette ({comparisonData.base_gazette.published_date})
                </h4>
                <div className="text-sm space-y-2">
                  <div><strong>President:</strong> {comparisonData.base_gazette.president}</div>
                  <div><strong>Ministries:</strong> {comparisonData.base_gazette.structure.ministers.length}</div>
                  <div><strong>Departments:</strong> {comparisonData.base_gazette.structure.departments.length}</div>
                  <div><strong>Laws:</strong> {comparisonData.base_gazette.structure.laws.length}</div>
                </div>
              </div>

              {/* Amendment Gazette Structure */}
              <div className="space-y-3">
                <h4 className="font-medium text-slate-800 flex items-center gap-2">
                  <span className="w-3 h-3 rounded-full bg-blue-500"></span>
                  Amendment Gazette ({comparisonData.amendment_gazette.published_date})
                </h4>
                <div className="text-sm space-y-2">
                  <div><strong>President:</strong> {comparisonData.amendment_gazette.president}</div>
                  <div><strong>Ministries:</strong> {comparisonData.amendment_gazette.structure.ministers.length}</div>
                  <div><strong>Departments:</strong> {comparisonData.amendment_gazette.structure.departments.length}</div>
                  <div><strong>Laws:</strong> {comparisonData.amendment_gazette.structure.laws.length}</div>
                </div>
              </div>
            </div>
          </div>

          {/* Changes Summary */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4">
            <h4 className="text-lg font-semibold text-slate-800 mb-4">Changes Summary</h4>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Added */}
              <div className="space-y-3">
                <h5 className="text-sm font-medium text-green-700 flex items-center gap-1">
                  <span>➕</span> Added ({comparisonData.changes.added_ministers.length + comparisonData.changes.added_departments.length + comparisonData.changes.added_laws.length})
                </h5>
                
                {comparisonData.changes.added_ministers.length > 0 && (
                  <div>
                    <div className="text-xs font-medium text-slate-600 mb-1">Ministries:</div>
                    {comparisonData.changes.added_ministers.map((minister, i) => (
                      <div key={i} className="text-xs text-green-600 bg-green-50 border border-green-200 rounded px-2 py-1 mb-1">
                        {minister.name}
                      </div>
                    ))}
                  </div>
                )}

                {comparisonData.changes.added_departments.length > 0 && (
                  <div>
                    <div className="text-xs font-medium text-slate-600 mb-1">Departments:</div>
                    {comparisonData.changes.added_departments.map((dept, i) => (
                      <div key={i} className="text-xs text-green-600 bg-green-50 border border-green-200 rounded px-2 py-1 mb-1">
                        {dept}
                      </div>
                    ))}
                  </div>
                )}

                {comparisonData.changes.added_laws.length > 0 && (
                  <div>
                    <div className="text-xs font-medium text-slate-600 mb-1">Laws:</div>
                    {comparisonData.changes.added_laws.map((law, i) => (
                      <div key={i} className="text-xs text-green-600 bg-green-50 border border-green-200 rounded px-2 py-1 mb-1">
                        {law}
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Removed */}
              <div className="space-y-3">
                <h5 className="text-sm font-medium text-red-700 flex items-center gap-1">
                  <span>➖</span> Removed ({comparisonData.changes.removed_ministers.length + comparisonData.changes.removed_departments.length + comparisonData.changes.removed_laws.length})
                </h5>
                
                {comparisonData.changes.removed_ministers.length > 0 && (
                  <div>
                    <div className="text-xs font-medium text-slate-600 mb-1">Ministries:</div>
                    {comparisonData.changes.removed_ministers.map((minister, i) => (
                      <div key={i} className="text-xs text-red-600 bg-red-50 border border-red-200 rounded px-2 py-1 mb-1">
                        {minister.name}
                      </div>
                    ))}
                  </div>
                )}

                {comparisonData.changes.removed_departments.length > 0 && (
                  <div>
                    <div className="text-xs font-medium text-slate-600 mb-1">Departments:</div>
                    {comparisonData.changes.removed_departments.map((dept, i) => (
                      <div key={i} className="text-xs text-red-600 bg-red-50 border border-red-200 rounded px-2 py-1 mb-1">
                        {dept}
                      </div>
                    ))}
                  </div>
                )}

                {comparisonData.changes.removed_laws.length > 0 && (
                  <div>
                    <div className="text-xs font-medium text-slate-600 mb-1">Laws:</div>
                    {comparisonData.changes.removed_laws.map((law, i) => (
                      <div key={i} className="text-xs text-red-600 bg-red-50 border border-red-200 rounded px-2 py-1 mb-1">
                        {law}
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Modified */}
              <div className="space-y-3">
                <h5 className="text-sm font-medium text-amber-700 flex items-center gap-1">
                  <span>🔄</span> Modified ({comparisonData.changes.modified_ministers.length})
                </h5>
                
                {comparisonData.changes.modified_ministers.length > 0 && (
                  <div>
                    <div className="text-xs font-medium text-slate-600 mb-1">Ministries:</div>
                    {comparisonData.changes.modified_ministers.map((minister, i) => (
                      <div key={i} className="text-xs text-amber-600 bg-amber-50 border border-amber-200 rounded px-2 py-1 mb-1">
                        <div className="font-medium">{minister.name}</div>
                        {minister.changes.map((change: any, j: number) => (
                          <div key={j} className="ml-2 text-xs">
                            {change.type === 'departments' && (
                              <>
                                {change.added.length > 0 && (
                                  <div className="text-green-600">+{change.added.join(', ')}</div>
                                )}
                                {change.removed.length > 0 && (
                                  <div className="text-red-600">-{change.removed.join(', ')}</div>
                                )}
                              </>
                            )}
                          </div>
                        ))}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Tabbed Structure Details */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
            <h4 className="text-lg font-semibold text-slate-800 mb-6 flex items-center gap-2">
              <span className="h-6 w-6 rounded bg-slate-100 flex items-center justify-center text-slate-600 text-sm">🏛️</span>
              Government Structure Details
            </h4>

            {/* Tab Navigation */}
            <div className="flex space-x-1 mb-6 bg-slate-100 p-1 rounded-lg">
              <button
                onClick={() => setActiveTab('ministries')}
                className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                  activeTab === 'ministries'
                    ? 'bg-white text-slate-900 shadow-sm'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <span className="flex items-center justify-center gap-2">
                  <span>👥</span>
                  Ministries ({comparisonData.base_gazette.structure.ministers.length + comparisonData.amendment_gazette.structure.ministers.length})
                </span>
              </button>
              <button
                onClick={() => setActiveTab('departments')}
                className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                  activeTab === 'departments'
                    ? 'bg-white text-slate-900 shadow-sm'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <span className="flex items-center justify-center gap-2">
                  <span>🏢</span>
                  Departments ({comparisonData.base_gazette.structure.departments.length + comparisonData.amendment_gazette.structure.departments.length})
                </span>
              </button>
              <button
                onClick={() => setActiveTab('functions')}
                className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                  activeTab === 'functions'
                    ? 'bg-white text-slate-900 shadow-sm'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <span className="flex items-center justify-center gap-2">
                  <span>⚙️</span>
                  Functions ({(comparisonData.base_gazette.structure.functions?.length || 0) + (comparisonData.amendment_gazette.structure.functions?.length || 0)})
                </span>
              </button>
              <button
                onClick={() => setActiveTab('laws')}
                className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                  activeTab === 'laws'
                    ? 'bg-white text-slate-900 shadow-sm'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <span className="flex items-center justify-center gap-2">
                  <span>📜</span>
                  Laws ({comparisonData.base_gazette.structure.laws.length + comparisonData.amendment_gazette.structure.laws.length})
                </span>
              </button>
            </div>

             {/* Tab Content */}
             <div className="space-y-6">
               {/* Ministries Tab */}
               {activeTab === 'ministries' && (
                 <div className="space-y-6">
                   {/* Added Ministers */}
                   {comparisonData.changes.added_ministers.length > 0 && (
                     <div>
                       <h5 className="text-md font-semibold text-green-700 mb-4 flex items-center gap-2">
                         <span className="w-3 h-3 rounded-full bg-green-500"></span>
                         Added Ministers ({comparisonData.changes.added_ministers.length})
                       </h5>
                       <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                         {comparisonData.changes.added_ministers.map((minister, index) => (
                           <div key={index} className="bg-green-50 border border-green-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                             <div className="flex items-start gap-3">
                               <div className="h-10 w-10 rounded-lg bg-green-100 flex items-center justify-center text-green-600 text-lg">
                                 ➕
                               </div>
                               <div className="flex-1 min-w-0">
                                 <h6 className="font-medium text-slate-800 text-sm leading-tight">
                                   {minister.name}
                                 </h6>
                                 {minister.functions && minister.functions.length > 0 && (
                                   <div className="mt-2">
                                     <div className="text-xs font-medium text-slate-600 mb-1">Functions:</div>
                                     <div className="space-y-1">
                                       {minister.functions.slice(0, 2).map((func, i) => (
                                         <div key={i} className="text-xs text-slate-500 bg-white rounded px-2 py-1 border">
                                           {func}
                                         </div>
                                       ))}
                                       {minister.functions.length > 2 && (
                                         <div className="text-xs text-slate-400">
                                           +{minister.functions.length - 2} more
                                         </div>
                                       )}
                                     </div>
                                   </div>
                                 )}
                                 {minister.departments && minister.departments.length > 0 && (
                                   <div className="mt-2">
                                     <div className="text-xs font-medium text-slate-600 mb-1">Departments:</div>
                                     <div className="space-y-1">
                                       {minister.departments.slice(0, 2).map((dept, i) => (
                                         <div key={i} className="text-xs text-slate-500 bg-white rounded px-2 py-1 border">
                                           {dept}
                                         </div>
                                       ))}
                                       {minister.departments.length > 2 && (
                                         <div className="text-xs text-slate-400">
                                           +{minister.departments.length - 2} more
                                         </div>
                                       )}
                                     </div>
                                   </div>
                                 )}
                               </div>
                             </div>
                           </div>
                         ))}
                       </div>
                     </div>
                   )}

                   {/* Removed Ministers */}
                   {comparisonData.changes.removed_ministers.length > 0 && (
                     <div>
                       <h5 className="text-md font-semibold text-red-700 mb-4 flex items-center gap-2">
                         <span className="w-3 h-3 rounded-full bg-red-500"></span>
                         Removed Ministers ({comparisonData.changes.removed_ministers.length})
                       </h5>
                       <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                         {comparisonData.changes.removed_ministers.map((minister, index) => (
                           <div key={index} className="bg-red-50 border border-red-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                             <div className="flex items-start gap-3">
                               <div className="h-10 w-10 rounded-lg bg-red-100 flex items-center justify-center text-red-600 text-lg">
                                 ➖
                               </div>
                               <div className="flex-1 min-w-0">
                                 <h6 className="font-medium text-slate-800 text-sm leading-tight">
                                   {minister.name}
                                 </h6>
                                 {minister.functions && minister.functions.length > 0 && (
                                   <div className="mt-2">
                                     <div className="text-xs font-medium text-slate-600 mb-1">Functions:</div>
                                     <div className="space-y-1">
                                       {minister.functions.slice(0, 2).map((func, i) => (
                                         <div key={i} className="text-xs text-slate-500 bg-white rounded px-2 py-1 border">
                                           {func}
                                         </div>
                                       ))}
                                       {minister.functions.length > 2 && (
                                         <div className="text-xs text-slate-400">
                                           +{minister.functions.length - 2} more
                                         </div>
                                       )}
                                     </div>
                                   </div>
                                 )}
                                 {minister.departments && minister.departments.length > 0 && (
                                   <div className="mt-2">
                                     <div className="text-xs font-medium text-slate-600 mb-1">Departments:</div>
                                     <div className="space-y-1">
                                       {minister.departments.slice(0, 2).map((dept, i) => (
                                         <div key={i} className="text-xs text-slate-500 bg-white rounded px-2 py-1 border">
                                           {dept}
                                         </div>
                                       ))}
                                       {minister.departments.length > 2 && (
                                         <div className="text-xs text-slate-400">
                                           +{minister.departments.length - 2} more
                                         </div>
                                       )}
                                     </div>
                                   </div>
                                 )}
                               </div>
                             </div>
                           </div>
                         ))}
                       </div>
                     </div>
                   )}

                   {/* Modified Ministers */}
                   {comparisonData.changes.modified_ministers.length > 0 && (
                     <div>
                       <h5 className="text-md font-semibold text-amber-700 mb-4 flex items-center gap-2">
                         <span className="w-3 h-3 rounded-full bg-amber-500"></span>
                         Modified Ministers ({comparisonData.changes.modified_ministers.length})
                       </h5>
                       <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                         {comparisonData.changes.modified_ministers.map((minister, index) => (
                           <div key={index} className="bg-amber-50 border border-amber-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                             <div className="flex items-start gap-3">
                               <div className="h-10 w-10 rounded-lg bg-amber-100 flex items-center justify-center text-amber-600 text-lg">
                                 🔄
                               </div>
                               <div className="flex-1 min-w-0">
                                 <h6 className="font-medium text-slate-800 text-sm leading-tight">
                                   {minister.name}
                                 </h6>
                                 {minister.changes && minister.changes.length > 0 && (
                                   <div className="mt-2">
                                     {minister.changes.map((change: any, changeIndex: number) => (
                                       <div key={changeIndex} className="mb-2">
                                         {change.type === 'departments' && (
                                           <div>
                                             <div className="text-xs font-medium text-slate-600 mb-1">Department Changes:</div>
                                             {change.added && change.added.length > 0 && (
                                               <div className="space-y-1">
                                                 {change.added.map((dept: string, i: number) => (
                                                   <div key={i} className="text-xs text-green-600 bg-green-50 rounded px-2 py-1 border border-green-200">
                                                     +{dept}
                                                   </div>
                                                 ))}
                                               </div>
                                             )}
                                             {change.removed && change.removed.length > 0 && (
                                               <div className="space-y-1">
                                                 {change.removed.map((dept: string, i: number) => (
                                                   <div key={i} className="text-xs text-red-600 bg-red-50 rounded px-2 py-1 border border-red-200">
                                                     -{dept}
                                                   </div>
                                                 ))}
                                               </div>
                                             )}
                                           </div>
                                         )}
                                       </div>
                                     ))}
                                   </div>
                                 )}
                               </div>
                             </div>
                           </div>
                         ))}
                       </div>
                     </div>
                   )}

                   {/* No Changes Message */}
                   {comparisonData.changes.added_ministers.length === 0 && 
                    comparisonData.changes.removed_ministers.length === 0 && 
                    comparisonData.changes.modified_ministers.length === 0 && (
                     <div className="text-center py-8 text-slate-500">
                       <div className="text-lg mb-2">📋</div>
                       <div>No ministry changes found between these gazettes</div>
                     </div>
                   )}
                 </div>
               )}

               {/* Departments Tab */}
               {activeTab === 'departments' && (
                 <div className="space-y-6">
                   {/* Added Departments */}
                   {comparisonData.changes.added_departments.length > 0 && (
                     <div>
                       <h5 className="text-md font-semibold text-green-700 mb-4 flex items-center gap-2">
                         <span className="w-3 h-3 rounded-full bg-green-500"></span>
                         Added Departments ({comparisonData.changes.added_departments.length})
                       </h5>
                       <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                         {comparisonData.changes.added_departments.map((department, index) => (
                           <div key={index} className="bg-green-50 border border-green-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                             <div className="flex items-start gap-3">
                               <div className="h-10 w-10 rounded-lg bg-green-100 flex items-center justify-center text-green-600 text-lg">
                                 ➕
                               </div>
                               <div className="flex-1 min-w-0">
                                 <h6 className="font-medium text-slate-800 text-sm leading-tight">
                                   {department}
                                 </h6>
                               </div>
                             </div>
                           </div>
                         ))}
                       </div>
                     </div>
                   )}

                   {/* Removed Departments */}
                   {comparisonData.changes.removed_departments.length > 0 && (
                     <div>
                       <h5 className="text-md font-semibold text-red-700 mb-4 flex items-center gap-2">
                         <span className="w-3 h-3 rounded-full bg-red-500"></span>
                         Removed Departments ({comparisonData.changes.removed_departments.length})
                       </h5>
                       <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                         {comparisonData.changes.removed_departments.map((department, index) => (
                           <div key={index} className="bg-red-50 border border-red-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                             <div className="flex items-start gap-3">
                               <div className="h-10 w-10 rounded-lg bg-red-100 flex items-center justify-center text-red-600 text-lg">
                                 ➖
                               </div>
                               <div className="flex-1 min-w-0">
                                 <h6 className="font-medium text-slate-800 text-sm leading-tight">
                                   {department}
                                 </h6>
                               </div>
                             </div>
                           </div>
                         ))}
                       </div>
                     </div>
                   )}

                   {/* No Changes Message */}
                   {comparisonData.changes.added_departments.length === 0 && 
                    comparisonData.changes.removed_departments.length === 0 && (
                     <div className="text-center py-8 text-slate-500">
                       <div className="text-lg mb-2">🏢</div>
                       <div>No department changes found between these gazettes</div>
                     </div>
                   )}
                 </div>
               )}

               {/* Laws Tab */}
               {activeTab === 'laws' && (
                 <div className="space-y-6">
                   {/* Added Laws */}
                   {comparisonData.changes.added_laws.length > 0 && (
                     <div>
                       <h5 className="text-md font-semibold text-green-700 mb-4 flex items-center gap-2">
                         <span className="w-3 h-3 rounded-full bg-green-500"></span>
                         Added Laws ({comparisonData.changes.added_laws.length})
                       </h5>
                       <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                         {comparisonData.changes.added_laws.map((law, index) => (
                           <div key={index} className="bg-green-50 border border-green-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                             <div className="flex items-start gap-3">
                               <div className="h-10 w-10 rounded-lg bg-green-100 flex items-center justify-center text-green-600 text-lg">
                                 ➕
                               </div>
                               <div className="flex-1 min-w-0">
                                 <h6 className="font-medium text-slate-800 text-sm leading-tight">
                                   {law}
                                 </h6>
                               </div>
                             </div>
                           </div>
                         ))}
                       </div>
                     </div>
                   )}

                   {/* Removed Laws */}
                   {comparisonData.changes.removed_laws.length > 0 && (
                     <div>
                       <h5 className="text-md font-semibold text-red-700 mb-4 flex items-center gap-2">
                         <span className="w-3 h-3 rounded-full bg-red-500"></span>
                         Removed Laws ({comparisonData.changes.removed_laws.length})
                       </h5>
                       <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                         {comparisonData.changes.removed_laws.map((law, index) => (
                           <div key={index} className="bg-red-50 border border-red-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                             <div className="flex items-start gap-3">
                               <div className="h-10 w-10 rounded-lg bg-red-100 flex items-center justify-center text-red-600 text-lg">
                                 ➖
                               </div>
                               <div className="flex-1 min-w-0">
                                 <h6 className="font-medium text-slate-800 text-sm leading-tight">
                                   {law}
                                 </h6>
                               </div>
                             </div>
                           </div>
                         ))}
                       </div>
                     </div>
                   )}

                   {/* No Changes Message */}
                   {comparisonData.changes.added_laws.length === 0 && 
                    comparisonData.changes.removed_laws.length === 0 && (
                     <div className="text-center py-8 text-slate-500">
                       <div className="text-lg mb-2">📜</div>
                       <div>No law changes found between these gazettes</div>
                     </div>
                   )}
                 </div>
               )}

               {/* Functions Tab */}
               {activeTab === 'functions' && (
                 <div className="space-y-6">
                   {/* Added Functions */}
                   {(comparisonData.changes.added_functions?.length || 0) > 0 && (
                     <div>
                       <h5 className="text-md font-semibold text-green-700 mb-4 flex items-center gap-2">
                         <span className="w-3 h-3 rounded-full bg-green-500"></span>
                         Added Functions ({comparisonData.changes.added_functions?.length || 0})
                       </h5>
                       <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                         {(comparisonData.changes.added_functions || []).map((func, index) => (
                           <div key={index} className="bg-green-50 border border-green-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                             <div className="flex items-start gap-3">
                               <div className="h-10 w-10 rounded-lg bg-green-100 flex items-center justify-center text-green-600 text-lg">
                                 ➕
                               </div>
                               <div className="flex-1 min-w-0">
                                 <h6 className="font-medium text-slate-800 text-sm leading-tight">
                                   {func}
                                 </h6>
                               </div>
                             </div>
                           </div>
                         ))}
                       </div>
                     </div>
                   )}

                   {/* Removed Functions */}
                   {(comparisonData.changes.removed_functions?.length || 0) > 0 && (
                     <div>
                       <h5 className="text-md font-semibold text-red-700 mb-4 flex items-center gap-2">
                         <span className="w-3 h-3 rounded-full bg-red-500"></span>
                         Removed Functions ({comparisonData.changes.removed_functions?.length || 0})
                       </h5>
                       <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                         {(comparisonData.changes.removed_functions || []).map((func, index) => (
                           <div key={index} className="bg-red-50 border border-red-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                             <div className="flex items-start gap-3">
                               <div className="h-10 w-10 rounded-lg bg-red-100 flex items-center justify-center text-red-600 text-lg">
                                 ➖
                               </div>
                               <div className="flex-1 min-w-0">
                                 <h6 className="font-medium text-slate-800 text-sm leading-tight">
                                   {func}
                                 </h6>
                               </div>
                             </div>
                           </div>
                         ))}
                       </div>
                     </div>
                   )}

                   {/* No Changes Message */}
                   {(!comparisonData.changes.added_functions || comparisonData.changes.added_functions.length === 0) && 
                    (!comparisonData.changes.removed_functions || comparisonData.changes.removed_functions.length === 0) && (
                     <div className="text-center py-8 text-slate-500">
                       <div className="text-lg mb-2">⚙️</div>
                       <div>No function changes found between these gazettes</div>
                     </div>
                   )}
                 </div>
               )}
            </div>
          </div>
        </div>
      )}


      {/* No Data State */}
      {!evolutionData && !comparisonData && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-8 text-center">
          <div className="text-slate-500">
            {viewMode === 'evolution' 
              ? 'Select a base gazette to view its evolution timeline'
              : 'Select base and amendment gazettes to compare their structures'
            }
          </div>
        </div>
      )}
    </div>
  );
}
