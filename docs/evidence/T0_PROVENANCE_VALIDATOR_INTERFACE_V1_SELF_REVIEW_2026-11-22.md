# T0 Provenance Validator Interface V1 — Self-Review

Date: 2026-11-22
Repository: kenznguyen/btcquant-application
Branch: main
Status: **REVIEW COMPLETE — READ-ONLY; GREEN NOT AUTHORIZED**

## Sources and exact blobs reviewed

- Interface: `docs/design/T0_PROVENANCE_VALIDATOR_INTERFACE_V1_2026-11-22.md`, blob `632eb6d38461ea3c65638ca073abc5fe4ae98729`.
- RED tests: `market_data/test_archive_provenance_validator_red.py`, blob `abbaeab16f026757923c679330f124a3d99e0774`.
- S1 amended design: `docs/design/T0_ARCHIVE_STAGING_S1_PROVENANCE_SCHEMA_FREEZE_2026-11-22.md`, blob `af7c90af0f0bcfa8d0b2143578222619af620197`.
- S2 execution evidence: `docs/evidence/T0_S2_SYNTHETIC_PROVENANCE_VALIDATOR_RED_2026-11-22.md`, blob `5a66bdf605d882a0ad8716d89f6b00ea533ce0d5`.

## Review result

The public module/function names, result DTO shape, T0ENC1 framing, attempt-ID preimage, no-side-effect boundary, and the nine error-code spellings used by RED source are consistent with the tests and S1 design. The additional `PROVENANCE_INPUT_SHAPE_INVALID` code is a reasonable interface-level rule but has no corresponding RED assertion.

### Error-code crosswalk

| Interface V1 code | RED test | Review |
|---|---|---|
| `PROVENANCE_INPUT_SHAPE_INVALID` | None | Additional contract; NOT TESTED |
| `INVENTORY_OBJECT_SET_INCOMPLETE` | `test_missing_inventory_objects_fail_closed` | Aligned |
| `OBJECT_NOT_IN_APPROVED_INVENTORY` | `test_object_requested_key_must_match_allowlisted_key` | Aligned |
| `QUARANTINED_EVIDENCE_PRESENT` | `test_quarantined_object_can_preserve_incomplete_measurements` | Aligned |
| `ATTEMPT_OUTCOME_UNKNOWN` | `test_unknown_attempt_is_not_a_successful_transfer` | Aligned |
| `TRANSFERRED_ATTEMPT_INCOMPLETE` | `test_transferred_attempt_requires_complete_object_digest` | Aligned |
| `VERIFIED_PAIR_MEMBER_CARDINALITY_INVALID` | `test_verified_pair_requires_exactly_one_verified_csv_member` | Aligned |
| `ACCEPTED_SOURCE_ROW_LINK_CARDINALITY_INVALID` | `test_accepted_source_row_requires_matching_provenance_link` | Aligned |
| `CANDLE_IDENTITY_VALUE_CONFLICT` | `test_conflicting_values_for_one_candle_identity_quarantine` | Aligned at value-ID level only |
| `CANDLE_AVAILABILITY_BOUNDARY_INVALID` | `test_bar_close_boundary_uses_exclusive_interval_end` | Aligned |

Nine catalogue codes have direct RED assertions; one is not tested. The other three of the 12 tests cover T0ENC1 framing/NULL distinction and attempt-ID determinism/domain separation.

## Findings and limitations

1. **RED execution is not assertion execution.** The recorded run is 12 tests / 12 errors in `setUp()` due to the absent validator module. No business assertion ran. This review does not upgrade any invariant to VERIFIED.
2. **Fixtures are deliberately incomplete.** Most validator fixtures use an empty inventory, which conflicts with the exact 404-object inventory rule. Their assertions use `assertIn`, so they require the target error to be present but do not establish the complete error set or exact ordering.
3. **Error aggregation/order is untested.** No RED case asserts deduplication, multi-code aggregation, catalogue ordering, or permutation invariance.
4. **Input-shape code is untested.** No test covers non-mapping payloads, missing top-level keys, wrong collection containers, or non-mapping collection items.
5. **T0ENC1 coverage is narrow.** Current tests cover prefix, field-boundary separation and NULL-vs-empty only; not integer canonicalization, bool rejection, invalid types/UTF-8, length/count bounds, or exact byte vectors.
6. **Attempt-ID coverage is narrow.** Current test covers determinism, output format and attempt-number separation; it does not test every argument's domain separation, invalid arguments, signed-64-bit boundaries, or a fixed expected digest vector.
7. **Candle conflict coverage is partial.** The fixture supplies two different `candle_value_id` values for one natural key but not the complete normalized value tuples; it does not prove digest recomputation or tuple-to-digest consistency.
8. **S1 coverage remains broader than the 12 tests.** Exact inventory cardinalities, all object/pair/member cross-references, source-row ordinals and raw digests, parser/OHLCV constraints, complete attempt history, all acceptance-matrix cases and all cross-record invariants remain NOT VERIFIED.
9. **Immutability and purity are contract requirements, not test-proven.** No test currently verifies payload non-mutation, immutable DTO behavior, or absence of I/O/environment/clock/random dependencies.

No blocking contradiction was found between the frozen interface and the 12 test source cases. The above are coverage gaps and implementation-acceptance risks, not permission to weaken S1 semantics.

## Proposed GREEN scope — requires separate owner approval

**Recommended bounded increment: implement the frozen V1 Python interface only.**

In scope:
- Add only `market_data/archive_provenance_validator.py`.
- Implement the frozen immutable `ProvenanceValidationResult` DTO.
- Implement exactly `encode_t0enc1`, `derive_attempt_id`, and `validate_provenance` per Interface V1 and S1.
- Implement the 10 frozen error codes, deduplicated aggregation and catalogue order.
- Keep all functions deterministic, side-effect-free and non-mutating.
- Add focused synthetic unit tests for the contract gaps listed above, including malformed input shape, aggregation/order, encoder type/boundary vectors, attempt-ID invalid inputs and candle normalized-value consistency. Keep tests synthetic-only.

Out of scope:
- No edits to existing 12 RED tests unless separately approved.
- No DDL, SQLite, importer, archive retrieval, workflow, network, filesystem, exchange or environment access.
- No Canonical T0, MAY-10, REST tail, VPS/runtime, T1/T2, deployment, cleanup/deletion or trading.
- No claim that the complete S1 acceptance matrix is proven by this bounded GREEN increment.

Acceptance gates proposed:
1. Existing 12 RED tests execute their test bodies and pass.
2. New synthetic contract tests pass.
3. Targeted module tests and full repository regression are run and recorded separately; if full regression cannot be run, mark NOT VERIFIED.
4. Independent review of implementation and evidence before any later phase.
5. Exact source SHA, workflow run/job/artifact (or NONE), test command/results, PASS/BLOCKED/NOT VERIFIED, and exclusions recorded on the current branch.

## Disposition

- Interface V1 document review: **PASS WITH COVERAGE LIMITATIONS**.
- Nine tested code names cross-check: **SOURCE-ALIGNED; ASSERTIONS NOT EXECUTED**.
- Input-shape code: **NOT TESTED**.
- Existing RED runtime: **12 errors at setUp; business assertions NOT VERIFIED**.
- GREEN implementation: **NOT AUTHORIZED — awaiting separate owner approval**.
- Repository/runtime/data state: **unchanged by this review**.
- Workflow run/job/artifact for this review: **NONE**.
