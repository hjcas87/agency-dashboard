'use client'

/**
 * Mendri footer component for auth pages.
 * Fixed at bottom, centered, minimal.
 */
export function MendriFooter() {
  return (
    <div className="fixed inset-x-0 bottom-4 z-50 flex items-center justify-center gap-1.5 text-xs text-muted-foreground">
      Desarrollado por <span className="font-medium text-foreground">Mendri</span>
    </div>
  )
}
