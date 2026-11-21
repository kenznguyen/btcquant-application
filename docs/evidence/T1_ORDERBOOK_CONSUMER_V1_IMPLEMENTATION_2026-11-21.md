# T1 Orderbook Consumer Contract V1 — Implementation Evidence

Date: 2026-11-21  
Repository: `kenznguyen/btcquant-application`  
Branch: `main`  
Status: **CONSUMER IMPLEMENTATION PASS / PRODUCER COMPATIBILITY BLOCKED / RUNTIME NOT AUTHORIZED**

## 1. Approved scope

Owner approval covered implementation of the Application-owned T1 Orderbook V1 DTO, strict consumer validator, deterministic synthetic fixtures, and transport-neutral adapter boundary, plus isolated tests. It did not authorize T1 producer changes, provider activation, transport implementation, T1 → T2 runtime connection, T0 access, VPS/exchange access, or trading.

## 2. Implemented files

| File | Responsibility | Blob SHA |
|---|---|---|
| `market_data/t1_orderbook/__init__.py` | Public consumer package exports | `afa2951b1ec138fccbfaca61f3e4c24643957025` |
| `market_data/t1_orderbook/errors.py` | Stable typed rejection codes | `5f6bf5a5b23f21c11c26015cef35b76ced5e0f43` |
| `market_data/t1_orderbook/contract.py` | Frozen immutable DTO; decimal strings preserved | `ecf63e232eec31ec10a9c832bd724d2fbdf7af54` |
| `market_data/t1_orderbook/fixtures.py` | Deterministic synthetic fixture builder and canonical JSON bytes | `9d54016bbd0659e7c11418631b011db73c3a4238` |
| `market_data/t1_orderbook/validation.py` | Bounded strict JSON/schema/decimal/book/sequence/freshness/digest validation | `2cf2418e0738330c5e3ea6854f73c578de9cbb94` |
| `market_data/t1_orderbook/adapter.py` | Pure transport-neutral validated/unavailable/rejected result | `dd67fbdd12b63ac95856fa97128be675c694bfb1` |
| `market_data/test_t1_orderbook_contract.py` | 43 focused consumer acceptance tests | `e043c98a21be4ed311c210f59477cc58972c34d2` |
| `.github/workflows/t1-orderbook-consumer-contract.yml` | Isolated offline CI gate; includes adjacent T0 validator regression | `78bdd95c8db97a76021a3a9ffc202c571d133ce8` |

No third-party dependencies were added. The consumer accepts bytes only, caps payload size at 65,536 bytes, rejects duplicate/unknown/missing fields, uses exact decimal strings and arbitrary-precision Decimal comparisons, verifies the canonical SHA-256 snapshot digest, and returns a frozen DTO only after all checks pass. The digest is explicitly not treated as authentication or producer provenance.

The adapter does not perform HTTP, socket, retry, cache, clock, scheduler, or background work. The caller supplies one fixed `now_ms`. Missing payload returns `Unavailable`; invalid payload returns typed `Rejected`. No T0 import or fallback exists.

## 3. TDD and CI evidence

- RED test-first commit: `4c4c304d61ad48e6f9d4365d8f258994b979cb54`.
- Initial RED workflow run: [44849764243](https://github.com/kenznguyen/btcquant-application/actions/runs/44849764243), exact test-first SHA `4b7f9326a6bf1c8d658a0a0c0c87ae683a9db877`; failed as expected because the consumer module did not yet exist (`ModuleNotFoundError`).
- Final implementation/test source SHA: `3d85f19e36807f3b7eed1eb8a9057b4a77173a6d`.
- Final CI run: [44850261269](https://github.com/kenznguyen/btcquant-application/actions/runs/44850261269), workflow `T1 Orderbook Consumer Contract V1`, job `136679697952`, conclusion **SUCCESS**.
- Test result: **53/53 PASS** — 43 T1 consumer tests plus 10 adjacent offline T0 REST-tail validator regression tests; runtime 0.014 seconds.
- Test container: immutable CPython 3.12.16 image, network disabled, read-only workspace, no credentials, no provider process, no T0 database/data mounted.
- Artifact: `t1-orderbook-consumer-contract-evidence`, ID `14684123969`, SHA-256 `d160586bbaff3187ffdfdfa6d4bb0a27c64e1924e09202b537b647281e6d2e6b`, [run artifact](https://github.com/kenznguyen/btcquant-application/actions/runs/44850261269/artifacts/14684123969).

## 4. Acceptance coverage and deferred gates

Implemented and passed: exact V1 schema/key sets; duplicate/malformed/truncated/oversized/deeply nested JSON rejection; unsigned integer and type checks; canonical decimal grammar; exact decimal preservation and ordering; bid/ask depth, spread and price ordering; sequence watermark and generation invariants; freshness/future-time checks against caller-supplied evaluation time; canonical digest golden vector and digest-mismatch rejection; immutable DTO; typed unavailable/rejected adapter outcomes; offline adapter boundary; synthetic fixture provenance marker.

One producer-dependent acceptance case remains deliberately **BLOCKED**: initial REST snapshot/WebSocket bridge boundary. The T1 producer contract and publisher validator disagree on whether `firstAppliedU <= snapshotLastUpdateId` is valid. No consumer test was written to bless either interpretation. Reconcile T1's producer contract, publisher validation, and Binance bridge semantics before resuming Provider work.

The consumer cannot independently prove the full intervening `pu` event chain or that `sourceTimestampMs` and `observedAtMs` belong to the same diff. It relies on producer-side evidence behind `continuity=VERIFIED`. The existing T1 producer still has known gaps in exact decimal preservation (`f64` storage), snapshot metadata retention, strict post-reconnect continuity, and receipt timestamp provenance.

Transport authentication, TLS/token policy, endpoint, retries, provider readiness/lifecycle and deployment are not implemented. The SHA-256 field is integrity-only, not authentication.

## 5. Review and disposition

Author self-review across correctness, readability, architecture, security and performance found no additional required change within this bounded consumer-only scope. An independent review has **NOT BEEN PERFORMED** and remains a separate quality gate if required.

- Consumer DTO/validator/fixtures/adapter: **PASS** for the tested V1 contract subset.
- Focused acceptance and adjacent T0 regression: **PASS (53/53)**.
- Bridge-boundary compatibility: **BLOCKED**.
- Producer compatibility: **BLOCKED**.
- HTTP/transport/provider runtime: **NOT IMPLEMENTED / PAUSED**.
- T1 → T2 runtime and strategy feature activation: **NOT APPROVED**.
- Production readiness: **NOT VERIFIED**.

No T1 source, T0 data asset, canonical database, VPS, exchange, credentials, runtime, deployment, strategy, or execution path was accessed or modified. No real orders were possible or attempted.
