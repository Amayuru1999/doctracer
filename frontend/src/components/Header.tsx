import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  Home, 
  GitBranch, 
  Building2, 
  BarChart3,
  Network,
  BookOpen
} from 'lucide-react'

const Header: React.FC = () => {
  const location = useLocation()

  const navigation = [
    { path: '/', label: 'Dashboard', icon: Home },
    { path: '/tree', label: 'Ministries', icon: GitBranch },
    { path: '/departments', label: 'Departments', icon: Building2 },
    { path: '/analytics', label: 'Analytics', icon: BarChart3 },
    { path: '/network', label: 'Network', icon: Network }
  ]

  return (
    <header className="header">
      <div className="header-content">
        <div className="logo">
          <div className="logo-icon">
            <BookOpen size={28} className="text-blue-600" />
          </div>
          <div className="logo-text">
            <h1>DocTracer</h1>
            <span>Government Structure Tracker</span>
          </div>
        </div>
        
        <nav className="navigation">
          {navigation.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path
            
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`nav-link ${isActive ? 'active' : ''}`}
              >
                <Icon size={18} />
                <span>{item.label}</span>
                {isActive && <div className="active-indicator" />}
              </Link>
            )
          })}
        </nav>
      </div>
    </header>
  )
}

export default Header
