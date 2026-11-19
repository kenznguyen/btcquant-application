# CURRENT STATUS OVERRIDE — 2026-11-20 — Owner approved T0 archive source partition

- Decision: `docs/decisions/T0_RECONSTRUCTED_CANONICAL_SOURCE_PARTITION_APPROVAL_2026-11-20.md`, commit `ce42ae530d5b11a46e46c4e79e573bd4b5d0f3d2`.
- Owner approved monthly USD-M archive as default bulk source for full months 2020-01–2026-10; daily archive for 2019-12-31 and 2026-11-01–2026-11-18; daily as targeted fallback/diagnostic for payload-level gaps/conflicts.
- Any retrieved daily/monthly overlap must be compared using complete normalized candle payloads. Exact duplicates may be deduplicated with both provenances retained; conflicts must be quarantined.
- REST `/fapi/v1/klines` tail remains a separate future approval gate; this decision does not authorize REST calls.
- Approval is source-partition/documentation only. ZIP/checksum body download, raw staging, market-data retrieval, SQLite, Dropbox, restore, VPS/runtime, writer/feeder and cutover remain NOT AUTHORIZED.
- Archive listing remains PASS for object-key coverage only. ZIP/checksum integrity, candle-level completeness, row counts, actual first/last candle timestamps, intra-file gaps and closed state remain NOT VERIFIED.
- Tests/workflows NOT RUN; no run/job/artifact. Documentation-only update.
- Next gate: request separate bounded approval for exact ZIP/checksum payload retrieval and validation, including staging destination and resource/retention budgets.

---

# CURRENT STATUS OVERRIDE — 2026-11-20 — Binance USD-M archive metadata inspection PASS

- Evidence: `docs/evidence/T0_BINANCE_UM_BTCUSDT_ARCHIVE_METADATA_INSPECTION_2026-11-20.md`, commit `0b37e158e30824e7e6cfd80ff9d8a457ee715ec9`.
- Owner-approved scope executed: read-only S3-compatible ListObjectsV2 metadata inspection for Binance Public Data `data/futures/um` BTCUSDT M15/H1 daily and monthly prefixes only.
- Monthly per timeframe: 82 ZIP + 82 `.CHECKSUM` keys; continuous 2020-01 through 2026-10; listing complete.
- Daily per timeframe: 2,515 ZIP + 2,515 `.CHECKSUM` keys across six pages; continuous filename dates 2019-12-31 through 2026-11-18; no duplicate or missing calendar filename dates.
- Latest daily archive object date 2026-11-18, LastModified 2026-11-19T08:16:17Z. Latest monthly object October 2026, LastModified 2026-11-11T10:50:21Z.
- Daily and monthly object coverage overlaps for 2020-01 through 2026-10. Proposed partition (NOT OWNER-APPROVED): monthly bulk for 2020-01–2026-10, daily for 2019-12-31 and 2026-11-01–18, with daily fallback for payload-level gaps and REST tail considered separately.
- Important: listing PASS is object-key coverage only. ZIP/checksum bodies not fetched; SHA-256 not validated; first/last candle timestamps, candle counts, intra-file gaps, closed state and earliest REST history remain NOT VERIFIED.
- No REST API, ZIP/checksum body download, raw staging, SQLite, Dropbox, VPS/runtime, writer/feeder or cutover. Tests/workflows NOT RUN; no run/job/artifact.
- Next: owner decision on proposed source partition, then separate bounded approval for archive payload retrieval/validation and any REST probe. No reconstruction/database creation authorized.

---

# CURRENT STATUS OVERRIDE — 2026-11-20 — T0 historical source selection review recorded

