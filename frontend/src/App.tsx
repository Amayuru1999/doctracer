
import { Routes, Route, NavLink } from 'react-router-dom'
import Dashboard from './components/Dashboard'
import TreeVisualization from './components/TreeVisualization'
import DepartmentChanges from './components/DepartmentChanges'
import AnalyticsDashboard from './components/AnalyticsDashboard'
import NetworkGraph from './components/NetworkGraph'
import { DataProvider } from './contexts/DataContext'

function Header() {
  const nav = [
    { to: '/', label: 'Dashboard' },
    { to: '/tree', label: 'Ministries' },
    { to: '/departments', label: 'Departments' },
    { to: '/analytics', label: 'Analytics' },
    { to: '/network', label: 'Network' },
  ]
  return (
    <header className="bg-white border-b border-slate-200">
      <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-sky-100 flex items-center justify-center text-sky-700 font-bold">📖</div>
          <div>
            <div className="text-lg font-semibold text-slate-800">DocTracer</div>
            <div className="text-xs text-slate-500">Government Structure Tracker</div>
          </div>
        </div>
        <nav className="flex gap-2">
          {nav.map(n => (
            <NavLink
              key={n.to}
              to={n.to}
              className={({isActive}) => [
                "px-3 py-2 rounded-lg text-sm",
                isActive ? "bg-sky-100 text-sky-700 font-medium" : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
              ].join(' ')}
            >
              {n.label}
            </NavLink>
          ))}
        </nav>
      </div>
    </header>
  )
}

export default function App() {
  return (
    <DataProvider>
      <div className="min-h-screen bg-slate-50">
        <Header />
        <main className="max-w-6xl mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/tree" element={<TreeVisualization />} />
            <Route path="/departments" element={<DepartmentChanges />} />
            <Route path="/analytics" element={<AnalyticsDashboard />} />
            <Route path="/network" element={<NetworkGraph />} />
          </Routes>
        </main>
      </div>
    </DataProvider>
  )
}
