# T2 M2.4 — AI Strategy Signal Contract RED Evidence

Date: 2026-11-21  
Repository: `kenznguyen/btcquant-application`  
Branch: `main`  
Source repository reference: `kenznguyen/btcusdt-telegram-signals2`, branch `feature/core-operational-proof-20261112`, source HEAD `e6606e28a696374f31cd6db1ec0a1372d942d64d`

## 1. Owner approval and scope

Owner approved M2.4: AI Strategy Contract, independent of Strategy Core, with RED tests and GitHub evidence.

Completed within this increment:
- Defined target-owned AI Signal Contract V1.
- Defined the pure validation boundary `pipeline.ai_signal_contract.validate_ai_signal(report, now_ms, policy)`.
- Specified independent LONG/SHORT signal reports; no Core report/state is an input prerequisite.
- Specified WAIT/fail-closed behavior for missing calibration, invalid policy, provenance mismatch, leakage, stale/unverified evidence and expired/future reports.
- Restricted the output to a signal DTO. No order, execution intent, quantity, leverage, margin, reservation or ledger fields.
- Added 10 target-owned RED test methods and a pinned, isolated expected-RED GitHub Actions workflow.

Explicitly not done:
- No GREEN implementation of `pipeline/ai_signal_contract.py`.
- No AI model training, calibration registry implementation/signing, production confidence threshold, AI paper admission, ledger writes or Shared Risk Engine caller wiring.
- No Core strategy, leverage/sizing, risk policy or existing adapter behavior changes.
- No dependency changes, T0/T1 integration, database, VPS, runtime, deployment, exchange connection or trading.

## 2. Exact tested source and blobs

Final exact tested target source SHA: `6fa66d2855a0d0804da6cee9ed37a723bbaf03d9`

| Path | Blob SHA |
|---|---|
| `docs/architecture/AI_STRATEGY_SIGNAL_CONTRACT_V1.md` | `e5df7ec59c04a4f08b6ec0fc98e7e5702b3543dc` |
| `pipeline/test_ai_signal_contract_red.py` | `bd4c6325739a7d1eadf5ced64c71e7e4742e7a31` |
| `.github/workflows/t2-ai-signal-contract-red.yml` | `d8323caa1bc96f909219afd1028923971a247ad4` |

The contract's test-only confidence minimum fixture is `0.6`; it is not a production threshold. The policy domain is `[0, 1)`, with 1 rejected because the approved linear leverage mapping denominator would be zero.

## 3. RED result

- Test methods discovered: **10**
- Result: **10 methods executed; expected RED**
- Python unittest reported **27 errors** because subtests expand into multiple failing cases.
- Every error had the same intended cause: `ModuleNotFoundError: No module named 'pipeline.ai_signal_contract'`.
- No unrelated import/runtime error was observed in the captured test log.
- The missing module is intentional at M2.4. These failures prove that the public API is not yet implemented; they do not prove behavior is correct.

## 4. GitHub Actions and artifact

Final workflow: [T2 AI Signal Contract RED specification](https://github.com/kenznguyen/btcquant-application/actions/runs/44914696468)

- Workflow run ID: `44914696468`
- Tested SHA: `6fa66d2855a0d0804da6cee9ed37a723bbaf03d9`
- Job ID: `136877715288`
- Job conclusion: **SUCCESS** — expected-RED wrapper verified the 10-test RED result and the precise missing-module cause.
- Artifact: `t2-ai-signal-contract-red-evidence`
- Artifact ID: `14711520763`
- SHA-256: `822c74c766555c60e1f0f2c88af4f325aba8e7dafba3bd8d1b613287314018f0`
- Artifact expiry: 2026-12-05
- Environment: pinned `python:3.12.16-slim-bookworm` image; container network disabled; read-only workspace; no DB mount; no exchange credentials.

### Superseded workflow attempts

The initial runs exposed harness issues, not product behavior:
- Run `44914527542`: first workflow commit still had placeholder blob pins.
- Run `44914551057`: RED subtest cases expanded to 27 errors, while the wrapper incorrectly expected 10 error headings. The wrapper was corrected to assert 10 discovered tests and count only the expected missing-module exception.
- Run `44914692589`: documentation threshold correction had landed before the workflow blob pin was updated; exact-source pin verification correctly failed.
- Final run `44914696468`: updated document pin, RED verification and artifact upload all succeeded.

Do not use the superseded runs as passing evidence.

## 5. Review and disposition

- Same-session self-review: completed; confidence threshold domain corrected to `[0, 1)`.
- Genuine independent second-person review: **NOT VERIFIED**.
- M2.4 status: **PASS — contract and expected RED specification recorded**.
- AI Signal GREEN implementation: **NOT IMPLEMENTED / NOT AUTHORIZED by M2.4**.
- Full repository regression: **NOT RUN**.
- Core leverage/sizing conflict: remains separately blocked; unchanged.
- T0/T1, data ownership, runtime, DB and execution posture: unchanged.

## 6. Next permitted step

Request a separate owner approval for M2.5 GREEN implementation of the pure AI signal-contract validator against these exact tests. Keep calibration cryptographic verification, Shared Risk Engine admission, AI ledger, runner, runtime and paper/live execution outside M2.5 unless separately approved.
