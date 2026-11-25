# T0 S1.2 independent review snapshot

- Review purpose: source-only independent review of the S1.2 SQLite staging schema, DTO adapter, S3/V1 projection, graph validator, synthetic tests and CI.
- Tested implementation source SHA: `284d9d243d529b84de4318e65266993fad71a757`.
- Review snapshot base: `564fda608153c668b217ef4a205228d3947ce35a`.
- All executable source/test/workflow blobs in this snapshot are byte-for-byte identical to their original files on main and to the tested implementation SHA. Design/evidence docs are copied from current main at the review snapshot base.
- Exact-SHA CI: [run 45011049882](https://github.com/kenznguyen/btcquant-application/actions/runs/45010072833), job `137173247655`, SUCCESS; importer-core 20/20, adapter 43/43, staging schema 32/32, full market_data 496/496; artifact count 0.
- The physical schema spec includes owner-approved Amendments A/B, exact 11 tables, 8 indexes, and exactly two append-only triggers.
- Review request: assess correctness, test adequacy, design/source parity, deterministic projection, graph completeness, transaction atomicity, disposable-path security, identity/digest grammar, schema fingerprinting and fail-closed behavior. Report severity, exact snapshot path/line, reproduction, impact and remediation. Return APPROVE / REQUEST CHANGES / NOT VERIFIED. State reviewer independence.
- Known unresolved design decision: candidate snapshot digest preimage/serialization is not specified by the approved design. Current implementation checks digest shape/presence and CANDIDATE↔VALIDATED equality; it intentionally does not recompute the digest.
- Restrictions: review only. Do not modify source, execute tests against real data, access archive/sidecar files, open Canonical T0, perform host/workstation/runner preflight, run B8, access VPS, deploy, use credentials/exchange, connect T1/T2 runtime or enable trading.
- **DO NOT MERGE.** This branch contains only byte-for-byte review snapshots and this scope manifest; no production-path code changes.

F7 additionally verifies rollback when append-only authorizer installation fails; authorizer setup now occurs before COMMIT.

## Source-to-snapshot blob mapping

| Original path | Original Git blob SHA | Snapshot blob SHA | Identical |
|---|---|---|---|
| `market_data/archive_staging_schema.py` | `f530f4f2f394dfb018e5bc750d04974df8b1adcd` | `f530f4f2f394dfb018e5bc750d04974df8b1adcd` | YES |
| `market_data/test_archive_staging_schema.py` | `e1555b424aacb15b06894ddfc34a99b2989e9ad5` | `e1555b424aacb15b06894ddfc34a99b2989e9ad5` | YES |
| `market_data/archive_staging_adapter.py` | `70bcf83c37936593e394c8476134046a7da70f4c` | `70bcf83c37936593e394c8476134046a7da70f4c` | YES |
| `market_data/test_archive_staging_adapter.py` | `19cd18b40cb61252094b5805eb9d3cc35a7ff39b` | `19cd18b40cb61252094b5805eb9d3cc35a7ff39b` | YES |
| `market_data/archive_provenance_validator.py` | `b94bac0f82ae141984552409f99a5cff70435b3b` | `b94bac0f82ae141984552409f99a5cff70435b3b` | YES |
| `market_data/test_archive_provenance_validator_s1_red.py` | `41f5b21eaa418bb32f4f40e00de7e920ca39c4bf` | `41f5b21eaa418bb32f4f40e00de7e920ca39c4bf` | YES |
| `.github/workflows/t0-importer-core-synthetic.yml` | `0e319368fc36d8752f8e1640c3dd513dc18fd0ce` | `0e319368fc36d8752f8e1640c3dd513dc18fd0ce` | YES |
| `docs/design/T0_ARCHIVE_STAGING_S1_2_PROVENANCE_IMPORTER_PHYSICAL_SCHEMA_SPEC_2026-11-22.md` | `2cff982c7503d47a3d13e102ac8e76f64e3f794f` | `2cff982c7503d47a3d13e102ac8e76f64e3f794f` | YES |
| `docs/design/T0_ARCHIVE_STAGING_S1_2_COMPATIBILITY_AMENDMENT_A_2026-11-22.md` | `6f9476f696962c88f27421cdf83fb42a6b4f794f` | `6f9476f696962c88f27421cdf83fb42a6b4f794f` | YES |
| `docs/design/T0_ARCHIVE_STAGING_S1_2_APPEND_ONLY_TRIGGER_COMPATIBILITY_AMENDMENT_B_2026-11-22.md` | `6d633e5f0e72ab47255076b09125570279d779d3` | `6d633e5f0e72ab47255076b09125570279d779d3` | YES |
| `docs/design/T0_S1_2_F2_ADAPTER_GRAPH_IMPLEMENTATION_CONTRACT_2026-11-22.md` | `e8194c2e1cc0322859ff100cca88f39e8f63cacb` | `e8194c2e1cc0322859ff100cca88f39e8f63cacb` | YES |
| `docs/decisions/T0_S1_2_ADAPTER_SQLITE_STAGING_OWNER_AUTHORIZATION_2026-11-22.md` | `afb1059e2f4b1307e878ac6a7b6592cf40fd1ebe` | `afb1059e2f4b1307e878ac6a7b6592cf40fd1ebe` | YES |
| `docs/reviews/T0_S1_2_SQLITE_STAGING_SCHEMA_SELF_REVIEW_D7CDEA3_2026-11-22.md` | `0dddc314446465f384b7122f933ef0e807f85177` | `0dddc314446465f384b7122f933ef0e807f85177` | YES |
| `docs/evidence/T0_S1_2_F2_DTO_READONLY_PROJECTION_CI_2026-11-22.md` | `5b79763df422940ee0a18ef9a202f038f167c7c3` | `5b79763df422940ee0a18ef9a202f038f167c7c3` | YES |
