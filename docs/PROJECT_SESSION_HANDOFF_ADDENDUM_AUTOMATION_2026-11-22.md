# Project Session Handoff Addendum — Maximum Automation

Date: 2026-11-22
Repository: `kenznguyen/btcquant-application`
Branch: `main`

## Current governance decision

- Decision: `docs/decisions/AUTOMATION_MAXIMUM_EXPLICIT_PERMISSION_EXPANSION_2026-11-22.md`.
- Decision commit: `78cce40c3443afc437aab4a5aeb804026263c8d4`.
- Policy: **OWNER APPROVED — GOVERNANCE POLICY**.
- Operating model: **Maximum Automation — Explicit Approval for Permission Expansion**.
- Automate routine work already covered by an active owner-approved scope; do not request repeated approval for ordinary substeps.
- If the next action requires broader permissions, a new protected resource, or a higher-risk operation, continue independent authorized work, prepare a bounded approval request, and stop before crossing the boundary.
- Approval applies only to the exact approved delta. Silence, ambiguity, prior unrelated approval or technical capability is not authorization.

## Mandatory boundaries retained

This governance policy does not grant blanket technical permission. Existing decisions and exclusions remain effective, including:

- GitHub Actions First; E2B remains a separately approved exception.
- B4 resource ceilings and fail-closed behavior remain unchanged.
- B6 source/staging/private evidence is preserved until explicit deletion approval; sanitized CI artifacts remain limited to 30 days where applicable.
- B7 destination/preflight requirements remain unchanged.
- Real archive access, protected/Canonical database operations, host/SSH/filesystem/preflight, credentials/secrets, deployment, runtime integration, T0/T1/T2 boundary changes, exchange connectivity, trading and deletion require specific approval.
- Manual/on-demand and no-autostart restrictions remain unchanged unless separately amended.
- No source code, workflow, secret, runtime, data, database or host state was changed by this policy record.

## Status

- Governance policy record: **COMMITTED**.
- Automatic enforcement across every workflow/tool: **NOT VERIFIED / NOT IMPLEMENTED**.
- Existing workstream approvals: unchanged; verify exact scope before execution.
- Next: apply this scope-based authorization model to subsequent work, and request only the minimum additional permission needed when a genuine boundary is reached.
