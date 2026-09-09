# Final Clean Demo Checklist

```bash
sudo docker compose down -v
sudo docker compose up -d --build
curl http://localhost:8000/api/v1/health
```

1. Open `http://localhost:3000/dashboard`.
2. Upload `backend/data/fixtures/bec.eml` through `/docs`.
3. Analyze the case.
4. Run ML, risk, graph, MITRE, and report endpoints.
5. Verify the ledger.
6. Open the case workspace at `/cases/{id}`.

All demo data is synthetic and provider output is explicitly labeled.
