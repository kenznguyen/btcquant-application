# T1 Orderbook Consumer Contract V1 — Design and Acceptance Specification

Status: **DESIGN APPROVED / DOCUMENTATION ONLY**  
Repository: `kenznguyen/btcquant-application`  
Owning producer: `kenznguyen/binance-futures-collector`  
Scope: BTCUSDT Binance USD-M perpetual orderbook snapshot, consumer-side only  
Provider status: **PAUSED** — this document does not authorize provider implementation or activation  
Runtime status: **NOT APPROVED** — no T1 → T2 runtime connection

## 1. Purpose and boundaries

Define the Application-owned contract boundary for consuming a verified T1 BTCUSDT orderbook snapshot at a future, separately approved integration point.

This contract is deliberately separate from T0 candles:

- T0 remains the independent canonical source for M15/H1 candles and historical candle continuity.
- T1 remains the owner of exchange WebSocket/REST collection, orderbook reconstruction, raw capture/storage, replay, and provider implementation.
- Application owns only the consumer-side schema, DTO, validation, typed errors, future adapter boundary, and deterministic fixtures/tests.
- T1 orderbook data is an optional market-context input. It is not a candle source, not a signal, and not an execution instruction.
- Strategy Core (RSI + ADX + Smart DCA) and independent AI Strategy retain their own signal generation. Neither strategy may bypass the Shared Risk Engine or Kill Switch.
- No provider endpoint, socket, HTTP client, background worker, collector process, exchange request, or runtime integration is created by this design.

Out of scope: trades, liquidations, klines, funding, open interest, raw CSV, capture/replay, storage migration, T0 access, provider activation, live trading.

## 2. Source snapshot and provenance

Design reviewed against these exact repository snapshots:

| Item | Repository / branch | SHA or blob |
|---|---|---|
| Application baseline | `btcquant-application` / `main` | `d0fb85f0711b7459306bf0fbe63737c0086d5ca6` |
| Ownership decision | Application / `main` | `1f5fd95f73e76e2dbc976e6c1e6e77ccca477a7b` (document blob) |
| T1 baseline | `binance-futures-collector` / `main` | `c91a8c22d3b6236c98ab9a4d4d69b25d47f7f738` |
| T1 Provider contract/RED plan | T1 / `main` | `fcf45baff1707aa839f6294493e963b1e774c6e8` |
| T1 publisher module | T1 / `main` | `1a17f60f3b0a960ac5cb67ddee1dafc57dd718b2` |
| T1 OrderbookManager | T1 / `main` | `d18d047c1f7cdddd03cea60b02de54b656ad4edf` |
| T1 publisher tests | T1 / `main` | `2bdb6386f33a589fee229b0c2790c051c7bbde44` |

The T1 contract document says the provider is implemented only in part and paused; there is no HTTP route or collector-runtime integration. The Application consumer must therefore be testable from deterministic byte fixtures without a provider or network.

## 3. Consumer contract identity

- Contract version: `T1_T2_ORDERBOOK_V1`
- Symbol: `BTCUSDT`
- Market: `BINANCE_USDM_PERPETUAL`
- Direction: producer → consumer, read-only
- Payload: one immutable, complete orderbook snapshot
- Consumer policy: validate the entire payload before exposing any typed snapshot to downstream code
- Unknown versions, unknown fields, missing fields, malformed values, and any failed invariant are rejected (fail closed).

The V1 DTO is a wire-format model, not the internal Strategy Core or AI Strategy feature model. A later feature adapter must explicitly map validated fields into strategy inputs; it must not silently reinterpret or fill missing orderbook data.

## 4. Wire schema

The JSON object has exactly these 17 top-level fields:

