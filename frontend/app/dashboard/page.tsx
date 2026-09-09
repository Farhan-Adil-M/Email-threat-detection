export default function DashboardPage() {
  return (
    <main className="min-h-screen bg-background p-8">
      <div className="mx-auto max-w-7xl space-y-8">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Investigation Dashboard</h1>
          <p className="text-muted-foreground">SOC overview of suspicious email cases.</p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <MetricCard label="Open Cases" value="0" />
          <MetricCard label="High Risk" value="0" />
          <MetricCard label="Active Campaigns" value="0" />
          <MetricCard label="Indicators Observed" value="0" />
        </div>

        <div className="rounded-lg border border-border bg-card p-6">
          <h2 className="text-lg font-semibold text-card-foreground">Recent Investigations</h2>
          <p className="text-sm text-muted-foreground mt-2">No cases yet. Upload a .eml file to start an investigation.</p>
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
