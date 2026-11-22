# CURRENT STATUS OVERRIDE — 2026-11-22 — reverse-insert multi-row ordering GREEN; candidate digest formula unresolved

- Latest test SHA: `912ed3208851837302d979c4b4fa29f90e0effdf`; test blob `e5019a825bb262f8f7f4173eb7568234dc836dfc`; adapter blob `0ddd724c7e69d681333fa845c91a83852dd3420c`.
- Exact-SHA CI run [45008220039](https://github.com/kenznguyen/btcquant-application/actions/runs/45008220039), job `137164470095`, SUCCESS; checkout SHA matches.
- Runtime CPython 3.13.18 / SQLite 3.45.1; importer-core 20/20, adapter 33/33, schema 14/14, full regression 468/468 PASS; artifacts 0.
- Multi-row test inserts objects, attempts, successful-attempt relations, run events and failure observations in reverse order; projection returns deterministic order.
- Multi-row permutation coverage for pairs, members, source_rows, candles and links still NOT VERIFIED (explicit SQL ordering exists, but no multi-row fixtures yet).
- Graph negative tests include lifecycle timestamps/snapshot consistency, orphan and noncontiguous failure observations, missing successful attempt, pair/member/source-row reference breaks, and candle-link mismatch.
- Candidate snapshot hash preimage/serialization remains undefined in approved design; only shape/presence and equality between CANDIDATE and VALIDATED events are checked. Do not invent digest formula.
- F2 **PARTIAL / SYNTHETIC CI PASS**; S1.2 **NOT FROZEN**; independent review **NOT RUN**; B8 **NOT APPROVED**; real-data build **NOT AUTHORIZED**.
- Evidence: `docs/evidence/T0_S1_2_F2_DTO_READONLY_PROJECTION_CI_2026-11-22.md`.
- Next: multi-row permutations for remaining relations, full F1–F7 remediation tests, exact-SHA full regression, independent review. Candidate snapshot formula needs owner-approved amendment before recomputation.
- All exclusions remain unchanged: no real archive/sidecar access/acquisition, host/workstation/SSH/filesystem/runner preflight, B8 workflow/dispatch/runner, real-data staging, uploads/deletion/cleanup, Canonical T0, MAY-10, REST tail, T1/T2 runtime, VPS/deployment, credentials, exchange or trading.

---

# CURRENT STATUS OVERRIDE — 2026-11-22 — graph negative-invariant matrix GREEN; candidate snapshot formula remains unresolved

- Latest graph-test source SHA: `3e08ba4f9e326a9978d119cba54138cff0281f5e`; test blob `d78c20e561fe921d73e9636a61fa7ca75f7b85cc`; adapter source blob `0ddd724c7e69d681333fa845c91a83852dd3420c`.
- Exact-SHA run [45008115272](https://github.com/kenznguyen/btcquant-application/actions/runs/45008115272), job `137164142899`, SUCCESS; checkout SHA matches.
- Runtime CPython 3.13.18 / SQLite 3.45.1; importer-core 20/20, adapter 33/33, schema 14/14, full `market_data` regression 468/468 PASS; artifacts 0.
- Negative graph tests now cover nonmonotonic event times, orphan failure observation, failure ordinal gaps, missing successful-attempt relation, missing pair object, missing member pair, missing source-row member and link/candle mismatch.
- S3/V1 complete synthetic fixture and populated SQLite all-eleven-relation mapping remain GREEN at prior exact SHAs `1fade80a7c57348a0da605fbc292ad0ceb9d5efe` and `6a71fe066e0ce80f9b3d580404682e5e2c216976`.
- Remaining gaps: exhaustive multi-row/multiplicity ordering across all relations and all graph failure branches; candidate snapshot digest preimage/serialization is not defined by approved design, so recomputation is not implemented; final F1–F7 re-run and independent review pending.
- F2 **PARTIAL / SYNTHETIC CI PASS**; S1.2 **NOT FROZEN**; independent review **NOT RUN**; B8 **NOT APPROVED**; real-data build **NOT AUTHORIZED**.
- Evidence: `docs/evidence/T0_S1_2_F2_DTO_READONLY_PROJECTION_CI_2026-11-22.md`.
- Next: add multi-row relation ordering and remaining graph negative tests; do not invent candidate snapshot hash formula. Once synthetic scope is complete, exact-SHA full regression and independent review; separately request owner approval for the digest contract.
- All prior exclusions remain unchanged: no real archive/sidecar access/acquisition, host/workstation/SSH/filesystem/runner preflight, B8 workflow/dispatch/runner, real-data staging, uploads/deletion/cleanup, Canonical T0, MAY-10, REST tail, T1/T2 runtime, VPS/deployment, credentials, exchange or trading.

---

# CURRENT STATUS OVERRIDE — 2026-11-22 — canonical manifest + run lifecycle binding GREEN; snapshot digest formula unresolved

- Latest tested source SHA: `589adf4124eb186df6f072069fdb5193a9953c3a`; adapter source blob `0ddd724c7e69d681333fa845c91a83852dd3420c`; adapter test blob `0bcac7250f493e3a81cb57540f573bdee18bee1f`.
- RED: canonical-manifest/lifecycle digest tests at `4752235995044868b5d059f5f9bd9661c5ce4f28`, run [45007845805](https://github.com/kenznguyen/btcquant-application/actions/runs/45007845805), job `137163340224`; candidate snapshot consistency test at `218790587755ad17ea318394c6a3335037596d70`, run [45007966306](https://github.com/kenznguyen/btcquant-application/actions/runs/45007966306), job `137163690155`.
- GREEN: run [45008004977](https://github.com/kenznguyen/btcquant-application/actions/runs/45008004977), job `137163809455`, SUCCESS; exact SHA checkout matches.
- Runtime CPython 3.13.18 / SQLite 3.45.1; importer-core 20/20, adapter 25/25, schema 14/14, full `market_data` regression 460/460 PASS; artifacts 0.
- Added deterministic compact sorted-key coverage-manifest JSON enforcement; VALIDATED event requires validator payload SHA; CANDIDATE/VALIDATED snapshot hashes must match; duplicate VALIDATED event rejected.
- Critical unresolved design: candidate snapshot digest preimage/serialization is not defined in approved design. Current graph validator checks SHA field validity/presence and CANDIDATE↔VALIDATED equality only; it does not recompute digest. Do not invent a formula. Requires owner-approved amendment before implementing recomputation.
- F2 **PARTIAL**; S1.2 **NOT FROZEN**; independent review **NOT RUN**; B8 **NOT APPROVED**; real-data staging **NOT AUTHORIZED**.
- Evidence: `docs/evidence/T0_S1_2_F2_DTO_READONLY_PROJECTION_CI_2026-11-22.md`.
- Next: continue synthetic graph invariant tests (multi-row ordering, failed/quarantined branches, orphan/duplicate failure observations, event transitions) while retaining digest recomputation as a design blocker; then run all F1–F7 tests at final exact SHA and request independent review.
- All previous exclusions remain unchanged: no real archive/sidecar access/acquisition, host/workstation/SSH/filesystem/runner preflight, B8 workflow/dispatch/runner, real-data staging, uploads/deletion/cleanup, Canonical T0, MAY-10, REST tail, T1/T2 runtime, VPS/deployment, credentials, exchange or trading.

---

# CURRENT STATUS OVERRIDE — 2026-11-22 — populated SQLite → eleven DTO relations GREEN; F2 still needs exhaustive graph cases/review

- Latest test source SHA: `6a71fe066e0ce80f9b3d580404682e5e2c216976`; test blob `69d708a198c201059df34e6210c699f9e533e2ac`; adapter source blob `78e82833fded534fc777dee2d2c7ed90dfd7ac61`.
- Exact-SHA CI run [45007736688](https://github.com/kenznguyen/btcquant-application/actions/runs/45007736688), job `137162999481`, SUCCESS; checkout SHA matches.
- Runtime CPython 3.13.18 / SQLite 3.45.1; importer-core 20/20, adapter 22/22, staging schema 14/14, full `market_data` regression 457/457 PASS; artifacts 0.
- New disposable in-memory DB integration test inserts synthetic rows in all eleven relations and verifies populated DB→DTO mapping, deterministic ordering, raw inventory bytes, raw_fields_json, connection ownership and transaction preservation.
- S3/V1 projection and graph validator already passed the 404/202 synthetic fixture at source SHA `1fade80a7c57348a0da605fbc292ad0ceb9d5efe`, run `45007572947`, job `137162475080`, adapter 21/21 and full regression 456/456 PASS.
- Remaining gaps: exhaustive graph negative cases; multi-row deterministic ordering/edge cases for every relation; canonical coverage-manifest JSON verification; candidate snapshot digest binding; all F1–F7 tests after current source changes; independent review.
- F2 **PARTIAL / SYNTHETIC CI PASS**; S1.2 **NOT FROZEN**; independent review **NOT RUN**; B8 **NOT APPROVED**; real-data build **NOT AUTHORIZED**.
- Evidence: `docs/evidence/T0_S1_2_F2_DTO_READONLY_PROJECTION_CI_2026-11-22.md`.
- Next: close candidate snapshot/coverage-manifest binding and event transition matrix with synthetic TDD; expand multi-row ordering and relation edge tests; then exact-SHA full regression and independent review.
- All exclusions remain unchanged: no real archive/sidecar access/acquisition, host/workstation/SSH/filesystem/runner preflight, B8 workflow/dispatch/runner, real-data staging, uploads/deletion/cleanup, Canonical T0, MAY-10, REST tail, T1/T2 runtime, VPS/deployment, credentials, exchange or trading.

---

# CURRENT STATUS OVERRIDE — 2026-11-22 — S3/V1 projection + graph validator synthetic GREEN; SQLite populated mapping remains open

- Latest complete S3/V1 integration test SHA: `1fade80a7c57348a0da605fbc292ad0ceb9d5efe`; test blob `f1d656b5845fcf441ee0cd1aa0c3d8988877f2fd`. Adapter implementation source at preceding GREEN SHA `1fcf708216bf52ba7807532bcd799e569aa8ca01`; adapter blob `78e82833fded534fc777dee2d2c7ed90dfd7ac61`.
- S3/graph RED: commit `d59ed7a0dbff8e3534e8d8419a424129c0db00aa`, run [45007382883](https://github.com/kenznguyen/btcquant-application/actions/runs/45007382883), job `137161868207`; expected missing API tests failed.
- First implementation GREEN: run [45007483528](https://github.com/kenznguyen/btcquant-application/actions/runs/45007483528), job `137162183334`, SUCCESS; exact SHA `1fcf708216bf52ba7807532bcd799e569aa8ca01`; 20 importer-core, 20 adapter, 14 schema, 455 full regression PASS.
- Complete synthetic S1 fixture GREEN: run [45007572947](https://github.com/kenznguyen/btcquant-application/actions/runs/45007572947), job `137162475080`, SUCCESS; exact SHA `1fade80a7c57348a0da605fbc292ad0ceb9d5efe`; 20 importer-core, 21 adapter, 14 schema, 456 full regression PASS.
- Fixture exercised 404 inventory objects, 404 attempts, 202 pairs, 202 members, 202 rows, 202 candles and 202 links; physical DTO→unchanged S3/V1 payload passed existing `validate_provenance()`; graph validator accepted event/attempt/pair/member/source-row/candle/link graph. Artifacts: 0.
- Implemented APIs: `build_s3_v1_payload(projection)`, `validate_staging_graph(projection)`, `project_staging_s3_v1_payload(connection)`. No S3/V1 contract fields or validator implementation changed.
- Remaining: no populated disposable SQLite integration test yet for all eleven physical row mappers; graph negative cases not exhaustive; candidate snapshot digest binding and canonical coverage-manifest validation require additional explicit tests.
- F2 **PARTIAL**; S1.2 **NOT FROZEN**; independent review **NOT RUN**; B8 **NOT APPROVED**; real-data build **NOT AUTHORIZED**.
- Evidence: `docs/evidence/T0_S1_2_F2_DTO_READONLY_PROJECTION_CI_2026-11-22.md`.
- Next: create one disposable in-memory schema-v2 fixture with populated synthetic rows across all eleven relations, verify deterministic DB→DTO mapping and exact raw byte/JSON preservation, then test graph negative cases and candidate snapshot/coverage-manifest binding.
- All prior exclusions remain unchanged: no real archive/sidecar access/acquisition, host/workstation/SSH/filesystem/runner preflight, B8 workflow/dispatch/runner, real-data staging, uploads/deletion/cleanup, Canonical T0, MAY-10, REST tail, T1/T2 runtime, VPS/deployment, credentials, exchange or trading.

---

# CURRENT STATUS OVERRIDE — 2026-11-22 — F2 strict immutable DTO validation GREEN; payload/graph still open

- Latest tested source SHA: `a5f628b1c85c33879a9469ee1a6f90577f53d5d1`; adapter source blob `c29463798b5e21f0421ab1433a2f2de2a7f23a84`; adapter tests blob `13f48580d447239a6d7011b18e652bba082e7c9e`.
- Strict DTO test RED: commit `88e214e0e02a5dbbfe5d3839bac3953b92251fd7`, run [45007175284](https://github.com/kenznguyen/btcquant-application/actions/runs/45007175284), job `137161232664`; exact SHA checkout verified; strict constructor assertions failed as expected.
- GREEN: run [45007240516](https://github.com/kenznguyen/btcquant-application/actions/runs/45007240516), job `137161422988`, SUCCESS, exact checkout SHA matches.
- Runtime CPython 3.13.18 / SQLite 3.45.1; importer-core 20/20, adapter 18/18, schema 14/14, full `market_data` regression 453/453 PASS; artifacts 0.
- Strict DTO base validation now enforces required/nullability/type/integer/digest/flag/HTTP/singleton constraints across all eleven physical DTOs.
- F2 remains **PARTIAL**. Row mapping is tested for singleton run and empty relations, but not yet for populated rows across all relations. S3/V1 payload assembly and graph validator remain **NOT IMPLEMENTED**. Independent review **NOT RUN**. S1.2 **NOT FROZEN**. B8 **NOT APPROVED**.
- Evidence: `docs/evidence/T0_S1_2_F2_DTO_READONLY_PROJECTION_CI_2026-11-22.md`.
- Next: add tests first for S3/V1 payload assembly and graph validation; then implement mappings and event/cross-record invariants. Keep exact-SHA CI and full regression.
- All prior exclusions unchanged: no real archive/sidecar, host/workstation/SSH/filesystem/runner preflight, B8 dispatch/runner, real-data staging, uploads/deletion/cleanup, Canonical T0, MAY-10, REST tail, T1/T2 runtime, VPS/deployment, credentials, exchange or trading.

---

