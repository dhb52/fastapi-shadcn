# Frontend

## Package manager

Priority: bun > pnpm > npm. Detect from the lockfile:

| Lockfile | Manager | Run scripts | shadcn |
|---|---|---|---|
| `bun.lock` / `bun.lockb` | bun | `bun run <script>` | `bunx --bun shadcn@latest ...` |
| `pnpm-lock.yaml` | pnpm | `pnpm <script>` | `pnpm dlx shadcn@latest ...` |
| `package-lock.json` | npm | `npm run <script>` | `npx shadcn@latest ...` |

The pre-commit hooks call `frontend/node_modules/.bin/biome` and `frontend/node_modules/.bin/tsc`, so they work with any manager after install.

## Stack

- React 19 + Vite 8 + TypeScript 6
- Tailwind CSS v4 via `@tailwindcss/vite`
- shadcn/ui `new-york` style on Radix primitives
- i18next + react-i18next, English and Chinese resources
- Biome 2.6 for format + lint
- `@/` alias to `src/`

`vite.config.ts` configures the alias and the `/api` dev proxy:

```ts
server: {
  proxy: {
    "/api": { target: "http://127.0.0.1:8000", changeOrigin: true },
  },
}
```

`VITE_API_URL` overrides the API base for split deployments. Leave it empty in development.

## shadcn

`components.json` uses:

- `"style": "new-york"`
- `"rsc": false`
- `"css": "src/index.css"`
- `"baseColor": "neutral"`
- `"cssVariables": true`
- aliases under `@/`

The scaffold ships the five primitives it uses (`button`, `card`, `input`, `label`, `alert`) so the project builds without a registry call. Add new components with:

```bash
bunx --bun shadcn@latest add dialog
```

Generated primitives belong in `src/components/ui/`. Biome excludes that directory, matching the official template. App code belongs in `src/features/<feature>/`.

The official shadcn skill (`skills add shadcn/ui`) is complementary; it reads `components.json` and documents the current CLI. Do not duplicate its component documentation here.

## API client and config

`src/lib/api.ts`:

- `API_BASE = import.meta.env.VITE_API_URL ?? ""`
- JSON `Content-Type` is set when a body is present.
- Non-2xx responses throw `ApiError` with the backend `detail` string when available.

`src/features/config/use-app-config.ts` fetches `/api/v1/config` once and returns `{ config, error }`. The config type is:

```ts
type AppConfig = {
  app_name: string
  environment: string
  captcha_enabled: boolean
}
```

## Captcha field

`src/features/auth/captcha-field.tsx`:

- Props: `enabled`, controlled `value: { token, code }`, `onChange`.
- Returns `null` when disabled.
- Fetches `/api/v1/auth/captcha` when enabled; resets `code` when a new token arrives.
- Shows the base64 image, a `type="button"` refresh button, a label/input, and an error message.
- The parent holds state with `useState`, so `onChange` is stable and the fetch effect does not loop.

`App.tsx` only renders the field when `config.captcha_enabled` is true and only shows the verify button in that state. When false, it shows an informational alert. This is the required config-driven hiding behavior.

## i18n

`src/i18n/index.ts` initializes i18next before React renders:

- Resources live in `src/i18n/locales/en.json` and `src/i18n/locales/zh.json`; the English file is the source of truth.
- `src/i18n/i18next.d.ts` augments `CustomTypeOptions`, so keys passed to `t()` are type-checked and unknown keys fail `tsc`.
- Language resolution order: `localStorage["app.language"]`, then the browser language (`zh*` -> `zh`, otherwise `en`), with `en` as the fallback.
- Every change writes `app.language`, updates `<html lang>`, and sets `document.title` from `app.title`.
- `src/features/i18n/language-switcher.tsx` toggles between English and Chinese; `CardAction` places it in the card header.

In components, use `const { t } = useTranslation()` and translate every user-visible string, including placeholders, `alt` text, and error fallbacks. Outside React (API client, config hook), import the initialized instance:

```ts
import i18n from "@/i18n"

i18n.t("api.requestFailed", { status: response.status })
```

The fallback message for a non-2xx response without a backend `detail` is already translated in `src/lib/api.ts`. Add a locale by importing its JSON file in `src/i18n/index.ts`, adding it to `languages`, and adding its native name under `language`; the switcher cycles through `languages` in order.

Do not hardcode display strings in components; the scaffold's messages are the reference for key naming (`app`, `language`, `config`, `captcha`, `api`).

## Biome

```bash
bun run typecheck
bun run lint
bun run check     # write fixes
bun run build
```

`biome.json` uses recommended rules, organizes imports, formats with spaces and double quotes, and excludes `src/components/ui/**`, `dist`, and `node_modules`.

Do not add ESLint/Prettier/Husky. One formatter/linter keeps the pre-commit hook fast and the config small.

## Browser verification

Run backend and frontend, then check:

1. Config card shows the app name and `environment: development`.
2. With `CAPTCHA_ENABLED=false`, no captcha image/input is rendered and the disabled alert is visible.
3. Restart backend with `CAPTCHA_ENABLED=true`; reload: image, refresh, input, and verify button appear.
4. Verify a code through `POST /api/v1/auth/captcha/verify`; wrong code shows the backend error.
5. Switch the card header language; all labels, placeholders, alerts, and `<html lang>` change, and the choice survives reload.
6. Console has no errors and the network panel shows `/api/v1/config`, `/api/v1/auth/captcha`.
