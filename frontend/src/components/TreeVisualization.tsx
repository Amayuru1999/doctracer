import { useEffect, useMemo, useState } from "react";
import { useData } from "../contexts/DataContext";
import {
  ChevronRight,
  ChevronDown,
  Landmark,
  Building2,
  Scale,
  ListChecks,
  Filter,
  RefreshCw,
  Search,
} from "lucide-react";

type DetailRow = {
  minister?: string | null;
  departments?: (string | null | undefined)[];
  laws?: (string | null | undefined)[];
  functions?: (string | null | undefined)[];
};

type TreeNode = {
  id: string;
  label: string;
  icon?: JSX.Element;
  children?: TreeNode[];
};

const uniq = (arr: (string | null | undefined)[]) =>
  Array.from(new Set(arr.filter((x): x is string => !!x && x.trim().length > 0)));

export default function TreeVisualization() {
  const { details, selectedGazetteId, loading, error } = useData();
  const [q, setQ] = useState("");
  const qnorm = q.trim().toLowerCase();

  const tree: TreeNode | null = useMemo(() => {
    // Safety: coerce the incoming data to a predictable shape
    const rows: DetailRow[] = Array.isArray(details) ? details : [];

    const children: TreeNode[] = rows.map((d, idx) => {
      const minister = (d?.minister ?? `Unknown minister #${idx}`).trim();
      const deptList = uniq(d?.departments ?? []);
      const lawList = uniq(d?.laws ?? []);
      const funcList = uniq(d?.functions ?? []);

      const deptNodes: TreeNode[] = deptList.map((name, i) => ({
        id: `dept:${minister}:${name}:${i}`, // keep unique even if names repeat
        label: name,
        icon: <Building2 className="h-4 w-4 text-indigo-500" />,
      }));

      const lawNodes: TreeNode[] = lawList.map((name, i) => ({
        id: `law:${minister}:${name}:${i}`,
        label: name,
        icon: <Scale className="h-4 w-4 text-emerald-600" />,
      }));

      const funcNodes: TreeNode[] = funcList.map((name, i) => ({
        id: `func:${minister}:${name}:${i}`,
        label: name,
        icon: <ListChecks className="h-4 w-4 text-amber-600" />,
      }));

      const groups: TreeNode[] = [
        { id: `g:dept:${minister}`, label: `Departments (${deptNodes.length})`, children: deptNodes },
        { id: `g:law:${minister}`, label: `Laws (${lawNodes.length})`, children: lawNodes },
        { id: `g:func:${minister}`, label: `Functions (${funcNodes.length})`, children: funcNodes },
      ];

      return {
        id: `min:${minister}`,
        label: minister,
        icon: <Landmark className="h-4 w-4 text-sky-600" />,
        children: groups,
      };
    });

    // If there are no ministers at all, return null so we can show an empty state.
    if (!children.length) return null;

    return {
      id: `gaz:${selectedGazetteId ?? "unknown"}`,
      label: `Gazette ${selectedGazetteId ?? ""}`,
      icon: <Landmark className="h-5 w-5 text-sky-700" />,
      children,
    };
  }, [details, selectedGazetteId]);

  const [open, setOpen] = useState<Set<string>>(new Set());
  useEffect(() => {
    if (!tree) return;
    const s = new Set<string>();
    s.add(tree.id);
    tree.children?.forEach((c) => s.add(c.id));
    setOpen(s);
  }, [tree?.id]); // re-open when gazette changes

  const toggle = (id: string) => {
    setOpen((prev) => {
      const n = new Set(prev);
      n.has(id) ? n.delete(id) : n.add(id);
      return n;
    });
  };

  const filterTree = (node: TreeNode): TreeNode | null => {
    if (!qnorm) return node;
    const selfMatch = node.label.toLowerCase().includes(qnorm);
    const kids = node.children?.map(filterTree).filter(Boolean) as TreeNode[] | undefined;
    if (selfMatch || (kids && kids.length)) return { ...node, children: kids };
    return null;
  };

  const filtered = tree ? filterTree(tree) : null;

  const counts = useMemo(() => {
    const rows: DetailRow[] = Array.isArray(details) ? details : [];
    return {
      ministers: rows.length,
      departments: rows.reduce((a, b) => a + uniq(b?.departments ?? []).length, 0),
      laws: rows.reduce((a, b) => a + uniq(b?.laws ?? []).length, 0),
      functions: rows.reduce((a, b) => a + uniq(b?.functions ?? []).length, 0),
    };
  }, [details]);

  if (loading) return <p className="text-slate-500">Loading…</p>;
  if (error) return <p className="text-red-600">{error}</p>;
  if (!tree) return <p className="text-slate-500">No data.</p>;

  const NodeRow = ({ node, depth = 0 }: { node: TreeNode; depth?: number }) => {
    const hasChildren = !!node.children?.length;
    const isOpen = open.has(node.id);
    return (
      <div className="select-text">
        <div
          className={`flex items-start gap-2 py-2 px-2 rounded hover:bg-slate-50 ${
            depth === 0 ? "font-semibold text-slate-800" : "text-slate-700"
          }`}
          style={{ paddingLeft: depth * 16 + 8 }}
        >
          {hasChildren ? (
            <button
              onClick={() => toggle(node.id)}
              className="mt-0.5 rounded hover:bg-slate-100 p-1"
              aria-label={isOpen ? "Collapse" : "Expand"}
            >
              {isOpen ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
            </button>
          ) : (
            <span className="h-4 w-4 ml-1" />
          )}
          {node.icon}
          <span className="leading-5">{node.label}</span>
        </div>
        {hasChildren && isOpen && (
          <div className="border-l border-slate-200 ml-4">
            {node.children!.map((c, i) => (
              <NodeRow key={c.id || `${node.id}-${i}`} node={c} depth={depth + 1} />
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <section className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Government Structure</h1>
          <p className="text-slate-500">Gazette {selectedGazetteId}</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="h-4 w-4 text-slate-400 absolute left-2 top-2.5" />
            <input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Search ministers, departments, laws, functions…"
              className="pl-8 pr-3 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-sky-300 w-80"
            />
          </div>
          <button
            onClick={() => {
              setQ("");
              if (!tree) return;
              const s = new Set<string>();
              s.add(tree.id);
              tree.children?.forEach((c) => s.add(c.id));
              setOpen(s);
            }}
            className="inline-flex items-center gap-2 px-3 py-2 rounded-lg border border-slate-300 hover:bg-slate-50"
            title="Reset"
          >
            <RefreshCw className="h-4 w-4" />
            Reset
          </button>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="bg-white rounded-xl shadow-sm p-4 border border-slate-200">
          <div className="text-slate-500 text-sm">Ministers</div>
          <div className="text-2xl font-semibold">{counts.ministers}</div>
        </div>
        <div className="bg-white rounded-xl shadow-sm p-4 border border-slate-200">
          <div className="text-slate-500 text-sm">Departments</div>
          <div className="text-2xl font-semibold">{counts.departments}</div>
        </div>
        <div className="bg-white rounded-xl shadow-sm p-4 border border-slate-200">
          <div className="text-slate-500 text-sm">Laws</div>
          <div className="text-2xl font-semibold">{counts.laws}</div>
        </div>
        <div className="bg-white rounded-xl shadow-sm p-4 border border-slate-200">
          <div className="text-slate-500 text-sm">Functions</div>
          <div className="text-2xl font-semibold">{counts.functions}</div>
        </div>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="px-4 py-3 border-b border-slate-200 flex items-center gap-2">
          <Filter className="h-4 w-4 text-slate-500" />
          <div className="text-slate-700 text-sm">
            Expand a minister to view departments, laws, and functions.
          </div>
        </div>
        <div className="p-2">
          {filtered ? <NodeRow node={filtered} /> : <p className="p-4 text-slate-500">No matches.</p>}
        </div>
      </div>
    </section>
  );
}