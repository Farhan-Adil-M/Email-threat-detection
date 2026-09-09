#!/usr/bin/env python3
"""Populate campaigns, threat intel, and MITRE mappings for all cases."""
import json
import urllib.request
import urllib.error

BASE = "http://localhost:8000/api/v1"


def api(method, path, data=None, headers=None):
    url = f"{BASE}{path}"
    hdrs = headers or {}
    body = None
    if data:
        hdrs["Content-Type"] = "application/json"
        body = json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read()) if e.read() else {}
    except Exception:
        return 0, {}


def login():
    _, r = api("POST", "/auth/login", {"username": "analyst", "password": "change-me-analyst"})
    return {"Authorization": f"Bearer {r['data']['access_token']}"}


def main():
    headers = login()
    cases = []
    page = 1
    while True:
        _, r = api("GET", f"/cases?page={page}&page_size=100", headers=headers)
        batch = r.get("data", [])
        if not batch:
            break
        cases.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    print(f"Found {len(cases)} cases")

    enriched = 0
    correlated = 0
    mapped = 0

    for i, case in enumerate(cases):
        cid = case["id"]

        # Enrich
        status, _ = api("POST", f"/cases/{cid}/enrich", headers=headers)
        if status == 200:
            enriched += 1

        # Correlate
        status, _ = api("POST", f"/cases/{cid}/correlate", headers=headers)
        if status == 200:
            correlated += 1

        # MITRE
        status, _ = api("POST", f"/cases/{cid}/mitre", headers=headers)
        if status == 200:
            mapped += 1

        if (i + 1) % 20 == 0:
            print(f"  Processed {i+1}/{len(cases)}...")

    print(f"\nDone:")
    print(f"  Enriched: {enriched} cases")
    print(f"  Correlated: {correlated} cases")
    print(f"  MITRE mapped: {mapped} cases")

    _, stats = api("GET", "/dashboard/stats", headers=headers)
    stats = stats.get("data", {})
    print(f"\nDashboard stats:")
    print(f"  Total cases: {stats.get('total_cases', 0)}")
    print(f"  Open cases: {stats.get('open_cases', 0)}")
    print(f"  Campaigns: {len(stats.get('campaigns', []))}")
    ind = stats.get("indicators", {})
    print(f"  Indicators: {ind.get('total', 0)} ({ind.get('unique_domains', 0)} domains, {ind.get('unique_ips', 0)} IPs)")
    print(f"  MITRE techniques: {stats.get('mitre_techniques', 0)}")
    print(f"  Risk distribution: {stats.get('risk_distribution', {})}")


if __name__ == "__main__":
    main()
