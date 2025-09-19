import { createContext, useContext, useState, ReactNode } from 'react'

interface GovernmentContextType {
  selectedGovernment: string | null
  setSelectedGovernment: (government: string | null) => void
  governmentInfo: {
    name: string
    period: string
    color: string
  } | null
}

const GovernmentContext = createContext<GovernmentContextType | undefined>(undefined)

const governmentData = {
  maithripala: {
    name: 'Maithripala Sirisena',
    period: '2015-2019',
    color: 'from-blue-500 to-blue-700'
  },
  gotabaya: {
    name: 'Gotabaya Rajapaksa',
    period: '2019-2022',
    color: 'from-green-500 to-green-700'
  },
  ranil: {
    name: 'Ranil Wickramasinghe',
    period: '2022-2024',
    color: 'from-purple-500 to-purple-700'
  },
  anura: {
    name: 'Anura Kumara Dissanayaka',
    period: '2024-Present',
    color: 'from-orange-500 to-orange-700'
  }
}

interface GovernmentProviderProps {
  children: ReactNode
}

export function GovernmentProvider({ children }: GovernmentProviderProps) {
  const [selectedGovernment, setSelectedGovernment] = useState<string | null>(null)

  const governmentInfo = selectedGovernment 
    ? governmentData[selectedGovernment as keyof typeof governmentData] || null
    : null

  return (
    <GovernmentContext.Provider value={{
      selectedGovernment,
      setSelectedGovernment,
      governmentInfo
    }}>
      {children}
    </GovernmentContext.Provider>
  )
}

export function useGovernment() {
  const context = useContext(GovernmentContext)
  if (context === undefined) {
    throw new Error('useGovernment must be used within a GovernmentProvider')
  }
  return context
}

