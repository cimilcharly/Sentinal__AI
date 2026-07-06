'use client'

import { useAuthStore } from '@/store/auth'
import { LogOut, Settings, User } from 'lucide-react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

export default function Navbar() {
  const { user, logout } = useAuthStore()
  const router = useRouter()

  const handleLogout = () => {
    logout()
    router.push('/login')
  }

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link href="/dashboard" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold">🛡️</span>
            </div>
            <span className="text-xl font-bold text-gray-900">Sentinel AI</span>
          </Link>

          {/* Right side */}
          {user && (
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">{user.full_name}</span>
              <div className="relative group">
                <button className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg">
                  <User size={20} />
                </button>
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none group-hover:pointer-events-auto">
                  <div className="p-2">
                    <Link href="/settings" className="flex items-center space-x-2 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded">
                      <Settings size={16} />
                      <span>Settings</span>
                    </Link>
                    <button onClick={handleLogout} className="w-full flex items-center space-x-2 px-4 py-2 text-red-600 hover:bg-red-50 rounded">
                      <LogOut size={16} />
                      <span>Logout</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </nav>
  )
}
