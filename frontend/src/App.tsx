
import { Routes, Route, NavLink, useParams, useNavigate } from 'react-router-dom'
import Dashboard from './components/Dashboard'
import TreeVisualization from './components/TreeVisualization'
import DepartmentChanges from './components/DepartmentChanges'
import AnalyticsDashboard from './components/AnalyticsDashboard'
import BaseGazetteVisualization from './components/BaseGazetteVisualization'
import RadialVisualization from './components/RadialVisualization'
import GovernmentSelection from './components/GovernmentSelection'
import { DataProvider } from './contexts/DataContext'
import { GovernmentProvider, useGovernment } from './contexts/GovernmentContext'

function Header() {
  const { selectedGovernment, governmentInfo } = useGovernment()
  const { government } = useParams()
  const navigate = useNavigate()
  
  const nav = [
    { to: 'dashboard', label: 'Dashboard' },
    { to: 'tree', label: 'Ministries' },
    { to: 'departments', label: 'Departments' },
    { to: 'visualization', label: 'Visualization' },
    { to: 'radial', label: 'Radial View' },
    { to: 'analytics', label: 'Analytics' },
  ]
  return (
    <header className="bg-white border-b border-slate-200">
      <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-green-600 to-yellow-500 flex items-center justify-center text-white font-bold text-lg shadow-lg">
            🇱🇰
          </div>
          <div>
            <div className="text-lg font-semibold text-slate-800">DocTracer</div>
            <div className="text-xs text-slate-500">
              {governmentInfo ? `${governmentInfo.name} (${governmentInfo.period})` : 'Sri Lanka Government Structure Tracker'}
            </div>
          </div>
        </div>
        <div className="flex items-center gap-4">
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
          <button
            onClick={() => navigate('/')}
            className="px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg text-sm font-medium hover:from-blue-600 hover:to-purple-700 transition-all duration-200 shadow-lg hover:shadow-xl"
          >
            Change Government
          </button>
        </div>
      </div>
    </header>
  )
}

function AppContent() {
  return (
    <div className="min-h-screen bg-slate-50">
      <Routes>
        <Route path="/" element={<GovernmentSelection />} />
        <Route path="/:government/dashboard" element={<Dashboard />} />
        <Route path="/:government/tree" element={<TreeVisualization />} />
        <Route path="/:government/departments" element={<DepartmentChanges />} />
        <Route path="/:government/visualization" element={<BaseGazetteVisualization />} />
        <Route path="/:government/radial" element={<RadialVisualization />} />
        <Route path="/:government/analytics" element={<AnalyticsDashboard />} />
      </Routes>
    </div>
  )
}

function AppWithHeader() {
  return (
    <div className="min-h-screen bg-slate-50">
      <Header />
      <main className="max-w-6xl mx-auto px-4 py-8">
        <Routes>
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="tree" element={<TreeVisualization />} />
          <Route path="departments" element={<DepartmentChanges />} />
          <Route path="visualization" element={<BaseGazetteVisualization />} />
          <Route path="radial" element={<RadialVisualization />} />
          <Route path="analytics" element={<AnalyticsDashboard />} />
        </Routes>
      </main>
    </div>
  )
}

export default function App() {
  return (
    <GovernmentProvider>
      <DataProvider>
        <Routes>
          <Route path="/" element={<GovernmentSelection />} />
          <Route path="/:government/*" element={<AppWithHeader />} />
        </Routes>
      </DataProvider>
    </GovernmentProvider>
  )
}