- Review: `docs/reviews/T0_RECONSTRUCTED_CANONICAL_SOURCE_SELECTION_REVIEW_2026-11-20.md`, commit `70f6c26b9f205c7d0198c5e58f46308642f5f48f`.
- Documentation-based comparison: Binance USD-M REST `/fapi/v1/klines` vs Binance Public Data USD-M (`um`) daily/monthly kline archives.
- Recommendation (NOT OWNER-APPROVED): archive as bulk base; REST as latest-closed-candle tail/completion; preserve per-chunk provenance and quarantine conflicting overlaps.
- Official docs identify REST max limit 1,500 and request-weight tiers; archive docs identify USD-M/COIN-M separation, klines sourced from `/fapi/v1/klines`, companion SHA-256 checksums, daily next-day and monthly first-Monday publication, and possible later archive corrections.
- Earliest BTCUSDT M15/H1 archive object, exact listing completeness, archive overlap behavior and latest available object remain NOT VERIFIED; no archive listing/API endpoint was queried.
- Status: documentation review **PASS / COMPLETE**; source selection **PROPOSED / OWNER APPROVAL PENDING**.
- No API call, metadata probe, ZIP/checksum download, market-data download, raw staging, SQLite, Dropbox, VPS/runtime, writer/feeder or cutover. Tests/workflows **NOT RUN**; no run/job/artifact.
- Next approval gate: read-only archive index/listing metadata inspection only; no ZIP candle payloads and no REST klines probe. Reconstruction requires a separate approval.

---

# CURRENT STATUS OVERRIDE — 2026-11-19 — Reconstructed Canonical workflow design recorded

- Workflow/validation contract: docs/decisions/T0_RECONSTRUCTED_CANONICAL_SQLITE_RECONSTRUCTION_WORKFLOW_2026-11-19.md.
- Status: DESIGN DRAFT / NOT IMPLEMENTED / NOT EXECUTED. Covers source-selection gate, immutable raw chunks, resumable pagination/checkpoints, normalization, M15/H1 expected-grid gap detection, semantic validation, staged SQLite gates, mandatory provenance manifest, fail-closed states, Dropbox snapshot and isolated restore gates.
- Owner-approved target remains all Binance USD-M BTCUSDT M15/H1 history available at retrieval time, each timeframe from its independently evidenced earliest candle through the latest fully closed candle at the recorded UTC cutoff. Lineage RECONSTRUCTED.
- All gaps must be enumerated; no synthetic candles, interpolation, forward-fill or silent omission. Gap disposition remains pending evidence and explicit owner decision.
- Open before implementation: source family selection; request/chunk/resource budgets; raw staging destination; exact Candle Contract/SQLite schema compatibility; gap disposition evidence; retention policy.
- Authorization remains Phase 1 documentation/static only. No Binance access/download, raw data staging, SQLite initialization/write, Dropbox upload, snapshot, restore, VPS/runtime, writer/feeder or cutover.
- Tests/workflows: NOT RUN; no run/job/artifact for this documentation-only change.

---

# CURRENT STATUS OVERRIDE — 2026-11-19 — Owner approved reconstructed Canonical coverage target

- Decision: [T0 Reconstructed Canonical Coverage Decision](decisions/T0_RECONSTRUCTED_CANONICAL_COVERAGE_DECISION_2026-11-19.md).
- Scope: Binance USD-M BTCUSDT M15 and H1; for each timeframe independently, start at the earliest candle actually available from Binance and end at the latest fully closed candle available at the recorded UTC retrieval cutoff.
- Retrieve all history available through the selected Binance USD-M historical-data interface at retrieval time; document source/endpoint limits, exact first/last candle times, retrieval cutoff, counts and partial-boundary treatment.
- Every missing expected interval must be reported with UTC boundaries/duration/count and evidence. No synthetic fill, interpolation, forward-fill or silent omission. Gap acceptability remains subject to validation and explicit owner disposition.
- Lineage must be RECONSTRUCTED; this is not recovery of the historical original database.
- Authorization remains Phase 1 DESIGN / DOCUMENTATION ONLY. No Binance access/download, reconstruction, SQLite initialization/write, Dropbox upload, snapshot, restore, VPS/runtime, feeder/writer or cutover is authorized.
- Tests/workflows: NOT RUN; no run/job/artifact for this documentation-only update.

---

# CURRENT STATUS OVERRIDE — 2026-11-19 — Owner approved independent CI and VPS runtime validation tracks

