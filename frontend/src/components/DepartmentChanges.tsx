import { useMemo } from "react";
import { useData } from "../contexts/DataContext";

export default function DepartmentChanges() {
  const { details, loading } = useData();
  const rows = useMemo(() => {
    return details.flatMap(d => d.departments.map(dep => ({ minister: d.minister, department: dep })));
  }, [details]);

  if (loading) return <p>Loading…</p>;

  return (
    <table className="min-w-full bg-white shadow rounded">
      <thead>
        <tr>
          <th className="text-left p-2">Minister</th>
          <th className="text-left p-2">Department</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((r, i) => (
          <tr key={`${r.minister}-${i}`} className="border-t">
            <td className="p-2">{r.minister}</td>
            <td className="p-2">{r.department}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
