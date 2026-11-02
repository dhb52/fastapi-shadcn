import { useEffect, useState } from "react"

import i18n from "@/i18n"
import { apiFetch } from "@/lib/api"

export type AppConfig = {
  app_name: string
  environment: string
  captcha_enabled: boolean
}

export function useAppConfig() {
  const [config, setConfig] = useState<AppConfig | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    apiFetch<AppConfig>("/api/v1/config")
      .then((value) => {
        if (!cancelled) setConfig(value)
      })
      .catch((reason: unknown) => {
        if (!cancelled) {
          setError(
            reason instanceof Error
              ? reason.message
              : i18n.t("config.errorFallback"),
          )
        }
      })

    return () => {
      cancelled = true
    }
  }, [])

  return { config, error }
}
