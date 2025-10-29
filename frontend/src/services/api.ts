
import type { 
  Gazette, 
  GazetteDetail, 
  Amendment, 
  GraphData, 
  GazetteFullDetails 
} from '../types/gazette'

// Re-export types for convenience
export type { Gazette, GazetteDetail, Amendment, GraphData, GazetteFullDetails }

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:5001'
console.log('[API_URL]', API_URL)

export async function getGazettes(): Promise<Gazette[]> {
  const r = await fetch(`${API_URL}/gazettes`)
  if (!r.ok) throw new Error(`Failed /gazettes: ${r.status}`)
  return r.json()
}

export async function getGazetteDetails(gazetteId: string): Promise<GazetteDetail[]> {
  const r = await fetch(`${API_URL}/gazettes/${encodeURIComponent(gazetteId)}`)
  if (!r.ok) throw new Error(`Failed /gazettes/:id ${r.status}`)
  return r.json()
}

export async function getAmendments(): Promise<Amendment[]> {
  const r = await fetch(`${API_URL}/amendments`);
  if (!r.ok) throw new Error(`/amendments ${r.status}`);
  return r.json();
}

export async function getAmendmentGraph(id: string): Promise<GraphData> {
  const r = await fetch(`${API_URL}/amendments/${encodeURIComponent(id)}/graph`);
  if (!r.ok) throw new Error(`/amendments/:id/graph ${r.status}`);
  return r.json();
}

export async function getCompleteGraph(): Promise<GraphData> {
  const r = await fetch(`${API_URL}/graph/complete`);
  if (!r.ok) throw new Error(`/graph/complete ${r.status}`);
  return r.json();
}

export async function getGazetteFullDetails(gazetteId: string): Promise<GazetteFullDetails> {
  const r = await fetch(`${API_URL}/gazettes/${encodeURIComponent(gazetteId)}/details`);
  if (!r.ok) throw new Error(`/gazettes/:id/details ${r.status}`);
  return r.json();
}

export async function searchGazettes(query: string = '', type: 'all' | 'base' | 'amendment' = 'all'): Promise<Gazette[]> {
  const params = new URLSearchParams();
  if (query) params.append('q', query);
  if (type !== 'all') params.append('type', type);
  
  const r = await fetch(`${API_URL}/search?${params.toString()}`);
  if (!r.ok) throw new Error(`/search ${r.status}`);
  return r.json();
}

export interface DashboardSummary {
  counts: Record<string, number>;
  recent_gazettes: Gazette[];
}

export interface MinisterStructure {
  name: string;
  departments: string[];
  laws: string[];
}

export interface GazetteStructure {
  gazette_id: string;
  ministers: MinisterStructure[];
  departments: string[];
  laws: string[];
  raw_entities: any[];
}

export interface GazetteComparison {
  base_gazette: {
    id: string;
    structure: GazetteStructure;
    president: string;
    published_date: string;
  };
  amendment_gazette: {
    id: string;
    structure: GazetteStructure;
    president: string;
    published_date: string;
  };
  changes: {
    added_ministers: MinisterStructure[];
    removed_ministers: MinisterStructure[];
    modified_ministers: any[];
    added_departments: string[];
    removed_departments: string[];
    added_laws: string[];
    removed_laws: string[];
  };
}

export async function getDashboardSummary(): Promise<DashboardSummary> {
  const r = await fetch(`${API_URL}/dashboard/summary`);
  if (!r.ok) throw new Error(`/dashboard/summary ${r.status}`);
  return r.json();
}

export async function getGazetteStructure(gazetteId: string): Promise<GazetteStructure> {
  const r = await fetch(`${API_URL}/gazettes/${encodeURIComponent(gazetteId)}/structure`);
  if (!r.ok) throw new Error(`/gazettes/:id/structure ${r.status}`);
  return r.json();
}


export interface GovernmentEvolution {
  evolution: Array<{
    gazette: {
      id: string;
      published_date: string;
      type: 'base' | 'amendment';
      parent_gazette_id?: string;
    };
    structure: {
      ministers: MinisterStructure[];
      departments: string[];
      laws: string[];
    };
  }>;
  total_gazettes: number;
}

export interface GovernmentEvolutionFromBase extends GovernmentEvolution {
  base_gazette: string;
  changes: Array<{
    from_gazette: string;
    to_gazette: string;
    added_ministers: MinisterStructure[];
    removed_ministers: MinisterStructure[];
    modified_ministers: Array<{
      name: string;
      departments_added: string[];
      departments_removed: string[];
    }>;
    added_departments: string[];
    removed_departments: string[];
    added_laws: string[];
    removed_laws: string[];
  }>;
}

export async function getGovernmentStructureEvolution(): Promise<GovernmentEvolution> {
  const r = await fetch(`${API_URL}/network/government-evolution`);
  if (!r.ok) throw new Error(`/network/government-evolution ${r.status}`);
  return r.json();
}

export async function getGovernmentEvolutionFromBase(baseId: string): Promise<GovernmentEvolutionFromBase> {
  const r = await fetch(`${API_URL}/network/government-evolution/${encodeURIComponent(baseId)}`);
  if (!r.ok) throw new Error(`/network/government-evolution/:id ${r.status}`);
  return r.json();
}

export async function compareGazetteStructures(baseId: string, amendmentId: string): Promise<GazetteComparison> {
  const r = await fetch(`${API_URL}/gazettes/${encodeURIComponent(baseId)}/compare/${encodeURIComponent(amendmentId)}`);
  if (!r.ok) throw new Error(`/gazettes/:id/compare ${r.status}`);
  return r.json();
}

export async function debugDatabaseStructure(): Promise<any> {
  const r = await fetch(`${API_URL}/debug/database-structure`);
  if (!r.ok) throw new Error(`/debug/database-structure ${r.status}`);
  return r.json();
}
