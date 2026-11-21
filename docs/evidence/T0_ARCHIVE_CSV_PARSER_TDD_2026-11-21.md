# T0 Offline Archive CSV Parser — TDD Evidence

**Date:** 2026-11-21  
**Repository:** `kenznguyen/btcquant-application`  
**Branch:** `main`  
**Status:** **PASS — BOUNDED OFFLINE PARSER + FOCUSED SYNTHETIC TESTS**  
**Source commit / tested snapshot:** `c600e8b3680466241a45b429c76215b538927904`

## 1. Approved scope

Owner approved a separate TDD increment to implement a pure offline parser and tests using only the two already committed synthetic fixtures. Scope excludes real archive/REST access, personal host/VPS, SQLite creation or writes, Canonical T0, Contract 1.2.0 schema/API changes, importer, GitHub Actions workflow changes, runtime, deployment and trading.

## 2. Changed files and exact identities

| File | Blob SHA | Role |
|---|---|---|
| `market_data/archive_csv_parser.py` | `7d59706778a98a18185e0b2fe744c3c43c2eb870` | Pure CSV parser and immutable typed row |
| `market_data/test_archive_csv_parser.py` | `df237f495c253c053b29e5ca76c50aad060ba85d` | 19 focused unittest methods |
| `tests/fixtures/t0/binance_um_btcusdt_m15_synthetic.csv` | `1a616fde511407d90be8894391e783e716908c9d` | Synthetic M15 input |
| `tests/fixtures/t0/binance_um_btcusdt_h1_synthetic.csv` | `951f26ff4e4a6c330a14f5a515cc27cce8053e1e` | Synthetic H1 input |
| `tests/fixtures/t0/README.md` | `576cfd619af0ead0c3b864b4fe9e0ddcb33e08ae` | Fixture/parser limitations and usage |

Source commits:
- RED test specification: `0d4dc02ce9b3a48b01144e4b71b3fa4b016c3bc0`
- Parser implementation: `2413d4f94c8f85d619190897d8236ba6e32896fe`
- Numeric edge-case tests: `c64545bd8ec371b2c1cd3e612697c25e1cbd2c3a`
- Final test naming/clarity: `c600e8b3680466241a45b429c76215b538927904`
- Fixture documentation: `0d9ec85591d0826e5f0e9c43bfb43b41f7698ac3`

## 3. TDD evidence

### RED

Before `market_data/archive_csv_parser.py` existed, the focused unittest invocation failed with:

`ModuleNotFoundError: No module named 'market_data.archive_csv_parser'`

This demonstrated the missing behavior. The initial RED module had 18 test methods; one signed-timestamp boundary test was added during GREEN hardening.

### GREEN

Command:

```bash
python -B -m unittest -v market_data.test_archive_csv_parser
```

Result: **19 tests PASS**.

The local isolated scratch harness used byte-for-byte Git blob-matched copies of the final parser source, final test module and both synthetic fixture files. Runtime: Python 3.13. This is a local focused test result, not a GitHub Actions run and not a test of the full repository checkout.

Coverage includes:
- M15/H1 fixture parsing and exact Decimal values;
- immutable result rows and retention of all 12 raw fields;
- strict headerless 12-field row shape;
- unsupported timeframe, blank/malformed CSV, non-integer/out-of-range timestamps;
- timeframe alignment and inclusive close-time validation;
- finite plain-decimal grammar and token-length bound;
- OHLC envelope, nonnegative volume fields and integer trade count;
- taker-buy volume bounds;
- strictly increasing open timestamps.

## 4. Parser behavior

The parser exposes `parse_archive_csv(text, timeframe=...)`, returns immutable typed rows, uses `Decimal` without binary floating-point conversion, retains all 12 source fields and derives the exclusive bar-close boundary only after checking the provisional inclusive source close timestamp.

It performs no filesystem, network, exchange, archive, database or SQLite I/O. It does not assign exchange/symbol identity, create candles in a database, or mutate any data asset.

## 5. Verification status and limits

- TDD RED reproduction: **PASS**.
- Focused synthetic parser tests: **PASS — 19/19**.
- Exact parser/test/fixture blob identity against GitHub: **PASS**.
- GitHub Actions run/job/artifact: **NOT RUN / NOT APPLICABLE** — workflow YAML changes were outside the approval.
- Full repository regression: **NOT RUN**.
- Self-review: **PASS WITH LIMITS** — parser is deliberately strict and bounded to the provisional mapping; no real-source assumptions are promoted to verified facts.
- Real Binance archive CSV compatibility, header/encoding/delimiter/member name, actual numeric grammar and timestamp convention: **NOT VERIFIED**.
- Parser contract freeze: **BLOCKED** pending separately approved real-source evidence or owner decision accepting the residual risk.
- Contract 1.2.0 schema/API, importer, workflow, archive materialization, SQLite staging, Canonical T0, runtime and deployment: **NOT AUTHORIZED**.

No archive or REST request, host/VPS access, database/SQLite operation, Canonical data mutation, T1/T2 runtime connection, exchange credential use, order placement or trading operation occurred.
