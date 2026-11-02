import { useState } from "react"
import { useTranslation } from "react-i18next"

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { CaptchaField, type CaptchaValue } from "@/features/auth/captcha-field"
import { useAppConfig } from "@/features/config/use-app-config"
import { LanguageSwitcher } from "@/features/i18n/language-switcher"
import { apiFetch } from "@/lib/api"

export default function App() {
  const { t } = useTranslation()
  const { config, error } = useAppConfig()
  const [captcha, setCaptcha] = useState<CaptchaValue>({ token: "", code: "" })
  const [verifyResult, setVerifyResult] = useState<string | null>(null)

  async function verifyCaptcha() {
    setVerifyResult(null)
    try {
      const result = await apiFetch<{ valid: boolean }>(
        "/api/v1/auth/captcha/verify",
        {
          method: "POST",
          body: JSON.stringify(captcha),
        },
      )
      setVerifyResult(
        result.valid ? t("captcha.verifySuccess") : t("captcha.verifyInvalid"),
      )
    } catch (reason) {
      setVerifyResult(
        reason instanceof Error ? reason.message : t("captcha.verifyFailed"),
      )
    }
  }

  return (
    <main className="mx-auto flex min-h-svh max-w-2xl items-center p-6">
      <Card className="w-full">
        <CardHeader>
          <CardTitle>{config?.app_name ?? t("app.title")}</CardTitle>
          <CardDescription>
            {config
              ? t("config.environment", { environment: config.environment })
              : t("config.loading")}
          </CardDescription>
          <CardAction>
            <LanguageSwitcher />
          </CardAction>
        </CardHeader>
        <CardContent className="space-y-4">
          {error ? (
            <Alert variant="destructive">
              <AlertTitle>{t("config.errorTitle")}</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          ) : null}

          {config && !config.captcha_enabled ? (
            <Alert>
              <AlertTitle>{t("captcha.disabledTitle")}</AlertTitle>
              <AlertDescription>
                {t("captcha.disabledDescription")}
              </AlertDescription>
            </Alert>
          ) : null}

          <CaptchaField
            enabled={config?.captcha_enabled ?? false}
            value={captcha}
            onChange={setCaptcha}
          />

          {config?.captcha_enabled ? (
            <Button
              type="button"
              onClick={() => void verifyCaptcha()}
              disabled={!captcha.token || !captcha.code}
            >
              {t("captcha.verify")}
            </Button>
          ) : null}

          {verifyResult ? (
            <p className="text-sm text-muted-foreground">{verifyResult}</p>
          ) : null}
        </CardContent>
      </Card>
    </main>
  )
}
