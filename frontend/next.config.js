/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    // 如果設置了API URL環境變數，使用它；否則使用默認本地地址
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
    
    return [
      {
        source: '/api/:path*',
        destination: `${apiUrl}/:path*`,
      },
    ]
  },
  // 優化生產構建
  output: 'standalone',
  
  // 環境變數配置
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001',
  },
  
  // 圖片域名配置
  images: {
    domains: [
      'localhost',
      'your-api-domain.com',
    ],
  },
}

module.exports = nextConfig