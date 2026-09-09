import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "SENTINEL — Email Threat Detection",
  description: "SIH 26106 forensic investigation platform",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" className="dark">
      <body className={inter.className}>
        <header className="border-b border-border bg-card/80 px-6 py-4">
          <nav className="mx-auto flex max-w-7xl items-center justify-between">
            <a href="/" className="font-bold tracking-[0.25em] text-primary">SENTINEL</a>
            <div className="flex gap-5 text-sm text-muted-foreground">
              <a href="/dashboard" className="hover:text-foreground">Dashboard</a>
              <a href="/cases" className="hover:text-foreground">Cases</a>
              <a href="/investigate" className="hover:text-foreground">Investigate</a>
              <a href="/reports" className="hover:text-foreground">Reports</a>
              <a href="/settings" className="hover:text-foreground">Settings</a>
            </div>
          </nav>
        </header>
        {children}
      </body>
    </html>
  )
}
