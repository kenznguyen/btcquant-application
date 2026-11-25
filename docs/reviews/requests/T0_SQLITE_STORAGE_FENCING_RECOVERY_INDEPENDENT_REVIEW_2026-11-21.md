# Independent Review Request — T0 SQLite Storage, Write Gateway, Lease/Fencing and Recovery

**Review classification:** independent second-person, adversarial source review  
**Review target repository:** `kenznguyen/btcquant-application`  
**Immutable source snapshot:** `b79c7e5d0bc7cf5e6beee0d4e05505a1b1aa6556` (branch `main` at request creation)  
**Review target paths:** source/test/workflow blobs listed below.  
**PR purpose:** review request and scope only. No implementation change is proposed.

## Reviewer instructions

Review the immutable source snapshot above, not merely this PR's documentation-only diff. Verify every blob SHA against the target commit before review. Do not rely on prior assistant self-reviews as independent evidence. Return a signed-off GitHub review with one verdict: **APPROVE**, **REQUEST CHANGES**, or **NOT VERIFIED**.

For every finding include severity (Critical/Required/Optional), exact path and line, concrete trigger/reproduction, impact, and bounded remediation. Distinguish proven behavior from assumptions and missing evidence. Do not execute against canonical data or production runtime.

## Scope A — SQLite storage, schema and migrations

- `market_data/storage.py` — `ae03c5a1caf68bb292ca2903e187a2a3a2474938`
- `market_data/store.py` — `4e1b0c54bd56455abe5be0e5c7d0807e63e0bc78`
- `market_data/initialize_sqlite.py` — `58bd2deba66cc667bad8d6446c5ff54e7f5dd240`
- `market_data/migrations.py` — `b4574f2a867b0dae7818cd39249cfd95fe0ce1f0`
- `market_data/postgres.py` — `2fe27fe2d066dda0c192a381b72d27404487b800`
- `market_data/test_storage.py` — `b2635f575323187f936360d033b4fc630d8138e0`
- `market_data/test_store.py` — `df1554a365ff5d619498dc4b07f7a1a435e761df`
- `market_data/test_initialize_sqlite.py` — `9823f42fa1b346c7c5b96786eec7e996484b692d`

Verify:
1. SQLite is the default backend; Postgres selection requires explicit configuration and cannot be selected silently.
2. Read paths are truly read-only; no implicit schema creation, migration, journal mutation, or database creation on API startup/read.
3. Initializer is explicit, empty-only and safe against existing/non-empty DB, symlink/path mistakes and concurrent initialization.
4. Transaction boundaries, busy/timeout behavior, WAL/checkpoint assumptions, connection lifecycle and thread/process concurrency.
5. Schema constraints, primary/unique keys, interval/time alignment, idempotent inserts, conflict handling and integrity invariants.
6. Migration ordering, atomicity, rollback, interrupted migration recovery and compatibility with existing data.
7. Postgres adapter is not silently used or allowed to weaken SQLite invariants; clearly classify unqualified behavior.
8. No data loss, destructive cleanup, automatic retention/deletion or unsafe restore path.

## Scope B — Write Gateway and fenced writes

- `market_data/write_gateway.py` — `0a77df443ae1a817ea74946fac5dc0f3809ddd83`
- `market_data/test_write_gateway.py` — `7b7f5072b461daedeb2ac0d55bc49305e69f8c97`
- `market_data/test_fenced_store.py` — `0573d0728f3e62a95b8d2a4f16359e33dd4789b4`

Verify:
1. All canonical writes flow through the gateway and require a valid current lease/fencing token.
2. Lease ownership, generation/fencing monotonicity and compare-and-swap semantics are atomic with the write transaction.
3. Stale owner, expired lease, owner replacement, concurrent writers, crash between validation and commit, and clock anomalies fail closed.
4. No bypass write path exists in store, sync, recovery, initializer, tests or helper code.
5. Idempotency, duplicate candle behavior, partial batch failure and rollback semantics preserve canonical invariants.
6. Write gateway does not claim protection against failure modes it does not actually fence (e.g. external process or DB copy/restore epoch).

