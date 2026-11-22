# CURRENT STATUS OVERRIDE — 2026-11-22 — Phase B revision 3 submitted for independent design review

- Revised design: `docs/design/T0_PHASE_B_DETAILED_SCHEMA_AND_CANONICAL_CONTRACT_DESIGN_2026-11-22.md`.
- Exact design commit: `98cde283e9b2dc2d0201e4359e3f1195016ff0ea`.
- Exact design blob SHA: `2e61e13ec8dc42a37ea03130edc1491b73a903bc`.
- Revision 3 self-review: `docs/reviews/T0_PHASE_B_DESIGN_SELF_REVIEW_ROUND_3_2026-11-22.md`, commit `7d9a8f1013a5665ac6303c63a1da3894dec3665b`; verdict READY TO SUBMIT FOR INDEPENDENT DESIGN REVIEW, NOT design approval.
- Independent review request: `docs/reviews/T0_PHASE_B_DESIGN_REVIEW_ROUND_3_REQUEST_2026-11-22.md`, commit `9c8ca98e082f72f8fc031c0092ad14c521530c6f`; status REQUESTED / PENDING.
- Revision 3 corrections:
  - R-07: aggTrade E=event time, T=trade time; T1 CSV timestamp_ms is candidate T only, E unavailable unless independently captured.
  - R-08: snapshot completeness means complete capture of the exact bounded top-N response, not full exchange book; manifest binds source/endpoint, requested limit, bid/ask/total counts, digest, completion and non-RPI scope; derived book remains bounded.
  - R-09: source-delivery/import cursor separated from contiguous book-sequence watermark, including durable quarantine, restart and replay semantics.
  - R-10: separate raw message bytes, levels, numeric token/precision, aggregate buffer bytes, snapshot rows/bytes and parser-structure ceilings; fail-closed on limit.
  - R-11: all T1 quantity→q mappings consistently candidate / NOT VERIFIED; nq never derived.
  - R-01..R-06 conceptual gaps reconciled: stream_epoch is provenance not identity; snapshot identity/completeness remains source-blocked; q/nq distinguished; ordinary depth explicitly non-RPI; E/T/receive/T0 clocks separated; gap/reorder policy includes resource ceilings and separate cursors.
- Synthetic matrix: **66 proposed cases** (SD-05 14, SD-06 25, SD-07 19, cross-domain 8), **NOT EXECUTED**.
- Blockers: B-01..B-20 remain open pending evidence or bounded owner acceptance. In particular SD-06 canonical acceptance remains blocked pending update-ID uniqueness proof; current T1 CSV snapshots remain not canonically acceptable pending source-generated capture identity/completeness; source mappings, numeric limits, digest encoding, API compatibility and atomic persistence remain unfrozen.
- Independent second-person review: **NOT PERFORMED YET**.
- Tests/workflows/artifacts: **NOT RUN / NONE**.
- Scope: documentation-only. No code, DTO, parser, validator, fixture, tests, DDL, database, data movement, T1 source/runtime, network, credentials, T1→T0/T2 runtime, VPS/deployment, Phase C or trading action.
- Latest main before this handoff update: `9c8ca98e082f72f8fc031c0092ad14c521530c6f`.
- Next: obtain independent review of exact design commit/blob above; do not freeze contracts or start implementation/Phase C before separate owner decision.

---

# CURRENT STATUS OVERRIDE — 2026-11-22 — Phase B second-round self-review: REQUEST CHANGES

- Exact reviewed design commit: 75e593517ec31d2e2a75ed0050e80ab5dd52edf2.
- Exact reviewed design blob: 56f2012d6625e5af328d7d5881d892a38a2121e9.
- Self-review report: docs/reviews/T0_PHASE_B_DESIGN_SELF_REVIEW_ROUND_2_2026-11-22.md
- Self-review report commit: 2f6317b28502bc06202daf673f1f32c41f847c88
- Verdict: **REQUEST CHANGES — PHASE B DESIGN NOT APPROVED**.
- Original findings R-01..R-06 dispositions: R-01 partially resolved (identity uniqueness proof remains blocked); R-02 partially resolved (manifest must bind bounded source/endpoint/limit); R-03 partially resolved (q mapping status inconsistent); R-04 addressed with bounded-depth qualification still required; R-05 partially resolved (aggTrade E/T mapping error and SD-07 snapshot E/T omission); R-06 partially resolved (separate source-delivery cursor vs book-sequence watermark and byte/resource bounds missing).
- New findings R-07..R-11: R-07 CRITICAL aggTrade E/T mapping reversed; R-08 snapshot completeness conflated with full-depth book despite USD-M REST depth being bounded (limit max 1000); R-09 source-delivery acknowledgement cursor and book sequence watermark not explicitly separated; R-10 event-count/age bounds do not bound bytes/levels/parser resource use; R-11 q mapping status is internally inconsistent.
- Review evidence: Binance USD-M aggTrade docs define E=event time and T=trade time; pinned T1 schema says timestamp_ms=trade time. Binance USD-M /fapi/v1/depth returns limited market depth with valid limits up to 1000. URLs and exact observations are recorded in the review report.
- Synthetic matrix: existing 45 cases remain NOT EXECUTED; must add coverage for R-07..R-11 and reconcile test descriptions.
- Independent second-person review: **NOT PERFORMED**. This is a self-review, not an independent review.
- Contract freeze: NOT APPROVED. Implementation, Phase C and runtime actions remain NOT AUTHORIZED.
- Tests/workflows/artifacts: NOT RUN / NONE.
- Next: revise design R-07..R-11, reconcile R-01..R-06 dispositions, update matrix and blockers, then submit a new exact SHA for review. Documentation-only.

