// ============================================
// Boussole - Next.js Configuration
// ============================================

const createNextIntlPlugin = require("next-intl/plugin");

// Wrap the config with next-intl plugin
const withNextIntl = createNextIntlPlugin("./i18n.ts");

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: false,
  // ============================================
  // NextAuth.js Configuration
  // ============================================
  // Note: NextAuth.js is configured in app/api/auth/[...nextauth]/route.ts

  // ============================================
  // Image Optimization
  // ============================================
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "**",
      },
    ],
  },

  // ============================================
  // Webpack Configuration
  // ============================================
  webpack: (config, { isServer }) => {
    // Fixes npm packages that depend on `fs` module
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
      };
    }
    return config;
  },


};

module.exports = withNextIntl(nextConfig);
