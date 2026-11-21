import unittest
from dataclasses import replace

from persistent_state.contracts import SessionRecord, SessionStatus
from persistent_state.evidence import (
    EvidenceBinding,
    PreflightAttestation,
    RestoreAttestation,
    RiskReadinessAttestation,
    validate_ready_evidence,
)


CONFIG_HASH = "sha256:" + "a" * 64
CHECKSUM = "sha256:" + "b" * 64


def session():
    return SessionRecord(
        session_id="session-1",
        account_scope_id="paper-account",
        status=SessionStatus.RESTORING,
        started_at_ms=1_800_000_000_000,
        initiator="MANUAL",
        source_snapshot_id="snapshot-1",
        config_hash=CONFIG_HASH,
        code_version="git:" + "c" * 40,
        last_committed_event_sequence=3,
    )


def binding(*, session_id="session-1", generation=7, config_hash=CONFIG_HASH,
            snapshot_id="snapshot-1", checked_at_ms=1_800_000_000_100):
    return EvidenceBinding(
        session_id=session_id,
        account_scope_id="paper-account",
        fencing_generation=generation,
        config_hash=config_hash,
        source_snapshot_id=snapshot_id,
        checked_at_ms=checked_at_ms,
    )


def evidence():
    return (
        PreflightAttestation(
            binding=binding(),
            market_data_snapshot_id="snapshot-1",
            data_as_of_ms=1_800_000_000_000,
            coverage_json='{"15m":200,"1h":100}',
            provenance="ccxt.binanceusdm",
            schema_version=1,
            passed=True,
        ),
        RestoreAttestation(
            binding=binding(),
            checkpoint_id="checkpoint-3",
            checkpoint_checksum=CHECKSUM,
            last_event_sequence=3,
            aggregate_versions_json='{"ai-ledger":1,"core-ledger":2}',
            core_ledger_reconciled=True,
            ai_ledger_reconciled=True,
            passed=True,
        ),
        RiskReadinessAttestation(
            binding=binding(),
            risk_policy_version="shared-risk-v1",
            kill_switch_latched=False,
            account_equity_quote="10000",
            ledger_reconciled=True,
            passed=True,
        ),
    )


class ReadyEvidenceContractTests(unittest.TestCase):
    def test_matching_successful_evidence_allows_ready(self):
        preflight, restore, risk = evidence()
        validate_ready_evidence(
            session(), fencing_generation=7,
            preflight=preflight, restore=restore, risk=risk,
        )

    def test_missing_attestation_is_rejected(self):
        preflight, restore, _ = evidence()
        with self.assertRaises(ValueError):
            validate_ready_evidence(
                session(), fencing_generation=7,
                preflight=preflight, restore=restore, risk=None,
            )

    def test_wrong_session_or_fencing_generation_is_rejected(self):
        preflight, restore, risk = evidence()
        wrong_generation = replace(risk, binding=binding(generation=6))
        with self.assertRaises(ValueError):
            validate_ready_evidence(
                session(), fencing_generation=7,
                preflight=preflight, restore=restore, risk=wrong_generation,
            )

    def test_config_or_market_snapshot_mismatch_is_rejected(self):
        preflight, restore, risk = evidence()
        wrong_snapshot = replace(
            preflight, binding=binding(snapshot_id="other-snapshot"),
        )
        with self.assertRaises(ValueError):
            validate_ready_evidence(
                session(), fencing_generation=7,
                preflight=wrong_snapshot, restore=restore, risk=risk,
            )

    def test_failed_preflight_restore_or_risk_attestation_is_rejected(self):
        for index in range(3):
            items = list(evidence())
            items[index] = replace(items[index], passed=False, reason_codes=("BLOCKED",))
            with self.subTest(attestation=index), self.assertRaises(ValueError):
                validate_ready_evidence(
                    session(), fencing_generation=7,
                    preflight=items[0], restore=items[1], risk=items[2],
                )

    def test_risk_readiness_rejects_latched_kill_switch(self):
        preflight, restore, risk = evidence()
        risk = replace(risk, kill_switch_latched=True)
        with self.assertRaises(ValueError):
            validate_ready_evidence(
                session(), fencing_generation=7,
                preflight=preflight, restore=restore, risk=risk,
            )

    def test_restore_requires_both_strategy_ledgers_reconciled(self):
        preflight, restore, risk = evidence()
        restore = replace(restore, ai_ledger_reconciled=False)
        with self.assertRaises(ValueError):
            validate_ready_evidence(
                session(), fencing_generation=7,
                preflight=preflight, restore=restore, risk=risk,
            )


if __name__ == "__main__":
    unittest.main()
