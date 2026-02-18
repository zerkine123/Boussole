// i18n configuration for Boussole
export const locales = ["en", "fr", "ar"] as const;
export const defaultLocale = "en" as const;
export const localePrefix = "as-needed";


export const localeNames: Record<string, string> = {
  en: "English",
  fr: "Français",
  ar: "العربية",
};

export const localeDirections: Record<string, "ltr" | "rtl"> = {
  en: "ltr",
  fr: "ltr",
  ar: "rtl",
};

export function getDirection(locale: string): "ltr" | "rtl" {
  return localeDirections[locale] || "ltr";
}

export function isRTL(locale: string): boolean {
  return getDirection(locale) === "rtl";
}
