# T0 Phase B — Canonical DTO, Digest, Checkpoint & Atomic Persistence Design v1

- Date: 2026-11-22
- Design baseline reviewed: Revision 10 commit `b32d9af088099f92b09d113ecfa27056cfd9b83d`, blob `a8934cb862c330f1d1fa72aa1f3fdb2b22f9ac96`.
- T1 source audit: `docs/evidence/T1_AGGTRADE_TIMESTAMP_SOURCE_MAPPING_AUDIT_2026-11-22.md`.
- Status: **PROPOSED TECHNICAL CONTRACT — NOT FROZEN; DOCUMENTATION ONLY**.
- This design does not authorize DTO code, validators, DDL, database writes, tests, fixtures, data movement, runtime or deployment.

## 1. Contract boundaries

- T0 owns canonical acceptance, identity adjudication, durable evidence, outcomes, checkpoints and derived book state.
- T1 owns acquisition, native capture provenance and SD-07 capture identity issuance.
- The application repository may own consumer contracts/DTOs/adapters only after separate authorization; it must not duplicate the T1 collector.
- At-least-once delivery is assumed. Exactly-once effects are achieved by durable idempotency and atomic state transitions, not by assuming exactly-once transport.
- Raw source evidence is immutable. No delete-on-ack, destructive normalization or silent overwrite.
- A source-delivery locator, exchange-event identity, SD-07 capture identity, stream epoch, source cursor and book watermark are different concepts and must never be substituted for one another.

## 2. Common DTO envelope (logical schema)

The following is a language-neutral logical contract, not an implementation-ready generated type. All fields are required unless explicitly nullable.

```text
CanonicalSourceEnvelopeV1 {
  contract_version: "T0_CANONICAL_SOURCE_V1"
  domain: "SD05_AGG_TRADE" | "SD06_DEPTH_DIFF" | "SD07_DEPTH_SNAPSHOT"
  exchange: "binance"
  market_type: "USD_M_PERPETUAL"
  symbol: normalized lowercase exchange symbol
  source_kind: explicit allowlisted source-kind enum
  source_schema_version: immutable source schema/parser contract identifier
  source_producer: {
    repository: string
    source_commit: 40-hex SHA
    source_blob_set: map<path, 40-hex blob SHA>
    build_id: string | null
    binary_sha256: 64-hex | null
  }
  source_object: {
    sha256: 64-hex
    media_type: string
    immutable_locator: string
    record_locator: {
      kind: "BYTE_RANGE" | "ROW_INDEX" | "GROUP_ID"
      start: uint64 | null
      end_exclusive: uint64 | null
      row_index: uint64 | null
      group_id: string | null
    }
  }
  clocks: {
    exchange_event_time_ms: int64 | null
    exchange_transaction_time_ms: int64 | null
    exchange_trade_time_ms: int64 | null
    producer_receive_time_ms: int64 | null
    t0_received_at_ms: int64
    t0_committed_at_ms: int64 | null
  }
  provenance: {
    stream_epoch: string | null
    capture_producer_id: string | null
    capture_sequence: uint64 | null
    producer_registration_ref: string | null
    producer_attestation_ref: string | null
  }
  raw_object_sha256: 64-hex
  canonical_payload_sha256: 64-hex
}
```

Rules:
- Unknown clocks remain null with an explicit unavailable reason in the validation/outcome record; never copy one clock into another.
- T1 CSV imports without a verifiable build ID retain `build_id=null` and are not upgraded to verified-build provenance by inference.
- For a legacy CSV source object, `raw_object_sha256` is the SHA-256 of the exact immutable CSV object bytes, not a claimed native WebSocket-message digest.
- A row locator must resolve to exactly one byte range or one stable row/group locator. File path alone is insufficient when a file can still append or rotate.
- `market_type` is explicit USD-M perpetual scope; generic `futures` is not sufficient canonical namespace evidence without a pinned source-registration rule.

## 3. Domain DTOs

### 3.1 SD-05 aggregate trade

