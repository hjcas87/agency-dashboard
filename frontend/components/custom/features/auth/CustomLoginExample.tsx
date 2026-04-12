/**
 * EXAMPLE: Custom Login Page
 * 
 * This is an example of how to create a fully customized login page
 * while still using the core functionality.
 * 
 * Copy this to your custom auth pages if you need more control.
 */

"use client"

import { AuthBrandingProvider, useBranding } from "@/components/core/features/auth/AuthBrandingProvider"
import { BaseLoginForm } from "@/components/core/features/auth/BaseLoginForm"

function CustomLoginContent() {
  const branding = useBranding()

  return (
    <div className="min-h-screen flex">
      {/* Left side - Custom content */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-blue-600 to-purple-600 p-12 flex-col justify-center">
        <div className="max-w-md text-white">
          <h1 className="text-5xl font-bold mb-4">
            ¡Bienvenido
          </h1>
          <h2 className="text-4xl font-semibold mb-6">
            a nuestro CRM!
          </h2>
          <p className="text-xl mb-8 opacity-90">
            Completa tus datos y empezá a operar
          </p>
          {/* Custom logo or image */}
          <div className="mt-8">
            <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center">
              <span className="text-blue-600 font-bold text-2xl">O</span>
            </div>
          </div>
        </div>
      </div>

      {/* Right side - Login form */}
      <div 
        className="flex-1 flex items-center justify-center p-4 relative"
        style={{
          backgroundImage: "url('/auth-background.jpg')",
          backgroundSize: "cover",
          backgroundPosition: "center",
        }}
      >
        {/* Overlay */}
        <div 
          className="absolute inset-0"
          style={{
            backgroundColor: "rgba(59, 130, 246, 0.5)",
          }}
        />
        
        {/* Form */}
        <div className="relative z-10 w-full max-w-md">
          <BaseLoginForm />
        </div>
      </div>
    </div>
  )
}

export function CustomLoginExample() {
  return (
    <AuthBrandingProvider>
      <CustomLoginContent />
    </AuthBrandingProvider>
  )
}