- Decision: `docs/decisions/T0_DUAL_TRACK_CI_RUNTIME_VALIDATION_DECISION_2026-11-19.md`.
- Owner approval: **APPROVED**. The prior GitHub-only validation decision is superseded.
- Track A — GitHub Actions isolated Uvicorn + Nginx integration: preserve **PASS — CI ONLY**, exact tested source/workflow SHA `65661cd4a2492f9552fe05186581c66d14fbe293`, FastAPI workflow run `44550458804`, job `135652465869`, integration artifact `14543536038`, SHA-256 `af07b99fa0a53ff315bad148c508533ea0e808d6365fc2c81faafa11ebe8c872`.
- Track B — VPS/Scaleway runtime integration: **NOT VERIFIED / NOT RUN**. No VPS probe or runtime action is authorized by this decision. Any future runtime validation requires a separate explicit owner approval defining the exact scope.
- CI and runtime statuses, evidence and acceptance criteria remain independent. Never merge into one PASS or infer VPS readiness from CI.
- Documentation-only governance update. No code, tests, workflow, dependencies, runtime configuration or data changed. No CI or runtime validation was run as part of recording this decision.
- Preserved restrictions: no canonical T0 SQLite/feeder/writer/lease/recovery access or changes; no T1/T2/PostgreSQL/retention/trading changes; no real orders; no systemd/autostart, persistent service, public ingress, DNS/TLS or production deployment authorization. Paper-first and `ai_execution_enabled=false` remain unchanged.

---

# CURRENT STATUS OVERRIDE — 2026-11-19 — Uvicorn + Nginx isolated GitHub Actions integration PASS

