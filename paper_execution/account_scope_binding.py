"""Explicit binding between the PAPER ledger account and the session fence store."""
from __future__ import annotations

import hashlib
import sqlite3
from contextlib import closing
from pathlib import Path

from persistent_state.account_risk import PaperAccountBinding, validate_paper_account_binding


MIGRATION_VERSION = 1
MIGRATION_CHECKSUM = hashlib.sha256(
    b"paper-account-scope-binding-v1:explicit-immutable-scope-map"
).hexdigest()


def migrate_paper_account_scope_binding(
    connection: sqlite3.Connection,
    *,
    account_scope_id: str,
    source_sha: str,
    applied_at_ms: int,
) -> None:
    """Explicitly bind PAPER account_id=1 to one persistent-state account scope."""
    if not isinstance(account_scope_id, str) or not account_scope_id.strip() or len(account_scope_id) > 256:
        raise ValueError("PAPER_ACCOUNT_SCOPE_ID_INVALID")
    if not isinstance(source_sha, str) or len(source_sha) != 40 or any(
        char not in "0123456789abcdef" for char in source_sha.lower()
    ):
        raise ValueError("PAPER_ACCOUNT_SCOPE_MIGRATION_SOURCE_SHA_INVALID")
    if type(applied_at_ms) is not int or applied_at_ms <= 0:
        raise ValueError("PAPER_ACCOUNT_SCOPE_MIGRATION_TIME_INVALID")
    if connection.in_transaction:
        raise sqlite3.DatabaseError("PAPER_ACCOUNT_SCOPE_MIGRATION_REQUIRES_IDLE_CONNECTION")
    connection.execute("BEGIN IMMEDIATE")
    try:
        tables = {row[0] for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )}
        if "paper_accounts" not in tables:
            raise sqlite3.DatabaseError("PAPER_ACCOUNT_SCOPE_SCHEMA_NOT_READY")
        connection.execute("""CREATE TABLE IF NOT EXISTS paper_account_scope_binding_migrations (
            version INTEGER PRIMARY KEY, checksum TEXT NOT NULL,
            source_sha TEXT NOT NULL, applied_at_ms INTEGER NOT NULL,
            status TEXT NOT NULL CHECK(status='APPLIED')
        )""")
        migration = connection.execute(
            "SELECT checksum,status FROM paper_account_scope_binding_migrations WHERE version=?",
            (MIGRATION_VERSION,),
        ).fetchone()
        columns = {row[1] for row in connection.execute("PRAGMA table_info(paper_accounts)")}
        if migration:
            if migration != (MIGRATION_CHECKSUM, "APPLIED") or "account_scope_id" not in columns:
                raise sqlite3.DatabaseError("PAPER_ACCOUNT_SCOPE_MIGRATION_INVALID")
            row = connection.execute(
                "SELECT account_scope_id,mode FROM paper_accounts WHERE account_id=1"
            ).fetchone()
            if row != (account_scope_id, "PAPER"):
                raise sqlite3.DatabaseError("PAPER_ACCOUNT_SCOPE_BINDING_CONFLICT")
            connection.commit()
            return
        if "account_scope_id" in columns:
            raise sqlite3.DatabaseError("PAPER_ACCOUNT_SCOPE_COLUMN_WITHOUT_MIGRATION")
        row = connection.execute(
            "SELECT mode FROM paper_accounts WHERE account_id=1"
        ).fetchone()
        if row != ("PAPER",):
            raise sqlite3.DatabaseError("PAPER_ACCOUNT_IDENTITY_INVALID")
        connection.execute("ALTER TABLE paper_accounts ADD COLUMN account_scope_id TEXT")
        connection.execute(
            "UPDATE paper_accounts SET account_scope_id=? WHERE account_id=1 AND account_scope_id IS NULL",
            (account_scope_id,),
        )
        connection.execute("""CREATE TRIGGER paper_account_scope_id_immutable
            BEFORE UPDATE OF account_scope_id ON paper_accounts
            WHEN OLD.account_scope_id IS NOT NULL
             AND NEW.account_scope_id != OLD.account_scope_id
            BEGIN SELECT RAISE(ABORT,'PAPER_ACCOUNT_SCOPE_BINDING_IMMUTABLE'); END""")
        connection.execute(
            """INSERT INTO paper_account_scope_binding_migrations
               (version,checksum,source_sha,applied_at_ms,status)
               VALUES (?,?,?,?, 'APPLIED')""",
            (MIGRATION_CHECKSUM, applied_at_ms, source_sha.lower()),
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise


def resolve_paper_account_binding(
    paper_db_path,
    state_repository,
    *,
    account_id: int,
    session_id: str,
    fencing_generation: int,
) -> PaperAccountBinding:
    """Resolve persisted PAPER scope and validate it against the current RUNNING writer."""
    if type(account_id) is not int or account_id != 1:
        raise ValueError("PAPER_ACCOUNT_IDENTITY_INVALID")
    path = Path(paper_db_path).resolve()
    if not path.is_file():
        raise FileNotFoundError("Paper ledger is unavailable")
    with closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True, timeout=5)) as db:
        db.execute("PRAGMA query_only=ON")
        db.execute("BEGIN")
        tables = {row[0] for row in db.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )}
        if "paper_account_scope_binding_migrations" not in tables:
            raise sqlite3.DatabaseError("PAPER_ACCOUNT_SCOPE_BINDING_MISSING")
        migration = db.execute(
            "SELECT checksum,status FROM paper_account_scope_binding_migrations WHERE version=?",
            (MIGRATION_VERSION,),
        ).fetchone()
        columns = {row[1] for row in db.execute("PRAGMA table_info(paper_accounts)")}
        if migration != (MIGRATION_CHECKSUM, "APPLIED") or "account_scope_id" not in columns:
            raise sqlite3.DatabaseError("PAPER_ACCOUNT_SCOPE_BINDING_MISSING")
        row = db.execute(
            "SELECT account_id,mode,account_scope_id FROM paper_accounts WHERE account_id=?",
            (account_id,),
        ).fetchone()
        if row is None or row[0] != 1 or row[1] != "PAPER" or not row[2]:
            raise ValueError("PAPER_ACCOUNT_IDENTITY_INVALID")
        scope_id = row[2]
    try:
        session, fence = state_repository.read_active_writer_binding(
            scope_id, session_id, fencing_generation
        )
    except Exception as exc:
        if "PAPER_SESSION_FENCE_NOT_CURRENT" in str(exc):
            raise ValueError("PAPER_SESSION_FENCE_NOT_CURRENT") from None
        raise
    binding = PaperAccountBinding(
        account_id=account_id,
        account_mode="PAPER",
        account_scope_id=scope_id,
        session_id=session.session_id,
        fencing_generation=fence.fencing_generation,
    )
    return validate_paper_account_binding(
        binding,
        account_id=account_id,
        account_mode="PAPER",
        account_scope_id=scope_id,
        session_id=session_id,
        fencing_generation=fencing_generation,
    )


__all__ = [
    "MIGRATION_VERSION",
    "MIGRATION_CHECKSUM",
    "migrate_paper_account_scope_binding",
    "resolve_paper_account_binding",
]