```text
AggTradeV1 {
  envelope: CanonicalSourceEnvelopeV1
  identity: {
    exchange: "binance"
    market_type: "USD_M_PERPETUAL"
    symbol: string
    aggregate_trade_id: int64_nonnegative
  }
  event: {
    trade_time_ms: int64_nonnegative | null
    event_time_ms: int64_nonnegative | null
    price: CanonicalDecimalString
    quantity_all_q: CanonicalDecimalString | null
    quantity_non_rpi_nq: CanonicalDecimalString | null
    first_trade_id: int64_nonnegative
    last_trade_id: int64_nonnegative
    is_buyer_maker: boolean
    aggressor_side: "BUY" | "SELL"
  }
}
```

Validation:
- Identity is `(exchange, market_type, symbol, aggregate_trade_id)`; never use timestamp/price as a substitute.
- Require `first_trade_id <= last_trade_id`; reject negative IDs and values outside signed 64-bit source representability.
- `is_buyer_maker=true` maps to `aggressor_side=SELL`; false maps to BUY. If both are supplied, require exact consistency.
- `q` means quantity including RPI-involved trades; `nq` means normal quantity excluding RPI-involved trades. They are distinct. Never derive `nq` from `q`.
- Current inspected T1 source maps native `T → timestamp_ms`, parses `q`, `a/f/l/m`, but does not parse `nq`. Current T1 CSV numeric formatting uses f64 and 12 decimal places; it is not exact native decimal-byte preservation. Preserve the raw CSV object and mark `nq` unavailable.
- Event time E remains unavailable in current CSV. The source-level T mapping is proven; deployed build provenance remains unverified (B-01/B-17).

### 3.2 SD-06 depth diff

```text
DepthDiffV1 {
  envelope: CanonicalSourceEnvelopeV1
  identity: {
    exchange: "binance"
    market_type: "USD_M_PERPETUAL"
    symbol: string
    first_update_id: uint64
    final_update_id: uint64
  }
  sequence: {
    previous_final_update_id: uint64
    stream_epoch: string
    snapshot_anchor_update_id: uint64
  }
  event_time_ms: int64_nonnegative | null
  transaction_time_ms: int64_nonnegative | null
  bid_changes: Array<{ price: CanonicalDecimalString, quantity: CanonicalDecimalString }>
  ask_changes: Array<{ price: CanonicalDecimalString, quantity: CanonicalDecimalString }>
}
```

Validation:
- Require `first_update_id <= final_update_id`; each side is an array of exact price/absolute-quantity pairs; zero quantity deletes a level.
- `stream_epoch` is provenance/continuity state, not identity.
- Ordinary depth is non-RPI only. Do not infer RPI liquidity.
- Current T1 source parses native E and T, U/u/pu and b/a; current CSV conversion persists E as timestamp and drops T. Producer receive time is not currently proven in the CSV.
- The canonical identity remains conditional on verified exchange namespace uniqueness and protocol bridge evidence. An unproven namespace or sequence event is quarantined; do not add stream_epoch to the identity.

### 3.3 SD-07 snapshot capture and manifest

```text
SnapshotCaptureV1 {
  identity: {
    capture_producer_id: string
    capture_sequence: uint64
  }
  immutable_attributes: {
    exchange: "binance"
    market_type: "USD_M_PERPETUAL"
    symbol: string
    source_kind: "BINANCE_USDM_REST_DEPTH_RESPONSE_V1"
              | "T1_RECONSTRUCTED_LOCAL_BOOK_V1"
    source_schema_version: string
    snapshot_kind: "INITIAL" | "PERIODIC" | "BRIDGE"
    captured_at_ms: int64_nonnegative
    snapshot_event_time_ms: int64_nonnegative | null
    snapshot_transaction_time_ms: int64_nonnegative | null
    last_update_id: uint64
    requested_limit: uint32 | null
    actual_bid_levels: uint32
    actual_ask_levels: uint32
    total_level_rows: uint32
    complete: true
    empty_book: boolean
    declared_depth_boundary: uint32 | null
    upstream_snapshot_anchor_ref: string | null
    stream_epoch: string | null
    last_contiguous_diff_update_id: uint64 | null
    continuity_status: "CONTIGUOUS" | "NOT_APPLICABLE"
    source_object_sha256: 64-hex
    canonical_levels_sha256: 64-hex
  }
  levels: Array<{ side: "BID" | "ASK", price: CanonicalDecimalString, quantity: CanonicalDecimalString }>
}
```

