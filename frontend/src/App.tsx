import { Routes, Route, NavLink, useParams, useNavigate, useLocation } from 'react-router-dom'
import { useState, useEffect, useRef } from 'react'

// --- Component Imports ---
// Ensure these paths match your project structure
import Dashboard from './components/Dashboard'
import TreeVisualization from './components/TreeVisualization'
import DepartmentChanges from './components/DepartmentChanges'
import AnalyticsDashboard from './components/AnalyticsDashboard'
import BaseGazetteVisualization from './components/BaseGazetteVisualization'
import RadialVisualization from './components/RadialVisualization'
import GovernmentSelection from './components/GovernmentSelection'

// --- Context Imports ---
import { DataProvider } from './contexts/DataContext'
import { GovernmentProvider, useGovernment } from './contexts/GovernmentContext'

function Header() {
  const { governmentInfo } = useGovernment()
  // const { government } = useParams() // Optional: if you need url params here
  const navigate = useNavigate()
  const location = useLocation()

  // State
  const [menuOpen, setMenuOpen] = useState(false)
  const [vizOpen, setVizOpen] = useState(false)

  // Refs
  const dropdownRef = useRef<HTMLDivElement>(null)

  // 1. Close menus when route changes
  useEffect(() => {
    setMenuOpen(false)
    setVizOpen(false)
  }, [location.pathname])

  // 2. Close dropdown when clicking outside (Desktop)
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setVizOpen(false)
      }
    }

    document.addEventListener("mousedown", handleClickOutside)
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [])

  const nav = [
    { to: 'dashboard', label: 'Dashboard' },
    { to: 'tree', label: 'Ministries' },
    { to: 'departments', label: 'Departments' },
    {
      to: 'visualization', // Parent grouping identifier
      label: 'Visualization',
      children: [
        { to: 'visualization', label: 'Hierarchy View' },
        { to: 'radial', label: 'Radial View' },
      ],
    },
    // { to: 'analytics', label: 'Analytics' },
  ]

  // Helper to check if a parent section is active
  const isParentActive = (children: { to: string }[]) => {
    return children.some(c => location.pathname.endsWith(c.to) || location.pathname.includes(c.to))
  }

  // Styles
  const linkBase = "px-3 py-2 rounded-lg text-sm font-medium transition-colors duration-200 block text-center lg:text-left w-full lg:w-auto"
  const activeStyle = "bg-sky-100 text-sky-700"
  const inactiveStyle = "text-slate-600 hover:text-slate-900 hover:bg-slate-100"

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 py-3 flex flex-wrap items-center justify-between gap-y-4">
        
        {/* --- Logo & Title --- */}
        <div 
          className="flex items-center gap-3 flex-shrink-0 cursor-pointer" 
          onClick={() => navigate(`/${useParams().government || ''}/dashboard`)}
        >
          <div className="h-10 w-10 sm:h-12 sm:w-12 rounded-xl bg-gradient-to-br from-green-600 to-yellow-500 flex items-center justify-center text-white font-bold text-lg shadow-lg">
            🇱🇰
          </div>
          <div className="flex flex-col">
            <div className="text-lg font-semibold text-slate-800 leading-tight">DocTracer</div>
            <div className="text-xs text-slate-500 max-w-[150px] sm:max-w-none truncate">
              {governmentInfo
                ? `${governmentInfo.name} (${governmentInfo.period})`
                : 'Sri Lanka Government Structure'}
            </div>
          </div>
        </div>

        {/* --- Mobile Hamburger Button --- */}
        <button
          className="lg:hidden ml-auto px-3 py-2 rounded-lg text-slate-600 hover:bg-slate-100 focus:outline-none"
          onClick={() => setMenuOpen(!menuOpen)}
          aria-label="Toggle Navigation"
        >
          <span className="text-xl">{menuOpen ? '✕' : '☰'}</span>
        </button>

        {/* --- Navigation Links --- */}
        <div
          className={`${
            menuOpen ? 'flex' : 'hidden'
          } lg:flex w-full lg:w-auto flex-col lg:flex-row items-stretch lg:items-center gap-2 lg:gap-1 mt-2 lg:mt-0`}
        >
          <nav className="flex flex-col lg:flex-row gap-2 w-full lg:w-auto">
            {nav.map(n => {
              // Handle Dropdown Items
              if (n.children) {
                const isActive = isParentActive(n.children)
                return (
                  <div key={n.label} className="relative w-full lg:w-auto" ref={dropdownRef}>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        setVizOpen(!vizOpen)
                      }}
                      className={`${linkBase} flex items-center justify-center lg:justify-start gap-1 ${
                        isActive ? activeStyle : inactiveStyle
                      }`}
                    >
                      {n.label}
                      <span className={`transition-transform duration-200 ${vizOpen ? 'rotate-180' : ''}`}>▾</span>
                    </button>

                    {/* Dropdown Menu */}
                    {vizOpen && (
                      <div className={`
                        relative w-full bg-slate-50 border-t border-b border-slate-100 flex flex-col py-1
                        lg:absolute lg:left-0 lg:top-full lg:mt-1 lg:w-48 lg:bg-white lg:border lg:border-slate-200 lg:rounded-lg lg:shadow-xl lg:z-50
                      `}>
                        {n.children.map(c => (
                          <NavLink
                            key={c.to}
                            to={c.to}
                            className={({ isActive }) =>
                              `block px-4 py-2 text-sm text-center lg:text-left hover:bg-slate-100 ${
                                isActive ? 'text-sky-700 font-medium bg-sky-50 lg:bg-transparent' : 'text-slate-600'
                              }`
                            }
                            onClick={() => {
                              setMenuOpen(false)
                              setVizOpen(false)
                            }}
                          >
                            {c.label}
                          </NavLink>
                        ))}
                      </div>
                    )}
                  </div>
                )
              }

              // Handle Standard Links
              return (
                <NavLink
                  key={n.to}
                  to={n.to}
                  className={({ isActive }) => `${linkBase} ${isActive ? activeStyle : inactiveStyle}`}
                  onClick={() => setMenuOpen(false)}
                >
                  {n.label}
                </NavLink>
              )
            })}
          </nav>

          {/* --- Divider for Mobile --- */}
          <div className="h-px bg-slate-200 my-2 lg:hidden"></div>

          {/* --- Action Button --- */}
          <button
            onClick={() => {
              setMenuOpen(false)
              navigate('/')
            }}
            className="w-full lg:w-auto px-4 py-2 ml-0 lg:ml-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg text-sm font-medium hover:from-blue-700 hover:to-indigo-700 transition-all duration-200 shadow-md hover:shadow-lg whitespace-nowrap"
          >
            Change Government
          </button>
        </div>
      </div>
    </header>
  )
}

function AppWithHeader() {
  return (
    <div className="min-h-screen bg-slate-50">
      <Header />
      <main className="max-w-6xl mx-auto px-4 py-6 sm:py-8">
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