## Scope C — Lease, feeder lifecycle, scheduler and recovery

- `market_data/feeder.py` — `299a9b5a8b1ebd581eb620d5ee860d9f9ff5dc5c`
- `market_data/feeder_service.py` — `6d238a01f35003b943e2b22c8e05f05090ccb518`
- `market_data/sync.py` — `e7ad4e6f2074225957b01f74abb0befe37675ea2`
- `market_data/test_feeder_lease.py` — `9e3cef256ed55c9784d02e21f9ac30cf723c31b0`
- `market_data/test_feeder_recovery.py` — `034c9e8f157b0750aaf856c122b00ef96c808ee8`
- `market_data/test_feeder_service_lifecycle.py` — `590c29a0fbf553d19582912a113a92bb74da083f`
- `market_data/test_sync.py` — `7621c85a4c7eb2ad233de94da89e6fbb411ea534`
- Also inspect current-commit scheduler, retry, health and lifecycle tests: `test_feeder_scheduler.py`, `test_feeder_retry.py`, `test_feeder_health.py`, `test_feeder_lifecycle.py`; verify their exact blob SHAs from the immutable tree.

Verify:
1. Lease TTL/heartbeat/renew/release semantics and fencing generation are race-safe.
2. Lease loss immediately prevents further writes and READY/healthy claims; recovery does not proceed under uncertain ownership.
3. Recovery lookback, cursor/vector progress, gap detection/backfill, duplicate overlap and restart idempotency.
4. Network/API failure, rate limit, malformed payload, empty response, timeout, process termination and clock movement all have bounded retry/backoff and fail-closed behavior.
5. Scheduler shutdown, cancellation, thread/process ownership, heartbeat failure and restart are deterministic.
6. No hidden autostart/systemd/service installation or runtime side effect occurs on import/test.
7. Recovery and health state are not confused with data readiness or complete historical coverage.

## Existing evidence — context only, not independent approval

- FastAPI/current contract workflow [44861746989](https://github.com/kenznguyen/btcquant-application/actions/runs/44861746989) is isolated API evidence, not proof of storage/feeder production behavior.
- SQLite-only aggregate [44740818608](https://github.com/kenznguyen/btcquant-application/actions/runs/44740818608) reports 174/174 PASS on exact historical source SHA `b4e16a153ef7b0306784efa117b3121fc83dacb5`; it is not a current-snapshot run.
- Historical tests do not prove VPS runtime, canonical DB integrity, real exchange ingestion or operational readiness.

## Required reviewer deliverable

1. Confirm exact target commit and all source/test blob SHAs reviewed.
2. Review correctness, concurrency, transaction/fencing safety, recovery determinism, security, failure isolation and test adequacy.
3. Identify any unguarded write route or implicit initialization.
4. Provide Critical/Required/Optional findings with precise reproduction and explicit final verdict.
5. State whether the review was genuinely independent of the implementation author.

## Non-scope / safety boundary

- Source-only review. No canonical SQLite open/read/write, no data inventory, backup, restore, copy, migration or cutover.
- No Feeder/Scheduler/runtime start, VPS/SSH access, systemd/autostart, deployment or public ingress.
- No Binance REST/WebSocket calls, retries or bypass of HTTP 451; no exchange credentials.
- No T1/T2 runtime connection, Postgres/Timescale activation, AI execution or real orders.
- Do not implement fixes in this review PR. Record findings; any remediation belongs in a separate bounded implementation PR with tests and exact-SHA evidence.

## PR acceptance criteria

- A genuine independent reviewer submits an explicit review on this PR.
- Every Critical/Required finding is tracked with reproduction and remediation; no silent waiver.
- Any remediation is performed separately, tested against exact SHA and followed by independent review.
- This PR is a review request only, not permission to merge implementation changes or operate T0 runtime.
