# T0 S1.2 — F2 approval and implementation checkpoint

Date: 2026-11-22  
Repository: kenznguyen/btcquant-application  
Branch: main

## Decision and scope

Owner approved proceeding with F2 after F1 design reconciliation. The authorized work is limited to:
- complete immutable DTOs for the eleven physical evidence relations;
- read-only SQLite row projection from a caller-supplied connection;
- deterministic unchanged S3/V1 payload projection;
- pure in-memory graph validation;
- synthetic-only TDD using in-memory/disposable SQLite fixtures.

The detailed contract is recorded in:
- docs/design/T0_S1_2_F2_ADAPTER_GRAPH_IMPLEMENTATION_CONTRACT_2026-11-22.md
- commit: 49759a9198ca39afa8d28d16dcace8c844269992

## Baseline inspected

- Existing adapter source blob: 9d61bb36cfb2ff80c0a1b303e52f34d8d44d2b28.
- Existing adapter test blob: 271e465825ededd3042abc35cd6dc8c451aa07a3.
- Staging schema source blob: 56e7600fcf0d200098cfd4b875359b204956eb79.
- S3/V1 validator source blob: b94bac0f82ae141984552409f99a5cff70435b3b.
- Physical schema design blob: 78ec1b642e9b5b5e4e161f7e4afdbfe3bccf0d3b.
- Amendment A blob: 6f9476f696962c88f27421cdf83fb42a6b4f794f.
- Amendment B commit: 37e54c419ea41064aa9c1d2eb68ec50b3489be52.

## Findings from contract inspection

- Current adapter contains only AttemptRecord, SourceRowRecord and PairRecord plus three projection helpers and attempt-summary derivation.
- Design §3.2 requires eleven DTO families covering run, objects, attempts, successful-attempt relation, pairs, members, source rows, candles, links, failure observations and run events.
- Design §3.3 requires unchanged S3/V1 collections: inventory, objects, pairs, members, attempts, source_rows, candles, links; plus the existing S1 envelope.
- run_events and failure_observations remain physical audit relations and must not be added to the public S3/V1 payload.
- Existing S3/V1 validator remains authoritative and unchanged. The adapter must not fill missing fields or fabricate acquisition/workflow evidence.
- A projection API taking a filesystem path would be unsafe; the F2 contract requires an already-open caller-supplied SQLite connection and no implicit connect/path discovery.

## Status

- F1 design: **RESOLVED** by owner-approved Amendment B.
- F2 contract: **DOCUMENTED** in commit 49759a9198ca39afa8d28d16dcace8c844269992.
- F2 source implementation: **NOT STARTED / NOT IMPLEMENTED**.
- F2 tests: **NOT STARTED**.
- RED/GREEN: **NOT RUN**.
- Exact-SHA CI/full regression: **NOT RUN for F2**.
- Workflow run/job/artifact: **NONE**.
- S1.2: **NOT FROZEN**.
- Independent review: **NOT RUN**.

## Next step

Add synthetic test-first coverage for the canonical DTOs and projection API, then implement the smallest matching adapter changes. Continue with graph invariants and full synthetic regression. Record exact source SHA, workflow run/job, checked-out SHA, test counts and artifact metadata only after they are observed.

## Exclusions unchanged

No B8 workflow changes/dispatch, runner installation/registration, archive/sidecar listing/download/extraction/parsing/sampling/access, host/workstation/SSH/filesystem/disk/encryption/runner preflight, real-data staging build/persistence, uploads, retention/deletion/cleanup, Canonical T0 recovery/create/replace/migration/merge/promotion/cutover, MAY-10, REST tail, T1/T2 runtime, VPS, deployment, credentials, exchange access or trading.
