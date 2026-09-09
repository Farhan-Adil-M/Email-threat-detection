# Performance Notes v0

The MVP records no fabricated SLA. Relevant timings to instrument next are upload, parse, enrichment, risk, graph, and report generation. Uploads are bounded at 25 MB; intelligence indicators are capped at 50 per case; DNS timeout defaults to 2 seconds. Optional provider failures do not block deterministic analysis.
