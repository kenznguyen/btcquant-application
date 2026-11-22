# CURRENT STATUS OVERRIDE — 2026-11-22 — S1.1 design owner-accepted and frozen; implementation not authorized

- S1.1 design: `docs/design/T0_ARCHIVE_STAGING_S1_1_PROVENANCE_SCHEMA_RECONCILIATION_2026-11-22.md`, blob `209c9d10cc0e54dc90148efa9ef6884f74aa143d`.
- S1.1 self-review: `docs/reviews/T0_S1_1_SCHEMA_RECONCILIATION_SELF_REVIEW_2026-11-22.md`, blob `a46dd4ce9b64bad09a6ccec078476fa10dc67a65`; verdict **SELF-REVIEW PASS WITH LIMITATIONS**, not independent review.
- Owner acceptance recorded in addendum commit `f591b137272d445ea450f5d3748d15bc56b48fcb`.
- Latest authoritative `docs/PROJECT_SESSION_HANDOFF.md` T0 status update commit: `0c190a312747e205ca6068d54f509c5bf9756836`.
- B1 resolved at design level: failed/incomplete evidence nullable; attempts append-only; successful attempt separate relation; pair/member failure semantics; coverage manifest persistence; cross-table invariants.
- B2 resolved at policy level: SQLite STRICT minimum 3.37.0; exact Python/SQLite pin and per-connection FK checks required later. Exact versions deferred to separately approved implementation.
- Original S1 DDL is marked historical/superseded where inconsistent with S1.1.
- Detailed S1.1 design acceptance: **OWNER ACCEPTED / DESIGN FROZEN** on 2026-11-22.
- Acceptance remains documentation-only: no DDL, SQLite, importer, tests, workflow, archive/data operation, runtime or deployment.
- B3 archive format NOT VERIFIED; B5 actual coverage values NOT VERIFIED; B8 importer/build NOT AUTHORIZED; B9 separate review track unchanged.
- B4/B6/B7 decision package is committed for owner decision: `docs/design/T0_B4_B6_B7_RESOURCE_RETENTION_DESTINATION_DECISION_PACKAGE_2026-11-22.md` (blob `9119b5789825951e66a061e4b9d989256934adec`); self-review `docs/reviews/T0_B4_B6_B7_DECISION_PACKAGE_SELF_REVIEW_2026-11-22.md` (blob `6c6eb22d8643206aba517b3ea8625b70a64735c5`). Status: B4 proposed/pending; B6 proposed/pending; B7 Option A recommended but owner selection and later preflight pending. No operational activity authorized.
- No workflow run/job/artifact. All existing exclusions remain in force.

---

# CURRENT STATUS OVERRIDE — 2026-11-22 — S1.1 design reconciliation committed; owner acceptance pending

- S1.1 document: `docs/design/T0_ARCHIVE_STAGING_S1_1_PROVENANCE_SCHEMA_RECONCILIATION_2026-11-22.md`, final blob `505c23a00772667d0da3f5cc4a48f2d724b84c2a`.
- S1.1 initial commit `255e505149d1739a18549baab6d81ba458f124d7`; clarification commit `2971efa75a5f8f9f75277adba2ced72514797bab`.
- Original S1 DDL is explicitly marked as historical and superseded where it conflicts with S1.1; authority-notice commit `5ef5641da3d881c5c07a3704289c396834331a66`.
- B1 schema/failure-evidence/attempt-history/successful-attempt/coverage-manifest conflicts: **RESOLVED AT DESIGN LEVEL**.
- B2 SQLite STRICT minimum and runtime/FK verification contract: **RESOLVED AT POLICY/CONTRACT LEVEL**; minimum SQLite 3.37.0. Exact Python/SQLite pins deferred to separately approved implementation.
- S3 R3–R6, V1 interface, T0ENC1, identity prefixes, `T0_STAGING_SCHEMA_V2` and `user_version=2` unchanged.
- S1.1 is documentation-only. **No DDL, SQLite, importer, tests, workflow, archive access, data operation or runtime change.**
- S1.1 detailed design: **OWNER ACCEPTANCE PENDING**. Scope approval is not treated as acceptance of every detailed design choice.
- B3 archive format coverage NOT VERIFIED; B4 resource budgets OPEN; B5 actual coverage manifest NOT VERIFIED; B6 retention/artifact policy OPEN; B7 destination/preflight OPEN; B8 importer/build NOT AUTHORIZED. Existing independent review track unchanged.
- Latest handoff addendum update commit: `e8f91a3dadb01d680dadd29b428643594487987f`.
- Next: owner review of S1.1 document only. No later phase is authorized.

---

# CURRENT STATUS OVERRIDE — 2026-11-22 — Post-S3 T0 blocker audit

