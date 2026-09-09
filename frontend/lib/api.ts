const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export async function api<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API}/api/v1${path}`, { ...options, cache: "no-store" })
  if (!response.ok) throw new Error(`API request failed (${response.status})`)
  const body = await response.json()
  return body.data as T
}

export type Case = {
  id: string; title: string; status: string; severity?: string;
  tags?: string; created_by?: string; created_at: string; updated_at?: string;
}

export type Finding = {
  id?: string; rule_id: string; category: string; severity: string;
  title: string; description: string; score_delta: number; confidence: number;
}

export type EmailMessage = {
  id: string; from_address: string | null; from_display_name: string | null;
  to_addresses: string | null; cc_addresses: string | null;
  reply_to: string | null; return_path: string | null;
  subject: string | null; date: string | null; message_id: string | null;
  body_text: string | null; body_html_sanitized: string | null;
}

export type AuthResult = {
  mechanism: string; domain: string | null; result: string | null;
  alignment: string | null; policy: string | null; explanation: string | null;
}

export type Explanation = {
  executive_summary: string; why_suspicious: string[];
  key_evidence: Record<string, unknown>[]; possible_attack_type: string[];
  investigative_next_steps: string[]; limitations: string[];
}

export type MLAssessment = {
  phishing_probability: number; bec_probability: number;
  impersonation_probability: number; model_version: string;
}

export type CaseSummary = {
  case: Case; email: EmailMessage | null;
  risk_score: number | null; risk_level: string | null;
  summary: string; findings_plain: string[];
  explanation: Explanation | null; ml: MLAssessment | null;
  auth_results: AuthResult[]; hops_count: number; findings_count: number;
}

export type Campaign = {
  id: string; name: string; description: string;
  confidence: number; case_count: number; created_at: string;
}

export type DashboardStats = {
  total_cases: number; open_cases: number;
  severity_counts: Record<string, number>;
  status_counts: Record<string, number>;
  campaigns: Campaign[];
  indicators: {
    total: number; unique_domains: number; unique_ips: number; unique_urls: number;
    top_domains: string[]; top_ips: string[];
  };
  mitre_techniques: Record<string, number>;
  risk_distribution: Record<string, number>;
  recent_cases: { id: string; title: string; status: string; severity: string; created_at: string }[];
}
