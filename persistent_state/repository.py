"""Isolated SQLite repository for application-owned paper state.

No default path is provided. Constructing the repository performs no I/O.
Call initialize() explicitly with an operator-selected path; tests use temporary
directories only. This module has no T0, market-data, network or exchange client.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import sqlite3
from typing import Protocol

from persistent_state.contracts import (
    CONTRACT_SCHEMA_VERSION,
    Checkpoint,
    EventRecord,
    IdempotencyClaim,
    SessionRecord,
    SessionStatus,
    StrategyId,
    canonical_json,
)
from persistent_state.lifecycle import is_terminal_session_status, validate_session_transition


GRACEFUL_STOP_TIMEOUT_MS = 30_000


class RepositoryError(RuntimeError):
    """Base class for persistent-state repository errors."""


class RepositorySchemaError(RepositoryError):
    """Stored schema is unknown, incomplete or newer than this implementation."""


class IdempotencyConflictError(RepositoryError):
    """A previously claimed logical intent was retried with a different payload."""


class AggregateVersionConflictError(RepositoryError):
    """The aggregate version no longer matches the caller's expected version."""


class EventSequenceConflictError(RepositoryError):
    """The supplied event sequence is not the next contiguous account sequence."""


class TransitionContractError(RepositoryError):
    """Event, idempotency claim and aggregate mutation do not describe one transition."""


class CheckpointCoverageError(RepositoryError):
    """Checkpoint claims to cover events that are not committed."""


class CheckpointConflictError(RepositoryError):
    """Checkpoint identity or active generation conflicts with an existing checkpoint."""


class CheckpointIntegrityError(RepositoryError):
    """A persisted checkpoint fails checksum or metadata validation."""


class WriterOwnershipError(RepositoryError):
    """A new writer session cannot be claimed."""


class StaleFencingTokenError(RepositoryError):
    """The caller's fencing generation is no longer current."""


class SessionStateConflictError(RepositoryError):
    """The session is not in the required lifecycle state."""


class SessionTransitionError(RepositoryError):
    """The requested session lifecycle transition is not permitted."""


class CheckpointRequiredForCloseError(RepositoryError):
    """A session cannot close without a verified checkpoint at its event boundary."""


class GracefulStopTimeoutError(RepositoryError):
    """The bounded manual Stop grace period has expired."""


@dataclass(frozen=True, slots=True)
class FencingToken:
    account_scope_id: str
    session_id: str
    fencing_generation: int

    def __post_init__(self) -> None:
        if not isinstance(self.account_scope_id, str) or not self.account_scope_id.strip():
            raise ValueError("account_scope_id must be a non-empty string")
        if not isinstance(self.session_id, str) or not self.session_id.strip():
            raise ValueError("session_id must be a non-empty string")
        if (
            isinstance(self.fencing_generation, bool)
            or not isinstance(self.fencing_generation, int)
            or self.fencing_generation < 1
        ):
            raise ValueError("fencing_generation must be an integer >= 1")


