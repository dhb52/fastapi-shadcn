# assistant-ui (optional)

Use only when the user asks for an AI chat UI. The base scaffold has no chat backend; do not ship a fake echo route.

Docs: https://www.assistant-ui.com/docs/installation and https://www.assistant-ui.com/docs/runtimes/custom/local-runtime

## Install

Add the style-aware registry to `frontend/components.json`:

```json
"registries": {
  "@assistant-ui": "https://r.assistant-ui.com/styles/{style}/{name}.json"
}
```

Install the thread components with the detected package manager:

```bash
bunx --bun shadcn@latest add @assistant-ui/thread @assistant-ui/thread-list
```

If the registry does not install the runtime package:

```bash
bun add @assistant-ui/react
```

## Runtime adapter

Create `src/features/chat/chat-runtime.tsx`:

```tsx
import type { ReactNode } from "react"
import {
  AssistantRuntimeProvider,
  type ChatModelAdapter,
  useLocalRuntime,
} from "@assistant-ui/react"

import { API_BASE } from "@/lib/api"

const adapter: ChatModelAdapter = {
  async *run({ messages, abortSignal }) {
    const response = await fetch(`${API_BASE}/api/v1/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages }),
      signal: abortSignal,
    })
    if (!response.ok || !response.body) throw new Error("Chat request failed")

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let text = ""
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      text += decoder.decode(value, { stream: true })
      yield { content: [{ type: "text", text }] }
    }
  },
}

export function ChatRuntimeProvider({ children }: { children: ReactNode }) {
  const runtime = useLocalRuntime(adapter)
  return (
    <AssistantRuntimeProvider runtime={runtime}>
      {children}
    </AssistantRuntimeProvider>
  )
}
```

Wrap the app (or the chat route) in `ChatRuntimeProvider` and render the generated `Thread` component from `@/components/assistant-ui/thread`.

## Backend contract

The adapter expects:

- `POST /api/v1/chat/stream`
- JSON body: `{ "messages": ThreadMessage[] }`
- Response: `text/plain` or SSE stream of text chunks
- Abort via `AbortSignal`

Implement the route with FastAPI `StreamingResponse` and the app's model provider. Keep provider credentials server-side. If the provider returns structured tool calls or agent state, use assistant-ui's data-stream or assistant-transport runtime instead of extending this text adapter ad hoc.

## Vite notes

- Do not copy Next.js route handlers or `"use client"` directives.
- The shadcn registry serves Radix or Base UI flavored components based on `components.json` style; keep the style stable.
- Generated chat components are app-owned code; review them like any other feature code.
