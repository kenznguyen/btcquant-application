# T0 Real Archive CSV Sample Verification Workflow — Implementation Record

Date: 2026-11-21

## Scope

Created exactly one manually dispatched GitHub Actions workflow:
`.github/workflows/t0-real-archive-csv-sample-verification.yml`

Owner approval record: `docs/decisions/T0_REAL_ARCHIVE_CSV_SAMPLE_VERIFICATION_WORKFLOW_APPROVAL_2026-11-21.md`, commit `02b407fe7d90efe184ae11d8b271a7aeb6e23f96`.

The workflow:
- Has only the `workflow_dispatch` trigger.
- Uses GitHub-hosted `ubuntu-24.04`, read-only `contents: read`, no secrets and no persisted checkout credentials.
- Pins the six ZIP keys, expected byte sizes, SHA-256 values and row counts from inventory blob `eb251ac0924b46add906123f99b82e054d887a59`.
- Fetches only those six ZIPs and their six exact paired `.CHECKSUM` sidecars from `https://data.binance.vision/`.
- Verifies ZIP byte size/SHA-256, sidecar asserted digest and own size/SHA-256, ZIP CRC, one safe CSV member, UTF-8/BOM, newline convention, header absence, comma delimiter, 12 columns, row count and complete parse using parser blob `7d59706778a98a18185e0b2fe744c3c43c2eb870`.
- Runs the existing parser unit test module pinned by blob `50199cd168fd52314a846760cc4baf51a8cd5e9a`.
- Uploads only a diagnostic JSON report (14-day retention); raw ZIP/sidecar/CSV payloads are not uploaded.

## Source and Git evidence

- Repository: `kenznguyen/btcquant-application`
- Branch: `main`
- Workflow creation commit: `d96f5b402ae46d529ad46429a8b760b73c66bde6`
- Workflow correction commit: `bcae66f9f30dff4eacc742a210fda265c11d7378`
- Final workflow approval-pin commit: `b5bd4f7f1f6fb48c5310281a7796c9a5a80ec0b2`
- Final workflow blob: `44f83168908c7b4c8f7b67383e4cbfaea34b0c09`
- Approval source commit pinned by workflow: `02b407fe7d90efe184ae11d8b271a7aeb6e23f96`
- Approved sample inventory blob: `eb251ac0924b46add906123f99b82e054d887a59`

## Verification status

- Workflow file existence and final blob: PASS (verified from GitHub).
- Static scope review: PASS — one workflow, one trigger, exact 12-object allowlist, no SQLite/importer/REST-tail/Canonical T0 operations, no raw-source artifact upload.
- YAML/actionlint validation: NOT RUN.
- Workflow dispatch: NOT RUN by design in this step.
- GitHub Actions run ID/job/artifact: NOT AVAILABLE — no run was started.
- Real archive retrieval and CSV compatibility: NOT VERIFIED.
- Parser contract freeze/importer: BLOCKED pending a manually dispatched run, evidence review and a separate owner decision.

## Safety boundaries

No archive or REST request was made. No SQLite/database was created or changed. No importer, Contract 1.2.0 implementation, Canonical T0, T1/T2, VPS/runtime, deployment, exchange credentials or trading behavior was touched.

## Next step

Owner may separately authorize one manual dispatch of this workflow. Review the resulting 12-object report before deciding whether the provisional parser contract should be amended or frozen. The workflow does not itself authorize importer or staging work.


## Dispatch attempt 1 — 2026-11-21

