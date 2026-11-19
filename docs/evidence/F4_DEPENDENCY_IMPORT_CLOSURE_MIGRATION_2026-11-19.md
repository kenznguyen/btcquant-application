# F4 Dependency Closure — Minimal Provenance Migration — 2026-11-19

## Approval and scope
Owner approved option A: migrate only the three previously identified missing modules needed to close the selected F4 Pipeline import paths. Preserve source bytes exactly; no business-logic edits.

- Target: `kenznguyen/btcquant-application`, existing branch `main`.
- Target parent before this increment: `5fe6dd0a190205aa59d45be88f8769917332b5c0`.
- Source: `kenznguyen/btcusdt-telegram-signals2`, branch `feature/t0-centralized-data-feeder-p1-20261101`, exact source HEAD `5223cef02f0e296c4f58afc5d7992b9c641ab208`.
- No legacy history, workflows, dependency manifests, database/data payloads, runtime configuration, or unrelated components were copied.
- No T0 canonical assets or legacy source files were modified.

## Migrated files and provenance

| Target path | Source blob SHA | Target blob SHA | Result |
|---|---|---|---|
| `futures_intelligence/import_collector.py` | `5effe6540b86edcb190456c95b6bb11456aec099` | `5effe6540b86edcb190456c95b6bb11456aec099` | Exact match |
| `integrations/hummingbot_bridge.py` | `aa9db7522ffb7ce911c7fbbdc73a7f9b47401331` | `aa9db7522ffb7ce911c7fbbdc73a7f9b47401331` | Exact match |
| `market_data/test_support.py` | `64b99a858eb4ddc9d6275957cbb048a1cfc1843d` | `64b99a858eb4ddc9d6275957cbb048a1cfc1843d` | Exact match |

The three target blobs were created from source content fetched at the exact source HEAD above. Git blob identity confirms byte-for-byte preservation.

## Static import-closure result

The previously blocked import paths now have their identified modules present:

- `pipeline/test_api.py` imports `futures_intelligence.import_collector.build_snapshot` and `market_data.test_support.seed_candles`.
- `pipeline/test_decision.py` imports `market_data.test_support.seed_candles`, and imports `HEADERS` / `build_snapshot` from `futures_intelligence.import_collector`.
- `pipeline/api.py` has a lazy integration path to `integrations.hummingbot_bridge`; the adapter module is now present.
- The importer’s local dependency `pipeline.values` and the test helper’s `market_data.store` are present in the target snapshot.
- No `__init__.py` was added: the existing repository’s package layout already uses namespace-compatible directories, and adding package markers was not required by the inspected import statements.

This is a static path-presence assessment only. It does not prove successful imports, runtime behavior, dependency compatibility, or integration correctness.

## Verification and limits

- Source branch/HEAD read: PASS.
- Source file content fetched at exact source HEAD: PASS.
- Three source/target blob identities: PASS (3/3 exact).
- Static presence of the three previously missing import targets: PASS.
- Python import execution, tests, compile, build, CI/workflows: NOT RUN / NOT VERIFIED.
- Third-party dependency closure and supported Python version: NOT VERIFIED.
- Pipeline API runtime integration, Hummingbot upstream connectivity, dashboard assets: NOT VERIFIED.
- F4-R1/R2/R3: remain open and uncorrected.
- Core-First remains controlling: Strategy Core only in current paper path; AI offline research only; no AI Ledger writes or paper orders; `AI_EXECUTION_ENABLED=false`.
- Runtime/database/VPS/exchange: NOT ACCESSED.
- Paper execution: NOT AUTHORIZED. Live trading: PROHIBITED.

**Disposition: MINIMAL SOURCE MIGRATION PASS; STATIC IMPORT PATHS PRESENT; FUNCTIONAL VERIFICATION NOT VERIFIED.**
