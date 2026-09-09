---
name: email-forensics
description: Use when parsing email headers, reconstructing Received chains, analyzing SPF/DKIM/DMARC, or normalizing forensic evidence. RFC-aware email analysis with raw evidence preservation.
---

# Skill: Email Forensics

## Purpose

- RFC-aware email analysis
- Header parsing
- Received-chain reconstruction
- Authentication interpretation
- Evidence normalization

## Rules

- Preserve raw evidence at every step.
- Never infer beyond available fields.
- Maintain source references for every extracted value.
- Distinguish parsed data from conclusions.
- Distinguish: observed header vs parsed interpretation vs inference.

## Header fields of interest

- From
- To
- CC
- Reply-To
- Return-Path
- Subject
- Date
- Message-ID
- Authentication-Results
- Received
- DKIM-Signature

## Received-chain

- Display newest/oldest ordering clearly.
- Extract source host, destination host, source IP, timestamps, protocol markers where reliable.
- Identify private/reserved addresses, missing data, malformed entries, suspicious inconsistencies.
- Do not assume every hop is trustworthy.

## Authentication

- Parse SPF, DKIM, DMARC results and alignment.
- Policy and explanation are evidence, not proof of malice.

## Adversarial robustness

- Missing From / Date
- Multiple Reply-To / Return-Path
- Malformed Received
- Private IP in Received
- Loop-like Received chain
- Duplicate Message-ID
- Long header values
- Folded headers
- Broken / nested MIME
- Empty body
- Mixed encoding

The parser must not crash.
