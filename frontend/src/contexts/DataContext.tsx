import React, { createContext, useContext, useState, useEffect } from 'react';

// Mock data for development
const MOCK_TREE_DATA: TreeNode = {
  name: "Government of Sri Lanka",
  children: [
    {
      name: "Ministry of Finance",
      status: "added",
      source: "amendment",
      children: [
        { name: "Treasury", type: "department", status: "added" },
        { name: "Customs", type: "department", status: "unchanged" },
        { name: "Inland Revenue", type: "department", status: "modified" }
      ]
    },
    {
      name: "Ministry of Education",
      status: "unchanged",
      source: "base",
      children: [
        { name: "Schools", type: "department", status: "unchanged" },
        { name: "Universities", type: "department", status: "unchanged" },
        { name: "Technical Education", type: "department", status: "added" }
      ]
    },
    {
      name: "Ministry of Health",
      status: "modified",
      source: "amendment",
      children: [
        { name: "Public Health", type: "department", status: "modified" },
        { name: "Hospitals", type: "department", status: "unchanged" },
        { name: "Medical Services", type: "department", status: "added" }
      ]
    },
    {
      name: "Ministry of Defense",
      status: "unchanged",
      source: "base",
      children: [
        { name: "Army", type: "department", status: "unchanged" },
        { name: "Navy", type: "department", status: "unchanged" },
        { name: "Air Force", type: "department", status: "unchanged" }
      ]
    },
    {
      name: "Ministry of Transport",
      status: "added",
      source: "amendment",
      children: [
        { name: "Roads", type: "department", status: "added" },
        { name: "Railways", type: "department", status: "added" },
        { name: "Ports", type: "department", status: "unchanged" }
      ]
    }
  ]
};

const MOCK_SUMMARY_DATA = {
  node_counts: [
    { node_type: "Ministry", count: 5 },
    { node_type: "Department", count: 15 },
    { node_type: "Function", count: 8 },
    { node_type: "Law", count: 12 }
  ],
  changes: [
    { status: "ADDED_DEPARTMENTS", count: 6 },
    { status: "REMOVED_DEPARTMENTS", count: 2 },
    { status: "MODIFIED_DEPARTMENTS", count: 3 },
    { status: "NEW_MINISTRIES", count: 2 }
  ]
};

const MOCK_DEPARTMENT_CHANGES = [
  {
    id: 1,
    department_name: "Treasury",
    ministry: "Ministry of Finance",
    change_type: "added",
    change_date: "2024-01-15",
    description: "New department added for financial management",
    impact_level: "high"
  },
  {
    id: 2,
    department_name: "Technical Education",
    ministry: "Ministry of Education",
    change_type: "added",
    change_date: "2024-01-10",
    description: "New department for technical and vocational education",
    impact_level: "medium"
  },
  {
    id: 3,
    department_name: "Medical Services",
    ministry: "Ministry of Health",
    change_type: "added",
    change_date: "2024-01-08",
    description: "New department for medical service coordination",
    impact_level: "high"
  },
  {
    id: 4,
    department_name: "Roads",
    ministry: "Ministry of Transport",
    change_type: "added",
    change_date: "2024-01-05",
    description: "New department for road infrastructure",
    impact_level: "medium"
  },
  {
    id: 5,
    department_name: "Railways",
    ministry: "Ministry of Transport",
    change_type: "added",
    change_date: "2024-01-03",
    description: "New department for railway management",
    impact_level: "medium"
  }
];

interface TreeNode {
  name: string;
  status?: 'added' | 'removed' | 'unchanged' | 'modified';
  source?: 'base' | 'amendment';
  type?: 'department' | 'function' | 'law';
  children?: TreeNode[];
}

export interface Minister {
  name: string;
  status: 'added' | 'removed' | 'unchanged' | 'modified';
  source: 'base' | 'amendment';
  type?: 'minister';
  children?: Department[];
}

export interface Department {
  name: string;
  type?: 'department' | 'function' | 'law';
  status: 'added' | 'removed' | 'unchanged' | 'modified';
  source?: 'base' | 'amendment';
}

interface NodeCount {
  node_type: string;
  count: number;
}

interface Change {
  status: string;
  count: number;
}

interface SummaryData {
  node_counts: NodeCount[];
  changes: Change[];
}

interface DepartmentChange {
  id: number;
  department_name: string;
  ministry: string;
  change_type: string;
  change_date: string;
  description: string;
  impact_level: string;
}

interface DataContextType {
  treeData: TreeNode | null;
  summaryData: SummaryData | null;
  departmentChanges: DepartmentChange[];
  loading: boolean;
  error: string | null;
  fetchTreeData: () => void;
  fetchSummaryData: () => void;
  fetchDepartmentChanges: () => void;
}

const DataContext = createContext<DataContextType | undefined>(undefined);

export const useData = () => {
  const context = useContext(DataContext);
  if (context === undefined) {
    throw new Error('useData must be used within a DataProvider');
  }
  return context;
};

export const DataProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [treeData, setTreeData] = useState<TreeNode | null>(null);
  const [summaryData, setSummaryData] = useState<SummaryData | null>(null);
  const [departmentChanges, setDepartmentChanges] = useState<DepartmentChange[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTreeData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 500));
      setTreeData(MOCK_TREE_DATA);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch tree data');
    } finally {
      setLoading(false);
    }
  };

  const fetchSummaryData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 300));
      setSummaryData(MOCK_SUMMARY_DATA);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch summary data');
    } finally {
      setLoading(false);
    }
  };

  const fetchDepartmentChanges = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 400));
      setDepartmentChanges(MOCK_DEPARTMENT_CHANGES);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch department changes');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Load all data on component mount
    fetchTreeData();
    fetchSummaryData();
    fetchDepartmentChanges();
  }, []);

  const value: DataContextType = {
    treeData,
    summaryData,
    departmentChanges,
    loading,
    error,
    fetchTreeData,
    fetchSummaryData,
    fetchDepartmentChanges,
  };

  return (
    <DataContext.Provider value={value}>
      {children}
    </DataContext.Provider>
  );
};
