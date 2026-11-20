# T0 Candle Contract — Graphify Review Snapshot

<badge>DO NOT MERGE</badge>

## Purpose

This is a review-only, byte-for-byte mirror of six files from source commit `fc2e48420c6bbd00b7c5cfbaa8b3d7b2fc996235`, created so Graphify can review the exact T0 Candle Contract implementation without changing production paths or moving the repository's main branch.

The PR head is a review wrapper based on `main`. The original source commit is recorded below and each mirrored file is copied verbatim from that commit. Review the mirrored files as the source; do not treat this wrapper commit as a new implementation.

## Exact source identity

- Repository: `kenznguyen/btcquant-application`
- Source commit: `fc2e48420c6bbd00b7c5cfbaa8b3d7b2fc996235`
- Snapshot folder: `review-snapshots/t0-candle-contract-2026-11-20/`
- Base branch: `main`
- Review branch: `review/t0-candle-contract-graphify-20261120`

## Source-to-mirror mapping

| Original path | Mirrored path | Original Git blob SHA |
|---|---|---|
| `market_data/api_contract.py` | `review-snapshots/t0-candle-contract-2026-11-20/market_data/api_contract.py` | `4297ab173fee6f7ee78ef759217c229cd58eb4e4` |
| `market_data/fastapi_app.py` | `review-snapshots/t0-candle-contract-2026-11-20/market_data/fastapi_app.py` | `e0b607770004a4c1b01c1368c5dce268298d89a3` |
| `pipeline/api.py` | `review-snapshots/t0-candle-contract-2026-11-20/pipeline/api.py` | `887901302fc767750568933232daebb947902ee1` |
| `market_data/test_api_contract.py` | `review-snapshots/t0-candle-contract-2026-11-20/market_data/test_api_contract.py` | `856e8b7ae8932df6e081fe012ee962a0cf509dea` |
| `pipeline/test_api.py` | `review-snapshots/t0-candle-contract-2026-11-20/pipeline/test_api.py` | `8c4b4c3d0cb16cbd53a87ff40aafb35473b73bb7` |
| `market_data/README.md` | `review-snapshots/t0-candle-contract-2026-11-20/market_data/README.md` | `6561214efdca5108672b83809a9c12047462d72b` |

## Review requirements

Review five axes: correctness, readability/simplicity, architecture, security, and performance.

Focus on:
- Fail-closed validation of timestamps, freshness, timeframe grids, and evaluation boundaries.
- Contract envelope consistency between FastAPI and the application adapter.
- Error handling, malformed/empty input, boundary timestamps, and response semantics.
- Authentication and trust boundaries; no accidental exposure of secrets or permissive fallbacks.
- Resource bounds, query limits, pagination/window limits, and hot-path cost.
- Whether tests assert externally observable behavior and cover failure paths.

Return one explicit verdict: **APPROVE**, **REQUEST CHANGES**, or **NOT VERIFIED**. For every finding include severity, mirrored file/line, impact, evidence, and remediation. Distinguish blocking findings from optional suggestions.

## Verification evidence (author-provided; not a substitute for review)

- FastAPI Contract Regression: workflow run `44728558303`, 65/65 PASS; artifact `14625231382`; artifact SHA-256 `4454a5f5dea5e71d2d35210ca362945c3f2b1dfe313c70e12eefa87bf99e3e10`.
- T0 SQLite aggregate: workflow run `44728445702`, 174/174 PASS.
- These test results do not constitute independent review and do not certify runtime/production readiness.

## Strict restrictions

- **DO NOT MERGE this PR.** It is a review-only mirror.
- Do not copy mirrored files back into production paths.
- No source/runtime edits, CI dispatch, deployment, VPS/network access, credentials, canonical SQLite access, T1/T2 connection, PostgreSQL activation, trading, or data lifecycle changes are authorized.
- No live orders; no runtime activation.
- The review must evaluate the exact source snapshot identified by the source commit and blob SHAs above. If any mirrored blob differs, stop and report **NOT VERIFIED**.