---

# CURRENT STATUS OVERRIDE — 2026-11-22 — Phase B revision 2 submitted for second design review

- Revised Phase B design: docs/design/T0_PHASE_B_DETAILED_SCHEMA_AND_CANONICAL_CONTRACT_DESIGN_2026-11-22.md
- Design commit: 75e593517ec31d2e2a75ed0050e80ab5dd52edf2
- Design blob SHA: 56f2012d6625e5af328d7d5881d892a38a2121e9
- Second-round review request: docs/reviews/T0_PHASE_B_DESIGN_REVIEW_ROUND_2_REQUEST_2026-11-22.md
- Review-request commit: 8c358bdb3da2447e11e28c026d43e278150eb672
- First-round review: docs/reviews/T0_PHASE_B_DESIGN_REVIEW_2026-11-22.md, commit 347dbcec6f7ddedac4ac1c8e90ee57c549ae49ef; verdict REQUEST CHANGES.
- R-01..R-06 revised in the design: canonical event identity is separated from stream epoch; snapshot capture identity/completeness is a hard gate; aggTrade q/nq are distinguished; ordinary depth is explicitly non-RPI; depth E/T and receive/commit clocks are distinct; bounded reorder/gap/checkpoint/recovery rules are specified.
- Synthetic matrix expanded to 45 proposed cases: SD-05 10, SD-06 20, SD-07 15. NOT EXECUTED.
- B-01..B-16 remain open. The design revision does not prove source implementation behavior or freeze contracts.
- Second-round independent review: REQUESTED / PENDING; no second-round verdict yet.
- Tests/workflows/artifacts: NOT RUN / NONE.
- Phase B remains documentation-only. No code/DTO/parser/validator/tests/fixtures/DDL/database/data movement/network/credentials/T1 source/runtime/T1→T0/T2/VPS/deployment/trading actions.
- Next: complete second-round review, address any new findings, then seek explicit owner decision. Phase C and implementation remain blocked.

---

# CURRENT STATUS OVERRIDE — 2026-11-22 — Phase B design review requests changes

- Review record: `docs/reviews/T0_PHASE_B_DESIGN_REVIEW_2026-11-22.md`, commit `347dbcec6f7ddedac4ac1c8e90ee57c549ae49ef`.
- Reviewed Phase B design baseline: `docs/design/T0_PHASE_B_DETAILED_SCHEMA_AND_CANONICAL_CONTRACT_DESIGN_2026-11-22.md`, commit `efbce3477c367ddc7be3e7ccfb430ba897b3e9d8`, blob `ca57a4f8628d95471bdd575d3846b1db49a4f1f5`.
- Verdict: **REQUEST CHANGES — PHASE B DESIGN NOT APPROVED**.
- Required findings R-01..R-06:
  1. Separate SD-06 canonical event identity from stream/session epoch.
  2. Make snapshot capture identity and completeness proof hard acceptance gates.
  3. Account for Binance USD-M Aggregate Trade `nq` missing from documented T1 CSV.
  4. Explicitly define non-RPI vs RPI depth scope.
  5. Account for depth transaction time `T` missing from documented T1 CSV.
  6. Define bounded out-of-order handling, gap detection/recovery and checkpoint behavior.
- Existing B-01..B-13 source/provenance/checkpoint/API blockers remain open; do not freeze contracts by assumption.
- Phase B remains documentation-only. No code, tests, fixtures, DDL, DB, data movement, T1 source/runtime, network, credentials, T1→T0/T2, VPS/deployment or trading actions.
- Tests/workflows/artifacts: **NOT RUN / NONE**.
- Next: revise Phase B design for R-01..R-06, then request another owner review. Do not begin Phase C or implementation.

---

# CURRENT STATUS OVERRIDE — 2026-11-22 — Phase A owner-approved; Phase B documentation-only design in progress

