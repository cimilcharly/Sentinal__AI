'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/store/auth'
import { apiClient } from '@/lib/api'
import Navbar from '@/components/Navbar'
import Sidebar from '@/components/Sidebar'
import ThreatCard, { Threat } from '@/components/ThreatCard'
import { Search, Filter } from 'lucide-react'

export default function ThreatsPage() {
  const router = useRouter()
  const { isAuthenticated } = useAuthStore()
  const [threats, setThreats] = useState<Threat[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterType, setFilterType] = useState<'all' | 'flagged' | 'malicious' | 'suspicious' | 'negligent'>('all')

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login')
      return
    }

    const fetchThreats = async () => {
      try {
        const response = await apiClient.getAssessments(30, filterType === 'flagged')
        if (response.data) {
          setThreats(Array.isArray(response.data) ? response.data : [])
        }
      } catch (err) {
        console.error('Failed to fetch threats:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchThreats()
  }, [isAuthenticated, router, filterType])

  const filteredThreats = threats.filter((threat) => {
    const matchesSearch = threat.employee_id.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesType = filterType === 'all' || threat.threat_type === filterType
    return matchesSearch && matchesType
  })

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />

      <div className="flex-1 ml-64 flex flex-col">
        <Navbar />

        <main className="flex-1 overflow-auto">
          <div className="max-w-6xl mx-auto px-6 py-8">
            {/* Header */}
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-900">Threat Assessments</h1>
              <p className="text-gray-600 mt-1">Monitor and analyze employee threat classifications</p>
            </div>

            {/* Search and filters */}
            <div className="mb-6 space-y-4">
              <div className="flex flex-col sm:flex-row gap-4">
                {/* Search */}
                <div className="flex-1 relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
                  <input
                    type="text"
                    placeholder="Search by employee ID..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                  />
                </div>

                {/* Filter */}
                <div className="flex items-center space-x-2">
                  <Filter size={20} className="text-gray-400" />
                  <select
                    value={filterType}
                    onChange={(e) => setFilterType(e.target.value as any)}
                    className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                  >
                    <option value="all">All Threats</option>
                    <option value="flagged">Flagged Only</option>
                    <option value="malicious">Malicious</option>
                    <option value="suspicious">Suspicious</option>
                    <option value="negligent">Negligent</option>
                  </select>
                </div>
              </div>

              {/* Results count */}
              <p className="text-sm text-gray-600">
                Showing {filteredThreats.length} of {threats.length} assessments
              </p>
            </div>

            {/* Threats list */}
            {!loading ? (
              <div className="space-y-4">
                {filteredThreats.length > 0 ? (
                  filteredThreats.map((threat) => (
                    <ThreatCard
                      key={threat.id}
                      threat={threat}
                      employeeName={`Employee ${threat.employee_id}`}
                      onClick={() => router.push(`/threats/${threat.employee_id}`)}
                    />
                  ))
                ) : (
                  <div className="bg-white rounded-lg p-12 text-center border border-gray-200">
                    <p className="text-gray-600 text-lg">No threats found matching your criteria</p>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center justify-center h-64">
                <div className="text-center">
                  <div className="spinner w-8 h-8 border-4 border-blue-200 border-t-blue-500 rounded-full mx-auto mb-3"></div>
                  <p className="text-gray-600">Loading threats...</p>
                </div>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  )
}
