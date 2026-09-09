"use client"
import { useEffect, useState } from "react"
import Link from "next/link"
import { api, Case } from "@/lib/api"

export default function CasesPage() {
  const [cases, setCases] = useState<Case[] | null>(null)
  const [error, setError] = useState(false)
  useEffect(() => { api<Case[]>("/cases").then(setCases).catch(() => setError(true)) }, [])
  return <main className="min-h-screen bg-background p-8"><div className="mx-auto max-w-7xl space-y-6">
    <div><h1 className="text-3xl font-bold">Cases</h1><p className="text-muted-foreground">Investigation queue and analyst triage.</p></div>
    {error && <State text="Unable to load cases. Check that the backend is running." />}
    {!cases && !error && <State text="Loading investigations…" />}
    {cases?.length === 0 && <State text="No investigations yet." />}
    {cases && cases.length > 0 && <div className="overflow-hidden rounded-lg border border-border bg-card"><table className="w-full text-left text-sm"><thead className="border-b border-border text-muted-foreground"><tr><th className="p-4">Case</th><th>Status</th><th>Severity</th><th>Created</th></tr></thead><tbody>{cases.map((item) => <tr key={item.id} className="border-b border-border/60 hover:bg-muted/40"><td className="p-4"><Link className="text-primary hover:underline" href={`/cases/${item.id}`}>{item.title}</Link><div className="text-xs text-muted-foreground">{item.id}</div></td><td>{item.status}</td><td>{item.severity || "unassigned"}</td><td>{new Date(item.created_at).toLocaleString()}</td></tr>)}</tbody></table></div>}
  </div></main>
}
function State({ text }: { text: string }) { return <div className="rounded-lg border border-border bg-card p-8 text-sm text-muted-foreground">{text}</div> }
