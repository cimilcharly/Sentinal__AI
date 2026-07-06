'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/store/auth'
import { apiClient } from '@/lib/api'
import Navbar from '@/components/Navbar'
import Sidebar from '@/components/Sidebar'
import { FileText, Download, Send, Plus } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'

interface Report {
  id: string
  report_type: string
  title: string
  created_at: string
  is_sent: boolean
}

export default function ReportsPage() {
  const router = useRouter()
  const { isAuthenticated } = useAuthStore()
  const [reports, setReports] = useState<Report[]>([])
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [reportTitle, setReportTitle] = useState('')
  const [reportType, setReportType] = useState('weekly')

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login')
      return
    }

    const fetchReports = async () => {
      try {
        const response = await apiClient.getReports(20)
        if (response.data) {
          setReports(Array.isArray(response.data) ? response.data : [])
        }
      } catch (err) {
        console.error('Failed to fetch reports:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchReports()
  }, [isAuthenticated, router])

  const handleGenerateReport = async (e: React.FormEvent) => {
    e.preventDefault()
    setGenerating(true)

    try {
      const response = await apiClient.generateReport(reportType, reportTitle || `${reportType} Report`, 30)
      if (response.data && !response.error) {
        setReports([response.data as Report, ...reports])
        setReportTitle('')
        setReportType('weekly')
      }
    } catch (err) {
      console.error('Failed to generate report:', err)
    } finally {
      setGenerating(false)
    }
  }

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />

      <div className="flex-1 ml-64 flex flex-col">
        <Navbar />

        <main className="flex-1 overflow-auto">
          <div className="max-w-6xl mx-auto px-6 py-8">
            {/* Header */}
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-900">Security Reports</h1>
              <p className="text-gray-600 mt-1">Generate and manage threat assessment reports</p>
            </div>

            {/* Generate report form */}
            <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200 mb-8">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Generate New Report</h2>
              <form onSubmit={handleGenerateReport} className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <input
                    type="text"
                    placeholder="Report title (optional)"
                    value={reportTitle}
                    onChange={(e) => setReportTitle(e.target.value)}
                    className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                  />
                  <select
                    value={reportType}
                    onChange={(e) => setReportType(e.target.value)}
                    className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                  >
                    <option value="daily">Daily Report</option>
                    <option value="weekly">Weekly Report</option>
                    <option value="monthly">Monthly Report</option>
                    <option value="custom">Custom Report</option>
                  </select>
                  <button
                    type="submit"
                    disabled={generating}
                    className="flex items-center justify-center space-x-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-400 transition font-semibold"
                  >
                    <Plus size={20} />
                    <span>{generating ? 'Generating...' : 'Generate'}</span>
                  </button>
                </div>
              </form>
            </div>

            {/* Reports list */}
            {!loading ? (
              <div className="space-y-4">
                {reports.length > 0 ? (
                  reports.map((report) => (
                    <div key={report.id} className="bg-white rounded-lg shadow-sm p-6 border border-gray-200 hover:shadow-md transition">
                      <div className="flex items-start justify-between">
                        <div className="flex items-start space-x-4 flex-1">
                          <div className="p-3 bg-blue-50 rounded-lg">
                            <FileText className="text-blue-500" size={24} />
                          </div>
                          <div className="flex-1">
                            <h3 className="font-semibold text-gray-900">{report.title}</h3>
                            <p className="text-sm text-gray-600 mt-1">
                              {report.report_type.charAt(0).toUpperCase() + report.report_type.slice(1)} Report
                            </p>
                            <p className="text-xs text-gray-500 mt-2">
                              Generated {formatDistanceToNow(new Date(report.created_at), { addSuffix: true })}
                            </p>
                          </div>
                        </div>

                        {/* Actions */}
                        <div className="flex items-center space-x-2">
                          <button className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition" title="Download">
                            <Download size={20} />
                          </button>
                          {!report.is_sent && (
                            <button className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition" title="Send">
                              <Send size={20} />
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="bg-white rounded-lg p-12 text-center border border-gray-200">
                    <FileText className="mx-auto text-gray-400 mb-3" size={40} />
                    <p className="text-gray-600 text-lg">No reports generated yet</p>
                    <p className="text-gray-500 text-sm mt-1">Generate your first report to get started</p>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center justify-center h-64">
                <div className="text-center">
                  <div className="spinner w-8 h-8 border-4 border-blue-200 border-t-blue-500 rounded-full mx-auto mb-3"></div>
                  <p className="text-gray-600">Loading reports...</p>
                </div>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  )
}
