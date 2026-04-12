/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: process.env.NODE_ENV === 'production' ? 'standalone' : undefined,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
  // Permitir Server Actions cuando se usa un túnel de desarrollo
  experimental: {
    serverActions: {
      allowedOrigins: ['localhost:3000', '*.devtunnels.ms', '*.brs.devtunnels.ms'],
    },
  },
}

module.exports = nextConfig
