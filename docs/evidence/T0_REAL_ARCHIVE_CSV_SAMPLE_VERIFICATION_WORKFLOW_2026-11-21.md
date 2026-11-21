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
