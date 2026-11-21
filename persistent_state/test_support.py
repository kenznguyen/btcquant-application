"""Synthetic-only helpers for isolated persistent-state contract tests."""
from persistent_state.evidence import (
    EvidenceBinding, PreflightAttestation, ReadyEvidenceBundle,
    RestoreAttestation, RiskReadinessAttestation,
)


def ready_evidence_for(session, fencing_token, *, checked_at_ms=None):
    checked = max(
        session.started_at_ms,
        session.started_at_ms + 1 if checked_at_ms is None else checked_at_ms,
    )
    binding = EvidenceBinding(
        session_id=session.session_id,
        account_scope_id=session.account_scope_id,
        fencing_generation=fencing_token.fencing_generation,
        config_hash=session.config_hash,
        source_snapshot_id=session.source_snapshot_id,
        checked_at_ms=checked,
    )
    return ReadyEvidenceBundle(
        preflight=PreflightAttestation(
            binding=binding,
            market_data_snapshot_id=session.source_snapshot_id,
            data_as_of_ms=checked,
            coverage_json='{"15m":200,"1h":100}',
            provenance="test-only.synthetic",
            schema_version=1,
            passed=True,
        ),
        restore=RestoreAttestation(
            binding=binding,
            checkpoint_id="synthetic-empty-or-replayed-state",
            checkpoint_checksum="sha256:" + "b" * 64,
            last_event_sequence=session.last_committed_event_sequence,
            aggregate_versions_json="{}",
            core_ledger_reconciled=True,
            ai_ledger_reconciled=True,
            passed=True,
        ),
        risk=RiskReadinessAttestation(
            binding=binding,
            risk_policy_version="test-only-risk-v1",
            kill_switch_latched=False,
            account_equity_quote="10000",
            ledger_reconciled=True,
            passed=True,
        ),
    )
