/**
 * Sidebar navigation configuration for Mendri agency dashboard.
 * All navigation items, icons, labels are centralized here.
 * Customize this file for your project.
 */
import {
  IconBriefcase,
  IconCalendarEvent,
  IconDashboard,
  IconFileInvoice,
  IconSettings,
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
  { title: 'Actividades', url: '/actividades', icon: IconCalendarEvent },
  { title: 'Clientes', url: '/clients', icon: IconUsers },
  { title: 'Presupuestos', url: '/proposals', icon: IconBriefcase },
  { title: 'Facturación', url: '/invoices', icon: IconFileInvoice },
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
  '/actividades': 'Actividades',
  '/clients': 'Clientes',
  '/proposals': 'Presupuestos',
  '/invoices': 'Facturación',
  '/settings': 'Configuración',
  '/clientes': 'Clientes',
  '/presupuestos': 'Presupuestos',
  '/facturacion': 'Facturación',
}