| Field | Wire type | Required invariant |
|---|---|---|
| `contractVersion` | string | Exactly `T1_T2_ORDERBOOK_V1` |
| `symbol` | string | Exactly `BTCUSDT` |
| `market` | string | Exactly `BINANCE_USDM_PERPETUAL` |
| `bids` | array of two-string tuples | Price descending; quantity positive; at least 20 levels |
| `asks` | array of two-string tuples | Price ascending; quantity positive; at least 20 levels |
| `snapshotLastUpdateId` | unsigned JSON integer | REST snapshot anchor, non-negative |
| `firstAppliedU` | unsigned JSON integer | First applied diff event's `U` |
| `lastAppliedU` | unsigned JSON integer | Latest applied diff event's `u`; not below first applied U |
| `sourceTimestampMs` | unsigned JSON integer | Binance event time `E` for latest applied diff |
| `observedAtMs` | unsigned JSON integer | Local UTC receipt time for that same diff |
| `decisionWatermark` | unsigned JSON integer | Exactly equals `lastAppliedU` |
| `generation` | unsigned JSON integer | Greater than zero |
| `snapshotId` | string | `sha256:<64 lowercase hex>`; digest of canonical snapshot excluding this field |
| `continuity` | string | Exactly `VERIFIED` |
| `freshness` | string | Exactly `FRESH` at producer publication time; consumer independently checks age |
| `depth` | object | Exactly two keys: `bids`, `asks`; counts equal array lengths |
| `complete` | boolean | Exactly `true` |

Nested shape is strict:

- Each bid/ask level is exactly `[priceText, quantityText]`; no JSON floating-point or integer values are accepted for price/quantity.
- `depth` contains exactly `bids` and `asks`, both unsigned integer counts.
- No nulls, extra object keys, duplicate JSON keys, non-finite numbers, or trailing payload data.
- Response body maximum: 65,536 bytes (65 KiB). Reject before unbounded buffering or decoding.

## 5. Decimal canonicalization

Price and quantity remain strings end-to-end; never parse through binary floating point.

Canonical decimal grammar:

- ASCII digits only, optional single decimal point.
- At least one whole-number digit.
- No sign, exponent, whitespace, thousands separators, or leading zeroes except the value `0`.
- If a fractional part exists, it is non-empty and must not end in `0`.
- Quantity must be strictly greater than zero.
- Price must be strictly greater than zero.
- Compare decimal strings exactly using digit/scale comparison (or a proven arbitrary-precision decimal implementation); never compare via `f64`.

Book invariants:

- Bid prices strictly descending; ask prices strictly ascending.
- No duplicate price levels on either side.
- Best bid strictly below best ask (locked/crossed book rejected).
- At least 20 levels on each side.
- `depth.bids == bids.length` and `depth.asks == asks.length`.

## 6. Sequence, timestamps, and snapshot identity

### Sequence and continuity

- `decisionWatermark == lastAppliedU`.
- `lastAppliedU >= firstAppliedU`.
- `generation > 0`.
- Producer is responsible for proving the REST-anchor bridge, strict continuity of subsequent diffs, and invalidation/re-anchor behavior before publishing `continuity=VERIFIED`.
- Consumer must not infer full event-chain continuity from only the three sequence fields in this snapshot; the wire payload does not carry every intervening `pu`.
- Consumer verifies only the observable snapshot-level relationships after the producer-side continuity claim has been accepted.

**Open contract issue — bridge boundary must be reconciled before provider implementation resumes.** Binance's initial bridge rule can accept an event where `U <= snapshotLastUpdateId + 1 <= u`; therefore `firstAppliedU` may be less than or equal to the snapshot anchor. The current T1 publisher validator rejects `firstAppliedU <= snapshotLastUpdateId`. This may reject a valid bridge event. T1's producer contract, publisher validator, and consumer acceptance fixtures must agree on the exact boundary before any provider activation. This Application design does not change or waive the T1 rule.

### Freshness

At consumer evaluation time `nowMs`:

- `sourceTimestampMs <= nowMs + 250`.
- `observedAtMs <= nowMs + 250`.
- `nowMs - sourceTimestampMs <= 2,000`.
- `nowMs - observedAtMs <= 2,000`.
- Reject negative, overflowed, or non-integral timestamp values.
- Consumer uses one captured evaluation-time value for all timestamp checks in one validation operation.
- A producer's `freshness=FRESH` label never overrides a failed consumer-side age check.