Rules:
- Sole capture identity is exactly `(capture_producer_id, capture_sequence)`. All other fields are immutable attributes bound to that pair.
- T0 owns registry/authorization; T1 issues sequence within its assigned namespace. A producer registry row or producer self-assertion is not proof of origin, uniqueness or fencing.
- REST-response and T1-reconstructed snapshots have different evidence requirements and may not be conflated.
- A snapshot group is accepted only when a source-generated completion manifest proves its exact group, counts, object digest, completeness and empty-book semantics. EOF, file rotation, elapsed time or row count alone are not completion evidence.
- No partial snapshot group is canonically accepted. Group rows and manifest are committed atomically.
- Current T1 CSV lacks this manifest and producer identity; current-schema snapshots remain non-canonical-acceptable until additive evidence exists.

## 4. Decimal canonicalization

`CanonicalDecimalString` is a base-10 string, never a binary floating-point value.

- Reject NaN, Infinity, exponent notation, leading plus, whitespace, locale separators and negative zero.
- Remove redundant leading integer zeros and trailing fractional zeros; remove the decimal point if no fractional digits remain.
- Canonical zero is exactly `0`.
- Price must be strictly positive. Quantity must be nonnegative for depth changes; retained snapshot levels must be positive.
- No rounding is allowed during canonicalization. Precision/scale ceilings are separate configuration gates (B-14/B-20).
- The original source lexeme remains available only through immutable raw-object evidence; canonical decimal normalization does not replace it.

## 5. Versioned digest encoding

Do not hash ordinary JSON serialization or a language runtime's default map order.

### 5.1 Raw evidence digest

`raw_object_sha256 = SHA256(exact immutable source-object bytes)`.

For a CSV row, the source object is the exact CSV file object and the row locator identifies the exact row. A separate optional `raw_record_sha256` may hash the exact byte range for that row. Neither digest is described as a native exchange-message digest unless original native bytes were actually retained.

### 5.2 Canonical semantic digest

Version 1 is a deterministic typed-field frame:

- Prefix: ASCII bytes `BTCQ-T0-CANONICAL-V1\0`.
- Fixed field order per domain schema; each field frame is `tag:u16 big-endian | type:u8 | length:u32 big-endian | value:bytes`.
- Type codes: UTF8=1, signed-int64=2, unsigned-int64=3, boolean=4, decimal-string=5, nullable-null=6, list=7.
- Integer values use fixed-width big-endian two's-complement (signed) or unsigned representation. Boolean is one byte 0x00/0x01. Null has zero length.
- UTF-8 strings are validated; canonical instrument identifiers use the documented lowercase ASCII normalization. Do not silently normalize arbitrary source strings.
- Decimal values use §4 canonical strings encoded as UTF-8.
- Lists encode a u32 element count followed by each element as a nested length-framed typed record. Preserve the source order for depth updates and snapshot levels in v1; reordering therefore changes the digest and is conservatively a conflict.
- Include contract version and domain discriminator in the digest preimage. Exclude delivery locator, T0 receipt/commit time, retry count and transport-attempt metadata from semantic payload digest.
- `canonical_payload_sha256 = SHA256(encoded canonical semantic payload)`.

Identity and digest are separate: same identity + same semantic digest is replay; same identity + different semantic digest is conflict. Raw object digest changes do not by themselves mean canonical semantic conflict if the semantic payload is unchanged.

## 6. Source-delivery locator and idempotency

A delivery locator identifies one immutable observation in one source object; it is not a canonical event identity.

- Preferred CSV locator: `(raw_object_sha256, byte_start, byte_end_exclusive)`.
- If byte offsets cannot be guaranteed, use a stable row index only when the object bytes are immutable and the row parser/version is pinned.
- Snapshot locator identifies the whole immutable group/manifest, not an arbitrary price-level row.
- Unique delivery constraint: one terminal intake outcome per immutable locator and source schema version.
- Same locator retry returns the already committed outcome. Same locator with changed object digest or row bytes is a source-object integrity conflict, not a new attempt.

