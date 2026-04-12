'use client'

import Image from 'next/image'
import { ReactNode } from 'react'
import { useBranding } from '../AuthBrandingProvider'
import { ThemeToggle } from '@/components/core/features/dashboard/theme-toggle'

interface AuthLayoutProps {
  children: ReactNode
}

/**
 * Auth layout component.
 * Renders a centered or split-screen layout using shadcn theme colors.
 */
export function AuthLayout({ children }: AuthLayoutProps) {
  const branding = useBranding()
  const { layout, logo } = branding

  if (layout.type === 'split-screen') {
    return (
      <div className="flex min-h-screen">
        {/* Left side */}
        <div className="hidden lg:flex lg:w-1/2 flex-col items-center justify-center bg-muted p-12">
          {layout.leftSideContent ? (
            <div className="max-w-md text-center lg:text-left">
              {layout.leftSideContent.title && layout.leftSideContent.subtitle ? (
                <h1 className="mb-8 text-5xl font-bold text-foreground">
                  {layout.leftSideContent.title} {layout.leftSideContent.subtitle}
                </h1>
              ) : layout.leftSideContent.title ? (
                <h1 className="mb-8 text-5xl font-bold text-foreground">
                  {layout.leftSideContent.title}
                </h1>
              ) : null}

              <div className="mb-8 flex items-center justify-center lg:justify-start">
                {logo.component ? (
                  <logo.component className="size-16 text-primary" />
                ) : logo.src ? (
                  <Image
                    src={logo.src}
                    alt={logo.alt || 'Logo'}
                    width={300}
                    height={72}
                    className="h-16 w-auto"
                    priority
                  />
                ) : logo.text ? (
                  <span className="text-4xl font-bold text-primary">{logo.text}</span>
                ) : null}
              </div>

              {layout.leftSideContent.description && (
                <p className="mt-8 text-lg text-muted-foreground">
                  {layout.leftSideContent.description}
                </p>
              )}
              {layout.leftSideContent.image && (
                <div className="mt-8">
                  <Image
                    src={layout.leftSideContent.image}
                    alt="Brand image"
                    width={400}
                    height={300}
                    className="rounded-lg"
                  />
                </div>
              )}
            </div>
          ) : (
            <h1 className="mb-4 text-4xl font-bold text-foreground">¡Bienvenido a Mendri!</h1>
          )}
        </div>

        {/* Right side */}
        <div className="relative flex flex-1 items-center justify-center overflow-hidden bg-background p-4">
          <div className="absolute right-4 top-4">
            <ThemeToggle />
          </div>
          {layout.backgroundImage && layout.backgroundOverlay && (
            <div
              className="absolute inset-0"
              style={{ backgroundColor: layout.backgroundOverlay }}
            />
          )}
          <div className="relative z-10 w-full max-w-lg">{children}</div>
        </div>
      </div>
    )
  }

  // Default: centered
  return (
    <div className="relative flex min-h-screen flex-col items-center justify-center bg-background p-4">
      <div className="absolute right-4 top-4">
        <ThemeToggle />
      </div>
      <div className="w-full max-w-lg">{children}</div>
    </div>
  )
}
