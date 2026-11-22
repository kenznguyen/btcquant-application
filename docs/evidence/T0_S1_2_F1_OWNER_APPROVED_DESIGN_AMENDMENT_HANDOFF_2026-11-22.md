# S1.2 progress handoff addendum — 2026-11-22

## F1 — owner-approved append-only trigger design amendment

- Owner decision in this conversation: retain the two SQLite append-only triggers and amend S1.2 §4.1 to permit exactly those triggers.
- Amendment: `docs/design/T0_ARCHIVE_STAGING_S1_2_APPEND_ONLY_TRIGGER_COMPATIBILITY_AMENDMENT_B_2026-11-22.md`.
- Amendment commit: `37e54c419ea41064aa9c1d2eb68ec50b3489be52`.
- Design baseline reviewed: `d7cdea3a467aa0ee2a8b177aaec23fdfea3201ce`.
- Relevant source: `market_data/archive_staging_schema.py`; exact trigger DDL remains `trg_run_events_no_update` and `trg_run_events_no_delete`. Both are included in the ordered fingerprint manifest and exact schema verifier.
- Decision: F1 design contradiction **RESOLVED**. F1 implementation/tests are **NOT RE-RUN AFTER AMENDMENT**; the existing synthetic coverage is documented in Amendment B and must be rechecked during the next exact-SHA TDD/CI cycle.
- Tests/workflows: documentation-only change; **NOT RUN**. Workflow run/job/artifact: **NONE**.
- Source SHA remains `d7cdea3a467aa0ee2a8b177aaec23fdfea3201ce` for the reviewed implementation; the amendment commit is documentation only.
- S1.2 remains **NOT FROZEN**. Independent review **NOT RUN**.
- Next authorized step: complete F2 immutable DTOs, DB-to-S3/V1 projection and graph validator; then synthetic TDD for F1–F7, exact-SHA CI/full `market_data` regression, and independent review.
- Exclusions unchanged: B8, real archives/sidecars, host/workstation/runner preflight or provisioning, real-data build, uploads/deletion, Canonical T0, MAY-10, REST tail, T1/T2, VPS/runtime, credentials, exchange and trading.
