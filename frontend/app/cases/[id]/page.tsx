"use client"
import { useEffect, useState } from "react"
import { api, Case, Finding } from "@/lib/api"

export default function CasePage({ params }: { params: { id: string } }) {
  const [item, setItem] = useState<Case | null>(null)
  const [findings, setFindings] = useState<Finding[] | null>(null)
  const [error, setError] = useState(false)
  useEffect(() => { Promise.all([api<Case>(`/cases/${params.id}`), api<Finding[]>(`/cases/${params.id}/findings`)]).then(([c, f]) => { setItem(c); setFindings(f) }).catch(() => setError(true)) }, [params.id])
  if (error) return <main className="p-8"><State text="Unable to load this case." /></main>
  if (!item) return <main className="p-8"><State text="Loading investigation…" /></main>
  return <main className="min-h-screen bg-background p-8"><div className="mx-auto max-w-7xl space-y-6">
    <section className="rounded-lg border border-border bg-card p-6"><div className="flex flex-wrap items-start justify-between gap-4"><div><p className="text-xs tracking-widest text-muted-foreground">CASE {item.id.slice(0, 8).toUpperCase()}</p><h1 className="mt-2 text-3xl font-bold">{item.title}</h1></div><div className="rounded-full border border-red-500/40 px-4 py-2 text-sm text-red-300">{item.severity || "UNASSESSED"}</div></div><div className="mt-5 flex gap-3 text-sm text-muted-foreground"><span>Status: {item.status}</span><span>Created: {new Date(item.created_at).toLocaleString()}</span></div></section>
    <section className="grid gap-6 lg:grid-cols-[1.3fr_1fr]"><div className="rounded-lg border border-border bg-card p-6"><h2 className="text-lg font-semibold">Risk breakdown</h2><p className="mt-2 text-sm text-muted-foreground">Deterministic evidence contributions are shown below. ML signals remain separate.</p><div className="mt-5 space-y-3">{findings?.map((finding) => <div key={finding.rule_id} className="flex items-center justify-between border-b border-border/60 pb-3"><div><p className="font-medium">{finding.title}</p><p className="text-xs text-muted-foreground">{finding.rule_id} · confidence {Math.round(finding.confidence * 100)}%</p></div><span className="font-mono text-amber-300">+{finding.score_delta}</span></div>)}</div></div><div className="rounded-lg border border-border bg-card p-6"><h2 className="text-lg font-semibold">Investigation graph</h2><div className="mt-5 flex h-48 items-center justify-center rounded border border-dashed border-border text-center text-sm text-muted-foreground">Graph drilldown available through the API. Visual graph surface is next.</div></div></section>
  </div></main>
}
function State({ text }: { text: string }) { return <div className="rounded-lg border border-border bg-card p-8 text-sm text-muted-foreground">{text}</div> }
