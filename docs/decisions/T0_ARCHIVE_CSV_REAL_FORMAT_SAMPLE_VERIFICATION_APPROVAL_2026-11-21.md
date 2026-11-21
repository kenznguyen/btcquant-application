# Owner decision — representative real Binance archive CSV format verification

Date: 2026-11-21  
Repository: `kenznguyen/btcquant-application`  
Branch: `main`  
Status: **APPROVED — 12-OBJECT SAMPLE SCOPE; EXECUTION BLOCKED PENDING WORKFLOW AUTHORIZATION**

## 1. Owner approval

The owner approves a bounded verification of the real Binance USD-M BTCUSDT archive CSV format using exactly six ZIP objects and their six paired `.CHECKSUM` sidecars (12 objects total), executed on a GitHub-hosted ephemeral runner. The purpose is to establish source-format facts needed before freezing the offline parser contract.

This approval is limited to reading the exact allowlisted public archive objects, validating their bytes/structure and parsing their CSV members for format inspection. It does not approve full 404-object materialization.

## 2. Exact sample selection

Use only the following six ZIP keys from the committed archive provenance inventory and each exact paired sidecar key recorded in that inventory:

| Timeframe | Period | ZIP object key |
|---|---|---|
| 15m | 2019-12-31 | `data/futures/um/daily/klines/BTCUSDT/15m/BTCUSDT-15m-2019-12-31.zip` |
| 15m | 2022-08 | `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2022-08.zip` |
| 15m | 2026-10 | `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2026-10.zip` |
| 1h | 2019-12-31 | `data/futures/um/daily/klines/BTCUSDT/1h/BTCUSDT-1h-2019-12-31.zip` |
| 1h | 2022-08 | `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2022-08.zip` |
| 1h | 2026-10 | `data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2026-10.zip` |

Inventory path: `docs/manifests/T0_BINANCE_UM_BTCUSDT_ARCHIVE_OBJECT_PROVENANCE_INVENTORY_2026-11-20.json`  
Inventory blob SHA at approval: `eb251ac0924b46add906123f99b82e054d887a59`.

The sidecar key for each ZIP must be taken from its `paired_sidecar_key` entry in this exact inventory; do not synthesize additional keys or expand the sample.

## 3. Required verification

For each ZIP/sidecar pair:
- Fetch only the exact approved object keys from the already documented Binance Public Data source; no bucket listing, wildcard, alternate endpoint, proxy, REST Klines, or fallback.
- Record retrieval time, HTTP status/headers where available, actual byte count and SHA-256 for both ZIP and sidecar.
- Compare ZIP byte count and SHA-256 with the inventory; parse the sidecar body and compare its asserted digest with the measured ZIP digest.
- Validate ZIP CRC and archive structure; identify all members and require exactly one CSV member unless the owner is asked to decide on an unexpected structure. Do not silently select a member.
- Inspect raw CSV encoding, BOM, delimiter, newline convention, quoting, header presence/text/order, field count, blank-row behavior, numeric grammar, timestamp grammar, and row count.
- Validate the complete source-column mapping and compare all six samples for format drift.
- Verify actual source close-time convention against open time and timeframe interval; do not assume the synthetic fixture convention.
- Run the current parser only as a diagnostic comparison. A mismatch is evidence to revise tests/parser, not permission to coerce or discard source fields.
- Preserve a concise evidence report and hashes; raw sample files are temporary to the ephemeral runner and must not be uploaded as an artifact unless separately approved.

## 4. Hard boundaries

This decision does NOT authorize:
- Creating or modifying GitHub Actions workflow YAML.
- Running an existing workflow unless its exact path and behavior are independently verified as already authorized for this task.
- Downloading any object beyond the six ZIPs and six paired sidecars.
- Full 404-object archive materialization.
- Contract 1.2.0 schema/API implementation or parser contract freeze.
- Importer creation, SQLite creation/open/write, normalization into a database, or staging.
- Canonical T0 access or mutation, personal host/VPS, Dropbox, T1/T2, runtime, deployment, exchange credentials, REST tail, or trading.
- Raw archive artifact upload, automatic deletion/cleanup policy, or retention changes.

The GitHub-hosted runner is ephemeral and is the only approved execution environment for this sample verification. No other host or destination may be substituted.

## 5. Execution gate and next step

Although the 12-object source-verification scope and GitHub-hosted ephemeral execution environment are approved, no suitable already-authorized workflow has been established in this decision record. Creating the workflow YAML is explicitly outside this approval.

Therefore execution status is **BLOCKED — WORKFLOW IMPLEMENTATION NOT AUTHORIZED**. The next step is to obtain a separate owner decision approving one narrowly scoped, manually dispatched workflow that performs only this exact 12-object verification, with read-only repository permissions, pinned actions, bounded transfer/retry limits, no secrets, no artifacts containing raw data, and no database/runtime access.

After the verification evidence is reviewed, a further owner decision is required before freezing the parser contract or implementing an importer.
