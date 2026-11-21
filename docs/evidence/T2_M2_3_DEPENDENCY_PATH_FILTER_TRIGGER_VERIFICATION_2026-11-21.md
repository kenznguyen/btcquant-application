# T2 Core Adapter dependency-only path-filter trigger verification

Date: 2026-11-21
Repository: `kenznguyen/btcquant-application`
Branch: `main`

## Objective and bounded scope

Owner approved a controlled trigger exercise for the two dependency paths added to `.github/workflows/t2-core-adapter-green.yml`:
- `pipeline/core_signal.py`
- `pipeline/values.py`

Each probe was a comment-only change to exactly one dependency file, followed by a revert restoring its original byte-identical blob. No functional code, tests, workflow configuration, risk policy, runner, ledger, T0/T1, AI, DB, runtime, deployment or trading behavior was intentionally changed.

## Probe A — pipeline/core_signal.py

- Probe commit: `e47a34052ef80548fbff9e19c41d617023c08c17`
- Changed file: only `pipeline/core_signal.py`; comment-only.
- Probe blob: `476708d681018dc3df7a22dd820ba6515bfdec6e`
- Prior/original blob: `df5fbb59611bdd4fbb8224665f79655dd4433455`
- GitHub Actions run [44901618566](https://github.com/kenznguyen/btcquant-application/actions/runs/44901618566): **SUCCESS**, event `push`, exact HEAD `e47a34052ef80548fbff9e19c41d617023c08c17`.
- Job `core-adapter-contract`: `136838538409`, **SUCCESS**.
- Test result: **10/10 PASS**.
- Artifact ID: `14706495727`; SHA-256 `ae7d39a9533828eb3194ba3bfd04335c4cbd8cbd528b1f249c30a74e789a863f`.
- Artifact downloaded; local SHA-256 matched GitHub digest. Metadata confirms exact HEAD and 10/10 PASS.

Revert:
- Commit `b9968abc76c8d81eb23702e6592efc092a93037c`.
- Restored `pipeline/core_signal.py` blob exactly to `df5fbb59611bdd4fbb8224665f79655dd4433455`.
- T2 workflow cleanup run [44901629534](https://github.com/kenznguyen/btcquant-application/actions/runs/44901629534): **SUCCESS**.

## Probe B — pipeline/values.py

- Probe commit: `6e1a7e44d555693b38888ca70884dd29c0afb083`
- Changed file: only `pipeline/values.py`; comment-only.
- Probe blob: `50d6586fc91f3ab13942c47eca3ec352f250f166`
- Prior/original blob: `5576376454af129b944919fb588e26c0657a781e`
- GitHub Actions run [44901659062](https://github.com/kenznguyen/btcquant-application/actions/runs/44901659062): **SUCCESS**, event `push`, exact HEAD `6e1a7e44d555693b38888ca70884dd29c0afb083`.
- Job `core-adapter-contract`: `136838660363`, **SUCCESS**.
- Test result: **10/10 PASS**.
- Artifact ID: `14705134527`; SHA-256 `773aebcbb1f97663e3234b4a768f17392251b1d6c7d77ecc78049cc5030c57f1`.
- Artifact downloaded; local SHA-256 matched GitHub digest. Metadata confirms exact HEAD and 10/10 PASS.

Revert:
- Commit `50be22b5852b0908c389ce33570a9a9d1e284471`.
- Restored `pipeline/values.py` blob exactly to `5576376454af129b944919fb588e26c0657a781e`.
- T2 workflow cleanup run [44901677918](https://github.com/kenznguyen/btcquant-application/actions/runs/44901677918): **SUCCESS**.

## Adjacent F4 workflow observation

The `pipeline/values.py` push also triggered the existing F4 Pipeline API and Decision workflow. This is outside the approved T2 Adapter slice and was not modified.

- Probe run [44901659042](https://github.com/kenznguyen/btcquant-application/actions/runs/44901659042), head `6e1a7e44d555693b38888ca70884dd29c0afb083`: failed during immutable source verification before tests; the first reported pin was `pipeline/test_decision.py` expected blob `6781f26d66635f56662a627bdd3b4a63f26c1f28`. This failure is not evidence that the values path filter failed; the dedicated T2 workflow ran and passed.
- Cleanup run [44901677917](https://github.com/kenznguyen/btcquant-application/actions/runs/44901677917), head `50be22b5852b0908c389ce33570a9a9d1e284471): source identity verification passed, but F4 tests failed: 45 tests ran, 2 failures and 5 errors. Examples include missing `order` fields in API results and HTTP 400 `INVALID_INPUT` for Core/AI shared-risk tests. Job `136838719555`; artifact `14705209340`, SHA-256 `47f0864fd67ce2937c57166dff1c07198063ace26b4c30e9933f40d658c6ff68`.
- Treat F4 regression status as **BLOCKED / REQUIRES SEPARATE TRIAGE**. Do not modify F4 or application behavior under this T2 trigger-test approval.

## Final verification and verdict

- Dependency-only push to `pipeline/core_signal.py`: target workflow triggered and **PASS**.
- Dependency-only push to `pipeline/values.py`: target workflow triggered and **PASS**.
- Both T2 focused test executions: **10/10 PASS each**.
- Revert commits restored the two dependency files to their original exact blobs.
- Latest cleanup commit at this record's preparation: `50be22b5852b0908c389ce33570a9a9d1e284471`.
- The workflow path-filter behavioral finding is **CLOSED — PASS** for both dependency paths.
- Full repository regression: **NOT RUN**.
- F4 adjacent workflow: **BLOCKED** as recorded above; outside this slice.
- Independent second-person review: **NOT VERIFIED**.
- No runtime, DB, T0/T1 integration, AI admission, paper order submission, live trading or real orders were performed or authorized.

## Next

Preserve the T2 path-filter PASS and separately triage the F4 workflow failures under their own bounded scope. Do not fold F4 fixes, runtime integration or risk-policy changes into this completed trigger-verification increment.
