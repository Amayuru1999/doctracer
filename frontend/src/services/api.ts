
import type { Gazette, GazetteDetail } from '../types/gazette'

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
export interface Amendment {
  gazette_id: string;
  published_date: string;
  parent_gazette_id?: string;
}

export interface GraphPayload {
  nodes: { id: string; label: string; kind: string }[];
  links: { source: string; target: string; kind: string }[];
}

export async function getAmendments(): Promise<Amendment[]> {
  const r = await fetch(`${API_URL}/amendments`);
  if (!r.ok) throw new Error(`/amendments ${r.status}`);
  return r.json();
}

export async function getAmendmentGraph(id: string): Promise<GraphPayload> {
  const r = await fetch(`${API_URL}/amendments/${encodeURIComponent(id)}/graph`);
  if (!r.ok) throw new Error(`/amendments/:id/graph ${r.status}`);
  return r.json();
}
