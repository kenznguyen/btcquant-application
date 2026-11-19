# T0 HTTP Consumer Migration Scope Review — 2026-11-19

## 1. Review boundary and source identity

Read-only review of the approved TDD migration scope against the active Core First source branch. No source or test files were edited. No tests or workflows were run. No endpoint, network, database, credentials, runtime, VPS or deployment was accessed.

- Consumer repository: `kenznguyen/btcusdt-telegram-signals2`
- Branch: `feature/core-operational-proof-20261112`
- Compared source SHA: `e6606e28a696374f31cd6db1ec0a1372d942d64d`
- GitHub compare of inspected SHA against current branch ref: `identical`, ahead 0 / behind 0.
- Reviewed client blob: `freqai_bridge/http_candles.py` — `1f430c6d3a762deab9342e42072824661df3bf96`
- Reviewed normalizer blob: `core_runtime/bundle_inputs.py` — `f78ebde30413a3329063a2c68c457fe862a50c5e`
- Reviewed provider blob: `core_runtime/bundle_provider.py` — `9d67f1600d4177e6f9756e366af6ef9319b27c19`
- Reviewed runtime factory blob: `core_runtime/runtime_factory.py` — `b2dbd2efe0076ad5e831682caea0bd5e4a4f8bd6`
- Reviewed Common API blob: `pipeline/api.py` — `bb89b0bdf196f64b3ab9d9ac15b6597f333c583e`
- Reviewed client test blob: `freqai_bridge/test_http_candles.py` — `8b38048e72d781d9219de1fe789e7078962c4824`

## 2. Review verdict

**Scope is directionally correct, but implementation must not begin until the design clarifications in section 3 are incorporated and separately authorized.** The most important issue is that the existing multi-page `fetch()` does not merely validate the T0 envelope: it synthesizes a new envelope and currently labels it contract `1.0.0`, derives freshness from `generatedAtMs`, and unconditionally sets `evaluable=true`. A simple version bump or permissive field-set change would preserve incorrect semantics.

## 3. Required design clarifications before implementation

### A. Separate a T0 page envelope from an assembled consumer window

Current `fetch()`:
- requests up to 32 candles per page;
- validates each page as contract 1.0.0;
- concatenates candles;
- synthesizes a dataset digest for multi-page windows;
- returns a new envelope labelled `contractVersion: 1.0.0`;
- calculates observation/close ages from max `generatedAtMs`;
- derives latest expected candle from generated time;
- unconditionally sets `freshness.evaluable=true`.

For contract 1.1.0, do not simply change the returned version to 1.1.0. That would falsely imply the synthesized multi-page object is an original T0-owned 1.1.0 response. Define an explicit internal assembled-window result/schema (or an equally clear adapter boundary) distinct from the T0 page envelope. It must carry source contract/version, evaluation anchor/time, timestamp validity, coverage, final-window freshness/evaluability, and constituent dataset provenance without fabricating a T0 server verdict.

### B. Page-level validation versus final-window evaluability

For every page:
- enforce exact T0 1.1.0 envelope and freshness schema;
- validate candle identity, timestamp validity, page coverage, ordering and availability constraints;
- preserve the server's page verdict and evaluation anchor;
- do not reject an otherwise valid historical page solely because its latest candle is not fresh relative to the overall evaluation anchor.

For the assembled window:
- ensure all pages share the same requested range semantics and evaluation anchor;
- reject any page with invalid timestamps, incomplete coverage, malformed identity or inconsistent anchors;
- derive final-window freshness/evaluability from the final expected/returned candle and authoritative 1.1.0 rules at the same anchor;
- never set `evaluable=true` merely because all page requests returned successfully.

### C. Preserve the Core decision path's stricter requirement

`CoreBundleProvider` uses `fetch_one_page()` for 100 M15 and 100 H1 candles. This is a single T0 response per timeframe (within T0's 2,000-candle response limit), not the 32-candle paginated `fetch()` path. Core Bundle construction must continue to fail closed unless the requested decision window satisfies the authoritative 1.1.0 evaluability rule at its `asOfMs` anchor.

Do not weaken Core's readiness gate to make historical multi-page research/dashboard reads pass.

### D. Bundle normalizer and provenance

`normalize_candle_window()` independently hard-requires `contractVersion == 1.0.0` and an exact frozen envelope field set. Update tests and design for 1.1.0 as a separate explicit contract revision. Preserve 1.1.0 evaluation metadata and provenance in the Core Bundle; do not strip the new quality fields or recalculate them from wall-clock time.

### E. Keep ingestion policy separate

The existing consumer `max_lag_ms` check is an ingestion-delay policy based on `availableAtMs - closeTimeMs`. Keep this independent from 1.1.0 `fresh` and `evaluable`. A page may be historically valid while not fresh for the final evaluation point; ingestion delay must not be used as a substitute for the server's evaluability decision.

## 4. Test matrix amendments

Keep the approved matrix and add/clarify:
- direct Core one-page 100-candle M15 and H1 envelopes;
- the T0 endpoint maximum page size (2,000) separately from the client's 32-candle pagination chunk and 3,000-candle assembled-window cap;
- single-page and multi-page result types, explicitly proving an assembled window is not mislabelled as a raw T0 envelope;
- mixed `generatedAtMs` values with a common `evaluationTimeMs`/`evaluationAnchor`;
- page-anchor mismatch, page overlap, missing range, duplicate candle and out-of-order page rejection;
- final-page `fresh=false` and `evaluable=false` rejection for Core decision bundles;
- historical non-final pages with `fresh=false`/`evaluable=false` accepted only as valid components of a complete assembled research/dashboard window, subject to final-window verdict;
- tests proving no code path manufactures `evaluable=true` or silently changes contract versions;
- Common API behavior for both Core one-page calls and 96-bar dashboard windows.

## 5. Recommended implementation order after separate approval

1. Reconfirm branch ref remains identical to the inspected SHA and inspect working-tree/branch protections through the repository workflow; do not overwrite newer work.
2. Write RED tests for the explicit raw-page versus assembled-window boundary first.
3. Implement 1.1.0 page validation and assembled-window aggregation as separate, typed responsibilities.
4. Migrate Core Bundle normalizer and its fixtures; retain fail-closed decision readiness.
5. Verify Common API, dashboard and Android parsing behavior without runtime connections.
6. Run only approved isolated synthetic tests and exact-SHA CI; record run/job/artifact/checksum.
7. Obtain independent code review before considering any endpoint or runtime gate.

## 6. Status

| Item | Status |
|---|---|
| Approved TDD scope read-only review | PASS WITH DESIGN AMENDMENTS |
| Contract 1.1.0 client compatibility | BLOCKED |
| Raw-page / assembled-window boundary | DESIGN CLARIFICATION REQUIRED |
| Core Bundle 1.1.0 normalization | BLOCKED |
| Source edits | NOT STARTED |
| Tests / CI | NOT RUN |
| Endpoint / runtime | NOT VERIFIED; NOT AUTHORIZED |
| Production readiness | NOT CERTIFIED |

No implementation, tests, workflow dispatch, endpoint probe, runtime connection, deployment, canonical data access, strategy execution or trading is authorized by this review.
