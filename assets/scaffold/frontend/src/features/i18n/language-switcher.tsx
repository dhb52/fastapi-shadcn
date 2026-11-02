import { Languages } from "lucide-react"
import { useTranslation } from "react-i18next"

import { Button } from "@/components/ui/button"
import { type Language, languages, setLanguage } from "@/i18n"

export function LanguageSwitcher() {
  const { t, i18n } = useTranslation()
  const current = languages.indexOf(i18n.resolvedLanguage as Language)
  const next = languages[(current + 1) % languages.length]

  return (
    <Button
      type="button"
      variant="ghost"
      size="sm"
      aria-label={t("language.switch")}
      title={t("language.switch")}
      onClick={() => setLanguage(next)}
    >
      <Languages />
      {t(`language.${next}`)}
    </Button>
  )
}