## 7. Checkpoint contract

Two independently persisted checkpoints are mandatory.

```text
SourceDeliveryCursorV1 {
  source_object_sha256: 64-hex
  source_object_version: string
  record_locator: immutable locator
  source_schema_version: string
  last_terminal_outcome: "ACCEPTED" | "DUPLICATE_REPLAY" | "CONFLICT"
                       | "QUARANTINED" | "GAP_RECORDED" | "RESOURCE_REJECTED"
  cursor_generation: uint64
  committed_at_ms: int64
}

BookSequenceWatermarkV1 {
  exchange: string
  market_type: string
  symbol: string
  snapshot_capture_identity: (capture_producer_id, capture_sequence)
  stream_epoch: string
  snapshot_anchor_update_id: uint64
  last_contiguous_applied_update_id: uint64
  continuity_state: "CONTIGUOUS" | "GAP_PENDING" | "GAP_UNRESOLVED"
                   | "CONFLICTED" | "UNAVAILABLE"
  watermark_generation: uint64
  committed_at_ms: int64
}
```

Rules:
- Source cursor advances only after the source observation and terminal outcome are durable. It may advance after durable quarantine/gap/resource rejection.
- Book watermark advances only after a diff is actually and contiguously applied to the derived book and the resulting book state is durable.
- A source cursor may be ahead of the book watermark. This is expected after quarantine/gap and is not evidence of book continuity.
- A watermark may never jump over a gap, conflict, quarantine, resource rejection or unapplied event.
- Restart restores both markers and unresolved-gap state independently. Never derive one from the other.

## 8. Atomic persistence and acknowledgement

Logical transaction boundary for one intake observation:

1. Verify immutable source object is durable and addressable. For filesystem-backed objects: write temp file, flush/fsync, atomic rename, fsync parent directory; for object storage, require a successful immutable-object durability acknowledgement before the DB transaction.
2. Begin one T0 canonical-store transaction.
3. Insert/verify source-object and record-locator evidence.
4. Claim the delivery locator under a unique constraint; on conflict, compare exact locator/object digest and return the previous terminal result only if identical.
5. Resolve native canonical identity:
   - absent identity → reject/quarantine;
   - same identity + same semantic digest → DUPLICATE_REPLAY;
   - same identity + different semantic digest → CONFLICT, preserve both evidence references, no overwrite;
   - new identity → candidate acceptance subject to all domain validations.
6. For accepted SD-06 diffs, apply the event to the derived book only if snapshot bridge and continuity are valid; persist canonical event, application outcome, derived book mutation and book watermark in the same transaction.
7. For a gap/conflict/quarantine/resource rejection, persist source evidence, outcome, source cursor and gap state; do not advance book watermark.
8. For SD-07, insert manifest, capture identity, all level rows and terminal outcome in one transaction. Partial groups are not visible as accepted captures.
9. Update source cursor and checkpoint generation with compare-and-swap/monotonic-generation protection.
10. Commit. Only after commit may T0 acknowledge the source delivery.

### Crash/retry matrix

| Crash point | Required recovery |
|---|---|
| Before source object durable | No cursor advance; source must be reacquired/retried |
| After object durable, before DB transaction | Orphan immutable object is safe; rescan/retry by same locator |
| During DB transaction | Rollback all canonical rows/outcomes/checkpoints/book changes |
| After DB commit, before acknowledgement | Retry same locator; return prior committed outcome; no duplicate book effect |
| After acknowledgement | Commit and both checkpoint states already durable |

### Store requirements

- One transaction must cover delivery claim, canonical identity/digest outcome, checkpoint state and applicable derived-book mutation.
- A store that cannot enforce unique constraints and atomic multi-record transactions cannot implement this contract.
- For SQLite, transaction mode, journal/synchronous settings, busy/lock handling, durability guarantees, backup/restore behavior and single-writer fencing must be separately verified before claiming crash durability.
- External object storage is outside the SQLite transaction; the immutable object must be durable before committing a DB reference. Orphan objects are acceptable; dangling DB references are not.
- No delete-on-ack, source-object deletion or automatic retention expiry is included.

## 9. Blocker disposition after source audit and design work

