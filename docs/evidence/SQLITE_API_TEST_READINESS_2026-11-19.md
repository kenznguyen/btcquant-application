# SQLite/API Test Readiness — 2026-11-19

- Repository: `kenznguyen/btcquant-application`
- Branch: `main`
- Exact inspected HEAD: `358aaf47367a721d2db4f51bd1ffc5e152440f30`
- Scope: owner-approved read-only readiness review of Python compatibility, dependencies, test discovery and isolation. This report records static inspection only.

## 1. Python compatibility

- No target `pyproject.toml`, `setup.cfg`, `tox.ini`, `runtime.txt` or other explicit Python-version declaration was found in the repository root.
- Static source inspection found a PEP 604 union annotation (`str | None`) in `market_data/feeder.py` (blob `299a9b5a8b1ebd581eb620d5ee860d9f9ff5dc5c`).
- This syntax requires Python 3.10 or newer when evaluated normally. Therefore **Python >=3.10 is the inferred minimum for the current T0 source**, not an owner-pinned or executed compatibility guarantee.
- No Python interpreter matrix or runtime compatibility test was run.

## 2. Dependency readiness

- Target repository has no `requirements.txt`, `pyproject.toml`, `setup.cfg` or `Pipfile`.
- The source repository's `requirements.txt` blob is `f5c242bdac51eba200b19233e08e7d4b22f598c4`, with ranges:
  - `requests>=2.32.0,<3`
  - `numpy>=1.26.0,<3`
  - `pandas>=2.2.0,<3`
  - `Flask>=3.0.0,<4`
  - `gunicorn>=22.0.0,<24`
  - `cryptography>=42.0.0,<47`
  - `rfc8785>=0.1.4,<0.2`
- That source manifest does not declare `ccxt` or `psycopg`; both are lazy imports in the application paths for exchange collection and PostgreSQL respectively.
- Static import inspection of the six selected SQLite/API test modules and their direct T0 dependencies found only Python standard-library imports. The API is a direct WSGI application and does not import Flask. The SQLite test paths do not require CCXT or Psycopg.
- Therefore, **no third-party package is statically indicated as necessary for the scoped six-module SQLite/API test suite**. This is not yet confirmed by interpreter execution; import-time hidden dependencies or environment issues remain possible.
- Do not copy the legacy requirements file wholesale or guess versions as part of this readiness gate. The wider application/runtime dependency manifest remains NOT VERIFIED.

## 3. Test discovery and inventory

The target currently contains six T0 test modules:
| Module | Declared test methods |
|---|---:|
| `test_feeder_recovery.py` | 10 |
| `test_feeder_lease.py` | 10 |
| `test_write_gateway.py` | 11 |
| `test_storage.py` | 7 |
| `test_sync.py` | 10 |
| `test_api.py` | 13 |
| **Total** | **61** |

- All six use `unittest.TestCase`; no pytest-only fixtures or pytest imports were identified.
- The source directory has no `market_data/__init__.py`. Python namespace-package imports are supported by Python 3.10; a discovery invocation should be run from repository root so that imports of `market_data.*` resolve.
- Candidate discovery command (NOT EXECUTED):
  ```sh
  python -m unittest discover -s market_data -p 'test_*.py' -v
  ```
- This is a proposed invocation, not proof that discovery succeeds. The actual test count and outcomes must come from a future test run.

## 4. Static isolation review

- `test_feeder_recovery.py`: injected/mock recovery callbacks; no network or database connection identified.
- `test_feeder_lease.py`: uses temporary local SQLite database and local threads.
- `test_write_gateway.py`: uses temporary SQLite paths; its child process writes to the test's temporary database and is bounded by a timeout.
- `test_storage.py`: uses temporary SQLite paths and configuration mappings; PostgreSQL connection failure path is exercised without requiring a working database service.
- `test_sync.py`: uses an in-memory mock exchange object. Its subprocess cases request module help or verify the CLI rejects a request lacking `--shadow-only`; they do not make a Binance request.
- `test_api.py`: invokes the WSGI application directly, patches environment variables, and uses temporary SQLite databases. Its PostgreSQL negative case verifies fail-closed behavior without a DSN.
- No reviewed test path intentionally accesses canonical T0 data, a shared DB, an exchange API, a deployed HTTP service or live order execution.
- This is static source review only; process-level network isolation and actual test behavior are NOT VERIFIED.

## 5. CI/workflow inventory

- The target repository root listing contains only `README.md`, `docs/` and `market_data/`.
- `.github/workflows/` is absent (GitHub contents lookup returned 404); no target GitHub Actions workflow is available to dispatch.
- No workflow run, job, log or artifact exists for this readiness review.
- Do not use source-repository CI runs as evidence for the target repository.

## 6. Readiness verdict

| Gate | Status | Evidence |
|---|---|---|
| Python minimum | CONDITIONAL PASS | Static syntax implies >=3.10; no declared/pinned runtime |
| Scoped test dependencies | CONDITIONAL PASS | Standard-library imports in reviewed test paths; not executed |
| Test framework | PASS (static) | Six modules use unittest |
| Test inventory | PASS (static) | 61 declared test methods |
| Candidate discovery command | NOT VERIFIED | Command proposed, not run |
| Test isolation | PARTIAL PASS | Temporary SQLite/mock/direct WSGI; no runtime network sandbox proof |
| Target CI | BLOCKED / NOT AVAILABLE | No `.github/workflows/` |
| Test execution | NOT RUN | No interpreter/test command invoked |
| Runtime / canonical data | NOT ACCESSED | Out of scope |
| Production readiness | NOT CERTIFIED | No execution or runtime evidence |

## 7. Recommended next gate

A separate owner approval is required before test execution. Recommended bounded execution:
1. Use a disposable clean environment with Python 3.10+ (prefer a currently supported Python version once explicitly selected).
2. Start from repository root and run the candidate unittest discovery command above.
3. Disable network access at the execution environment level; do not rely solely on test mocks.
4. Use a clean environment with no inherited market-data DB/DSN/token settings; verify every SQLite file is under test-owned temporary directories.
5. Do not install packages unless the interpreter run demonstrates a missing dependency and the owner separately approves the exact package/version.
6. Do not run PostgreSQL/TimescaleDB tests, exchange collection, Feeder/API services, canonical DB operations, VPS/runtime actions or trading.
7. Record exact interpreter version, command, exit code, discovered/passed/failed/skipped counts, logs and source SHA.

No source, tests, dependency manifests, workflows, schemas or runtime settings were modified in this readiness review. No package was installed; no test or workflow was executed.
