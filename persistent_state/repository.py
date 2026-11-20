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
    EventRecord,
    IdempotencyClaim,
    StrategyId,
    canonical_json,
)


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


class StateRepository(Protocol):
    def initialize(self) -> None: ...

    def commit_transition(
        self, event: EventRecord, claim: IdempotencyClaim, mutation: AggregateMutation,
    ) -> CommitResult: ...

    def read_aggregate(self, account_scope_id: str, aggregate_id: str) -> AggregateSnapshot | None: ...

    def read_events(self, account_scope_id: str, *, after_sequence: int = 0) -> tuple[EventRecord, ...]: ...


_SCHEMA_STATEMENTS = (
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
)

_REQUIRED_SCHEMA_OBJECTS = {
    "ps_aggregate_state", "ps_events", "ps_idempotency_claims",
    "ps_events_no_update", "ps_events_no_delete",
    "ps_idempotency_no_update", "ps_idempotency_no_delete",
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
    ) -> CommitResult:
        """Atomically append event + idempotency claim + aggregate mutation."""
        self._validate_transition(event, claim, mutation)
        connection = self._connect_existing()
        try:
            connection.execute("BEGIN IMMEDIATE")
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
                    created_at_ms, recorded_at_ms, payload_json, market_snapshot_id,
                    candle_open_time_ms
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.event_id, event.account_scope_id, event.session_id, event.event_sequence,
                    mutation.aggregate_id, event.aggregate_version, event.event_type,
                    None if event.strategy_id is None else event.strategy_id.value,
                    event.strategy_version, event.created_at_ms, event.recorded_at_ms,
                    event.payload_json, event.market_snapshot_id, event.candle_open_time_ms,
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
                SELECT event_id, account_scope_id, session_id, event_sequence,
                       aggregate_version, event_type, strategy_id, strategy_version,
                       created_at_ms, recorded_at_ms, payload_json, market_snapshot_id,
                       candle_open_time_ms
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
                )
                for row in rows
            )
        finally:
            connection.close()


__all__ = [
    "AggregateMutation", "AggregateSnapshot", "AggregateVersionConflictError",
    "CommitResult", "EventSequenceConflictError", "IdempotencyConflictError",
    "RepositoryError", "RepositorySchemaError", "SQLiteStateRepository",
    "StateRepository", "TransitionContractError",
]
