/**
 * Sidebar navigation configuration for Mendri.
 * All navigation items, icons, labels are centralized here.
 * No magic strings — everything comes from this file.
 */
import {
  IconDashboard,
  IconMessage,
  IconSettings,
  IconShoppingCart,
  IconUsers,
} from '@tabler/icons-react'
import type React from 'react'

export type NavItem = {
  title: string
  url: string
  icon: React.ComponentType<{ className?: string }>
}

/** Main navigation items shown at the top of the sidebar. */
export const MAIN_NAV: NavItem[] = [
  { title: 'Dashboard', url: '/', icon: IconDashboard },
  { title: 'Carritos abandonados', url: '/abandoned-cart', icon: IconShoppingCart },
  { title: 'Clientes', url: '/customers', icon: IconUsers },
  { title: 'Mensajes', url: '/messages', icon: IconMessage },
]

/** Settings item shown at the bottom of the sidebar, above the user section. */
export const SETTINGS_NAV: NavItem = {
  title: 'Configuración',
  url: '/settings',
  icon: IconSettings,
}

/** Route-to-title map for the header. */
export const ROUTE_TITLES: Record<string, string> = {
  '/': 'Dashboard',
  '/abandoned-cart': 'Carritos abandonados',
  '/customers': 'Clientes',
  '/messages': 'Mensajes',
  '/settings': 'Configuración',
}
