# T0 Phase B Revision 6 — Documentation Self-Check

- Date: 2026-11-22
- Exact design path: `docs/design/T0_PHASE_B_DETAILED_SCHEMA_AND_CANONICAL_CONTRACT_DESIGN_2026-11-22.md`
- Exact design commit: `9b69c18ea16731bf28efba7a92077e96a74107ce`
- Exact design blob SHA: `7012a228561620f4447a0e363a2c5f27d734912a`
- Base reviewed revision: Revision 5 commit `51a11272a7cc9204d2b42a255942614e36f40b6f`, blob `9aeb036267e9dfce73e0b2405c7f4c9ef27cc5ab`
- Trigger: design review R-17 HIGH in review report commit `c2360834ac7642edef5a97d34f57bafdec465a6d`.
- Scope: documentation-only correction of SD-07 capture-producer ownership/registration and proposed synthetic cases. No code or runtime work.

## Verdict

**SELF-CHECK PASS — READY FOR NEXT DESIGN REVIEW. NOT OWNER-APPROVED. NOT AN INDEPENDENT SECOND-PERSON REVIEW.**

## R-17 correction

- Both SD-07 allowlisted source kinds are explicitly owned by T1 in `kenznguyen/binance-futures-collector`: direct Binance USD-M REST response acquisition and T1 reconstructed-local-book serialization.
- Direct REST capture identity is issued by the T1 request/response component, not Binance and not T0.
- T0 remains canonical owner/ingestion and validation boundary. It validates and records registration evidence; it does not mint or replace `capture_producer_id` or `capture_sequence`.
- Candidate producer registration binds producer ID to collector/repository identity, exact source kind, exchange/market/domain and symbol scope, producer implementation/version and identity-scheme version.
- Unknown, inactive, unregistered or mismatched registration fails closed; producer registration failure is distinguished from missing exchange-native `lastUpdateId`.
- Producer namespace uniqueness, durable allocation, clone fencing and stale-state rollback protection remain unproven and unfrozen. B-07 remains OPEN.

## Synthetic matrix

- SD-05: 14 proposed cases.
- SD-06: 28 proposed cases.
- SD-07: 39 proposed cases.
- Cross-domain: 10 proposed cases.
- Total: **91 proposed cases — NOT EXECUTED**.
- Added SD-07 cases 33–39 cover registered T1 direct REST producer, registered T1 reconstructed-book producer, unknown producer, source-kind/domain/symbol mismatch, concurrent clone namespace collision, stale restored producer state/sequence reuse, and T0 mint/substitution of producer identity.
- No fixtures or test code were created; no tests were run.

## Static verification

- Revision 6 header/status present.
- T1 ownership binding is explicit for both SD-07 source kinds.
- T0 does not issue or replace producer capture identity.
- Candidate registration fields and fail-closed mismatch rules are present.
- R-15 three identity domains remain distinct.
- R-16 retry remains based on the same immutable source-delivery locator; the old ambiguous phrase `same immutable message identity` is absent.
- Matrix count reconciles: 14 + 28 + 39 + 10 = 91.
- B-01..B-20 section was compared byte-for-byte against Revision 5 before save; all 20 blocker rows remain present and unchanged.
- Static checks only; no execution tests.

## Status and exclusions

- B-01..B-20: **OPEN / unchanged**. B-07 remains OPEN pending producer namespace uniqueness, durable sequence, non-reuse/fencing and source evidence.
- Contract freeze: **NOT APPROVED**.
- Implementation, database, runtime, T1 source changes, T1→T0/T2 connectivity, VPS/deployment and Phase C: **NOT AUTHORIZED**.
- Tests/workflows/artifacts: **NOT RUN / NONE**.
- Independent second-person review: **NOT VERIFIED**.
- No code, DTO, parser, validator, fixture, test, DDL, database, data movement, network, credentials, collector activation, runtime integration, VPS/deployment or trading action occurred.

## Next step

Submit exact Revision 6 design commit/blob for design review. Preserve B-01..B-20 as OPEN and byte-identical until evidence-backed resolution or bounded owner acceptance. No implementation or Phase C without separate explicit owner approval.
