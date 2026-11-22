# T0 S1.2 — Owner Authorization for Gated Adapter & Synthetic SQLite Staging

Date: 2026-11-22
Repository: kenznguyen/btcquant-application
Target branch: main
Decision: OWNER APPROVED — BOUNDED IMPLEMENTATION SCOPE

## Authorization

The owner approved continuation beyond documentation-only review to:
- remediate S1.2 compatibility findings S12-01 through S12-07;
- implement immutable adapter DTOs and deterministic physical-record to unchanged S3/V1 projection;
- add synthetic-only TDD tests, including RED and GREEN evidence;
- implement and test the approved SQLite staging schema against synthetic fixtures;
- verify STRICT tables, CHECK/NULL behavior, foreign keys, append-only run events, schema fingerprint, integrity and application-level graph invariants.

All work must be committed directly to the existing main branch. Do not create a branch, fork, or divergent PR.

## Preconditions and sequencing

1. S1.2 design findings must be resolved before adapter/DDL behavior is frozen.
2. Exact source SHAs and test evidence must be recorded for every implementation milestone.
3. Tests must run in the repository's dedicated exact-SHA GitHub Actions workflow; no PASS claim without observed run/job evidence.
4. SQLite staging tests may use only disposable databases populated exclusively with synthetic fixtures. No existing or Canonical database may be opened.
5. Any DDL executed during this scope must be confined to the disposable synthetic test database and exact tested runtime; this does not establish a production runtime pin.

## Explicit exclusions

This approval does NOT authorize:
- listing, downloading, extracting, parsing, sampling or otherwise accessing real archive/sidecar objects;
- workstation, host, SSH, filesystem path, disk, encryption or runner preflight/provisioning/registration;
- self-hosted runner execution or B8 acquisition workflow changes/dispatch;
- real-data Historical build, staging population, archive coverage acceptance or data acquisition;
- upload, retention change, cleanup or deletion of source/staging/private evidence;
- Canonical T0 recovery, creation, replacement, migration, merge, promotion or cutover;
- MAY-10, REST tail, T1/T2, VPS, deployment, credentials, exchange connectivity or trading.

B8 remains NOT READY / NOT APPROVED as an acquisition execution model. No workflow/job IDs may be fabricated.

## Required reporting

For each completed milestone record:
- scope and exact source SHA;
- commit SHA and changed paths;
- exact workflow run/job IDs and checked-out SHA;
- test counts and outcomes;
- artifact ID/digest when produced;
- PASS / BLOCKED / NOT VERIFIED status;
- next step and remaining prohibited actions.

## Current starting evidence

- Latest observed main commit at authorization: 32e403839b1da71f8058227ac808590ecf301a9b.
- S1.2 proposal commit: 3e178d5d4bd1bcb5bb652798ddadf31034b91580.
- Independent compatibility review commit: b2901a33220368597b332b3d1878c5937b9e9d3f.
- Review disposition commit: 32e403839b1da71f8058227ac808590ecf301a9b.
- Review verdict: S1.2 not ready to freeze; S12-01 through S12-07 require design revisions.
- Existing importer-core synthetic exact-SHA GREEN: run 44992591222; 20/20 focused and 421/421 market_data tests PASS at source SHA 0fc21ac6ba91e82e531fe58a02f9303462c71ea7.

This authorization does not imply any implementation or test has already been performed.
