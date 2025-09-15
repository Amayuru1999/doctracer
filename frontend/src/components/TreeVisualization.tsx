import { useMemo } from "react";
import { useData } from "../contexts/DataContext";

export default function TreeVisualization() {
  const { details, selectedGazetteId, loading } = useData();

  const tree = useMemo(() => {
    // shape: { name: 'Gazette', children: [{name: minister, children:[...]}] }
    const children = details.map(d => ({
      name: d.minister,
      children: [
        ...d.departments.map(name => ({ name: `Dept: ${name}` })),
        ...d.laws.map(name => ({ name: `Law: ${name}` })),
        ...d.functions.map(name => ({ name: `Func: ${name}` })),
      ],
    }));
    return { name: `Gazette ${selectedGazetteId ?? ""}`, children };
  }, [details, selectedGazetteId]);

  if (loading) return <p>Loading…</p>;
  if (!details.length) return <p>No data.</p>;

  // render however your current tree lib expects; below is placeholder
  return (
    <pre className="bg-gray-100 p-4 rounded overflow-auto text-sm">
      {JSON.stringify(tree, null, 2)}
    </pre>
  );
}
