import { useMemo } from "react";
import { useData } from "../contexts/DataContext";

type Node = { id: string; label: string; group: string };
type Link = { source: string; target: string };

export default function NetworkGraph() {
  const { details, selectedGazetteId } = useData();

  const { nodes, links } = useMemo(() => {
    const nMap = new Map<string, Node>();
    const l: Link[] = [];

    const addNode = (id: string, label: string, group: string) => {
      if (!nMap.has(id)) nMap.set(id, { id, label, group });
    };

    addNode(`g:${selectedGazetteId}`, `Gazette ${selectedGazetteId}`, "gazette");
    details.forEach(d => {
      const mId = `m:${d.minister}`;
      addNode(mId, d.minister, "minister");
      l.push({ source: `g:${selectedGazetteId}`, target: mId });

      d.departments.forEach(dep => {
        const id = `d:${dep}`;
        addNode(id, dep, "department");
        l.push({ source: mId, target: id });
      });
      d.laws.forEach(law => {
        const id = `l:${law}`;
        addNode(id, law, "law");
        l.push({ source: mId, target: id });
      });
      d.functions.forEach(fn => {
        const id = `f:${fn}`;
        addNode(id, fn, "function");
        l.push({ source: mId, target: id });
      });
    });

    return { nodes: Array.from(nMap.values()), links: l };
  }, [details, selectedGazetteId]);

  // Render with your current graph lib; placeholder JSON:
  return (
    <pre className="bg-gray-100 p-4 rounded overflow-auto text-sm">
      {JSON.stringify({ nodes, links }, null, 2)}
    </pre>
  );
}
