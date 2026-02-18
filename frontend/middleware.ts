// ============================================
// Boussole - i18n Middleware with RTL Support
// ============================================

import createMiddleware from "next-intl/middleware";
import { NextRequest } from "next/server";

// Create middleware
export default createMiddleware({
  // A list of all locales that are supported
  locales: ["en", "fr", "ar"],

  // Used when no locale matches
  defaultLocale: "en",

  // The default locale to use when the user visits `/`
  localePrefix: "as-needed",
});

export const config = {
  // Match all pathnames except for
  // - … if they start with `/api`, `/_next` or `/_vercel`
  // - … the ones containing a dot (e.g. `favicon.ico`)
  matcher: ["/((?!api|_next|_vercel|.*\\..*).*)"],
};

// ============================================
// RTL Support Configuration
// ============================================

/**
 * Get text direction based on locale
 * @param locale - The locale code
 * @returns 'rtl' for Arabic, 'ltr' otherwise
 */
export function getTextDirection(locale: string): "rtl" | "ltr" {
  return locale === "ar" ? "rtl" : "ltr";
}

/**
 * Check if a locale is RTL
 * @param locale - The locale code
 * @returns true if locale is Arabic
 */
export function isRTL(locale: string): boolean {
  return locale === "ar";
}
