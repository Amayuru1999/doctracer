import { useGovernment } from '../contexts/GovernmentContext'

export default function GovernmentBanner() {
  const { governmentInfo } = useGovernment()

  if (!governmentInfo) {
    return null
  }

  return (
    <div className={`bg-gradient-to-r ${governmentInfo.color} text-white p-4 rounded-lg shadow-lg mb-6`}>
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold">{governmentInfo.name}</h2>
          <p className="text-white/80">Presidential Period: {governmentInfo.period}</p>
        </div>
        <div className="text-right">
          <p className="text-sm text-white/80">Current Government</p>
          <p className="text-lg font-semibold">Active</p>
        </div>
      </div>
    </div>
  )
}

