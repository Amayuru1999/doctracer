import React, { useState, useEffect } from 'react';
import { useData } from '../contexts/DataContext';
import { 
  Users, 
  Building2, 
  MapPin, 
  Activity,
  Target
} from 'lucide-react';

interface AnalyticsData {
  ministryStats: {
    totalMinistries: number;
    totalDepartments: number;
    totalEmployees: number;
    activeChanges: number;
  };
  changeTimeline: Array<{
    date: string;
    added: number;
    removed: number;
    modified: number;
  }>;
  ministrySizes: Array<{
    name: string;
    departmentCount: number;
    employeeCount: number;
  }>;
  budgetDistribution: Array<{
    ministry: string;
    budget: number;
    percentage: number;
  }>;
  regionalCoverage: Array<{
    region: string;
    departmentCount: number;
    population: number;
  }>;
  performanceMetrics: Array<{
    department: string;
    kpi: string;
    value: number;
    target: number;
  }>;
}

const AnalyticsDashboard: React.FC = () => {
  const { summaryData, loading, error } = useData();
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [selectedTimeframe, setSelectedTimeframe] = useState<'7d' | '30d' | '90d'>('30d');

  // Mock analytics data - replace with actual Neo4j queries
  useEffect(() => {
    if (summaryData) {
      // Simulate fetching analytics data from Neo4j
      const mockAnalytics: AnalyticsData = {
        ministryStats: {
          totalMinistries: 25,
          totalDepartments: 195,
          totalEmployees: 15420,
          activeChanges: 12
        },
        changeTimeline: [
          { date: '2024-01-01', added: 5, removed: 2, modified: 3 },
          { date: '2024-01-02', added: 3, removed: 1, modified: 4 },
          { date: '2024-01-03', added: 7, removed: 0, modified: 2 },
          { date: '2024-01-04', added: 2, removed: 3, modified: 1 },
          { date: '2024-01-05', added: 4, removed: 1, modified: 5 },
          { date: '2024-01-06', added: 6, removed: 2, modified: 3 },
          { date: '2024-01-07', added: 1, removed: 0, modified: 2 }
        ],
        ministrySizes: [
          { name: 'Ministry of Finance', departmentCount: 18, employeeCount: 1250 },
          { name: 'Ministry of Education', departmentCount: 15, employeeCount: 2100 },
          { name: 'Ministry of Health', departmentCount: 22, employeeCount: 1850 },
          { name: 'Ministry of Defense', departmentCount: 12, employeeCount: 950 },
          { name: 'Ministry of Transport', departmentCount: 14, employeeCount: 1100 }
        ],
        budgetDistribution: [
          { ministry: 'Ministry of Finance', budget: 2500000000, percentage: 25 },
          { ministry: 'Ministry of Education', budget: 1800000000, percentage: 18 },
          { ministry: 'Ministry of Health', budget: 2200000000, percentage: 22 },
          { ministry: 'Ministry of Defense', budget: 1500000000, percentage: 15 },
          { ministry: 'Ministry of Transport', budget: 1200000000, percentage: 12 }
        ],
        regionalCoverage: [
          { region: 'Western Province', departmentCount: 45, population: 5800000 },
          { region: 'Central Province', departmentCount: 32, population: 2500000 },
          { region: 'Southern Province', departmentCount: 28, population: 2800000 },
          { region: 'Northern Province', departmentCount: 25, population: 1100000 },
          { region: 'Eastern Province', departmentCount: 22, population: 1500000 }
        ],
        performanceMetrics: [
          { department: 'Treasury', kpi: 'Budget Efficiency', value: 87, target: 90 },
          { department: 'Customs', kpi: 'Revenue Collection', value: 92, target: 85 },
          { department: 'Public Health', kpi: 'Service Delivery', value: 78, target: 80 },
          { department: 'Schools', kpi: 'Student Performance', value: 85, target: 88 }
        ]
      };
      
      setAnalyticsData(mockAnalytics);
    }
  }, [summaryData]);

  const formatNumber = (num: number) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'LKR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading analytics dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <p>Error loading analytics: {error}</p>
      </div>
    );
  }

  if (!analyticsData) {
    return (
      <div className="error-container">
        <p>No analytics data available</p>
      </div>
    );
  }

  return (
    <div className="analytics-dashboard">
      {/* Header */}
      <div className="dashboard-header">
        <h1>Government Analytics Dashboard</h1>
        <p>Real-time insights from Neo4j database</p>
      </div>

      {/* Key Metrics Cards */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-icon">
            <Building2 size={24} className="text-blue-600" />
          </div>
          <div className="metric-content">
            <h3>Total Ministries</h3>
            <p className="metric-value">{analyticsData.ministryStats.totalMinistries}</p>
            <span className="metric-change positive">+2 this month</span>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">
            <Users size={24} className="text-green-600" />
          </div>
          <div className="metric-content">
            <h3>Total Departments</h3>
            <p className="metric-value">{analyticsData.ministryStats.totalDepartments}</p>
            <span className="metric-change positive">+8 this month</span>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">
            <Users size={24} className="text-purple-600" />
          </div>
          <div className="metric-content">
            <h3>Total Employees</h3>
            <p className="metric-value">{formatNumber(analyticsData.ministryStats.totalEmployees)}</p>
            <span className="metric-change positive">+156 this month</span>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">
            <Activity size={24} className="text-orange-600" />
          </div>
          <div className="metric-content">
            <h3>Active Changes</h3>
            <p className="metric-value">{analyticsData.ministryStats.activeChanges}</p>
            <span className="metric-change neutral">No change</span>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="charts-grid">
        {/* Change Timeline */}
        <div className="chart-card">
          <div className="chart-header">
            <h3>Change Timeline</h3>
            <div className="timeframe-selector">
              <button 
                className={selectedTimeframe === '7d' ? 'active' : ''}
                onClick={() => setSelectedTimeframe('7d')}
              >
                7D
              </button>
              <button 
                className={selectedTimeframe === '30d' ? 'active' : ''}
                onClick={() => setSelectedTimeframe('30d')}
              >
                30D
              </button>
              <button 
                className={selectedTimeframe === '90d' ? 'active' : ''}
                onClick={() => setSelectedTimeframe('90d')}
              >
                90D
              </button>
            </div>
          </div>
          <div className="chart-content">
            <div className="timeline-chart">
              {analyticsData.changeTimeline.map((day, index) => (
                <div key={index} className="timeline-bar">
                  <div className="bar-group">
                    <div 
                      className="bar added" 
                      style={{ height: `${(day.added / 10) * 100}%` }}
                      title={`Added: ${day.added}`}
                    ></div>
                    <div 
                      className="bar removed" 
                      style={{ height: `${(day.removed / 10) * 100}%` }}
                      title={`Removed: ${day.removed}`}
                    ></div>
                    <div 
                      className="bar modified" 
                      style={{ height: `${(day.modified / 10) * 100}%` }}
                      title={`Modified: ${day.modified}`}
                    ></div>
                  </div>
                  <span className="timeline-date">{new Date(day.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</span>
                </div>
              ))}
            </div>
            <div className="chart-legend">
              <div className="legend-item">
                <div className="legend-color added"></div>
                <span>Added</span>
              </div>
              <div className="legend-item">
                <div className="legend-color removed"></div>
                <span>Removed</span>
              </div>
              <div className="legend-item">
                <div className="legend-color modified"></div>
                <span>Modified</span>
              </div>
            </div>
          </div>
        </div>

        {/* Ministry Sizes */}
        <div className="chart-card">
          <div className="chart-header">
            <h3>Ministry Sizes</h3>
            <span className="chart-subtitle">Departments per Ministry</span>
          </div>
          <div className="chart-content">
            <div className="bar-chart">
              {analyticsData.ministrySizes.map((ministry, index) => (
                <div key={index} className="bar-item">
                  <div className="bar-label">{ministry.name}</div>
                  <div className="bar-container">
                    <div 
                      className="bar-fill" 
                      style={{ width: `${(ministry.departmentCount / 25) * 100}%` }}
                    ></div>
                    <span className="bar-value">{ministry.departmentCount}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Budget Distribution */}
        <div className="chart-card">
          <div className="chart-header">
            <h3>Budget Distribution</h3>
            <span className="chart-subtitle">Fiscal Year 2024</span>
          </div>
          <div className="chart-content">
            <div className="pie-chart">
              {analyticsData.budgetDistribution.map((item, index) => (
                <div key={index} className="pie-item">
                  <div className="pie-slice" style={{ 
                    background: `conic-gradient(from ${index * 72}deg, var(--color-${index + 1}) 0deg, var(--color-${index + 1}) ${item.percentage * 3.6}deg, transparent ${item.percentage * 3.6}deg)`
                  }}></div>
                  <div className="pie-info">
                    <h4>{item.ministry}</h4>
                    <p>{formatCurrency(item.budget)}</p>
                    <span>{item.percentage}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Regional Coverage */}
        <div className="chart-card">
          <div className="chart-header">
            <h3>Regional Coverage</h3>
            <span className="chart-subtitle">Departments by Region</span>
          </div>
          <div className="chart-content">
            <div className="map-chart">
              {analyticsData.regionalCoverage.map((region, index) => (
                <div key={index} className="region-item">
                  <div className="region-header">
                    <MapPin size={16} className="text-blue-600" />
                    <h4>{region.region}</h4>
                  </div>
                  <div className="region-stats">
                    <div className="stat">
                      <span className="stat-label">Departments</span>
                      <span className="stat-value">{region.departmentCount}</span>
                    </div>
                    <div className="stat">
                      <span className="stat-label">Population</span>
                      <span className="stat-value">{formatNumber(region.population)}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Performance Metrics */}
      <div className="performance-section">
        <div className="section-header">
          <h3>Performance Metrics</h3>
          <Target size={20} className="text-green-600" />
        </div>
        <div className="performance-grid">
          {analyticsData.performanceMetrics.map((metric, index) => (
            <div key={index} className="performance-card">
              <div className="performance-header">
                <h4>{metric.department}</h4>
                <span className="kpi-name">{metric.kpi}</span>
              </div>
              <div className="performance-value">
                <span className="current-value">{metric.value}%</span>
                <span className="target-value">Target: {metric.target}%</span>
              </div>
              <div className="performance-bar">
                <div 
                  className="performance-fill" 
                  style={{ width: `${(metric.value / metric.target) * 100}%` }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;
