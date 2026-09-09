const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export async function api<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API}/api/v1${path}`, { ...options, cache: "no-store" })
  if (!response.ok) throw new Error(`API request failed (${response.status})`)
  const body = await response.json()
  return body.data as T
}

export type Case = { id: string; title: string; status: string; severity?: string; tags?: string; created_at: string }
export type Finding = { rule_id: string; category: string; severity: string; title: string; description: string; score_delta: number; confidence: number }
