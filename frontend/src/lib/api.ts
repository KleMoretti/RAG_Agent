export type ChatRequest = { message: string; session_id?: string | null }
export type ReasoningStep = { thought?: string; tool_name?: string | null; tool_input?: string | null }
export type ChatResponse = { response: string; reasoning_steps?: ReasoningStep[] }

export type FileUploadResponse = {
  success: boolean
  message: string
  file_id?: string | null
  file_name?: string | null
  file_size?: number | null
  content_type?: string | null
  chunks?: Array<{
    content: string
    type: string
    length: number
  }> | null
}

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000"

export type TokenResponse = { access_token: string; token_type: string }
export type MeResponse = { id: number; username: string; role: string }
export type RegisterResponse = { id: number; username: string }

export async function login(username: string, password: string): Promise<TokenResponse> {
  const res = await fetch(`${API_BASE}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  })
  if (!res.ok) throw new Error(`Login error: ${res.status}`)
  return res.json()
}

export async function register(username: string, password: string): Promise<RegisterResponse> {
  const res = await fetch(`${API_BASE}/api/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  })
  if (!res.ok) {
    try {
      const data = await res.json()
      // FastAPI validation errors shape: { detail: [{ msg, loc, type }, ...] }
      if (data?.detail) {
        const messages = Array.isArray(data.detail)
          ? data.detail.map((d: any) => d?.msg).filter(Boolean)
          : [String(data.detail)]
        throw new Error(messages.join("; ") || `Register error: ${res.status}`)
      }
      if (data?.message) throw new Error(String(data.message))
    } catch (_) {
      // ignore JSON parse errors, fall through to generic
    }
    throw new Error(`Register error: ${res.status}`)
  }
  return res.json()
}

export async function me(token: string): Promise<MeResponse> {
  const res = await fetch(`${API_BASE}/api/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!res.ok) throw new Error(`Me error: ${res.status}`)
  return res.json()
}

export async function refreshToken(token: string): Promise<TokenResponse> {
  const res = await fetch(`${API_BASE}/api/auth/refresh`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!res.ok) throw new Error(`Refresh token error: ${res.status}`)
  return res.json()
}

export async function chat(req: ChatRequest): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  })
  if (!res.ok) {
    throw new Error(`Chat API error: ${res.status}`)
  }
  return res.json()
}

export async function uploadFile(file: File): Promise<FileUploadResponse> {
  const formData = new FormData()
  formData.append('file', file)
  
  const res = await fetch(`${API_BASE}/api/upload`, {
    method: "POST",
    body: formData,
  })
  if (!res.ok) {
    throw new Error(`Upload API error: ${res.status}`)
  }
  return res.json()
}