The source and observed timestamps must describe the same latest applied diff. The consumer cannot independently prove this pairing from the payload alone; it relies on producer provenance and future producer-side tests.

### Snapshot digest

- Digest prefix: `sha256:`.
- Hash input: UTF-8 canonical JSON for the complete object with `snapshotId` omitted.
- Canonicalization must be pinned by golden test vectors: recursively sorted object keys, compact separators, UTF-8, no insignificant whitespace, deterministic JSON number representation.
- Consumer recomputes the digest and compares in constant-time where practical.
- Do not treat a valid digest as authentication or provenance; transport authentication and producer trust are separate controls.

## 7. Consumer-side module boundary (proposed; not implemented)

Proposed Application location:

```text
market_data/t1_orderbook/
  contract.py       # immutable wire DTO / typed domain snapshot
  validation.py    # strict parsing and invariant validation
  errors.py        # stable typed rejection reasons
  adapter.py       # future transport-neutral consumer boundary
  fixtures/        # deterministic valid and invalid payloads
  test_contract.py
  test_validation.py
  test_adapter.py
```

Responsibilities:

- `contract.py`: immutable typed representation; keep wire strings and unsigned integer semantics explicit.
- `validation.py`: bounded JSON decoding, exact key-set checks, schema/type checks, decimal comparison, book invariants, timestamps, digest.
- `errors.py`: stable machine-readable categories such as `PAYLOAD_TOO_LARGE`, `MALFORMED_JSON`, `UNSUPPORTED_VERSION`, `SCHEMA_MISMATCH`, `INVALID_DECIMAL`, `INVALID_BOOK`, `INVALID_SEQUENCE`, `STALE_SNAPSHOT`, `FUTURE_TIMESTAMP`, `DIGEST_MISMATCH`.
- `adapter.py`: later accept bytes/payload from a separately approved source interface and return either a validated immutable snapshot or a typed unavailable/rejected result. No HTTP, socket, retry, scheduler, or background worker is part of this design.
- Fixtures: synthetic only; clearly labelled as synthetic and never represented as exchange evidence.

No imports from T1 Rust source are required. No shared source tree, submodule, Git subtree, binary copy, or duplicated producer implementation is permitted.

## 8. Failure semantics (fail closed)

A rejected/unavailable snapshot must not be converted to an empty book, zero liquidity, cached last-known-good data, synthetic data, or a candle-derived substitute.

- Invalid payload: reject with typed reason.
- Missing snapshot / provider unavailable: return unavailable; do not invent a snapshot.
- Stale or future timestamps: reject.
- Unknown version/schema: reject; no permissive fallback.
- Digest mismatch: reject.
- Partial/truncated/oversized payload: reject.
- Consumer must not silently retry or switch source in this contract. Retry/transport policy belongs to a separately approved transport design.
- Rejection must not create a Strategy Core or AI signal, suppress a valid independent signal, or bypass the Shared Risk Engine. Strategy-level policy for optional orderbook features is a separate decision.

## 9. Acceptance test specification (design only)

These are required future tests; **no test files or test code are created in this approval**. Use deterministic synthetic fixtures and a fixed `nowMs`. Test names below are normative acceptance behavior.

### A. Parsing and schema

1. `accepts_exact_v1_payload_with_all_17_fields` — valid fixture parses.
2. `rejects_unknown_contract_version`.
3. `rejects_wrong_symbol_or_market`.
4. `rejects_missing_each_required_top_level_field` — parameterized across all fields.
5. `rejects_any_unknown_top_level_or_nested_field`.
6. `rejects_duplicate_json_object_keys`.
7. `rejects_non_object_root_and_trailing_json_data`.
8. `rejects_malformed_or_truncated_json`.
9. `rejects_payload_over_65536_bytes_before_unbounded_decode`.
10. `rejects_boolean_or_float_where_unsigned_integer_is_required`.
11. `rejects_negative_or_overflowed_unsigned_integer`.
12. `rejects_numeric_price_or_quantity_instead_of_string_tuple`.
13. `rejects_tuple_with_missing_or_extra_elements`.

