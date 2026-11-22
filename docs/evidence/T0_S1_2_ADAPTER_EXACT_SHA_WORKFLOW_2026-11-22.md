# T0 S1.2 Adapter — Exact-SHA GitHub Actions Verification

Date: 2026-11-22
Repository: kenznguyen/btcquant-application
Branch: main

## Workflow run

- Workflow: T0 importer-core synthetic TDD
- Run: [45000330203](https://github.com/kenznguyen/btcquant-application/actions/runs/45000330203)
- Run attempt: 1
- Event: push
- Branch: main
- Run conclusion: SUCCESS
- Job: Importer-core synthetic tests
- Job ID: 137140241389
- Job URL: https://github.com/kenznguyen/btcquant-application/actions/runs/45000330203/job/137140241389
- Job conclusion: SUCCESS
- Started: 2026-11-22T07:54:26Z
- Completed: 2026-11-22T07:54:51Z

## Exact source verification

- Workflow run head SHA: `cd0c54e9b9cb579685e9a8d262a3a166afdf9df1`
- Job head SHA: `cd0c54e9b9cb579685e9a8d262a3a166afdf9df1`
- Intended source SHA: `cd0c54e9b9cb579685e9a8d262a3a166afdf9df1`
- Exact-SHA validation step: completed / success
- Checkout exact source SHA step: completed / success
- Verify exact checked-out SHA step: completed / success
- Source commit message: `fix(t0): correct adapter digest regex anchors`
- Source commit parent: `374c39ae0c97f42e02a9f221b3ed7356d0cfccd3`
- Adapter source blob: `9d61bb36cfb2ff80c0a1b303e52f34d8d44d2b28`
- Adapter test blob: `271e465825ededd3042abc35cd6dc8c451aa07a3`
- Workflow blob: `2af6aa2eb0e852d97f5ae1614cf4731f2b7d3166`

## Test execution steps

All three test steps completed successfully:

1. Focused synthetic importer-core tests — SUCCESS.
2. Focused synthetic S1.2 adapter tests — SUCCESS.
3. Complete `market_data` regression suite — SUCCESS.

Runtime setup also succeeded: Python 3.13 for focused suites; Python 3.12.16 for full regression; committed hash-locked test dependencies installed successfully.

The GitHub Actions run/job metadata exposed successful step conclusions but not the step log bodies. Therefore exact numeric test counts and detailed unittest output are **NOT VERIFIED from the available run metadata**. No test count is inferred or invented.

## Artifact

- Workflow artifacts endpoint returned `total_count: 0`.
- Artifact ID, checksum and downloadable test-log artifact: NOT AVAILABLE.
- This workflow run did not publish a downloadable artifact.

## Status

- Exact-SHA workflow run: **PASS**.
- Exact checkout verification: **PASS**.
- Focused importer-core test command: **SUCCESS**.
- Focused S1.2 adapter test command: **SUCCESS**.
- Full `market_data` regression command: **SUCCESS**.
- Numeric test counts / detailed log inspection: **NOT VERIFIED**.
- Artifact evidence: **NOT AVAILABLE**.
- SQLite staging schema and disposable SQLite tests: **NOT STARTED**.
- Real archive validation/build, Canonical T0, B8 acquisition runner, T1/T2 runtime, VPS/deployment, credentials, exchange/trading, upload, cleanup/deletion: **NOT AUTHORIZED**.

## Next step

Proceed only within the already approved synthetic-only scope: design and implement the SQLite staging schema module using disposable synthetic fixtures, with TDD and in-memory/temp databases only. Preserve all exclusions above. S1.2 is not frozen until the revised physical schema, adapter invariants and independent review are complete.
