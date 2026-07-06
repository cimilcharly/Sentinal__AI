'use client'

import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/store/auth'
import Navbar from '@/components/Navbar'
import Sidebar from '@/components/Sidebar'
import { useState, useEffect } from 'react'
import { apiClient } from '@/lib/api'
import { Settings, Plus, Trash2, AlertCircle } from 'lucide-react'

interface Integration {
  id: string
  integration_type: string
  name: string
  is_active: boolean
  last_sync?: string
}

export default function SettingsPage() {
  const router = useRouter()
  const { user, isAuthenticated } = useAuthStore()
  const [integrations, setIntegrations] = useState<Integration[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddForm, setShowAddForm] = useState(false)
  const [selectedType, setSelectedType] = useState('office365')
  const [credentials, setCredentials] = useState<Record<string, string>>({})

  useEffect(() => {
    if (!isAuthenticated || user?.role !== 'admin') {
      router.push('/dashboard')
      return
    }

    const fetchIntegrations = async () => {
      try {
        const response = await apiClient.listIntegrations()
        if (response.data) {
          setIntegrations(Array.isArray(response.data) ? response.data : [])
        }
      } catch (err) {
        console.error('Failed to fetch integrations:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchIntegrations()
  }, [isAuthenticated, user?.role, router])

  const handleAddIntegration = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      const response = await apiClient.createIntegration(
        selectedType,
        `${selectedType} Integration`,
        credentials
      )

      if (response.data && !response.error) {
        setIntegrations([...integrations, response.data as Integration])
        setShowAddForm(false)
        setSelectedType('office365')
        setCredentials({})
      }
    } catch (err) {
      console.error('Failed to create integration:', err)
    }
  }

  const handleTestIntegration = async (integrationId: string) => {
    try {
      const response = await apiClient.testIntegration(integrationId)
      if (!response.error) {
        alert('Integration test successful!')
      } else {
        alert('Integration test failed: ' + response.error)
      }
    } catch (err) {
      alert('Error testing integration')
    }
  }

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />

      <div className="flex-1 ml-64 flex flex-col">
        <Navbar />

        <main className="flex-1 overflow-auto">
          <div className="max-w-4xl mx-auto px-6 py-8">
            {/* Header */}
            <div className="mb-8">
              <div className="flex items-center space-x-3 mb-2">
                <Settings size={32} className="text-blue-500" />
                <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
              </div>
              <p className="text-gray-600">Admin only - Manage integrations and configuration</p>
            </div>

            {/* Integrations Section */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-gray-900">Data Integrations</h2>
                <button
                  onClick={() => setShowAddForm(!showAddForm)}
                  className="flex items-center space-x-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 font-semibold"
                >
                  <Plus size={20} />
                  <span>Add Integration</span>
                </button>
              </div>

              {/* Add Integration Form */}
              {showAddForm && (
                <form onSubmit={handleAddIntegration} className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Integration Type
                      </label>
                      <select
                        value={selectedType}
                        onChange={(e) => setSelectedType(e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                      >
                        <option value="office365">Office365</option>
                        <option value="splunk">Splunk</option>
                        <option value="active_directory">Active Directory</option>
                        <option value="aws">AWS CloudTrail</option>
                      </select>
                    </div>

                    {/* Dynamic credential fields */}
                    {selectedType === 'office365' && (
                      <>
                        <input
                          type="text"
                          placeholder="Client ID"
                          onChange={(e) => setCredentials({ ...credentials, client_id: e.target.value })}
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                        />
                        <input
                          type="password"
                          placeholder="Client Secret"
                          onChange={(e) => setCredentials({ ...credentials, client_secret: e.target.value })}
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                        />
                      </>
                    )}

                    {selectedType === 'splunk' && (
                      <>
                        <input
                          type="text"
                          placeholder="Host (https://splunk.example.com)"
                          onChange={(e) => setCredentials({ ...credentials, host: e.target.value })}
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                        />
                        <input
                          type="text"
                          placeholder="Username"
                          onChange={(e) => setCredentials({ ...credentials, username: e.target.value })}
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                        />
                        <input
                          type="password"
                          placeholder="Password"
                          onChange={(e) => setCredentials({ ...credentials, password: e.target.value })}
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                        />
                      </>
                    )}

                    <div className="flex space-x-2">
                      <button
                        type="submit"
                        className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 font-semibold"
                      >
                        Add Integration
                      </button>
                      <button
                        type="button"
                        onClick={() => setShowAddForm(false)}
                        className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                </form>
              )}

              {/* Integrations List */}
              {!loading ? (
                <div className="space-y-4">
                  {integrations.length > 0 ? (
                    integrations.map((integration) => (
                      <div key={integration.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition">
                        <div className="flex-1">
                          <h3 className="font-semibold text-gray-900">{integration.name}</h3>
                          <p className="text-sm text-gray-600">Type: {integration.integration_type}</p>
                          <p className="text-xs text-gray-500 mt-1">
                            {integration.is_active ? '✅ Active' : '⏸️ Inactive'}
                          </p>
                        </div>

                        <div className="flex space-x-2">
                          <button
                            onClick={() => handleTestIntegration(integration.id)}
                            className="px-4 py-2 text-blue-600 hover:bg-blue-50 rounded-lg font-semibold"
                          >
                            Test
                          </button>
                          <button className="px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg">
                            <Trash2 size={18} />
                          </button>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="p-8 text-center border border-dashed border-gray-300 rounded-lg">
                      <AlertCircle className="mx-auto text-gray-400 mb-3" size={40} />
                      <p className="text-gray-600">No integrations configured yet</p>
                      <p className="text-gray-500 text-sm mt-1">Add your first integration to start collecting data</p>
                    </div>
                  )}
                </div>
              ) : (
                <div className="flex items-center justify-center h-40">
                  <p className="text-gray-600">Loading integrations...</p>
                </div>
              )}
            </div>

            {/* Documentation */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h3 className="font-semibold text-blue-900 mb-2">Supported Integrations</h3>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>✅ Office365 - Email and collaboration monitoring</li>
                <li>✅ Splunk - SIEM event ingestion</li>
                <li>✅ Active Directory - User and group changes</li>
                <li>✅ AWS CloudTrail - Cloud activity logging</li>
                <li>✅ Okta - Identity event monitoring</li>
              </ul>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
