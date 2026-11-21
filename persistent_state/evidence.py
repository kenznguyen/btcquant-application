"""Typed, session-bound evidence required before a session can become READY.

This module is pure validation: it performs no I/O and cannot start execution.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import json
import re

from persistent_state.contracts import SessionRecord, SessionStatus, canonical_json


_SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")


def _nonempty(name: str, value: object, *, maximum: int = 256) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise ValueError(f"{name} must be a non-empty string of at most {maximum} characters")
    return value


def _timestamp(name: str, value: object) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(f"{name} must be an integer >= 0")
    return value


def _sha256(name: str, value: object) -> str:
    if not isinstance(value, str) or not _SHA256.fullmatch(value):
        raise ValueError(f"{name} must use sha256:<64 lowercase hex characters>")
    return value


def _canonical_object(name: str, value: object) -> dict:
    if not isinstance(value, str):
        raise ValueError(f"{name} must be canonical JSON text")
    try:
        parsed = json.loads(value)
    except (TypeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{name} must be valid JSON") from exc
    if not isinstance(parsed, dict) or canonical_json(parsed) != value:
        raise ValueError(f"{name} must be a canonical JSON object")
    return parsed


@dataclass(frozen=True, slots=True)
class EvidenceBinding:
    session_id: str
    account_scope_id: str
    fencing_generation: int
    config_hash: str
    source_snapshot_id: str
    checked_at_ms: int

    def __post_init__(self) -> None:
        _nonempty("session_id", self.session_id)
        _nonempty("account_scope_id", self.account_scope_id)
        if type(self.fencing_generation) is not int or self.fencing_generation < 1:
            raise ValueError("fencing_generation must be an integer >= 1")
        _sha256("config_hash", self.config_hash)
        _nonempty("source_snapshot_id", self.source_snapshot_id)
        _timestamp("checked_at_ms", self.checked_at_ms)


@dataclass(frozen=True, slots=True)
class PreflightAttestation:
    binding: EvidenceBinding
    market_data_snapshot_id: str
    data_as_of_ms: int
    coverage_json: str
    provenance: str
    schema_version: int
    passed: bool
    reason_codes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.binding, EvidenceBinding):
            raise ValueError("preflight binding is required")
        _nonempty("market_data_snapshot_id", self.market_data_snapshot_id)
        _timestamp("data_as_of_ms", self.data_as_of_ms)
        coverage = _canonical_object("coverage_json", self.coverage_json)
        if set(coverage) != {"15m", "1h"} or any(
            type(coverage[timeframe]) is not int or coverage[timeframe] < 1
            for timeframe in ("15m", "1h")
        ):
            raise ValueError("coverage_json must contain positive 15m and 1h lookback counts")
        _nonempty("provenance", self.provenance)
        if type(self.schema_version) is not int or self.schema_version < 1:
            raise ValueError("schema_version must be an integer >= 1")
        _validate_outcome(self.passed, self.reason_codes)


@dataclass(frozen=True, slots=True)
class RestoreAttestation:
    binding: EvidenceBinding
    checkpoint_id: str
    checkpoint_checksum: str
    last_event_sequence: int
    aggregate_versions_json: str
    core_ledger_reconciled: bool
    ai_ledger_reconciled: bool
    passed: bool
    reason_codes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.binding, EvidenceBinding):
            raise ValueError("restore binding is required")
        _nonempty("checkpoint_id", self.checkpoint_id)
        _sha256("checkpoint_checksum", self.checkpoint_checksum)
        _timestamp("last_event_sequence", self.last_event_sequence)
        versions = _canonical_object("aggregate_versions_json", self.aggregate_versions_json)
        if any(type(version) is not int or version < 0 for version in versions.values()):
            raise ValueError("aggregate versions must be non-negative integers")
        if type(self.core_ledger_reconciled) is not bool or type(self.ai_ledger_reconciled) is not bool:
            raise ValueError("Core and AI reconciliation results must be boolean")
        _validate_outcome(self.passed, self.reason_codes)


@dataclass(frozen=True, slots=True)
class RiskReadinessAttestation:
    binding: EvidenceBinding
    risk_policy_version: str
    kill_switch_latched: bool
    account_equity_quote: str
    ledger_reconciled: bool
    passed: bool
    reason_codes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.binding, EvidenceBinding):
            raise ValueError("risk binding is required")
        _nonempty("risk_policy_version", self.risk_policy_version)
        if type(self.kill_switch_latched) is not bool or type(self.ledger_reconciled) is not bool:
            raise ValueError("Kill Switch and ledger reconciliation results must be boolean")
        if not isinstance(self.account_equity_quote, str):
            raise ValueError("account_equity_quote must be an exact decimal string")
        try:
            equity = Decimal(self.account_equity_quote)
        except InvalidOperation as exc:
            raise ValueError("account_equity_quote must be a finite positive decimal") from exc
        if not equity.is_finite() or equity <= 0:
            raise ValueError("account_equity_quote must be a finite positive decimal")
        _validate_outcome(self.passed, self.reason_codes)


@dataclass(frozen=True, slots=True)
class ReadyEvidenceBundle:
    """The complete evidence set required for the RESTORING -> READY transition."""

    preflight: PreflightAttestation
    restore: RestoreAttestation
    risk: RiskReadinessAttestation

    def __post_init__(self) -> None:
        if not isinstance(self.preflight, PreflightAttestation):
            raise ValueError("preflight attestation is required")
        if not isinstance(self.restore, RestoreAttestation):
            raise ValueError("restore attestation is required")
        if not isinstance(self.risk, RiskReadinessAttestation):
            raise ValueError("risk readiness attestation is required")



@dataclass(frozen=True, slots=True)
class OperatorResumeConfirmation:
    """Explicit operator approval plus a fresh risk attestation for Resume."""

    binding: EvidenceBinding
    operator_id: str
    confirmation_id: str
    confirmed_at_ms: int
    risk_attestation: RiskReadinessAttestation

    def __post_init__(self) -> None:
        if not isinstance(self.binding, EvidenceBinding):
            raise ValueError("operator confirmation binding is required")
        _nonempty("operator_id", self.operator_id)
        _nonempty("confirmation_id", self.confirmation_id)
        _timestamp("confirmed_at_ms", self.confirmed_at_ms)
        if not isinstance(self.risk_attestation, RiskReadinessAttestation):
            raise ValueError("fresh risk readiness attestation is required")
        if self.risk_attestation.binding != self.binding:
            raise ValueError("operator confirmation and risk evidence bindings must match")
        if self.confirmed_at_ms < self.binding.checked_at_ms:
            raise ValueError("operator confirmation cannot precede its risk check")


def _validate_outcome(passed: object, reason_codes: object) -> None:
    if type(passed) is not bool:
        raise ValueError("passed must be boolean")
    if not isinstance(reason_codes, tuple) or any(
        not isinstance(code, str) or not code.strip() for code in reason_codes
    ):
        raise ValueError("reason_codes must be a tuple of non-empty strings")
    if passed and reason_codes:
        raise ValueError("successful evidence cannot contain failure reason codes")
    if not passed and not reason_codes:
        raise ValueError("failed evidence must contain at least one reason code")


def _validate_binding(
    name: str,
    binding: EvidenceBinding,
    session: SessionRecord,
    fencing_generation: int,
) -> None:
    if binding.session_id != session.session_id:
        raise ValueError(f"{name} belongs to another session")
    if binding.account_scope_id != session.account_scope_id:
        raise ValueError(f"{name} belongs to another account scope")
    if binding.fencing_generation != fencing_generation:
        raise ValueError(f"{name} belongs to another fencing generation")
    if binding.config_hash != session.config_hash:
        raise ValueError(f"{name} config hash does not match the session")
    if binding.source_snapshot_id != session.source_snapshot_id:
        raise ValueError(f"{name} source snapshot does not match the session")
    if binding.checked_at_ms < session.started_at_ms:
        raise ValueError(f"{name} predates the session start")


def validate_ready_evidence(
    session: SessionRecord,
    *,
    fencing_generation: int,
    preflight: PreflightAttestation | None,
    restore: RestoreAttestation | None,
    risk: RiskReadinessAttestation | None,
) -> None:
    """Raise ValueError unless all successful attestations bind to this RESTORING session."""
    if not isinstance(session, SessionRecord) or session.status is not SessionStatus.RESTORING:
        raise ValueError("READY evidence can only be checked for a RESTORING session")
    if type(fencing_generation) is not int or fencing_generation < 1:
        raise ValueError("fencing_generation must be an integer >= 1")
    if not isinstance(preflight, PreflightAttestation):
        raise ValueError("successful preflight attestation is required")
    if not isinstance(restore, RestoreAttestation):
        raise ValueError("successful restore attestation is required")
    if not isinstance(risk, RiskReadinessAttestation):
        raise ValueError("successful risk readiness attestation is required")

    for name, attestation in (
        ("preflight", preflight), ("restore", restore), ("risk", risk),
    ):
        _validate_binding(name, attestation.binding, session, fencing_generation)
        if not attestation.passed:
            raise ValueError(f"{name} attestation did not pass")
    if preflight.market_data_snapshot_id != session.source_snapshot_id:
        raise ValueError("preflight market-data snapshot does not match the session")
    if restore.last_event_sequence != session.last_committed_event_sequence:
        raise ValueError("restore event sequence does not match the session event head")
    if not restore.core_ledger_reconciled or not restore.ai_ledger_reconciled:
        raise ValueError("both Core and AI ledgers must reconcile before READY")
    if risk.kill_switch_latched:
        raise ValueError("Kill Switch is latched")
    if not risk.ledger_reconciled:
        raise ValueError("risk ledger is not reconciled")



def validate_resume_confirmation(
    session: SessionRecord,
    *,
    fencing_generation: int,
    confirmation: OperatorResumeConfirmation | None,
) -> None:
    """Require explicit operator approval and a fresh passing risk check."""
    if not isinstance(session, SessionRecord) or session.status is not SessionStatus.READY:
        raise ValueError("Resume is permitted only for a READY session")
    if not isinstance(confirmation, OperatorResumeConfirmation):
        raise ValueError("explicit operator Resume confirmation is required")
    _validate_binding("operator confirmation", confirmation.binding, session, fencing_generation)
    risk = confirmation.risk_attestation
    _validate_binding("resume risk", risk.binding, session, fencing_generation)
    if not risk.passed:
        raise ValueError("fresh risk readiness check did not pass")
    if risk.kill_switch_latched:
        raise ValueError("Kill Switch is latched")
    if not risk.ledger_reconciled:
        raise ValueError("risk ledger is not reconciled")
    if confirmation.confirmed_at_ms < risk.binding.checked_at_ms:
        raise ValueError("operator confirmation predates the fresh risk check")


__all__ = [
    "EvidenceBinding", "PreflightAttestation", "RestoreAttestation",
    "RiskReadinessAttestation", "ReadyEvidenceBundle", "OperatorResumeConfirmation", "validate_ready_evidence", "validate_resume_confirmation",
]
