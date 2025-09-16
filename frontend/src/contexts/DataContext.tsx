
import React, { createContext, useContext, useEffect, useMemo, useState } from 'react'
import type { Gazette, GazetteDetail } from '../types/gazette'
import { getGazettes, getGazetteDetails } from '../services/api'

type State = {
  gazettes: Gazette[]
  selectedGazetteId?: string
  setSelectedGazetteId: (id?: string) => void
  details: GazetteDetail[]
  loading: boolean
  error?: string
  refresh: () => Promise<void>
}

const Ctx = createContext<State | undefined>(undefined)

export const DataProvider: React.FC<React.PropsWithChildren> = ({ children }) => {
  const [gazettes, setGazettes] = useState<Gazette[]>([])
  const [selectedGazetteId, setSelectedGazetteId] = useState<string | undefined>()
  const [details, setDetails] = useState<GazetteDetail[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string>()

  const loadDetails = async (id?: string) => {
    if (!id) { setDetails([]); return }
    const d = await getGazetteDetails(id)
    setDetails(d)
  }

  const refresh = async () => {
    try {
      setLoading(true)
      setError(undefined)
      const gs = await getGazettes()
      setGazettes(gs)
      const first = gs[0]?.gazette_id
      const id = selectedGazetteId ?? first
      setSelectedGazetteId(id)
      await loadDetails(id)
    } catch (e: any) {
      setError(e?.message ?? String(e))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { refresh() }, [])
  useEffect(() => { if (selectedGazetteId) loadDetails(selectedGazetteId) }, [selectedGazetteId])

  const value = useMemo<State>(() => ({
    gazettes, selectedGazetteId, setSelectedGazetteId, details, loading, error, refresh
  }), [gazettes, selectedGazetteId, details, loading, error])

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>
}

export const useData = () => {
  const v = useContext(Ctx)
  if (!v) throw new Error('useData must be used within DataProvider')
  return v
}
