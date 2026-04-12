'use client'

import { AppSidebar } from '@/components/core/features/dashboard/app-sidebar'
import { SiteHeader } from '@/components/core/features/dashboard/site-header'
import { SIDEBAR_WIDTH, SidebarInset, SidebarProvider } from '@/components/core/ui/sidebar'

/**
 * Dashboard layout provider.
 * Wraps all private routes with a sidebar + header layout.
 * Uses shadcn/ui SidebarProvider for collapsible sidebar state.
 */
export function DashboardProvider({ children }: { children: React.ReactNode }) {
  return (
    <SidebarProvider
      style={
        {
          '--sidebar-width': SIDEBAR_WIDTH,
        } as React.CSSProperties
      }
    >
      <AppSidebar variant="inset" />
      <SidebarInset>
        <SiteHeader />
        <main className="flex min-h-[calc(100vh-var(--header-height))] flex-1 flex-col overflow-auto">
          <div className="flex flex-1 flex-col p-4 md:p-6 lg:p-8">
            {children}
          </div>
          <footer className="border-t px-4 py-3 text-center text-xs text-muted-foreground md:px-6 lg:px-8">
            Desarrollado por{' '}
            <span className="font-medium text-foreground">Mendri</span>
          </footer>
        </main>
      </SidebarInset>
    </SidebarProvider>
  )
}
