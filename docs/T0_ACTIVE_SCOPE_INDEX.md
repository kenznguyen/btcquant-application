### D1 runtime-lock-only clean install and ASGI smoke — CLOSED / PASS — 2026-11-19

- Exact tested source SHA: `fe5f99d31aac832f85c1aab9ca007bd70386d9fe`.
- Added standard-library ASGI smoke harness `market_data/runtime_smoke.py`, commit `e50c5d83437d6db1b6eb15f8b75267575acde041`.
- Added isolated `runtime-lock-smoke` CI job, commit `fe5f99d31aac832f85c1aab9ca007bd70386d9fe`.
- Runtime-only job: workflow [44536493461](https://github.com/kenznguyen/btcquant-application/actions/runs/44536493461), job `135603190576`: **success**. Installs only `requirements-market-data-fastapi.lock` into a fresh CPython 3.12.16 venv, offline from the SHA-256-verified runtime wheelhouse; does not install the test lock. `pip check`, ASGI import and in-process GET `/health` all PASS.
- Runtime smoke artifact `14535727293`, SHA-256 `607771298cf289ab9af7f8bf7918d9738fff2d400be45e3e25bba388959042da`.
- Same-SHA FastAPI/parity job `135603189986`: **26/26 PASS**, run [44536493461](https://github.com/kenznguyen/btcquant-application/actions/runs/44536493461), artifact `14536536165`, SHA-256 `dbdbcc79ecd8495d91d39e14160187dbda6b9618f08d501f96cf4a6111dd02cd`.
- Same-SHA SQLite aggregate job `135603190883`: **196/196 PASS**, run [44536493268](https://github.com/kenznguyen/btcquant-application/actions/runs/44536493268), artifact `14536651799`, SHA-256 `fb0b74ec9276c7fc96c95e6c67b642079644d32d8329cb1efea9eb324462522a`.
- Detailed evidence: `docs/evidence/T0_FASTAPI_RUNTIME_LOCK_SMOKE_2026-11-19.md`, commit `b5d03b14175fc54360630113ac41ec186929704a`.
- D1: **CLOSED / PASS** for clean runtime-lock installation, dependency consistency, ASGI import and in-process health route. The smoke did not start a Uvicorn process or open a socket.
- Independent second-person review remains **PENDING**. WSGI/Gunicorn retirement **NOT APPROVED**. Uvicorn process/socket, Nginx, VPS/systemd, endpoint/runtime qualification and deployment **NOT VERIFIED / NOT AUTHORIZED**. Production readiness **NOT CERTIFIED**.
- Canonical SQLite, writer/lease/feeder/recovery, T1/T2, PostgreSQL, retention/deletion and trading were not changed or accessed.



### FastAPI follow-up self-review — 2026-11-19

- Re-inspected FastAPI adapter, shared contract helper, ASGI tests, runtime/test dependency inputs and locks, FastAPI workflow, SQLite aggregate workflow, storage facade and prior self-review evidence.
- API implementation: no new Critical source defect identified in the bounded static review. Additional non-blocking nit: stale test-module docstring.
- **Required CI finding R1:** FastAPI workflow push-path filter omits runtime/test dependencies (`market_data/storage.py`, `store.py`, `postgres.py`, plus test fixture dependencies `feeder.py`, `write_gateway.py`, `sync.py`). The SQLite aggregate triggers on some dependencies but its explicit test command does not run `market_data.test_fastapi_api`; FastAPI contract tests can therefore be skipped after dependency-only changes.
- Finding is recorded, **OPEN / NOT FIXED**. Workflow/source was not modified and no workflow was dispatched in this review.
- Updated report: [T0 FastAPI Internal Self-Review](evidence/T0_FASTAPI_INTERNAL_SELF_REVIEW_2026-11-19.md), commit `b88da69f6d73fb1e60e0d08638e652d9a0121434`.
- Verdict: internal self-review PASS WITH REQUIRED CI ACTION ITEM; independent reviewer remains **PENDING**. WSGI/Gunicorn removal remains **NOT APPROVED**; runtime/deployment remains **NOT AUTHORIZED**.


### FastAPI CI trigger correction and paired regression — 2026-11-19

- Corrected `.github/workflows/t0-fastapi-migration.yml` push paths to include `market_data/storage.py`, `store.py`, `postgres.py`, `feeder.py`, `write_gateway.py` and `sync.py`.
- Workflow correction commit: `3bdcaf093c381b2b767be3c903f9e86d5bf75bde`.
- Trigger proof: commit `b53e3e4f800d498317ac7ab4d0d01b44ef63a55c` changed only a CI sentinel comment in `market_data/storage.py`; GitHub started FastAPI and SQLite aggregate workflows on that exact push SHA.
- FastAPI run [44529575151](https://github.com/kenznguyen/btcquant-application/actions/runs/44529575151), job `135579262823`: **25/25 PASS**; artifact `14532693874`; SHA-256 `7bcf6fdd46e8c5e1c81f76bf078377437b81cdbb178a546ce0b18166a8ade5f5`.
- SQLite aggregate run [44529575307](https://github.com/kenznguyen/btcquant-application/actions/runs/44529575307), job `135579168097`: **196/196 PASS**; artifact `14531469720`; SHA-256 `93f30f492c9006a995c1f6248101080a3c2238be9d0530ab04421ce41f0580e8`.
- Both jobs checked out and tested exact SHA `b53e3e4f800d498317ac7ab4d0d01b44ef63a55c`. Artifact metadata and test logs independently confirm 25 and 196 tests with exit code 0.
- Updated internal review report in commit `608caa27910816e549fb109448004b1e080985b0`; R1 status **CLOSED / VERIFIED**.
- Scope: no FastAPI/SQLite runtime behavior changed; no canonical DB, feeder runtime, VPS, T1/T2, PostgreSQL, endpoint, deployment or trading access.
- Remaining gates: independent second-reviewer sign-off is still **PENDING**; WSGI/Gunicorn retirement is **NOT APPROVED**; runtime/deployment is **NOT AUTHORIZED**; production readiness **NOT CERTIFIED**.


### FastAPI follow-up internal self-review — 2026-11-19

- Re-reviewed current source/workflow at main HEAD `324fe0112c7c1d1a4c7e59aff29797c2f3cad3f4`; compared with tested source SHA `b53e3e4f800d498317ac7ab4d0d01b44ef63a55c`: four documentation-only commits, no source/workflow drift.
- Re-read FastAPI adapter, shared contract helper, ASGI tests, WSGI adapter, storage and SQLite/PostgreSQL adapters, fixture dependencies, locks/hash manifest and workflow filters.
- R1 dependency trigger: **CLOSED / VERIFIED**. FastAPI 25/25 and SQLite aggregate 196/196 remain PASS on exact SHA `b53e3e4f800d498317ac7ab4d0d01b44ef63a55c`; runs `44529575151` and `44529575307`.
- No new blocking API correctness/security issue found in bounded static review. No CVE research, dynamic pentest, load test, reverse-proxy or runtime validation performed.
- R2 stale docstring in `market_data/test_fastapi_api.py` (“not-yet-created ASGI app”): **OPEN / NON-BLOCKING NIT**; no source edit made.
- Current verdict: internal self-review **PASS WITH NON-BLOCKING NIT**; independent second review **PENDING**.
- WSGI/Gunicorn retirement **NOT APPROVED**; runtime/deployment **NOT AUTHORIZED**; production readiness **NOT CERTIFIED**.


### FastAPI R2 closure — 2026-11-19

- Corrected stale module docstring in `market_data/test_fastapi_api.py` to “Contract tests for the FastAPI ASGI adapter.”
- Documentation-only change; executable source/test logic, dependencies, workflows and runtime unchanged.
- R2: **CLOSED / VERIFIED**. No new CI run claimed; prior paired FastAPI 25/25 and SQLite aggregate 196/196 evidence remains tied to exact tested SHA `b53e3e4f800d498317ac7ab4d0d01b44ef63a55c`.
- Independent second review **PENDING**. WSGI/Gunicorn retirement **NOT APPROVED**. Runtime/deployment **NOT AUTHORIZED**.


### FastAPI independent review package — 2026-11-19

- Prepared reviewer package: [T0 FastAPI Independent Review Package](reviews/T0_FASTAPI_INDEPENDENT_REVIEW_PACKAGE_2026-11-19.md), commit `814721fb3974672fc936befc5267719a5b14bd28`.
- Exact review snapshot: `d69e2e44707ea9b177548c79d36bf72ac8a18f0b`; paired CI source SHA: `b53e3e4f800d498317ac7ab4d0d01b44ef63a55c`. Compare: 8 ahead / 0 behind; changed paths are documentation plus the already-closed test docstring correction; executable source/workflow/dependency locks unchanged.
- Package includes FastAPI 25/25 run `44529575151`, SQLite aggregate 196/196 run `44529575307`, artifact IDs/digests, source file inventory, review checklist, required verdict and scope restrictions.
- Independent reviewer: **NOT YET ASSIGNED / REVIEW PENDING**. This package is not itself a review approval.
- WSGI/Gunicorn retirement: **NOT APPROVED**. Runtime/deployment: **NOT AUTHORIZED**. Production readiness: **NOT CERTIFIED**.
- No source, tests, workflow, runtime, canonical data, T1/T2, PostgreSQL or trading changes; no tests or workflows run during package preparation.


### FastAPI adversarial follow-up self-review — 2026-11-19

- Review record: [T0 FastAPI Adversarial Self-Review](evidence/T0_FASTAPI_ADVERSARIAL_SELF_REVIEW_2026-11-19.md), commit `b2a075ace4c99227a3701f6183061f5dc3b59354`.
- Verdict: **PASS WITH VERIFICATION GAPS** in bounded static review; no blocking source defect identified.
- C1 **MEDIUM / NOT VERIFIED**: no automated WSGI-vs-FastAPI same-fixture differential test. Required before WSGI/Gunicorn retirement.
- D1 **LOW / NOT VERIFIED**: standalone runtime-lock install smoke test not separately evidenced; recommend before runtime qualification.
- This was performed by the same assistant and is explicitly **not an independent second-person review**. Independent review remains **PENDING**.
- WSGI/Gunicorn retirement **NOT APPROVED**; runtime/deployment **NOT AUTHORIZED**; production readiness **NOT CERTIFIED**. No source/tests/workflow/runtime/data changes and no tests/workflows run during this review.


### C1 WSGI–FastAPI differential contract test — 2026-11-19

- Added `market_data/test_fastapi_parity.py`, commit `78770e49c61075ff10da9ba94526b2d3aef0141d`, blob `2d951e924c99e5929dcc21c21ad144586658aabe`.
- The test constructs one temporary SQLite fixture, invokes the retained WSGI callable and FastAPI ASGI app against that same database and deterministic clock, then compares HTTP status, complete response headers and exact response-body bytes (plus parsed JSON).
- Cases: health, successful candle read, unauthorized, missing token configuration, malformed query, duplicate query parameter, unknown path, non-GET, missing SQLite store, and historical `asOfMs`.
- Updated `.github/workflows/t0-fastapi-migration.yml` to trigger on the new test file and run it alongside the 25 FastAPI contract tests. Workflow commit: `62054b53119308eca9d2256dcd5aae5561da235b`.
- Current source/test verification: **PENDING CI**. Do not claim C1 closed until the exact-SHA FastAPI workflow passes and its logs/artifact confirm the differential test ran. SQLite aggregate workflow is expected to trigger because its path filter includes the FastAPI workflow file; its result is also pending.
- No API implementation, WSGI/Gunicorn lifecycle, dependencies, canonical SQLite data, feeder, T1/T2, PostgreSQL, runtime, endpoint, VPS, deployment, retention/deletion or trading behavior changed.
- C1 remains **OPEN / NOT VERIFIED** pending CI. Independent second-person review remains **PENDING**. WSGI/Gunicorn retirement **NOT APPROVED**; runtime/deployment **NOT AUTHORIZED**; production readiness **NOT CERTIFIED**.


### C1 WSGI–FastAPI differential parity — CLOSED / VERIFIED — 2026-11-19

- Exact tested source SHA: `62054b53119308eca9d2256dcd5aae5561da235b`.
- FastAPI workflow run [44534512421](https://github.com/kenznguyen/btcquant-application/actions/runs/44534512421), job `135596271306`: **26/26 PASS**. The log explicitly records `test_same_fixture_has_identical_status_headers_and_body_for_contract_cases ... ok`, followed by `Ran 26 tests` and `OK`.
- FastAPI artifact `14533664834`, SHA-256 `555c63db97aa8466857cb4dd84728808989edc8107b25af0af31336bd3e84883`. Downloaded and inspected ZIP: `runner_metadata.txt` confirms both `workflow_commit` and `checked_out_source_sha` equal the exact SHA; `test_count=26`, `test_exit_code=0`. Test log included in artifact.
- SQLite aggregate workflow run [44534512612](https://github.com/kenznguyen/btcquant-application/actions/runs/44534512612), job `135596271401`: **196/196 PASS**, log ends `Ran 196 tests` / `OK`.
- SQLite artifact `14534628423`, SHA-256 `8e9c5274d48a44bb779bdd1db4119d3a83f1873c61ff889b769fc03fd6a0cfb0`. Downloaded and inspected ZIP: metadata confirms exact source SHA and expected 196 tests; aggregate test log confirms pass.
- Both workflow runs have event `push`, branch `main`, and exact `head_sha` equal to `62054b53119308eca9d2256dcd5aae5561da235b`; both conclusions are `success`.
- C1 finding (absence of same-fixture WSGI–FastAPI differential test): **CLOSED / VERIFIED** for the ten explicit contract cases in `market_data/test_fastapi_parity.py`. This does not claim exhaustive equivalence for every possible HTTP request or environment.
- D1 (runtime-only clean-install smoke test) remains **NOT VERIFIED**. Independent second-person review remains **PENDING**; this CI proof is not independent review.
- WSGI/Gunicorn retirement remains **NOT APPROVED**; runtime/deployment remains **NOT AUTHORIZED**; production readiness remains **NOT CERTIFIED**.
- Scope unchanged: no API implementation behavior, canonical SQLite data, writer/lease/feeder/recovery, T1/T2, PostgreSQL, VPS/systemd, runtime, deployment, retention/deletion or trading was modified or accessed.


### FastAPI independent review package refreshed after C1 closure — 2026-11-19

- Updated reviewer package: [T0 FastAPI Independent Review Package](reviews/T0_FASTAPI_INDEPENDENT_REVIEW_PACKAGE_2026-11-19.md), commit `495c234d920feaec8a323044955b42a80c6d5ea1`.
- Exact review snapshot: `440379b243d0b63e80f22b032fa8499bc2e1a6f4`; exact tested implementation/workflow SHA: `62054b53119308eca9d2256dcd5aae5561da235b`.
- Verified compare: 4 commits ahead / 0 behind; only `docs/PROJECT_SESSION_HANDOFF.md` and `docs/T0_ACTIVE_SCOPE_INDEX.md` changed after the tested SHA; no executable source, test, workflow or dependency drift.
- Package now includes C1's ten-case same-fixture differential test, exact FastAPI 26/26 run `44534512421` / job `135596271306` / artifact `14533664834` / SHA-256 `555c63db97aa8466857cb4dd84728808989edc8107b25af0af31336bd3e84883`, and SQLite 196/196 run `44534512612` / job `135596271401` / artifact `14534628423` / SHA-256 `8e9c5274d48a44bb779bdd1db4119d3a83f1873c61ff889b769fc03fd6a0cfb0`.
- C1 remains **CLOSED / VERIFIED** for ten enumerated cases. D1 clean runtime-only install smoke test **NOT VERIFIED**. Independent second-person review **PENDING**; no reviewer has been assigned or approved.
- No source/test/workflow/dependency/runtime/data changes; no tests or workflows run for this documentation refresh.
- WSGI/Gunicorn retirement **NOT APPROVED**; runtime/deployment **NOT AUTHORIZED**; production readiness **NOT CERTIFIED**.


### FastAPI adversarial self-review follow-up — 2026-11-19

- Review report: [T0 FastAPI Adversarial Self-Review Follow-up](evidence/T0_FASTAPI_ADVERSARIAL_SELF_REVIEW_FOLLOWUP_2026-11-19.md), commit `17ab5aa4cc246f5eafb618fbe9eaddc963399bee`.
- Reviewed snapshot: `440379b243d0b63e80f22b032fa8499bc2e1a6f4`; tested implementation/workflow SHA: `62054b53119308eca9d2256dcd5aae5561da235b`.
- Same-assistant static review inspected FastAPI/WSGI adapters, shared contract, parity/ASGI tests, storage selection, dependency locks and workflow. No additional blocking source defect identified in the bounded review.
- D1 remains **OPEN / NOT VERIFIED**: workflow downloads runtime-lock wheels but installs only the test lock in its test container; a separate clean runtime-only install/import smoke test is not evidenced.
- Dependency CVE/advisory research, dynamic security testing, Nginx/reverse-proxy validation, Uvicorn/VPS runtime, load and latency testing remain NOT PERFORMED.
- Verdict: **PASS WITH VERIFICATION GAPS — SELF-REVIEW ONLY**. This reviewer participated in implementation and prior reviews; this is explicitly **NOT INDEPENDENT** and does not satisfy the second-person review gate.
- C1 remains **CLOSED / VERIFIED** for ten cases. Independent second-person review **PENDING**.
- No source/test/workflow/dependency/runtime/data changes; no tests or workflows run.
- WSGI/Gunicorn retirement **NOT APPROVED**; runtime/deployment **NOT AUTHORIZED**; production readiness **NOT CERTIFIED**.
