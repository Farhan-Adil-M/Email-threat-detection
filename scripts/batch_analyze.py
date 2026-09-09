#!/usr/bin/env python3
"""Batch upload and analyze all fixture .eml files for demo."""
import requests
import glob
import json
import time
import sys

BASE = "http://localhost:8000/api/v1"
FIXTURES = glob.glob("data/fixtures/*.eml")


def login():
    r = requests.post(f"{BASE}/auth/login", json={"username": "analyst", "password": "change-me-analyst"})
    r.raise_for_status()
    token = r.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def upload(headers, path):
    with open(path, "rb") as f:
        r = requests.post(f"{BASE}/evidence/upload", headers=headers, files={"file": f})
    if r.status_code == 200:
        return r.json()["data"]["case_id"]
    else:
        print(f"  [SKIP] {path}: {r.status_code} {r.text[:120]}")
        return None


def analyze(headers, case_id):
    requests.post(f"{BASE}/cases/{case_id}/analyze", headers=headers)


def ml_analyze(headers, case_id):
    requests.post(f"{BASE}/cases/{case_id}/ml-analyze", headers=headers)


def risk(headers, case_id):
    r = requests.post(f"{BASE}/cases/{case_id}/risk", headers=headers)
    if r.status_code == 200:
        d = r.json()["data"]
        return d["risk_score"], d["risk_level"]
    return None, None


def explanation(headers, case_id):
    r = requests.post(f"{BASE}/cases/{case_id}/graph", headers=headers)


def update_case(headers, case_id, status=None, severity=None, tags=None):
    payload = {}
    if status: payload["status"] = status
    if severity: payload["severity"] = severity
    if tags: payload["tags"] = tags
    if payload:
        requests.patch(f"{BASE}/cases/{case_id}", headers=headers, json=payload)


def add_note(headers, case_id, body):
    requests.post(f"{BASE}/cases/{case_id}/notes", headers=headers, json={"body": body})


def build_graph(headers, case_id):
    requests.post(f"{BASE}/cases/{case_id}/graph", headers=headers)


def build_mitre(headers, case_id):
    requests.post(f"{BASE}/cases/{case_id}/mitre", headers=headers)


def build_report(headers, case_id):
    requests.get(f"{BASE}/cases/{case_id}/report.json", headers=headers)


def main():
    headers = login()
    print(f"Logged in. Processing {len(FIXTURES)} fixtures...\n")

    results = []
    for i, path in enumerate(sorted(FIXTURES)):
        name = path.split("/")[-1].replace(".eml", "")
        print(f"[{i+1}/{len(FIXTURES)}] {name}...", end=" ", flush=True)

        case_id = upload(headers, path)
        if not case_id:
            continue

        analyze(headers, case_id)
        ml_analyze(headers, case_id)
        score, level = risk(headers, case_id)
        explanation(headers, case_id)
        build_graph(headers, case_id)
        build_mitre(headers, case_id)
        build_report(headers, case_id)

        # Set varied statuses for dashboard variety
        status = "NEW"
        if "legitimate" in name or "newsletter" in name or "receipt" in name:
            status = "FALSE_POSITIVE"
            update_case(headers, case_id, status=status, severity="info", tags=["legitimate"])
            add_note(headers, case_id, "Automated analysis confirms this is a legitimate email. No threats detected.")
        elif score and score >= 70:
            status = "INVESTIGATING"
            update_case(headers, case_id, status=status, severity="critical", tags=["high-priority", "automated-triage"])
            add_note(headers, case_id, f"High-risk email detected (score: {score}). Automated triage flagged for investigation.")
        elif score and score >= 40:
            status = "TRIAGED"
            update_case(headers, case_id, status=status, severity="warning", tags=["needs-review"])
            add_note(headers, case_id, f"Medium-risk email (score: {score}). Requires manual review.")
        else:
            status = "NEW"
            update_case(headers, case_id, status=status, severity="low")

        risk_display = f"{score} ({level})" if score else "N/A"
        print(f"OK | {risk_display} | {status}")
        results.append({"name": name, "case_id": case_id, "score": score, "level": level, "status": status})

    print(f"\n{'='*60}")
    print(f"Processed {len(results)} cases")

    # Summary stats
    scores = [r["score"] for r in results if r["score"] is not None]
    levels = {}
    statuses = {}
    for r in results:
        if r["level"]:
            levels[r["level"]] = levels.get(r["level"], 0) + 1
        statuses[r["status"]] = statuses.get(r["status"], 0) + 1

    if scores:
        print(f"Score range: {min(scores)} - {max(scores)}")
        print(f"Average score: {sum(scores)/len(scores):.1f}")
    print(f"Risk levels: {json.dumps(levels, indent=2)}")
    print(f"Case statuses: {json.dumps(statuses, indent=2)}")
    print(f"\nDashboard: http://localhost:3000/cases")
    print(f"API docs:  http://localhost:8000/docs")


if __name__ == "__main__":
    main()