| Blocker | Current disposition | Why it remains open / closure evidence |
|---|---|---|
| B-01 | PARTIALLY RESOLVED | T1 source proves T→timestamp_ms and q/a/f/l/m mappings; build provenance and exact decimal/raw-payload fidelity remain unverified |
| B-02 | OPEN — CONTRACT PROPOSED | ID fields are parsed as signed i64; nonnegative/range/order validation must be tested and source semantics pinned |
| B-03 | RESOLVED AT SOURCE-MAPPING LEVEL | T1 maps m=true→sell, false→buy; Binance describes m as buyer-maker. Contract requires exact cross-field validation; tests still pending |
| B-04 | OPEN | No immutable stream_epoch in current T1 CSV; additive capture provenance and lifecycle proof required |
| B-05 | OPEN | Binance defines U/u/pu, but exchange namespace uniqueness across reconnect/restart and the selected exact USD-M snapshot bridge still need pinned protocol/T1 proof |
| B-06 | OPEN | T1 parses E and T but current CSV drops T; raw-message bytes and receive-time provenance are not persisted in current schema |
| B-07 | OPEN | Producer-origin attestation, allocator, single-writer fencing, durable sequence non-reuse and restore/rollback proof absent |
| B-08 | OPEN | Source-generated snapshot completion manifest absent |
| B-09 | OPEN | Snapshot-to-stream epoch linkage absent |
| B-10 | OPEN | Immutable object/manifest and stable row/group locator policy not implemented/proven |
| B-11 | DESIGN SPECIFIED — NOT VERIFIED | Typed digest preimage proposed here; requires independent review, cross-language vectors and exact-decimal tests |
| B-12 | DESIGN SPECIFIED — NOT VERIFIED | Atomic transaction/recovery protocol proposed; requires store-specific crash/restart/rollback proof |
| B-13 | CLOSED — OWNER BOUNDED EXCLUSION | Read API/dataset-version compatibility remains outside Phase B |
| B-14 | OPEN | Numeric count/age/wait limits cannot be invented; measure source behavior and owner-approve ceilings |
| B-15 | OPEN — SOURCE OMISSION CONFIRMED | aggTrade nq absent; depth T parsed but dropped by current CSV conversion |
| B-16 | CLOSED — OWNER BOUNDED EXCLUSION | Ordinary non-RPI depth only |
| B-17 | OPEN — SOURCE MAPPING PASS, BUILD PROVENANCE BLOCKED | Exact source path proven; deployed/imported producer binary not tied to that source build |
| B-18 | OPEN | Snapshot manifest fields designed; source producer does not emit/verify completion manifest |
| B-19 | DESIGN SPECIFIED — NOT VERIFIED | Independent cursor/watermark and restart semantics specified; atomic implementation proof absent |
| B-20 | OPEN | Raw bytes, parsed levels, decimal token, buffer and group ceilings require measurement and owner approval |

A design-level resolution is not an implementation/test pass. B-03 is closed only at source-mapping semantics; its DTO validation remains a mandatory test gate. B-11/B-12/B-19 are specified but remain blockers until independently reviewed and proven in the selected store.

## 10. Remaining hard gates

1. Pin and verify exact deployed/imported T1 binary/build provenance or keep the affected data lineage unverified.
2. Verify exact Binance USD-M bridge protocol and exchange identity namespace scope; do not infer across product families.
3. Define and prove T1 producer attestation, allocation, fencing, sequence persistence and restore/rollback policy.
4. Define source-generated SD-07 manifest and stable immutable source object/row locators.
5. Derive numeric limits from bounded source measurements and resource budgets; owner approval required.
6. Independently review this DTO/digest/checkpoint/atomicity design.
7. Obtain explicit owner authorization before implementing any DTO, validator, test fixture, DDL, persistence change or running the 101-case synthetic matrix.

## 11. Explicit non-authorization

No code, DTO implementation, parser change, validator, fixture, test execution, DDL, database mutation, source copy, import, data movement, collector activation, T0/T1 runtime, T2 connection, API, VPS process, systemd/autostart, deployment or trading action is authorized by this design. The 101-case matrix remains NOT EXECUTED. Contract Freeze remains NOT APPROVED.
