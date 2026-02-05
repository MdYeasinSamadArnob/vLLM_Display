import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  experimental: {
    serverActions: {
      allowedOrigins: ["localhost:3000", "10.11.200.99:3000", "localhost:3003", "10.11.200.99:3003", "10.11.200.99:8001"]
    }
  }
};

export default nextConfig;