- Owner review decision: **PHASE A DESIGN APPROVED; PHASE B DOCUMENTATION-ONLY AUTHORIZED**. Owner note: none.
- Decision record: `docs/decisions/T0_PHASE_A_OWNER_REVIEW_APPROVAL_AND_PHASE_B_DOCUMENTATION_AUTHORIZATION_2026-11-22.md`, commit `f2f5741cad47b86c70dae23dbaa9b497258cc80a`.
- Approved Phase A baseline: `docs/design/T0_PHASE_A_DETAILED_SCHEMA_AND_CANONICAL_CONTRACT_DESIGN_2026-11-22.md`, design commit `4fdf1412539e784ab6a72338b8198f3c72c76349`, reviewed blob `9aeec4b04d838b5bf70a1ce5041eb34cb6d3f1fd`.
- Phase A approval does **not** freeze its contracts. A-01..A-10 remain open until evidence-backed resolution or explicit bounded owner acceptance.
- Phase B design draft: `docs/design/T0_PHASE_B_DETAILED_SCHEMA_AND_CANONICAL_CONTRACT_DESIGN_2026-11-22.md`, commit `efbce3477c367ddc7be3e7ccfb430ba897b3e9d8`, blob `ca57a4f8628d95471bdd575d3846b1db49a4f1f5`.
- Phase B scope: SD-05 aggregate trades; SD-06 order-book depth diffs; SD-07 order-book snapshots. T1 source schema inspected read-only: `kenznguyen/binance-futures-collector/docs/SCHEMA.md`, blob `895f87a8281a3f9b6d37d96b5f68568e4285bee6`.
- Key Phase B blockers: aggTrade field semantics/build mapping; depth stream epoch absent from documented CSV; snapshot capture ID and group completeness absent; sequence bridge rules require exact exchange/source verification; digest/provenance/checkpoint/API versioning remain unfrozen.
- Phase B status: **DOCUMENTATION DRAFT COMPLETE / OWNER REVIEW REQUIRED**. Design acceptance/freeze is not implied.
- Tests/workflows/artifacts: **NOT RUN / NONE** for this documentation work.
- No code/DTO/parser/validator/test/fixture/workflow changes; no DDL/database/data movement/import; no T1 source change/activation/T1→T0/T2 runtime; no network/credentials/VPS/deployment; no order submission or trading.
- Next: owner review Phase B design draft and B-01..B-13. Do not proceed to Phase C or implementation without a separate explicit decision.

---

# CURRENT STATUS OVERRIDE — 2026-11-22 — Phase A detailed design ready for owner review

- Phase A design: `docs/design/T0_PHASE_A_DETAILED_SCHEMA_AND_CANONICAL_CONTRACT_DESIGN_2026-11-22.md`
- Design commit: `4fdf1412539e784ab6a72338b8198f3c72c76349`
- Status: **PHASE A DESIGN COMPLETE FOR OWNER REVIEW / CONTRACT FREEZE NOT APPROVED**.
- Scope: SD-01 trade OHLCV; SD-02 mark-price klines; SD-03 index-price klines; SD-04 premium-index klines; SD-09 funding rates; SD-10 open interest.
- Evidence pinned in design: T1 SCHEMA blob `895f87a8281a3f9b6d37d96b5f68568e4285bee6`; T1 README `5e03d3e00bb4b1fe6ed4ed389006e50d5683c5e3`; T0 `market_data/store.py` `4e1b0c54bd56455abe5be0e5c7d0807e63e0bc78`; T0 market-data README `6561214efdca5108672b83809a9c12047462d72b`.
- Important boundaries: existing T0 Candle contract remains BTCUSDT M15/H1 closed trade candles; T1 1m klines lack explicit finality/receive-time fields and are not canonical-acceptance-ready; MARK/INDEX/PREMIUM_INDEX remain separate price-basis series; funding `next_funding_time` is settlement time, not sample identity; OI fields are retained independently and arithmetic precision needs evidence.
- A-01..A-10 are open contract-freeze blockers/owner decisions. Digest encoding, provenance persistence, source overlap, file-close/checkpoint semantics and non-candle versioning remain unfrozen.
- Synthetic test matrix drafted but NOT EXECUTED. Tests/workflows/artifacts: NOT RUN / NONE.
- No code, DTO, parser, test, workflow, DDL, database, data movement, network, credentials, T1 runtime, T1→T0/T2, VPS, deployment, order submission or trading action.
- Phase B must remain paused until owner reviews/approves Phase A design baseline. If approved, Phase B starts documentation-only.
- Status: **PHASE A DESIGN PASS (DOCUMENTATION) / OWNER REVIEW REQUIRED / PHASE B BLOCKED PENDING REVIEW / IMPLEMENTATION NOT AUTHORIZED**.

---

# CURRENT STATUS OVERRIDE — 2026-11-22 — Owner approved source-domain onboarding priority

- Owner approval record: `docs/decisions/T0_SOURCE_DOMAIN_ONBOARDING_PRIORITY_OWNER_APPROVAL_2026-11-22.md`, commit `44e72107604f39ff4a412befa940a4b25d5a81b0`.
- Design addendum: `docs/design/T0_SOURCE_DOMAIN_ONBOARDING_PRIORITY_ADDENDUM_2026-11-22.md`, commit `eb80f8eb6eb86a9a6d3d54951cb27d23c2032141`.
- Approval fixes design/onboarding order only:
  - Phase A: SD-01 trade OHLCV; SD-02 mark-price klines; SD-03 index-price klines; SD-04 premium-index klines; SD-09 funding rates; SD-10 open interest.
  - Phase B: SD-05 aggregate trades; SD-06 order-book depth diffs; SD-07 order-book snapshots.
  - Phase C: SD-08 liquidations/force orders; SD-11 long/short ratios; SD-12 taker buy/sell ratio; SD-13 source health/gaps/checkpoints.
