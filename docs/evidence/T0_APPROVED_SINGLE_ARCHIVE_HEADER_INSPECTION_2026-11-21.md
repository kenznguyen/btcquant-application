# T0 Approved Single-Archive Header Inspection — Implementation Record

Date: 2026-11-21  
Status: **WORKFLOW CREATED / STATIC REVIEW PARTIAL / DISPATCH NOT AVAILABLE THROUGH CONNECTED GITHUB ACTIONS TOOLS**

## Owner authorization and scope

Following the owner's affirmative approval, create one dedicated manual workflow to inspect exactly:
- ZIP: `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2022-08.zip`
- Paired sidecar: the exact `.zip.CHECKSUM` object.

Pinned ZIP metadata from approved inventory blob `eb251ac0924b46add906123f99b82e054d887a59`:
- Expected size: 143,927 bytes.
- Expected SHA-256: `517e241a31c2062c50ca9861eb832fa9b3505b0ae67350135d5a74d812228eab`.
- Expected data rows after the first record: 2,976.

## Workflow

Path: `.github/workflows/t0-approved-single-archive-header-inspection.yml`  
Creation commit: `8332f9e10c1844f40f92273134724bb65aa184e1`  
Workflow blob: `c40ed95b707e6a67165d6b2007fc2001e2e38225`  
Parent: `b56bd519501711f463662353a43e6579d7b92494`

The workflow:
- Has only `workflow_dispatch`, read-only `contents: read`, GitHub-hosted `ubuntu-24.04`, timeout and concurrency guard.
- Uses the already pinned checkout/setup-python/upload-artifact actions and no secrets.
- Verifies exact approved source ancestry and inventory blob SHA.
- Requests only the exact ZIP and its paired sidecar over HTTPS; validates ZIP size/SHA, sidecar digest, ZIP CRC, one safe CSV member, UTF-8/BOM, newline convention, exactly 12 fields in the first record, all subsequent rows have 12 nonblank fields, and 2,976 data rows.
- Writes only a diagnostic JSON containing the exact ordered 12-field first record and provenance/encoding metadata. It does not write/upload ZIP, sidecar, full CSV, or data rows.
- Labels the first record `HEADER_CANDIDATE_REQUIRES_MANUAL_SCHEMA_REVIEW`; it does not freeze a schema or silently normalize labels.
- Does not invoke the parser, SQLite, importer, REST tail, Canonical T0, T1/T2, VPS/runtime, deployment, credentials or trading.

## Static review

- Exact one ZIP key and one sidecar key: **PASS** by source inspection.
- One Binance base URL and exact object-key variables: **PASS** by source inspection.
- No other sample archive keys: **PASS** by source inspection.
- Ordered first-record field capture and manual-review marker: **PASS** by source inspection.
- Workflow YAML/actionlint validation: **NOT RUN**.
- Workflow dispatch: **NOT RUN**. The connected GitHub tools available in this session expose repository file writes and run/log/artifact reads, but no new workflow_dispatch operation.
- Archive retrieval: **NOT RUN**.
- Exact header labels/order: **NOT VERIFIED**.
- Header contract freeze: **BLOCKED**.
- TDD implementation: **NOT AUTHORIZED**.

## Next step

Manually dispatch this dedicated workflow exactly once from GitHub Actions on `main`, then inspect the run, job log and diagnostic artifact. The artifact should contain the first CSV record's 12 ordered fields. Review that record against the source and inventory evidence; only then propose a canonical header tuple and normalization policy for separate owner approval. Do not dispatch the previous six-archive workflow.

## Explicit non-actions

No archive or REST request was made by this implementation step. No parser/test change, SQLite/database, importer, staging dataset, Contract 1.2.0 implementation, Canonical T0, T1/T2, VPS/runtime, deployment, exchange credentials or trading operation occurred.
