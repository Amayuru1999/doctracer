import { useState, useEffect } from "react";
import type { KeyboardEvent } from "react";
import { useParams } from "react-router-dom";
import {
  getDashboardSummary as fetchDashboardSummary,
  getGazettes,
  getAmendments,
  getGazetteStructure,
  compareGazetteStructures,
  type DashboardSummary,
  type Gazette,
  type Amendment,
  type GazetteStructure,
  type GazetteComparison,
} from "../services/api";
import AmendmentTracker from "./AmendmentTracker";
import BaseGazetteVisualization from "./BaseGazetteVisualization";
import { useGovernment } from "../contexts/GovernmentContext";

export default function Dashboard() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [gazettes, setGazettes] = useState<Gazette[]>([]);
  const [amendments, setAmendments] = useState<Amendment[]>([]);
  const [selectedGazette, setSelectedGazette] = useState<Gazette | null>(null);
  const [selectedAmendment, setSelectedAmendment] = useState<Amendment | null>(
    null
  );
  const [gazetteStructure, setGazetteStructure] =
    useState<GazetteStructure | null>(null);
  const [comparison, setComparison] = useState<GazetteComparison | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<
    "structure" | "comparison" | "amendment-tracker" | "visualization"
  >("structure");
  const [expandedMinisters, setExpandedMinisters] = useState<Record<string, boolean>>({});
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({});
  const [expandedMinisterSections, setExpandedMinisterSections] = useState<Record<string, Record<string, boolean>>>({});

  const { selectedGovernment } = useGovernment();
  const params = useParams<{ presidentId?: string }>();
  const routeParam = params?.presidentId;
  const pathnameSegment =
    typeof window !== "undefined"
      ? window.location.pathname.split("/").filter(Boolean)[0]
      : undefined;
  const effectiveGovernment =
    selectedGovernment || routeParam || pathnameSegment;

  const govToPresidentName: { [key: string]: string } = {
    maithripala: "Maithripala Sirisena",
    gotabaya: "Gotabaya Rajapaksa",
    ranil: "Ranil Wickremesinghe",
    anura: "Anura Kumara Dissanayaka",
  };

  const presidentMapping: { [key: string]: string } = {
    "2159/15": "Gotabaya Rajapaksa",
    "2297/78": "Ranil Wickremesinghe",
    "2153/12": "Gotabaya Rajapaksa",
    "1905/4": "Maithripala Sirisena",
    "1897/15": "Maithripala Sirisena",
    "2289/43": "Ranil Wickremesinghe",
    "2412/08": "Anura Kumara Dissanayaka",
    "2458/65": "Anura Kumara Dissanayaka",
  };

  useEffect(() => {
    loadDashboardData();
  }, [effectiveGovernment]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [summaryData, gazettesData, amendmentsData] = await Promise.all([
        fetchDashboardSummary(),
        getGazettes(),
        getAmendments(),
      ]);
      setSummary(summaryData);
      setGazettes(gazettesData);
      setAmendments(amendmentsData);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getFilteredSummary = (rawSummary: DashboardSummary | null) => {
    if (!rawSummary || !effectiveGovernment) return rawSummary;

    const presidentName = govToPresidentName[effectiveGovernment];
    if (!presidentName) return rawSummary;

    // Filter recent gazettes by president
    const filteredRecent = rawSummary.recent_gazettes.filter((g: any) => {
      const gPresident = presidentMapping[g.gazette_id];
      return gPresident === presidentName;
    });

    // Count base & amendment gazettes for this president
    const baseCount = filteredRecent.filter((g: any) =>
      g.labels?.includes("BaseGazette")
    ).length;
    const amendmentCount = filteredRecent.filter((g: any) =>
      g.labels?.includes("AmendmentGazette")
    ).length;

    return {
      ...rawSummary,
      counts: {
        BaseGazette: baseCount,
        AmendmentGazette: amendmentCount,
      },
      recent_gazettes: filteredRecent,
    };
  };

  const displaySummary = getFilteredSummary(summary);

  const handleGazetteSelect = async (gazetteId: string) => {
    const gazette = gazettes.find((g) => g.gazette_id === gazetteId);
    if (gazette) {
      setSelectedGazette(gazette);
      setComparison(null);
      setError(null);
      try {
        const structure = await getGazetteStructure(gazetteId);
        setGazetteStructure(structure);
      } catch (err: any) {
        console.error("Failed to load gazette structure:", err);
        setError(`Failed to load gazette structure: ${err.message}`);
        setGazetteStructure(null);
      }
    }
  };

  const handleAmendmentSelect = async (amendmentId: string) => {
    const amendment = amendments.find((a) => a.gazette_id === amendmentId);
    if (amendment) {
      setSelectedAmendment(amendment);
      setGazetteStructure(null);
      setComparison(null);

      // If we have a base gazette selected, automatically compare
      if (selectedGazette) {
        try {
          const comparisonData = await compareGazetteStructures(
            selectedGazette.gazette_id,
            amendmentId
          );
          setComparison(comparisonData);
          setViewMode("comparison");
        } catch (err: any) {
          console.error("Failed to load comparison:", err);
        }
      }
    }
  };

  const handleCompare = async () => {
    if (selectedGazette && selectedAmendment) {
      try {
        setLoading(true);
        const comparisonData = await compareGazetteStructures(
          selectedGazette.gazette_id,
          selectedAmendment.gazette_id
        );
        setComparison(comparisonData);
        setViewMode("comparison");
      } catch (err: any) {
        console.error("Failed to load comparison:", err);
        setError("Failed to load comparison data");
      } finally {
        setLoading(false);
      }
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-slate-500">Loading dashboard data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-red-600 bg-red-50 p-4 rounded-lg">
        Error loading dashboard: {error}
      </div>
    );
  }

  const sortMinistries = <T extends { number?: string; name?: string }>(items: T[]) =>
    [...items].sort((a, b) => {
      const numA = parseInt(a.number || "999", 10);
      const numB = parseInt(b.number || "999", 10);
      if (!Number.isNaN(numA) && !Number.isNaN(numB) && numA !== numB) return numA - numB;
      return (a.name || "").localeCompare(b.name || "");
    });

  const renderGovernmentStructure = (
    structure: GazetteStructure,
    title: string,
    highlights?: {
      ministersAdded?: Set<string>;
      ministersRemoved?: Set<string>;
      ministersModified?: Set<string>;
      departmentsAdded?: Set<string>;
      departmentsRemoved?: Set<string>;
      functionsAdded?: Set<string>;
      functionsRemoved?: Set<string>;
      lawsAdded?: Set<string>;
      lawsRemoved?: Set<string>;
    },
    ministerAlignmentData?: Map<string, {
      allFunctions: string[];
      allDepartments: string[];
      allLaws: string[];
    }>
  ) => {
    // Sort ministers by their actual number from Neo4j
    const sortedMinisters = [...structure.ministers].sort((a, b) => {
      const numA = parseInt(a.number || "999", 10);
      const numB = parseInt(b.number || "999", 10);
      return numA - numB;
    });

    return (
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-slate-800 border-b pb-2">
          {title}
        </h3>

        {/* Ministers */}
        {sortedMinisters.length > 0 && (
          <div>
            <h4 className="font-medium text-slate-700 mb-3 flex items-center gap-2">
              <span className="w-3 h-3 bg-blue-500 rounded-full"></span>
              Ministers ({sortedMinisters.length})
            </h4>
            <div className="space-y-3">
              {sortedMinisters.map((minister, index) => {
                const rawNum = minister.number && minister.number !== 'Unknown' ? String(minister.number) : '';
                const ministryNumber = rawNum ? rawNum.padStart(2, '0') : `${String(index + 1).padStart(2, '0')}`;
                const ministerKey = `${ministryNumber}-${minister.name}`; // shared key so base/amendment expand together
                const isExpanded = !!expandedMinisters[ministerKey];
                const isAdded = highlights?.ministersAdded?.has(ministerKey);
                const isRemoved = highlights?.ministersRemoved?.has(ministerKey);
                const isModified = highlights?.ministersModified?.has(ministerKey);

                const handleToggle = () => {
                  setExpandedMinisters((prev) => ({ ...prev, [ministerKey]: !prev[ministerKey] }));
                };
                const handleKeyDown = (e: KeyboardEvent<HTMLDivElement>) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    handleToggle();
                  }
                };
                
                return (
                  <div
                    key={ministerKey}
                    className={`rounded-lg p-4 border cursor-pointer hover:border-sky-200 ${
                      isAdded ? "bg-green-50 border-green-300" : isRemoved ? "bg-red-50 border-red-300" : isModified ? "bg-yellow-50 border-yellow-300" : "bg-slate-50"
                    }`}
                    onClick={handleToggle}
                    onKeyDown={handleKeyDown}
                    tabIndex={0}
                    role="button"
                    aria-expanded={isExpanded}
                    aria-label={`${isExpanded ? 'Collapse' : 'Expand'} ${minister.name}`}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <h5 className="font-medium text-slate-800 mb-1">
                          {`${ministryNumber}. ${minister.name}`}
                        </h5>
                        {!isExpanded && (
                          <div className="text-xs text-slate-500">Click to view departments, functions, and laws</div>
                        )}
                      </div>
                      <div className="text-sm text-slate-600" aria-hidden>
                        {isExpanded ? "▾" : "▸"}
                      </div>
                    </div>

                    {isExpanded && (
                      <div className="mt-3 space-y-2">
                        {/* Functions (click whole section to toggle) */}
                        {(() => {
                          const alignmentData = ministerAlignmentData?.get(ministerKey);
                          const functionsToShow = alignmentData?.allFunctions || (minister.functions || []);
                          const actualFunctions = new Set(minister.functions || []);
                          const actualCount = actualFunctions.size; // Count only actual items, not blanks
                          
                          // Count changes
                          const addedCount = functionsToShow.filter(f => highlights?.functionsAdded?.has(f) && actualFunctions.has(f)).length;
                          const removedCount = functionsToShow.filter(f => highlights?.functionsRemoved?.has(f) && actualFunctions.has(f)).length;
                          
                          // Determine border color based on changes
                          const hasChanges = addedCount > 0 || removedCount > 0;
                          const borderColor = !hasChanges ? "border-slate-200" : 
                                            addedCount > 0 && removedCount > 0 ? "border-yellow-400 border-2" :
                                            addedCount > 0 ? "border-green-400 border-2" : "border-red-400 border-2";
                          const bgColor = !hasChanges ? "" : 
                                         addedCount > 0 && removedCount > 0 ? "bg-yellow-50" :
                                         addedCount > 0 ? "bg-green-50" : "bg-red-50";
                          
                          if (functionsToShow.length === 0) return null;
                          
                          const isSubExpanded = !!expandedMinisterSections[ministerKey]?.functions;
                          const toggle = () =>
                            setExpandedMinisterSections((prev) => ({
                              ...prev,
                              [ministerKey]: { ...(prev[ministerKey] || {}), functions: !isSubExpanded },
                            }));
                          
                          return (
                            <div
                              className={`border ${borderColor} ${bgColor} rounded-lg p-2 cursor-pointer hover:border-sky-300`}
                              onClick={(e) => { e.stopPropagation(); toggle(); }}
                              role="button"
                              aria-expanded={isSubExpanded}
                            >
                              <div className="flex items-center justify-between">
                                <span className="text-sm font-medium text-slate-600">Functions ({actualCount})</span>
                                <span className="text-sm text-slate-600" aria-hidden>{isSubExpanded ? "▾" : "▸"}</span>
                              </div>
                              {isSubExpanded && (
                                <ul className="mt-2 space-y-1">
                                  {functionsToShow.map((func, i) => {
                                    const isPresent = actualFunctions.has(func);
                                    const added = highlights?.functionsAdded?.has(func);
                                    const removed = highlights?.functionsRemoved?.has(func);
                                    
                                    // If not present in this structure, show as blank row
                                    if (!isPresent && alignmentData) {
                                      return (
                                        <li key={i} className="bg-slate-100 border border-dashed border-slate-300 px-3 py-2 text-xs rounded text-slate-400 flex items-center gap-2">
                                          <span className="font-bold">—</span>
                                          <span className="italic"></span>
                                        </li>
                                      );
                                    }
                                    
                                    const bgClass = added
                                      ? "bg-green-50 border-l-4 border-green-500"
                                      : removed
                                      ? "bg-red-50 border-l-4 border-red-500"
                                      : "bg-purple-50 border-l-4 border-purple-400";
                                    const textClass = added ? "text-green-900" : removed ? "text-red-900" : "text-purple-900";
                                    return (
                                      <li key={i} className={`${bgClass} px-3 py-2 text-xs rounded ${textClass} flex items-center gap-2`}>
                                        <span className="font-bold">{added ? "✓" : removed ? "✗" : "•"}</span>
                                        <span>{func}</span>
                                      </li>
                                    );
                                  })}
                                </ul>
                              )}
                            </div>
                          );
                        })()}

                        {/* Departments (click whole section to toggle) */}
                        {(() => {
                          const alignmentData = ministerAlignmentData?.get(ministerKey);
                          const departmentsToShow = alignmentData?.allDepartments || (minister.departments || []);
                          const actualDepartments = new Set(minister.departments || []);
                          const actualCount = actualDepartments.size; // Count only actual items, not blanks
                          
                          // Count changes
                          const addedCount = departmentsToShow.filter(d => highlights?.departmentsAdded?.has(d) && actualDepartments.has(d)).length;
                          const removedCount = departmentsToShow.filter(d => highlights?.departmentsRemoved?.has(d) && actualDepartments.has(d)).length;
                          
                          // Determine border color based on changes
                          const hasChanges = addedCount > 0 || removedCount > 0;
                          const borderColor = !hasChanges ? "border-slate-200" : 
                                            addedCount > 0 && removedCount > 0 ? "border-yellow-400 border-2" :
                                            addedCount > 0 ? "border-green-400 border-2" : "border-red-400 border-2";
                          const bgColor = !hasChanges ? "" : 
                                         addedCount > 0 && removedCount > 0 ? "bg-yellow-50" :
                                         addedCount > 0 ? "bg-green-50" : "bg-red-50";
                          
                          if (departmentsToShow.length === 0) return null;
                          
                          const isSubExpanded = !!expandedMinisterSections[ministerKey]?.departments;
                          const toggle = () =>
                            setExpandedMinisterSections((prev) => ({
                              ...prev,
                              [ministerKey]: { ...(prev[ministerKey] || {}), departments: !isSubExpanded },
                            }));
                          
                          return (
                            <div
                              className={`border ${borderColor} ${bgColor} rounded-lg p-2 cursor-pointer hover:border-sky-300`}
                              onClick={(e) => { e.stopPropagation(); toggle(); }}
                              role="button"
                              aria-expanded={isSubExpanded}
                            >
                              <div className="flex items-center justify-between">
                                <span className="text-sm font-medium text-slate-600">Departments ({actualCount})</span>
                                <span className="text-sm text-slate-600" aria-hidden>{isSubExpanded ? "▾" : "▸"}</span>
                              </div>
                              {isSubExpanded && (
                                <ul className="mt-2 space-y-1">
                                  {departmentsToShow.map((dept, i) => {
                                    const isPresent = actualDepartments.has(dept);
                                    const added = highlights?.departmentsAdded?.has(dept);
                                    const removed = highlights?.departmentsRemoved?.has(dept);
                                    
                                    // If not present in this structure, show as blank row
                                    if (!isPresent && alignmentData) {
                                      return (
                                        <li key={i} className="bg-slate-100 border border-dashed border-slate-300 px-3 py-2 text-xs rounded text-slate-400 flex items-center gap-2">
                                          <span className="font-bold">—</span>
                                          <span className="italic"></span>
                                        </li>
                                      );
                                    }
                                    
                                    const bgClass = added
                                      ? "bg-green-50 border-l-4 border-green-500"
                                      : removed
                                      ? "bg-red-50 border-l-4 border-red-500"
                                      : "bg-blue-50 border-l-4 border-blue-400";
                                    const textClass = added ? "text-green-900" : removed ? "text-red-900" : "text-blue-900";
                                    return (
                                      <li key={i} className={`${bgClass} px-3 py-2 text-xs rounded ${textClass} flex items-center gap-2`}>
                                        <span className="text-xs font-bold">{added ? "✓" : removed ? "✗" : "•"}</span>
                                        <span>{dept}</span>
                                      </li>
                                    );
                                  })}
                                </ul>
                              )}
                            </div>
                          );
                        })()}

                        {/* Laws (click whole section to toggle) */}
                        {(() => {
                          const alignmentData = ministerAlignmentData?.get(ministerKey);
                          const lawsToShow = alignmentData?.allLaws || (minister.laws || []);
                          const actualLaws = new Set(minister.laws || []);
                          const actualCount = actualLaws.size; // Count only actual items, not blanks
                          
                          // Count changes
                          const addedCount = lawsToShow.filter(l => highlights?.lawsAdded?.has(l) && actualLaws.has(l)).length;
                          const removedCount = lawsToShow.filter(l => highlights?.lawsRemoved?.has(l) && actualLaws.has(l)).length;
                          
                          // Determine border color based on changes
                          const hasChanges = addedCount > 0 || removedCount > 0;
                          const borderColor = !hasChanges ? "border-slate-200" : 
                                            addedCount > 0 && removedCount > 0 ? "border-yellow-400 border-2" :
                                            addedCount > 0 ? "border-green-400 border-2" : "border-red-400 border-2";
                          const bgColor = !hasChanges ? "" : 
                                         addedCount > 0 && removedCount > 0 ? "bg-yellow-50" :
                                         addedCount > 0 ? "bg-green-50" : "bg-red-50";
                          
                          if (lawsToShow.length === 0) return null;
                          
                          const isSubExpanded = !!expandedMinisterSections[ministerKey]?.laws;
                          const toggle = () =>
                            setExpandedMinisterSections((prev) => ({
                              ...prev,
                              [ministerKey]: { ...(prev[ministerKey] || {}), laws: !isSubExpanded },
                            }));
                          
                          return (
                            <div
                              className={`border ${borderColor} ${bgColor} rounded-lg p-2 cursor-pointer hover:border-sky-300`}
                              onClick={(e) => { e.stopPropagation(); toggle(); }}
                              role="button"
                              aria-expanded={isSubExpanded}
                            >
                              <div className="flex items-center justify-between">
                                <span className="text-sm font-medium text-slate-600">Laws ({actualCount})</span>
                                <span className="text-sm text-slate-600" aria-hidden>{isSubExpanded ? "▾" : "▸"}</span>
                              </div>
                              {isSubExpanded && (
                                <ul className="mt-2 space-y-1">
                                  {lawsToShow.map((law, i) => {
                                    const isPresent = actualLaws.has(law);
                                    const added = highlights?.lawsAdded?.has(law);
                                    const removed = highlights?.lawsRemoved?.has(law);
                                    
                                    // If not present in this structure, show as blank row
                                    if (!isPresent && alignmentData) {
                                      return (
                                        <li key={i} className="bg-slate-100 border border-dashed border-slate-300 px-3 py-2 text-xs rounded text-slate-400 flex items-center gap-2">
                                          <span className="font-bold">—</span>
                                          <span className="italic"></span>
                                        </li>
                                      );
                                    }
                                    
                                    const bgClass = added
                                      ? "bg-green-50 border-l-4 border-green-500"
                                      : removed
                                      ? "bg-red-50 border-l-4 border-red-500"
                                      : "bg-orange-50 border-l-4 border-orange-400";
                                    const textClass = added ? "text-green-900" : removed ? "text-red-900" : "text-orange-900";
                                    return (
                                      <li key={i} className={`${bgClass} px-3 py-2 text-xs rounded ${textClass} flex items-center gap-2`}>
                                        <span className="text-xs font-bold">{added ? "✓" : removed ? "✗" : "•"}</span>
                                        <span>{law}</span>
                                      </li>
                                    );
                                  })}
                                </ul>
                              )}
                            </div>
                          );
                        })()}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Standalone Departments */}
        {structure.departments.length > 0 && (() => {
          const sectionKey = "departments"; // shared so base/amendment stay in sync
          const isExpanded = !!expandedSections[sectionKey];
          const toggle = () => setExpandedSections((prev) => ({ ...prev, [sectionKey]: !prev[sectionKey] }));
          const onKey = (e: KeyboardEvent<HTMLDivElement>) => {
            if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle(); }
          };
          return (
            <div
              className="border border-slate-200 rounded-lg p-3 mb-2 cursor-pointer hover:border-sky-200"
              onClick={toggle}
              onKeyDown={onKey}
              tabIndex={0}
              role="button"
              aria-expanded={isExpanded}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 bg-green-500 rounded-full"></span>
                  <span className="font-medium text-slate-700">Departments ({structure.departments.length})</span>
                </div>
                <span className="text-sm text-slate-600" aria-hidden>{isExpanded ? "▾" : "▸"}</span>
              </div>
              {isExpanded && (
                <ul className="space-y-1">
                  {structure.departments.map((dept, i) => {
                    const added = highlights?.departmentsAdded?.has(dept);
                    const removed = highlights?.departmentsRemoved?.has(dept);
                    const bgClass = added
                      ? "bg-green-50 border-l-4 border-green-500"
                      : removed
                      ? "bg-red-50 border-l-4 border-red-500"
                      : "bg-green-50 border-l-4 border-green-400";
                    const textClass = added ? "text-green-900" : removed ? "text-red-900" : "text-green-900";
                    return (
                      <li key={i} className={`${bgClass} px-3 py-2 text-sm rounded ${textClass} flex items-center gap-2`}>
                        <span className="font-bold">{added ? "✓" : removed ? "✗" : "•"}</span>
                        <span>{dept}</span>
                      </li>
                    );
                  })}
                </ul>
              )}
            </div>
          );
        })()}

        {/* Standalone Functions */}
        {(structure.functions || []).length > 0 && (() => {
          const sectionKey = "functions";
          const isExpanded = !!expandedSections[sectionKey];
          const toggle = () => setExpandedSections((prev) => ({ ...prev, [sectionKey]: !prev[sectionKey] }));
          const onKey = (e: KeyboardEvent<HTMLDivElement>) => {
            if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle(); }
          };
          return (
            <div
              className="border border-slate-200 rounded-lg p-3 mb-2 cursor-pointer hover:border-sky-200"
              onClick={toggle}
              onKeyDown={onKey}
              tabIndex={0}
              role="button"
              aria-expanded={isExpanded}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 bg-purple-500 rounded-full"></span>
                  <span className="font-medium text-slate-700">Functions ({(structure.functions || []).length})</span>
                </div>
                <span className="text-sm text-slate-600" aria-hidden>{isExpanded ? "▾" : "▸"}</span>
              </div>
              {isExpanded && (
                <ul className="space-y-1">
                  {(structure.functions || []).map((func, i) => {
                    const added = highlights?.functionsAdded?.has(func);
                    const removed = highlights?.functionsRemoved?.has(func);
                    const bgClass = added
                      ? "bg-green-50 border-l-4 border-green-500"
                      : removed
                      ? "bg-red-50 border-l-4 border-red-500"
                      : "bg-purple-50 border-l-4 border-purple-400";
                    const textClass = added ? "text-green-900" : removed ? "text-red-900" : "text-purple-900";
                    return (
                      <li key={i} className={`${bgClass} px-3 py-2 text-sm rounded ${textClass} flex items-center gap-2`}>
                        <span className="font-bold">{added ? "✓" : removed ? "✗" : "•"}</span>
                        <span>{func}</span>
                      </li>
                    );
                  })}
                </ul>
              )}
            </div>
          );
        })()}

        {/* Standalone Laws */}
        {structure.laws.length > 0 && (() => {
          const sectionKey = "laws";
          const isExpanded = !!expandedSections[sectionKey];
          const toggle = () => setExpandedSections((prev) => ({ ...prev, [sectionKey]: !prev[sectionKey] }));
          const onKey = (e: KeyboardEvent<HTMLDivElement>) => {
            if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle(); }
          };
          return (
            <div
              className="border border-slate-200 rounded-lg p-3 mb-2 cursor-pointer hover:border-sky-200"
              onClick={toggle}
              onKeyDown={onKey}
              tabIndex={0}
              role="button"
              aria-expanded={isExpanded}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 bg-orange-500 rounded-full"></span>
                  <span className="font-medium text-slate-700">Laws ({structure.laws.length})</span>
                </div>
                <span className="text-sm text-slate-600" aria-hidden>{isExpanded ? "▾" : "▸"}</span>
              </div>
              {isExpanded && (
                <ul className="space-y-1">
                  {structure.laws.map((law, i) => {
                    const added = highlights?.lawsAdded?.has(law);
                    const removed = highlights?.lawsRemoved?.has(law);
                    const bgClass = added
                      ? "bg-green-50 border-l-4 border-green-500"
                      : removed
                      ? "bg-red-50 border-l-4 border-red-500"
                      : "bg-orange-50 border-l-4 border-orange-400";
                    const textClass = added ? "text-green-900" : removed ? "text-red-900" : "text-orange-900";
                    return (
                      <li key={i} className={`${bgClass} px-3 py-2 text-sm rounded ${textClass} flex items-center gap-2`}>
                        <span className="font-bold">{added ? "✓" : removed ? "✗" : "•"}</span>
                        <span>{law}</span>
                      </li>
                    );
                  })}
                </ul>
              )}
            </div>
          );
        })()}

        {/* Raw Entities Debug */}
        {structure.raw_entities.length > 0 && (
          <details className="mt-4">
            <summary className="text-sm font-medium text-slate-600 cursor-pointer">
              Debug: Raw Entities ({structure.raw_entities.length})
            </summary>
            <div className="mt-2 p-3 bg-gray-100 rounded text-xs">
              <pre>{JSON.stringify(structure.raw_entities, null, 2)}</pre>
            </div>
          </details>
        )}
      </div>
    );
  };

  const renderComparison = (comparison: GazetteComparison) => (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-blue-50 to-green-50 rounded-xl p-6 border border-slate-200">
        <div>
          <h3 className="text-2xl font-bold text-slate-800 mb-3">
            Government Structure Comparison
          </h3>
          <div className="flex items-center gap-4 text-sm">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 bg-blue-500 rounded-full"></span>
              <span className="font-semibold text-blue-900">Base:</span>
              <span className="text-slate-700">{comparison.base_gazette.president}</span>
              <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-medium">
                {comparison.base_gazette.id}
              </span>
              <span className="text-slate-500 text-xs">
                {comparison.base_gazette.published_date}
              </span>
            </div>
            <span className="text-2xl text-slate-400">→</span>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 bg-green-500 rounded-full"></span>
              <span className="font-semibold text-green-900">Amendment:</span>
              <span className="text-slate-700">{comparison.amendment_gazette.president}</span>
              <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs font-medium">
                {comparison.amendment_gazette.id}
              </span>
              <span className="text-slate-500 text-xs">
                {comparison.amendment_gazette.published_date}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Show note if detailed tracking is not available */}
      {(comparison.amendment_gazette.structure as any).note && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <svg
                className="h-5 w-5 text-yellow-400"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-yellow-800">
                Limited Change Tracking
              </h3>
              <div className="mt-2 text-sm text-yellow-700">
                <p>{(comparison.amendment_gazette.structure as any).note}</p>
                <p className="mt-1">
                  The comparison below shows the base gazette structure.
                  Detailed change tracking for this amendment is not available
                  in the current dataset.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Changes Summary */}
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h4 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
          <span className="w-2 h-2 bg-gradient-to-r from-green-500 to-red-500 rounded-full"></span>
          Change Summary
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-gradient-to-br from-green-50 to-green-100 border-2 border-green-200 rounded-lg p-4 shadow-sm">
            <div className="flex items-center gap-2 mb-3">
              <span className="text-2xl">✓</span>
              <h4 className="font-bold text-green-900">Added</h4>
            </div>
            <div className="space-y-2 text-sm text-green-800">
              <div className="flex justify-between items-center bg-white/50 px-2 py-1 rounded">
                <span>Ministers</span>
                <span className="font-bold">{comparison.changes.added_ministers.length}</span>
              </div>
              <div className="flex justify-between items-center bg-white/50 px-2 py-1 rounded">
                <span>Departments</span>
                <span className="font-bold">{comparison.changes.added_departments.length}</span>
              </div>
              <div className="flex justify-between items-center bg-white/50 px-2 py-1 rounded">
                <span>Functions</span>
                <span className="font-bold">{(comparison.changes.added_functions || []).length}</span>
              </div>
              <div className="flex justify-between items-center bg-white/50 px-2 py-1 rounded">
                <span>Laws</span>
                <span className="font-bold">{comparison.changes.added_laws.length}</span>
              </div>
            </div>
            {comparison.changes.added_ministers.length > 0 && (
              <details className="mt-2">
                <summary className="cursor-pointer text-xs font-semibold text-green-900 hover:text-green-700">
                  View Ministers ({comparison.changes.added_ministers.length})
                </summary>
                <div className="mt-2 space-y-1 max-h-32 overflow-y-auto">
                  {sortMinistries(comparison.changes.added_ministers).map((minister, i) => {
                    const displayNumber = minister.number && minister.number !== "Unknown"
                      ? minister.number
                      : String(i + 1).padStart(2, "0");
                    return (
                      <div
                        key={i}
                        className="text-xs bg-white px-2 py-1 rounded border border-green-200"
                      >
                        {`${displayNumber}. ${minister.name}`}
                      </div>
                    );
                  })}
                </div>
              </details>
            )}
          </div>

          <div className="bg-gradient-to-br from-red-50 to-red-100 border-2 border-red-200 rounded-lg p-4 shadow-sm">
            <div className="flex items-center gap-2 mb-3">
              <span className="text-2xl">✗</span>
              <h4 className="font-bold text-red-900">Removed</h4>
            </div>
            <div className="space-y-2 text-sm text-red-800">
              <div className="flex justify-between items-center bg-white/50 px-2 py-1 rounded">
                <span>Ministers</span>
                <span className="font-bold">{comparison.changes.removed_ministers.length}</span>
              </div>
              <div className="flex justify-between items-center bg-white/50 px-2 py-1 rounded">
                <span>Departments</span>
                <span className="font-bold">{comparison.changes.removed_departments.length}</span>
              </div>
              <div className="flex justify-between items-center bg-white/50 px-2 py-1 rounded">
                <span>Functions</span>
                <span className="font-bold">{(comparison.changes.removed_functions || []).length}</span>
              </div>
              <div className="flex justify-between items-center bg-white/50 px-2 py-1 rounded">
                <span>Laws</span>
                <span className="font-bold">{comparison.changes.removed_laws.length}</span>
              </div>
            </div>
            {comparison.changes.removed_ministers.length > 0 && (
              <details className="mt-2">
                <summary className="cursor-pointer text-xs font-semibold text-red-900 hover:text-red-700">
                  View Ministers ({comparison.changes.removed_ministers.length})
                </summary>
                <div className="mt-2 space-y-1 max-h-32 overflow-y-auto">
                  {sortMinistries(comparison.changes.removed_ministers).map((minister, i) => {
                    const displayNumber = minister.number && minister.number !== "Unknown"
                      ? minister.number
                      : String(i + 1).padStart(2, "0");
                    return (
                      <div
                        key={i}
                        className="text-xs bg-white px-2 py-1 rounded border border-red-200"
                      >
                        {`${displayNumber}. ${minister.name}`}
                      </div>
                    );
                  })}
                </div>
              </details>
            )}
          </div>

          <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 border-2 border-yellow-200 rounded-lg p-4 shadow-sm">
            <div className="flex items-center gap-2 mb-3">
              <span className="text-2xl">⚡</span>
              <h4 className="font-bold text-yellow-900">Modified</h4>
            </div>
            <div className="space-y-2 text-sm text-yellow-800">
              <div className="flex justify-between items-center bg-white/50 px-2 py-1 rounded">
                <span>Ministers</span>
                <span className="font-bold">{comparison.changes.modified_ministers.length}</span>
              </div>
            </div>
            {comparison.changes.modified_ministers.length > 0 && (
              <details className="mt-2">
                <summary className="cursor-pointer text-xs font-semibold text-yellow-900 hover:text-yellow-700">
                  View Ministers ({comparison.changes.modified_ministers.length})
                </summary>
                <div className="mt-2 space-y-1 max-h-32 overflow-y-auto">
                  {sortMinistries(comparison.changes.modified_ministers).map((minister, i) => {
                    const displayNumber = minister.number && minister.number !== "Unknown"
                      ? minister.number
                      : String(i + 1).padStart(2, "0");
                    return (
                      <div
                        key={i}
                        className="text-xs bg-white px-2 py-1 rounded border border-yellow-200"
                      >
                        {`${displayNumber}. ${minister.name}`}
                      </div>
                    );
                  })}
                </div>
              </details>
            )}
          </div>

          <div className="bg-gradient-to-br from-blue-50 to-blue-100 border-2 border-blue-200 rounded-lg p-4 shadow-sm">
            <div className="flex items-center gap-2 mb-3">
              <span className="text-2xl">📊</span>
              <h4 className="font-bold text-blue-900">Total</h4>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-blue-900">
                {comparison.changes.added_ministers.length +
                  comparison.changes.removed_ministers.length +
                  comparison.changes.modified_ministers.length +
                  comparison.changes.added_departments.length +
                  comparison.changes.removed_departments.length +
                  comparison.changes.added_laws.length +
                  comparison.changes.removed_laws.length +
                  (comparison.changes.added_functions || []).length +
                  (comparison.changes.removed_functions || []).length}
              </div>
              <div className="text-xs text-blue-700 mt-1">Changes</div>
            </div>
          </div>
        </div>
      </div>

      {/* Detailed Changes */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border-2 border-blue-200 shadow-lg overflow-hidden">
          <div className="bg-gradient-to-r from-blue-500 to-blue-600 px-6 py-4">
            <h4 className="font-bold text-white text-lg flex items-center gap-2">
              <span className="w-2 h-2 bg-white rounded-full animate-pulse"></span>
              Base Gazette
            </h4>
            <div className="text-blue-100 text-sm mt-1">
              <span className="font-semibold">{comparison.base_gazette.president}</span>
              {" • "}
              {comparison.base_gazette.id}
              {" • "}
              {comparison.base_gazette.published_date}
            </div>
          </div>
          <div className="p-6">
          {(() => {
            // Create per-minister alignment data
            const ministerAlignmentMap = new Map<string, {
              allFunctions: string[];
              allDepartments: string[];
              allLaws: string[];
            }>();
            
            // Build a map of ministers from both sides by their key
            const baseMinisterMap = new Map(
              comparison.base_gazette.structure.ministers.map(m => {
                const raw = m.number && m.number !== "Unknown" ? String(m.number) : "";
                const number = raw ? raw.padStart(2, "0") : "";
                return [`${number}-${m.name}`, m];
              })
            );
            
            const amendmentMinisterMap = new Map(
              comparison.amendment_gazette.structure.ministers.map(m => {
                const raw = m.number && m.number !== "Unknown" ? String(m.number) : "";
                const number = raw ? raw.padStart(2, "0") : "";
                return [`${number}-${m.name}`, m];
              })
            );
            
            // For each unique minister key, create alignment data
            const allMinisterKeys = new Set([
              ...baseMinisterMap.keys(),
              ...amendmentMinisterMap.keys()
            ]);
            
            allMinisterKeys.forEach(key => {
              const baseMinister = baseMinisterMap.get(key);
              const amendmentMinister = amendmentMinisterMap.get(key);
              
              // Collect functions from both sides for this specific minister
              const baseFunctions = new Set(baseMinister?.functions || []);
              const amendmentFunctions = new Set(amendmentMinister?.functions || []);
              const allFunctions = Array.from(new Set([...baseFunctions, ...amendmentFunctions])).sort();
              
              // Collect departments from both sides for this specific minister
              const baseDepartments = new Set(baseMinister?.departments || []);
              const amendmentDepartments = new Set(amendmentMinister?.departments || []);
              const allDepartments = Array.from(new Set([...baseDepartments, ...amendmentDepartments])).sort();
              
              // Collect laws from both sides for this specific minister
              const baseLaws = new Set(baseMinister?.laws || []);
              const amendmentLaws = new Set(amendmentMinister?.laws || []);
              const allLaws = Array.from(new Set([...baseLaws, ...amendmentLaws])).sort();
              
              ministerAlignmentMap.set(key, {
                allFunctions,
                allDepartments,
                allLaws
              });
            });
            
            // Build highlight sets for base side (show removed/modified)
            const ministersRemoved = new Set(
              comparison.changes.removed_ministers.map((m) => {
                const raw = m.number && m.number !== "Unknown" ? String(m.number) : "";
                const number = raw ? raw.padStart(2, "0") : "";
                return `${number}-${m.name}`;
              })
            );
            const ministersModified = new Set(
              (comparison.changes.modified_ministers || []).map((m: any) => {
                const raw = m.number && m.number !== "Unknown" ? String(m.number) : "";
                const number = raw ? raw.padStart(2, "0") : "";
                return `${number}-${m.name}`;
              })
            );
            const departmentsRemoved = new Set(comparison.changes.removed_departments);
            const functionsRemoved = new Set(comparison.changes.removed_functions || []);
            const lawsRemoved = new Set(comparison.changes.removed_laws);
            return renderGovernmentStructure(
              comparison.base_gazette.structure,
              `Base: ${comparison.base_gazette.id}`,
              {
                ministersRemoved,
                ministersModified,
                departmentsRemoved,
                functionsRemoved,
                lawsRemoved,
              },
              ministerAlignmentMap
            );
          })()}
          </div>
        </div>

        <div className="bg-white rounded-xl border-2 border-green-200 shadow-lg overflow-hidden">
          <div className="bg-gradient-to-r from-green-500 to-green-600 px-6 py-4">
            <h4 className="font-bold text-white text-lg flex items-center gap-2">
              <span className="w-2 h-2 bg-white rounded-full animate-pulse"></span>
              Amendment Gazette
            </h4>
            <div className="text-green-100 text-sm mt-1">
              <span className="font-semibold">{comparison.amendment_gazette.president}</span>
              {" • "}
              {comparison.amendment_gazette.id}
              {" • "}
              {comparison.amendment_gazette.published_date}
            </div>
          </div>
          <div className="p-6">
          {(() => {
            // Reuse the same per-minister alignment data
            const ministerAlignmentMap = new Map<string, {
              allFunctions: string[];
              allDepartments: string[];
              allLaws: string[];
            }>();
            
            // Build a map of ministers from both sides by their key
            const baseMinisterMap = new Map(
              comparison.base_gazette.structure.ministers.map(m => {
                const number = m.number && m.number !== "Unknown" ? m.number : "";
                return [`${number}-${m.name}`, m];
              })
            );
            
            const amendmentMinisterMap = new Map(
              comparison.amendment_gazette.structure.ministers.map(m => {
                const number = m.number && m.number !== "Unknown" ? m.number : "";
                return [`${number}-${m.name}`, m];
              })
            );
            
            // For each unique minister key, create alignment data
            const allMinisterKeys = new Set([
              ...baseMinisterMap.keys(),
              ...amendmentMinisterMap.keys()
            ]);
            
            allMinisterKeys.forEach(key => {
              const baseMinister = baseMinisterMap.get(key);
              const amendmentMinister = amendmentMinisterMap.get(key);
              
              // Collect functions from both sides for this specific minister
              const baseFunctions = new Set(baseMinister?.functions || []);
              const amendmentFunctions = new Set(amendmentMinister?.functions || []);
              const allFunctions = Array.from(new Set([...baseFunctions, ...amendmentFunctions])).sort();
              
              // Collect departments from both sides for this specific minister
              const baseDepartments = new Set(baseMinister?.departments || []);
              const amendmentDepartments = new Set(amendmentMinister?.departments || []);
              const allDepartments = Array.from(new Set([...baseDepartments, ...amendmentDepartments])).sort();
              
              // Collect laws from both sides for this specific minister
              const baseLaws = new Set(baseMinister?.laws || []);
              const amendmentLaws = new Set(amendmentMinister?.laws || []);
              const allLaws = Array.from(new Set([...baseLaws, ...amendmentLaws])).sort();
              
              ministerAlignmentMap.set(key, {
                allFunctions,
                allDepartments,
                allLaws
              });
            });
            
            // Build highlight sets for amendment side (show added/modified)
            const ministersAdded = new Set(
              comparison.changes.added_ministers.map((m) => {
                const raw = m.number && m.number !== "Unknown" ? String(m.number) : "";
                const number = raw ? raw.padStart(2, "0") : "";
                return `${number}-${m.name}`;
              })
            );
            const ministersModified = new Set(
              (comparison.changes.modified_ministers || []).map((m: any) => {
                const raw = m.number && m.number !== "Unknown" ? String(m.number) : "";
                const number = raw ? raw.padStart(2, "0") : "";
                return `${number}-${m.name}`;
              })
            );
            const departmentsAdded = new Set(comparison.changes.added_departments);
            const functionsAdded = new Set(comparison.changes.added_functions || []);
            const lawsAdded = new Set(comparison.changes.added_laws);
            
            // Sets for removed items
            const departmentsRemoved = new Set(comparison.changes.removed_departments || []);
            const functionsRemoved = new Set(comparison.changes.removed_functions || []);
            const lawsRemoved = new Set(comparison.changes.removed_laws || []);

            // Also integrate raw_entities from the amendment structure: if Neo4j created
            // nodes with added_by == amendment id and is_active != false, treat them
            // as added even if they didn't appear in the flattened change lists.
            // Also handle removed entities where is_active == false
            const amendId = comparison.amendment_gazette.id;
            (comparison.amendment_gazette.structure.raw_entities || []).forEach((ent: any) => {
              try {
                const props = ent.properties || {};
                const labels = ent.labels || [];
                const name = props.name || props.node_name || props.item_name || '';
                const isAdded = props.added_by && String(props.added_by) === String(amendId) && (props.is_active === undefined || props.is_active === true);
                const isRemoved = props.removed_by && String(props.removed_by) === String(amendId) && props.is_active === false;
                
                if (!isAdded && !isRemoved || !name) return;

                if (labels.some((l: string) => /Minister$/.test(l))) {
                  const numRaw = props.number && String(props.number) !== 'Unknown' ? String(props.number) : '';
                  const num = numRaw ? numRaw.padStart(2, '0') : '';
                  if (isAdded) {
                    ministersAdded.add(`${num}-${name}`);
                  } else if (isRemoved) {
                    // Handle removed ministers - not typically displayed but could be tracked
                  }
                } else if (labels.some((l: string) => /Department$/.test(l))) {
                  if (isAdded) {
                    departmentsAdded.add(name);
                  } else if (isRemoved) {
                    departmentsRemoved.add(name);
                  }
                } else if (labels.some((l: string) => /Function$/.test(l))) {
                  if (isAdded) {
                    functionsAdded.add(name);
                  } else if (isRemoved) {
                    functionsRemoved.add(name);
                  }
                } else if (labels.some((l: string) => /Law$/.test(l))) {
                  if (isAdded) {
                    lawsAdded.add(name);
                  } else if (isRemoved) {
                    lawsRemoved.add(name);
                  }
                }
              } catch (e) {
                // ignore malformed entity
              }
            });
            return renderGovernmentStructure(
              comparison.amendment_gazette.structure,
              `Amendment: ${comparison.amendment_gazette.id}`,
              {
                ministersAdded,
                ministersModified,
                departmentsAdded,
                functionsAdded,
                lawsAdded,
                departmentsRemoved,
                functionsRemoved,
                lawsRemoved,
              },
              ministerAlignmentMap
            );
          })()}
          </div>
        </div>
      </div>
    </div>
  );

  console.log("Gazette are:", gazettes);
  console.log("Amendments", amendments);

  const updatedGazettesAll = gazettes
    .filter((g) => g.labels.includes("BaseGazette")) // ← filters only BaseGazette
    .map((g) => ({
      ...g,
      president: presidentMapping[g.gazette_id] || "Unknown",
    }));

  // If a government is selected, filter base gazettes to only those matching the selected president
  const filteredGazettes = effectiveGovernment
    ? updatedGazettesAll.filter(
        (g) => g.president === govToPresidentName[effectiveGovernment]
      )
    : updatedGazettesAll;

  const updatedAmendments = amendments.map((g) => ({
    ...g,
    president: presidentMapping[g.gazette_id] || "Unknown",
  }));

  // Filter amendment gazettes by the effective government (context OR route param)
  const filteredAmendments = effectiveGovernment
    ? updatedAmendments.filter(
        (a) => a.president === govToPresidentName[effectiveGovernment]
      )
    : updatedAmendments;

  console.log("Updated Amendments:", updatedAmendments);

  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-800">
          Government Gazette Dashboard
        </h1>
        <p className="text-slate-600 mt-2">
          Track and analyze government structure changes through gazettes
        </p>
      </div>

      {/* Summary Cards */}
      {displaySummary && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-600">
                  Base Gazettes
                </p>
                <p className="text-2xl font-bold text-slate-900">
                  {displaySummary.counts.BaseGazette || 0}
                </p>
              </div>
              <div className="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <span className="text-2xl">📄</span>
              </div>
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-600">
                  Amendment Gazettes
                </p>
                <p className="text-2xl font-bold text-slate-900">
                  {displaySummary.counts.AmendmentGazette || 0}
                </p>
              </div>
              <div className="h-12 w-12 bg-green-100 rounded-lg flex items-center justify-center">
                <span className="text-2xl">📝</span>
              </div>
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-600">
                  Total Gazettes
                </p>
                <p className="text-2xl font-bold text-slate-900">
                  {(displaySummary.counts.BaseGazette || 0) +
                    (displaySummary.counts.AmendmentGazette || 0)}
                </p>
              </div>
              <div className="h-12 w-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <span className="text-2xl">📊</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Gazette Selection */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2 ">
              Select Base Gazette
            </label>
            <select
              value={selectedGazette?.gazette_id || ""}
              onChange={(e) => handleGazetteSelect(e.target.value)}
              className="w-full rounded-lg border-slate-300 text-sm cursor-pointer"
            >
              <option value="">Select a base gazette...</option>
              {filteredGazettes.map((g) => (
                <option key={g.gazette_id} value={g.gazette_id}>
                  {g.gazette_id} — {g.published_date || "N/A"} — {g.president}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Select Amendment Gazette
            </label>
            <select
              value={selectedAmendment?.gazette_id || ""}
              onChange={(e) => handleAmendmentSelect(e.target.value)}
              className="w-full max-w-full truncate rounded-lg border-slate-300 text-sm cursor-pointer"
            >
              <option value="">Select an amendment gazette...</option>
              {filteredAmendments.map((a) => (
                <option key={a.gazette_id} value={a.gazette_id}>
                  {a.gazette_id} — {a.published_date || "N/A"} — {a.president}
                </option>
              ))}
            </select>
          </div>
        </div>

        {selectedGazette && selectedAmendment && (
          <div className="mt-4 flex gap-3">
            <button
              onClick={() => setViewMode("structure")}
              className={`px-4 py-2 rounded-lg text-sm font-medium ${
                viewMode === "structure"
                  ? "bg-blue-600 text-white"
                  : "bg-slate-100 text-slate-700 hover:bg-slate-200"
              }`}
            >
              View Structure
            </button>
            <button
              onClick={handleCompare}
              className={`px-4 py-2 rounded-lg text-sm font-medium ${
                viewMode === "comparison"
                  ? "bg-green-600 text-white"
                  : "bg-slate-100 text-slate-700 hover:bg-slate-200"
              }`}
            >
              Compare Structures
            </button>
            <button
              onClick={() => setViewMode("amendment-tracker")}
              className={`px-4 py-2 rounded-lg text-sm font-medium ${
                viewMode === "amendment-tracker"
                  ? "bg-purple-600 text-white"
                  : "bg-slate-100 text-slate-700 hover:bg-slate-200"
              }`}
            >
              Enhanced Comparison
            </button>
            <button
              onClick={() => setViewMode("visualization")}
              className={`px-4 py-2 rounded-lg text-sm font-medium ${
                viewMode === "visualization"
                  ? "bg-indigo-600 text-white"
                  : "bg-slate-100 text-slate-700 hover:bg-slate-200"
              }`}
            >
              Interactive Visualization
            </button>
          </div>
        )}
      </div>

      {/* Main Content */}
      {viewMode === "structure" && selectedGazette && (
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
          {gazetteStructure ? (
            renderGovernmentStructure(
              gazetteStructure,
              `Government Structure: ${gazetteStructure.gazette_id}`
            )
          ) : (
            <div className="text-center py-8">
              <div className="text-slate-500 mb-4">
                {error ? (
                  <div className="text-red-600">
                    <p className="font-medium">Error loading structure</p>
                    <p className="text-sm">{error}</p>
                  </div>
                ) : (
                  <div>
                    <p className="font-medium">
                      No government structure data found
                    </p>
                    <p className="text-sm">
                      This gazette may not have any ministers, departments, or
                      laws defined in the database.
                    </p>
                  </div>
                )}
              </div>
              <div className="text-xs text-slate-400">
                Gazette ID: {selectedGazette.gazette_id} | Published:{" "}
                {selectedGazette.published_date}
              </div>
            </div>
          )}
        </div>
      )}

      {viewMode === "comparison" && comparison && (
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
          {renderComparison(comparison)}
        </div>
      )}

      {viewMode === "amendment-tracker" &&
        selectedGazette &&
        selectedAmendment && (
          <AmendmentTracker baseGazetteId={selectedGazette.gazette_id} />
        )}

      {viewMode === "visualization" && (
        <BaseGazetteVisualization gazetteId={selectedGazette?.gazette_id} />
      )}

      {/* Recent Gazettes */}
      {summary && summary.recent_gazettes.length > 0 && (
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
          <h2 className="text-xl font-semibold text-slate-800 mb-4">
            Recent Gazettes
          </h2>
          <div className="space-y-2">
            {summary.recent_gazettes.map((gazette, index) => (
              <div
                key={`${gazette.gazette_id}-${index}`}
                className="flex items-center justify-between py-2 px-3 bg-slate-50 rounded-lg"
              >
                <div>
                  <span className="font-medium text-slate-800">
                    {gazette.gazette_id}
                  </span>
                  <span className="text-sm text-slate-600 ml-2">
                    {gazette.gazette_id.includes("1897") ? "Base" : "Amendment"}
                  </span>
                </div>
                <div className="text-sm text-slate-600">
                  {gazette.published_date}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
