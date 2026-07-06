'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/store/auth'
import { apiClient } from '@/lib/api'
import Navbar from '@/components/Navbar'
import Sidebar from '@/components/Sidebar'
import StatCard from '@/components/StatCard'
import ThreatCard, { Threat } from '@/components/ThreatCard'
import { AlertTriangle, Users, TrendingUp, Shield } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

export default function DashboardPage() {
  const router = useRouter()
  const { user, isAuthenticated } = useAuthStore()
  const [threats, setThreats] = useState<Threat[]>([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({
    totalThreats: 0,
    flaggedThreats: 0,
    avgRiskScore: 0,
    monitoredEmployees: 0,
  })

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login')
      return
    }

    const fetchData = async () => {
      try {
        const response = await apiClient.getAssessments(7, false)
        if (response.data) {
          const threatsList = Array.isArray(response.data) ? response.data : []
          setThreats(threatsList)

          // Calculate stats
          const flagged = threatsList.filter((t: Threat) => t.flagged).length
          const avgScore = threatsList.length > 0
            ? (threatsList.reduce((sum: number, t: Threat) => sum + t.ml_anomaly_score, 0) / threatsList.length).toFixed(1)
            : 0

          setStats({
            totalThreats: threatsList.length,
            flaggedThreats: flagged,
            avgRiskScore: parseFloat(avgScore as string),
            monitoredEmployees: new Set(threatsList.map((t: Threat) => t.employee_id)).size,
          })
        }
      } catch (err) {
        console.error('Failed to fetch assessments:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [isAuthenticated, router])

  // Chart data
  const threatDistribution = [
    { name: 'Normal', value: threats.filter(t => t.threat_type === 'normal').length, fill: '#10b981' },
    { name: 'Negligent', value: threats.filter(t => t.threat_type === 'negligent').length, fill: '#f59e0b' },
    { name: 'Suspicious', value: threats.filter(t => t.threat_type === 'suspicious').length, fill: '#ef6644' },
    { name: 'Malicious', value: threats.filter(t => t.threat_type === 'malicious').length, fill: '#ef4444' },
  ]

  const riskTrend = [
    { name: 'Mon', risk: 42 },
    { name: 'Tue', risk: 45 },
    { name: 'Wed', risk: 38 },
    { name: 'Thu', risk: 51 },
    { name: 'Fri', risk: 48 },
    { name: 'Sat', risk: 52 },
    { name: 'Sun', risk: 55 },
  ]

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <Sidebar />

      {/* Main content */}
      <div className="flex-1 ml-64 flex flex-col">
        {/* Navbar */}
        <Navbar />

        {/* Content */}
        <main className="flex-1 overflow-auto">
          <div className="max-w-7xl mx-auto px-6 py-8">
            {/* Header */}
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
              <p className="text-gray-600 mt-1">Welcome back, {user?.full_name}!</p>
            </div>

            {/* Stats grid */}
            {!loading && (
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                  <StatCard
                    title="Total Assessments"
                    value={stats.totalThreats}
                    icon={Users}
                    color="blue"
                  />
                  <StatCard
                    title="Flagged Threats"
                    value={stats.flaggedThreats}
                    icon={AlertTriangle}
                    trend={{ value: 12, direction: 'up' }}
                    color="red"
                  />
                  <StatCard
                    title="Average Risk Score"
                    value={stats.avgRiskScore.toFixed(1)}
                    icon={TrendingUp}
                    color="yellow"
                  />
                  <StatCard
                    title="Monitored Employees"
                    value={stats.monitoredEmployees}
                    icon={Shield}
                    color="green"
                  />
                </div>

                {/* Charts row */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                  {/* Risk Trend */}
                  <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
                    <h2 className="text-lg font-semibold text-gray-900 mb-4">Risk Trend (7 Days)</h2>
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={riskTrend}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                        <XAxis dataKey="name" stroke="#6b7280" />
                        <YAxis stroke="#6b7280" />
                        <Tooltip contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb' }} />
                        <Bar dataKey="risk" fill="#3b82f6" radius={[8, 8, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>

                  {/* Threat Distribution */}
                  <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
                    <h2 className="text-lg font-semibold text-gray-900 mb-4">Threat Distribution</h2>
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                        <Pie data={threatDistribution} cx="50%" cy="50%" labelLine={false} label={({ name, value }) => `${name}: ${value}`} outerRadius={80} fill="#8884d8" dataKey="value">
                          {threatDistribution.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.fill} />
                          ))}
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Recent Threats */}
                <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
                  <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Assessments</h2>
                  {threats.length > 0 ? (
                    <div className="space-y-3 max-h-96 overflow-y-auto">
                      {threats.slice(0, 5).map((threat, idx) => (
                        <ThreatCard
                          key={threat.id}
                          threat={threat}
                          employeeName={`Employee ${threat.employee_id}`}
                          onClick={() => router.push(`/threats/${threat.employee_id}`)}
                        />
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-600 text-center py-8">No threat assessments found</p>
                  )}
                </div>
              </>
            )}

            {loading && (
              <div className="flex items-center justify-center h-64">
                <div className="text-center">
                  <div className="spinner w-8 h-8 border-4 border-blue-200 border-t-blue-500 rounded-full mx-auto mb-3"></div>
                  <p className="text-gray-600">Loading dashboard...</p>
                </div>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  )
}