- Next authorized work: Phase A detailed native-schema mapping, provenance/identity/dedup/conflict/checkpoint contract refinement and synthetic test-case design — documentation only.
- Phase B/C remain sequenced after Phase A design review. No implementation is authorized by this priority approval.
- SD-08 liquidation canonical acceptance remains BLOCKED: T1 CSV lacks native order/trade event ID; do not invent collision-safe composite identity.
- Overall source inventory/ingestion contract remains a design proposal; this priority order does not freeze schema, digest encoding, storage or transport.
- No code, tests, workflows, DB/schema, data movement, network, runtime, credentials, T1 provider activation, T1→T0/T2 connectivity, VPS/deployment, order submission or trading actions occurred. Tests/workflows/artifacts: NOT RUN.
- Preserve T0 as sole canonical owner, T1 code in its own repository, raw source evidence, no destructive deletion after acknowledgement, paper-first/no-live-trading guardrails.
- Status: **PRIORITY APPROVED / PHASE A DESIGN NOT STARTED / IMPLEMENTATION NOT AUTHORIZED**.

---

# SOURCE SCHEMA MAPPING CHECKPOINT — 2026-11-22

- T1 native CSV schema inspected: `kenznguyen/binance-futures-collector/docs/SCHEMA.md`, source blob SHA `895f87a8281a3f9b6d37d96b5f68568e4285bee6`.
- Inventory/contract refined to match documented T1 columns and timestamp semantics. Funding and OI timestamps are sample times; long/short and taker ratio timestamps are bucket starts; klines use bar-open time; trades/liquidations/depth diffs use event/trade time.
- Important blocker: T1 liquidation CSV schema omits native order/trade event ID. Timestamp + symbol + side + price + quantity may collide; liquidation domain must remain quarantined until a collision-safe source identity is approved or the source contract is extended.
- Order-book snapshots are one row per level; T0 must group levels by snapshot event/time/update ID before canonical acceptance.
- Updated design commit: `16ba0af5290a9869a564ad853ca3d77d1ffd4a78`.
- Design remains OWNER REVIEW REQUIRED; no code/tests/workflows, runtime, network, DB or data actions.

---

# DESIGN CHECKPOINT — 2026-11-22 — Source Domain Inventory & Canonical Ingestion Contract v1

- Design document: `docs/design/T0_SOURCE_DOMAIN_INVENTORY_AND_CANONICAL_INGESTION_CONTRACT_V1_2026-11-22.md`
- Design commit: `95f78306eaf793862c5e0c6f1f5c1bc24c38ef60`
- Status: **DESIGN PROPOSAL — OWNER REVIEW REQUIRED**; no implementation authorization.
- Initial inventory covers 13 domain families: trade OHLCV candles; mark/index/premium candles; aggregate trades; order-book diffs and snapshots; liquidations; funding; open interest; three long/short ratio variants; taker buy/sell ratio; source health/gaps/checkpoints.
- Contract defines source ownership, canonical envelope/provenance, domain identities, at-least-once/idempotent ingestion, replay-vs-conflict behavior, quarantine, checkpoint acknowledgement, T0 single-writer boundary and staged rollout.
- T1 README inventory used; exact native CSV column mapping remains PARTIAL until `docs/SCHEMA.md` and relevant T1 source schemas are inspected.
- Open decisions remain: liquidation collision-safe identity, kline finality/revisions, source overlap/conflict policy, non-candle canonical digest encoding, physical multi-domain SQLite schema/capacity, transport, per-stream checkpoint and raw evidence retention.
- No tests/workflows/artifacts. No code/schema/database/data/network/runtime/VPS/deployment changes. T1→T0 runtime ingestion remains NOT AUTHORIZED.
- Next: owner confirms/amends inventory and BTCUSDT-first source priority; then native schema mapping and contract freeze, documentation-only.

---

# ARCHITECTURE STATUS OVERRIDE — 2026-11-22 — Independent Multi-Source Data Foundation OWNER-APPROVED

