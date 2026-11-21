# T0 Provenance Validator — Interface Contract V1

Date: 2026-11-22  
Repository: kenznguyen/btcquant-application  
Branch: main  
Status: **DESIGN CONTRACT — DOCUMENTATION ONLY; OWNER APPROVED**

## 1. Purpose and decision boundary

This document freezes the Python-facing interface expected by the S2 synthetic RED tests for `market_data.archive_provenance_validator`.

It resolves the previously open interface questions:
- public function names, arguments and return types;
- immutable result DTO;
- stable error-code catalogue for the S2 V1 validator surface;
- deterministic error aggregation and ordering;
- input-shape handling and side-effect boundaries.

This is a design contract only. It does **not** authorize or implement GREEN validator code, edits to RED tests, DDL, SQLite, importer, archive retrieval, workflows, or any data/runtime operation. A separate owner approval is required before implementation.

## 2. Module and public API

Expected module:

```python
market_data.archive_provenance_validator
```

The V1 public API consists of exactly these three functions:

```python
encode_t0enc1(domain: str, *fields: str | bytes | int | None) -> bytes

derive_attempt_id(
    *,
    object_id: str,
    attempt_number: int,
    workflow_run_id: str,
    workflow_job_id: str,
    trigger_sha: str,
    requested_key: str,
) -> str

validate_provenance(payload: Mapping[str, object]) -> ProvenanceValidationResult
```

No network, filesystem, archive, exchange, SQLite, database, environment-variable, clock, random-number, or process access is permitted. Functions are deterministic and side-effect-free. The validator must not mutate the supplied payload or nested values.

## 3. Result DTO

The result type is an immutable dataclass:

```python
@dataclass(frozen=True, slots=True)
class ProvenanceValidationResult:
    valid: bool
    error_codes: tuple[str, ...]
```

Contract:
- `valid` is exactly `True` if and only if `error_codes == ()`.
- `error_codes` is a tuple of unique stable V1 error-code strings.
- No free-form error text, source values, paths, secrets, response bodies, stack traces or nondeterministic metadata are included.
- V1 does not expose warnings. A warning system, detailed diagnostics, or extra result fields require a separately reviewed interface version/amendment.
- The result object and its `error_codes` collection are immutable.

## 4. T0ENC1 encoder interface

`encode_t0enc1` implements the exact S1 §3 framing contract:
1. Prefix bytes: ASCII `T0ENC1` followed by NUL.
2. Domain: UTF-8 bytes preceded by unsigned 32-bit big-endian byte length.
3. Field count: unsigned 32-bit big-endian.
4. Each field:
   - `None`: tag `0x00`, then unsigned 64-bit big-endian zero length.
   - non-null: tag `0x01`, unsigned 64-bit big-endian byte length, then field bytes.
5. `str` is encoded as exact UTF-8; `bytes` are used unchanged; `int` is canonical base-10 ASCII. Boolean is not accepted as an integer field.
6. No trimming, Unicode normalization, case folding, implicit coercion, or NULL/empty equivalence.

Reject invalid argument types, invalid UTF-8 input strings, a non-string/empty domain, and values whose encoded lengths/counts cannot fit the specified unsigned framing fields. The function returns raw `bytes`, not hex or a digest.

The two existing RED tests define mandatory examples:
- field boundaries must distinguish `("ab", "c")` from `("a", "bc")`;
- `None` must differ from the empty string;
- output begins with `b"T0ENC1\\x00"`.

## 5. Acquisition attempt ID interface

`derive_attempt_id` implements S1 §12.2 exactly:

```text
"att1:" + lowercase_hex(
  SHA256(ENC(
    "T0-ACQUISITION-ATTEMPT-V1",
    object_id,
    attempt_number,
    workflow_run_id,
    workflow_job_id,
    trigger_sha,
    requested_key
  ))
)
```

Rules:
- `attempt_number` is an integer, not bool, in the positive signed-64-bit range; it is framed as canonical ASCII decimal by T0ENC1.
- All other arguments are non-empty strings encoded as UTF-8 without normalization.
- The output is exactly `att1:` followed by 64 lowercase hexadecimal characters.
- Identical arguments always produce identical IDs. Changing any framed field, including attempt number, changes the preimage and therefore the derived ID.
- The function does not check database uniqueness or whether an attempt was actually run; it only derives the deterministic identifier.

## 6. Validator input contract

The validator accepts one mapping with these top-level keys:

| Key | Required type | Meaning |
|---|---|---|
| `inventory` | mapping | Pinned inventory metadata and its `objects` collection |
| `objects` | list/tuple of mappings | Archive object evidence |
| `pairs` | list/tuple of mappings | ZIP/sidecar pair evidence |
| `members` | list/tuple of mappings | Observed CSV member evidence |
| `attempts` | list/tuple of mappings | Acquisition attempt evidence |
| `source_rows` | list/tuple of mappings | Source-row provenance |
| `candles` | list/tuple of mappings | Candidate candle rows |
| `links` | list/tuple of mappings | Candle provenance links |

The inventory mapping contains an `objects` list/tuple of allowlisted inventory entries. The exact approved S1 inventory scope is 404 entries (202 ZIP and 202 CHECKSUM_SIDECAR entries); a missing or incomplete evidence set is not treated as success.

Negative test fixtures may intentionally omit fields from individual evidence mappings to represent incomplete evidence. Such omissions must be evaluated as semantic failures where applicable, not silently defaulted to success.

