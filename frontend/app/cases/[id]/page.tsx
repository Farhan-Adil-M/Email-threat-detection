"use client"
import { useEffect, useState, useCallback } from "react"
import Link from "next/link"
import { api, CaseSummary, Finding, AuthResult, ReceivedHop, URLIndicator, AttachmentInfo, ThreatIntel, GraphNode, GraphEdge } from "@/lib/api"

export default function CasePage({ params }: { params: { id: string } }) {
  const [data, setData] = useState<CaseSummary | null>(null)
  const [findings, setFindings] = useState<Finding[]>([])
  const [graph, setGraph] = useState<{ nodes: GraphNode[]; edges: GraphEdge[] } | null>(null)
  const [error, setError] = useState(false)
  const [openSections, setOpenSections] = useState<Record<string, boolean>>({
    auth: true, urls: false, infra: false, graph: false, intel: false,
    evidence: false, campaign: false, mitre: false,
  })
  const [notes, setNotes] = useState<{ author: string; body: string; created_at: string }[]>([])
  const [noteText, setNoteText] = useState("")

  const toggle = (key: string) => setOpenSections(prev => ({ ...prev, [key]: !prev[key] }))

  const load = useCallback(() => {
    Promise.all([
      api<CaseSummary>(`/cases/${params.id}/summary`),
      api<Finding[]>(`/cases/${params.id}/findings`).catch(() => []),
      api<{ nodes: GraphNode[]; edges: GraphEdge[] }>(`/cases/${params.id}/graph`).catch(() => ({ nodes: [], edges: [] })),
    ]).then(([s, f, g]) => { setData(s); setFindings(f); setGraph(g) }).catch(() => setError(true))
  }, [params.id])

  useEffect(() => { load() }, [load])

  useEffect(() => {
    if (data) {
      api<{ author: string; body: string; created_at: string }[]>(`/cases/${params.id}/notes`)
        .then(setNotes).catch(() => {})
    }
  }, [data, params.id])

  const addNote = async () => {
    if (!noteText.trim()) return
    try {
      await api(`/cases/${params.id}/notes`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ body: noteText }),
      })
      setNoteText("")
      const n = await api<{ author: string; body: string; created_at: string }[]>(`/cases/${params.id}/notes`)
      setNotes(n)
    } catch { /* ignore */ }
  }

  if (error) return <main className="p-8"><Box>Unable to load this case.</Box></main>
  if (!data) return <main className="p-8"><Box>Loading investigation...</Box></main>

  const { case: c, email, risk_score, risk_level, summary, findings_plain, explanation, ml,
    auth_results, hops, urls, attachments, intelligence, evidence_sha256, campaign,
    related_case_ids, mitre } = data

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

  const nodeColor = (type: string) => {
    const m: Record<string, string> = { Email: "bg-cyan-500/20 text-cyan-300 border-cyan-500/30", Domain: "bg-amber-500/20 text-amber-300 border-amber-500/30", URL: "bg-purple-500/20 text-purple-300 border-purple-500/30", IP: "bg-green-500/20 text-green-300 border-green-500/30", Campaign: "bg-red-500/20 text-red-300 border-red-500/30", MITRE: "bg-orange-500/20 text-orange-300 border-orange-500/30", IntelResult: "bg-blue-500/20 text-blue-300 border-blue-500/30", EvidenceHash: "bg-gray-500/20 text-gray-300 border-gray-500/30", Attachment: "bg-pink-500/20 text-pink-300 border-pink-500/30" }
    return m[type] || "bg-muted text-muted-foreground border-border"
  }

  return (
    <main className="min-h-screen bg-background p-4 md:p-8">
      <div className="mx-auto max-w-5xl space-y-4">

        <div className="flex items-center justify-between">
          <Link href="/cases" className="text-sm text-muted-foreground hover:text-foreground transition-colors">&larr; Back to Cases</Link>
          <div className="flex gap-2">
            <a href={`http://localhost:8000/api/v1/cases/${c.id}/report.pdf`} target="_blank" rel="noopener"
              className="rounded-md border border-border px-3 py-1.5 text-xs text-muted-foreground hover:bg-muted transition-colors">Download PDF</a>
          </div>
        </div>

        <div className="rounded-lg border border-border bg-card p-5">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <p className="text-xs tracking-widest text-muted-foreground">CASE {c.id.slice(0, 8).toUpperCase()}</p>
              <h1 className="mt-1 text-2xl font-bold">{c.title}</h1>
            </div>
            <div className="flex items-center gap-2">
              <span className={`rounded-full border px-3 py-1 text-xs font-medium ${statusColor}`}>{c.status}</span>
              {risk_level && <span className={`rounded-full border px-3 py-1 text-xs font-medium ${riskColor}`}>{risk_level.toUpperCase()}</span>}
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
                  <div className={`h-full rounded-full transition-all ${risk_level === "critical" ? "bg-red-500" : risk_level === "high" ? "bg-orange-500" : risk_level === "medium" || risk_level === "guarded" ? "bg-amber-500" : "bg-green-500"}`} style={{ width: `${Math.min(100, risk_score)}%` }} />
                </div>
              </div>
            </div>
          )}
          <p className="mt-3 text-sm text-muted-foreground leading-relaxed">{summary}</p>
          {explanation?.possible_attack_type && explanation.possible_attack_type.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-2">
              {explanation.possible_attack_type.map((t) => (
                <span key={t} className="rounded-full bg-red-500/10 border border-red-500/20 px-2.5 py-0.5 text-xs text-red-300 font-medium">{t}</span>
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

        {email && (
          <div className="rounded-lg border border-border bg-card overflow-hidden">
            <div className="border-b border-border bg-muted/30 px-5 py-3">
              <h2 className="text-sm font-semibold text-foreground">The Email</h2>
            </div>
            <div className="p-5 space-y-3">
              <div className="grid gap-1 text-sm">
                <Row label="From">
                  {email.from_display_name && <span className="text-foreground">{email.from_display_name} </span>}
                  <span className="text-muted-foreground">&lt;{email.from_address}&gt;</span>
                </Row>
                {email.reply_to && email.reply_to !== email.from_address && (
                  <Row label="Reply-To"><span className="text-amber-300">{email.reply_to}</span></Row>
                )}
                {email.return_path && email.return_path !== email.from_address && (
                  <Row label="Return-Path"><span className="text-amber-300">{email.return_path}</span></Row>
                )}
                <Row label="To">{email.to_addresses}</Row>
                {email.cc_addresses && <Row label="CC">{email.cc_addresses}</Row>}
                <Row label="Date">{email.date ? new Date(email.date).toLocaleString() : "Unknown"}</Row>
                <Row label="Subject"><span className="font-medium text-foreground">{email.subject || "(no subject)"}</span></Row>
              </div>
              <div className="border-t border-border pt-4">
                <div className="whitespace-pre-wrap text-sm leading-relaxed text-foreground/90 max-h-96 overflow-y-auto">
                  {email.body_text || email.body_html_sanitized || "(no content)"}
                </div>
              </div>
            </div>
          </div>
        )}

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

        {auth_results.length > 0 && (
          <Collapsible title="Authentication Results" open={openSections.auth} onToggle={() => toggle("auth")}>
            <div className="space-y-2">
              {auth_results.map((a: AuthResult, i: number) => (
                <div key={i} className="flex items-center justify-between rounded border border-border p-2.5 text-xs">
                  <div className="flex items-center gap-3">
                    <span className="font-mono font-medium text-foreground">{a.mechanism}</span>
                    {a.domain && <span className="text-muted-foreground">{a.domain}</span>}
                  </div>
                  <span className={`font-medium ${a.result === "pass" ? "text-green-400" : a.result === "fail" ? "text-red-400" : "text-amber-400"}`}>
                    {a.result?.toUpperCase()}
                  </span>
                </div>
              ))}
            </div>
          </Collapsible>
        )}

        {findings.length > 0 && (
          <Collapsible title={`Findings (${data.findings_count})`} open={openSections.auth} onToggle={() => toggle("auth")}>
            <div className="space-y-2">
              {findings.map((f, i) => (
                <div key={i} className="rounded border border-border p-2.5 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-foreground">{f.title}</span>
                    <span className="font-mono text-amber-300">+{f.score_delta}</span>
                  </div>
                  <div className="mt-1 text-muted-foreground">{f.rule_id} &middot; {f.category} &middot; confidence {Math.round(f.confidence * 100)}%</div>
                </div>
              ))}
            </div>
          </Collapsible>
        )}

        {hops.length > 0 && (
          <Collapsible title={`Received Chain (${hops.length} hops)`} open={openSections.infra} onToggle={() => toggle("infra")}>
            <div className="space-y-1">
              {hops.map((h: ReceivedHop, i: number) => (
                <div key={i} className="flex items-center gap-2 text-xs font-mono">
                  <span className="w-5 text-right text-muted-foreground">{i + 1}</span>
                  <span className="text-muted-foreground">from</span>
                  <span className="text-foreground">{h.source_host || "?"}</span>
                  {h.source_ip && <span className="text-cyan-300">({h.source_ip}{h.is_private_ip ? " *private*" : ""})</span>}
                  <span className="text-muted-foreground">by</span>
                  <span className="text-foreground">{h.destination_host || "?"}</span>
                  {h.protocol && <span className="text-muted-foreground">with {h.protocol}</span>}
                </div>
              ))}
            </div>
          </Collapsible>
        )}

        {urls.length > 0 && (
          <Collapsible title={`URLs & Domains (${urls.length})`} open={openSections.urls} onToggle={() => toggle("urls")}>
            <div className="space-y-2">
              {urls.map((u: URLIndicator) => (
                <div key={u.id} className="rounded border border-border p-2.5 text-xs">
                  <div className="font-mono text-foreground break-all">{u.normalized_url}</div>
                  <div className="mt-1 flex gap-3 text-muted-foreground">
                    {u.hostname && <span>Host: <span className="text-foreground">{u.hostname}</span></span>}
                    {u.has_userinfo && <span className="text-amber-300">Has userinfo</span>}
                    {u.is_ip_literal && <span className="text-red-300">IP literal</span>}
                    {u.is_punycode && <span className="text-amber-300">Punycode</span>}
                  </div>
                </div>
              ))}
            </div>
          </Collapsible>
        )}

        {intelligence.filter((i: ThreatIntel) => i.status === "success").length > 0 && (
          <Collapsible title="Infrastructure Intelligence" open={openSections.intel} onToggle={() => toggle("intel")}>
            <div className="space-y-2">
              {intelligence.filter((i: ThreatIntel) => i.status === "success").map((intel: ThreatIntel) => {
                const parsed = JSON.parse(intel.data_json)
                return (
                  <div key={intel.id} className="rounded border border-border p-2.5 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="font-mono font-medium text-foreground">{intel.indicator}</span>
                      <span className="text-muted-foreground">{intel.provider} &middot; {Math.round(intel.confidence * 100)}%</span>
                    </div>
                    {parsed.ip_enrichment && (
                      <div className="mt-2 space-y-1">
                        {parsed.ip_enrichment.map((ip: { ip: string; data: Record<string, string | number | null>; status: string }) => (
                          <div key={ip.ip} className="flex items-center gap-2 text-muted-foreground">
                            <span className="text-green-300">{ip.ip}</span>
                            {ip.data.country && <span>{String(ip.data.country)}</span>}
                            {ip.data.asn && <span className="text-cyan-300">{String(ip.data.asn)}</span>}
                            {ip.data.isp && <span>&middot; {String(ip.data.isp)}</span>}
                          </div>
                        ))}
                      </div>
                    )}
                    {parsed.dns?.A && <div className="mt-1 text-muted-foreground">IPs: {parsed.dns.A.join(", ")}</div>}
                    {parsed.rdap?.registrar && <div className="mt-1 text-muted-foreground">Registrar: {String(parsed.rdap.registrar)}</div>}
                  </div>
                )
              })}
            </div>
          </Collapsible>
        )}

        {graph && graph.nodes.length > 0 && (
          <Collapsible title="Investigation Graph" open={openSections.graph} onToggle={() => toggle("graph")}>
            <div className="space-y-3">
              <div className="flex flex-wrap gap-2">
                {graph.nodes.map((n: GraphNode) => {
                  const props = JSON.parse(n.properties_json)
                  return (
                    <div key={n.id} className={`rounded border px-3 py-2 text-xs ${nodeColor(n.node_type)}`}>
                      <div className="font-medium">{n.label}</div>
                      <div className="text-[10px] opacity-70">{n.node_type}{props.role && ` (${props.role})`}</div>
                    </div>
                  )
                })}
              </div>
              <div className="text-xs text-muted-foreground">
                {graph.edges.length} relationship{graph.edges.length !== 1 ? "s" : ""}:{" "}
                {Array.from(new Set(graph.edges.map((e: GraphEdge) => e.relationship_type))).join(", ")}
              </div>
            </div>
          </Collapsible>
        )}

        {campaign && (
          <Collapsible title="Related Cases & Campaign" open={openSections.campaign} onToggle={() => toggle("campaign")}>
            <div className="rounded border border-border p-3 text-xs">
              <div className="font-medium text-foreground">{campaign.name}</div>
              <div className="mt-1 text-muted-foreground">{campaign.description}</div>
              <div className="mt-1 text-muted-foreground">Confidence: {Math.round(campaign.confidence * 100)}%</div>
              {related_case_ids.length > 0 && (
                <div className="mt-2 text-muted-foreground">Related: {related_case_ids.length} other case{related_case_ids.length !== 1 ? "s" : ""}</div>
              )}
            </div>
          </Collapsible>
        )}

        {mitre.length > 0 && (
          <Collapsible title="MITRE ATT&CK" open={openSections.mitre} onToggle={() => toggle("mitre")}>
            <div className="flex flex-wrap gap-2">
              {mitre.map((m: { id: string; technique: string; reason: string; confidence: number }) => (
                <div key={m.id} className="rounded bg-muted px-2.5 py-1.5 text-xs">
                  <span className="font-mono font-medium text-foreground">{m.technique}</span>
                  <span className="ml-2 text-muted-foreground">{m.reason}</span>
                  <span className="ml-2 text-muted-foreground">({Math.round(m.confidence * 100)}%)</span>
                </div>
              ))}
            </div>
          </Collapsible>
        )}

        {attachments.length > 0 && (
          <Collapsible title={`Attachments (${attachments.length})`} open={false} onToggle={() => toggle("attachments")}>
            <div className="space-y-2">
              {attachments.map((a: AttachmentInfo) => (
                <div key={a.id} className="flex items-center justify-between rounded border border-border p-2.5 text-xs">
                  <div>
                    <span className="font-medium text-foreground">{a.filename || "unnamed"}</span>
                    <span className="ml-2 text-muted-foreground">{a.content_type} &middot; {a.size} bytes</span>
                  </div>
                  {a.sha256 && <span className="font-mono text-muted-foreground text-[10px]">{a.sha256.slice(0, 16)}...</span>}
                </div>
              ))}
            </div>
          </Collapsible>
        )}

        {evidence_sha256 && (
          <Collapsible title="Evidence & Audit" open={openSections.evidence} onToggle={() => toggle("evidence")}>
            <div className="space-y-3">
              <div>
                <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1">Evidence Fingerprint (SHA-256)</h3>
                <div className="rounded bg-muted p-2 font-mono text-xs text-foreground break-all">{evidence_sha256}</div>
              </div>
              <div className="flex gap-2">
                <a href={`http://localhost:8000/api/v1/cases/${c.id}/ledger/verify`} target="_blank" rel="noopener"
                  className="rounded border border-border px-3 py-1.5 text-xs text-muted-foreground hover:bg-muted transition-colors">
                  Verify Audit Chain
                </a>
                <a href={`http://localhost:8000/api/v1/cases/${c.id}/report.json`} target="_blank" rel="noopener"
                  className="rounded border border-border px-3 py-1.5 text-xs text-muted-foreground hover:bg-muted transition-colors">
                  JSON Report
                </a>
              </div>
            </div>
          </Collapsible>
        )}

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
            <input type="text" value={noteText} onChange={(e) => setNoteText(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && addNote()} placeholder="Add a note..."
              className="flex-1 rounded border border-border bg-muted px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring" />
            <button onClick={addNote} className="rounded bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors">Add</button>
          </div>
        </div>

      </div>
    </main>
  )
}

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return <div className="flex gap-2"><span className="w-16 shrink-0 text-muted-foreground">{label}</span><span>{children}</span></div>
}

function Collapsible({ title, open, onToggle, children }: { title: string; open: boolean; onToggle: () => void; children: React.ReactNode }) {
  return (
    <div className="rounded-lg border border-border bg-card overflow-hidden">
      <button onClick={onToggle} className="flex w-full items-center justify-between px-5 py-3 text-left text-sm font-semibold text-foreground hover:bg-muted/30 transition-colors">
        <span>{title}</span>
        <span className="text-muted-foreground text-xs">{open ? "▲" : "▼"}</span>
      </button>
      {open && <div className="border-t border-border p-5">{children}</div>}
    </div>
  )
}

function Box({ children }: { children: React.ReactNode }) {
  return <div className="rounded-lg border border-border bg-card p-8 text-sm text-muted-foreground">{children}</div>
}