- Controlling decision: `docs/decisions/INDEPENDENT_MULTI_SOURCE_DATA_FOUNDATION_OWNER_DECISION_2026-11-22.md`, recorded in commit `f8d2dacc8d33b05114403a8ba5ceb286be44d6f3`.
- Owner explicitly confirms that Independent Multi-Source Data Foundation was approved. Current repository history inspected in this reconciliation did not expose the original approval date/commit; do not invent one.
- T0 is the independent multi-source Data Foundation and canonical ownership boundary for accepted market data. T1 remains a specialized collector in its own repository and supplies source data to T0 through separately approved contracts/ingestion. T1 is not a competing canonical store.
- Preserve T1 code ownership and raw capture/replay implementation in `kenznguyen/binance-futures-collector`; do not copy/fork the full collector into `btcquant-application`.
- This supersedes older statements that T0 and T1 are independent competing data assets or that the approved architecture has no T1→T0 data path. It does not itself authorize T1→T0 runtime connectivity.
- SQLite remains the recorded T0 storage direction. Former Canonical SQLite remains LOST; reconstructed SQLite remains NOT CREATED per latest T0 records. No DB creation/migration/promotion/cutover is authorized by this architecture correction.
- T2 Core and independent AI consume versioned T0 datasets; derived features/caches/training bundles are not competing canonical stores. All trade intents remain behind shared risk controls; paper-first/no-live-trading restrictions remain.
- This is documentation/governance only. No tests/workflows, database, source ingestion, runtime, VPS, deployment, provider activation or trading actions.
- Current implementation status: **NOT VERIFIED / NOT COMPLETE**. Next: design source-domain inventory and canonical ingestion contracts only; obtain separate approval before implementation or runtime.

---

# CURRENT STATUS OVERRIDE — 2026-11-22 — F1–F7 synthetic matrix GREEN; independent review on final snapshot pending

