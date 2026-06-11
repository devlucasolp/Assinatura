import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: 'svgl.app', pathname: '/library/**' },
    ],
  },
  allowedDevOrigins: ['172.23.240.1', 'localhost'],

  // Tree-shake agressivo no dev — corta ~30-50% do tempo de compile
  experimental: {
    optimizePackageImports: ['lucide-react'],
  },

  // Desabilita typed routes em dev (custoso em path com acentos)
  typedRoutes: false,

  // Source maps mais leves
  productionBrowserSourceMaps: false,
}

export default nextConfig
