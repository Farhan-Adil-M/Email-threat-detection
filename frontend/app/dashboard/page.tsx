"use client"
import { useEffect, useState } from "react"
import { api, Case } from "@/lib/api"

export default function DashboardPage() {
  const [cases, setCases] = useState<Case[] | null>(null)
  const [error, setError] = useState(false)
  useEffect(() => { api<Case[]>("/cases").then(setCases).catch(() => setError(true)) }, [])
  const open = cases?.filter((item) => !["RESOLVED", "FALSE_POSITIVE"].includes(item.status)).length ?? 0
  return (
    <main className="min-h-screen bg-background p-8">
      <div className="mx-auto max-w-7xl space-y-8">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Investigation Dashboard</h1>
          <p className="text-muted-foreground">SOC overview of suspicious email cases.</p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <MetricCard label="Open Cases" value={cases ? String(open) : "—"} />
          <MetricCard label="High Risk" value={cases ? String(cases.filter((item) => item.severity === "high").length) : "—"} />
          <MetricCard label="Active Campaigns" value="—" />
          <MetricCard label="Indicators Observed" value="—" />
        </div>

        <div className="rounded-lg border border-border bg-card p-6">
          <h2 className="text-lg font-semibold text-card-foreground">Recent Investigations</h2>
          {error ? <p className="text-sm text-red-400">Backend unavailable. Core UI is ready; retry when the API is online.</p> : <p className="text-sm text-muted-foreground mt-2">{cases?.length ? `${cases.length} investigations loaded.` : "No cases yet. Upload a .eml file through the API docs to start."}</p>}
        </div>
      </div>
    </main>
  )
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-border bg-card p-6">
      <p className="text-sm text-muted-foreground">{label}</p>
      <p className="mt-2 text-3xl font-bold text-card-foreground">{value}</p>
    </div>
  )
}
