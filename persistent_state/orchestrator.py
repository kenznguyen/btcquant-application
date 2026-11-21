"""Manual session orchestration over the existing persistent-state components.

The orchestrator prepares a session to READY. It never starts strategy workers.
RUNNING requires a separate authenticated operator approval and a fresh risk check.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from persistent_state.contracts import SessionRecord, SessionStatus
from persistent_state.evidence import (
    EvidenceBinding, OperatorResumeConfirmation, PreflightAttestation,
    ReadyEvidenceBundle, RestoreAttestation, RiskReadinessAttestation,
    validate_preflight_attestation,
)
from persistent_state.recovery import (
    RecoveryResult, Reducer, RecoveryValidationError, recover_repository_state,
)
from persistent_state.repository import FencingToken, StateRepository


@dataclass(frozen=True, slots=True)
class OperatorApproval:
    operator_id: str
    confirmation_id: str
    confirmed_at_ms: int

    def __post_init__(self) -> None:
        if not isinstance(self.operator_id, str) or not self.operator_id.strip():
            raise ValueError("operator_id must be non-empty")
        if not isinstance(self.confirmation_id, str) or not self.confirmation_id.strip():
            raise ValueError("confirmation_id must be non-empty")
        if type(self.confirmed_at_ms) is not int or self.confirmed_at_ms < 0:
            raise ValueError("confirmed_at_ms must be an integer >= 0")


@dataclass(frozen=True, slots=True)
class SessionStartResult:
    session: SessionRecord
    fencing_token: FencingToken
    recovery: RecoveryResult | None
    blocked_reason: str | None = None


PreflightProvider = Callable[[SessionRecord, FencingToken], PreflightAttestation]
RestoreAttestationProvider = Callable[[SessionRecord, FencingToken, RecoveryResult], RestoreAttestation]
RiskReadinessProvider = Callable[[SessionRecord, FencingToken], RiskReadinessAttestation]
Clock = Callable[[], int]


class SessionOrchestrator:
    """Coordinates preflight, deterministic recovery, READY evidence and manual Resume."""

    def __init__(
        self,
        repository: StateRepository,
        *,
        reducer: Reducer,
        preflight_provider: PreflightProvider,
        restore_attestation_provider: RestoreAttestationProvider,
        risk_readiness_provider: RiskReadinessProvider,
        clock_ms: Clock,
    ) -> None:
        self.repository = repository
        self.reducer = reducer
        self.preflight_provider = preflight_provider
        self.restore_attestation_provider = restore_attestation_provider
        self.risk_readiness_provider = risk_readiness_provider
        self.clock_ms = clock_ms

    def _advance(self, token, expected, target):
        return self.repository.advance_session(
            token, expected_status=expected, new_status=target, at_ms=self.clock_ms(),
        )

    def start(self, session: SessionRecord) -> SessionStartResult:
        """Claim a new manual session and stop at READY; never auto-resume."""
        if not isinstance(session, SessionRecord) or session.status is not SessionStatus.START_REQUESTED:
            raise ValueError("start requires a START_REQUESTED SessionRecord")
        if session.initiator != "MANUAL":
            raise ValueError("session start must be explicitly initiated by MANUAL operator action")

        token = self.repository.claim_writer(session)
        self._advance(token, SessionStatus.START_REQUESTED, SessionStatus.PREFLIGHT)
        current = self.repository.get_session(session.session_id)
        try:
            preflight = self.preflight_provider(current, token)
            validate_preflight_attestation(
                current, fencing_generation=token.fencing_generation,
                preflight=preflight,
            )
        except Exception as exc:
            blocked = self._advance(token, SessionStatus.PREFLIGHT, SessionStatus.BLOCKED_PREFLIGHT)
            return SessionStartResult(
                session=blocked, fencing_token=token, recovery=None,
                blocked_reason=f"PREFLIGHT_BLOCKED:{type(exc).__name__}",
            )

        self._advance(token, SessionStatus.PREFLIGHT, SessionStatus.RESTORING)
        current = self.repository.get_session(session.session_id)
        try:
            recovery = recover_repository_state(
                self.repository, session.account_scope_id, self.reducer,
            )
            restore = self.restore_attestation_provider(current, token, recovery)
            risk = self.risk_readiness_provider(current, token)
            bundle = ReadyEvidenceBundle(
                preflight=preflight, restore=restore, risk=risk,
            )
            ready = self.repository.advance_session(
                token, expected_status=SessionStatus.RESTORING,
                new_status=SessionStatus.READY, at_ms=self.clock_ms(),
                readiness_evidence=bundle,
            )
            return SessionStartResult(
                session=ready, fencing_token=token, recovery=recovery,
            )
        except Exception as exc:
            blocked = self._advance(token, SessionStatus.RESTORING, SessionStatus.BLOCKED_RESTORE)
            reason = "RESTORE_BLOCKED:" + (
                "RECOVERY_VALIDATION" if isinstance(exc, RecoveryValidationError)
                else type(exc).__name__
            )
            return SessionStartResult(
                session=blocked, fencing_token=token, recovery=None,
                blocked_reason=reason,
            )

    def resume(self, fencing_token: FencingToken, approval: OperatorApproval) -> SessionRecord:
        """Enter RUNNING only after explicit operator approval and a fresh risk check."""
        if not isinstance(approval, OperatorApproval):
            raise ValueError("explicit OperatorApproval is required; restart never resumes automatically")
        session = self.repository.get_session(fencing_token.session_id)
        if session.status is not SessionStatus.READY:
            raise ValueError("only a READY session can be resumed")
        risk = self.risk_readiness_provider(session, fencing_token)
        if not isinstance(risk, RiskReadinessAttestation):
            raise ValueError("fresh risk readiness attestation is required for Resume")
        confirmation = OperatorResumeConfirmation(
            binding=risk.binding,
            operator_id=approval.operator_id,
            confirmation_id=approval.confirmation_id,
            confirmed_at_ms=approval.confirmed_at_ms,
            risk_attestation=risk,
        )
        return self.repository.advance_session(
            fencing_token, expected_status=SessionStatus.READY,
            new_status=SessionStatus.RUNNING, at_ms=self.clock_ms(),
            resume_confirmation=confirmation,
        )


__all__ = [
    "OperatorApproval", "SessionOrchestrator", "SessionStartResult",
]
