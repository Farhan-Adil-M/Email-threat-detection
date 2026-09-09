import Link from "next/link"

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-background p-8">
      <div className="max-w-2xl text-center space-y-6">
        <h1 className="text-4xl font-bold tracking-tight text-foreground sm:text-6xl">
          SENTINEL
        </h1>
        <p className="text-lg text-muted-foreground">
          AI-Powered Email Threat Detection, Geolocation & Forensic Intelligence Platform
        </p>
        <p className="text-sm text-muted-foreground">
          SIH 26106 — Detect · Explain · Trace · Correlate · Preserve · Report
        </p>
        <div className="flex justify-center gap-4">
          <Link
            href="/dashboard"
            className="rounded-md bg-primary px-6 py-3 text-sm font-medium text-primary-foreground hover:bg-primary/90"
          >
            Open Dashboard
          </Link>
        </div>
      </div>
    </main>
  )
}
