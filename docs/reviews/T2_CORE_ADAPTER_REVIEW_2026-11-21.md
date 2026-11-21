# T2 Core Adapter Review — 2026-11-21

## Review scope and provenance

Target repository: `kenznguyen/btcquant-application`  
Branch: `main`  
Reviewed target HEAD: `ec9ec22745c8e9404190d051e47f3c5d6be2ff66`  
Pinned source repository: `kenznguyen/btcusdt-telegram-signals2`  
Pinned source HEAD: `e6606e28a696374f31cd6db1ec0a1372d942d64d`

Reviewed files:
- `core_runtime/adapter.py`, blob `9795c346d2eec4c78c22035c32f463af6b40b8f4`
- `core_runtime/test_adapter_contract.py`, blob `fbe6cc428fd7058a6dbefd9eaec1979a95638474`
- `pipeline/core_signal.py`, blob `df5fbb59611bdd4fbb8224665f79655dd4433455`
- `pipeline/test_core_signal.py`, current target version
- `.github/workflows/t2-core-adapter-green.yml`

Review axes: correctness, readability, architecture, security, performance, and verification evidence.

## Findings

### Required — Add an adapter-to-validator parity test

The six adapter tests exercise the adapter in isolation. They do not prove that the adapter's output is accepted by the target's canonical `pipeline.core_signal.validate` boundary.

The intended flow is:
1. Strategy Core producer report (`BUY/SELL/CLOSE/WAIT`, nested intent with `LONG/SHORT/FLAT`).
2. `producer_report_to_signal` translates it into the top-level `LONG/SHORT/FLAT/WAIT` shape.
3. `pipeline.core_signal.validate(report, now_ms)` performs market, provenance, timestamp, direction, price and target validation and creates the canonical PAPER intent.

The adapter test fixtures resemble the producer contract, but no test composes steps 2 and 3. This leaves the most important module-boundary assumption unverified.

Required remediation:
- Add deterministic tests that build a producer-shaped BUY, SELL, CLOSE and WAIT report, adapt it, and pass the result into `pipeline.core_signal.validate` with a fixed `now_ms`.
- Assert the expected BUY/SELL/CLOSE/WAIT result, canonical intent presence/absence, market identity and provenance preservation.
- Include malformed and expired values to prove the downstream validator remains the fail-closed authority.
- Do not change `pipeline.core_signal.py` semantics or add risk/ledger behavior in this remediation.

### Optional — Normalize malformed unhashable action input

In `producer_report_to_signal`, `_ACTION_MAP.get(action)` raises `TypeError` when a malformed Mapping contains an unhashable action value such as a list or dict. The function otherwise uses stable `ValueError` contract codes for invalid producer input.

Suggested remediation:
- Check that action is a string before dictionary lookup, and raise `ValueError("CORE_PRODUCER_ACTION_INVALID")` otherwise.
- Add one regression test for an unhashable action value.

This does not affect normal producer output, which emits string action constants.

## Five-axis assessment

- Correctness: Core mapping and required provenance-field copying match the pinned producer contract. The downstream validator is the canonical semantic gate, but adapter-to-validator composition is not yet tested.
- Readability: Small, pure function with clear mapping and explicit error codes.
- Architecture: Appropriate separation; adapter does not import or duplicate the canonical validator and does not perform risk admission or persistence.
- Security: No I/O, network, credentials, dynamic execution or dependency addition. Treats the report as untrusted structured input; malformed action edge case noted above.
- Performance: Constant-time field checks and small dictionary construction; no material performance concern.
- Verification: Prior exact-blob isolated GREEN run passed 6/6 tests, but it does not cover the adapter/validator boundary.

## Verification evidence reviewed

- RED workflow: [44895676994](https://github.com/kenznguyen/btcquant-application/actions/runs/44895676994), expected missing-module RED.
- GREEN workflow: [44895903601](https://github.com/kenznguyen/btcquant-application/actions/runs/44895903601), 6/6 adapter-only tests PASS.
- GREEN artifact: `14703892144`, SHA-256 `c6a716385cc485936d5e9e539b2f30d214756edd4872253cb6abb1ab0c261664`.

No new tests were run as part of this read-only review. No source, test, workflow, dependency, database or runtime state was changed.

## Verdict

**REQUEST CHANGES — boundary parity test required before accepting the adapter slice as review-complete.**

This document records a technical review performed in this ChatGPT session. It is **not evidence of a genuine independent second-person GitHub review**: no distinct reviewer identity was supplied or available to attest to a second-person review. Therefore the project's independent-review gate remains **NOT VERIFIED** until a reviewer distinct from the implementation author reviews the exact source/test blobs and records an explicit verdict.

## Next step and limits

- Add the required adapter-to-validator parity tests in a separately bounded TDD increment, only after owner approval.
- Consider the optional malformed-action hardening in the same bounded test-first increment if approved.
- Obtain genuine second-person review after the fixes and exact-SHA CI.
- No changes to Core leverage/sizing semantics, Shared Risk Engine, ledgers, runner, AI Strategy, T0/T1 integration, runtime, database, deployment or trading are authorized by this review.