- Latest exact-SHA S3 GREEN: source `d1651196af3059e00b22f65461dbd897e5c599df`, run [44976543815](https://github.com/kenznguyen/btcquant-application/actions/runs/44976543815), job `137067027769`. S3 30/30, V1 24/24, full `market_data` 387/387 PASS. Validator/test/contract/workflow blobs are recorded in the S3 evidence and session handoff.
- S3 GREEN closes only the pure in-memory provenance validator and synthetic verification. It does NOT authorize DDL, SQLite, importer, archive acquisition, staging, runtime, VPS or deployment.
- Current blocker audit: `docs/reviews/T0_POST_S3_BLOCKER_AUDIT_2026-11-22.md`, commit `a66234d0ee10fbcd22f67f978a3ced73570cca22`.
- **S1 schema freeze BLOCKED**: original DDL is not reconciled with the failed/incomplete evidence amendment; acquisition-attempt table and successful-attempt relationship are unresolved; S3 R4–R6 and run coverage-manifest persistence need alignment.
- **STRICT SQLite runtime BLOCKED FOR DDL**: minimum version policy and exact Python/SQLite runtime verification contract are not frozen. No SQLite runtime test/database creation authorized.
- **Archive format coverage NOT VERIFIED**: exact header evidence covers only M15 monthly 2022-08. Do not infer the other 201 ZIPs.
- **Acquisition BLOCKED**: decompression/ratio/disk/concurrency/retry/timeout limits, source/evidence retention and exact owner-controlled destination require separate decisions. Former VPS is deleted; prior staging path is not an active approved destination.
- **Coverage acceptance NOT VERIFIED**: S3 R6 manifest schema is frozen, but no freshly measured archive-derived coverage manifest exists. Historical totals are not fresh proof.
- **Importer / SQLite staging NOT IMPLEMENTED / NOT AUTHORIZED**. Require separate approvals for synthetic importer, database creation, acquisition, build and read-only acceptance.
- T0 Application Foundation independent reviews PR #3/#4 remain separate review gates; S3 GREEN does not close them.
- REST tail remains **NOT VERIFIED — CLOSED BY OWNER DECISION / NO FURTHER RETRIEVAL**; MAY-10 excluded. Former Canonical SQLite remains LOST. Any future reconstruction may only be `RECONSTRUCTED — PARTIAL COVERAGE`.
- Recommended next task: **S1.1 documentation-only schema reconciliation**. No archive/DB/runtime operation is implied.

---

# CURRENT STATUS OVERRIDE — 2026-11-21 — T0 transfer continuation / reconstruction gates

- Target ownership: `kenznguyen/btcquant-application`. Former Canonical SQLite is **LOST** and not needed; no recovery/migration/deletion is in scope. New reconstructed dataset is **NOT CREATED**.
- PR #3/#4 automated reviews from Codex and Graphify are **ACCEPTED BY OWNER**. Review PRs remain OPEN / UNMERGED; this does not imply implementation merge or runtime approval.
- Controlling reconstruction records: `docs/decisions/T0_CANONICAL_DATA_PRESERVE_AND_RECONSTRUCT_DECISION_2026-11-20.md` and `docs/plans/T0_CANONICAL_SQLITE_RECONSTRUCTION_EXECUTION_PLAN_2026-11-20.md`. Older materialization approval/staging plan is superseded/hold for execution. Old proposed `/srv/btcquant/staging/t0-reconstructed-btcusdt-20261120-run-001` is not an active approved destination; former VPS was deleted.
- Archive evidence accepted only as **RECONSTRUCTED — PARTIAL COVERAGE**: 202 ZIP + 202 sidecars; M15 241,440 rows through 2026-11-18 23:45 UTC; H1 60,360 rows through 2026-11-18 23:00 UTC. REST tail is **NOT VERIFIED — CLOSED BY OWNER DECISION / NO FURTHER RETRIEVAL**. Draft manifest contains stale REST-success claims and is not usable for DB build.
- Current blockers: new exact owner-controlled host/path, source access, fresh per-object archive evidence/sidecar hashes, source-column mapping, `available_at_ms` policy, importer SHA/dependency lock, gap/conflict policy, validation plan and separate execution approval.
- Status: design **APPROVED**; archive materialization **NOT AUTHORIZED**; destination preflight **NOT RUN**; SQLite **NOT AUTHORIZED / NOT CREATED**; promotion, cutover, runtime and T1/T2 **NOT AUTHORIZED**.
- No data, host, database, runtime, source code or tests changed. Governance documentation only.
- Next: resolve owner gates and submit a newly reconciled execution request; no preflight/network/data/DB operation until explicit approval.

---

# CURRENT STATUS OVERRIDE — 2026-11-21 — Two T0 independent-review PRs opened

- Review target snapshot for both PRs: `b79c7e5d0bc7cf5e6beee0d4e05505a1b1aa6556` (main at PR creation).
- PR #3 — [INDEPENDENT REVIEW ONLY — T0 Candle Contract, FastAPI & Application Adapter](https://github.com/kenznguyen/btcquant-application/pull/3). Head branch `review/t0-candle-fastapi-adapter-20261121`, head SHA `5aa49ee34031e11db2563776ee204b8dc0d4d38e`; request document `docs/reviews/requests/T0_CANDLE_FASTAPI_APPLICATION_ADAPTER_INDEPENDENT_REVIEW_2026-11-21.md`. Documentation-only; 1 file, 85 additions.
- PR #4 — [INDEPENDENT REVIEW ONLY — T0 SQLite Storage, Write Gateway, Lease/Fencing & Recovery](https://github.com/kenznguyen/btcquant-application/pull/4). Head branch `review/t0-sqlite-storage-fencing-recovery-20261121`, head SHA `52784c94c5cec58601ecb5767262b385653878bf`; request document `docs/reviews/requests/T0_SQLITE_STORAGE_FENCING_RECOVERY_INDEPENDENT_REVIEW_2026-11-21.md`. Documentation-only; 1 file, 97 additions.
- Both PRs are OPEN, not merged. No reviewer usernames were supplied; requested_reviewers is empty. They require genuine independent reviewers to submit explicit GitHub reviews.
- PR #3 scope: Candle Contract 1.1.0, FastAPI read-only/auth/limits/error/lifecycle/dependency CI, Application Common API parity, exact source/test blob verification and adversarial tests.
- PR #4 scope: SQLite backend/storage/schema/migrations/explicit initializer, Write Gateway, lease/fencing atomicity, feeder/scheduler/recovery, gap/cursor/retry/idempotency and fail-closed lifecycle.
- Both PRs pin source snapshot `b79c7e5d0bc7cf5e6beee0d4e05505a1b1aa6556`; their own branch changes are review request documents only. Do not mistake PR diff for implementation source changes.
- Restrictions: no merge as implementation, no source fixes in review PRs, no Canonical SQLite/data access or mutation, no Feeder/VPS/runtime/deployment, no REST 451 retry/bypass, no PostgreSQL activation, no T1/T2 runtime connection or trading.
- Status: review requests **OPEN / AWAITING INDEPENDENT REVIEW**; T0 overall independent validation remains **NOT VERIFIED** until reviewer findings and explicit verdicts are submitted.

---

# CURRENT STATUS OVERRIDE — 2026-11-21 — T0 Application Foundation current-source audit recorded

- Current review snapshot: `d6e7516e0cdbcde58d4b78327c18c22aa3a4c2a0`; review package: `docs/reviews/T0_APPLICATION_FOUNDATION_CURRENT_REVIEW_PACKAGE_2026-11-21.md`, commit `7cf9e3a4e51bd5b395d8ee968852777d6defc18c`.
- T0 application code/CI status: implementation **PASS — CODE PRESENT**; FastAPI/Candle API **69/69 PASS** on exact T0 source SHA `4d41294a7b82566666e50a79b87f62b668672077`; runtime-lock smoke and isolated Uvicorn/Nginx process/socket integration **PASS — CI ONLY**.
- Latest FastAPI run: [44861746989](https://github.com/kenznguyen/btcquant-application/actions/runs/44861746989); jobs `136716449564` (69/69), `136716449529` (runtime-lock smoke), `136716449322` (Uvicorn/Nginx). Artifacts: contract `14689618455` / `fe44ab13bf1dca83bcb072b88467f99d1e6f2249f6884f24f2a75b0d1f990068`; runtime `14690086537` / `0c1c9fdd2424a4cf4488e9e6bf27a7a7b66f47a3735c3a91beb7a71f6e210312`; Uvicorn/Nginx `14690171368` / `736daffdceaa1b52a74d940c6e29d1b3f4593b0b3028d0e3b36b0b2b87e4088b`.
- SQLite-only aggregate remains **174/174 PASS** on exact historical SHA `b4e16a153ef7b0306784efa117b3121fc83dacb5`, run [44740818608](https://github.com/kenznguyen/btcquant-application/actions/runs/44740818608), artifact `14629919931`, SHA-256 `87df9fe44627016066b893f9cf98d27bad5b31f80e64cb6993c7e9d8b61fc731`. Do not relabel as a current-HEAD run.
- Current T0 paths are unchanged from the tested FastAPI SHA to current HEAD; no T0 source/test/workflow path appears in the 107-commit compare. This is exact-path continuity evidence, not a CI run on current HEAD.
- Genuine independent second-person review of current T0 source: **NOT VERIFIED / PENDING**. Existing review package targets older SHA `fc2e48420c6bbd00b7c5cfbaa8b3d7b2fc996235`; Graphify index is stale at `1e7dcc5e70a0e6840a7c5617893d3d2b0fc952df`. The new review package is preparation only, not reviewer approval.
- REST-tail validator synthetic CI remains **10/10 PASS** at SHA `265268c0b527c4a323493c4643a67a46ee15a223`; real REST payload validation remains **NOT VERIFIED — CLOSED BY OWNER DECISION** after HTTP 451. No retry/bypass.
- VPS/runtime/production readiness **NOT VERIFIED / NOT AUTHORIZED**; PostgreSQL/TimescaleDB **PARKED / BLOCKED**. `/health` is owner-approved liveness-only, not readiness.
- No source code, tests, workflow, dependency, canonical DB/data, Feeder, VPS/runtime, T1/T2 connection, deployment or trading behavior changed or accessed in this audit.
- Next: obtain genuine independent second-person review of the current exact-source snapshot; remediate only bounded Required findings with exact-SHA regression and follow-up review. Preserve all data/runtime/production exclusions.

---

# CURRENT STATUS OVERRIDE — 2026-11-20 — Application-first T0 Application Foundation / REST-tail validator CI PASS

- Controlling delivery decision: `docs/decisions/DELIVERY_ORDER_APPLICATION_FIRST_2026-11-20.md` — Application-first; complete application/software foundations before Feeder restart or new T0 Canonical reconstruction.
- T0 Application Foundation increment: dedicated isolated workflow `.github/workflows/t0-rest-tail-validator.yml`, blob `8303b83fb5bf6d5b309556992ae4feae60f2b446`.
- Exact tested source SHA: `265268c0b527c4a323493c4643a67a46ee15a223` on `main`; validator blob `3437e7a9181611cfed77eab59afee27136472963`; test blob `293d9a605b6ec6498d551504fda04eecf298601f`.
- CI run [44723882441](https://github.com/kenznguyen/btcquant-application/actions/runs/44723882441), run 2, **SUCCESS**; job `136246309375`; syntax parse PASS and **10/10 synthetic regression tests PASS**.
- Artifact `t0-rest-tail-validator-evidence`: ID `14622617786`, SHA-256 `0ac0f81bacd65c8dd1b5748d1ba5da186dcc614963c050dfa8e0a403ec5ee713`, expires 2026-12-04.
- Initial run [44723808398](https://github.com/kenznguyen/btcquant-application/actions/runs/44723808398) failed because py_compile wrote bytecode into a read-only checkout. Harness corrected with in-memory AST parsing and `python -B`; no validator behavior or assertion was weakened.
- Real REST payload validation remains **NOT VERIFIED**; `m15.json` and `h1.json` are absent from the current repository tree. No retry/retrieval; HTTP 451 / owner-closed boundary preserved.
- No Canonical SQLite, archive, Dropbox, VPS, Feeder, credentials, T1/T2 runtime or trading was accessed or changed.
- Status: offline validator CI **PASS**; T0 Application Foundation **IN PROGRESS**; real payload validation **NOT VERIFIED**; Canonical reconstruction/Feeder/runtime/integration/trading remain **BLOCKED / NOT AUTHORIZED**.
- Evidence report: `docs/evidence/T0_REST_TAIL_VALIDATOR_CI_2026-11-20.md`.
- Next: continue bounded application-side contracts and deterministic regression harnesses only. No data/runtime expansion without separate approval.

---

# CURRENT STATUS OVERRIDE — 2026-11-20 — T1 repository ownership decision approved

- Decision: `docs/decisions/T1_REPOSITORY_OWNERSHIP_AND_CONSUMER_BOUNDARY_2026-11-20.md`, commit `10313ef41b975343e5e09e24793be48258d1c46e`.
- T1 implementation stays in `kenznguyen/binance-futures-collector`; do not copy/fork its full implementation into `kenznguyen/btcquant-application`.
- Application-side T1 artifacts are limited to separately approved consumer contracts/interfaces, DTOs, validation, adapters and deterministic fixtures/mocks.
- T1 HTTP Provider remains **PAUSED**; T1 → T2 runtime connection **NOT APPROVED**; T1 storage/data migration **NOT AUTHORIZED**.
- T0 Canonical SQLite and its independent data ownership remain unchanged.
- Provenance snapshots: application pre-decision main HEAD `0844e16b08d52fa7cf6ed001d7c260ee6bde1ff8`; T1 main latest observed `c91a8c22d3b6236c98ab9a4d4d69b25d47f7f738`.
- Documentation-only; no tests/workflows run and no Actions run/job/artifact. No runtime/data/database/trading changes.
- Next: separately define a versioned T1 consumer contract only if required by T2. Runtime transport or provider activation requires a new owner approval.

---

# CURRENT STATUS OVERRIDE — 2026-11-20 — T0 staging plan reconciliation PASS

- Plan: `docs/plans/T0_RECONSTRUCTED_PARTIAL_SQLITE_STAGING_PLAN_2026-11-20.md`, blob `b35e25d5d52a09dc73cfb1ced91b408a4979b045`.
- Independent re-review: `docs/reviews/T0_ARCHIVE_STAGING_PLAN_RECONCILIATION_INDEPENDENT_REREVIEW_2026-11-20.md`, blob `44c7cf4f6006d0a0ad529d37044181cefa20e9d0`.
- Status: **DOCUMENT RECONCILIATION PASS — DESTINATION PREFLIGHT NOT RUN / BLOCKING**.
- Existing approval remains exactly 404 allowlisted objects, exact path `/srv/btcquant/staging/t0-reconstructed-btcusdt-20261120-run-001`, 100 MiB including retries. No alternate path or scope expansion.
- SQLite remains NOT AUTHORIZED; requires separate owner approval.
- No archive network access/materialization, SQLite, Dropbox, REST tail, VPS/runtime, T1/T2, deployment or cleanup. No tests/workflows/Actions run.
- Next: exact-path read-only destination preflight; STOP on any failed or unverifiable condition.

---

# CURRENT STATUS OVERRIDE — 2026-11-20 — Owner approved archive materialization; exact local target; preflight pending

- Owner decision: `docs/decisions/T0_RECONSTRUCTED_ARCHIVE_MATERIALIZATION_APPROVAL_2026-11-20.md`, commit `c8793aee2ac3cab5594372e718421c33aa0d46ff`.
- Approved exact local staging target: `/srv/btcquant/staging/t0-reconstructed-btcusdt-20261120-run-001`. This path is not yet verified or created. Before any network request, verify owner-controlled local filesystem, outside Dropbox and operational T0/database paths, empty/new, no symlink, create-only, sufficient free space; record filesystem/mount identity, owner and permissions. If preflight fails, STOP; no alternate path without new owner approval.
- Historical 11,277-byte difference accepted as aggregate reporting/reconciliation discrepancy of unknown root cause, not evidence of missing candle data. Preserve old figures. New run must verify each of 404 objects individually, measure actual size/SHA-256 for each sidecar and compute a fresh aggregate; do not require matching historical 14,929,033-byte summary. Any per-object size/hash/checksum mismatch, missing/extra object or validation failure quarantines the run.
- Exact approved scope: 202 ZIP + 202 paired checksum sidecars, exact committed allowlist, official S3-compatible source, max 100 MiB transferred including retries, bounded concurrency/timeouts/retries, raw create-only files, preserve until owner review and separate cleanup decision.
- Approval proposal updated: `docs/plans/T0_RECONSTRUCTED_ARCHIVE_MATERIALIZATION_APPROVAL_REQUEST_2026-11-20.md`, commit `4946ad2d88b297f20e7d412f5d537f217ffa2001`.
- Inventory updated: `docs/manifests/T0_BINANCE_UM_BTCUSDT_ARCHIVE_OBJECT_PROVENANCE_INVENTORY_2026-11-20.json`, commit `6225e55a7efd68981a95211efd8bc2c7f0dd1403`.
- Staging plan updated: `docs/plans/T0_RECONSTRUCTED_PARTIAL_SQLITE_STAGING_PLAN_2026-11-20.md`, commit `5f2fc22c7bfb6a4274e4f1e0ca9d05cda00777a0`.
- Current status: APPROVED — PREFLIGHT PENDING / NOT RUN. No archive request/materialization has started. SQLite creation/open/write/import remains NOT AUTHORIZED and requires separate later owner approval.
- Explicit exclusions remain: REST tail (NOT VERIFIED, closed, no retry/bypass); SQLite; Dropbox; VPS/runtime; feeder/writer/lease; T1/T2; restore; deployment/cutover; auto-delete/cleanup; OFFICIAL/VERIFIED promotion.
- No tests/workflows run; no workflow run/job/artifact. No source archive accessed; no raw data staged; no SQLite/Dropbox/VPS/runtime action.
- Next: perform only the approved destination preflight. If it passes, execute exact 404-object materialization; if not, stop and request owner direction.

---

# CURRENT STATUS OVERRIDE — 2026-11-20 — Owner accepts RECONSTRUCTED partial archive coverage; SQLite remains gated

- Owner decision: `docs/decisions/T0_RECONSTRUCTED_PARTIAL_COVERAGE_ACCEPTANCE_2026-11-20.md`, commit `1a1910648bba711710b6f159d539f1f8a4ab209c`.
- Accepted label: **RECONSTRUCTED — PARTIAL COVERAGE** only. This does not assert earliest-ever Binance history, current tail completeness, recovery of the deleted original DB, or OFFICIAL / VERIFIED status.
- Validated bounds: M15 2019-12-31 00:00–2026-11-18 23:45 UTC, 241,440 rows; H1 2019-12-31 00:00–2026-11-18 23:00 UTC, 60,360 rows. Continuity PASS only within these observed bounds.
- Leading history before 2019-12-31 and trailing history from 2026-11-19 00:00 UTC remain NOT VERIFIED. REST tail remains CLOSED BY OWNER DECISION / NO FURTHER RETRIEVAL; do not retry or bypass.
- Manifest draft: `docs/manifests/T0_RECONSTRUCTED_BTCUSDT_M15_H1_MANIFEST_DRAFT.json`, commit `635f5927cc6415d2bd09cf08ce923e9199d2cca6`. It is explicitly DRAFT_NOT_FOR_DATABASE_BUILD; machine-readable inventory of all 404 ZIP/sidecar objects remains pending.
- Staging plan: `docs/plans/T0_RECONSTRUCTED_PARTIAL_SQLITE_STAGING_PLAN_2026-11-20.md`, commit `ef9bd47ab0e61c0aed1486cc6d29bf88bf776439`.
- Static schema inspection only: Candle Contract 1.1.0, SQLite user_version 1, tables candles + feeder_leases; current candles schema stores OHLCV and available_at_ms. Archive-only CSV fields must remain auditable in preserved raw payloads; no schema extension authorized.
- This approval authorizes documentation/static preparation only. Raw payload materialization/re-download, SQLite initialization/writes, database build/validation, Dropbox, restore, VPS/runtime, feeder/writer, deployment and cutover remain separately gated and NOT AUTHORIZED / NOT RUN.
- No source code, schema, dependencies, tests or workflows changed or run. No market-data endpoint/archive accessed. No SQLite file created/opened/modified. No Actions run/job/artifact.
- Next: complete machine-readable per-object provenance inventory and independent static review. Then request separate approval for bounded raw archive materialization; request a separate explicit approval again before SQLite creation/writes.
 
---

# CURRENT STATUS OVERRIDE — 2026-11-20 — Owner decision: REST tail remains NOT VERIFIED

- Owner explicitly decided to leave the REST tail from 2026-11-19 00:00 UTC as **NOT VERIFIED** following the bounded Binance USD-M REST attempt blocked by HTTP 451.
- Do not retry the endpoint, use alternate endpoints/domains, proxies, geo-routing or another execution environment. No further REST tail access is authorized.
- Preserve archive payload validation as PASS through M15 2026-11-18 23:45 UTC and H1 2026-11-18 23:00 UTC. Do not infer coverage after those archive boundaries or completeness through a later retrieval cutoff.
- Evidence: `docs/evidence/T0_BINANCE_UM_BTCUSDT_REST_TAIL_VALIDATION_2026-11-20.md`, commit `782d4a46f6a75dfc2aa4977e6a33b14e86ede268`.
- Status: REST tail **NOT VERIFIED — CLOSED BY OWNER DECISION / NO FURTHER RETRIEVAL**. Archive payload validation remains **PASS** for its documented scope.
- No source/test/workflow/dependency/schema/canonical data changes; no GitHub Actions run/job/artifact. SQLite, Dropbox, VPS/runtime, feeder/writer, deployment, restore and cutover remain NOT RUN / separately gated.
- Next: preserve this boundary. Any future reconsideration requires a new explicit owner decision; do not reopen automatically.

---

# CURRENT STATUS OVERRIDE — 2026-11-20 — REST tail validation BLOCKED by HTTP 451

- Owner approved a bounded, read-only public Binance USD-M REST tail check for BTCUSDT M15/H1 from 2026-11-19 00:00 UTC, maximum 500 rows/timeframe and 5 MiB isolated staging; only fully closed candles were eligible.
- Evidence report: `docs/evidence/T0_BINANCE_UM_BTCUSDT_REST_TAIL_VALIDATION_2026-11-20.md`, commit `782d4a46f6a75dfc2aa4977e6a33b14e86ede268`.
- The approved `GET https://fapi.binance.com/fapi/v1/klines` request for M15 returned HTTP 451 from the isolated execution environment before any kline payload was received. H1 was not attempted after the M15 block. No payload or raw staging file was created.
- Status: endpoint reachability **BLOCKED — HTTP 451**; M15 payload **NOT RETRIEVED**; H1 **NOT ATTEMPTED**; tail candle validation **NOT VERIFIED**. Do not bypass with alternate domains, proxies or geo-routing.
- Previously validated archive coverage remains PASS through M15 2026-11-18 23:45 UTC and H1 2026-11-18 23:00 UTC. Tail from 2026-11-19 00:00 UTC remains NOT VERIFIED.
- No source/test/workflow/dependency/schema/canonical data changes; no GitHub Actions run/job/artifact. No SQLite, Dropbox, VPS/runtime, feeder/writer, deployment, restore or cutover.
- Next gate: owner decides whether to leave the tail unresolved or separately authorize a compliant attempt from an owner-approved, legally available execution environment. SQLite/Dropbox/runtime/feeder/writer/cutover remain separately gated.

---

# CURRENT STATUS OVERRIDE — 2026-11-20 — Owner approved T0 archive source partition

- Decision: `docs/decisions/T0_RECONSTRUCTED_CANONICAL_SOURCE_PARTITION_APPROVAL_2026-11-20.md`, commit `ce42ae530d5b11a46e46c4e79e573bd4b5d0f3d2`.
- Owner approved monthly USD-M archive as default bulk source for full months 2020-01–2026-10; daily archive for 2019-12-31 and 2026-11-01–2026-11-18; daily as targeted fallback/diagnostic for payload-level gaps/conflicts.
- Any retrieved daily/monthly overlap must be compared using complete normalized candle payloads. Exact duplicates may be deduplicated with both provenances retained; conflicts must be quarantined.
- REST `/fapi/v1/klines` tail remains a separate future approval gate; this decision does not authorize REST calls.
- Approval is source-partition/documentation only. ZIP/checksum body download, raw staging, market-data retrieval, SQLite, Dropbox, restore, VPS/runtime, writer/feeder and cutover remain NOT AUTHORIZED.
- Archive listing remains PASS for object-key coverage only. ZIP/checksum integrity, candle-level completeness, row counts, actual first/last candle timestamps, intra-file gaps and closed state remain NOT VERIFIED.
- Tests/workflows NOT RUN; no run/job/artifact. Documentation-only update.
- Next gate: request separate bounded approval for exact ZIP/checksum payload retrieval and validation, including staging destination and resource/retention budgets.

---

# CURRENT STATUS OVERRIDE — 2026-11-20 — Binance USD-M archive metadata inspection PASS

- Evidence: `docs/evidence/T0_BINANCE_UM_BTCUSDT_ARCHIVE_METADATA_INSPECTION_2026-11-20.md`, commit `0b37e158e30824e7e6cfd80ff9d8a457ee715ec9`.
- Owner-approved scope executed: read-only S3-compatible ListObjectsV2 metadata inspection for Binance Public Data `data/futures/um` BTCUSDT M15/H1 daily and monthly prefixes only.
- Monthly per timeframe: 82 ZIP + 82 `.CHECKSUM` keys; continuous 2020-01 through 2026-10; listing complete.
- Daily per timeframe: 2,515 ZIP + 2,515 `.CHECKSUM` keys across six pages; continuous filename dates 2019-12-31 through 2026-11-18; no duplicate or missing calendar filename dates.
- Latest daily archive object date 2026-11-18, LastModified 2026-11-19T08:16:17Z. Latest monthly object October 2026, LastModified 2026-11-11T10:50:21Z.
- Daily and monthly object coverage overlaps for 2020-01 through 2026-10. Proposed partition (NOT OWNER-APPROVED): monthly bulk for 2020-01–2026-10, daily for 2019-12-31 and 2026-11-01–18, with daily fallback for payload-level gaps and REST tail considered separately.
- Important: listing PASS is object-key coverage only. ZIP/checksum bodies not fetched; SHA-256 not validated; first/last candle timestamps, candle counts, intra-file gaps, closed state and earliest REST history remain NOT VERIFIED.
- No REST API, ZIP/checksum body download, raw staging, SQLite, Dropbox, VPS/runtime, writer/feeder or cutover. Tests/workflows NOT RUN; no run/job/artifact.
- Next: owner decision on proposed source partition, then separate bounded approval for archive payload retrieval/validation and any REST probe. No reconstruction/database creation authorized.

---

# CURRENT STATUS OVERRIDE — 2026-11-20 — T0 historical source selection review recorded

- Review: `docs/reviews/T0_RECONSTRUCTED_CANONICAL_SOURCE_SELECTION_REVIEW_2026-11-20.md`, commit `70f6c26b9f205c7d0198c5e58f46308642f5f48f`.
- Documentation-based comparison: Binance USD-M REST `/fapi/v1/klines` vs Binance Public Data USD-M (`um`) daily/monthly kline archives.
- Recommendation (NOT OWNER-APPROVED): archive as bulk base; REST as latest-closed-candle tail/completion; preserve per-chunk provenance and quarantine conflicting overlaps.
- Official docs identify REST max limit 1,500 and request-weight tiers; archive docs identify USD-M/COIN-M separation, klines sourced from `/fapi/v1/klines`, companion SHA-256 checksums, daily next-day and monthly first-Monday publication, and possible later archive corrections.
- Earliest BTCUSDT M15/H1 archive object, exact listing completeness, archive overlap behavior and latest available object remain NOT VERIFIED; no archive listing/API endpoint was queried.
- Status: documentation review **PASS / COMPLETE**; source selection **PROPOSED / OWNER APPROVAL PENDING**.
- No API call, metadata probe, ZIP/checksum download, market-data download, raw staging, SQLite, Dropbox, VPS/runtime, writer/feeder or cutover. Tests/workflows **NOT RUN**; no run/job/artifact.
- Next approval gate: read-only archive index/listing metadata inspection only; no ZIP candle payloads and no REST klines probe. Reconstruction requires a separate approval.

---

# CURRENT STATUS OVERRIDE — 2026-11-19 — Reconstructed Canonical workflow design recorded

- Workflow/validation contract: docs/decisions/T0_RECONSTRUCTED_CANONICAL_SQLITE_RECONSTRUCTION_WORKFLOW_2026-11-19.md.
- Status: DESIGN DRAFT / NOT IMPLEMENTED / NOT EXECUTED. Covers source-selection gate, immutable raw chunks, resumable pagination/checkpoints, normalization, M15/H1 expected-grid gap detection, semantic validation, staged SQLite gates, mandatory provenance manifest, fail-closed states, Dropbox snapshot and isolated restore gates.
- Owner-approved target remains all Binance USD-M BTCUSDT M15/H1 history available at retrieval time, each timeframe from its independently evidenced earliest candle through the latest fully closed candle at the recorded UTC cutoff. Lineage RECONSTRUCTED.
- All gaps must be enumerated; no synthetic candles, interpolation, forward-fill or silent omission. Gap disposition remains pending evidence and explicit owner decision.
- Open before implementation: source family selection; request/chunk/resource budgets; raw staging destination; exact Candle Contract/SQLite schema compatibility; gap disposition evidence; retention policy.
- Authorization remains Phase 1 documentation/static only. No Binance access/download, raw data staging, SQLite initialization/write, Dropbox upload, snapshot, restore, VPS/runtime, writer/feeder or cutover.
- Tests/workflows: NOT RUN; no run/job/artifact for this documentation-only change.

---

# CURRENT STATUS OVERRIDE — 2026-11-19 — Owner approved reconstructed Canonical coverage target

- Decision: [T0 Reconstructed Canonical Coverage Decision](decisions/T0_RECONSTRUCTED_CANONICAL_COVERAGE_DECISION_2026-11-19.md).
- Scope: Binance USD-M BTCUSDT M15 and H1; for each timeframe independently, start at the earliest candle actually available from Binance and end at the latest fully closed candle available at the recorded UTC retrieval cutoff.
- Retrieve all history available through the selected Binance USD-M historical-data interface at retrieval time; document source/endpoint limits, exact first/last candle times, retrieval cutoff, counts and partial-boundary treatment.
- Every missing expected interval must be reported with UTC boundaries/duration/count and evidence. No synthetic fill, interpolation, forward-fill or silent omission. Gap acceptability remains subject to validation and explicit owner disposition.
- Lineage must be RECONSTRUCTED; this is not recovery of the historical original database.
- Authorization remains Phase 1 DESIGN / DOCUMENTATION ONLY. No Binance access/download, reconstruction, SQLite initialization/write, Dropbox upload, snapshot, restore, VPS/runtime, feeder/writer or cutover is authorized.
- Tests/workflows: NOT RUN; no run/job/artifact for this documentation-only update.

---

# CURRENT STATUS OVERRIDE — 2026-11-19 — Owner approved independent CI and VPS runtime validation tracks

- Decision: `docs/decisions/T0_DUAL_TRACK_CI_RUNTIME_VALIDATION_DECISION_2026-11-19.md`.
- Owner approval: **APPROVED**. The prior GitHub-only validation decision is superseded.
- Track A — GitHub Actions isolated Uvicorn + Nginx integration: preserve **PASS — CI ONLY**, exact tested source/workflow SHA `65661cd4a2492f9552fe05186581c66d14fbe293`, FastAPI workflow run `44550458804`, job `135652465869`, integration artifact `14543536038`, SHA-256 `af07b99fa0a53ff315bad148c508533ea0e808d6365fc2c81faafa11ebe8c872`.
- Track B — VPS/Scaleway runtime integration: **NOT VERIFIED / NOT RUN**. No VPS probe or runtime action is authorized by this decision. Any future runtime validation requires a separate explicit owner approval defining the exact scope.
- CI and runtime statuses, evidence and acceptance criteria remain independent. Never merge into one PASS or infer VPS readiness from CI.
- Documentation-only governance update. No code, tests, workflow, dependencies, runtime configuration or data changed. No CI or runtime validation was run as part of recording this decision.
- Preserved restrictions: no canonical T0 SQLite/feeder/writer/lease/recovery access or changes; no T1/T2/PostgreSQL/retention/trading changes; no real orders; no systemd/autostart, persistent service, public ingress, DNS/TLS or production deployment authorization. Paper-first and `ai_execution_enabled=false` remain unchanged.

---

# CURRENT STATUS OVERRIDE — 2026-11-19 — Uvicorn + Nginx isolated GitHub Actions integration PASS

- Evidence report: `docs/evidence/T0_UVICORN_NGINX_ISOLATED_INTEGRATION_2026-11-19.md`, commit `15563d2a4d47b0ac860f82b37b3050c6ebba238a`.
- Repository: `kenznguyen/btcquant-application`, branch `main`.
- Exact tested source/workflow SHA: `65661cd4a2492f9552fe05186581c66d14fbe293`.
- Added `market_data/uvicorn_nginx_smoke.py` (blob `38e5fcdf10990af265f68f3597cdfef386f5a0aa`) and a dedicated `uvicorn-nginx-socket-integration` job in `.github/workflows/t0-fastapi-migration.yml` (blob `82b65cad3ea90d437d73998f33384f66b543431b`).
- FastAPI workflow [44550458804](https://github.com/kenznguyen/btcquant-application/actions/runs/44550458804): exact SHA above, **SUCCESS**. Uvicorn/Nginx job `135652465869` SUCCESS; existing FastAPI contract job `135652465887` SUCCESS; runtime-lock smoke job `135652465650` SUCCESS.
- Integration artifact `14543536038`, SHA-256 `af07b99fa0a53ff315bad148c508533ea0e808d6365fc2c81faafa11ebe8c872`.
- FastAPI contract artifact `14541653518`, SHA-256 `cdcc7a4c039c1b3fe4115c3d770c42754312b660efd384bc34319e59a447cdaa`; runtime smoke artifact `14543502169`, SHA-256 `e6779dd50b10d003e0e850c35cab245e003f9e5babafd3f8ee5be45ca7a1b6e7`.
- SQLite aggregate workflow [44550458851](https://github.com/kenznguyen/btcquant-application/actions/runs/44550458851): exact same SHA, **SUCCESS**; job `135652463602`; artifact `14543096166`, SHA-256 `852ce0109b95bd7f9d021d9fc2ccda4db076409f45cf189d989d2dd7c4bdd78f`.
- Verified behavior: real Uvicorn and Nginx subprocesses; loopback TCP sockets; Nginx health proxy; Bearer header forwarding and Candle Contract 1.1.0 read; missing token 401; unknown path 404; POST 405/Allow GET; stopped upstream returns 502; dummy token absent from Nginx logs.
- Isolation: temporary SQLite fixture only, synthetic token, listeners bound to 127.0.0.1, external network disabled during test, non-root/read-only/bounded container. Canonical T0 SQLite not mounted.
- Status: Uvicorn process/socket + Nginx reverse proxy **PASS — isolated CI only**. VPS/Scaleway runtime and Nginx **NOT VERIFIED**. systemd/autostart, public ingress, TLS, deployment and production readiness **NOT AUTHORIZED / NOT VERIFIED**.
- No canonical T0 writer/lease/feeder/recovery/data, T1/T2, PostgreSQL, retention/deletion, exchange, strategy/risk/trading changes or access. Paper-first and `ai_execution_enabled=false` remain unchanged.
- Next step: only a separate explicit owner approval may authorize a VPS probe, persistent service, Nginx modification, public endpoint, TLS or runtime activation. Do not infer VPS readiness from CI.
 
---

### T0 WSGI/Gunicorn retirement — completed — 2026-11-19

- Owner approval and human-review waiver: [T0 WSGI/Gunicorn Retirement Approval](decisions/T0_WSGI_GUNICORN_RETIREMENT_APPROVAL_2026-11-19.md).
- Evidence: [T0 WSGI/Gunicorn Retirement Report](evidence/T0_WSGI_GUNICORN_RETIREMENT_2026-11-19.md).
- Implementation commit: `7bc8fab6b6c6f49ed70b7370a113958d7981cd20`; corrected test/workflow exact SHA: `c77ab92b621b2e79167d6b8eb910be015b428f62`.
- Removed WSGI module and Gunicorn dependency; migrated API/acceptance tests to ASGI; removed WSGI parity test after preserving C1 evidence; updated FastAPI, SQLite and dependency workflows.
- FastAPI + migrated tests + retirement guards: **50/50 PASS**, run `44546084887`.
- SQLite aggregate: **174/174 PASS**, run `44546084972`.
- F1 write-gateway regression: **14/14 PASS**, run `44546084937`.
- Runtime-lock ASGI import/in-process health: **PASS**, run `44546084887`.
- Dependency compatibility after Gunicorn removal: **PASS**, run `44545799691`, dependency-change SHA `7bc8fab6b6c6f49ed70b7370a113958d7981cd20`.
- WSGI/Gunicorn retirement: **PASS**. Human independent review prerequisite: **WAIVED BY OWNER**. Gemini review remains **BLOCKED / NOT VERIFIED**.
- Uvicorn socket/process, Nginx, VPS/systemd, endpoint runtime and deployment remain **NOT AUTHORIZED / NOT VERIFIED**. Production readiness **NOT CERTIFIED**.
- T0 canonical SQLite/writer/lease/feeder/recovery, T1/T2, PostgreSQL, retention/deletion and trading unchanged.

### Owner approval — T0 WSGI/Gunicorn retirement — 2026-11-19

- Decision: [T0 WSGI/Gunicorn Retirement Approval](decisions/T0_WSGI_GUNICORN_RETIREMENT_APPROVAL_2026-11-19.md).
- Owner explicitly waived the human independent second-person review prerequisite and approved the bounded retirement.
- Gemini external AI review is **BLOCKED / NOT VERIFIED** (repository and exact SHA inaccessible); no independent code-level approval is claimed. ChatGPT supplementary review remains non-independent.
- Baseline main HEAD at approval: `7fdf4e3eedaf0b568c7219ee8b140684ff066718`; tested implementation/workflow SHA: `a92cca39a3c23c3325191922c80e73b81384d9ce`.
- Authorized implementation scope: remove WSGI entrypoint and Gunicorn dependency/lock; migrate WSGI-dependent tests and acceptance fixtures to ASGI; retire the parity test after preserving its C1 evidence; update workflows and docs; rerun FastAPI, SQLite aggregate and dependency compatibility CI on one exact SHA.
- Preserve Candle Contract 1.1.0 and T0 canonical SQLite/writer/lease/feeder/recovery boundaries.
- Owner approval: **APPROVED**. Retirement implementation: **AUTHORIZED / NOT STARTED**. Post-change tests/CI: **NOT RUN**.
- Uvicorn socket, endpoint, Nginx, VPS/systemd, runtime/deployment: **NOT AUTHORIZED / NOT VERIFIED**. Production readiness: **NOT CERTIFIED**.
- PostgreSQL, T1/T2, data retention/deletion and trading remain excluded.

### ChatGPT supplementary adversarial review — completed, not independent sign-off — 2026-11-19

- Report: `docs/reviews/T0_FASTAPI_CHATGPT_SUPPLEMENTARY_REVIEW_2026-11-19.md`, commit `cd1dd1c3e55f635d9cc542ab3f9bb665d614f922`.
- Exact implementation/workflow SHA inspected: `a92cca39a3c23c3325191922c80e73b81384d9ce`; review-start documentation snapshot: `379ac5021d347668dbfe42686e1bfb5fa0f14a6b`.
- Outcome: **NO CONFIRMED BLOCKING DEFECT IDENTIFIED IN THE INSPECTED STATIC SCOPE**. Same assistant participated in implementation and prior self-review; this report is supplementary only and is not an independent second-person review or certification.
- Scope: read-only static inspection of FastAPI/WSGI adapters, contract helpers, storage, tests, dependency locks and CI workflow. No tests/workflows run; no source/runtime/data/deployment changes.
- Limitations: C1 ten cases only; C2 api.py-only trigger not simulated; D1 in-process health only; no Uvicorn/Nginx/VPS/load/dynamic security qualification.
- Independent second-person review **PENDING**; reviewer not assigned. WSGI/Gunicorn retirement **NOT APPROVED**; runtime/deployment **NOT AUTHORIZED**; production readiness **NOT CERTIFIED**.

### Independent Review package refreshed — READY TO ASSIGN — 2026-11-19

- Refreshed `docs/reviews/T0_FASTAPI_INDEPENDENT_REVIEW_PACKAGE_2026-11-19.md`, commit `50d6fc71629ab03f9841959e0900dba50107425f`, blob `ec5f86bb4a5165cb8a66609cf0c6ff8eebc74f0c`.
- Exact tested implementation/workflow SHA: `a92cca39a3c23c3325191922c80e73b81384d9ce`; review snapshot before package refresh: `71be9bf1b477577643c557e69727bb92dec0c011`.
- Tested SHA to review snapshot: 3 ahead / 0 behind; only three documentation files changed. No executable source/test/workflow/dependency drift.
- Exact-SHA FastAPI workflow `44538454822`: contract job `135610069787` success, artifact `14535834201`, SHA-256 `350db8e7ec0dd7a876d814b8116306a37b3ca8c89ae7f826d9acf656db952983`; runtime job `135610069433` success, artifact `14536258780`, SHA-256 `b705d5c57283eff983d6d16e9301e2b9f882eaf8c038a2d058499864ebfefba7`.
- Exact-SHA SQLite aggregate workflow `44538454988`, job `135610069795` success, artifact `14536023784`, SHA-256 `a3ed69d72ceec7bf06e4a5c790d5b00f16f9ca46104e6a8a77e2e8a2d95d07a1`.
- C1 remains CLOSED / VERIFIED for ten enumerated cases; D1 CLOSED / PASS for runtime-lock installation, dependency check, ASGI import and in-process health; C2 CLOSED / VERIFIED for workflow path config and push-triggered success, with api.py-only trigger simulation not performed.
- Independent second-person reviewer **NOT YET ASSIGNED**. Package readiness is not independent review approval.
- WSGI/Gunicorn retirement **NOT APPROVED**; runtime/deployment **NOT AUTHORIZED**; production readiness **NOT CERTIFIED**.
- Documentation-only preparation. No tests/workflows run or dispatched; no source, runtime, data or trading changes.

### FastAPI C2 workflow trigger correction — CLOSED / VERIFIED — 2026-11-19

- User-approved workflow-only fix: added `market_data/api.py` to `.github/workflows/t0-fastapi-migration.yml` `on.push.paths`.
- Commit / exact tested SHA: `a92cca39a3c23c3325191922c80e73b81384d9ce`; workflow blob `7dabf111a2b89e22a80c3e02a5cf7f65a667095b`.
- Diff: one workflow file, +1/-0. No app source, test, dependency, runtime or data files changed.
- Static config verification: exactly one `market_data/api.py` path entry.
- Push-triggered FastAPI workflow [44538454822](https://github.com/kenznguyen/btcquant-application/actions/runs/44538454822): **success** on exact SHA; contract job `135610069787`, runtime-lock smoke job `135610069433`; artifacts `14535834201` (SHA-256 `350db8e7ec0dd7a876d814b8116306a37b3ca8c89ae7f826d9acf656db952983`) and `14536258780` (SHA-256 `b705d5c57283eff983d6d16e9301e2b9f882eaf8c038a2d058499864ebfefba7`).
- SQLite aggregate workflow [44538454988](https://github.com/kenznguyen/btcquant-application/actions/runs/44538454988): **success** on exact SHA; job `135610069795`; artifact `14536023784`, SHA-256 `a3ed69d72ceec7bf06e4a5c790d5b00f16f9ca46104e6a8a77e2e8a2d95d07a1`.
- Detailed evidence: `docs/evidence/T0_FASTAPI_ADVERSARIAL_SELF_REVIEW_FOLLOWUP_2026-11-19.md`, addendum commit `7ceea5a826b27242fa671948304aef225318892c`.
- C2: **CLOSED / VERIFIED** for path-filter configuration and successful push-triggered workflow execution. Qualification: the push changed the workflow file itself; an isolated api.py-only commit was not created because the approved scope excluded WSGI implementation changes.
- Independent second-person review remains **PENDING**; WSGI/Gunicorn retirement **NOT APPROVED**; runtime/deployment **NOT AUTHORIZED**; production readiness **NOT CERTIFIED**.

### FastAPI adversarial self-review C2 finding — 2026-11-19

- Review report: [T0 FastAPI Adversarial Self-Review Follow-up](evidence/T0_FASTAPI_ADVERSARIAL_SELF_REVIEW_FOLLOWUP_2026-11-19.md), commit `2815e6f4917f74679c19e88026c433e6258538fc`.
- Review HEAD: `7878e2d3b5cd9522ea6ed85b1c6083f8726a2816`; tested implementation/workflow SHA: `fe5f99d31aac832f85c1aab9ca007bd70386d9fe`.
- **C2 MEDIUM / OPEN:** `.github/workflows/t0-fastapi-migration.yml` omits `market_data/api.py` from `on.push.paths`, although the parity suite imports the WSGI adapter. WSGI-only edits will not trigger the FastAPI differential workflow.
- Required bounded correction: add `market_data/api.py` to the path filter and prove trigger behavior on an exact SHA. No source/workflow change or CI dispatch was made in this review.
- C1: **CLOSED / VERIFIED** for ten cases. D1: **CLOSED / PASS** for clean runtime-lock installation, dependency check, ASGI import and in-process health only.
- FastAPI/parity 26/26 and SQLite aggregate 196/196 PASS on exact SHA `fe5f99d31aac832f85c1aab9ca007bd70386d9fe`; artifacts/digests are in the evidence report.
- Same-assistant review only; independent second-person review remains **PENDING**. WSGI/Gunicorn retirement **NOT APPROVED**; runtime/deployment **NOT AUTHORIZED**; production readiness **NOT CERTIFIED**.

### FastAPI independent review package refreshed after D1 closure — 2026-11-19

- Updated `docs/reviews/T0_FASTAPI_INDEPENDENT_REVIEW_PACKAGE_2026-11-19.md`, commit `8a50de8b23566a57cc56f62755dda0f3b504b682`.
- Exact review snapshot before the package refresh: `4651bf1b26132ca028e6bb428ee0869963432bc0`.
- Exact tested implementation/workflow SHA: `fe5f99d31aac832f85c1aab9ca007bd70386d9fe`.
- Package now includes D1 runtime-only installation and ASGI health evidence, exact workflow/job IDs, artifact IDs/digests, smoke harness path and remaining runtime limitations.
- D1: **CLOSED / PASS**. C1: **CLOSED / VERIFIED** for ten cases. FastAPI/parity: **26/26 PASS**. SQLite aggregate: **196/196 PASS**.
- Independent second-person review remains **PENDING**; reviewer not yet assigned. WSGI/Gunicorn retirement **NOT APPROVED**. Runtime endpoint, Uvicorn process/socket, Nginx, VPS/systemd and deployment **NOT AUTHORIZED**. Production readiness **NOT CERTIFIED**.
- Next step: assign the updated package to a reviewer who did not author the implementation or self-reviews. No runtime or deployment work is authorized by this package refresh.

### D1 runtime-lock-only clean install and ASGI smoke — CLOSED / PASS — 2026-11-19

- Exact tested source SHA: `fe5f99d31aac832f85c1aab9ca007bd70386d9fe`.
- Added standard-library ASGI smoke harness `market_data/runtime_smoke.py`, commit `e50c5d83437d6db1b6eb15f8b75267575acde041`.
- Added isolated `runtime-lock-smoke` CI job, commit `fe5f99d31aac832f85c1aab9ca007bd70386d9fe`.
- Runtime-only job: workflow [44536493461](https://github.com/kenznguyen/btcquant-application/actions/runs/44536493461), job `135603190576`: **success**. Installs only `requirements-market-data-fastapi.lock` into a fresh CPython 3.12.16 venv, offline from the SHA-256-verified runtime wheelhouse; does not install the test lock. `pip check`, ASGI import and in-process GET `/health` all PASS.
- Runtime smoke artifact `14535727293`, SHA-256 `607771298cf289ab9af7f8bf7918d9738fff2d400be45e3e25bba388959042da`.
- Same-SHA FastAPI/parity job `135603189986`: **26/26 PASS**, run [44536493461](https://github.com/kenznguyen/btcquant-application/actions/runs/44536493461), artifact `14536536165`, SHA-256 `dbdbcc79ecd8495d91d39e14160187dbda6b9618f08d501f96cf4a6111dd02cd`.
- Same-SHA SQLite aggregate job `135603190883`: **196/196 PASS**, run [44536493268](https://github.com/kenznguyen/btcquant-application/actions/runs/44536493268), artifact `14536651799`, SHA-256 `fb0b74ec9276c7fc96c95e6c67b642079644d32d8329cb1efea9eb324462522a`.
- Detailed evidence: `docs/evidence/T0_FASTAPI_RUNTIME_LOCK_SMOKE_2026-11-19.md`, commit `b5d03b14175fc54360630113ac41ec186929704a`.
- D1: **CLOSED / PASS** for clean runtime-lock installation, dependency consistency, ASGI import and in-process health route. The smoke did not start a Uvicorn process or open a socket.
- Independent second-person review remains **PENDING**. WSGI/Gunicorn retirement **NOT APPROVED**. Uvicorn process/socket, Nginx, VPS/systemd, endpoint/runtime qualification and deployment **NOT VERIFIED / NOT AUTHORIZED**. Production readiness **NOT CERTIFIED**.
- Canonical SQLite, writer/lease/feeder/recovery, T1/T2, PostgreSQL, retention/deletion and trading were not changed or accessed.



### FastAPI follow-up self-review — 2026-11-19

- Re-inspected FastAPI adapter, shared contract helper, ASGI tests, runtime/test dependency inputs and locks, FastAPI workflow, SQLite aggregate workflow, storage facade and prior self-review evidence.
- API implementation: no new Critical source defect identified in the bounded static review. Additional non-blocking nit: stale test-module docstring.
- **Required CI finding R1:** FastAPI workflow push-path filter omits runtime/test dependencies (`market_data/storage.py`, `store.py`, `postgres.py`, plus test fixture dependencies `feeder.py`, `write_gateway.py`, `sync.py`). The SQLite aggregate triggers on some dependencies but its explicit test command does not run `market_data.test_fastapi_api`; FastAPI contract tests can therefore be skipped after dependency-only changes.
- Finding is recorded, **OPEN / NOT FIXED**. Workflow/source was not modified and no workflow was dispatched in this review.
- Updated report: [T0 FastAPI Internal Self-Review](evidence/T0_FASTAPI_INTERNAL_SELF_REVIEW_2026-11-19.md), commit `b88da69f6d73fb1e60e0d08638e652d9a0121434`.
- Verdict: internal self-review PASS WITH REQUIRED CI ACTION ITEM; independent reviewer remains **PENDING**. WSGI/Gunicorn removal remains **NOT APPROVED**; runtime/deployment remains **NOT AUTHORIZED**.


### FastAPI CI trigger correction and paired regression — 2026-11-19

- Corrected `.github/workflows/t0-fastapi-migration.yml` push paths to include `market_data/storage.py`, `store.py`, `postgres.py`, `feeder.py`, `write_gateway.py` and `sync.py`.
- Workflow correction commit: `3bdcaf093c381b2b767be3c903f9e86d5bf75bde`.
- Trigger proof: commit `b53e3e4f800d498317ac7ab4d0d01b44ef63a55c` changed only a CI sentinel comment in `market_data/storage.py`; GitHub started FastAPI and SQLite aggregate workflows on that exact push SHA.
- FastAPI run [44529575151](https://github.com/kenznguyen/btcquant-application/actions/runs/44529575151), job `135579262823`: **25/25 PASS**; artifact `14532693874`; SHA-256 `7bcf6fdd46e8c5e1c81f76bf078377437b81cdbb178a546ce0b18166a8ade5f5`.
- SQLite aggregate run [44529575307](https://github.com/kenznguyen/btcquant-application/actions/runs/44529575307), job `135579168097`: **196/196 PASS**; artifact `14531469720`; SHA-256 `93f30f492c9006a995c1f6248101080a3c2238be9d0530ab04421ce41f0580e8`.
- Both jobs checked out and tested exact SHA `b53e3e4f800d498317ac7ab4d0d01b44ef63a55c`. Artifact metadata and test logs independently confirm 25 and 196 tests with exit code 0.
- Updated internal review report in commit `608caa27910816e549fb109448004b1e080985b0`; R1 status **CLOSED / VERIFIED**.
- Scope: no FastAPI/SQLite runtime behavior changed; no canonical DB, feeder runtime, VPS, T1/T2, PostgreSQL, endpoint, deployment or trading access.
- Remaining gates: independent second-reviewer sign-off is still **PENDING**; WSGI/Gunicorn retirement is **NOT APPROVED**; runtime/deployment is **NOT AUTHORIZED**; production readiness **NOT CERTIFIED**.


### FastAPI follow-up internal self-review — 2026-11-19

- Re-reviewed current source/workflow at main HEAD `324fe0112c7c1d1a4c7e59aff29797c2f3cad3f4`; compared with tested source SHA `b53e3e4f800d498317ac7ab4d0d01b44ef63a55c`: four documentation-only commits, no source/workflow drift.
- Re-read FastAPI adapter, shared contract helper, ASGI tests, WSGI adapter, storage and SQLite/PostgreSQL adapters, fixture dependencies, locks/hash manifest and workflow filters.
- R1 dependency trigger: **CLOSED / VERIFIED**. FastAPI 25/25 and SQLite aggregate 196/196 remain PASS on exact SHA `b53e3e4f800d498317ac7ab4d0d01b44ef63a55c`; runs `44529575151` and `44529575307`.
- No new blocking API correctness/security issue found in bounded static review. No CVE research, dynamic pentest, load test, reverse-proxy or runtime validation performed.
- R2 stale docstring in `market_data/test_fastapi_api.py` (“not-yet-created ASGI app”): **OPEN / NON-BLOCKING NIT**; no source edit made.
- Current verdict: internal self-review **PASS WITH NON-BLOCKING NIT**; independent second review **PENDING**.
- WSGI/Gunicorn retirement **NOT APPROVED**; runtime/deployment **NOT AUTHORIZED**; production readiness **NOT CERTIFIED**.


### FastAPI R2 closure — 2026-11-19

- Corrected stale module docstring in `market_data/test_fastapi_api.py` to “Contract tests for the FastAPI ASGI adapter.”
- Documentation-only change; executable source/test logic, dependencies, workflows and runtime unchanged.
- R2: **CLOSED / VERIFIED**. No new CI run claimed; prior paired FastAPI 25/25 and SQLite aggregate 196/196 evidence remains tied to exact tested SHA `b53e3e4f800d498317ac7ab4d0d01b44ef63a55c`.
- Independent second review **PENDING**. WSGI/Gunicorn retirement **NOT APPROVED**. Runtime/deployment **NOT AUTHORIZED**.


### FastAPI independent review package — 2026-11-19

- Prepared reviewer package: [T0 FastAPI Independent Review Package](reviews/T0_FASTAPI_INDEPENDENT_REVIEW_PACKAGE_2026-11-19.md), commit `814721fb3974672fc936befc5267719a5b14bd28`.
- Exact review snapshot: `d69e2e44707ea9b177548c79d36bf72ac8a18f0b`; paired CI source SHA: `b53e3e4f800d498317ac7ab4d0d01b44ef63a55c`. Compare: 8 ahead / 0 behind; changed paths are documentation plus the already-closed test docstring correction; executable source/workflow/dependency locks unchanged.
- Package includes FastAPI 25/25 run `44529575151`, SQLite aggregate 196/196 run `44529575307`, artifact IDs/digests, source file inventory, review checklist, required verdict and scope restrictions.
- Independent reviewer: **NOT YET ASSIGNED / REVIEW PENDING**. This package is not itself a review approval.
- WSGI/Gunicorn retirement: **NOT APPROVED**. Runtime/deployment: **NOT AUTHORIZED**. Production readiness: **NOT CERTIFIED**.
- No source, tests, workflow, runtime, canonical data, T1/T2, PostgreSQL or trading changes; no tests or workflows run during package preparation.


### FastAPI adversarial follow-up self-review — 2026-11-19

- Review record: [T0 FastAPI Adversarial Self-Review](evidence/T0_FASTAPI_ADVERSARIAL_SELF_REVIEW_2026-11-19.md), commit `b2a075ace4c99227a3701f6183061f5dc3b59354`.
- Verdict: **PASS WITH VERIFICATION GAPS** in bounded static review; no blocking source defect identified.
- C1 **MEDIUM / NOT VERIFIED**: no automated WSGI-vs-FastAPI same-fixture differential test. Required before WSGI/Gunicorn retirement.
- D1 **LOW / NOT VERIFIED**: standalone runtime-lock install smoke test not separately evidenced; recommend before runtime qualification.
- This was performed by the same assistant and is explicitly **not an independent second-person review**. Independent review remains **PENDING**.
- WSGI/Gunicorn retirement **NOT APPROVED**; runtime/deployment **NOT AUTHORIZED**; production readiness **NOT CERTIFIED**. No source/tests/workflow/runtime/data changes and no tests/workflows run during this review.


### C1 WSGI–FastAPI differential contract test — 2026-11-19

- Added `market_data/test_fastapi_parity.py`, commit `78770e49c61075ff10da9ba94526b2d3aef0141d`, blob `2d951e924c99e5929dcc21c21ad144586658aabe`.
- The test constructs one temporary SQLite fixture, invokes the retained WSGI callable and FastAPI ASGI app against that same database and deterministic clock, then compares HTTP status, complete response headers and exact response-body bytes (plus parsed JSON).
- Cases: health, successful candle read, unauthorized, missing token configuration, malformed query, duplicate query parameter, unknown path, non-GET, missing SQLite store, and historical `asOfMs`.
- Updated `.github/workflows/t0-fastapi-migration.yml` to trigger on the new test file and run it alongside the 25 FastAPI contract tests. Workflow commit: `62054b53119308eca9d2256dcd5aae5561da235b`.
- Current source/test verification: **PENDING CI**. Do not claim C1 closed until the exact-SHA FastAPI workflow passes and its logs/artifact confirm the differential test ran. SQLite aggregate workflow is expected to trigger because its path filter includes the FastAPI workflow file; its result is also pending.
- No API implementation, WSGI/Gunicorn lifecycle, dependencies, canonical SQLite data, feeder, T1/T2, PostgreSQL, runtime, endpoint, VPS, deployment, retention/deletion or trading behavior changed.
- C1 remains **OPEN / NOT VERIFIED** pending CI. Independent second-person review remains **PENDING**. WSGI/Gunicorn retirement **NOT APPROVED**; runtime/deployment **NOT AUTHORIZED**; production readiness **NOT CERTIFIED**.


### C1 WSGI–FastAPI differential parity — CLOSED / VERIFIED — 2026-11-19

- Exact tested source SHA: `62054b53119308eca9d2256dcd5aae5561da235b`.
- FastAPI workflow run [44534512421](https://github.com/kenznguyen/btcquant-application/actions/runs/44534512421), job `135596271306`: **26/26 PASS**. The log explicitly records `test_same_fixture_has_identical_status_headers_and_body_for_contract_cases ... ok`, followed by `Ran 26 tests` and `OK`.
- FastAPI artifact `14533664834`, SHA-256 `555c63db97aa8466857cb4dd84728808989edc8107b25af0af31336bd3e84883`. Downloaded and inspected ZIP: `runner_metadata.txt` confirms both `workflow_commit` and `checked_out_source_sha` equal the exact SHA; `test_count=26`, `test_exit_code=0`. Test log included in artifact.
- SQLite aggregate workflow run [44534512612](https://github.com/kenznguyen/btcquant-application/actions/runs/44534512612), job `135596271401`: **196/196 PASS**, log ends `Ran 196 tests` / `OK`.
- SQLite artifact `14534628423`, SHA-256 `8e9c5274d48a44bb779bdd1db4119d3a83f1873c61ff889b769fc03fd6a0cfb0`. Downloaded and inspected ZIP: metadata confirms exact source SHA and expected 196 tests; aggregate test log confirms pass.
- Both workflow runs have event `push`, branch `main`, and exact `head_sha` equal to `62054b53119308eca9d2256dcd5aae5561da235b`; both conclusions are `success`.
- C1 finding (absence of same-fixture WSGI–FastAPI differential test): **CLOSED / VERIFIED** for the ten explicit contract cases in `market_data/test_fastapi_parity.py`. This does not claim exhaustive equivalence for every possible HTTP request or environment.
- D1 (runtime-only clean-install smoke test) remains **NOT VERIFIED**. Independent second-person review remains **PENDING**; this CI proof is not independent review.
- WSGI/Gunicorn retirement remains **NOT APPROVED**; runtime/deployment remains **NOT AUTHORIZED**; production readiness remains **NOT CERTIFIED**.
- Scope unchanged: no API implementation behavior, canonical SQLite data, writer/lease/feeder/recovery, T1/T2, PostgreSQL, VPS/systemd, runtime, deployment, retention/deletion or trading was modified or accessed.


### FastAPI independent review package refreshed after C1 closure — 2026-11-19

- Updated reviewer package: [T0 FastAPI Independent Review Package](reviews/T0_FASTAPI_INDEPENDENT_REVIEW_PACKAGE_2026-11-19.md), commit `495c234d920feaec8a323044955b42a80c6d5ea1`.
- Exact review snapshot: `440379b243d0b63e80f22b032fa8499bc2e1a6f4`; exact tested implementation/workflow SHA: `62054b53119308eca9d2256dcd5aae5561da235b`.
- Verified compare: 4 commits ahead / 0 behind; only `docs/PROJECT_SESSION_HANDOFF.md` and `docs/T0_ACTIVE_SCOPE_INDEX.md` changed after the tested SHA; no executable source, test, workflow or dependency drift.
- Package now includes C1's ten-case same-fixture differential test, exact FastAPI 26/26 run `44534512421` / job `135596271306` / artifact `14533664834` / SHA-256 `555c63db97aa8466857cb4dd84728808989edc8107b25af0af31336bd3e84883`, and SQLite 196/196 run `44534512612` / job `135596271401` / artifact `14534628423` / SHA-256 `8e9c5274d48a44bb779bdd1db4119d3a83f1873c61ff889b769fc03fd6a0cfb0`.
- C1 remains **CLOSED / VERIFIED** for ten enumerated cases. D1 clean runtime-only install smoke test **NOT VERIFIED**. Independent second-person review **PENDING**; no reviewer has been assigned or approved.
- No source/test/workflow/dependency/runtime/data changes; no tests or workflows run for this documentation refresh.
- WSGI/Gunicorn retirement **NOT APPROVED**; runtime/deployment **NOT AUTHORIZED**; production readiness **NOT CERTIFIED**.


### FastAPI adversarial self-review follow-up — 2026-11-19

- Review report: [T0 FastAPI Adversarial Self-Review Follow-up](evidence/T0_FASTAPI_ADVERSARIAL_SELF_REVIEW_FOLLOWUP_2026-11-19.md), commit `17ab5aa4cc246f5eafb618fbe9eaddc963399bee`.
- Reviewed snapshot: `440379b243d0b63e80f22b032fa8499bc2e1a6f4`; tested implementation/workflow SHA: `62054b53119308eca9d2256dcd5aae5561da235b`.
- Same-assistant static review inspected FastAPI/WSGI adapters, shared contract, parity/ASGI tests, storage selection, dependency locks and workflow. No additional blocking source defect identified in the bounded review.
- D1 remains **OPEN / NOT VERIFIED**: workflow downloads runtime-lock wheels but installs only the test lock in its test container; a separate clean runtime-only install/import smoke test is not evidenced.
- Dependency CVE/advisory research, dynamic security testing, Nginx/reverse-proxy validation, Uvicorn/VPS runtime, load and latency testing remain NOT PERFORMED.
- Verdict: **PASS WITH VERIFICATION GAPS — SELF-REVIEW ONLY**. This reviewer participated in implementation and prior reviews; this is explicitly **NOT INDEPENDENT** and does not satisfy the second-person review gate.
- C1 remains **CLOSED / VERIFIED** for ten cases. Independent second-person review **PENDING**.
- No source/test/workflow/dependency/runtime/data changes; no tests or workflows run.
- WSGI/Gunicorn retirement **NOT APPROVED**; runtime/deployment **NOT AUTHORIZED**; production readiness **NOT CERTIFIED**.


### Canonical SQLite read-only inventory — 2026-11-19

- Evidence: [T0 Canonical SQLite Read-only Inventory](evidence/T0_CANONICAL_SQLITE_READONLY_INVENTORY_2026-11-19.md), commit `9fe5cf641081391ad23e79975d54a151a0414f69`.
- Target snapshot inspected: `e62ef2d52c30e9245a1499c52d15aeb002b37892`; source selected-file snapshot: `c0f48b8910655fdb40d14214ad048b1d3cfa7fe9`; earlier source audit: `eb91528bab2b994f283dbe34cd7b0bcbfe406cb5`.
- Migration manifest confirms canonical SQLite/data payload was not copied. Target `.data/market-data.sqlite3` is only a default path; empty-only initializer refuses existing paths and creates only an empty DB.
- Static schema: `candles` + `feeder_leases`; candle rows persist `available_at_ms`; scheduler completion watermarks are in-memory; recovery gaps are derived from candle coverage. No dedicated persisted provenance/manifest, scheduler cursor or recovery-checkpoint table was found in the inspected SQLite schema.
- Historical VPS path `/home/ubuntu/t0/app/.data/market-data.sqlite3` belonged to `btcquant-t0-t1-test-01`, deleted 2026-11-11. Historical observations (622,592 bytes, integrity `ok`, M15 2,045, H1 2,011) do not prove current existence or recoverability.
- Historical 2026-11-09 coverage PASS is limited to one M15 window (3/3) and one H1 window (3/3); full history and scheduler completion remain NOT VERIFIED.
- Disposition: repository/schema inventory PASS (static only); current canonical DB existence/access, current integrity, full M15/H1 coverage, provenance completeness, recovery continuity and backup/restore **BLOCKED / NOT VERIFIED**.
- No database/runtime/VPS access, copy/export/restore, source/test/workflow/dependency changes, tests or workflow runs. Documentation-only commit.
- Next: identify an owner-held canonical SQLite file or immutable backup and its approved read-only access location. No initializer, writer, restore, or migration action is authorized.


### Canonical data external recovery source search — 2026-11-19

- Owner explicitly authorized read-only external source inspection.
- Evidence: [T0 Canonical Data Recovery Source Search](evidence/T0_CANONICAL_DATA_RECOVERY_SOURCE_SEARCH_2026-11-19.md), commit `137f104ba3a1fb5bb748a256e7037fb87f27c58e`.
- Historical source inventory (blob `92b36a488619512ef64297b53a8fadb7db8608d8`, exact source HEAD `93f3b0e350cf62b205f8d2a3a84fd139e9c5f59e`) scanned a complete 994-entry tree and found no tracked raw candle/database payload or canonical M15/H1 bundle. Nine selected T0 Actions artifacts contained test/runtime logs only; two P1.8 artifacts were synthetic. Historical run listing covered newest 1,000 of 1,387 only.
- Current known-run artifact spot check: run `44272495963` artifact `14413755795` is Core-First code operational proof (not market data). Known runs `42021445350` and `41996998169` returned 404 from artifact listing. GitHub Releases listing and a fresh exhaustive Actions-run listing are NOT VERIFIED because the connected GitHub tool set exposes no such list operations.
- Dropbox active indexed search returned no matches for 16 relevant queries. Deleted/unindexed content, other accounts and local devices were not inspected.
- Status: selected GitHub artifacts **PASS — NOT DATA**; Dropbox search **NO MATCHES**; Releases **NOT VERIFIED**; exhaustive Actions history **PARTIAL**; canonical backup **NOT IDENTIFIED**; recovery readiness **BLOCKED / NOT VERIFIED**.
- No data downloaded/exported/restored, no runtime/VPS/SSH/API/exchange access, no workflow dispatch, no source/test/workflow/dependency/schema changes. Documentation-only; no workflow run/job/artifact.
- Next: inspect Releases in authenticated GitHub UI or provide an exact release asset URL; identify other owner-held cloud/local/device snapshots. If none exists, prepare a separate owner-approval proposal for RECONSTRUCTED Binance USD-M history. No reconstruction, download, T0 initialization, writer or canonical acceptance is authorized.


---

# CURRENT STATUS OVERRIDE — 2026-11-19 — Canonical SQLite + Dropbox snapshot design (Phase 1 only)

- Owner decision: Dropbox is the versioned, downloadable repository for validated official Canonical SQLite snapshots; it is not the live operational primary.
- Operational primary remains on a controlled local filesystem suitable for SQLite locking and writes. Never synchronize an actively written SQLite database or its WAL/SHM files directly through Dropbox.
- Design: `docs/decisions/T0_CANONICAL_SQLITE_DROPBOX_SNAPSHOT_DESIGN_2026-11-19.md`, commit `f0df0617c46a476ed89f313cbebf1c7e7f450fd2`.
- Snapshot protocol uses SQLite Online Backup API to a staging path, then closes and validates the snapshot, computes SHA-256, emits a provenance/coverage manifest, uploads as a new immutable version, and requires read-back checksum verification. Restore occurs to a separate destination and requires validation before any cutover.
- Official/verified acceptance requires SQLite integrity, schema, row counts, M15/H1 coverage, gaps, duplicate/OHLCV checks, lineage, manifest and checksum. A snapshot without a successful restore drill is only UPLOADED / NOT RESTORE-VERIFIED.
- Reconstructed market history must be explicitly labeled `RECONSTRUCTED`; it must never be represented as recovery of the historical original database.
- Authorization: **Phase 1 DESIGN / STATIC ONLY**. Static implementation checks and independent review are **NOT YET PERFORMED**. No database initialization, exchange download, data copy/export, snapshot, Dropbox upload, restore, VPS/runtime, writer/lease/feeder or deployment is authorized.
- No tests or workflows were run; no test run, job or artifact exists for this documentation-only increment.
- Next: bounded static review of the manifest/acceptance contract and update this handoff. Any reconstruction, snapshot/Dropbox operation, restore drill or primary cutover requires separate explicit approval.


---

# CURRENT STATUS OVERRIDE — 2026-11-19 — Canonical Dropbox snapshot design static review

- Static review report: `docs/reviews/T0_CANONICAL_SQLITE_DROPBOX_SNAPSHOT_STATIC_REVIEW_2026-11-19.md`, commit `c08d5e225140d02235206d4dabc4e24349370f3f`.
- Clarified design: `docs/decisions/T0_CANONICAL_SQLITE_DROPBOX_SNAPSHOT_DESIGN_2026-11-19.md`, update commit `d7274fa2678caca5a0fedb8ca64083809cdf356c`.
- Review baseline main HEAD: `5955423a8edc1661e9cd4f9b7b80a317c6bc77cf`. Read-only inspection covered the design, SQLite initializer/store/storage and feeder source, and prior T0 inventory.
- Verdict: **PASS WITH REQUIRED SPECIFICATION CLARIFICATIONS**. R1–R5 recorded: Dropbox create-only/no-overwrite plus file ID/revision and exact-revision readback; owner-approved M15/H1 UTC coverage/gap policy; mandatory provenance manifest; SQLite Online Backup API and isolated restore path/sidecar handling; explicit manifest validation/status transitions. R6 records `PRAGMA user_version` validation.
- Static source finding: no snapshot publisher, Dropbox adapter, manifest validator or restore verifier exists in the inspected repository scope. No implementation or restore behavior is proven.
- Coverage boundaries and acceptable-gap policy remain **BLOCKED pending owner decision**. No snapshot can be marked OFFICIAL / VERIFIED before those are approved and checked.
- No source/test/workflow/dependency/schema/data changes; no SQLite opened, exchange access, Dropbox action, VPS/runtime, snapshot, restore or cutover. No tests/workflows run; no run/job/artifact exists.
- Phase 1 remains DESIGN / STATIC ONLY. Next: owner review of clarified specification, including explicit M15/H1 coverage boundaries and gap policy. Implementation proposal requires separate approval.


## Latest evidence — archive payload validation (2026-11-20)

- **PASS:** `docs/evidence/T0_BINANCE_UM_BTCUSDT_ARCHIVE_PAYLOAD_VALIDATION_2026-11-20.md`
- 202/202 ZIP checksum and ZIP/CSV structural validations passed; 241,440 M15 + 60,360 H1 rows; no detected gaps or duplicates across the selected archive partition.
- **NOT VERIFIED:** completeness beyond 2019-12-31 through 2026-11-18; current REST tail and any SQLite build.
- No REST, SQLite, Dropbox, VPS/runtime, feeder/writer, deployment or cutover was performed.


### 404-object Binance archive provenance inventory static review — 2026-11-20

- Review: [T0 Archive Object Provenance Inventory Static Review](reviews/T0_ARCHIVE_OBJECT_PROVENANCE_INVENTORY_STATIC_REVIEW_2026-11-20.md).
- Reviewed baseline `d2c1ec24ddf3dd5ddc5970d231039799960f5404`; inventory blob `eb251ac0924b46add906123f99b82e054d887a59`.
- **PASS:** 404/404 unique object identities (202 ZIP + 202 paired `.CHECKSUM` sidecars); 202/202 ZIP records have key/size/SHA-256/row count/PASS; 202/202 ZIP digests match their paired sidecar assertions; all pairs resolve; 38 daily + 164 monthly ZIPs; row totals M15 241,440 / H1 60,360.
- **METADATA PARTIAL:** independent sidecar-object byte sizes and sidecar-payload SHA-256 were not retained and remain NOT VERIFIED. Do not infer them.
- Preserve accepted historical 11,277-byte aggregate reporting discrepancy; measure all 404 objects individually in any newly approved materialization.
- Materialization is owner-approved only after exact target preflight at `/srv/btcquant/staging/t0-reconstructed-btcusdt-20261120-run-001`. Preflight pending; no transfer, SQLite, Dropbox or runtime action.


### Independent archive manifest/staging/verification review — 2026-11-20

- Review: [T0 Archive Manifest, Staging and Verification Independent Review](reviews/T0_ARCHIVE_MANIFEST_STAGING_VERIFICATION_INDEPENDENT_REVIEW_2026-11-20.md).
- Reviewed HEAD `d947a97dc8908723de5cf2c800cd6df38d236f8c`; manifest `eb251ac0924b46add906123f99b82e054d887a59`; plan `99d4adc4ffb63ee22084fd5014dd3dd3da7e68cf`; owner approval `87a2be9ea1ca16f1ce3d5a27a9349c1132da698b`; payload evidence `45386fa75a61039ed12e7b6b0f18e48b2f1ef725`.
- Manifest static checks **PASS** for 404 unique object identities, 202 ZIP + 202 sidecars, ZIP metadata/pair assertions 202/202, and row totals M15 241,440 / H1 60,360. Historical sidecar own-object metadata remains NOT VERIFIED.
- Overall **REVIEW COMPLETE — EXECUTION PLAN BLOCKED**: reconcile stale staging-plan authorization wording, distinguish archive inventory from final dataset manifest, update stale sidecar approval condition, and clarify deterministic parser/transfer-cap/path-safety/CSV/timestamp/evidence rules.
- Exact approved target remains `/srv/btcquant/staging/t0-reconstructed-btcusdt-20261120-run-001`; preflight not run. No archive transfer or SQLite. SQLite separately NOT AUTHORIZED.


## 2026-11-20 — Offline REST tail validator prepared
- Added `market_data/rest_tail_validator.py` (blob `3437e7a9181611cfed77eab59afee27136472963`) and 10 deterministic regression tests (`market_data/test_rest_tail_validator.py`, blob `293d9a605b6ec6498d551504fda04eecf298601f`).
- Preparation evidence: `docs/evidence/T0_REST_TAIL_OFFLINE_VALIDATOR_PREPARATION_2026-11-20.md`, commit `4a6adce076b38e4aadb9e75fd561312880d9f09c`.
- Offline-only: reads saved M15/H1 JSON; no network, archive, SQLite or runtime access. Fixed cutoff 2026-11-20T08:02:15.852Z; expected closed counts M15 128, H1 32; forming 08:00 candle excluded.
- Synthetic unit tests and CLI fixture smoke PASS; no Actions workflow/run/artifact.
- Actual payload validation remains **BLOCKED / NOT VERIFIED** because previous personal-host probe did not retain raw JSON response arrays. No new REST retrieval is authorized by this validator; obtain separate approval before any new request.


---

# CURRENT STATUS OVERRIDE — 2026-11-20 — Personal-host REST tail retrieval and offline validation PASS

- Owner separately approved one bounded personal-host retrieval of Binance USD-M public REST klines for BTCUSDT M15/H1, preserving exact JSON response bodies locally, followed by the existing offline read-only validator.
- Evidence: `docs/evidence/T0_BINANCE_UM_BTCUSDT_REST_TAIL_PERSONAL_HOST_VALIDATION_2026-11-20.md`.
- Retrieval: M15 and H1 both HTTP 200 from CloudFront POP `SGN50-P3`; request IDs, response byte counts and locally reported SHA-256 values are recorded in the evidence. Payloads remain on the user's Windows machine and were not committed.
- Fixed cutoff `2026-11-20T08:02:15.852Z`; M15 129 raw / 128 closed / 1 forming excluded; H1 33 raw / 32 closed / 1 forming excluded.
- Actual offline validation output: both intervals `ok: true`, no errors, no missing grid intervals. Result **PASS for the bounded retrieved window and checks implemented by the validator**.
- Regression suite: 10/10 PASS on user's local Windows host. Local `git rev-parse HEAD` reported `04a0a6275ff44da20f0a40e11ab541f9c112459f`; branch `main`; working tree reported clean after removing generated `__pycache__`.
- No GitHub Actions run/job/artifact was produced. Retrieval script was an untracked local script outside the repository. Payloads and metadata remain local.
- This does not establish earliest-ever history, completeness outside the tested window, recovery of the lost Canonical SQLite, or a reconstructed database. Archive historical bounds and this REST tail window are separate evidence sets.
- No archive retrieval, SQLite open/write/create/import, Dropbox, VPS/runtime, feeder/writer, T1/T2, deployment, restore, cleanup, or trading action occurred.
- Next: preserve the evidence and handoff. Any archive materialization or SQLite reconstruction remains subject to its own explicit approval and existing gates.


---

# CURRENT STATUS OVERRIDE — 2026-11-20 — RECONSTRUCTED dataset documentation reconciliation

## 2026-11-20 — Documentation-only reconciliation approved and recorded

- Owner instruction: pause all personal-PC runtime work; approve documentation-only reconciliation of the archive evidence and the separately validated Binance USD-M BTCUSDT REST tail for a future `RECONSTRUCTED` dataset.
- Current evidence: archive 202 ZIP + 202 paired sidecars; historical payload validation M15 241,440 / H1 60,360 rows through M15 2026-11-18 23:45 UTC and H1 2026-11-18 23:00 UTC. REST tail was retrieved once from the personal Windows host and offline validated at fixed cutoff 2026-11-20T08:02:15.852Z: M15 129 raw / 128 closed / 1 forming excluded; H1 33 raw / 32 closed / 1 forming excluded; both `ok=true`, no errors/gaps.
- Archive/REST boundary is contiguous for both intervals. Conditional candidate combined counts are M15 241,568 and H1 60,392; not yet source-reconciled or approved for import.
- New REST source manifest: `docs/manifests/T0_BINANCE_UM_BTCUSDT_REST_TAIL_SOURCE_EVIDENCE_2026-11-20.json`.
- Updated draft dataset manifest: `docs/manifests/T0_RECONSTRUCTED_BTCUSDT_M15_H1_MANIFEST_DRAFT.json`; remains `DRAFT_NOT_FOR_DATABASE_BUILD`, SQLite `NOT_CREATED_NOT_AUTHORIZED`.
- Updated execution plan addendum: `docs/plans/T0_CANONICAL_SQLITE_RECONSTRUCTION_EXECUTION_PLAN_2026-11-20.md`. Complete-coverage plan annotated but remains blocked because earliest-ever history and post-cutoff tail are not verified.
- Key unresolved gates: 11,277-byte historical archive aggregate discrepancy; per-sidecar historical own size/SHA; current archive source availability; exact host and destination; importer SHA/dependency lock; source-to-candle reconciliation; duplicate/conflict policy; owner-approved `available_at_ms` semantics (archive historical first-observation time is not evidenced); gap/exception policy.
- Runtime work on personal PC is **PAUSED**. No tests or workflows, Actions runs/jobs/artifacts, REST calls, archive access/download/copy, host preflight, SQLite create/open/write/import/validation, runtime, T1/T2, deployment or trading occurred for this documentation update.
- SQLite creation/import remains **NOT AUTHORIZED** and requires separate explicit approval naming exact host/path, source inventory, importer SHA, coverage/gap policy and validation gates. No Canonical promotion is implied.
- Next: documentation review only if requested; otherwise hold.


---

# CURRENT STATUS OVERRIDE — 2026-11-20 — T0 API contract and adapter parity

- Evidence: `docs/evidence/T0_CANDLE_CONTRACT_FAIL_CLOSED_AND_APPLICATION_ADAPTER_PARITY_2026-11-20.md`.
- Source/test HEAD: `fc2e48420c6bbd00b7c5cfbaa8b3d7b2fc996235`.
- T0 FastAPI contract: **65/65 PASS**, run [44728558303](https://github.com/kenznguyen/btcquant-application/actions/runs/44728558303), artifact ID `14625231382`.
- T0 SQLite aggregate: **174/174 PASS**, run [44728445702](https://github.com/kenznguyen/btcquant-application/actions/runs/44728445702), artifact ID `14624483667`.
- Application API parity: shared `candle_envelope()`, strict query parser, matching error behavior, cache/content headers and freshness fields. Adjacent F4 tests also PASS; see evidence report for exact runs and digests.
- Internal review PASS; independent second-person review **PENDING**. Cross-layer runtime connection remains **BLOCKED / NOT AUTHORIZED**.
- Original M15/H1 REST files were not accessed; integrity remains **NOT VERIFIED** pending independent hash recomputation from the exact source files.


---

# CURRENT STATUS OVERRIDE — 2026-11-21 — T0 offline archive CSV parser TDD increment

- Owner approved a bounded TDD increment: pure offline parser plus tests using only the synthetic M15/H1 fixtures. No real archive/REST, host/VPS, SQLite, Canonical T0, Contract 1.2.0, importer, workflow YAML, runtime or deployment work was authorized.
- Parser: `market_data/archive_csv_parser.py`, blob `7d59706778a98a18185e0b2fe744c3c43c2eb870`.
- Tests: `market_data/test_archive_csv_parser.py`, blob `50199cd168fd52314a846760cc4baf51a8cd5e9a`; 19 unittest methods.
- Fixtures: M15 blob `1a616fde511407d90be8894391e783e716908c9d`; H1 blob `951f26ff4e4a6c330a14f5a515cc27cce8053e1e`. Both are explicitly SYNTHETIC — NOT SOURCE EVIDENCE.
- Final source snapshot SHA: `59fbc79d7df33da09c8e483923dc64964003d31e`. Evidence record: `docs/evidence/T0_ARCHIVE_CSV_PARSER_TDD_2026-11-21.md`, commit `ae45b421d69c15eb62089221cb8384df6a759b93`.
- TDD RED reproduced missing module import before implementation. GREEN focused test command `python -B -m unittest -v market_data.test_archive_csv_parser`: **19/19 PASS** in an isolated local Python 3.13 scratch harness using byte-for-byte blob-matched parser, test and fixture files.
- GitHub Actions run/job/artifact: **NOT RUN**; workflow YAML was explicitly outside this approval. Full repository regression: **NOT RUN**.
- Real archive format/parser compatibility: **NOT VERIFIED**; exact source CSV header/encoding/member/delimiter/numeric grammar/close-time convention remain unfrozen. Parser contract freeze is **BLOCKED** pending approved real-source evidence or a new owner decision.
- No archive/REST access, host/VPS, SQLite, Canonical data, importer, Contract 1.2.0 schema/API, workflow, runtime, deployment, T1/T2 integration, exchange credentials or trading was accessed or changed.
- Next: preserve this parser as a provisional offline test utility. Request separate approval before any source-format verification, Contract 1.2.0 work, importer, workflow or staging execution.


## 2026-11-21 — Real archive CSV sample verification approved, execution gated

- Owner approved exactly 6 ZIP + 6 paired .CHECKSUM objects (M15/H1, first/middle/latest sample periods) for real-source CSV format inspection on a GitHub-hosted ephemeral runner.
- Decision: docs/decisions/T0_ARCHIVE_CSV_REAL_FORMAT_SAMPLE_VERIFICATION_APPROVAL_2026-11-21.md, commit f46f1b2e76c0fcdc38ecde6c45c8fee52e76f904.
- Inventory blob: eb251ac0924b46add906123f99b82e054d887a59. Exact sidecars are resolved only through each selected ZIP's paired_sidecar_key in that inventory.
- BLOCKED — NOT EXECUTED: workflow YAML creation was explicitly excluded; obtain separate approval for a one-purpose manual workflow. No archive object was fetched.
- Parser contract freeze, importer, SQLite and Contract 1.2.0 implementation remain unauthorized pending real-source evidence and separate decisions.
