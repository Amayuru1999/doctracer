import type {Gazette, GazetteDetail} from "../types/gazette.ts";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:5001";

export async function getGazettes(): Promise<Gazette[]> {
  const res = await fetch(`${API_URL}/gazettes`);
  if (!res.ok) throw new Error("Failed to fetch gazettes");
  return res.json();
}

export async function getGazetteDetails(gazetteId: string): Promise<GazetteDetail[]> {
  const res = await fetch(`${API_URL}/gazettes/${encodeURIComponent(gazetteId)}`);
  if (!res.ok) throw new Error("Failed to fetch gazette details");
  return res.json();
}
