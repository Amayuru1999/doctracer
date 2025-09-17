import { useState } from "react";
import { GitCompare, Building2 } from "lucide-react";
import AmendmentTracker from "./AmendmentTracker";

export default function DepartmentChanges() {
  const [viewMode, setViewMode] = useState<'overview' | 'comparison'>('overview');

  return (
    <section className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Department Changes</h1>
          <p className="text-slate-500">Track and analyze department structure changes across gazettes</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setViewMode('overview')}
            className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
              viewMode === 'overview'
                ? 'bg-sky-100 text-sky-700'
                : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            <Building2 className="h-4 w-4 inline mr-1" />
            Overview
          </button>
          <button
            onClick={() => setViewMode('comparison')}
            className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
              viewMode === 'comparison'
                ? 'bg-sky-100 text-sky-700'
                : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            <GitCompare className="h-4 w-4 inline mr-1" />
            Compare Gazettes
          </button>
        </div>
      </div>

      {viewMode === 'overview' && (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-8">
          <div className="text-center">
            <div className="text-6xl mb-4">🏢</div>
            <h3 className="text-xl font-semibold text-slate-800 mb-2">Department Changes Overview</h3>
            <p className="text-slate-600 mb-6">
              This section will show department-specific analytics and changes over time.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-2xl mx-auto">
              <div className="bg-slate-50 rounded-lg p-4">
                <div className="text-2xl font-bold text-slate-800">0</div>
                <div className="text-sm text-slate-600">Total Departments</div>
              </div>
              <div className="bg-slate-50 rounded-lg p-4">
                <div className="text-2xl font-bold text-slate-800">0</div>
                <div className="text-sm text-slate-600">Active Changes</div>
              </div>
              <div className="bg-slate-50 rounded-lg p-4">
                <div className="text-2xl font-bold text-slate-800">0</div>
                <div className="text-sm text-slate-600">Recent Updates</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {viewMode === 'comparison' && (
        <AmendmentTracker />
      )}
    </section>
  );
}