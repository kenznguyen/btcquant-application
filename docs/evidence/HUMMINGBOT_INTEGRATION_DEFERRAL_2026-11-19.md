# Hummingbot integration deferral decision — 2026-11-19

## Decision
The owner confirms that Hummingbot is **temporarily not integrated into the current system** to reduce implementation and verification complexity. The target architecture retains the option to integrate Hummingbot in a later, separately approved phase.

## Repository treatment
- Keep `integrations/hummingbot_bridge.py` in the application repository as a provenance-preserved adapter from the approved F4 snapshot migration.
- Treat the adapter as dormant / not activated. Its presence does not imply runtime integration, dependency installation, connection, or operational support.
- Do not add Hummingbot dependencies, configuration, endpoints, workflows, runtime wiring, or connectivity checks under this decision.
- Do not remove or rewrite the adapter as part of this documentation-only decision.
- Any future activation or removal requires a separate scoped review and explicit approval.

## Evidence and scope
- Repository: `kenznguyen/btcquant-application`
- Branch: `main`
- Parent HEAD before this record: `fd983d51af84dc2c0ed3b6793fb41a18988535ad`
- Existing adapter migration commit: `aafdd95c9b2869f58c75e937ebe95db27af8939a`
- Adapter source/target blob SHA: `aa9db7522ffb7ce911c7fbbdc73a7f9b47401331`
- Decision: documentation-only; no application source, tests, dependencies, workflow, runtime, database, T0 asset, VPS, exchange, or trading behavior changed or accessed.
- Tests/import/build/CI: NOT RUN; no behavior change was made.
- Runtime integration and Hummingbot connectivity: NOT VERIFIED.

## Status
- Temporary Hummingbot deferral: **DECIDED**
- Target architecture option retained: **DECIDED**
- Adapter provenance retained: **PASS** (existing migration record; no source modification)
- Runtime integration/connectivity: **NOT VERIFIED**
- Hummingbot activation: **NOT AUTHORIZED**
- Paper execution remains NOT AUTHORIZED; live trading remains PROHIBITED.

## Next step and limits
Continue the separately approved Core-First/F4 work without Hummingbot activation. Revisit Hummingbot only through a future explicit architecture and implementation approval.
