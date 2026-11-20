# T0 Canonical SQLite Reconstruction — Bounded Execution Plan

Date: 2026-11-20  
Status: **PLAN DRAFTED — EXECUTION BLOCKED / NOT AUTHORIZED**

## 1. Purpose

Define a controlled path for reconstructing a new, isolated SQLite dataset from the previously validated Binance USD-M BTCUSDT M15/H1 archive. This is reconstruction of historical market data, not recovery of the former Canonical SQLite database.

The controlling owner decision is `docs/decisions/T0_CANONICAL_DATA_PRESERVE_AND_RECONSTRUCT_DECISION_2026-11-20.md`. It approves design/procedure only. It does not authorize archive transfer, database creation, import, validation writes, backup, restore, promotion, or runtime activation.

## 2. Preserved invariants

- T0 remains an independent data asset; do not place market-data payloads or SQLite files in the application Git repository.
- Preserve all validated source ZIPs and paired checksum sidecars unchanged and immutable.
- Never overwrite, move, mutate, or claim recovery of the former Canonical SQLite.
- The MAY-10 trial database is separate and may contain only newly closed candles; never import archive history into it.
- Any new database is labeled `RECONSTRUCTED`; it is not Canonical by default.
- No auto-delete, TTL cleanup, vacuum-based retention policy, or source archive cleanup.
- No T1/T2, PostgreSQL/Timescale, Dropbox snapshot, restore drill, primary cutover, trading, or real orders.

## 3. Known source evidence

Source inventory: `docs/manifests/T0_BINANCE_UM_BTCUSDT_ARCHIVE_OBJECT_PROVENANCE_INVENTORY_2026-11-20.json`.

- Exactly 404 source identities: 202 ZIP objects and 202 paired `.CHECKSUM` sidecars.
- ZIP checksums, CRC, single-CSV structure and 12-column validation previously passed for all 202 ZIPs.
- M15: 241,440 rows, observed opens from 2019-12-31 00:00 UTC through 2026-11-18 23:45 UTC.
- H1: 60,360 rows, observed opens from 2019-12-31 00:00 UTC through 2026-11-18 23:00 UTC.
- Internal continuity was reported PASS within those observed bounds. This does not establish earliest-ever history or data after 2026-11-18.
- REST tail remains NOT VERIFIED; HTTP 451 restriction is closed. Do not retry or bypass it.
- The inventory is identity-complete but sidecar own historical byte size/hash is NOT VERIFIED. Fresh materialization, if later approved, must calculate each sidecar's own size and SHA-256.
- Historical aggregate discrepancy of 11,277 bytes remains unexplained. Preserve both historical values; do not infer or silently reconcile them.
- These are historical validation results, not proof that source files currently exist at an accessible location.

## 4. Required owner decisions before execution

Every item below is a hard gate. Until all are explicitly resolved and recorded, status remains BLOCKED.

1. **Exact destination and host:** provide/approve a currently existing owner-controlled host and exact absolute staging path. The former proposed path `/srv/btcquant/staging/t0-reconstructed-btcusdt-20261120-run-001` is not assumed reusable: the former Scaleway VPS was deleted, and the latest Preserve & Reconstruct approval did not authorize transfer or staging. No fallback path may be selected by the operator.
2. **Source object availability:** identify the exact immutable source location and verify that all 404 objects are available there without changing them. Do not initiate network retrieval or copy before approval.
3. **Coverage acceptance:** explicitly accept the observed partial boundaries per timeframe above, and confirm whether the known internal no-gap result is sufficient or whether a fresh full object-level continuity reconciliation is required before import. No extension beyond the observed bounds is implied.
4. **Importer identity:** select the implementation and pin its exact source commit SHA, dependency lock/hash set and invocation. The importer SHA is currently UNKNOWN; no importer is approved.
5. **Schema contract:** confirm the exact Candle Contract version, SQLite schema, `user_version`, mapping of the Binance 12 source columns, and deterministic semantics for `available_at_ms`. No schema extension is implied.
6. **Validation and quarantine policy:** approve the machine-readable manifest format, exact expected row counts, duplicate/conflict rules, timestamp grid, OHLC/numeric checks, SQLite integrity checks, quarantine behavior and immutable retention.
7. **Execution approval:** after the above are resolved, issue a separate explicit approval naming the exact destination, 404-object inventory revision, importer SHA, coverage/gap policy and validation gates. Approval of this plan alone is not execution authorization.

