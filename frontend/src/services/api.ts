
import type { 
  Gazette, 
  GazetteDetail, 
  Amendment, 
  GraphData, 
  GazetteFullDetails 
} from '../types/gazette'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:5001'
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