If the payload is not a mapping, a required top-level key is missing, a top-level collection has the wrong container type, or a collection contains a non-mapping item, return `PROVENANCE_INPUT_SHAPE_INVALID`. Do not raise an incidental Python exception for these payload-shape failures.

The validator does not accept a caller-supplied expected-error list, success override, permissive mode, or skip-validation flag.

## 7. Stable V1 error-code catalogue

The following catalogue is closed for interface V1. Codes are machine-readable, uppercase ASCII identifiers. Their meanings must not be repurposed.

| Code | Required meaning |
|---|---|
| `PROVENANCE_INPUT_SHAPE_INVALID` | Payload or evidence collection has an invalid top-level/container shape |
| `INVENTORY_OBJECT_SET_INCOMPLETE` | Evidence does not account for the exact approved inventory object set |
| `OBJECT_NOT_IN_APPROVED_INVENTORY` | An evidence object/requested key is not the exact allowlisted inventory object |
| `QUARANTINED_EVIDENCE_PRESENT` | Quarantined object/pair/member evidence is present in a candidate presented for validation |
| `ATTEMPT_OUTCOME_UNKNOWN` | An acquisition attempt has outcome UNKNOWN and cannot be treated as successful |
| `TRANSFERRED_ATTEMPT_INCOMPLETE` | A TRANSFERRED attempt lacks complete-object evidence, including its complete-object digest |
| `VERIFIED_PAIR_MEMBER_CARDINALITY_INVALID` | A VERIFIED pair does not have exactly one VERIFIED CSV member |
| `ACCEPTED_SOURCE_ROW_LINK_CARDINALITY_INVALID` | An ACCEPTED source row does not have exactly one matching provenance link |
| `CANDLE_IDENTITY_VALUE_CONFLICT` | One candle natural identity is associated with conflicting normalized candle values |
| `CANDLE_AVAILABILITY_BOUNDARY_INVALID` | BAR_CLOSE_BOUNDARY availability does not equal open time plus the full timeframe interval |

These are the complete error codes asserted by the current S2 RED test file plus the one input-shape code required to make malformed API inputs deterministic. This is **not** a claim that every S1 cross-record invariant already has a dedicated V1 error code or is covered by the current 12 tests. Any additional invariant/code needed by a later implementation must be proposed as a reviewed V1 amendment or a new interface version before it is relied upon.

## 8. Error aggregation and determinism

- Evaluate all applicable checks; do not stop after the first semantic violation.
- Return each applicable error code once, even if multiple records trigger the same code.
- Order codes by the exact catalogue order in §7, not by dictionary iteration order, row order, hash-map order, locale, or exception order.
- The same logically equivalent payload must produce the same `valid` and `error_codes` regardless of input mapping insertion order or evidence-list permutation, except where the S1 contract explicitly defines order as meaningful (for example, ordinal fields within one CSV member).
- No nondeterministic detail is included in the result.
- If any error code is present, `valid=False`; otherwise `valid=True`.

## 9. Relationship to S1 and limits of this freeze

This interface implements the Python boundary for S1 design contracts; it does not replace them. The validator's semantic checks remain governed by:
- S1 §2–§3 stable identifiers and T0ENC1 framing;
- S1 §4 and §12 provenance evidence, quarantine and acquisition-attempt semantics;
- S1 §6 cross-record invariants and acceptance matrix;
- the S1 all-or-nothing candidate acceptance rule.

The current RED tests exercise only a subset of those invariants. In particular, the present test file does not prove exact 404/202/202 cardinalities on a valid full fixture, every source-row ordinal rule, every object/pair/member cross-reference, all OHLCV/parser constraints, full acquisition-attempt history, or the entire S1 acceptance matrix. These remain **NOT VERIFIED** until separately covered by synthetic tests and execution under a future, separately approved scope.

The interface freeze does not resolve the still-open SQLite STRICT runtime, compression/disk-reserve limits, retention, archive header-mode evidence, or SQLite-safe successful-attempt relationship. Those remain independent gates.

## 10. Versioning and change control

- Interface identifier: `T0_PROVENANCE_VALIDATOR_INTERFACE_V1`.
- Module name and the three public function names are frozen for V1.
- The result DTO fields/types, T0ENC1 behavior, attempt-ID preimage, error-code spelling/meaning, and deterministic ordering are frozen for V1.
- Adding, removing, renaming or changing the meaning of a V1 error code; changing the result DTO; changing payload semantics; or changing digest framing requires an explicit owner-approved amendment or a new interface version before implementation.
- No undocumented compatibility aliases or silent coercions.

## 11. Status and authorization

| Item | Status |
|---|---|
| Interface design and result DTO | **FROZEN — DESIGN ONLY** |
| V1 error-code catalogue | **FROZEN — DESIGN ONLY** |
| Error aggregation/order | **FROZEN — DESIGN ONLY** |
| Input and side-effect boundary | **FROZEN — DESIGN ONLY** |
| Existing 12 RED test source | **UNCHANGED** |
| RED assertions executed | **NOT VERIFIED** (module absent; all prior errors occurred in setUp) |
| GREEN validator implementation | **NOT AUTHORIZED** |
| Additional synthetic coverage | **NOT AUTHORIZED by this decision** |
| DDL / SQLite / importer / archive / workflow | **NOT AUTHORIZED** |
| Canonical T0 / MAY-10 / REST tail / VPS / T1 / T2 / deployment / trading | **EXCLUDED / NOT AUTHORIZED** |

Owner approval recorded for this increment: documentation-only Validator Interface Contract design and freeze. Any implementation or scope expansion requires separate approval.
