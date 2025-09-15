import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchGazettes } from "../services/api";
import { Gazette } from "../types/gazette";

export default function GazetteList() {
  const [gazettes, setGazettes] = useState<Gazette[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchGazettes()
      .then(setGazettes)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>Loading gazettes...</p>;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Base Gazettes</h1>
      <ul className="space-y-2">
        {gazettes.map((g) => (
          <li key={g.gazette_id} className="p-4 bg-white rounded shadow">
            <Link to={`/gazettes/${encodeURIComponent(g.gazette_id)}`}>
              {g.gazette_id} – {g.published_date}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