- Evidence report: `docs/evidence/T0_UVICORN_NGINX_ISOLATED_INTEGRATION_2026-11-19.md`, commit `15563d2a4d47b0ac860f82b37b3050c6ebba238a`.
- Repository: `kenznguyen/btcquant-application`, branch `main`.
- Exact tested source/workflow SHA: `65661cd4a2492f9552fe05186581c66d14fbe293`.
- Added `market_data/uvicorn_nginx_smoke.py` (blob `38e5fcdf10990af265f68f3597cdfef386f5a0aa`) and a dedicated `uvicorn-nginx-socket-integration` job in `.github/workflows/t0-fastapi-migration.yml` (blob `82b65cad3ea90d437d73998f33384f66b543431b`).
- FastAPI workflow [44550458804](https://github.com/kenznguyen/btcquant-application/actions/runs/44550458804): exact SHA above, **SUCCESS**. Uvicorn/Nginx job `135652465869` SUCCESS; existing FastAPI contract job `135652465887` SUCCESS; runtime-lock smoke job `135652465650` SUCCESS.
- Integration artifact `14543536038`, SHA-256 `af07b99fa0a53ff315bad148c508533ea0e808d6365fc2c81faafa11ebe8c872`.
- FastAPI contract artifact `14541653518`, SHA-256 `cdcc7a4c039c1b3fe4115c3d770c42754312b660efd384bc34319e59a447cdaa`; runtime smoke artifact `14543502169`, SHA-256 `e6779dd50b10d003e0e850c35cab245e003f9e5babafd3f8ee5be45ca7a1b6e7`.
- SQLite aggregate workflow [44550458851](https://github.com/kenznguyen/btcquant-application/actions/runs/44550458851): exact same SHA, **SUCCESS**; job `135652463602`; artifact `14543096166`, SHA-256 `852ce0109b95bd7f9d021d9fc2ccda4db076409f45cf189d989d2dd7c4bdd78f`.
- Verified behavior: real Uvicorn and Nginx subprocesses; loopback TCP sockets; Nginx health proxy; Bearer header forwarding and Candle Contract 1.1.0 read; missing token 401; unknown path 404; POST 405/Allow GET; stopped upstream returns 502; dummy token absent from Nginx logs.
- Isolation: temporary SQLite fixture only, synthetic token, listeners bound to 127.0.0.1, external network disabled during test, non-root/read-only/bounded container. Canonical T0 SQLite not mounted.
- Status: Uvicorn process/socket + Nginx reverse proxy **PASS — isolated CI only**. VPS/Scaleway runtime and Nginx **NOT VERIFIED**. systemd/autostart, public ingress, TLS, deployment and production readiness **NOT AUTHORIZED / NOT VERIFIED**.
- No canonical T0 writer/lease/feeder/recovery/data, T1/T2, PostgreSQL, retention/deletion, exchange, strategy/risk/trading changes or access. Paper-first and `ai_execution_enabled=false` remain unchanged.
- Next step: only a separate explicit owner approval may authorize a VPS probe, persistent service, Nginx modification, public endpoint, TLS or runtime activation. Do not infer VPS readiness from CI.
 
---

### T0 WSGI/Gunicorn retirement — completed — 2026-11-19

- Owner approval and human-review waiver: [T0 WSGI/Gunicorn Retirement Approval](decisions/T0_WSGI_GUNICORN_RETIREMENT_APPROVAL_2026-11-19.md).
- Evidence: [T0 WSGI/Gunicorn Retirement Report](evidence/T0_WSGI_GUNICORN_RETIREMENT_2026-11-19.md).
- Implementation commit: `7bc8fab6b6c6f49ed70b7370a113958d7981cd20`; corrected test/workflow exact SHA: `c77ab92b621b2e79167d6b8eb910be015b428f62`.
- Removed WSGI module and Gunicorn dependency; migrated API/acceptance tests to ASGI; removed WSGI parity test after preserving C1 evidence; updated FastAPI, SQLite and dependency workflows.
- FastAPI + migrated tests + retirement guards: **50/50 PASS**, run `44546084887`.
- SQLite aggregate: **174/174 PASS**, run `44546084972`.
- F1 write-gateway regression: **14/14 PASS**, run `44546084937`.
- Runtime-lock ASGI import/in-process health: **PASS**, run `44546084887`.
- Dependency compatibility after Gunicorn removal: **PASS**, run `44545799691`, dependency-change SHA `7bc8fab6b6c6f49ed70b7370a113958d7981cd20`.
- WSGI/Gunicorn retirement: **PASS**. Human independent review prerequisite: **WAIVED BY OWNER**. Gemini review remains **BLOCKED / NOT VERIFIED**.
- Uvicorn socket/process, Nginx, VPS/systemd, endpoint runtime and deployment remain **NOT AUTHORIZED / NOT VERIFIED**. Production readiness **NOT CERTIFIED**.
- T0 canonical SQLite/writer/lease/feeder/recovery, T1/T2, PostgreSQL, retention/deletion and trading unchanged.

### Owner approval — T0 WSGI/Gunicorn retirement — 2026-11-19

- Decision: [T0 WSGI/Gunicorn Retirement Approval](decisions/T0_WSGI_GUNICORN_RETIREMENT_APPROVAL_2026-11-19.md).
- Owner explicitly waived the human independent second-person review prerequisite and approved the bounded retirement.
- Gemini external AI review is **BLOCKED / NOT VERIFIED** (repository and exact SHA inaccessible); no independent code-level approval is claimed. ChatGPT supplementary review remains non-independent.
- Baseline main HEAD at approval: `7fdf4e3eedaf0b568c7219ee8b140684ff066718`; tested implementation/workflow SHA: `a92cca39a3c23c3325191922c80e73b81384d9ce`.
- Authorized implementation scope: remove WSGI entrypoint and Gunicorn dependency/lock; migrate WSGI-dependent tests and acceptance fixtures to ASGI; retire the parity test after preserving its C1 evidence; update workflows and docs; rerun FastAPI, SQLite aggregate and dependency compatibility CI on one exact SHA.
- Preserve Candle Contract 1.1.0 and T0 canonical SQLite/writer/lease/feeder/recovery boundaries.
- Owner approval: **APPROVED**. Retirement implementation: **AUTHORIZED / NOT STARTED**. Post-change tests/CI: **NOT RUN**.
- Uvicorn socket, endpoint, Nginx, VPS/systemd, runtime/deployment: **NOT AUTHORIZED / NOT VERIFIED**. Production readiness: **NOT CERTIFIED**.
- PostgreSQL, T1/T2, data retention/deletion and trading remain excluded.

### ChatGPT supplementary adversarial review — completed, not independent sign-off — 2026-11-19

- Report: `docs/reviews/T0_FASTAPI_CHATGPT_SUPPLEMENTARY_REVIEW_2026-11-19.md`, commit `cd1dd1c3e55f635d9cc542ab3f9bb665d614f922`.
- Exact implementation/workflow SHA inspected: `a92cca39a3c23c3325191922c80e73b81384d9ce`; review-start documentation snapshot: `379ac5021d347668dbfe42686e1bfb5fa0f14a6b`.
- Outcome: **NO CONFIRMED BLOCKING DEFECT IDENTIFIED IN THE INSPECTED STATIC SCOPE**. Same assistant participated in implementation and prior self-review; this report is supplementary only and is not an independent second-person review or certification.
- Scope: read-only static inspection of FastAPI/WSGI adapters, contract helpers, storage, tests, dependency locks and CI workflow. No tests/workflows run; no source/runtime/data/deployment changes.
- Limitations: C1 ten cases only; C2 api.py-only trigger not simulated; D1 in-process health only; no Uvicorn/Nginx/VPS/load/dynamic security qualification.
- Independent second-person review **PENDING**; reviewer not assigned. WSGI/Gunicorn retirement **NOT APPROVED**; runtime/deployment **NOT AUTHORIZED**; production readiness **NOT CERTIFIED**.

### Independent Review package refreshed — READY TO ASSIGN — 2026-11-19

- Refreshed `docs/reviews/T0_FASTAPI_INDEPENDENT_REVIEW_PACKAGE_2026-11-19.md`, commit `50d6fc71629ab03f9841959e0900dba50107425f`, blob `ec5f86bb4a5165cb8a66609cf0c6ff8eebc74f0c`.
- Exact tested implementation/workflow SHA: `a92cca39a3c23c3325191922c80e73b81384d9ce`; review snapshot before package refresh: `71be9bf1b477577643c557e69727bb92dec0c011`.
- Tested SHA to review snapshot: 3 ahead / 0 behind; only three documentation files changed. No executable source/test/workflow/dependency drift.
- Exact-SHA FastAPI workflow `44538454822`: contract job `135610069787` success, artifact `14535834201`, SHA-256 `350db8e7ec0dd7a876d814b8116306a37b3ca8c89ae7f826d9acf656db952983`; runtime job `135610069433` success, artifact `14536258780`, SHA-256 `b705d5c57283eff983d6d16e9301e2b9f882eaf8c038a2d058499864ebfefba7`.
- Exact-SHA SQLite aggregate workflow `44538454988`, job `135610069795` success, artifact `14536023784`, SHA-256 `a3ed69d72ceec7bf06e4a5c790d5b00f16f9ca46104e6a8a77e2e8a2d95d07a1`.
- C1 remains CLOSED / VERIFIED for ten enumerated cases; D1 CLOSED / PASS for runtime-lock installation, dependency check, ASGI import and in-process health; C2 CLOSED / VERIFIED for workflow path config and push-triggered success, with api.py-only trigger simulation not performed.
- Independent second-person reviewer **NOT YET ASSIGNED**. Package readiness is not independent review approval.
- WSGI/Gunicorn retirement **NOT APPROVED**; runtime/deployment **NOT AUTHORIZED**; production readiness **NOT CERTIFIED**.
- Documentation-only preparation. No tests/workflows run or dispatched; no source, runtime, data or trading changes.

### FastAPI C2 workflow trigger correction — CLOSED / VERIFIED — 2026-11-19

- User-approved workflow-only fix: added `market_data/api.py` to `.github/workflows/t0-fastapi-migration.yml` `on.push.paths`.
- Commit / exact tested SHA: `a92cca39a3c23c3325191922c80e73b81384d9ce`; workflow blob `7dabf111a2b89e22a80c3e02a5cf7f65a667095b`.
- Diff: one workflow file, +1/-0. No app source, test, dependency, runtime or data files changed.
- Static config verification: exactly one `market_data/api.py` path entry.
- Push-triggered FastAPI workflow [44538454822](https://github.com/kenznguyen/btcquant-application/actions/runs/44538454822): **success** on exact SHA; contract job `135610069787`, runtime-lock smoke job `135610069433`; artifacts `14535834201` (SHA-256 `350db8e7ec0dd7a876d814b8116306a37b3ca8c89ae7f826d9acf656db952983`) and `14536258780` (SHA-256 `b705d5c57283eff983d6d16e9301e2b9f882eaf8c038a2d058499864ebfefba7`).
- SQLite aggregate workflow [44538454988](https://github.com/kenznguyen/btcquant-application/actions/runs/44538454988): **success** on exact SHA; job `135610069795`; artifact `14536023784`, SHA-256 `a3ed69d72ceec7bf06e4a5c790d5b00f16f9ca46104e6a8a77e2e8a2d95d07a1`.
- Detailed evidence: `docs/evidence/T0_FASTAPI_ADVERSARIAL_SELF_REVIEW_FOLLOWUP_2026-11-19.md`, addendum commit `7ceea5a826b27242fa671948304aef225318892c`.
- C2: **CLOSED / VERIFIED** for path-filter configuration and successful push-triggered workflow execution. Qualification: the push changed the workflow file itself; an isolated api.py-only commit was not created because the approved scope excluded WSGI implementation changes.
- Independent second-person review remains **PENDING**; WSGI/Gunicorn retirement **NOT APPROVED**; runtime/deployment **NOT AUTHORIZED**; production readiness **NOT CERTIFIED**.

### FastAPI adversarial self-review C2 finding — 2026-11-19

- Review report: [T0 FastAPI Adversarial Self-Review Follow-up](evidence/T0_FASTAPI_ADVERSARIAL_SELF_REVIEW_FOLLOWUP_2026-11-19.md), commit `2815e6f4917f74679c19e88026c433e6258538fc`.
- Review HEAD: `7878e2d3b5cd9522ea6ed85b1c6083f8726a2816`; tested implementation/workflow SHA: `fe5f99d31aac832f85c1aab9ca007bd70386d9fe`.
- **C2 MEDIUM / OPEN:** `.github/workflows/t0-fastapi-migration.yml` omits `market_data/api.py` from `on.push.paths`, although the parity suite imports the WSGI adapter. WSGI-only edits will not trigger the FastAPI differential workflow.
- Required bounded correction: add `market_data/api.py` to the path filter and prove trigger behavior on an exact SHA. No source/workflow change or CI dispatch was made in this review.
- C1: **CLOSED / VERIFIED** for ten cases. D1: **CLOSED / PASS** for clean runtime-lock installation, dependency check, ASGI import and in-process health only.
- FastAPI/parity 26/26 and SQLite aggregate 196/196 PASS on exact SHA `fe5f99d31aac832f85c1aab9ca007bd70386d9fe`; artifacts/digests are in the evidence report.
- Same-assistant review only; independent second-person review remains **PENDING**. WSGI/Gunicorn retirement **NOT APPROVED**; runtime/deployment **NOT AUTHORIZED**; production readiness **NOT CERTIFIED**.

### FastAPI independent review package refreshed after D1 closure — 2026-11-19

- Updated `docs/reviews/T0_FASTAPI_INDEPENDENT_REVIEW_PACKAGE_2026-11-19.md`, commit `8a50de8b23566a57cc56f62755dda0f3b504b682`.
- Exact review snapshot before the package refresh: `4651bf1b26132ca028e6bb428ee0869963432bc0`.
- Exact tested implementation/workflow SHA: `fe5f99d31aac832f85c1aab9ca007bd70386d9fe`.
- Package now includes D1 runtime-only installation and ASGI health evidence, exact workflow/job IDs, artifact IDs/digests, smoke harness path and remaining runtime limitations.
- D1: **CLOSED / PASS**. C1: **CLOSED / VERIFIED** for ten cases. FastAPI/parity: **26/26 PASS**. SQLite aggregate: **196/196 PASS**.
- Independent second-person review remains **PENDING**; reviewer not yet assigned. WSGI/Gunicorn retirement **NOT APPROVED**. Runtime endpoint, Uvicorn process/socket, Nginx, VPS/systemd and deployment **NOT AUTHORIZED**. Production readiness **NOT CERTIFIED**.
- Next step: assign the updated package to a reviewer who did not author the implementation or self-reviews. No runtime or deployment work is authorized by this package refresh.

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


### Canonical SQLite read-only inventory — 2026-11-19

- Evidence: [T0 Canonical SQLite Read-only Inventory](evidence/T0_CANONICAL_SQLITE_READONLY_INVENTORY_2026-11-19.md), commit `9fe5cf641081391ad23e79975d54a151a0414f69`.
- Target snapshot inspected: `e62ef2d52c30e9245a1499c52d15aeb002b37892`; source selected-file snapshot: `c0f48b8910655fdb40d14214ad048b1d3cfa7fe9`; earlier source audit: `eb91528bab2b994f283dbe34cd7b0bcbfe406cb5`.
- Migration manifest confirms canonical SQLite/data payload was not copied. Target `.data/market-data.sqlite3` is only a default path; empty-only initializer refuses existing paths and creates only an empty DB.
- Static schema: `candles` + `feeder_leases`; candle rows persist `available_at_ms`; scheduler completion watermarks are in-memory; recovery gaps are derived from candle coverage. No dedicated persisted provenance/manifest, scheduler cursor or recovery-checkpoint table was found in the inspected SQLite schema.
- Historical VPS path `/home/ubuntu/t0/app/.data/market-data.sqlite3` belonged to `btcquant-t0-t1-test-01`, deleted 2026-11-11. Historical observations (622,592 bytes, integrity `ok`, M15 2,045, H1 2,011) do not prove current existence or recoverability.
- Historical 2026-11-09 coverage PASS is limited to one M15 window (3/3) and one H1 window (3/3); full history and scheduler completion remain NOT VERIFIED.
- Disposition: repository/schema inventory PASS (static only); current canonical DB existence/access, current integrity, full M15/H1 coverage, provenance completeness, recovery continuity and backup/restore **BLOCKED / NOT VERIFIED**.
- No database/runtime/VPS access, copy/export/restore, source/test/workflow/dependency changes, tests or workflow runs. Documentation-only commit.
- Next: identify an owner-held canonical SQLite file or immutable backup and its approved read-only access location. No initializer, writer, restore, or migration action is authorized.


### Canonical data external recovery source search — 2026-11-19

- Owner explicitly authorized read-only external source inspection.
- Evidence: [T0 Canonical Data Recovery Source Search](evidence/T0_CANONICAL_DATA_RECOVERY_SOURCE_SEARCH_2026-11-19.md), commit `137f104ba3a1fb5bb748a256e7037fb87f27c58e`.
- Historical source inventory (blob `92b36a488619512ef64297b53a8fadb7db8608d8`, exact source HEAD `93f3b0e350cf62b205f8d2a3a84fd139e9c5f59e`) scanned a complete 994-entry tree and found no tracked raw candle/database payload or canonical M15/H1 bundle. Nine selected T0 Actions artifacts contained test/runtime logs only; two P1.8 artifacts were synthetic. Historical run listing covered newest 1,000 of 1,387 only.
- Current known-run artifact spot check: run `44272495963` artifact `14413755795` is Core-First code operational proof (not market data). Known runs `42021445350` and `41996998169` returned 404 from artifact listing. GitHub Releases listing and a fresh exhaustive Actions-run listing are NOT VERIFIED because the connected GitHub tool set exposes no such list operations.
- Dropbox active indexed search returned no matches for 16 relevant queries. Deleted/unindexed content, other accounts and local devices were not inspected.
- Status: selected GitHub artifacts **PASS — NOT DATA**; Dropbox search **NO MATCHES**; Releases **NOT VERIFIED**; exhaustive Actions history **PARTIAL**; canonical backup **NOT IDENTIFIED**; recovery readiness **BLOCKED / NOT VERIFIED**.
- No data downloaded/exported/restored, no runtime/VPS/SSH/API/exchange access, no workflow dispatch, no source/test/workflow/dependency/schema changes. Documentation-only; no workflow run/job/artifact.
- Next: inspect Releases in authenticated GitHub UI or provide an exact release asset URL; identify other owner-held cloud/local/device snapshots. If none exists, prepare a separate owner-approval proposal for RECONSTRUCTED Binance USD-M history. No reconstruction, download, T0 initialization, writer or canonical acceptance is authorized.


---

# CURRENT STATUS OVERRIDE — 2026-11-19 — Canonical SQLite + Dropbox snapshot design (Phase 1 only)

- Owner decision: Dropbox is the versioned, downloadable repository for validated official Canonical SQLite snapshots; it is not the live operational primary.
- Operational primary remains on a controlled local filesystem suitable for SQLite locking and writes. Never synchronize an actively written SQLite database or its WAL/SHM files directly through Dropbox.
- Design: `docs/decisions/T0_CANONICAL_SQLITE_DROPBOX_SNAPSHOT_DESIGN_2026-11-19.md`, commit `f0df0617c46a476ed89f313cbebf1c7e7f450fd2`.
- Snapshot protocol uses SQLite Online Backup API to a staging path, then closes and validates the snapshot, computes SHA-256, emits a provenance/coverage manifest, uploads as a new immutable version, and requires read-back checksum verification. Restore occurs to a separate destination and requires validation before any cutover.
- Official/verified acceptance requires SQLite integrity, schema, row counts, M15/H1 coverage, gaps, duplicate/OHLCV checks, lineage, manifest and checksum. A snapshot without a successful restore drill is only UPLOADED / NOT RESTORE-VERIFIED.
- Reconstructed market history must be explicitly labeled `RECONSTRUCTED`; it must never be represented as recovery of the historical original database.
- Authorization: **Phase 1 DESIGN / STATIC ONLY**. Static implementation checks and independent review are **NOT YET PERFORMED**. No database initialization, exchange download, data copy/export, snapshot, Dropbox upload, restore, VPS/runtime, writer/lease/feeder or deployment is authorized.
- No tests or workflows were run; no test run, job or artifact exists for this documentation-only increment.
- Next: bounded static review of the manifest/acceptance contract and update this handoff. Any reconstruction, snapshot/Dropbox operation, restore drill or primary cutover requires separate explicit approval.


---

# CURRENT STATUS OVERRIDE — 2026-11-19 — Canonical Dropbox snapshot design static review

- Static review report: `docs/reviews/T0_CANONICAL_SQLITE_DROPBOX_SNAPSHOT_STATIC_REVIEW_2026-11-19.md`, commit `c08d5e225140d02235206d4dabc4e24349370f3f`.
- Clarified design: `docs/decisions/T0_CANONICAL_SQLITE_DROPBOX_SNAPSHOT_DESIGN_2026-11-19.md`, update commit `d7274fa2678caca5a0fedb8ca64083809cdf356c`.
- Review baseline main HEAD: `5955423a8edc1661e9cd4f9b7b80a317c6bc77cf`. Read-only inspection covered the design, SQLite initializer/store/storage and feeder source, and prior T0 inventory.
- Verdict: **PASS WITH REQUIRED SPECIFICATION CLARIFICATIONS**. R1–R5 recorded: Dropbox create-only/no-overwrite plus file ID/revision and exact-revision readback; owner-approved M15/H1 UTC coverage/gap policy; mandatory provenance manifest; SQLite Online Backup API and isolated restore path/sidecar handling; explicit manifest validation/status transitions. R6 records `PRAGMA user_version` validation.
- Static source finding: no snapshot publisher, Dropbox adapter, manifest validator or restore verifier exists in the inspected repository scope. No implementation or restore behavior is proven.
- Coverage boundaries and acceptable-gap policy remain **BLOCKED pending owner decision**. No snapshot can be marked OFFICIAL / VERIFIED before those are approved and checked.
- No source/test/workflow/dependency/schema/data changes; no SQLite opened, exchange access, Dropbox action, VPS/runtime, snapshot, restore or cutover. No tests/workflows run; no run/job/artifact exists.
- Phase 1 remains DESIGN / STATIC ONLY. Next: owner review of clarified specification, including explicit M15/H1 coverage boundaries and gap policy. Implementation proposal requires separate approval.
