# T2 Core Adapter — self-review of parity increment — 2026-11-21

## Review identity and limitation

Review type: same-session technical self-review at the owner's request.  
This is **not** an independent second-person review and must not be represented as one.

Reviewed repository: `kenznguyen/btcquant-application`, branch `main`.  
Tested source SHA: `ca9f01902cd1e3b5f22ccecce7cd347077924f90`.

## Exact reviewed blobs

- Adapter: `core_runtime/adapter.py` — `9795c346d2eec4c78c22035c32f463af6b40b8f4`
- Original contract tests: `core_runtime/test_adapter_contract.py` — `fbe6cc428fd7058a6dbefd9eaec1979a95638474`
- Parity tests: `core_runtime/test_adapter_validator_parity.py` — `8f3c4dfa29f371334ded3486ca83f9a5ea7f974e`
- Canonical validator: `pipeline/core_signal.py` — `df5fbb59611bdd4fbb8224665f79655dd4433455`
- Shared validation primitives: `pipeline/values.py` — `5576376454af129b944919fb588e26c0657a781e`
- Focused workflow: `.github/workflows/t2-core-adapter-green.yml` — `5a5b70d244debcf8f5eb55733eef14d6e9661e38`

## Findings

### Required — CI path filter omits canonical validator dependencies

The workflow's `on.push.paths` currently includes the workflow, adapter and its two test modules, but omits:
- `pipeline/core_signal.py`
- `pipeline/values.py`

The parity tests import and exercise both omitted modules. A future change to the canonical validator or its shared numeric/timestamp/identity primitives can therefore land without triggering this focused CI workflow. This weakens the intended regression gate.

Required correction: add both paths to the workflow path filter. Keep the existing exact blob assertions for the reviewed Adapter and tests. Do not pin the validator to its current blob permanently unless the workflow is deliberately designed to require an explicit pin update whenever validator code changes. The immediate correction should be limited to triggering the job when either dependency changes.

Status: **OPEN — not changed in this review**.

### Optional — unhashable producer action raises TypeError

In `producer_report_to_signal`, `_ACTION_MAP.get(action)` raises `TypeError` when action is an unhashable value such as a list or dict, rather than the adapter's stable `ValueError("CORE_PRODUCER_ACTION_INVALID")` contract.

This does not affect ordinary JSON string actions, and the canonical validator is downstream fail-closed for adapted values. Consider a type guard and a regression test in a separate small TDD change.

Status: **OPTIONAL — not changed**.

## Positive observations

- Adapter is a pure translator: no I/O, risk admission, ledger mutation, timestamp synthesis or order execution.
- BUY/SELL/CLOSE mapping is explicit and intent action mismatch is rejected.
- Required provenance fields are checked for presence and non-empty string identity fields; the adapter does not synthesize missing provenance.
- WAIT cannot carry an intent.
- The parity tests exercise accepted BUY/SELL/CLOSE intents, non-intent WAIT, expiry rejection and wrong-symbol rejection at the canonical validator boundary.
- Workflow runs the focused tests in a pinned Python image, network-disabled container, read-only workspace, with no DB mount or exchange credentials.
- The recorded run 44896160495 succeeded with 10/10 tests at the exact tested SHA.

## Review verdict

**REQUEST CHANGES** — resolve the Required workflow path-filter finding before considering the focused CI guard complete.

This verdict is limited to the reviewed adapter/parity slice. It does not approve leverage/sizing semantics, runner, ledger, Shared Risk Engine integration, AI Strategy, T0/T1 integration, runtime, database, deployment or trading.

## Verification boundary

- GitHub Actions run: [44896160495](https://github.com/kenznguyen/btcquant-application/actions/runs/44896160495)
- Run HEAD: `ca9f01902cd1e3b5f22ccecce7cd347077924f90`
- Job: `136822153930`, success; 10/10 tests.
- Artifact: `14703678692`
- Artifact SHA-256: `1ce726534fe995a3b0061a50d35a98618213135b2f12e1e84471df88a0d37ebe`
- Full repository regression suite: **NOT RUN**.
- This self-review is not a second-person review: **INDEPENDENT REVIEW NOT VERIFIED**.

## Next step

Obtain approval for a narrowly scoped TDD fix that adds the two missing workflow path filters (and, if desired, separately hardens unhashable action handling). Then rerun the focused workflow and request a genuine second-person review of the resulting exact blobs.
