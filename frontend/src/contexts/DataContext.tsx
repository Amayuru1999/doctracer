import React, { createContext, useContext, useEffect, useMemo, useState } from "react";
import type { Gazette, GazetteDetail } from "../types/gazette";
import { getGazettes, getGazetteDetails } from "../services/api";

type State = {
  gazettes: Gazette[];
  loading: boolean;
  error?: string;
  selectedGazetteId?: string;
  details: GazetteDetail[]; // ministers + deps + laws + functions for selected gazette
  setSelectedGazetteId: (id?: string) => void;
  refresh: () => Promise<void>;
};

const DataCtx = createContext<State | undefined>(undefined);

export const DataProvider: React.FC<React.PropsWithChildren> = ({ children }) => {
  const [gazettes, setGazettes] = useState<Gazette[]>([]);
  const [details, setDetails] = useState<GazetteDetail[]>([]);
  const [selectedGazetteId, setSelectedGazetteId] = useState<string | undefined>();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();

  const refresh = async () => {
    try {
      setLoading(true);
      setError(undefined);
      const list = await getGazettes();
      setGazettes(list);
      // default select latest (by date)
      const latest = list
        .slice()
        .sort((a, b) => a.published_date.localeCompare(b.published_date))
        .at(-1);
      const idToUse = selectedGazetteId ?? latest?.gazette_id;
      setSelectedGazetteId(idToUse);
      if (idToUse) {
        const d = await getGazetteDetails(idToUse);
        setDetails(d);
      } else {
        setDetails([]);
      }
    } catch (e: any) {
      setError(e?.message ?? "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  // initial load
  useEffect(() => { void refresh(); /* eslint-disable-line */ }, []);

  // reload details when selection changes
  useEffect(() => {
    (async () => {
      if (!selectedGazetteId) return;
      try {
        setLoading(true);
        const d = await getGazetteDetails(selectedGazetteId);
        setDetails(d);
      } catch (e: any) {
        setError(e?.message ?? "Unknown error");
      } finally {
        setLoading(false);
      }
    })();
  }, [selectedGazetteId]);

  const value = useMemo<State>(() => ({
    gazettes, loading, error,
    selectedGazetteId, setSelectedGazetteId,
    details, refresh,
  }), [gazettes, loading, error, selectedGazetteId, details]);

  return <DataCtx.Provider value={value}>{children}</DataCtx.Provider>;
};

export function useData() {
  const ctx = useContext(DataCtx);
  if (!ctx) throw new Error("useData must be used within DataProvider");
  return ctx;
}