### B. Decimal and orderbook correctness

14. `accepts_canonical_decimal_strings_without_float_rounding`.
15. `rejects_empty_signed_exponent_whitespace_and_non_ascii_decimal`.
16. `rejects_leading_zero_and_fraction_with_trailing_zero`.
17. `rejects_zero_or_negative_price_and_quantity`.
18. `rejects_bid_levels_not_strictly_descending`.
19. `rejects_ask_levels_not_strictly_ascending`.
20. `rejects_duplicate_bid_or_ask_price`.
21. `rejects_locked_or_crossed_spread`.
22. `rejects_fewer_than_20_levels_on_either_side`.
23. `rejects_depth_count_mismatch`.

### C. Sequence, freshness, and digest

24. `requires_nonzero_generation`.
25. `requires_decision_watermark_equal_last_applied_u`.
26. `rejects_last_applied_u_below_first_applied_u`.
27. `applies_approved_initial_bridge_boundary_fixture` — blocked until the open bridge-boundary issue in Section 6 is reconciled.
28. `rejects_source_timestamp_older_than_2000ms`.
29. `rejects_observed_timestamp_older_than_2000ms`.
30. `rejects_source_or_observed_timestamp_more_than_250ms_in_future`.
31. `uses_one_fixed_evaluation_time_for_all_freshness_checks`.
32. `rejects_snapshot_digest_mismatch`.
33. `matches_canonical_snapshot_digest_golden_vectors`.
34. `does_not_treat_digest_as_transport_authentication` — contract/security boundary test or design assertion.

### D. Adapter boundary and isolation

35. `returns_immutable_validated_snapshot_only_after_all_checks_pass`.
36. `returns_typed_unavailable_when_no_payload_is_supplied`.
37. `does_not_return_partial_snapshot_after_any_validation_failure`.
38. `does_not_fallback_to_t0_candles_or_synthetic_orderbook`.
39. `does_not_create_http_socket_or_background_task_during_contract_validation`.
40. `does_not_emit_strategy_signal_or_execution_side_effect`.
41. `preserves_exact_decimal_text_through_dto_round_trip`.
42. `keeps_fixtures_marked_synthetic_and_separate_from_exchange_evidence`.

### E. Regression and evidence

43. Run focused T1 consumer contract tests in the Application repository once implemented.
44. Run the existing relevant Application regression suite; no T0 tests may be weakened or skipped.
45. Record exact source SHA, workflow run/job IDs, artifact IDs and SHA-256 (if produced), test count, and PASS/BLOCKED/NOT VERIFIED.
46. Verify no T1 repository, T0 data asset, provider runtime, VPS, exchange, credentials, or trading path was accessed by the test harness.

Acceptance tests are a future implementation gate. This document-only approval does not authorize writing or running them.

## 10. Known producer-side gaps / compatibility blockers

These are observations from the reviewed T1 source snapshot, not instructions to modify T1:

1. **Exact decimal provenance:** T1 `OrderbookManager` stores price keys/quantities as `f64`; original wire decimal strings are discarded in the live book path. Provider must prove exact decimal preservation before it can satisfy this consumer contract.
2. **Snapshot metadata:** current manager state does not retain all V1 metadata (REST anchor, first applied U, event E, local receive time, generation) as one trusted publication state.
3. **Continuity enforcement:** current manager's normal depth update path does not enforce strict `pu == previous u` after reconnect; Provider V1 must not publish VERIFIED until continuity is proven and invalidation/re-anchor behavior is correct.
4. **Receipt timestamp provenance:** buffered WebSocket messages need a trusted local UTC receipt timestamp paired with the same diff whose Binance event time is emitted.
5. **Bridge-boundary mismatch:** Section 6; current publisher validation appears stricter than the bridge semantics in the T1 design.
6. **No live provider route:** current T1 source has a publisher module, but the contract doc states no HTTP route or collector runtime integration. Provider remains paused.

Consumer-side validation cannot repair missing producer provenance. Do not relax consumer validation to make an incomplete producer appear compatible.

## 11. Transport and security deferred decisions

