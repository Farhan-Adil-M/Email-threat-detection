#!/usr/bin/env python3
"""Batch upload and analyze all fixture .eml files for demo."""
import glob
import json
import sys
import urllib.request
import urllib.error
import urllib.parse

BASE = "http://localhost:8000/api/v1"
FIXTURES = glob.glob("backend/data/fixtures/*.eml")


def api(method, path, data=None, headers=None, body=None):
    url = f"{BASE}{path}"
    hdrs = headers or {}
    if data:
        hdrs["Content-Type"] = "application/json"
        body = json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read()) if e.read() else {}


def upload_multipart(path, headers):
    import mimetypes
    boundary = "----SentinelBatchBoundary"
    filename = path.split("/")[-1]
    with open(path, "rb") as f:
        file_data = f.read()
    content_type = mimetypes.guess_type(path)[0] or "message/rfc822"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: {content_type}\r\n\r\n"
    ).encode() + file_data + f"\r\n--{boundary}--\r\n".encode()
    url = f"{BASE}/evidence/upload"
    hdrs = {**headers, "Content-Type": f"multipart/form-data; boundary={boundary}"}
    req = urllib.request.Request(url, data=body, headers=hdrs, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read()) if e.read() else {}


def login():
    _, r = api("POST", "/auth/login", {"username": "analyst", "password": "change-me-analyst"})
    token = r["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def upload(headers, path):
    status, r = upload_multipart(path, headers)
    if status == 200:
        return r["data"]["case_id"]
    else:
        print(f"  [SKIP] {path}: {status}")
        return None


def analyze(headers, case_id):
    api("POST", f"/cases/{case_id}/analyze", headers=headers)


def ml_analyze(headers, case_id):
    api("POST", f"/cases/{case_id}/ml-analyze", headers=headers)


def risk(headers, case_id):
    status, d = api("POST", f"/cases/{case_id}/risk", headers=headers)
    if status == 200:
        return d["data"]["risk_score"], d["data"]["risk_level"]
    return None, None


def explanation(headers, case_id):
    api("POST", f"/cases/{case_id}/graph", headers=headers)


def update_case(headers, case_id, status=None, severity=None, tags=None):
    payload = {}
    if status: payload["status"] = status
    if severity: payload["severity"] = severity
    if tags: payload["tags"] = tags
    if payload:
        api("PATCH", f"/cases/{case_id}", data=payload, headers=headers)


def add_note(headers, case_id, body):
    api("POST", f"/cases/{case_id}/notes", data={"body": body}, headers=headers)


def build_graph(headers, case_id):
    api("POST", f"/cases/{case_id}/graph", headers=headers)


def build_mitre(headers, case_id):
    api("POST", f"/cases/{case_id}/mitre", headers=headers)


def build_report(headers, case_id):
    api("GET", f"/cases/{case_id}/report.json", headers=headers)


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

        status = "NEW"
        if score and score >= 70:
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
