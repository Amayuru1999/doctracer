
import { useData } from '../contexts/DataContext'

export default function Dashboard() {
  const { gazettes, selectedGazetteId, setSelectedGazetteId, loading, error } = useData()

  return (
    <section className="space-y-4">
      <h1 className="text-3xl font-bold text-slate-800">Base Gazettes</h1>
      {error && <div className="text-red-600 text-sm">{error}</div>}

      <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm max-w-xl">
        <label className="block text-sm font-medium text-slate-700 mb-1">Select a gazette</label>
        <select
          value={selectedGazetteId ?? ''}
          onChange={(e) => setSelectedGazetteId(e.target.value)}
          disabled={loading}
          className="w-full rounded-lg border-slate-300"
        >
          <option value="" disabled>Select a gazette</option>
          {gazettes.map(g => (
            <option key={g.gazette_id} value={g.gazette_id}>
              {g.gazette_id} — {g.published_date}
            </option>
          ))}
        </select>
      </div>
    </section>
  )
}
