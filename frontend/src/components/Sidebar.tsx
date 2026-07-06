'use client'

import { useAuthStore } from '@/store/auth'
import {
  BarChart3,
  FileText,
  AlertTriangle,
  Settings,
  Home,
  Zap,
} from 'lucide-react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import clsx from 'clsx'

export default function Sidebar() {
  const pathname = usePathname()
  const { user } = useAuthStore()

  const isAdmin = user?.role === 'admin'

  const menuItems = [
    { href: '/dashboard', label: 'Dashboard', icon: Home },
    { href: '/threats', label: 'Threats', icon: AlertTriangle },
    { href: '/reports', label: 'Reports', icon: FileText },
    { href: '/analytics', label: 'Analytics', icon: BarChart3 },
    ...(isAdmin ? [{ href: '/settings', label: 'Settings', icon: Settings }] : []),
  ]

  return (
    <aside className="w-64 bg-gray-900 text-white h-screen fixed left-0 top-16 overflow-y-auto">
      <div className="p-6">
        <div className="mb-8">
          <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Menu</h2>
        </div>

        <nav className="space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon
            const isActive = pathname === item.href
            return (
              <Link
                key={item.href}
                href={item.href}
                className={clsx(
                  'flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors',
                  isActive
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-400 hover:bg-gray-800 hover:text-white'
                )}
              >
                <Icon size={20} />
                <span>{item.label}</span>
              </Link>
            )
          })}
        </nav>
      </div>

      {/* Bottom section */}
      <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-800">
        <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Zap size={16} />
            <h3 className="font-semibold text-sm">Pro Tier</h3>
          </div>
          <p className="text-xs text-gray-100">500 employees monitored</p>
        </div>
      </div>
    </aside>
  )
}
