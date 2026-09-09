#!/usr/bin/env python3
"""Populate campaigns, threat intel, and MITRE mappings for all cases."""
import requests
import json

BASE = "http://localhost:8000/api/v1"


def login():
    r = requests.post(f"{BASE}/auth/login", json={"username": "analyst", "password": "change-me-analyst"})
    r.raise_for_status()
    return {"Authorization": f"Bearer {r.json()['data']['access_token']}"}


def main():
    headers = login()
    # Fetch all cases with pagination
    cases = []
    page = 1
    while True:
        r = requests.get(f"{BASE}/cases?page={page}&page_size=100", headers=headers)
        batch = r.json()["data"]
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
        name = case["title"]

        # Skip false positives for enrichment
        if case["status"] == "FALSE_POSITIVE":
            continue

        # Enrich (threat intel)
        try:
            r = requests.post(f"{BASE}/cases/{cid}/enrich", headers=headers, timeout=10)
            if r.status_code == 200:
                data = r.json()["data"]
                if data:
                    enriched += 1
        except Exception:
            pass

        # Correlate (campaigns)
        try:
            r = requests.post(f"{BASE}/cases/{cid}/correlate", headers=headers, timeout=10)
            if r.status_code == 200:
                data = r.json()["data"]
                if data:
                    correlated += 1
        except Exception:
            pass

        # MITRE mapping
        try:
            r = requests.post(f"{BASE}/cases/{cid}/mitre", headers=headers, timeout=10)
            if r.status_code == 200:
                data = r.json()["data"]
                if data:
                    mapped += 1
        except Exception:
            pass

        if (i + 1) % 20 == 0:
            print(f"  Processed {i+1}/{len(cases)}...")

    print(f"\nDone:")
    print(f"  Enriched: {enriched} cases")
    print(f"  Correlated: {correlated} cases")
    print(f"  MITRE mapped: {mapped} cases")

    # Fetch dashboard stats
    r = requests.get(f"{BASE}/dashboard/stats", headers=headers)
    stats = r.json()["data"]
    print(f"\nDashboard stats:")
    print(f"  Total cases: {stats['total_cases']}")
    print(f"  Open cases: {stats['open_cases']}")
    print(f"  Campaigns: {len(stats['campaigns'])}")
    print(f"  Indicators: {stats['indicators']['total']} ({stats['indicators']['unique_domains']} domains, {stats['indicators']['unique_ips']} IPs)")
    print(f"  MITRE techniques: {stats['mitre_techniques']}")
    print(f"  Risk distribution: {stats['risk_distribution']}")


if __name__ == "__main__":
    main()