- Current `main` HEAD before this handoff update: `264e87d5d04ed4565bbebf4da1775d1587458106`.
- Latest tested implementation source SHA: `284d9d243d529b84de4318e65266993fad71a757`.
- Exact-SHA CI run [45011049882](https://github.com/kenznguyen/btcquant-application/actions/runs/45011049882), job `137173247655`, SUCCESS; requested SHA = checkout SHA.
- Results: importer-core 20/20; S1.2 adapter 43/43; staging schema 32/32; full `market_data` regression 496/496 PASS. CPython 3.13.18 / SQLite 3.45.1 focused; CPython 3.12.16 full regression. Artifact count 0.
- Latest source blobs: schema `f530f4f2f394dfb018e5bc750d04974df8b1adcd`; schema tests `e1555b424aacb15b06894ddfc34a99b2989e9ad5`; adapter `70bcf83c37936593e394c8476134046a7da70f4c`; adapter tests `19cd18b40cb61252094b5805eb9d3cc35a7ff39b`; unchanged S3/V1 validator `b94bac0f82ae141984552409f99a5cff70435b3b`; S1 fixture `41f5b21eaa418bb32f4f40e00de7e920ca39c4bf`; workflow `0e319368fc36d8752f8e1640c3dd513dc18fd0ce`.
- F1–F7 synthetic matrix PASS. F6 exact-bool opt-in guard is GREEN. F7 installs the append-only authorizer before COMMIT; authorizer-installation failure rolls back all schema objects and user_version. RED run `45011014408`; GREEN run `45011049882`.
- Physical schema spec synchronized with owner-approved Amendments A/B; F2 contract and evidence updated.
- Independent review PR #5: [DO NOT MERGE](https://github.com/kenznguyen/btcquant-application/pull/5). Latest review PR head `72be6af7a87c9c6fe0d76bcc6e486a699b39dfbb`; tested implementation source SHA `284d9d2`. All 14 original↔snapshot blob pairs verified identical in `REVIEW_SCOPE.md`.
- Codex review has been requested against latest PR head; its latest status comment still references the previous review head while the latest request is queued. Do not accept until the bot reports `72be6af`. Graphify status also refers to an earlier head and is not accepted.
- Remaining design blocker: candidate snapshot digest preimage/serialization remains unspecified. Current validator checks shape/presence and CANDIDATE↔VALIDATED equality only; do not invent formula.
- F2: **PARTIAL / SYNTHETIC CI PASS** pending independent review and candidate digest design decision. S1.2: **NOT FROZEN**. Independent review: **PENDING**. B8: **NOT APPROVED**. Real-data staging: **NOT AUTHORIZED**.
- Evidence: `docs/evidence/T0_S1_2_F2_DTO_READONLY_PROJECTION_CI_2026-11-22.md`.
- Next: wait for independent Codex review on PR #5 head `72be6af`; triage findings, implement only approved synthetic-scope fixes, rerun exact-SHA CI and request follow-up review.
- Exclusions unchanged: no real archive/sidecar access/acquisition, host/workstation/SSH/filesystem/runner preflight, B8 workflow/dispatch/runner, real-data staging, uploads/retention/deletion/cleanup, Canonical T0, MAY-10/REST tail/T1/T2 runtime/VPS/deployment/credentials/exchange/trading.

---

# CURRENT STATUS OVERRIDE — 2026-11-22 — F1–F7 synthetic matrix GREEN at latest SHA; independent review snapshot refresh required

- Latest tested implementation source SHA: `284d9d243d529b84de4318e65266993fad71a757`.
- Exact-SHA CI run [45011049882](https://github.com/kenznguyen/btcquant-application/actions/runs/45011049882), job `137173247655`, SUCCESS; requested SHA = checkout SHA.
- Results: importer-core 20/20; S1.2 adapter 43/43; staging schema 32/32; full `market_data` regression 496/496 PASS. CPython 3.13.18 / SQLite 3.45.1 focused; CPython 3.12.16 full regression. Artifact count 0.
- Latest source blobs: schema `f530f4f2f394dfb018e5bc750d04974df8b1adcd`; schema tests `e1555b424aacb15b06894ddfc34a99b2989e9ad5`; adapter `70bcf83c37936593e394c8476134046a7da70f4c`; adapter tests `19cd18b40cb61252094b5805eb9d3cc35a7ff39b`; unchanged S3/V1 validator `b94bac0f82ae141984552409f99a5cff70435b3b`; S1 fixture `41f5b21eaa418bb32f4f40e00de7e920ca39c4bf`; workflow `0e319368fc36d8752f8e1640c3dd513dc18fd0ce`.
- F1–F7 synthetic matrix PASS. F6 exact-bool opt-in guard is GREEN. F7 now installs the append-only authorizer before COMMIT; injected authorizer failure rolls back all schema objects and user_version. RED run `45011014408`; GREEN run `45011049882`.
- Physical schema spec synchronized with owner-approved Amendments A/B; F2 contract/evidence updated.
- Independent review PR #5: [DO NOT MERGE](https://github.com/kenznguyen/btcquant-application/pull/5). Current PR snapshot head at last check `89a83dd`; it is stale because latest source SHA is now `284d9d2`. Refresh schema source/test snapshots, F2 contract/evidence snapshots, REVIEW_SCOPE blob mapping and PR body to this exact source SHA. Request Codex review again after refresh.
- Codex review status is running but previously on a superseded PR head; do not accept until the bot reports the current PR head. Graphify status also refers to an earlier head and is not accepted.
- Remaining design blocker: candidate snapshot digest preimage/serialization remains unspecified. Current validator checks shape/presence and CANDIDATE↔VALIDATED equality only; do not invent formula.
- F2: **PARTIAL / SYNTHETIC CI PASS** pending independent review and candidate digest design decision. S1.2: **NOT FROZEN**. Independent review: **PENDING**. B8: **NOT APPROVED**. Real-data staging: **NOT AUTHORIZED**.
- Evidence: `docs/evidence/T0_S1_2_F2_DTO_READONLY_PROJECTION_CI_2026-11-22.md`.
- Next: refresh review PR #5 to source SHA `284d9d2`, verify all 14 blob pairs, request Codex review on current head, then triage findings and rerun exact-SHA CI for any fix.
- Exclusions unchanged: no real archive/sidecar access/acquisition, host/workstation/SSH/filesystem/runner preflight, B8 workflow/dispatch/runner, real-data staging, uploads/retention/deletion/cleanup, Canonical T0, MAY-10/REST tail/T1/T2 runtime/VPS/deployment/credentials/exchange/trading.

---

# CURRENT STATUS OVERRIDE — 2026-11-22 — F1–F7 synthetic matrix GREEN at latest SHA; independent review requested

- Current `main` HEAD before this handoff update: `7d0b346438da5843cadad66b5db98352601b2f97`.
- Latest tested implementation source SHA: `5074bf35f94f94a5b8905548b9628794274bc825`.
- Exact-SHA CI run [45010626565](https://github.com/kenznguyen/btcquant-application/actions/runs/45010626565), job `137171941617`, SUCCESS; requested SHA = checkout SHA.
- Results: importer-core 20/20; S1.2 adapter 43/43; staging schema 31/31; full `market_data` regression 495/495 PASS. CPython 3.13.18 / SQLite 3.45.1 focused; CPython 3.12.16 full regression. Artifact count 0.
- Latest source blobs: schema `01720183179211a10aa90c38ba8474bbfe37b561`; schema tests `d915bf4a45be979fc5a4a4bde21426050243f1c1`; adapter `70bcf83c37936593e394c8476134046a7da70f4c`; adapter tests `19cd18b40cb61252094b5805eb9d3cc35a7ff39b`; unchanged S3/V1 validator `b94bac0f82ae141984552409f99a5cff70435b3b`; S1 fixture `41f5b21eaa418bb32f4f40e00de7e920ca39c4bf`; workflow `0e319368fc36d8752f8e1640c3dd513dc18fd0ce`.
- F1–F7 synthetic matrix PASS. F6 now requires exact Python bool opt-in for file-backed disposable DB; truthy non-bool values are rejected before file creation. RED run `45010592494`; GREEN run `45010626565`.
- Physical schema spec synchronized with owner-approved Amendments A/B; F2 contract and evidence docs updated.
- Independent review PR: [#5](https://github.com/kenznguyen/btcquant-application/pull/5), DO NOT MERGE. Current review snapshot head `89a83dd5499d95b95541b1f8b829b345f6a7400e`; tested implementation SHA `5074bf3`. All 14 original↔snapshot source/design/test/workflow blob pairs verified identical in `REVIEW_SCOPE.md`.
- Codex review was requested against the refreshed PR head and is still running/queued; previous status entry was for an earlier PR head and is not accepted. Graphify status still reports an earlier review head; do not accept it as current-snapshot review.
- Remaining design blocker: candidate snapshot digest preimage/serialization remains unspecified. Current validator checks shape/presence and CANDIDATE↔VALIDATED equality only; do not invent formula.
- F2: **PARTIAL / SYNTHETIC CI PASS** pending independent review and candidate digest design decision. S1.2: **NOT FROZEN**. Independent review: **PENDING**. B8: **NOT APPROVED**. Real-data staging: **NOT AUTHORIZED**.
- Evidence: `docs/evidence/T0_S1_2_F2_DTO_READONLY_PROJECTION_CI_2026-11-22.md`.
- Next: wait for Codex/Graphify review of current PR head; triage findings, implement only approved synthetic-scope fixes, rerun exact-SHA CI and request follow-up review.
- Exclusions unchanged: no real archive/sidecar access/acquisition, host/workstation/SSH/filesystem/runner preflight, B8 workflow/dispatch/runner, real-data staging, uploads/retention/deletion/cleanup, Canonical T0, MAY-10/REST tail/T1/T2 runtime/VPS/deployment/credentials/exchange/trading.

---

# CURRENT STATUS OVERRIDE — 2026-11-22 — F1–F7 synthetic matrix GREEN at latest SHA; independent review snapshot being refreshed

- Current `main` HEAD: `4d219b07a8f8d4c0969ac0b60ffe7eeb42077268` (latest evidence/handoff documentation commits).
- Latest tested implementation source SHA: `5074bf35f94f94a5b8905548b9628794274bc825`.
- Exact-SHA CI run [45010626565](https://github.com/kenznguyen/btcquant-application/actions/runs/45010626565), job `137171941617`, SUCCESS; requested SHA = checkout SHA = `5074bf3`.
- Results: importer-core 20/20; S1.2 adapter 43/43; staging schema 31/31; full `market_data` regression 495/495 PASS. CPython 3.13.18 / SQLite 3.45.1 focused; CPython 3.12.16 full regression. Artifact count 0.
- Latest source blobs:
  - schema `01720183179211a10aa90c38ba8474bbfe37b561`
  - schema tests `d915bf4a45be979fc5a4a4bde21426050243f1c1`
  - adapter `70bcf83c37936593e394c8476134046a7da70f4c`
  - adapter tests `19cd18b40cb61252094b5805eb9d3cc35a7ff39b`
  - unchanged S3/V1 validator `b94bac0f82ae141984552409f99a5cff70435b3b`
  - S1 fixture `41f5b21eaa418bb32f4f40e00de7e920ca39c4bf`
  - workflow `0e319368fc36d8752f8e1640c3dd513dc18fd0ce`.
- F1–F7 synthetic matrix PASS. F6 additionally requires exact bool opt-in for disposable path; RED at `1a5ff9b`, GREEN at `5074bf3`.
- Physical schema specification synced to owner-approved Amendments A/B; F2 implementation contract and evidence updated.
- Remaining design blocker: candidate snapshot digest preimage/serialization remains unspecified. Current validator checks shape/presence and CANDIDATE↔VALIDATED equality only; do not invent formula.
- Review-only PR #5: [Independent review snapshot](https://github.com/kenznguyen/btcquant-application/pull/5). Its first snapshot pins `d91c92a` and is now stale due the exact-bool F6 hardening. Update the two changed source/test snapshot files and mapping to `5074bf3`, then require Graphify/Codex review of the updated PR head. Do not merge.
- F2: **PARTIAL / SYNTHETIC CI PASS** pending candidate digest design decision and independent review. S1.2: **NOT FROZEN**. Independent review: **RUNNING/QUEUED ON STALE SNAPSHOT; NOT ACCEPTED**. B8: **NOT APPROVED**. Real-data staging: **NOT AUTHORIZED**.
- Evidence: `docs/evidence/T0_S1_2_F2_DTO_READONLY_PROJECTION_CI_2026-11-22.md`.
- Next: refresh PR #5 snapshot to source SHA `5074bf3`, verify exact blob mapping, wait for Graphify/Codex results, address findings, rerun exact-SHA CI and follow-up review.
- Exclusions unchanged: no real archive/sidecar access or acquisition, host/workstation/SSH/filesystem/runner preflight, B8 workflow/dispatch/runner, real-data staging, uploads/retention/deletion/cleanup, Canonical T0, MAY-10/REST tail/T1/T2 runtime/VPS/deployment/credentials/exchange/trading.

---

# CURRENT STATUS OVERRIDE — 2026-11-22 — S1.2 F1–F7 synthetic matrix GREEN; independent review is next

- Current `main` HEAD: `9a8c15b37322d9f2b29c5ed0ad6173824830b1f9` (evidence/handoff documentation commits after tested code).
- Latest tested implementation source SHA: `d91c92a813ffe44c4ee786861e5e710654423c26`. All seven code/workflow blobs below were re-fetched at this SHA and at current main; each blob SHA is identical.
- Exact-SHA CI run [45010072833](https://github.com/kenznguyen/btcquant-application/actions/runs/45010072833), job `137170245583`, SUCCESS; requested SHA = checkout SHA = `d91c92a`.
- Runtime CPython 3.13.18 / SQLite 3.45.1 for focused suites; CPython 3.12.16 for full regression.
- Results: importer-core 20/20 PASS; S1.2 adapter 43/43 PASS; staging schema 30/30 PASS; full `market_data` regression 494/494 PASS. Artifact count 0.
- Verified source blobs:
  - schema `80393e2be87eafd0a2418dfbe48b91391712b8a2`
  - schema tests `46eaf32514c5622b6f9fa7dacbdf4f1bc1a0a356`
  - adapter `70bcf83c37936593e394c8476134046a7da70f4c`
  - adapter tests `19cd18b40cb61252094b5805eb9d3cc35a7ff39b`
  - unchanged S3/V1 validator `b94bac0f82ae141984552409f99a5cff70435b3b`
  - synthetic S1 test fixture `41f5b21eaa418bb32f4f40e00de7e920ca39c4bf`
  - CI workflow `0e319368fc36d8752f8e1640c3dd513dc18fd0ce`.
- F1–F7 synthetic test status: PASS at tested source SHA. F1 physical spec has been synchronized with owner-approved Amendments A/B; exact two append-only triggers included in schema fingerprint. F6 uses explicit disposable temp-path policy only; F7 schema init is atomic with rollback tests.
- Physical spec synchronization commit: `f09136c563b026aa718629f6c774505f1b8362f3`. F2 implementation contract status commit: `645d576be79533f187131207415e9b6b75b6cca7`. Evidence commit: `9a8c15b37322d9f2b29c5ed0ad6173824830b1f9`.
- Remaining design blocker: exact candidate snapshot digest preimage/serialization is undefined. Do not invent it or implement recomputation. Current graph validator validates presence/shape and CANDIDATE↔VALIDATED equality only.
- F2: **PARTIAL / SYNTHETIC CI PASS** pending candidate digest design decision and independent review. S1.2: **NOT FROZEN**. Independent review: **NOT RUN**. B8: **NOT APPROVED**. Real-data staging: **NOT AUTHORIZED**.
- Evidence: `docs/evidence/T0_S1_2_F2_DTO_READONLY_PROJECTION_CI_2026-11-22.md`.
- Next: create a byte-for-byte review-only source snapshot from current main and request Graphify/Codex independent review. Do not merge the review-only PR. Address only review findings within current approved synthetic scope, rerun exact-SHA CI, and obtain separate owner approval for the candidate digest contract.
- Exclusions remain unchanged: no real archive/sidecar access or acquisition; no host/workstation/SSH/filesystem/runner preflight; no B8 workflow/dispatch/runner; no real-data staging, upload, retention/deletion/cleanup; no Canonical T0 operation; no MAY-10/REST tail/T1/T2 runtime/VPS/deployment/credentials/exchange/trading.

---

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



## Independent review preliminary checkpoint — 2026-11-22

- Graphify automated review completed on superseded PR head `eb5121521d2abe3c37c2b01eac08c3e1c13b7147`, not the latest source snapshot. Gate: PASS, 0 blocking, 1 advisory, 4 graph findings; investigation `complete=false`, with 2 bug candidates, 1 cleanup candidate, 6 possible issues and 5 unconfirmed. This is preliminary only and is NOT accepted as final independent review.
- Graphify reported:
  1. possible TypeError on malformed candle `open_time_ms` in unchanged public S3/V1 validator around line 755; strict DTO/SQLite projection rejects non-int values, so this path is outside current S1.2 adapter input. Keep validator unchanged under current contract; record for separate owner decision.
  2. `unittest.main()` appears before later test classes in `test_archive_staging_adapter.py`, so direct script execution skips those later classes. CI's module-based unittest invocation still discovers them. Test-file quality issue to correct after current Codex review.
  3. synthetic inventory bytes use literal backslash-x00 text rather than an actual NUL byte; test fixture should be corrected and explicitly assert NUL preservation.
  4. unchanged S3/V1 validator accepts list-style natural keys in identity parsing but later compares list to tuple; adapter-generated payload uses tuple, so not exercised by this adapter. This is a pre-existing public-validator issue and outside current approved no-change boundary.
- Graphify also noted high/medium fan-out in test fixture, S1 validator and graph validator; advisory maintainability observations, not a correctness gate.
- Codex review was manually requested on the current review PR head `72be6af7a87c9c6fe0d76bcc6e486a699b39dfbb`; latest status is RUNNING. Do not accept older Codex/Graphify review heads.
- Review PR #5 remains DO NOT MERGE. After Codex completes, triage findings, fix only approved test/scope issues, rerun exact-SHA CI, refresh review snapshot and request follow-up independent review.

