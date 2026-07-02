import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  compress: true,
  images: {
    formats: ['image/avif', 'image/webp'],
    remotePatterns: [
      { protocol: 'https', hostname: 'images.unsplash.com' },
      { protocol: 'https', hostname: 'res.cloudinary.com' },
      { protocol: 'https', hostname: '**.amazonaws.com' },
      { protocol: 'http', hostname: '127.0.0.1' },
      { protocol: 'http', hostname: 'localhost' },
      { protocol: 'http', hostname: '45.148.29.33' },
      { protocol: 'https', hostname: 'api.okj.uz' },
    ],
  },
  async rewrites() {
    const targetUrl = process.env.BACKEND_API_URL || 'http://45.148.29.33:8000/api/v1';
    return [
      {
        source: '/api/v1/:path*',
        destination: `${targetUrl}/:path*`,
      },
    ];
  },
  experimental: {
    optimizePackageImports: ['lucide-react', 'framer-motion', '@tanstack/react-query'],
  },
};

export default nextConfig;
