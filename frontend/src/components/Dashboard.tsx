import { useData } from "../contexts/DataContext";

export default function Dashboard() {
  const { gazettes, selectedGazetteId, setSelectedGazetteId, loading, error } = useData();

  if (loading) return <p>Loading…</p>;
  if (error) return <p className="text-red-600">{error}</p>;

  return (
    <section>
      <h1 className="text-2xl font-bold mb-4">Base Gazettes</h1>
      <select
        className="border rounded px-3 py-2"
        value={selectedGazetteId ?? ""}
        onChange={(e) => setSelectedGazetteId(e.target.value)}
      >
        <option value="" disabled>Select a gazette</option>
        {gazettes.map(g => (
          <option key={g.gazette_id} value={g.gazette_id}>
            {g.gazette_id} — {g.published_date}
          </option>
        ))}
      </select>
    </section>
  );
}
