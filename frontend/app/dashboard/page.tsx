"use client"
import { useEffect, useState } from "react"
import Link from "next/link"
import { api, DashboardStats } from "@/lib/api"

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [error, setError] = useState(false)

  useEffect(() => {
    api<DashboardStats>("/dashboard/stats").then(setStats).catch(() => setError(true))
  }, [])

  if (error) return <main className="p-8"><Box>Backend unavailable. Core UI is ready; retry when the API is online.</Box></main>
  if (!stats) return <main className="p-8"><Box>Loading dashboard...</Box></main>

  const severityColors: Record<string, string> = {
    critical: "text-red-400", high: "text-orange-400", medium: "text-amber-400",
    guarded: "text-amber-300", low: "text-green-400", unassigned: "text-muted-foreground",
  }

  const statusColors: Record<string, string> = {
    INVESTIGATING: "bg-red-500/20 text-red-300", TRIAGED: "bg-amber-500/20 text-amber-300",
    FALSE_POSITIVE: "bg-green-500/20 text-green-300", RESOLVED: "bg-blue-500/20 text-blue-300",
    NEW: "bg-muted text-muted-foreground", CONTAINED: "bg-purple-500/20 text-purple-300",
  }

  return (
    <main className="min-h-screen bg-background p-4 md:p-8">
      <div className="mx-auto max-w-7xl space-y-6">

        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-foreground">Investigation Dashboard</h1>
          <p className="text-muted-foreground text-sm">SOC overview of suspicious email cases</p>
        </div>

        {/* Top Metrics */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <MetricCard label="Total Cases" value={String(stats.total_cases)} color="text-foreground" />
          <MetricCard label="Open Cases" value={String(stats.open_cases)} color="text-amber-400" />
          <MetricCard label="Active Campaigns" value={String(stats.campaigns.length)} color="text-red-400" />
          <MetricCard label="Indicators Observed" value={String(stats.indicators.total)} color="text-blue-400" />
        </div>

        {/* Risk Distribution + Severity */}
        <div className="grid gap-4 lg:grid-cols-2">
          {/* Risk Distribution */}
          <div className="rounded-lg border border-border bg-card p-5">
            <h2 className="text-sm font-semibold text-foreground mb-4">Risk Distribution</h2>
            <div className="space-y-3">
              {["critical", "high", "medium", "guarded", "low"].map(level => {
                const count = stats.risk_distribution[level] || 0
                const pct = stats.total_cases > 0 ? (count / stats.total_cases) * 100 : 0
                const barColor = level === "critical" ? "bg-red-500" : level === "high" ? "bg-orange-500"
                  : level === "medium" ? "bg-amber-500" : level === "guarded" ? "bg-amber-400" : "bg-green-500"
                return (
                  <div key={level}>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-muted-foreground capitalize">{level}</span>
                      <span className="text-foreground">{count}</span>
                    </div>
                    <div className="h-2 w-full rounded-full bg-muted overflow-hidden">
                      <div className={`h-full rounded-full ${barColor} transition-all`} style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Severity Breakdown */}
          <div className="rounded-lg border border-border bg-card p-5">
            <h2 className="text-sm font-semibold text-foreground mb-4">Severity Breakdown</h2>
            <div className="space-y-2">
              {Object.entries(stats.severity_counts).sort(([,a],[,b]) => b - a).map(([sev, count]) => (
                <div key={sev} className="flex items-center justify-between rounded border border-border p-2.5">
                  <span className={`text-sm font-medium capitalize ${severityColors[sev] || "text-foreground"}`}>{sev}</span>
                  <span className="text-sm text-foreground">{count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Active Campaigns */}
        {stats.campaigns.length > 0 && (
          <div className="rounded-lg border border-border bg-card p-5">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-semibold text-foreground">Active Campaigns</h2>
              <span className="text-xs text-muted-foreground">{stats.campaigns.length} detected</span>
            </div>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {stats.campaigns.slice(0, 6).map(c => (
                <div key={c.id} className="rounded border border-border p-3 space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-sm text-foreground">{c.name}</span>
                    <span className="text-xs text-muted-foreground">{c.case_count} cases</span>
                  </div>
                  <p className="text-xs text-muted-foreground line-clamp-2">{c.description}</p>
                  <div className="flex items-center gap-2 text-xs">
                    <span className="text-muted-foreground">Confidence:</span>
                    <span className="text-foreground">{Math.round(c.confidence * 100)}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Indicators Observed */}
        <div className="rounded-lg border border-border bg-card p-5">
          <h2 className="text-sm font-semibold text-foreground mb-4">Indicators Observed</h2>
          <div className="grid gap-4 sm:grid-cols-3 mb-4">
            <div className="rounded border border-border p-3 text-center">
              <p className="text-2xl font-bold text-blue-400">{stats.indicators.unique_domains}</p>
              <p className="text-xs text-muted-foreground mt-1">Unique Domains</p>
            </div>
            <div className="rounded border border-border p-3 text-center">
              <p className="text-2xl font-bold text-green-400">{stats.indicators.unique_ips}</p>
              <p className="text-xs text-muted-foreground mt-1">Unique IPs</p>
            </div>
            <div className="rounded border border-border p-3 text-center">
              <p className="text-2xl font-bold text-purple-400">{stats.indicators.unique_urls}</p>
              <p className="text-xs text-muted-foreground mt-1">Unique URLs</p>
            </div>
          </div>
          {stats.indicators.top_domains.length > 0 && (
            <div>
              <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">Top Observed Domains</h3>
              <div className="flex flex-wrap gap-2">
                {stats.indicators.top_domains.slice(0, 15).map(d => (
                  <span key={d} className="rounded bg-muted px-2 py-1 font-mono text-xs text-foreground">{d}</span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* MITRE ATT&CK Techniques */}
        {Object.keys(stats.mitre_techniques).length > 0 && (
          <div className="rounded-lg border border-border bg-card p-5">
            <h2 className="text-sm font-semibold text-foreground mb-4">MITRE ATT&CK Techniques Observed</h2>
            <div className="flex flex-wrap gap-3">
              {Object.entries(stats.mitre_techniques).sort(([,a],[,b]) => b - a).map(([tech, count]) => (
                <div key={tech} className="rounded border border-border p-3 text-center">
                  <p className="font-mono text-sm font-bold text-foreground">{tech}</p>
                  <p className="text-xs text-muted-foreground mt-1">{count} case{count !== 1 ? "s" : ""}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Recent Investigations */}
        <div className="rounded-lg border border-border bg-card p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-foreground">Recent Investigations</h2>
            <Link href="/cases" className="text-xs text-primary hover:underline">View all &rarr;</Link>
          </div>
          <div className="space-y-2">
            {stats.recent_cases.slice(0, 8).map(c => (
              <Link key={c.id} href={`/cases/${c.id}`} className="flex items-center justify-between rounded border border-border p-3 hover:bg-muted/40 transition-colors">
                <div className="flex items-center gap-3 min-w-0">
                  <span className={`inline-block h-2 w-2 shrink-0 rounded-full ${
                    c.severity === "critical" ? "bg-red-500" :
                    c.severity === "high" ? "bg-orange-500" :
                    c.severity === "guarded" || c.severity === "medium" ? "bg-amber-500" :
                    "bg-green-500"
                  }`} />
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-foreground truncate">{c.title}</p>
                    <p className="text-xs text-muted-foreground font-mono">{c.id.slice(0, 8)}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${statusColors[c.status] || "bg-muted text-muted-foreground"}`}>
                    {c.status}
                  </span>
                </div>
              </Link>
            ))}
          </div>
        </div>

      </div>
    </main>
  )
}

function MetricCard({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div className="rounded-lg border border-border bg-card p-5">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className={`mt-2 text-3xl font-bold ${color || "text-card-foreground"}`}>{value}</p>
    </div>
  )
}

function Box({ children }: { children: React.ReactNode }) {
  return <div className="rounded-lg border border-border bg-card p-8 text-sm text-muted-foreground">{children}</div>
}
