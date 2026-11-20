# T0 Complete-Coverage Reconstruction Plan — 2026-11-20

Date: 2026-11-20  
Status: **PLAN ONLY — EXECUTION BLOCKED / NOT AUTHORIZED**  
Owner selections: environment = `other` (host not selected); coverage = `complete`.

## 1. Objective and asset identity

Prepare a new, independently verifiable T0 SQLite dataset for Binance USD-M BTCUSDT M15 and H1. This is a new asset labeled `RECONSTRUCTED`; it is not recovery of the former Canonical SQLite, which the owner confirmed is lost.

T0 remains independent of the application repository. Market-data payloads and SQLite files must not be committed to Git.

## 2. Meaning of COMPLETE

The currently inventoried archive is not sufficient to claim complete coverage. Its historical evidence is limited to:

- 202 ZIP objects and 202 paired checksum sidecars;
- M15: 241,440 rows, observed opens 2019-12-31 00:00 UTC through 2026-11-18 23:45 UTC;
- H1: 60,360 rows, observed opens 2019-12-31 00:00 UTC through 2026-11-18 23:00 UTC;
- full earliest-ever history and data after 2026-11-18 remain NOT VERIFIED;
- the historical 11,277-byte aggregate discrepancy remains unexplained.

For this plan, COMPLETE means:

1. Establish a documented start boundary from authoritative evidence of the first valid/tradable BTCUSDT USD-M perpetual candle; do not infer it from the current archive's first date.
2. Establish an explicit UTC cutoff timestamp for the reconstruction.
3. Cover every expected M15 and H1 candle open-time grid point between the accepted start and cutoff, independently per timeframe.
4. Have zero unexplained missing intervals, duplicate conflicts, malformed records, or untraceable rows. Any legitimate exchange outage/non-trading interval must be supported by authoritative evidence and explicitly approved as an exception; do not silently waive gaps.
5. Reconcile the full interval across source objects and produce a machine-readable gap/exception report.
6. Verify M15/H1 consistency where aggregation semantics permit it. Do not assume fields with different source semantics are directly interchangeable.

If any boundary or interval cannot be evidenced, status remains **INCOMPLETE / BLOCKED**. Do not relabel partial archive coverage as complete.

## 3. Source strategy and restrictions

### 3.1 Existing evidence

Preserve the 404 inventoried archive identities (202 ZIP + 202 sidecars) as immutable evidence. Historical validation is prior evidence only; it does not prove current source availability or complete historical coverage.

The historical REST HTTP 451 restriction is closed. Do not retry, bypass, proxy around, or otherwise evade it.

### 3.2 Source discovery requirements (planning gate)

Before selecting an acquisition method, prepare a read-only source matrix containing:

- exact provider, official documentation and instrument identity;
- exact object/API endpoint pattern and date coverage;
- whether the source is official exchange data or a third-party corroborating source;
- licensing/terms and access constraints;
- integrity mechanism (published checksum/signature or independently computed hash);
- rate limits, pagination and retention limits;
- known missing periods and whether the source can cover the complete target interval.

Preferred order: official Binance USD-M public archive objects that are already lawfully accessible; other official Binance-published historical datasets; then independently reputable sources only as separately identified corroboration or gap candidates. A third-party source must never be silently merged into Binance-origin rows. Every row/object must retain source provenance and source-precedence decisions.

No network access, listing, download, copy, or source preflight is authorized by this plan.

## 4. Environment selection — unresolved

The owner selected `other`, not a specific host. Before any host provisioning or preflight, the owner must identify and approve:

- exact host/provider and account/ownership boundary;
- operating system and supported Python/runtime version;
- region and storage type;
- exact absolute staging root and final staging DB path;
- encryption-at-rest and access-control approach;
- filesystem capacity for raw source objects, temporary extraction, SQLite, manifests, logs and safety headroom;
- backup/retention location that is independent of the staging volume;
- confirmation that the paths are not Dropbox-synced, application-repository paths, operational T0 paths, or the separate MAY-10 trial database.

No host, VPS, WSL environment, storage volume, directory or account is to be provisioned or probed until separately approved. The former Scaleway VPS was deleted; its paths and state must not be assumed to exist.

## 5. Implementation and contract gates

Before import approval, pin and review:

1. Exact importer repository, commit SHA, source-tree identity and invocation.
2. Exact dependency lockfile and hashes; reproducible runtime version.
3. Binance USD-M kline source schema and strict parser, including exact 12-column mapping and header policy.
4. Target Candle Contract version, SQLite schema and `user_version`.
5. Deterministic semantics for `available_at_ms`, timezone and timestamp precision.
6. Decimal representation and OHLCV/quote-volume/trade-count/taker-volume constraints.
7. Stable primary/unique keys and deterministic duplicate/conflict policy.
8. Machine-readable source manifest, dataset manifest, per-object evidence, gap report and exception ledger.
9. Quarantine behavior: any unexplained mismatch quarantines the complete build; no silent row dropping, interpolation, forward-fill or synthetic candles.

Importer SHA is currently **UNKNOWN**. No importer is approved or authorized to run.

## 6. Gated execution sequence (not authorized)

### Gate 0 — owner decisions