## 5. Proposed gated sequence (not executed)

### Gate A — read-only preflight
- Inspect only the exact approved host/path.
- Verify mount/filesystem identity, ownership/permissions, free bytes/inodes, every path component with no-follow semantics, and that the path is empty and isolated from Dropbox sync roots and operational data paths.
- Record timestamped evidence and PASS/FAIL for every check.
- Any failed or unverifiable check means STOP. No alternate path.

### Gate B — source preservation/materialization
- Only after a separate approval, process exactly the 404 allowlisted objects.
- Enforce the owner-approved transfer cap and bounded retries, count response bytes across all attempts, use create-only/no-follow writes, and preserve original bytes.
- Independently hash every ZIP and sidecar; parse each sidecar strictly and verify its asserted ZIP digest against the paired ZIP.
- Quarantine the entire run on any missing/extra object, checksum/size mismatch, malformed payload, cap breach or unsafe path.

### Gate C — normalization and reconciliation
- Parse the pinned 12-column Binance USD-M kline schema with exact decimal arithmetic.
- Validate UTC millisecond timestamps, interval alignment, close-time relation, finite numeric values, OHLCV constraints and source-only fields.
- Reconcile expected M15/H1 timestamp grids, duplicates and conflicts. Do not synthesize, interpolate, forward-fill or silently drop rows.
- Generate a complete per-object inventory, dataset manifest and machine-readable gap report.

### Gate D — new SQLite build
- Requires a separate explicit approval for the exact new empty DB path and importer SHA.
- Use the reviewed empty-only initializer; refuse existing paths and symlinks.
- Import deterministically in timeframe/open-time order with bounded transactions and uniqueness enforcement.
- Do not start feeder, writer, lease, scheduler or API runtime.

### Gate E — independent read-only verification
- Close all writers/connections before validation.
- Require `PRAGMA integrity_check = ok`; verify exact schema and `user_version`.
- Independently verify M15/H1 counts and bounds, source-to-DB equivalence, timestamp ordering/alignment, duplicate/conflict policy, OHLC/numeric constraints, gaps and `available_at_ms` semantics.
- Any discrepancy => QUARANTINED; no promotion.

### Gate F — owner review
- Submit exact source inventory revision, importer SHA, schema identity, dataset/database hashes, row counts, boundaries, gap report, validation logs and quarantine status.
- A passing result may be called **STAGED / VALIDATED — RECONSTRUCTED — PARTIAL COVERAGE** only.
- Canonical designation, Dropbox snapshot, restore drill, operational primary, runtime and cutover each require separate approval.

## 6. Current status matrix

| Item | Status |
|---|---|
| Preserve & Reconstruct design | APPROVED |
| Historical archive payload validation | PASS for previously validated 202 ZIP + 202 sidecars |
| Full historical completeness / REST tail | NOT VERIFIED |
| Current immutable source location/access | NOT VERIFIED |
| Current staging host and exact destination | BLOCKED — OWNER INPUT REQUIRED |
| Coverage/gap acceptance for reconstruction | BLOCKED — OWNER CONFIRMATION REQUIRED |
| Importer source SHA and dependency identity | NOT SELECTED |
| SQLite schema/import contract confirmation | NOT VERIFIED for this execution |
| Archive transfer/materialization | NOT AUTHORIZED |
| Normalization/import | NOT AUTHORIZED |
| New reconstruction SQLite | NOT CREATED; NOT AUTHORIZED |
| Independent DB validation | NOT AUTHORIZED |
| Canonical promotion / cutover | NOT AUTHORIZED |

## 7. Explicit non-actions

No archive objects were accessed, downloaded, copied or changed. No destination was probed or created. No SQLite file was created, opened or modified. No importer was implemented or run. No Dropbox, VPS, WSL, feeder, API, T1/T2, PostgreSQL, runtime, deployment, backup, restore, promotion or trading operation occurred.

## 8. Work record

- Repository: `kenznguyen/btcquant-application`
- Branch: `main`
- Change type: planning documentation only.
- Tests/workflows: not run; no code behavior changed.
- Workflow run, job, artifact: none.
- Status: **PLAN DRAFTED / EXECUTION BLOCKED / NOT AUTHORIZED**.
- Next: resolve the seven owner gates in Section 4, then submit the fully pinned execution request for separate approval.
