"use client"
import { useEffect, useState, useMemo } from "react"
import Link from "next/link"
import { api, Case } from "@/lib/api"

type SortKey = "created_at" | "title" | "severity"
type SortDir = "asc" | "desc"

const SEVERITY_ORDER: Record<string, number> = { critical: 0, high: 1, medium: 2, guarded: 3, low: 4, "": 5 }
const STATUS_COLORS: Record<string, string> = {
  INVESTIGATING: "bg-red-500/20 text-red-300",
  TRIAGED: "bg-amber-500/20 text-amber-300",
  FALSE_POSITIVE: "bg-green-500/20 text-green-300",
  RESOLVED: "bg-blue-500/20 text-blue-300",
  CONTAINED: "bg-purple-500/20 text-purple-300",
  NEW: "bg-muted text-muted-foreground",
}

export default function CasesPage() {
  const [cases, setCases] = useState<Case[]>([])
  const [error, setError] = useState(false)
  const [loading, setLoading] = useState(true)

  const [search, setSearch] = useState("")
  const [statusFilter, setStatusFilter] = useState("ALL")
  const [severityFilter, setSeverityFilter] = useState("ALL")
  const [sortKey, setSortKey] = useState<SortKey>("created_at")
  const [sortDir, setSortDir] = useState<SortDir>("desc")
  const [page, setPage] = useState(1)
  const PAGE_SIZE = 25

  useEffect(() => {
    const load = async () => {
      try {
        const all: Case[] = []
        let p = 1
        while (true) {
          const batch = await api<Case[]>(`/cases?page=${p}&page_size=100`)
          if (!batch || batch.length === 0) break
          all.push(...batch)
          if (batch.length < 100) break
          p++
        }
        setCases(all)
      } catch { setError(true) }
      finally { setLoading(false) }
    }
    load()
  }, [])

  const filtered = useMemo(() => {
    let result = cases
    if (search) {
      const q = search.toLowerCase()
      result = result.filter(c => c.title.toLowerCase().includes(q) || c.id.toLowerCase().includes(q))
    }
    if (statusFilter !== "ALL") result = result.filter(c => c.status === statusFilter)
    if (severityFilter !== "ALL") result = result.filter(c => (c.severity || "") === severityFilter)

    result.sort((a, b) => {
      let cmp = 0
      if (sortKey === "title") cmp = a.title.localeCompare(b.title)
      else if (sortKey === "severity") cmp = (SEVERITY_ORDER[a.severity || ""] ?? 5) - (SEVERITY_ORDER[b.severity || ""] ?? 5)
      else cmp = new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
      return sortDir === "desc" ? -cmp : cmp
    })
    return result
  }, [cases, search, statusFilter, severityFilter, sortKey, sortDir])

  const totalPages = Math.ceil(filtered.length / PAGE_SIZE)
  const pageItems = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE)

  const statuses = useMemo(() => {
    const s = new Set(cases.map(c => c.status))
    return ["ALL", ...Array.from(s).sort()]
  }, [cases])

  const severities = useMemo(() => {
    const s = new Set(cases.map(c => c.severity || ""))
    return ["ALL", ...Array.from(s).sort()]
  }, [cases])

  const toggleSort = (key: SortKey) => {
    if (sortKey === key) setSortDir(d => d === "asc" ? "desc" : "asc")
    else { setSortKey(key); setSortDir("desc") }
  }

  const SortIcon = ({ active, dir }: { active: boolean; dir: SortDir }) => (
    <span className={`ml-1 text-xs ${active ? "text-foreground" : "text-muted-foreground/40"}`}>
      {active ? (dir === "asc" ? "▲" : "▼") : "⇅"}
    </span>
  )

  return (
    <main className="min-h-screen bg-background p-4 md:p-8">
      <div className="mx-auto max-w-7xl space-y-5">
        <div>
          <h1 className="text-3xl font-bold">Cases</h1>
          <p className="text-muted-foreground text-sm">{filtered.length} investigation{filtered.length !== 1 ? "s" : ""} found</p>
        </div>

        {error && <Box>Unable to load cases. Check that the backend is running.</Box>}
        {loading && <Box>Loading investigations...</Box>}

        {!loading && !error && (
          <>
            {/* Filters */}
            <div className="flex flex-wrap items-center gap-3">
              <input
                type="text"
                value={search}
                onChange={e => { setSearch(e.target.value); setPage(1) }}
                placeholder="Search by name or ID..."
                className="rounded border border-border bg-card px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring w-64"
              />
              <select
                value={statusFilter}
                onChange={e => { setStatusFilter(e.target.value); setPage(1) }}
                className="rounded border border-border bg-card px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
              >
                {statuses.map(s => <option key={s} value={s}>{s === "ALL" ? "All Statuses" : s}</option>)}
              </select>
              <select
                value={severityFilter}
                onChange={e => { setSeverityFilter(e.target.value); setPage(1) }}
                className="rounded border border-border bg-card px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
              >
                {severities.map(s => <option key={s} value={s}>{s === "ALL" ? "All Severities" : s || "unassigned"}</option>)}
              </select>
              {(search || statusFilter !== "ALL" || severityFilter !== "ALL") && (
                <button
                  onClick={() => { setSearch(""); setStatusFilter("ALL"); setSeverityFilter("ALL"); setPage(1) }}
                  className="text-xs text-muted-foreground hover:text-foreground transition-colors"
                >
                  Clear filters
                </button>
              )}
            </div>

            {/* Table */}
            {pageItems.length === 0 ? (
              <Box>No cases match your filters.</Box>
            ) : (
              <div className="overflow-hidden rounded-lg border border-border bg-card">
                <table className="w-full text-left text-sm">
                  <thead className="border-b border-border text-muted-foreground">
                    <tr>
                      <th className="p-4 cursor-pointer hover:text-foreground transition-colors" onClick={() => toggleSort("title")}>
                        Case <SortIcon active={sortKey === "title"} dir={sortDir} />
                      </th>
                      <th className="cursor-pointer hover:text-foreground transition-colors" onClick={() => toggleSort("severity")}>
                        Severity <SortIcon active={sortKey === "severity"} dir={sortDir} />
                      </th>
                      <th>Status</th>
                      <th className="cursor-pointer hover:text-foreground transition-colors" onClick={() => toggleSort("created_at")}>
                        Created <SortIcon active={sortKey === "created_at"} dir={sortDir} />
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {pageItems.map(item => (
                      <tr key={item.id} className="border-b border-border/60 hover:bg-muted/40 transition-colors">
                        <td className="p-4">
                          <Link className="text-primary hover:underline font-medium" href={`/cases/${item.id}`}>
                            {item.title}
                          </Link>
                          <div className="text-xs text-muted-foreground font-mono mt-0.5">{item.id.slice(0, 8)}</div>
                        </td>
                        <td>
                          <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${
                            item.severity === "critical" ? "bg-red-500/20 text-red-300" :
                            item.severity === "high" ? "bg-orange-500/20 text-orange-300" :
                            item.severity === "medium" || item.severity === "guarded" ? "bg-amber-500/20 text-amber-300" :
                            item.severity === "low" ? "bg-green-500/20 text-green-300" :
                            "bg-muted text-muted-foreground"
                          }`}>
                            {item.severity || "unassigned"}
                          </span>
                        </td>
                        <td>
                          <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_COLORS[item.status] || "bg-muted text-muted-foreground"}`}>
                            {item.status}
                          </span>
                        </td>
                        <td className="text-xs text-muted-foreground whitespace-nowrap">
                          {new Date(item.created_at).toLocaleDateString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between text-sm text-muted-foreground">
                <span>Page {page} of {totalPages}</span>
                <div className="flex gap-2">
                  <button
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="rounded border border-border px-3 py-1 text-xs hover:bg-muted disabled:opacity-40 transition-colors"
                  >
                    Previous
                  </button>
                  <button
                    onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                    disabled={page === totalPages}
                    className="rounded border border-border px-3 py-1 text-xs hover:bg-muted disabled:opacity-40 transition-colors"
                  >
                    Next
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </main>
  )
}

function Box({ children }: { children: React.ReactNode }) {
  return <div className="rounded-lg border border-border bg-card p-8 text-sm text-muted-foreground">{children}</div>
}
