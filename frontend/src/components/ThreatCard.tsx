'use client'

import { AlertTriangle, ArrowRight, Shield } from 'lucide-react'
import clsx from 'clsx'

export interface Threat {
  id: string
  employee_id: string
  ml_anomaly_score: number
  threat_type: 'normal' | 'negligent' | 'suspicious' | 'malicious'
  created_at: string
  flagged: boolean
}

interface ThreatCardProps {
  threat: Threat
  employeeName: string
  onClick?: () => void
}

export default function ThreatCard({
  threat,
  employeeName,
  onClick,
}: ThreatCardProps) {
  const threatConfig = {
    normal: { color: 'bg-green-50', textColor: 'text-green-700', label: 'Normal' },
    negligent: { color: 'bg-yellow-50', textColor: 'text-yellow-700', label: 'Negligent' },
    suspicious: { color: 'bg-orange-50', textColor: 'text-orange-700', label: 'Suspicious' },
    malicious: { color: 'bg-red-50', textColor: 'text-red-700', label: 'Malicious' },
  }

  const config = threatConfig[threat.threat_type]
  const scoreColor = threat.ml_anomaly_score > 70 ? 'text-red-600' : threat.ml_anomaly_score > 40 ? 'text-yellow-600' : 'text-green-600'

  return (
    <div
      onClick={onClick}
      className={clsx(
        'bg-white rounded-lg p-4 border-l-4 cursor-pointer transition-all hover:shadow-md',
        threat.threat_type === 'malicious' ? 'border-l-red-500' : threat.threat_type === 'suspicious' ? 'border-l-yellow-500' : 'border-l-green-500'
      )}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-2">
            <h3 className="font-semibold text-gray-900">{employeeName}</h3>
            {threat.flagged && (
              <AlertTriangle size={16} className="text-red-500" />
            )}
          </div>
          <p className="text-sm text-gray-600 mt-1">ID: {threat.employee_id}</p>
          <div className="flex items-center space-x-4 mt-3">
            <div>
              <p className="text-xs text-gray-500">Risk Score</p>
              <p className={clsx('text-lg font-bold', scoreColor)}>
                {threat.ml_anomaly_score.toFixed(1)}
              </p>
            </div>
            <div>
              <span className={clsx('px-2 py-1 rounded text-xs font-semibold', config.color, config.textColor)}>
                {config.label}
              </span>
            </div>
          </div>
        </div>
        <ArrowRight size={20} className="text-gray-400 flex-shrink-0" />
      </div>
    </div>
  )
}
