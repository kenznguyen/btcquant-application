"""Read-only PAPER AccountRiskSnapshot provider with account/session fencing."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import time
from contextlib import closing

from persistent_state.account_risk import (
    AccountRiskProvenance,
    AccountRiskSnapshot,
    AccountRiskSnapshotProvider,
    PaperAccountBinding,
)
from persistent_state.risk_policy import VersionedRiskPolicy

from paper_execution.account_scope_binding import resolve_paper_account_binding
from paper_execution.ledger import _read_account_risk_snapshot_connection
from paper_execution.versioned_risk_policy_store import load_active_versioned_risk_policy


_PROVIDER_ID = "application.paper-account-ledger.v1"
_SOURCE_ID = "T0_CANONICAL_MARKET_DATA"
_SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
_HASH = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True, slots=True)
class PaperAccountRiskBundle:
    """One account snapshot and the exact active policy read in the same SQLite transaction."""

    snapshot: AccountRiskSnapshot
    policy: VersionedRiskPolicy
    binding: PaperAccountBinding
    policy_payload_sha256: str
    policy_source_commit_sha: str

    def admission_context(self, risk_state, *, now_ms: int):
        """Create one immutable admission context reusable by both Core and AI."""
        from persistent_state.contracts import SessionStatus
        from persistent_state.risk_admission import RiskAdmissionContext

        if type(now_ms) is not int or now_ms < self.snapshot.generated_at_ms:
            raise ValueError("RISK_ADMISSION_CONTEXT_TIME_INVALID")
        return RiskAdmissionContext(
            account_scope_id=self.binding.account_scope_id,
            session_id=self.binding.session_id,
            fencing_generation=self.binding.fencing_generation,
            session_status=SessionStatus.RUNNING,
            risk_state=risk_state,
            account_risk_snapshot=self.snapshot,
            risk_policy=self.policy,
            now_ms=now_ms,
            shared_risk_engine_available=True,
        )


class SQLitePaperAccountRiskSnapshotProvider(AccountRiskSnapshotProvider):
    """Build a typed snapshot from one read-only PAPER transaction and a current writer fence.

    The persistent-state repository is injected explicitly. No environment variable,
    default account, default session, or default fencing generation is inferred.
    """

    def __init__(self, paper_db_path, state_repository, *, clock=None):
        self.paper_db_path = Path(paper_db_path).expanduser().resolve()
        self.state_repository = state_repository
        self.clock = clock or (lambda: time.time_ns() // 1_000_000)

    def _binding(self, account_scope_id, session_id, fencing_generation):
        binding = resolve_paper_account_binding(
            self.paper_db_path, self.state_repository, account_id=1,
            session_id=session_id, fencing_generation=fencing_generation,
        )
        if binding.account_scope_id != account_scope_id:
            raise ValueError("PAPER_ACCOUNT_SCOPE_MISMATCH")
        if (binding.session_id != session_id
                or binding.fencing_generation != fencing_generation):
            raise ValueError("PAPER_ACCOUNT_SESSION_FENCING_BINDING_MISMATCH")
        return binding

    @staticmethod
    def _policy(active):
        if active is None:
            raise sqlite3.DatabaseError("RISK_POLICY_ACTIVE_UNAVAILABLE")
        payload = active.get("payload")
        if not isinstance(payload, dict):
            raise sqlite3.DatabaseError("RISK_POLICY_ACTIVE_PAYLOAD_INVALID")
        drawdown = payload.get("drawdownLimit")
        if not isinstance(drawdown, dict) or drawdown.get("mode") != "ABSOLUTE_QUOTE":
            raise sqlite3.DatabaseError("RISK_POLICY_DRAWDOWN_MODE_UNSUPPORTED")
        digest = active.get("payloadSha256")
        commit = active.get("sourceGitCommitSha")
        if not isinstance(digest, str) or not _HASH.fullmatch(digest):
            raise sqlite3.DatabaseError("RISK_POLICY_ACTIVE_HASH_INVALID")
        if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
            raise sqlite3.DatabaseError("RISK_POLICY_SOURCE_COMMIT_INVALID")
        try:
            policy = VersionedRiskPolicy(
                version=active["policyVersion"],
                quote_asset=payload["quoteAsset"],
                max_snapshot_age_ms=payload["maxSnapshotAgeMs"],
                max_drawdown_quote=drawdown["value"],
                max_daily_loss_quote=payload["maxDailyLossQuote"],
                max_gross_exposure_quote=payload["maxGrossExposureQuote"],
            )
        except (KeyError, TypeError, ValueError):
            raise sqlite3.DatabaseError("RISK_POLICY_ACTIVE_PAYLOAD_INVALID") from None
        return policy, digest, commit

    @staticmethod
    def _snapshot(raw, binding, policy, policy_hash, now_ms):
        if (not isinstance(raw, dict) or raw.get("mode") != "PAPER"
                or raw.get("liveTradingSupported") is not False
                or raw.get("available") is not True):
            raise sqlite3.DatabaseError("PAPER_ACCOUNT_SNAPSHOT_UNAVAILABLE")
        if raw.get("riskReady") is not True:
            raise sqlite3.DatabaseError("ACCOUNT_RISK_NOT_READY")
        observed = raw.get("markObservedAtMs")
        if type(observed) is not int or observed < 0 or observed > now_ms:
            raise sqlite3.DatabaseError("ACCOUNT_RISK_MARK_TIME_INVALID")
        dataset_version = raw.get("datasetVersion")
        mark = raw.get("markProvenance")
        if (not isinstance(dataset_version, str) or not _SHA256.fullmatch(dataset_version)
                or not isinstance(mark, dict)
                or mark.get("sourceId") != _SOURCE_ID
                or mark.get("sourceSnapshotId") != dataset_version
                or mark.get("sourceVersion") != dataset_version
                or not isinstance(mark.get("sourcePayloadSha256"), str)
                or not _SHA256.fullmatch(mark["sourcePayloadSha256"])):
            raise sqlite3.DatabaseError("ACCOUNT_RISK_PROVENANCE_INVALID")
        provenance = AccountRiskProvenance(
            provider_id=_PROVIDER_ID,
            source_id=_SOURCE_ID,
            source_snapshot_id=mark["sourceSnapshotId"],
            source_version=mark["sourceVersion"],
            source_payload_sha256=mark["sourcePayloadSha256"],
        )
        fields = {
            "accountScopeId": binding.account_scope_id,
            "sessionId": binding.session_id,
            "fencingGeneration": binding.fencing_generation,
            "generatedAtMs": now_ms,
            "asOfMs": observed,
            "quoteAsset": policy.quote_asset,
            "accountEquityQuote": raw.get("accountEquityQuote"),
            "grossExposureQuote": raw.get("grossExposureQuote"),
            "reservedMarginQuote": raw.get("reservedMarginQuote"),
            "drawdownQuote": raw.get("maxDrawdownUsdt"),
            "dailyLossQuote": raw.get("dailyLossUsdt"),
            "sourceSnapshotId": provenance.source_snapshot_id,
            "sourceVersion": provenance.source_version,
            "sourcePayloadSha256": provenance.source_payload_sha256,
            "riskPolicyVersion": policy.version,
            "riskPolicyPayloadSha256": policy_hash,
        }
        canonical = json.dumps(fields, sort_keys=True, separators=(",", ":"), allow_nan=False)
        snapshot_id = "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        try:
            return AccountRiskSnapshot(
                snapshot_id=snapshot_id,
                schema_version=1,
                account_scope_id=binding.account_scope_id,
                session_id=binding.session_id,
                fencing_generation=binding.fencing_generation,
                generated_at_ms=now_ms,
                as_of_ms=observed,
                quote_asset=policy.quote_asset,
                account_equity_quote=raw["accountEquityQuote"],
                gross_exposure_quote=raw["grossExposureQuote"],
                reserved_margin_quote=raw["reservedMarginQuote"],
                drawdown_quote=raw["maxDrawdownUsdt"],
                daily_loss_quote=raw["dailyLossUsdt"],
                provenance=provenance,
                verified=True,
                ledger_reconciled=True,
            )
        except (KeyError, TypeError, ValueError):
            raise sqlite3.DatabaseError("ACCOUNT_RISK_SNAPSHOT_INVALID") from None

    def read_bundle(
        self,
        *,
        account_scope_id: str,
        session_id: str,
        fencing_generation: int,
    ) -> PaperAccountRiskBundle:
        now_ms = self.clock()
        if type(now_ms) is not int or now_ms < 0:
            raise ValueError("PROVIDER_CLOCK_INVALID")
        if not self.paper_db_path.is_file():
            raise FileNotFoundError("PAPER_ACCOUNT_DATABASE_UNAVAILABLE")

        before = self._binding(account_scope_id, session_id, fencing_generation)
        uri = self.paper_db_path.as_uri() + "?mode=ro"
        with closing(sqlite3.connect(uri, uri=True, timeout=10)) as db:
            db.row_factory = sqlite3.Row
            db.execute("PRAGMA query_only=ON")
            db.execute("BEGIN")
            raw = _read_account_risk_snapshot_connection(db, now_ms=now_ms)
            active = load_active_versioned_risk_policy(db)
            policy, policy_hash, policy_commit = self._policy(active)
            if policy.quote_asset != "USDT":
                raise sqlite3.DatabaseError("RISK_POLICY_QUOTE_ASSET_UNSUPPORTED")
            snapshot = self._snapshot(raw, before, policy, policy_hash, now_ms)
            db.execute("COMMIT")

        try:
            after = self._binding(account_scope_id, session_id, fencing_generation)
        except (OSError, sqlite3.Error, TypeError, ValueError):
            raise ValueError("PAPER_SESSION_FENCE_CHANGED_DURING_SNAPSHOT") from None
        if before != after:
            raise ValueError("PAPER_SESSION_FENCE_CHANGED_DURING_SNAPSHOT")
        return PaperAccountRiskBundle(
            snapshot=snapshot, policy=policy, binding=after,
            policy_payload_sha256=policy_hash,
            policy_source_commit_sha=policy_commit,
        )

    def read_snapshot(
        self,
        *,
        account_scope_id: str,
        session_id: str,
        fencing_generation: int,
    ) -> AccountRiskSnapshot:
        return self.read_bundle(
            account_scope_id=account_scope_id,
            session_id=session_id,
            fencing_generation=fencing_generation,
        ).snapshot


__all__ = [
    "PaperAccountRiskBundle",
    "SQLitePaperAccountRiskSnapshotProvider",
]
