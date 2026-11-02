import i18n from "i18next"
import { initReactI18next } from "react-i18next"

import en from "./locales/en.json"
import zh from "./locales/zh.json"

export const languages = ["en", "zh"] as const

export type Language = (typeof languages)[number]

const LANGUAGE_STORAGE_KEY = "app.language"

export function isLanguage(value: unknown): value is Language {
  return typeof value === "string" && languages.includes(value as Language)
}

function detectLanguage(): Language {
  const stored = localStorage.getItem(LANGUAGE_STORAGE_KEY)
  if (isLanguage(stored)) return stored
  return navigator.language.toLowerCase().startsWith("zh") ? "zh" : "en"
}

function syncDocument(language: string) {
  const current = isLanguage(language) ? language : "en"
  document.documentElement.lang = current === "zh" ? "zh-CN" : "en"
  document.title = i18n.t("app.title")
  localStorage.setItem(LANGUAGE_STORAGE_KEY, current)
}

void i18n.use(initReactI18next).init({
  resources: {
    en: { translation: en },
    zh: { translation: zh satisfies typeof en },
  },
  lng: detectLanguage(),
  fallbackLng: "en",
  supportedLngs: languages,
  interpolation: { escapeValue: false },
})

i18n.on("languageChanged", syncDocument)
syncDocument(i18n.resolvedLanguage ?? i18n.language)

export function setLanguage(language: Language) {
  void i18n.changeLanguage(language)
}

export default i18n
