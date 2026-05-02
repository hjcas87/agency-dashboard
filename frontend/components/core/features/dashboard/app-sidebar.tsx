'use client'

import { NavUser } from '@/components/core/features/dashboard/nav-user'
import { MAIN_NAV, SETTINGS_NAV } from '@/components/core/features/dashboard/sidebar-config'
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from '@/components/core/ui/sidebar'

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  return (
    <Sidebar collapsible="icon" {...props}>
      {/* Logo header — hidden when collapsed to icon strip */}
      <SidebarHeader className="flex items-center justify-center py-4 group-data-[collapsible=icon]:hidden">
        <a href="/">
          <div
            className="size-17.5 rounded-full ring-1 ring-sidebar-border flex items-center justify-center p-2"
            style={{ backgroundColor: 'oklch(0.15 0.02 260)' }}
          >
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src="/mendri-brand.png" alt="Mendri" className="size-full object-contain" />
          </div>
        </a>
      </SidebarHeader>

      <SidebarContent>
        {/* Main nav items */}
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              {MAIN_NAV.map(item => (
                <SidebarMenuItem key={item.url}>
                  <SidebarMenuButton asChild tooltip={item.title}>
                    <a href={item.url}>
                      <item.icon className="size-4" />
                      <span>{item.title}</span>
                    </a>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        {/* Settings at bottom */}
        <SidebarGroup className="mt-auto">
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton asChild tooltip={SETTINGS_NAV.title}>
                  <a href={SETTINGS_NAV.url}>
                    <SETTINGS_NAV.icon className="size-4" />
                    <span>{SETTINGS_NAV.title}</span>
                  </a>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter>
        <NavUser />
      </SidebarFooter>
    </Sidebar>
  )
}
