"use client"

import React, { ReactNode } from "react"
import { useBranding } from "../AuthBrandingProvider"
import Image from "next/image"

interface AuthLayoutProps {
  children: ReactNode
}

/**
 * Auth layout component that renders different layouts based on branding config.
 */
export function AuthLayout({ children }: AuthLayoutProps) {
  const branding = useBranding()
  const { layout, colors } = branding

  if (layout.type === "split-screen") {
    return (
      <div className="flex min-h-screen">
        {/* Left side */}
        <div
          className="hidden lg:flex lg:w-1/2 flex-col justify-center p-12"
          style={{ backgroundColor: colors.background }}
        >
          {layout.leftSideContent ? (
            <div className="max-w-md">
              {layout.leftSideContent.title && (
                <h1
                  className="text-4xl font-bold mb-4"
                  style={{ color: colors.primary }}
                >
                  {layout.leftSideContent.title}
                </h1>
              )}
              {layout.leftSideContent.subtitle && (
                <h2
                  className="text-2xl font-semibold mb-4"
                  style={{ color: colors.primary }}
                >
                  {layout.leftSideContent.subtitle}
                </h2>
              )}
              {layout.leftSideContent.description && (
                <p
                  className="text-lg mb-8"
                  style={{ color: colors.textSecondary }}
                >
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
            <div className="max-w-md">
              <h1
                className="text-4xl font-bold mb-4"
                style={{ color: colors.primary }}
              >
                ¡Bienvenido a nuestro CRM!
              </h1>
            </div>
          )}
        </div>

        {/* Right side with background */}
        <div
          className="flex-1 flex items-center justify-center p-4 relative overflow-hidden"
          style={{
            backgroundImage: layout.backgroundImage
              ? `url(${layout.backgroundImage})`
              : undefined,
            backgroundColor: layout.backgroundImage
              ? undefined
              : colors.background,
            backgroundSize: layout.backgroundImage ? "cover" : undefined,
            backgroundPosition: layout.backgroundImage ? "center" : undefined,
          }}
        >
          {layout.backgroundImage && layout.backgroundOverlay && (
            <div
              className="absolute inset-0"
              style={{
                backgroundColor: layout.backgroundOverlay,
              }}
            />
          )}
          <div className="relative z-10 w-full max-w-lg px-4">{children}</div>
        </div>
      </div>
    )
  }

  if (layout.type === "full-width") {
    return (
      <div
        className="min-h-screen p-4"
        style={{ backgroundColor: colors.background }}
      >
        <div className="max-w-4xl mx-auto">{children}</div>
      </div>
    )
  }

  // Default: centered layout
  return (
    <div
      className="flex flex-col min-h-screen"
      style={{ backgroundColor: colors.background }}
    >
      <div className="flex-1 flex items-center justify-center p-4">
        {children}
      </div>
    </div>
  )
}

