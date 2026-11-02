import { useCallback, useEffect, useState } from "react"
import { useTranslation } from "react-i18next"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import i18n from "@/i18n"
import { apiFetch } from "@/lib/api"

export type CaptchaValue = {
  token: string
  code: string
}

type CaptchaChallenge = {
  token: string
  image: string
}

type CaptchaFieldProps = {
  enabled: boolean
  value: CaptchaValue
  onChange: (value: CaptchaValue) => void
}

export function CaptchaField({ enabled, value, onChange }: CaptchaFieldProps) {
  const { t } = useTranslation()
  const [image, setImage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const load = useCallback(async () => {
    if (!enabled) {
      setImage(null)
      return
    }

    setLoading(true)
    setError(null)
    try {
      const challenge = await apiFetch<CaptchaChallenge>("/api/v1/auth/captcha")
      setImage(challenge.image)
      onChange({ token: challenge.token, code: "" })
    } catch (reason) {
      setError(
        reason instanceof Error ? reason.message : i18n.t("captcha.loadFailed"),
      )
    } finally {
      setLoading(false)
    }
  }, [enabled, onChange])

  useEffect(() => {
    void load()
  }, [load])

  if (!enabled) return null

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-3">
        {image ? (
          <img
            src={image}
            alt={t("captcha.imageAlt")}
            className="h-12 rounded-md border"
          />
        ) : (
          <div className="h-12 w-36 animate-pulse rounded-md border bg-muted" />
        )}
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={() => void load()}
        >
          {loading ? t("captcha.refreshing") : t("captcha.refresh")}
        </Button>
      </div>
      <div className="space-y-2">
        <Label htmlFor="captcha-code">{t("captcha.label")}</Label>
        <Input
          id="captcha-code"
          value={value.code}
          autoComplete="off"
          maxLength={8}
          onChange={(event) => onChange({ ...value, code: event.target.value })}
          placeholder={t("captcha.placeholder")}
        />
      </div>
      {error ? <p className="text-sm text-destructive">{error}</p> : null}
    </div>
  )
}
