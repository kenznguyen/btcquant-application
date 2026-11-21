# T0 Archive Header Schema — Approved Source Evidence Audit

**Date:** 2026-11-21  
**Status:** BLOCKED — exact header schema not recoverable from retained approved evidence  
**Scope:** Read-only audit of the approved third workflow run and current repository records  
**Implementation / archive retrieval / dispatch:** NOT PERFORMED

## 1. Question

Can the exact 12 header labels and their order be verified from the already-approved source sample, sufficiently to freeze the optional-header parser contract?

## 2. Approved sample reference

- Workflow run: [44923634320](https://github.com/kenznguyen/btcquant-application/actions/runs/44923634320)
- Source SHA: `ab2ae82c12f858492128528d52b01c4455f43083`
- Job: `136904830969`
- ZIP that triggered the failure: `data/futures/um/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2022-08.zip`
- Workflow blob at that source: `9edb0e4cf74c22f82c38f107c730e73abf04de44`

## 3. What the retained evidence proves

The downloaded job log shows that:
- ZIP and sidecar retrieval/integrity checks were reached for the first two samples in sequence.
- The workflow parsed the CSV member into records and confirmed 12 fields per row before the header check.
- The workflow then checked only whether the first field of the first record, after trim/lowercase, was `open_time` or `open time`.
- For the 2022-08 M15 monthly object, that condition was true and the workflow exited with `unexpected CSV header row`.
- The log contains the workflow source code and error message, but does **not** print the CSV header record or its 12 field values.
- No artifact was created. The report-writing step was after the failing check, so no diagnostic JSON report exists.
- The workflow uses a temporary directory and the run has ended; no retained CSV member or extracted sample is available through the run artifacts.

The run therefore proves a header-like first field and 12 columns, but does not prove the exact names/order of all 12 header fields.

## 4. Repository evidence audit

The pinned parser is headerless-only and has no canonical header tuple. The pinned parser tests contain a synthetic rejection test with a hand-authored header-like first row, not a real Binance source header. The verification workflow contains a one-cell heuristic and does not log the raw first record. The inventory records object metadata and hashes, not CSV member contents or header labels.

No repository evidence inspected in this audit provides a retained real-source header record.

## 5. Conclusion

**Exact schema: NOT VERIFIED. Header contract freeze: BLOCKED.**

It would be unsafe to infer the remaining 11 labels from the known Binance Kline semantic mapping, because the requirement is to verify the exact source header and order from the approved source sample. A one-field detection condition is not a source schema record.

Do not fabricate or assume a tuple such as `open_time, open, high, low, close, volume, close_time, ...` and call it verified. Do not add aliases, case folding or whitespace normalization without a retained source record and separate contract decision.

## 6. Required next evidence

To complete verification, an owner-approved, narrowly scoped operation must preserve the exact first CSV record from the already allowlisted M15 monthly 2022-08 ZIP, alongside:
- exact ZIP object key, expected size and SHA-256;
- paired sidecar validation result;
- ZIP member name and member SHA-256;
- CSV encoding/BOM, delimiter and newline metadata;
- exact first record as 12 parsed fields, with order preserved;
- a confirmation that the record is the header and not a data row.

This can be achieved by a narrowly scoped one-object sample inspection that emits only the header metadata/record into a diagnostic artifact and does not retain the full CSV or ZIP. However, the prior three-dispatch approval is consumed; this audit does not authorize another archive request or workflow dispatch. Obtain separate explicit approval for the exact retrieval/inspection mechanism before proceeding.

After exact source labels are verified, propose a frozen header tuple and normalization policy for owner review. Only after that separate contract approval should TDD implementation be requested.

## 7. Explicit non-actions

- No Binance/archive/REST request.
- No workflow dispatch, rerun or workflow edit.
- No parser or test edit.
- No SQLite, importer, staging dataset or Contract 1.2.0 implementation.
- No Canonical T0, T1/T2, VPS/runtime, deployment, credentials or trading change.