- Workflow run: [44922866259](https://github.com/kenznguyen/btcquant-application/actions/runs/44922866259)
- Event: `workflow_dispatch`; run number: 1; attempt: 1.
- Source SHA: `69c29e6a29c2d46e465465b15394a4122df4505d`.
- Job: `136902479488`; conclusion: **FAILURE**.
- Runner: GitHub-hosted `ubuntu-24.04`, Python 3.13.18 successfully installed.
- Failure step: `Set up Python`; exact error: `Caching for 'false' is not supported`.
- Root cause: workflow passes `cache: "false"` to `actions/setup-python`; this action does not accept the string `false` as a cache mode. Remove the `cache` input (or use a supported cache value) in a separately approved workflow correction.
- Checkout and Python installation completed. Archive verification, parser unit tests and artifact upload were skipped.
- Artifacts: none.
- Source requests: **NOT MADE**; the failure occurred before the archive-verification step.
- 12-object verification: **NOT VERIFIED**.
- CSV format compatibility: **NOT VERIFIED**.
- Parser contract freeze: **BLOCKED**.
- SQLite/importer/Canonical T0: untouched.
- This was the single approved dispatch. Do not rerun or dispatch a corrected workflow without separate owner approval. A workflow correction is also a separate change requiring approval before a second run.


## Approved workflow correction — 2026-11-21

- Owner explicitly approved removal of the invalid `cache: "false"` input and one second dispatch.
- Changed only `.github/workflows/t0-real-archive-csv-sample-verification.yml`: removed that single input from the existing `actions/setup-python` step. No other workflow line changed.
- Workflow correction commit: `c4c01ec96395ee204a311b29b5cd9c198038ff6e`; workflow blob: `0812cae7389eb5d328a200a4b590cd99bc195ef7`.
- Static correction check: **PASS** — exactly one invalid input removed; remaining workflow content byte-for-byte unchanged apart from that line.
- Second dispatch: **APPROVED, NOT YET DISPATCHED**. The available GitHub connection exposes GET/read operations and rerun operations, but no new workflow_dispatch action. Rerunning the failed prior job would use the old source SHA and would not apply this correction; it is not an acceptable substitute.
- Required dispatch target: corrected workflow commit `c4c01ec96395ee204a311b29b5cd9c198038ff6e` (or a descendant with the same workflow blob). Use the Actions page and click **Run workflow** once on `main`.
- Until a second run completes, 12-object verification and real CSV compatibility remain **NOT VERIFIED**; parser contract freeze remains **BLOCKED**. No archive requests have been made by this corrected workflow yet.
- All previous exclusions remain: exactly six ZIPs + six sidecars only; no REST, full 404-object materialization, SQLite, importer, Contract 1.2.0 freeze, Canonical T0, T1/T2, VPS/runtime, deployment, credentials or trading. No third dispatch is authorized.


## Second approved dispatch — 2026-11-21

- Workflow run: [44923263069](https://github.com/kenznguyen/btcquant-application/actions/runs/44923263069)
- Run number: 2; event: `workflow_dispatch`; attempt: 1; conclusion: **FAILURE**.
- Exact source SHA checked out: `2410f87f8917bd0d615b50e8393ad6aa7f15183f`.
- Job: `136903674953`; runner: `ubuntu-24.04`; Python 3.13.18 setup: **PASS**.
- Failure step: `Verify exact source pins and run real archive checks`.
- Exact error: `fatal: Not a valid commit name 02b407fe7d90efe184ae11d8b271a7aeb6e23f96`.
- Cause: checkout uses `fetch-depth: 1`; the approval source commit `02b407fe7d90efe184ae11d8b271a7aeb6e23f96` is not present in the shallow checkout. The subsequent `git merge-base --is-ancestor "$APPROVAL_SOURCE_SHA" HEAD` cannot resolve that commit.
- No archive download occurred: failure was before the first `curl` call. Parser unit tests and artifact upload were skipped. Artifacts: none.
- 12-object verification: **NOT VERIFIED**. Real archive CSV compatibility: **NOT VERIFIED**. Parser contract freeze: **BLOCKED**.
- This run consumed the separately approved second dispatch. The approval covered only removal of invalid `cache: "false"` and one second dispatch; it did not authorize further workflow changes or a third dispatch.
- A narrowly scoped next correction would need to make the approved ancestor commit available to the ancestry check (e.g. explicitly fetch that exact SHA before `merge-base`, or use sufficient checkout history). This is a proposal only, not implemented or authorized.
- No SQLite, importer, Contract 1.2.0 implementation/freeze, Canonical T0, REST tail, T1/T2, VPS/runtime, deployment, exchange credentials or trading was changed or invoked.


## Third dispatch authorization and ancestry correction — 2026-11-21

- Owner explicitly approved both (1) the narrowly scoped ancestry-check correction and (2) one third workflow dispatch.
- Run 2 failure root cause: `actions/checkout` default shallow history (`fetch-depth: 1`) did not contain approval commit `02b407fe7d90efe184ae11d8b271a7aeb6e23f96`; `git merge-base --is-ancestor` could not resolve it.
- Correction: set `fetch-depth: 0` for the existing pinned checkout action. No other workflow logic or scope changed. This provides full Git history for the ancestry assertion; it does not retrieve additional Binance archive objects.
- Correction commit: `82c1e8c1e20d7df335936a53005d84cc1756c075`.
- Workflow blob after correction: `9edb0e4cf74c22f82c38f107c730e73abf04de44`.
- Static verification: **PASS** — latest main workflow contains exactly one `fetch-depth: 0`; setup-python has no invalid `cache: "false"`; six ZIP allowlist and all other workflow content are unchanged relative to the prior version except the single checkout depth setting.
- Third dispatch: **APPROVED / NOT DISPATCHED**. The available GitHub actions connector supports reading workflow runs and rerunning prior runs, but does not expose creating a new `workflow_dispatch` run. Rerunning run 2 would use its old source SHA and is not a valid substitute. Do not rerun it.
- Real archive requests: none from run 2. Third dispatch has not occurred. 12-object verification remains **NOT VERIFIED**; parser contract freeze remains **BLOCKED**.
- No changes to archive allowlist, object scope, REST policy, parser, inventory, SQLite/importer, Contract 1.2.0, Canonical T0, T1/T2, VPS/runtime, deployment, or trading.


## Third approved dispatch — real archive format finding (2026-11-21)

- Workflow run: [44923634320](https://github.com/kenznguyen/btcquant-application/actions/runs/44923634320); run number 3; event `workflow_dispatch`; attempt 1; conclusion **FAILURE**.
- Exact source SHA checked out: `ab2ae82c12f858492128528d52b01c4455f43083`; job `136904830969`; runner `ubuntu-24.04`; Python 3.13.18 setup **PASS**.
- The ancestry assertion now passes: checkout fetched full history, resolved source SHA and checked out the exact requested commit. The pinned inventory/parser/test blob checks also passed before archive processing.
- Failure step: `Verify exact source pins and run real archive checks`. Exact error: `unexpected CSV header row in data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2022-08.zip`.
- This proves the current workflow's universal headerless assumption is false for at least the sampled M15 monthly 2022-08 CSV. Workflow order indicates the preceding M15 daily 2019-12-31 sample passed all checks needed to proceed to the next sample; this is limited evidence for that one ZIP/sidecar pair only.
- The workflow stopped at the second ZIP. Remaining four ZIPs and their sidecars were not processed. Do not infer full 12-object verification or parser compatibility.
- Parser unit tests: **SKIPPED**. Artifact upload: **SKIPPED**. Artifacts: **none**. No diagnostic JSON report exists.
- Status: ancestry/source pin checks **PASS**; M15 2022-08 headerless contract check **FAIL**; remaining samples **NOT VERIFIED**; 12-object verification **NOT VERIFIED**; parser unit tests **SKIPPED**; parser contract freeze **BLOCKED**.
- The result identifies a real-source format discrepancy, not proof that the archive is corrupt. Do not silently strip/ignore headers or change the parser contract based on this single run.
- This run consumed the third approved dispatch. No fourth dispatch, workflow correction, parser change, parser test change, importer, SQLite/staging, Contract 1.2.0 implementation, Canonical T0, REST-tail request, T1/T2, VPS/runtime, deployment, credentials or trading action is authorized by this result.
- Next gate: record and review this evidence. Any change to accept optional headers, distinguish archive variants, or run another sample requires a separate owner decision and narrowly scoped approval.
