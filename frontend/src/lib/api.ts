export type ChatRequest = { message: string; session_id?: string | null }
export type ReasoningStep = { thought?: string; tool_name?: string | null; tool_input?: string | null }
export type ChatResponse = { response: string; reasoning_steps?: ReasoningStep[] }

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000"

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
