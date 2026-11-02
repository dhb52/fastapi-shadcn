import i18n from "@/i18n"

const API_BASE = import.meta.env.VITE_API_URL ?? ""

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message)
    this.name = "ApiError"
  }
}

export async function apiFetch<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const headers = new Headers(init.headers)
  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json")
  }

  const response = await fetch(`${API_BASE}${path}`, { ...init, headers })
  if (!response.ok) {
    let message = i18n.t("api.requestFailed", { status: response.status })
    const payload: unknown = await response.json().catch(() => null)
    if (payload && typeof payload === "object" && "detail" in payload) {
      const detail = payload.detail
      if (typeof detail === "string") message = detail
    }
    throw new ApiError(response.status, message)
  }

  return (await response.json()) as T
}
