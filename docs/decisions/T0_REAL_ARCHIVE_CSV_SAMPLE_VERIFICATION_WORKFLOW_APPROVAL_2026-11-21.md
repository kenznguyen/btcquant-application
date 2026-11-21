# Owner approval — T0 real archive CSV sample verification workflow

Date: 2026-11-21

Status: **APPROVED FOR ONE MANUAL WORKFLOW; DISPATCH NOT YET AUTHORIZED**

## Decision

The owner explicitly approved creating exactly one GitHub Actions workflow with a `workflow_dispatch` trigger, solely to verify the six previously allowlisted Binance USD-M BTCUSDT archive ZIPs and their six paired `.CHECKSUM` sidecars (12 objects total).

The workflow must:
- Run on a GitHub-hosted ephemeral runner.
- Download only the six exact ZIP object keys and their six paired sidecar keys recorded in the approved sample decision and provenance inventory.
- Verify ZIP byte size and SHA-256 against the pinned inventory; verify each sidecar's asserted ZIP digest and record the sidecar's own size and SHA-256.
- Verify ZIP CRC, safe single CSV member, UTF-8 encoding/BOM, delimiter, newline convention, header presence, exact column count, row count, and full-file parsing using the pinned provisional parser.
- Preserve a diagnostic JSON report as the only uploaded artifact; never upload raw ZIP, sidecar, or CSV payloads.
- Use read-only repository permissions, no secrets, no REST tail, no personal host/VPS, and no automatic or scheduled trigger.

## Explicit exclusions

This approval does not authorize:
- Any trigger other than `workflow_dispatch`, or automatic dispatch.
- Fetching any object other than the exact 12-object allowlist.
- Full 404-object archive materialization or wildcard/list operations.
- Binance REST tail retrieval or inclusion.
- SQLite/database creation or mutation, importer implementation, Contract 1.2.0 implementation/freeze, or Canonical T0 replacement/modification.
- T1/T2 integration, runtime start, deployment, exchange credentials, or trading.
- Raw source archive upload or durable retention of source payloads.

## Evidence and next gate

The workflow file is:
`.github/workflows/t0-real-archive-csv-sample-verification.yml`

Creating the workflow does not run it. Dispatch remains a separate explicit action; no archive request is made until a manual run is started. Parser contract freeze and importer remain blocked pending review of the resulting real-source evidence and a separate owner decision.