Not pinned by this consumer DTO design:

- HTTP route/path, listener address, proxy/gateway, token provisioning/rotation, TLS, and process lifecycle.
- Request timeout, response retry, circuit-breaker, cache, polling cadence, and resource budgets beyond the payload ceiling.
- Provider startup/readiness semantics and deployment topology.
- Whether a future Application transport uses an in-process adapter, loopback HTTP client, or gateway route.

Any transport design must be separately approved and must preserve authenticated, read-only, bounded, fail-closed behavior. The paused T1 Provider is not to be activated as part of that later design.

## 12. Approval and change control

Approved scope in this increment:

- Consumer-side T1 Orderbook V1 design and schema.
- Proposed Application module boundary.
- Deterministic synthetic acceptance-test specification.
- Read-only comparison against the T1 producer contract/source snapshot.

Not approved:

- Source implementation or test-code creation/execution.
- T1 Provider changes, endpoint additions, or workflow dispatch.
- T1 collector start/restart, exchange/network access, deployment, or VPS access.
- T1 → T2 runtime connection or strategy feature activation.
- T0 data/database/runtime access or modification.
- Storage/data migration, live trading, or real orders.

Current disposition: **DESIGN BASELINE RECORDED; IMPLEMENTATION NOT STARTED; ACCEPTANCE TESTS SPECIFIED BUT NOT EXECUTED; PRODUCER COMPATIBILITY BLOCKED BY OPEN ITEMS ABOVE.**


---

## 13. Implementation status override — 2026-11-21

This update supersedes the earlier statements in Sections 9 and 12 that no consumer test code had been created or executed. The owner subsequently approved the bounded consumer implementation.

- Consumer package implemented under `market_data/t1_orderbook/`: immutable DTO, typed errors, strict validator, deterministic synthetic fixture builder, and a transport-neutral adapter that performs no I/O.
- Focused suite: **43 T1 consumer acceptance tests**. Adjacent offline T0 REST-tail validator regression: **10 tests**.
- Final GitHub Actions run [44850261269](https://github.com/kenznguyen/btcquant-application/actions/runs/44850261269), exact tested source SHA `3d85f19e36807f3b7eed1eb8a9057b4a77173a6d`, job `136679697952`: **53/53 PASS** in an isolated network-disabled CPython 3.12.16 container.
- Artifact `t1-orderbook-consumer-contract-evidence`: ID `14684123969`, SHA-256 `d160586bbaff3187ffdfdfa6d4bb0a27c64e1924e09202b537b647281e6d2e6b`.
- RED-first evidence: run [44849764243](https://github.com/kenznguyen/btcquant-application/actions/runs/44849764243), test-first SHA `4b7f9326a6bf1c8d658a0a0c0c87ae683a9db877`, failed as expected before the consumer package existed.
- The initial bridge-boundary test remains blocked and intentionally unimplemented because T1's design and publisher validator disagree on the accepted initial bridge event. Do not resolve this by weakening consumer checks or guessing a producer rule.
- Consumer implementation does not include HTTP, sockets, retries, caches, background work, T0 fallback, strategy signal generation, or execution. The adapter accepts already-obtained bytes only. No provider or runtime activation follows from this PASS.
- Producer compatibility remains **BLOCKED** by decimal provenance (`f64` in T1 OrderbookManager), incomplete snapshot metadata, strict continuity/reconnect evidence, receipt-time provenance, and the bridge-boundary mismatch. T1 Provider remains **PAUSED**.
- Independent review: **NOT PERFORMED**. Production readiness and T1 → T2 runtime: **NOT VERIFIED / NOT APPROVED**.
- Full implementation evidence and file blob SHAs: `docs/evidence/T1_ORDERBOOK_CONSUMER_V1_IMPLEMENTATION_2026-11-21.md`.

Current disposition: **CONSUMER IMPLEMENTATION PASS FOR THE TESTED SUBSET; PRODUCER COMPATIBILITY BLOCKED; TRANSPORT AND RUNTIME NOT IMPLEMENTED OR AUTHORIZED.**
