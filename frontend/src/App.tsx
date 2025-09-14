import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Header from './components/Header'
import Dashboard from './components/Dashboard'
import TreeVisualization from './components/TreeVisualization'
import DepartmentChanges from './components/DepartmentChanges'
import AnalyticsDashboard from './components/AnalyticsDashboard'
import NetworkGraph from './components/NetworkGraph'
import { DataProvider } from './contexts/DataContext'
import './App.css'

function App() {
  return (
    <DataProvider>
      <Router>
        <div style={{ minHeight: '100vh', backgroundColor: '#f9fafb' }}>
          <Header />
          <main style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem 1rem' }}>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/tree" element={<TreeVisualization />} />
              <Route path="/departments" element={<DepartmentChanges />} />
              <Route path="/analytics" element={<AnalyticsDashboard />} />
              <Route path="/network" element={<NetworkGraph />} />
            </Routes>
          </main>
        </div>
      </Router>
    </DataProvider>
  )
}

export default App
