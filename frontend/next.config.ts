/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  rewrites: async () => {
    return [
      {
        source: '/api/:path*',
        destination: process.env.NODE_ENV === 'production' 
          ? 'https://your-backend-deployment-url.vercel.app/:path*' 
          : 'http://localhost:8000/api/:path*'
      }
    ]
  }
};

export default nextConfig;