@dataclass(frozen=True, slots=True)
class AggregateMutation:
    account_scope_id: str
    aggregate_id: str
    aggregate_type: str
    strategy_id: StrategyId | None
    expected_version: int
    state_json: str

    def __post_init__(self) -> None:
        for name in ("account_scope_id", "aggregate_id", "aggregate_type"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if self.strategy_id is not None:
            try:
                strategy = self.strategy_id if isinstance(self.strategy_id, StrategyId) else StrategyId(self.strategy_id)
            except (TypeError, ValueError) as exc:
                raise ValueError("strategy_id must be CORE, AI or None") from exc
            object.__setattr__(self, "strategy_id", strategy)
        if isinstance(self.expected_version, bool) or not isinstance(self.expected_version, int) or self.expected_version < 0:
            raise ValueError("expected_version must be an integer >= 0")
        # Requiring canonical JSON here keeps aggregate state deterministic at the
        # persistence boundary, rather than silently normalizing caller payloads.
        try:
            parsed = json.loads(self.state_json)
        except (json.JSONDecodeError, TypeError) as exc:
            raise ValueError("state_json must be valid canonical JSON") from exc
        if not isinstance(parsed, dict) or canonical_json(parsed) != self.state_json:
            raise ValueError("state_json must be a canonical JSON object")


@dataclass(frozen=True, slots=True)
class AggregateSnapshot:
    account_scope_id: str
    aggregate_id: str
    aggregate_type: str
    strategy_id: StrategyId | None
    aggregate_version: int
    state_json: str


@dataclass(frozen=True, slots=True)
class CommitResult:
    event_id: str
    event_sequence: int
    aggregate_version: int
    duplicate: bool


@dataclass(frozen=True, slots=True)
class CheckpointPublishResult:
    checkpoint_id: str
    is_active: bool
    duplicate: bool


class StateRepository(Protocol):
    def initialize(self) -> None: ...

    def claim_writer(self, session: SessionRecord) -> FencingToken: ...

    def commit_transition(
        self, event: EventRecord, claim: IdempotencyClaim, mutation: AggregateMutation,
        *, fencing_token: FencingToken,
    ) -> CommitResult: ...

    def advance_session(
        self, fencing_token: FencingToken, *, expected_status: SessionStatus,
        new_status: SessionStatus, at_ms: int,
    ) -> SessionRecord: ...

    def publish_checkpoint(
        self, checkpoint: Checkpoint, *, fencing_token: FencingToken,
    ) -> CheckpointPublishResult: ...

    def read_aggregate(self, account_scope_id: str, aggregate_id: str) -> AggregateSnapshot | None: ...

    def read_events(self, account_scope_id: str, *, after_sequence: int = 0) -> tuple[EventRecord, ...]: ...

    def read_active_checkpoint(self, account_scope_id: str) -> Checkpoint | None: ...


_SCHEMA_STATEMENTS = (
    """
    CREATE TABLE ps_sessions (
        session_id TEXT PRIMARY KEY,
        account_scope_id TEXT NOT NULL,
        status TEXT NOT NULL,
        started_at_ms INTEGER NOT NULL,
        ended_at_ms INTEGER,
        stop_requested_at_ms INTEGER,
        initiator TEXT NOT NULL,
        source_snapshot_id TEXT NOT NULL,
        config_hash TEXT NOT NULL,
        code_version TEXT NOT NULL,
        last_committed_event_sequence INTEGER NOT NULL CHECK (last_committed_event_sequence >= 0),
        schema_version INTEGER NOT NULL CHECK (schema_version > 0)
    )
    """,
    """
    CREATE TABLE ps_writer_fences (
        account_scope_id TEXT PRIMARY KEY,
        owner_session_id TEXT NOT NULL REFERENCES ps_sessions(session_id),
        fencing_generation INTEGER NOT NULL CHECK (fencing_generation > 0)
    )
    """,
    """
    CREATE TABLE ps_aggregate_state (
        account_scope_id TEXT NOT NULL,
        aggregate_id TEXT NOT NULL,
        aggregate_type TEXT NOT NULL,
        strategy_id TEXT,
        aggregate_version INTEGER NOT NULL CHECK (aggregate_version > 0),
        state_json TEXT NOT NULL,
        PRIMARY KEY (account_scope_id, aggregate_id)
    )
    """,
    """
    CREATE TABLE ps_events (
        event_id TEXT PRIMARY KEY,
        account_scope_id TEXT NOT NULL,
        session_id TEXT NOT NULL,
        event_sequence INTEGER NOT NULL CHECK (event_sequence > 0),
        aggregate_id TEXT NOT NULL,
        aggregate_version INTEGER NOT NULL CHECK (aggregate_version > 0),
        event_type TEXT NOT NULL,
        strategy_id TEXT,
        strategy_version TEXT,
        created_at_ms INTEGER NOT NULL,
        recorded_at_ms INTEGER NOT NULL,
        payload_json TEXT NOT NULL,
        aggregate_state_json TEXT NOT NULL,
        market_snapshot_id TEXT,
        candle_open_time_ms INTEGER,
        UNIQUE (account_scope_id, event_sequence),
        UNIQUE (account_scope_id, aggregate_id, aggregate_version)
    )
    """,
    """
    CREATE TABLE ps_idempotency_claims (
        idempotency_key TEXT PRIMARY KEY,
        payload_hash TEXT NOT NULL,
        account_scope_id TEXT NOT NULL,
        ledger_id TEXT NOT NULL,
        strategy_id TEXT NOT NULL,
        strategy_version TEXT NOT NULL,
        market_snapshot_id TEXT NOT NULL,
        candle_open_time_ms INTEGER NOT NULL,
        action_kind TEXT NOT NULL,
        action_ordinal INTEGER NOT NULL CHECK (action_ordinal >= 0),
        outcome_event_id TEXT NOT NULL REFERENCES ps_events(event_id),
        event_sequence INTEGER NOT NULL,
        aggregate_version INTEGER NOT NULL
    )
    """,
    """
    CREATE TRIGGER ps_events_no_update
    BEFORE UPDATE ON ps_events
    BEGIN
        SELECT RAISE(ABORT, 'ps_events is append-only');
    END
    """,
    """
    CREATE TRIGGER ps_events_no_delete
    BEFORE DELETE ON ps_events
    BEGIN
        SELECT RAISE(ABORT, 'ps_events is append-only');
    END
    """,
    """
    CREATE TRIGGER ps_idempotency_no_update
    BEFORE UPDATE ON ps_idempotency_claims
    BEGIN
        SELECT RAISE(ABORT, 'ps_idempotency_claims is append-only');
    END
    """,
    """
    CREATE TRIGGER ps_idempotency_no_delete
    BEFORE DELETE ON ps_idempotency_claims
    BEGIN
        SELECT RAISE(ABORT, 'ps_idempotency_claims is append-only');
    END
    """,
    """
    CREATE TABLE ps_checkpoint_generations (
        checkpoint_id TEXT PRIMARY KEY,
        account_scope_id TEXT NOT NULL,
        session_id TEXT NOT NULL,
        schema_version INTEGER NOT NULL CHECK (schema_version > 0),
        covered_event_sequence INTEGER NOT NULL CHECK (covered_event_sequence >= 0),
        aggregate_versions_json TEXT NOT NULL,
        payload_json TEXT NOT NULL,
        payload_checksum TEXT NOT NULL,
        created_at_ms INTEGER NOT NULL,
        source_snapshot_id TEXT NOT NULL,
        strategy_versions_json TEXT NOT NULL,
        config_hash TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE ps_checkpoint_heads (
        account_scope_id TEXT PRIMARY KEY,
        checkpoint_id TEXT NOT NULL REFERENCES ps_checkpoint_generations(checkpoint_id),
        covered_event_sequence INTEGER NOT NULL CHECK (covered_event_sequence >= 0)
    )
    """,
    """
    CREATE TRIGGER ps_checkpoints_no_update
    BEFORE UPDATE ON ps_checkpoint_generations
    BEGIN
        SELECT RAISE(ABORT, 'ps_checkpoint_generations is append-only');
    END
    """,
    """
    CREATE TRIGGER ps_checkpoints_no_delete
    BEFORE DELETE ON ps_checkpoint_generations
    BEGIN
        SELECT RAISE(ABORT, 'ps_checkpoint_generations is append-only');
    END
    """,
)

_REQUIRED_SCHEMA_OBJECTS = {
    "ps_sessions", "ps_writer_fences", "ps_aggregate_state", "ps_events", "ps_idempotency_claims",
    "ps_events_no_update", "ps_events_no_delete",
    "ps_idempotency_no_update", "ps_idempotency_no_delete",
    "ps_checkpoint_generations", "ps_checkpoint_heads",
    "ps_checkpoints_no_update", "ps_checkpoints_no_delete",
}


class SQLiteStateRepository:
    """Explicit-path SQLite repository; constructor is side-effect free."""

    def __init__(self, database_path: str | os.PathLike[str]) -> None:
        raw_path = os.fspath(database_path)
        if not isinstance(raw_path, str) or not raw_path.strip():
            raise ValueError("database_path must be an explicit non-empty filesystem path")
        if raw_path == ":memory:" or raw_path.startswith("file:"):
            raise ValueError("database_path must be an explicit filesystem path, not a SQLite URI")
        self.database_path = raw_path

    def initialize(self) -> None:
        """Create the v1 schema only for a new, empty, explicitly supplied database."""
        path = Path(self.database_path)
        if not path.parent.exists():
            raise FileNotFoundError(f"database parent directory does not exist: {path.parent}")
        connection = sqlite3.connect(self.database_path, timeout=5, isolation_level=None)
        try:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute("PRAGMA busy_timeout = 5000")
            version = connection.execute("PRAGMA user_version").fetchone()[0]
            existing_tables = {
                row[0] for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                )
            }
            if version == 0:
                if existing_tables:
                    raise RepositorySchemaError(
                        "unversioned database is not empty; refusing to adopt or modify it"
                    )
                connection.execute("BEGIN IMMEDIATE")
                try:
                    for statement in _SCHEMA_STATEMENTS:
                        connection.execute(statement)
                    connection.execute(f"PRAGMA user_version = {CONTRACT_SCHEMA_VERSION}")
                    connection.commit()
                except Exception:
                    connection.rollback()
                    raise
            elif version != CONTRACT_SCHEMA_VERSION:
                raise RepositorySchemaError(
                    f"unsupported database schema version {version}; expected {CONTRACT_SCHEMA_VERSION}"
                )
            else:
                self._verify_schema_objects(connection)
        finally:
            connection.close()

    @staticmethod
    def _verify_schema_objects(connection: sqlite3.Connection) -> None:
        found = {
            row[0] for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE name NOT LIKE 'sqlite_%'"
            )
        }
        missing = _REQUIRED_SCHEMA_OBJECTS - found
        if missing:
            raise RepositorySchemaError(
                "database schema is incomplete: " + ", ".join(sorted(missing))
            )

    def _connect_existing(self) -> sqlite3.Connection:
        path = Path(self.database_path)
        if not path.is_file():
            raise FileNotFoundError(f"persistent-state database does not exist: {path}")
        connection = sqlite3.connect(self.database_path, timeout=5, isolation_level=None)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 5000")
        version = connection.execute("PRAGMA user_version").fetchone()[0]
        if version != CONTRACT_SCHEMA_VERSION:
            connection.close()
            raise RepositorySchemaError(
                f"unsupported database schema version {version}; expected {CONTRACT_SCHEMA_VERSION}"
            )
        try:
            self._verify_schema_objects(connection)
        except Exception:
            connection.close()
            raise
        return connection

    def claim_writer(self, session: SessionRecord) -> FencingToken:
        """Claim the account writer slot and fence any prior unfinished session."""
        if not isinstance(session, SessionRecord):
            raise TypeError("session must be a validated SessionRecord")
        if session.status is not SessionStatus.START_REQUESTED or session.ended_at_ms is not None:
            raise WriterOwnershipError("new writer session must start in START_REQUESTED")
        connection = self._connect_existing()
        try:
            connection.execute("BEGIN IMMEDIATE")
            if connection.execute(
                "SELECT 1 FROM ps_sessions WHERE session_id = ?", (session.session_id,)
            ).fetchone() is not None:
                raise WriterOwnershipError("session_id already exists")

            current = connection.execute(
                "SELECT owner_session_id, fencing_generation FROM ps_writer_fences "
                "WHERE account_scope_id = ?",
                (session.account_scope_id,),
            ).fetchone()
            generation = 1 if current is None else current["fencing_generation"] + 1

            if current is not None:
                previous = connection.execute(
                    "SELECT status, started_at_ms FROM ps_sessions WHERE session_id = ?",
                    (current["owner_session_id"],),
                ).fetchone()
                if previous is None:
                    raise RepositorySchemaError("writer fence references a missing session")
                previous_status = SessionStatus(previous["status"])
                if not is_terminal_session_status(previous_status):
                    latest_sequence = connection.execute(
                        "SELECT COALESCE(MAX(event_sequence), 0) FROM ps_events WHERE account_scope_id = ?",
                        (session.account_scope_id,),
                    ).fetchone()[0]
                    interrupted_at = max(session.started_at_ms, previous["started_at_ms"])
                    connection.execute(
                        """
                        UPDATE ps_sessions
                        SET status = ?, ended_at_ms = ?, last_committed_event_sequence = ?
                        WHERE session_id = ?
                        """,
                        (
                            SessionStatus.INTERRUPTED.value, interrupted_at,
                            latest_sequence, current["owner_session_id"],
                        ),
                    )

            connection.execute(
                """
                INSERT INTO ps_sessions (
                    session_id, account_scope_id, status, started_at_ms, ended_at_ms,
                    stop_requested_at_ms, initiator, source_snapshot_id, config_hash, code_version,
                    last_committed_event_sequence, schema_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session.session_id, session.account_scope_id, session.status.value,
                    session.started_at_ms, session.ended_at_ms, session.stop_requested_at_ms,
                    session.initiator, session.source_snapshot_id, session.config_hash, session.code_version,
                    session.last_committed_event_sequence, session.schema_version,
                ),
            )
            connection.execute(
                """
                INSERT INTO ps_writer_fences (account_scope_id, owner_session_id, fencing_generation)
                VALUES (?, ?, ?)
                ON CONFLICT(account_scope_id) DO UPDATE SET
                    owner_session_id = excluded.owner_session_id,
                    fencing_generation = excluded.fencing_generation
                """,
                (session.account_scope_id, session.session_id, generation),
            )
            connection.commit()
            return FencingToken(session.account_scope_id, session.session_id, generation)
        except Exception:
            if connection.in_transaction:
                connection.rollback()
            raise
        finally:
            connection.close()

    @staticmethod
    def _assert_fencing_token(
        connection: sqlite3.Connection,
        token: FencingToken,
        *,
        required_statuses: set[SessionStatus],
    ) -> sqlite3.Row:
        if not isinstance(token, FencingToken):
            raise TypeError("fencing_token must be a FencingToken")
        fence = connection.execute(
            "SELECT owner_session_id, fencing_generation FROM ps_writer_fences WHERE account_scope_id = ?",
            (token.account_scope_id,),
        ).fetchone()
        if (
            fence is None
            or fence["owner_session_id"] != token.session_id
            or fence["fencing_generation"] != token.fencing_generation
        ):
            raise StaleFencingTokenError("writer fencing generation is stale")
        session = connection.execute(
            "SELECT * FROM ps_sessions WHERE session_id = ? AND account_scope_id = ?",
            (token.session_id, token.account_scope_id),
        ).fetchone()
        if session is None:
            raise StaleFencingTokenError("fencing token session does not exist")
        if SessionStatus(session["status"]) not in required_statuses:
            raise SessionStateConflictError(
                "session status does not permit this operation: " + session["status"]
            )
        return session

    def get_session(self, session_id: str) -> SessionRecord:
        if not isinstance(session_id, str) or not session_id.strip():
            raise ValueError("session_id must be a non-empty string")
        connection = self._connect_existing()
        try:
            row = connection.execute(
                "SELECT * FROM ps_sessions WHERE session_id = ?", (session_id,)
            ).fetchone()
            if row is None:
                raise KeyError(session_id)
            return SessionRecord(
                session_id=row["session_id"], account_scope_id=row["account_scope_id"],
                status=SessionStatus(row["status"]), started_at_ms=row["started_at_ms"],
                initiator=row["initiator"], source_snapshot_id=row["source_snapshot_id"],
                config_hash=row["config_hash"], code_version=row["code_version"],
                last_committed_event_sequence=row["last_committed_event_sequence"],
                ended_at_ms=row["ended_at_ms"], stop_requested_at_ms=row["stop_requested_at_ms"],
                schema_version=row["schema_version"],
            )
        finally:
            connection.close()

    def get_writer_fence(self, account_scope_id: str) -> FencingToken | None:
        if not isinstance(account_scope_id, str) or not account_scope_id.strip():
            raise ValueError("account_scope_id must be a non-empty string")
        connection = self._connect_existing()
        try:
            row = connection.execute(
                "SELECT owner_session_id, fencing_generation FROM ps_writer_fences WHERE account_scope_id = ?",
                (account_scope_id,),
            ).fetchone()
            if row is None:
                return None
            return FencingToken(account_scope_id, row["owner_session_id"], row["fencing_generation"])
        finally:
            connection.close()

    def advance_session(
        self,
        fencing_token: FencingToken,
        *,
        expected_status: SessionStatus,
        new_status: SessionStatus,
        at_ms: int,
    ) -> SessionRecord:
        try:
            validate_session_transition(expected_status, new_status)
        except ValueError as exc:
            raise SessionTransitionError(str(exc)) from exc
        if isinstance(at_ms, bool) or not isinstance(at_ms, int) or at_ms < 0:
            raise ValueError("at_ms must be an integer >= 0")
        connection = self._connect_existing()
        try:
            connection.execute("BEGIN IMMEDIATE")
            session = self._assert_fencing_token(
                connection, fencing_token, required_statuses={expected_status},
            )
            if at_ms < session["started_at_ms"]:
                raise ValueError("session transition timestamp cannot precede session start")
            effective_status = new_status
            stop_requested_at_ms = session["stop_requested_at_ms"]
            if new_status is SessionStatus.CHECKPOINTING:
                stop_requested_at_ms = at_ms
            if stop_requested_at_ms is not None and at_ms < stop_requested_at_ms:
                raise ValueError("session transition timestamp cannot precede Stop request")
            if new_status is SessionStatus.CLOSED:
                if stop_requested_at_ms is None:
                    raise SessionTransitionError("CHECKPOINTING session has no stop request timestamp")
                if at_ms - stop_requested_at_ms > GRACEFUL_STOP_TIMEOUT_MS:
                    # The 30-second manual Stop window elapsed. Preserve the
                    # session as interrupted rather than falsely declaring it closed.
                    effective_status = SessionStatus.INTERRUPTED
                else:
                    latest_sequence = connection.execute(
                        "SELECT COALESCE(MAX(event_sequence), 0) FROM ps_events WHERE account_scope_id = ?",
                        (fencing_token.account_scope_id,),
                    ).fetchone()[0]
                    head = connection.execute(
                        """
                        SELECT generation.*
                        FROM ps_checkpoint_heads AS head
                        JOIN ps_checkpoint_generations AS generation
                          ON generation.checkpoint_id = head.checkpoint_id
                        WHERE head.account_scope_id = ?
                        """,
                        (fencing_token.account_scope_id,),
                    ).fetchone()
                    verified_checkpoint = None if head is None else self._checkpoint_from_row(head)
                    if (
                        verified_checkpoint is None
                        or verified_checkpoint.session_id != fencing_token.session_id
                        or verified_checkpoint.covered_event_sequence != latest_sequence
                    ):
                        raise CheckpointRequiredForCloseError(
                            "CLOSED requires this session's verified checkpoint at the latest committed event sequence"
                        )
            latest_sequence = connection.execute(
                "SELECT COALESCE(MAX(event_sequence), 0) FROM ps_events WHERE account_scope_id = ?",
                (fencing_token.account_scope_id,),
            ).fetchone()[0]
            terminal = is_terminal_session_status(effective_status)
            ended_at_ms = at_ms if terminal else None
            connection.execute(
                """
                UPDATE ps_sessions
                SET status = ?, ended_at_ms = ?, stop_requested_at_ms = ?,
                    last_committed_event_sequence = ?
                WHERE session_id = ? AND status = ?
                """,
                (
                    effective_status.value, ended_at_ms, stop_requested_at_ms,
                    latest_sequence, fencing_token.session_id, expected_status.value,
                ),
            )
            connection.commit()
        except Exception:
            if connection.in_transaction:
                connection.rollback()
            raise
        finally:
            connection.close()
        return self.get_session(fencing_token.session_id)

    @staticmethod
    def _validate_transition(
        event: EventRecord, claim: IdempotencyClaim, mutation: AggregateMutation,
    ) -> None:
        if not isinstance(event, EventRecord):
            raise TypeError("event must be EventRecord")
        if not isinstance(claim, IdempotencyClaim):
            raise TypeError("claim must be IdempotencyClaim")
        if not isinstance(mutation, AggregateMutation):
            raise TypeError("mutation must be AggregateMutation")
        if event.account_scope_id != claim.account_scope_id or event.account_scope_id != mutation.account_scope_id:
            raise TransitionContractError("account_scope_id mismatch across transition")
        if claim.ledger_id != mutation.aggregate_id:
            raise TransitionContractError("idempotency ledger_id must match aggregate_id")
        if event.aggregate_id != mutation.aggregate_id:
            raise TransitionContractError("event aggregate_id must match aggregate mutation")
        if event.aggregate_id != mutation.aggregate_id:
            raise TransitionContractError("event aggregate_id must match aggregate mutation")
        if claim.strategy_id != mutation.strategy_id or event.strategy_id != claim.strategy_id:
            raise TransitionContractError("strategy_id mismatch across transition")
        if event.strategy_version != claim.strategy_version:
            raise TransitionContractError("strategy_version mismatch across transition")
        if event.aggregate_version != mutation.expected_version + 1:
            raise TransitionContractError("event aggregate_version must advance expected_version by one")
        if claim.outcome_event_id not in (None, event.event_id):
            raise TransitionContractError("claim outcome_event_id does not match event_id")
        if mutation.aggregate_type != "POSITION_LEDGER":
            raise TransitionContractError("idempotent paper action must mutate a POSITION_LEDGER aggregate")

    def commit_transition(
        self, event: EventRecord, claim: IdempotencyClaim, mutation: AggregateMutation,
        *, fencing_token: FencingToken,
    ) -> CommitResult:
        """Atomically append event + idempotency claim + aggregate mutation."""
        self._validate_transition(event, claim, mutation)
        if (
            event.account_scope_id != fencing_token.account_scope_id
            or event.session_id != fencing_token.session_id
        ):
            raise TransitionContractError("event must belong to the current fencing-token session")
        connection = self._connect_existing()
        try:
            connection.execute("BEGIN IMMEDIATE")
            self._assert_fencing_token(
                connection, fencing_token, required_statuses={SessionStatus.RUNNING},
            )
            existing = connection.execute(
                """
                SELECT payload_hash, outcome_event_id, event_sequence, aggregate_version
                FROM ps_idempotency_claims WHERE idempotency_key = ?
                """,
                (claim.idempotency_key,),
            ).fetchone()
            if existing is not None:
                if existing["payload_hash"] != claim.payload_hash:
                    raise IdempotencyConflictError(
                        "same idempotency key was already claimed with a different payload hash"
                    )
                connection.commit()
                return CommitResult(
                    event_id=existing["outcome_event_id"],
                    event_sequence=existing["event_sequence"],
                    aggregate_version=existing["aggregate_version"],
                    duplicate=True,
                )

            latest_sequence = connection.execute(
                "SELECT COALESCE(MAX(event_sequence), 0) FROM ps_events WHERE account_scope_id = ?",
                (event.account_scope_id,),
            ).fetchone()[0]
            expected_sequence = latest_sequence + 1
            if event.event_sequence != expected_sequence:
                raise EventSequenceConflictError(
                    f"expected event_sequence {expected_sequence}, got {event.event_sequence}"
                )

            aggregate = connection.execute(
                """
                SELECT aggregate_version FROM ps_aggregate_state
                WHERE account_scope_id = ? AND aggregate_id = ?
                """,
                (mutation.account_scope_id, mutation.aggregate_id),
            ).fetchone()
            actual_version = 0 if aggregate is None else aggregate["aggregate_version"]
            if actual_version != mutation.expected_version:
                raise AggregateVersionConflictError(
                    f"expected aggregate version {mutation.expected_version}, found {actual_version}"
                )

            connection.execute(
                """
                INSERT INTO ps_events (
                    event_id, account_scope_id, session_id, event_sequence, aggregate_id,
                    aggregate_version, event_type, strategy_id, strategy_version,
                    created_at_ms, recorded_at_ms, payload_json, aggregate_state_json,
                    market_snapshot_id, candle_open_time_ms
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.event_id, event.account_scope_id, event.session_id, event.event_sequence,
                    mutation.aggregate_id, event.aggregate_version, event.event_type,
                    None if event.strategy_id is None else event.strategy_id.value,
                    event.strategy_version, event.created_at_ms, event.recorded_at_ms,
                    event.payload_json, mutation.state_json, event.market_snapshot_id,
                    event.candle_open_time_ms,
                ),
            )
            connection.execute(
                """
                INSERT INTO ps_idempotency_claims (
                    idempotency_key, payload_hash, account_scope_id, ledger_id, strategy_id,
                    strategy_version, market_snapshot_id, candle_open_time_ms, action_kind,
                    action_ordinal, outcome_event_id, event_sequence, aggregate_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    claim.idempotency_key, claim.payload_hash, claim.account_scope_id,
                    claim.ledger_id, claim.strategy_id.value, claim.strategy_version,
                    claim.market_snapshot_id, claim.candle_open_time_ms, claim.action_kind,
                    claim.action_ordinal, event.event_id, event.event_sequence,
                    event.aggregate_version,
                ),
            )
            self._apply_aggregate_mutation(connection, mutation)
            session_update = connection.execute(
                """
                UPDATE ps_sessions
                SET last_committed_event_sequence = ?
                WHERE session_id = ? AND account_scope_id = ? AND status = ?
                """,
                (
                    event.event_sequence, fencing_token.session_id,
                    fencing_token.account_scope_id, SessionStatus.RUNNING.value,
                ),
            )
            if session_update.rowcount != 1:
                raise SessionStateConflictError("session stopped being RUNNING during the transition")
            connection.commit()
            return CommitResult(
                event_id=event.event_id, event_sequence=event.event_sequence,
                aggregate_version=event.aggregate_version, duplicate=False,
            )
        except Exception:
            if connection.in_transaction:
                connection.rollback()
            raise
        finally:
            connection.close()

    @staticmethod
    def _apply_aggregate_mutation(
        connection: sqlite3.Connection, mutation: AggregateMutation,
    ) -> None:
        next_version = mutation.expected_version + 1
        if mutation.expected_version == 0:
            connection.execute(
                """
                INSERT INTO ps_aggregate_state (
                    account_scope_id, aggregate_id, aggregate_type, strategy_id,
                    aggregate_version, state_json
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    mutation.account_scope_id, mutation.aggregate_id, mutation.aggregate_type,
                    None if mutation.strategy_id is None else mutation.strategy_id.value,
                    next_version, mutation.state_json,
                ),
            )
            return
        cursor = connection.execute(
            """
            UPDATE ps_aggregate_state
            SET aggregate_type = ?, strategy_id = ?, aggregate_version = ?, state_json = ?
            WHERE account_scope_id = ? AND aggregate_id = ? AND aggregate_version = ?
            """,
            (
                mutation.aggregate_type,
                None if mutation.strategy_id is None else mutation.strategy_id.value,
                next_version, mutation.state_json, mutation.account_scope_id,
                mutation.aggregate_id, mutation.expected_version,
            ),
        )
        if cursor.rowcount != 1:
            raise AggregateVersionConflictError("aggregate changed while committing transition")

    @staticmethod
    def _checkpoint_from_row(row: sqlite3.Row) -> Checkpoint:
        try:
            return Checkpoint(
                checkpoint_id=row["checkpoint_id"],
                account_scope_id=row["account_scope_id"],
                session_id=row["session_id"],
                schema_version=row["schema_version"],
                covered_event_sequence=row["covered_event_sequence"],
                aggregate_versions_json=row["aggregate_versions_json"],
                payload_json=row["payload_json"],
                payload_checksum=row["payload_checksum"],
                created_at_ms=row["created_at_ms"],
                source_snapshot_id=row["source_snapshot_id"],
                strategy_versions_json=row["strategy_versions_json"],
                config_hash=row["config_hash"],
            )
        except (TypeError, ValueError) as exc:
            raise CheckpointIntegrityError("persisted checkpoint failed contract validation") from exc

    def publish_checkpoint(
        self, checkpoint: Checkpoint, *, fencing_token: FencingToken,
    ) -> CheckpointPublishResult:
        """Persist an immutable verified generation and atomically advance its active pointer."""
        if not isinstance(checkpoint, Checkpoint):
            raise TypeError("checkpoint must be a validated Checkpoint")
        if (
            checkpoint.account_scope_id != fencing_token.account_scope_id
            or checkpoint.session_id != fencing_token.session_id
        ):
            raise TransitionContractError("checkpoint must belong to the current fencing-token session")
        connection = self._connect_existing()
        try:
            connection.execute("BEGIN IMMEDIATE")
            session_row = self._assert_fencing_token(
                connection, fencing_token,
                required_statuses={SessionStatus.RUNNING, SessionStatus.CHECKPOINTING},
            )
            if SessionStatus(session_row["status"]) is SessionStatus.CHECKPOINTING:
                stop_requested_at = session_row["stop_requested_at_ms"]
                if stop_requested_at is None:
                    raise SessionStateConflictError("CHECKPOINTING session has no Stop request timestamp")
                if (
                    checkpoint.created_at_ms < stop_requested_at
                    or checkpoint.created_at_ms - stop_requested_at > GRACEFUL_STOP_TIMEOUT_MS
                ):
                    raise GracefulStopTimeoutError("checkpoint was not produced within the 30-second Stop window")
            latest_sequence = connection.execute(
                "SELECT COALESCE(MAX(event_sequence), 0) FROM ps_events WHERE account_scope_id = ?",
                (checkpoint.account_scope_id,),
            ).fetchone()[0]
            if checkpoint.covered_event_sequence > latest_sequence:
                raise CheckpointCoverageError(
                    f"checkpoint covers sequence {checkpoint.covered_event_sequence}, "
                    f"but only {latest_sequence} events are committed"
                )
            expected_versions = {
                row["aggregate_id"]: row["aggregate_version"]
                for row in connection.execute(
                    """
                    SELECT aggregate_id, MAX(aggregate_version) AS aggregate_version
                    FROM ps_events
                    WHERE account_scope_id = ? AND event_sequence <= ?
                    GROUP BY aggregate_id
                    """,
                    (checkpoint.account_scope_id, checkpoint.covered_event_sequence),
                ).fetchall()
            }
            if json.loads(checkpoint.aggregate_versions_json) != expected_versions:
                raise CheckpointCoverageError(
                    "checkpoint aggregate versions do not match the committed event prefix"
                )

            existing = connection.execute(
                "SELECT * FROM ps_checkpoint_generations WHERE checkpoint_id = ?",
                (checkpoint.checkpoint_id,),
            ).fetchone()
            if existing is not None:
                stored = self._checkpoint_from_row(existing)
                if stored != checkpoint:
                    raise CheckpointConflictError("checkpoint_id already exists with different content")
                head = connection.execute(
                    "SELECT checkpoint_id FROM ps_checkpoint_heads WHERE account_scope_id = ?",
                    (checkpoint.account_scope_id,),
                ).fetchone()
                connection.commit()
                return CheckpointPublishResult(
                    checkpoint_id=checkpoint.checkpoint_id,
                    is_active=head is not None and head["checkpoint_id"] == checkpoint.checkpoint_id,
                    duplicate=True,
                )

            current_head = connection.execute(
                "SELECT checkpoint_id, covered_event_sequence FROM ps_checkpoint_heads WHERE account_scope_id = ?",
                (checkpoint.account_scope_id,),
            ).fetchone()
            if (
                current_head is not None
                and current_head["covered_event_sequence"] == checkpoint.covered_event_sequence
                and current_head["checkpoint_id"] != checkpoint.checkpoint_id
            ):
                raise CheckpointConflictError(
                    "different checkpoint generation already exists at the active coverage boundary"
                )

            connection.execute(
                """
                INSERT INTO ps_checkpoint_generations (
                    checkpoint_id, account_scope_id, session_id, schema_version,
                    covered_event_sequence, aggregate_versions_json, payload_json,
                    payload_checksum, created_at_ms, source_snapshot_id,
                    strategy_versions_json, config_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    checkpoint.checkpoint_id, checkpoint.account_scope_id, checkpoint.session_id,
                    checkpoint.schema_version, checkpoint.covered_event_sequence,
                    checkpoint.aggregate_versions_json, checkpoint.payload_json,
                    checkpoint.payload_checksum, checkpoint.created_at_ms,
                    checkpoint.source_snapshot_id, checkpoint.strategy_versions_json,
                    checkpoint.config_hash,
                ),
            )
            self._set_checkpoint_head(connection, checkpoint)
            head = connection.execute(
                "SELECT checkpoint_id FROM ps_checkpoint_heads WHERE account_scope_id = ?",
                (checkpoint.account_scope_id,),
            ).fetchone()
            connection.commit()
            return CheckpointPublishResult(
                checkpoint_id=checkpoint.checkpoint_id,
                is_active=head is not None and head["checkpoint_id"] == checkpoint.checkpoint_id,
                duplicate=False,
            )
        except Exception:
            if connection.in_transaction:
                connection.rollback()
            raise
        finally:
            connection.close()

    @staticmethod
    def _set_checkpoint_head(connection: sqlite3.Connection, checkpoint: Checkpoint) -> None:
        current = connection.execute(
            "SELECT checkpoint_id, covered_event_sequence FROM ps_checkpoint_heads WHERE account_scope_id = ?",
            (checkpoint.account_scope_id,),
        ).fetchone()
        if current is None:
            connection.execute(
                "INSERT INTO ps_checkpoint_heads (account_scope_id, checkpoint_id, covered_event_sequence) "
                "VALUES (?, ?, ?)",
                (checkpoint.account_scope_id, checkpoint.checkpoint_id, checkpoint.covered_event_sequence),
            )
        elif checkpoint.covered_event_sequence > current["covered_event_sequence"]:
            connection.execute(
                "UPDATE ps_checkpoint_heads SET checkpoint_id = ?, covered_event_sequence = ? "
                "WHERE account_scope_id = ?",
                (checkpoint.checkpoint_id, checkpoint.covered_event_sequence, checkpoint.account_scope_id),
            )
        elif checkpoint.covered_event_sequence == current["covered_event_sequence"]:
            if checkpoint.checkpoint_id != current["checkpoint_id"]:
                raise CheckpointConflictError("active checkpoint cannot be replaced at the same event sequence")

    def read_active_checkpoint(self, account_scope_id: str) -> Checkpoint | None:
        if not isinstance(account_scope_id, str) or not account_scope_id.strip():
            raise ValueError("account_scope_id must be a non-empty string")
        connection = self._connect_existing()
        try:
            row = connection.execute(
                """
                SELECT generation.*
                FROM ps_checkpoint_heads AS head
                JOIN ps_checkpoint_generations AS generation
                  ON generation.checkpoint_id = head.checkpoint_id
                WHERE head.account_scope_id = ?
                """,
                (account_scope_id,),
            ).fetchone()
            if row is None:
                return None
            checkpoint = self._checkpoint_from_row(row)
            head_sequence = connection.execute(
                "SELECT covered_event_sequence FROM ps_checkpoint_heads WHERE account_scope_id = ?",
                (account_scope_id,),
            ).fetchone()["covered_event_sequence"]
            if head_sequence != checkpoint.covered_event_sequence:
                raise CheckpointIntegrityError("active checkpoint pointer sequence does not match generation")
            expected_versions = {
                item["aggregate_id"]: item["aggregate_version"]
                for item in connection.execute(
                    """
                    SELECT aggregate_id, MAX(aggregate_version) AS aggregate_version
                    FROM ps_events
                    WHERE account_scope_id = ? AND event_sequence <= ?
                    GROUP BY aggregate_id
                    """,
                    (account_scope_id, checkpoint.covered_event_sequence),
                ).fetchall()
            }
            if json.loads(checkpoint.aggregate_versions_json) != expected_versions:
                raise CheckpointIntegrityError(
                    "active checkpoint aggregate versions do not match the committed event prefix"
                )
            return checkpoint
        finally:
            connection.close()

    def list_checkpoints(self, account_scope_id: str) -> tuple[Checkpoint, ...]:
        if not isinstance(account_scope_id, str) or not account_scope_id.strip():
            raise ValueError("account_scope_id must be a non-empty string")
        connection = self._connect_existing()
        try:
            rows = connection.execute(
                """
                SELECT * FROM ps_checkpoint_generations
                WHERE account_scope_id = ?
                ORDER BY covered_event_sequence DESC, created_at_ms DESC, checkpoint_id ASC
                """,
                (account_scope_id,),
            ).fetchall()
            return tuple(self._checkpoint_from_row(row) for row in rows)
        finally:
            connection.close()

    def read_aggregate(self, account_scope_id: str, aggregate_id: str) -> AggregateSnapshot | None:
        if not isinstance(account_scope_id, str) or not account_scope_id.strip():
            raise ValueError("account_scope_id must be a non-empty string")
        if not isinstance(aggregate_id, str) or not aggregate_id.strip():
            raise ValueError("aggregate_id must be a non-empty string")
        connection = self._connect_existing()
        try:
            row = connection.execute(
                """
                SELECT account_scope_id, aggregate_id, aggregate_type, strategy_id,
                       aggregate_version, state_json
                FROM ps_aggregate_state WHERE account_scope_id = ? AND aggregate_id = ?
                """,
                (account_scope_id, aggregate_id),
            ).fetchone()
            if row is None:
                return None
            return AggregateSnapshot(
                account_scope_id=row["account_scope_id"], aggregate_id=row["aggregate_id"],
                aggregate_type=row["aggregate_type"],
                strategy_id=None if row["strategy_id"] is None else StrategyId(row["strategy_id"]),
                aggregate_version=row["aggregate_version"], state_json=row["state_json"],
            )
        finally:
            connection.close()

    def read_events(
        self, account_scope_id: str, *, after_sequence: int = 0,
    ) -> tuple[EventRecord, ...]:
        if not isinstance(account_scope_id, str) or not account_scope_id.strip():
            raise ValueError("account_scope_id must be a non-empty string")
        if isinstance(after_sequence, bool) or not isinstance(after_sequence, int) or after_sequence < 0:
            raise ValueError("after_sequence must be an integer >= 0")
        connection = self._connect_existing()
        try:
            rows = connection.execute(
                """
                SELECT event_id, account_scope_id, session_id, event_sequence, aggregate_id,
                       aggregate_version, event_type, strategy_id, strategy_version,
                       created_at_ms, recorded_at_ms, payload_json, aggregate_state_json,
                       market_snapshot_id, candle_open_time_ms
                FROM ps_events
                WHERE account_scope_id = ? AND event_sequence > ?
                ORDER BY event_sequence ASC
                """,
                (account_scope_id, after_sequence),
            ).fetchall()
            return tuple(
                EventRecord(
                    event_id=row["event_id"], account_scope_id=row["account_scope_id"],
                    session_id=row["session_id"], event_sequence=row["event_sequence"],
                    aggregate_version=row["aggregate_version"], event_type=row["event_type"],
                    strategy_id=None if row["strategy_id"] is None else StrategyId(row["strategy_id"]),
                    strategy_version=row["strategy_version"], created_at_ms=row["created_at_ms"],
                    recorded_at_ms=row["recorded_at_ms"], payload_json=row["payload_json"],
                    market_snapshot_id=row["market_snapshot_id"],
                    candle_open_time_ms=row["candle_open_time_ms"],
                    aggregate_id=row["aggregate_id"],
                    aggregate_state_json=row["aggregate_state_json"],
                    aggregate_id=row["aggregate_id"],
                )
                for row in rows
            )
        finally:
            connection.close()


__all__ = [
    "AggregateMutation", "AggregateSnapshot", "AggregateVersionConflictError",
    "CheckpointConflictError", "CheckpointCoverageError", "CheckpointIntegrityError",
    "CheckpointPublishResult", "CheckpointRequiredForCloseError", "CommitResult",
    "GRACEFUL_STOP_TIMEOUT_MS", "GracefulStopTimeoutError",
    "EventSequenceConflictError", "FencingToken", "IdempotencyConflictError",
    "RepositoryError", "RepositorySchemaError", "SQLiteStateRepository",
    "SessionStateConflictError", "SessionTransitionError", "StaleFencingTokenError",
    "StateRepository", "TransitionContractError", "WriterOwnershipError",
]
