"use client"
import { useEffect, useState, useCallback } from "react"
import Link from "next/link"
import { api, CaseSummary, Finding, AuthResult } from "@/lib/api"

export default function CasePage({ params }: { params: { id: string } }) {
  const [data, setData] = useState<CaseSummary | null>(null)
  const [findings, setFindings] = useState<Finding[]>([])
  const [error, setError] = useState(false)
  const [techOpen, setTechOpen] = useState(false)
  const [notes, setNotes] = useState<{ author: string; body: string; created_at: string }[]>([])
  const [noteText, setNoteText] = useState("")

  const load = useCallback(() => {
    Promise.all([
      api<CaseSummary>(`/cases/${params.id}/summary`),
      api<Finding[]>(`/cases/${params.id}/findings`).catch(() => []),
    ]).then(([s, f]) => { setData(s); setFindings(f) }).catch(() => setError(true))
  }, [params.id])

  useEffect(() => { load() }, [load])

  const addNote = async () => {
    if (!noteText.trim()) return
    try {
      await api(`/cases/${params.id}/notes`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ body: noteText }),
      })
      setNoteText("")
      const n = await api<{ author: string; body: string; created_at: string }[]>(`/cases/${params.id}/notes`)
      setNotes(n)
    } catch { /* ignore */ }
  }

  useEffect(() => {
    if (data) {
      api<{ author: string; body: string; created_at: string }[]>(`/cases/${params.id}/notes`)
        .then(setNotes).catch(() => {})
    }
  }, [data, params.id])

  if (error) return <main className="p-8"><Box>Unable to load this case.</Box></main>
  if (!data) return <main className="p-8"><Box>Loading investigation...</Box></main>

  const { case: c, email, risk_score, risk_level, summary, findings_plain, explanation, ml, auth_results, hops_count, findings_count } = data

  const riskColor = risk_level === "critical" ? "text-red-400 bg-red-500/10 border-red-500/30"
    : risk_level === "high" ? "text-orange-400 bg-orange-500/10 border-orange-500/30"
    : risk_level === "medium" || risk_level === "guarded" ? "text-amber-400 bg-amber-500/10 border-amber-500/30"
    : risk_level === "low" ? "text-green-400 bg-green-500/10 border-green-500/30"
    : "text-muted-foreground bg-muted border-border"

  const statusColor = c.status === "INVESTIGATING" ? "bg-red-500/20 text-red-300"
    : c.status === "TRIAGED" ? "bg-amber-500/20 text-amber-300"
    : c.status === "FALSE_POSITIVE" ? "bg-green-500/20 text-green-300"
    : c.status === "RESOLVED" ? "bg-blue-500/20 text-blue-300"
    : "bg-muted text-muted-foreground"

  return (
    <main className="min-h-screen bg-background p-4 md:p-8">
      <div className="mx-auto max-w-5xl space-y-5">

        {/* Header */}
        <div className="flex items-center justify-between">
          <Link href="/cases" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
            &larr; Back to Cases
          </Link>
          <div className="flex gap-2">
            <a href={`http://localhost:8000/api/v1/cases/${c.id}/report.pdf`} target="_blank" rel="noopener"
              className="rounded-md border border-border px-3 py-1.5 text-xs text-muted-foreground hover:bg-muted transition-colors">
              Download PDF
            </a>
          </div>
        </div>

        {/* Risk Assessment Card */}
        <div className="rounded-lg border border-border bg-card p-5">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <p className="text-xs tracking-widest text-muted-foreground">CASE {c.id.slice(0, 8).toUpperCase()}</p>
              <h1 className="mt-1 text-2xl font-bold">{c.title}</h1>
            </div>
            <div className="flex items-center gap-2">
              <span className={`rounded-full border px-3 py-1 text-xs font-medium ${statusColor}`}>{c.status}</span>
              {risk_level && (
                <span className={`rounded-full border px-3 py-1 text-xs font-medium ${riskColor}`}>
                  {risk_level.toUpperCase()}
                </span>
              )}
            </div>
          </div>

          {risk_score !== null && risk_score !== undefined && (
            <div className="mt-4 flex items-center gap-4">
              <div className="flex items-baseline gap-1">
                <span className={`text-4xl font-bold ${riskColor.split(" ")[0]}`}>{risk_score}</span>
                <span className="text-sm text-muted-foreground">/ 100</span>
              </div>
              <div className="flex-1">
                <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
                  <div
                    className={`h-full rounded-full transition-all ${
                      risk_level === "critical" ? "bg-red-500" :
                      risk_level === "high" ? "bg-orange-500" :
                      risk_level === "medium" || risk_level === "guarded" ? "bg-amber-500" :
                      "bg-green-500"
                    }`}
                    style={{ width: `${Math.min(100, risk_score)}%` }}
                  />
                </div>
              </div>
            </div>
          )}

          <p className="mt-3 text-sm text-muted-foreground leading-relaxed">{summary}</p>

          {explanation?.possible_attack_type && explanation.possible_attack_type.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-2">
              {explanation.possible_attack_type.map((t) => (
                <span key={t} className="rounded-full bg-red-500/10 border border-red-500/20 px-2.5 py-0.5 text-xs text-red-300 font-medium">
                  {t}
                </span>
              ))}
            </div>
          )}

          {ml && (
            <div className="mt-4 flex gap-4 text-xs text-muted-foreground">
              <span>Phishing: {Math.round(ml.phishing_probability * 100)}%</span>
              <span>BEC: {Math.round(ml.bec_probability * 100)}%</span>
              <span>Impersonation: {Math.round(ml.impersonation_probability * 100)}%</span>
            </div>
          )}
        </div>

        {/* The Email */}
        {email && (
          <div className="rounded-lg border border-border bg-card overflow-hidden">
            <div className="border-b border-border bg-muted/30 px-5 py-3">
              <h2 className="text-sm font-semibold text-foreground">The Email</h2>
            </div>
            <div className="p-5 space-y-3">
              <div className="grid gap-1 text-sm">
                <div className="flex gap-2">
                  <span className="w-16 shrink-0 text-muted-foreground">From</span>
                  <span className="font-medium">
                    {email.from_display_name && <span className="text-foreground">{email.from_display_name} </span>}
                    <span className="text-muted-foreground">&lt;{email.from_address}&gt;</span>
                  </span>
                </div>
                <div className="flex gap-2">
                  <span className="w-16 shrink-0 text-muted-foreground">To</span>
                  <span className="text-foreground">{email.to_addresses}</span>
                </div>
                {email.cc_addresses && (
                  <div className="flex gap-2">
                    <span className="w-16 shrink-0 text-muted-foreground">CC</span>
                    <span className="text-foreground">{email.cc_addresses}</span>
                  </div>
                )}
                <div className="flex gap-2">
                  <span className="w-16 shrink-0 text-muted-foreground">Date</span>
                  <span className="text-foreground">{email.date ? new Date(email.date).toLocaleString() : "Unknown"}</span>
                </div>
                <div className="flex gap-2">
                  <span className="w-16 shrink-0 text-muted-foreground">Subject</span>
                  <span className="font-medium text-foreground">{email.subject || "(no subject)"}</span>
                </div>
              </div>
              <div className="border-t border-border pt-4">
                <div className="whitespace-pre-wrap text-sm leading-relaxed text-foreground/90 max-h-96 overflow-y-auto">
                  {email.body_text || email.body_html_sanitized || "(no content)"}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Why Flagged */}
        {findings_plain.length > 0 && (
          <div className="rounded-lg border border-border bg-card p-5">
            <h2 className="text-sm font-semibold text-foreground mb-3">Why This Was Flagged</h2>
            <ul className="space-y-2">
              {findings_plain.map((f, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-muted-foreground">
                  <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-400" />
                  <span>{f}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Technical Details - Collapsible */}
        <div className="rounded-lg border border-border bg-card overflow-hidden">
          <button
            onClick={() => setTechOpen(!techOpen)}
            className="flex w-full items-center justify-between px-5 py-3 text-left text-sm font-semibold text-foreground hover:bg-muted/30 transition-colors"
          >
            <span>Technical Details</span>
            <span className="text-muted-foreground text-xs">{techOpen ? "▲ Collapse" : "▼ Expand"}</span>
          </button>
          {techOpen && (
            <div className="border-t border-border p-5 space-y-6">

              {/* Auth Results */}
              {auth_results.length > 0 && (
                <div>
                  <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">Authentication Results</h3>
                  <div className="space-y-2">
                    {auth_results.map((a: AuthResult, i: number) => (
                      <div key={i} className="flex items-center justify-between rounded border border-border p-2.5 text-xs">
                        <div className="flex items-center gap-3">
                          <span className="font-mono font-medium text-foreground">{a.mechanism}</span>
                          {a.domain && <span className="text-muted-foreground">{a.domain}</span>}
                        </div>
                        <span className={`font-medium ${
                          a.result === "pass" ? "text-green-400" :
                          a.result === "fail" ? "text-red-400" :
                          "text-amber-400"
                        }`}>
                          {a.result?.toUpperCase()}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Findings */}
              {findings.length > 0 && (
                <div>
                  <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">Findings ({findings_count})</h3>
                  <div className="space-y-2">
                    {findings.map((f, i) => (
                      <div key={i} className="rounded border border-border p-2.5 text-xs">
                        <div className="flex items-center justify-between">
                          <span className="font-medium text-foreground">{f.title}</span>
                          <span className="font-mono text-amber-300">+{f.score_delta}</span>
                        </div>
                        <div className="mt-1 text-muted-foreground">
                          {f.rule_id} &middot; {f.category} &middot; confidence {Math.round(f.confidence * 100)}%
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* MITRE */}
              {explanation?.possible_attack_type && explanation.possible_attack_type.length > 0 && (
                <div>
                  <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">MITRE ATT&CK</h3>
                  <div className="flex flex-wrap gap-2">
                    {explanation.possible_attack_type.map((t) => (
                      <span key={t} className="rounded bg-muted px-2 py-1 font-mono text-xs text-foreground">{t}</span>
                    ))}
                  </div>
                </div>
              )}

              {/* Investigation Info */}
              <div className="grid grid-cols-2 gap-4 text-xs">
                <div>
                  <span className="text-muted-foreground">Received Hops: </span>
                  <span className="text-foreground">{hops_count}</span>
                </div>
                <div>
                  <span className="text-muted-foreground">Findings: </span>
                  <span className="text-foreground">{findings_count}</span>
                </div>
              </div>

              {/* Next Steps */}
              {explanation?.investigative_next_steps && explanation.investigative_next_steps.length > 0 && (
                <div>
                  <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">Recommended Next Steps</h3>
                  <ul className="space-y-1 text-xs text-muted-foreground">
                    {explanation.investigative_next_steps.map((s, i) => (
                      <li key={i}>- {s}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Limitations */}
              {explanation?.limitations && explanation.limitations.length > 0 && (
                <div>
                  <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">Limitations</h3>
                  <ul className="space-y-1 text-xs text-muted-foreground/70">
                    {explanation.limitations.map((l, i) => (
                      <li key={i}>- {l}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Notes */}
        <div className="rounded-lg border border-border bg-card p-5">
          <h2 className="text-sm font-semibold text-foreground mb-3">Investigator Notes</h2>
          {notes.length > 0 && (
            <div className="space-y-2 mb-4">
              {notes.map((n, i) => (
                <div key={i} className="rounded border border-border p-3 text-xs">
                  <div className="flex justify-between text-muted-foreground mb-1">
                    <span className="font-medium">{n.author}</span>
                    <span>{new Date(n.created_at).toLocaleString()}</span>
                  </div>
                  <p className="text-foreground/90">{n.body}</p>
                </div>
              ))}
            </div>
          )}
          <div className="flex gap-2">
            <input
              type="text"
              value={noteText}
              onChange={(e) => setNoteText(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && addNote()}
              placeholder="Add a note..."
              className="flex-1 rounded border border-border bg-muted px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
            />
            <button
              onClick={addNote}
              className="rounded bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
            >
              Add
            </button>
          </div>
        </div>

      </div>
    </main>
  )
}

function Box({ children }: { children: React.ReactNode }) {
  return <div className="rounded-lg border border-border bg-card p-8 text-sm text-muted-foreground">{children}</div>
}
