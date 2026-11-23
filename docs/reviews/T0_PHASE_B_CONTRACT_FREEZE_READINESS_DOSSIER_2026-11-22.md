# T0 Phase B — Contract Freeze Readiness Dossier

- Date: 2026-11-22
- Owner decision: `docs/decisions/T0_PHASE_B_BOUNDED_EXCLUSIONS_AND_IDENTITY_SUPERSESSION_OWNER_DECISION_2026-11-22.md`
- Inventory amendment: `docs/design/T0_SOURCE_DOMAIN_INVENTORY_PHASE_B_IDENTITY_AMENDMENT_V2_2026-11-22.md`
- Revision 9 baseline: commit `5405928cf1ec61cf979453812d158caa8db18d4a`, blob `86c490be08961b02d03ba0a7986befe3e142b9df`.
- Revision 10 design: `docs/design/T0_PHASE_B_DETAILED_SCHEMA_AND_CANONICAL_CONTRACT_DESIGN_REVISION_10_2026-11-22.md`.
- Status: **DOSSIER PREPARED — NOT READY FOR CONTRACT FREEZE APPROVAL**.

## 1. Owner decisions incorporated

- B-13 CLOSED as bounded exclusion: no non-candle read API/dataset-version compatibility in Phase B; separate read contract required.
- B-16 CLOSED as bounded exclusion: ordinary non-RPI depth only; no all-displayed-liquidity claim or RPI inference.
- B-17 OPEN: owner accepts T-only/E-excluded scope conditionally, but exact pinned T1 parser/build proof that CSV `timestamp_ms` maps to native T is mandatory before closure.
- Inventory supersession accepted for Phase B SD-06/SD-07 only. SD-06 uses `(exchange, market_type, symbol, first_update_id, final_update_id)` subject to namespace proof, with stream_epoch as provenance; SD-07 uses pair-only capture identity `(capture_producer_id, capture_sequence)`.

## 2. Current blocker register

| Blocker | Status | Freeze gate |
|---|---|---|
| B-01..B-12 | OPEN | Resolve with source evidence, exact contracts and/or tested proof |
| B-13 | CLOSED — bounded exclusion | Keep read API/dataset-version work outside Phase B |
| B-14..B-15 | OPEN | Numeric bounds and native field fidelity |
| B-16 | CLOSED — bounded exclusion | Non-RPI scope only; explicit limitation retained |
| B-17 | OPEN — conditional scope accepted | Exact pinned T1 parser/build mapping proof |
| B-18..B-20 | OPEN | Snapshot manifest, cursor/watermark atomicity, parser/resource ceilings |

B-13/B-16 closure means only that the scope is deliberately excluded, not that excluded capabilities exist or have been implemented.

## 3. Evidence available

- Revision 9 full design review: PASS WITH CONDITIONS; no new material document-level findings; not independent human review.
- Revision 9 exact source SHA/blob verified: `5405928cf1ec61cf979453812d158caa8db18d4a` / `86c490be08961b02d03ba0a7986befe3e142b9df`.
- T1 `docs/SCHEMA.md` blob pinned: `895f87a8281a3f9b6d37d96b5f68568e4285bee6`; this documents timestamp_ms as trade time but does not prove exact parser implementation behavior.
- Synthetic matrix: 101 proposed cases (14/31/46/10), DESIGN ONLY / NOT EXECUTED.
- GitHub Actions runs/artifacts for exact Revision 9 design SHA: none verified.
- Tests/fixtures/formal proofs: NOT RUN / NOT CREATED.
- Independent second-person reviewer identity/verdict: NOT VERIFIED.

## 4. Mandatory freeze gates

1. Read-only inspect exact pinned T1 parser implementation/build; prove `timestamp_ms → native T`; record repository commit, relevant blob SHA, parser path/line range and build identity. If not proven, B-17 remains OPEN and disputed-clock records fail closed/quarantine.
2. Resolve B-01..B-12, B-14..B-15, B-18..B-20 with exact source/protocol evidence and explicit decisions. Hard gates include:
   - q/nq and aggressor/buyer-maker mappings;
   - SD-06 update-ID namespace uniqueness and Binance overlap/bridge semantics;
   - SD-07 producer-origin authentication, registry, allocator, single-writer fencing, durable sequence non-reuse and restore/rollback protection;
   - raw-object/canonical digest encoding and decimal canonicalization;
   - atomic provenance/identity/outcome/checkpoint persistence and restart/replay;
   - independent source cursor vs book watermark;
   - numeric and byte/resource ceilings; bounded snapshot capture manifest.
3. Freeze exact envelope/DTO, domain schemas, digest preimage, checkpoint and error/quarantine semantics; no implied T2 read API compatibility.
4. Execute the 101-case synthetic matrix only after separate explicit implementation/test authorization; record exact source SHA, workflow run, jobs, artifact IDs and test output. Matrix currently NOT EXECUTED.
5. Obtain independent second-person review against exact owner-approved Revision 10 source commit/blob; record reviewer identity, scope, findings and verdict.
6. Reconcile findings and update handoff/index with exact final evidence. Only then submit a separate Contract Freeze approval request.

## 5. Not authorized

No code, DTO, parser, validator, tests, fixtures, DDL, database, data movement, archive retrieval, T1/T0 runtime, API, T2 integration, VPS, process startup, systemd/autostart, deployment, order submission, live execution or real orders. No delete-on-ack or source cleanup. Raw evidence preservation remains mandatory.

## 6. Freeze decision

**NOT READY FOR CONTRACT FREEZE.** The owner decisions resolve two scope blockers and the Inventory identity authority question, but substantial technical blockers, T1 parser evidence, executed tests and independent review remain outstanding.