Resolve the exact completeness start/cutoff definition, source matrix and source precedence, exception policy, exact host/path, Candle Contract mapping, importer SHA, validation thresholds, retention and rollback. Record all choices in GitHub.

### Gate 1 — read-only environment/source preflight

Only after a separate explicit approval: verify exact host identity, path ownership/permissions, mount identity, free bytes/inodes, isolation, no symlink/path traversal, and source-object availability. Do not select alternate paths automatically. Any failed or unverifiable check means STOP.

### Gate 2 — immutable source acquisition

Only after a separate explicit acquisition approval: process an exact allowlist; use bounded requests/retries and streaming byte accounting; create-only/no-follow writes; independently calculate size and SHA-256 for every object and sidecar; verify published checksums; preserve originals. Record provider and acquisition timestamps. Any extra/missing/mismatched object quarantines the run.

### Gate 3 — full coverage normalization and reconciliation

Parse with the pinned importer; normalize timestamps and exact decimals; reconcile all expected M15/H1 grid points from accepted start through cutoff; classify every gap; reconcile duplicate/conflict rows; verify source provenance for every row; produce M15/H1 manifests and exception reports. No synthetic data.

### Gate 4 — isolated SQLite build

Requires a separate explicit approval naming the exact empty database path and importer SHA. Use an empty-only initializer that refuses existing files and symlinks. Import deterministically with bounded transactions and uniqueness enforcement. Do not start feeder, writer, lease, scheduler, API, T1/T2, or trading runtime.

### Gate 5 — independent read-only validation

With writers closed, independently verify SQLite integrity, schema and `user_version`; exact row counts against the reconciled manifests; start/end boundaries; timestamp order/alignment; zero unexplained gaps; duplicate/conflict rules; decimal/OHLCV constraints; source-to-database equivalence; `available_at_ms` semantics; DB and manifest hashes. Any mismatch => QUARANTINED, not accepted.

### Gate 6 — owner review and later promotion decision

Submit source inventory revision, source provenance, importer SHA, dependency hashes, schema identity, complete M15/H1 coverage report, exceptions, row counts, database hash, validation logs and quarantine state. A successful build may be called **STAGED / VALIDATED — RECONSTRUCTED — COMPLETE TO THE APPROVED CUTOFF** only. Canonical designation, backup/restore drill, Dropbox snapshot, primary cutover and runtime each require separate explicit approval.

## 7. Mandatory safety invariants

- Former Canonical = LOST; never claim recovery.
- Existing Binance archive evidence remains immutable; no cleanup/deletion.
- No automatic TTL deletion, vacuum-retention policy or source cleanup.
- MAY-10 trial DB remains separate and contains only newly closed candles; no archive import.
- No T1/T2 connection, PostgreSQL/Timescale activation, runtime, public ingress, systemd/autostart, deployment, trading or real orders.
- No promotion to Canonical by implication.
- No data operations until a separate approval identifies the exact source allowlist, host/path, importer SHA, coverage policy and validation gates.

## 8. Current status

| Item | Status |
|---|---|
| Old Canonical | LOST |
| Existing archive evidence | PRESERVE — IMMUTABLE; historical validation only |
| Complete historical start boundary | NOT VERIFIED |
| Complete cutoff boundary | NOT SELECTED |
| Full M15/H1 coverage | NOT VERIFIED |
| Gap/exception policy | NOT APPROVED |
| Current source availability | NOT VERIFIED |
| Source precedence / supplementation | NOT SELECTED |
| Host/provider and OS | OWNER INPUT REQUIRED |
| Exact staging destination | NOT SELECTED |
| Importer SHA / dependency lock | UNKNOWN / NOT SELECTED |
| Candle Contract/schema mapping | NOT VERIFIED FOR THIS BUILD |
| New SQLite | NOT CREATED |
| Archive acquisition / import | NOT AUTHORIZED |
| Validation / promotion | NOT AUTHORIZED |

## 9. Work record

- Repository: `kenznguyen/btcquant-application`
- Branch: `main`
- Change type: planning documentation only.
- Tests/workflows: not run; no code behavior changed.
- Workflow run, job, artifact: none.
- Data/source/host operations: none.
- Status: **PLAN RECORDED — EXECUTION BLOCKED / NOT AUTHORIZED**.
- Next: owner to identify the intended host/provider and OS, then resolve the completeness boundary and acceptable authoritative source strategy. After all gates are pinned, request separate approval for each operational phase.


---

# CURRENT EVIDENCE ADDENDUM — 2026-11-20 — Bounded REST tail

The previously recorded REST-tail NOT VERIFIED status is superseded only for the specific personal-host payload and fixed cutoff recorded in `docs/manifests/T0_BINANCE_UM_BTCUSDT_REST_TAIL_SOURCE_EVIDENCE_2026-11-20.json`. The tail passes offline validation and joins the archive boundary for M15/H1. This does not satisfy the COMPLETE definition in Section 2: earliest-ever start remains unverified, the post-cutoff tail remains unverified, the 11,277-byte historical archive discrepancy remains unresolved, and no complete-source acquisition/reconciliation has occurred. The plan remains PLAN ONLY — EXECUTION BLOCKED / NOT AUTHORIZED. No additional REST retrieval, source discovery, host preflight, archive materialization, SQLite creation/import or runtime operation is authorized.
