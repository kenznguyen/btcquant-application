# PAPER Risk Policy Authoring and Publication

This directory is the Git-reviewed authoring source for PAPER risk policies.

## Authoring rules

- Use `schema-v1.json` for each immutable policy document.
- Create one file per policy version, for example `paper-risk-v1.json`; never edit a published version in place.
- Policy changes require review and a commit on the existing application branch.
- A manifest conforming to `active-manifest.schema.json` identifies the exact policy version, file path, file SHA-256, schema version and source commit.
- No active policy document or numeric threshold is defined by this schema-only change. Do not infer thresholds or create defaults.
- No secrets, API keys or credentials belong in policy files.

## Publication and runtime

- Publication is an explicit manual operator action from an exact reviewed Git commit and file.
- The publisher must verify the commit/path/file bytes and SHA-256 before calling the SQLite publication API.
- SQLite stores the full canonical policy payload, policy/schema version, exact source commit and file hash, operator/reason/time, previous version/hash, and immutable publication audit.
- The active pointer is updated in one SQLite transaction using compare-and-swap against the previously active payload hash. Stale publishers must fail without changing the active policy.
- Published versions and audit rows are append-only. Runtime loads only the persisted active SQLite policy; it does not fetch GitHub or read environment-variable risk thresholds.
- Environment variables must not provision or override the versioned policy.

## Drawdown semantics

`drawdownLimit.mode` is mandatory and must be explicit:

- `ABSOLUTE_QUOTE`: `value` is a quote-asset loss amount.
- `PERCENT_HWM`: `value` is a percentage of high-water mark.

No percentage-to-quote conversion is implicit. The current SharedRiskEngine V1 policy adapter accepts absolute quote drawdown only. A `PERCENT_HWM` policy must remain inadmissible until the snapshot and engine contract explicitly support and test high-water-mark percentage semantics.

## Current status

Schema and isolated SQLite publication contract are under test. No production policy values, active manifest, operational database migration, Provider, or Core/AI caller wiring is created by this schema definition.
