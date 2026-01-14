import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Turbopack - Next.js 16 alreadystablefortoplevelConfig
  turbopack: {},

  // GraphpieceOptimization
  images: {
    formats: ["image/avif", "image/webp"],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
  },

  // EnablestrictPattern，help reveal potentialIssue
  reactStrictMode: true,

  // OptimizationProductionBuild
  poweredByHeader: false,
};

export default nextConfig;
