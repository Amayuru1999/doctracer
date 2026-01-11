import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useGovernment } from '../contexts/GovernmentContext'

interface President {
  id: string
  name: string
  fullName: string
  period: string
  image: string
  description: string
  color: string
  available: boolean
}

const presidents: President[] = [
  {
    id: 'maithripala',
    name: 'Maithripala Sirisena',
    fullName: 'Maithripala Sirisena',
    period: '2015-2019',
    image: '/presidents/maithripala.png',
    description: '7th President of Sri Lanka',
    color: 'from-blue-500 to-blue-700',
    available: true
  },
  {
    id: 'gotabaya',
    name: 'Gotabaya Rajapaksa',
    fullName: 'Gotabaya Rajapaksa',
    period: '2019-2022',
    image: '/presidents/gotabaya.png',
    description: '8th President of Sri Lanka',
    color: 'from-green-500 to-green-700',
    available: true
  },
  {
    id: 'ranil',
    name: 'Ranil Wickramasinghe',
    fullName: 'Ranil Wickramasinghe',
    period: '2022-2024',
    image: '/presidents/ranil.png',
    description: '9th President of Sri Lanka',
    color: 'from-purple-500 to-purple-700',
    available: true
  },
  {
    id: 'anura',
    name: 'Anura Kumara Dissanayaka',
    fullName: 'Anura Kumara Dissanayaka',
    period: '2024-Present',
    image: '/presidents/anura.png',
    description: '10th President of Sri Lanka',
    color: 'from-orange-500 to-orange-700',
    available: true
  }
]

export default function GovernmentSelection() {
  const [selectedPresident, setSelectedPresident] = useState<string | null>(null)
  const navigate = useNavigate()
  const { setSelectedGovernment } = useGovernment()

  const handleSelection = (presidentId: string) => {
    setSelectedPresident(presidentId)
    setSelectedGovernment(presidentId)
    // Navigate to the main dashboard with the selected government
    navigate(`/${presidentId}/dashboard`)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800">
      {/* Header */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 to-purple-600/20"></div>
        <div className="relative max-w-7xl mx-auto px-4 py-16">
          <div className="text-center">
            <div className="inline-flex items-center gap-3 mb-6">
              <div className="h-16 w-16 rounded-2xl bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center text-white font-bold text-2xl shadow-2xl">
                🇱🇰
              </div>
              <div>
                <h1 className="text-4xl font-bold text-white mb-2">DocTracer</h1>
                <p className="text-blue-200 text-lg">Sri Lanka Government Structure Tracker</p>
              </div>
            </div>
            <h2 className="text-3xl font-bold text-white mb-4">Select Government Period</h2>
            <p className="text-xl text-blue-100 max-w-3xl mx-auto">
              Choose a presidential period to explore government structure changes, 
              gazette amendments, and policy evolution during that era.
            </p>
          </div>
        </div>
      </div>

      {/* Presidents Grid */}
      <div className="max-w-7xl mx-auto px-4 pb-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {presidents.map((president) => (
            <div
              key={president.id}
              className={`group relative overflow-hidden rounded-2xl shadow-2xl transition-all duration-300 transform hover:scale-105 ${
                president.available 
                  ? 'cursor-pointer hover:shadow-3xl' 
                  : 'cursor-not-allowed opacity-60'
              }`}
              onClick={() => president.available && handleSelection(president.id)}
            >
              {/* Background Gradient */}
              <div className={`absolute inset-0 bg-gradient-to-br ${president.color} opacity-90`}></div>
              
              {/* President Image */}
              <div className="relative h-64 flex items-center justify-center">
                <div className="w-32 h-32 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center shadow-2xl overflow-hidden">
                  <img 
                    src={president.image} 
                    alt={president.name}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      const target = e.target as HTMLImageElement;
                      target.style.display = 'none';
                      target.nextElementSibling?.classList.remove('hidden');
                    }}
                  />
                  <div className="sm:hidden w-full h-full flex items-center justify-center text-4xl font-bold text-white">
                    {president.name.split(' ').map(n => n[0]).join('')}
                  </div>
                </div>
                {!president.available && (
                  <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
                    <span className="bg-red-500 text-white px-4 py-2 rounded-full text-sm font-semibold">
                      Coming Soon
                    </span>
                  </div>
                )}
              </div>

              {/* Content */}
              <div className="relative p-6 text-white">
                <h3 className="text-xl font-bold mb-2">{president.name}</h3>
                <p className="text-sm text-white/80 mb-2">{president.description}</p>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium bg-white/20 px-3 py-1 rounded-full">
                    {president.period}
                  </span>
                  {president.available && (
                    <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center group-hover:bg-white/30 transition-colors">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </div>
                  )}
                </div>
              </div>

              {/* Hover Effect */}
              {president.available && (
                <div className="absolute inset-0 bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              )}
            </div>
          ))}
        </div>

        {/* Additional Info */}
        <div className="mt-16 text-center">
          <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 max-w-4xl mx-auto">
            <h3 className="text-2xl font-bold text-white mb-4">About DocTracer</h3>
            <p className="text-blue-100 text-lg leading-relaxed">
              DocTracer provides comprehensive insights into Sri Lankan government structure changes 
              across different presidential periods. Track ministry reorganizations, department changes, 
              and policy evolution through interactive visualizations and detailed analytics.
            </p>
            <div className="mt-6 flex flex-wrap justify-center gap-4">
              <div className="flex items-center gap-2 text-white/80">
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                <span>Available</span>
              </div>
              <div className="flex items-center gap-2 text-white/80">
                <div className="w-2 h-2 bg-red-400 rounded-full"></div>
                <span>Coming Soon</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
