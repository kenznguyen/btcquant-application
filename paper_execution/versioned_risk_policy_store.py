"""Explicit SQLite publication store for immutable, Git-authored PAPER risk policies."""
from __future__ import annotations

import hashlib
import hmac
import json
import re
import sqlite3
from decimal import Decimal


SCHEMA_VERSION = 1
MIGRATION_VERSION = 1
MIGRATION_CHECKSUM = hashlib.sha256(
    b"paper-risk-policy-store-v1:immutable-history-audited-active-pointer-cas"
).hexdigest()
_DECIMAL = re.compile(r"^(?:0|[1-9][0-9]*)(?:\\.[0-9]+)?$")
_ASSET = re.compile(r"^[A-Z][A-Z0-9]{1,11}$")
_VERSION = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_SHA = re.compile(r"^[0-9a-f]{40}$")
_HASH = re.compile(r"^[0-9a-f]{64}$")


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _validate_policy(document):
    if not isinstance(document, dict) or set(document) != {
        "schemaVersion", "policyVersion", "quoteAsset", "maxSnapshotAgeMs",
        "drawdownLimit", "maxDailyLossQuote", "maxGrossExposureQuote",
    }:
        raise ValueError("RISK_POLICY_SCHEMA_INVALID")
    if type(document["schemaVersion"]) is not int or document["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("RISK_POLICY_SCHEMA_VERSION_UNSUPPORTED")
    if not isinstance(document["policyVersion"], str) or not _VERSION.fullmatch(document["policyVersion"]):
        raise ValueError("RISK_POLICY_VERSION_INVALID")
    if not isinstance(document["quoteAsset"], str) or not _ASSET.fullmatch(document["quoteAsset"]):
        raise ValueError("RISK_POLICY_QUOTE_ASSET_INVALID")
    if type(document["maxSnapshotAgeMs"]) is not int or document["maxSnapshotAgeMs"] <= 0:
        raise ValueError("RISK_POLICY_SNAPSHOT_AGE_INVALID")
    drawdown = document["drawdownLimit"]
    if not isinstance(drawdown, dict) or set(drawdown) != {"mode", "value"}:
        raise ValueError("RISK_POLICY_DRAWDOWN_INVALID")
    if drawdown["mode"] not in {"ABSOLUTE_QUOTE", "PERCENT_HWM"}:
        raise ValueError("RISK_POLICY_DRAWDOWN_MODE_UNSUPPORTED")
    for name in ("value",):
        value = drawdown[name]
        if not isinstance(value, str) or not _DECIMAL.fullmatch(value):
            raise ValueError("RISK_POLICY_DRAWDOWN_VALUE_INVALID")
    if drawdown["mode"] == "PERCENT_HWM" and Decimal(drawdown["value"]) > Decimal("100"):
        raise ValueError("RISK_POLICY_DRAWDOWN_VALUE_INVALID")
    for name in ("maxDailyLossQuote", "maxGrossExposureQuote"):
        value = document[name]
        if not isinstance(value, str) or not _DECIMAL.fullmatch(value):
            raise ValueError(f"RISK_POLICY_{name.upper()}_INVALID")
    return dict(document)


def _require_schema(connection):
    tables = {row[0] for row in connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )}
    required = {
        "paper_risk_policy_schema_migrations", "paper_risk_policy_versions",
        "paper_risk_policy_active", "paper_risk_policy_publication_audit",
    }
    if not required.issubset(tables):
        raise sqlite3.DatabaseError("RISK_POLICY_SCHEMA_NOT_INITIALIZED")
    migration = connection.execute(
        "SELECT checksum,status FROM paper_risk_policy_schema_migrations WHERE version=?",
        (MIGRATION_VERSION,),
    ).fetchone()
    if migration != (MIGRATION_CHECKSUM, "APPLIED"):
        raise sqlite3.DatabaseError("RISK_POLICY_SCHEMA_MIGRATION_INVALID")
    triggers = {row[0] for row in connection.execute(
        "SELECT name FROM sqlite_master WHERE type='trigger'"
    )}
    if not {
        "paper_risk_policy_versions_immutable_update",
        "paper_risk_policy_versions_immutable_delete",
        "paper_risk_policy_publication_audit_immutable_update",
        "paper_risk_policy_publication_audit_immutable_delete",
        "paper_risk_policy_active_audit_insert",
        "paper_risk_policy_active_audit_update",
        "paper_risk_policy_active_no_delete",
    }.issubset(triggers):
        raise sqlite3.DatabaseError("RISK_POLICY_IMMUTABILITY_GUARD_MISSING")


def initialize_risk_policy_schema(connection, *, source_sha, applied_at_ms):
    """Explicit schema migration; publication never initializes schema implicitly."""
    if not isinstance(source_sha, str) or not _SHA.fullmatch(source_sha):
        raise ValueError("RISK_POLICY_MIGRATION_SOURCE_SHA_INVALID")
    if type(applied_at_ms) is not int or applied_at_ms <= 0:
        raise ValueError("RISK_POLICY_MIGRATION_TIME_INVALID")
    if connection.in_transaction:
        raise sqlite3.DatabaseError("RISK_POLICY_MIGRATION_REQUIRES_IDLE_CONNECTION")
    connection.execute("PRAGMA foreign_keys=ON")
    connection.execute("BEGIN IMMEDIATE")
    try:
        connection.execute("""CREATE TABLE IF NOT EXISTS paper_risk_policy_schema_migrations (
            version INTEGER PRIMARY KEY, checksum TEXT NOT NULL,
            source_sha TEXT NOT NULL, applied_at_ms INTEGER NOT NULL,
            status TEXT NOT NULL CHECK(status='APPLIED')
        )""")
        existing = connection.execute(
            "SELECT checksum,status FROM paper_risk_policy_schema_migrations WHERE version=?",
            (MIGRATION_VERSION,),
        ).fetchone()
        if existing:
            if existing != (MIGRATION_CHECKSUM, "APPLIED"):
                raise sqlite3.DatabaseError("RISK_POLICY_SCHEMA_MIGRATION_INVALID")
            _require_schema(connection)
            connection.commit()
            return
        connection.execute("""CREATE TABLE paper_risk_policy_versions (
            account_id INTEGER NOT NULL CHECK(account_id=1),
            policy_version TEXT NOT NULL,
            schema_version INTEGER NOT NULL CHECK(schema_version=1),
            payload_json TEXT NOT NULL,
            payload_sha256 TEXT NOT NULL CHECK(length(payload_sha256)=64),
            source_git_commit_sha TEXT NOT NULL CHECK(length(source_git_commit_sha)=40),
            source_policy_path TEXT NOT NULL,
            source_policy_sha256 TEXT NOT NULL CHECK(length(source_policy_sha256)=64),
            published_at_ms INTEGER NOT NULL,
            operator_id TEXT NOT NULL,
            reason TEXT NOT NULL,
            previous_policy_version TEXT,
            previous_payload_sha256 TEXT,
            PRIMARY KEY(account_id,policy_version),
            UNIQUE(account_id,payload_sha256)
        )""")
        connection.execute("""CREATE TABLE paper_risk_policy_active (
            account_id INTEGER PRIMARY KEY CHECK(account_id=1),
            policy_version TEXT NOT NULL,
            payload_sha256 TEXT NOT NULL,
            activation_sequence INTEGER NOT NULL CHECK(activation_sequence>=1),
            activated_at_ms INTEGER NOT NULL,
            FOREIGN KEY(account_id,policy_version)
                REFERENCES paper_risk_policy_versions(account_id,policy_version)
        )""")
        connection.execute("""CREATE TABLE paper_risk_policy_publication_audit (
            audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL CHECK(account_id=1),
            activation_sequence INTEGER NOT NULL,
            previous_policy_version TEXT,
            previous_payload_sha256 TEXT,
            policy_version TEXT NOT NULL,
            payload_sha256 TEXT NOT NULL,
            source_git_commit_sha TEXT NOT NULL,
            source_policy_path TEXT NOT NULL,
            operator_id TEXT NOT NULL,
            reason TEXT NOT NULL,
            published_at_ms INTEGER NOT NULL,
            UNIQUE(account_id,activation_sequence)
        )""")
        for table in ("paper_risk_policy_versions", "paper_risk_policy_publication_audit"):
            connection.execute(
                f"""CREATE TRIGGER {table}_immutable_update BEFORE UPDATE ON {table}
                    BEGIN SELECT RAISE(ABORT,'RISK_POLICY_HISTORY_IMMUTABLE'); END"""
            )
            connection.execute(
                f"""CREATE TRIGGER {table}_immutable_delete BEFORE DELETE ON {table}
                    BEGIN SELECT RAISE(ABORT,'RISK_POLICY_HISTORY_IMMUTABLE'); END"""
            )
        connection.execute("""CREATE TRIGGER paper_risk_policy_active_audit_insert
            BEFORE INSERT ON paper_risk_policy_active
            WHEN NOT EXISTS (
                SELECT 1 FROM paper_risk_policy_publication_audit a
                WHERE a.account_id=NEW.account_id
                  AND a.activation_sequence=NEW.activation_sequence
                  AND a.previous_payload_sha256 IS NULL
                  AND a.policy_version=NEW.policy_version
                  AND a.payload_sha256=NEW.payload_sha256
                  AND a.published_at_ms=NEW.activated_at_ms
            )
            BEGIN SELECT RAISE(ABORT,'RISK_POLICY_ACTIVE_REQUIRES_AUDIT'); END""")
        connection.execute("""CREATE TRIGGER paper_risk_policy_active_audit_update
            BEFORE UPDATE ON paper_risk_policy_active
            WHEN NOT EXISTS (
                SELECT 1 FROM paper_risk_policy_publication_audit a
                WHERE a.account_id=NEW.account_id
                  AND a.activation_sequence=NEW.activation_sequence
                  AND a.previous_payload_sha256=OLD.payload_sha256
                  AND a.policy_version=NEW.policy_version
                  AND a.payload_sha256=NEW.payload_sha256
                  AND a.published_at_ms=NEW.activated_at_ms
            )
            BEGIN SELECT RAISE(ABORT,'RISK_POLICY_ACTIVE_REQUIRES_AUDIT'); END""")
        connection.execute("""CREATE TRIGGER paper_risk_policy_active_no_delete
            BEFORE DELETE ON paper_risk_policy_active
            BEGIN SELECT RAISE(ABORT,'RISK_POLICY_ACTIVE_DELETE_FORBIDDEN'); END""")
        connection.execute(
            """INSERT INTO paper_risk_policy_schema_migrations
               (version,checksum,source_sha,applied_at_ms,status)
               VALUES (?,?,?,?, 'APPLIED')""",
            (MIGRATION_VERSION, MIGRATION_CHECKSUM, source_sha, applied_at_ms),
        )
        _require_schema(connection)
        connection.commit()
    except Exception:
        connection.rollback()
        raise


def _validate_publication_metadata(
    *, source_git_commit_sha, source_policy_path, source_policy_sha256,
    operator_id, reason, published_at_ms,
):
    if not isinstance(source_git_commit_sha, str) or not _SHA.fullmatch(source_git_commit_sha):
        raise ValueError("RISK_POLICY_SOURCE_COMMIT_INVALID")
    if (not isinstance(source_policy_path, str)
            or not source_policy_path.startswith("config/risk_policies/")
            or not source_policy_path.endswith(".json")
            or ".." in source_policy_path.split("/")
            or "\\" in source_policy_path):
        raise ValueError("RISK_POLICY_SOURCE_PATH_INVALID")
    if not isinstance(source_policy_sha256, str) or not _HASH.fullmatch(source_policy_sha256):
        raise ValueError("RISK_POLICY_SOURCE_FILE_HASH_INVALID")
    if not isinstance(operator_id, str) or not operator_id.strip() or len(operator_id) > 128:
        raise ValueError("RISK_POLICY_OPERATOR_REQUIRED")
    if not isinstance(reason, str) or not reason.strip() or len(reason) > 512:
        raise ValueError("RISK_POLICY_PUBLICATION_REASON_REQUIRED")
    if type(published_at_ms) is not int or published_at_ms <= 0:
        raise ValueError("RISK_POLICY_PUBLICATION_TIME_INVALID")


def publish_versioned_risk_policy(
    connection,
    policy_document_json,
    *,
    expected_active_hash,
    source_git_commit_sha,
    source_policy_path,
    source_policy_sha256,
    operator_id,
    reason,
    published_at_ms,
):
    """Publish one Git-authored payload using a transactional active-hash CAS."""
    _require_schema(connection)
    _validate_publication_metadata(
        source_git_commit_sha=source_git_commit_sha,
        source_policy_path=source_policy_path,
        source_policy_sha256=source_policy_sha256,
        operator_id=operator_id, reason=reason, published_at_ms=published_at_ms,
    )
    if not isinstance(policy_document_json, str):
        raise ValueError("RISK_POLICY_DOCUMENT_JSON_REQUIRED")
    raw_hash = hashlib.sha256(policy_document_json.encode("utf-8")).hexdigest()
    if not hmac.compare_digest(raw_hash, source_policy_sha256):
        raise ValueError("RISK_POLICY_SOURCE_FILE_HASH_MISMATCH")
    try:
        document = json.loads(policy_document_json)
    except (TypeError, ValueError, json.JSONDecodeError):
        raise ValueError("RISK_POLICY_DOCUMENT_JSON_INVALID") from None
    document = _validate_policy(document)
    canonical = _canonical(document)
    payload_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    if expected_active_hash is not None and (
        not isinstance(expected_active_hash, str) or not _HASH.fullmatch(expected_active_hash)
    ):
        raise ValueError("RISK_POLICY_EXPECTED_ACTIVE_HASH_INVALID")

    if connection.in_transaction:
        raise sqlite3.DatabaseError("RISK_POLICY_PUBLICATION_REQUIRES_IDLE_CONNECTION")
    connection.execute("PRAGMA foreign_keys=ON")
    connection.execute("BEGIN IMMEDIATE")
    try:
        active = connection.execute(
            """SELECT policy_version,payload_sha256,activation_sequence
               FROM paper_risk_policy_active WHERE account_id=1"""
        ).fetchone()
        current_hash = active[1] if active else None
        if current_hash != expected_active_hash:
            raise ValueError("RISK_POLICY_ACTIVE_VERSION_CONFLICT")
        if connection.execute(
            "SELECT 1 FROM paper_risk_policy_versions WHERE account_id=1 AND policy_version=?",
            (document["policyVersion"],),
        ).fetchone():
            raise ValueError("RISK_POLICY_VERSION_ALREADY_PUBLISHED")
        previous_version = active[0] if active else None
        previous_hash = active[1] if active else None
        sequence = active[2] + 1 if active else 1
        connection.execute(
            """INSERT INTO paper_risk_policy_versions
               (account_id,policy_version,schema_version,payload_json,payload_sha256,
                source_git_commit_sha,source_policy_path,source_policy_sha256,
                published_at_ms,operator_id,reason,previous_policy_version,previous_payload_sha256)
               VALUES (1,?,1,?,?,?,?,?,?,?,?,?,?)""",
            (document["policyVersion"], canonical, payload_hash, source_git_commit_sha,
             source_policy_path, source_policy_sha256, published_at_ms, operator_id,
             reason, previous_version, previous_hash),
        )
        connection.execute(
            """INSERT INTO paper_risk_policy_publication_audit
               (account_id,activation_sequence,previous_policy_version,previous_payload_sha256,
                policy_version,payload_sha256,source_git_commit_sha,source_policy_path,
                operator_id,reason,published_at_ms)
               VALUES (1,?,?,?,?,?,?,?,?,?,?)""",
            (sequence, previous_version, previous_hash, document["policyVersion"], payload_hash,
             source_git_commit_sha, source_policy_path, operator_id, reason, published_at_ms),
        )
        if active:
            changed = connection.execute(
                """UPDATE paper_risk_policy_active
                   SET policy_version=?,payload_sha256=?,activation_sequence=?,activated_at_ms=?
                   WHERE account_id=1 AND payload_sha256=?""",
                (document["policyVersion"], payload_hash, sequence, published_at_ms, expected_active_hash),
            ).rowcount
            if changed != 1:
                raise ValueError("RISK_POLICY_ACTIVE_VERSION_CONFLICT")
        else:
            connection.execute(
                """INSERT INTO paper_risk_policy_active
                   (account_id,policy_version,payload_sha256,activation_sequence,activated_at_ms)
                   VALUES (1,?,?,?,?)""",
                (document["policyVersion"], payload_hash, sequence, published_at_ms),
            )
        connection.commit()
        return {
            "policyVersion": document["policyVersion"],
            "payloadSha256": payload_hash,
            "activationSequence": sequence,
            "activatedAtMs": published_at_ms,
        }
    except Exception:
        connection.rollback()
        raise


def load_active_versioned_risk_policy(connection):
    """Load and verify the current immutable policy without creating or mutating schema."""
    _require_schema(connection)
    row = connection.execute(
        """SELECT a.policy_version,a.payload_sha256,a.activation_sequence,a.activated_at_ms,
                  v.schema_version,v.payload_json,v.source_git_commit_sha,v.source_policy_path,
                  v.source_policy_sha256,v.operator_id,v.reason,v.published_at_ms
           FROM paper_risk_policy_active a
           JOIN paper_risk_policy_versions v
             ON v.account_id=a.account_id AND v.policy_version=a.policy_version
           WHERE a.account_id=1"""
    ).fetchone()
    if row is None:
        return None
    version, digest, sequence, activated, schema, payload, commit, path, file_hash, operator, reason, published = row
    try:
        document = _validate_policy(json.loads(payload))
        canonical = _canonical(document)
    except (TypeError, ValueError, json.JSONDecodeError):
        raise sqlite3.DatabaseError("RISK_POLICY_ACTIVE_PAYLOAD_INVALID") from None
    expected = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    if (schema != SCHEMA_VERSION or document["policyVersion"] != version
            or not hmac.compare_digest(expected, digest)
            or payload != canonical or type(sequence) is not int or sequence < 1
            or type(activated) is not int or activated <= 0
            or hashlib.sha256(payload.encode("utf-8")).hexdigest() != digest):
        raise sqlite3.DatabaseError("RISK_POLICY_ACTIVE_PAYLOAD_INVALID")
    return {
        "policyVersion": version, "schemaVersion": schema, "payload": document,
        "payloadSha256": digest, "activationSequence": sequence,
        "activatedAtMs": activated, "sourceGitCommitSha": commit,
        "sourcePolicyPath": path, "sourcePolicySha256": file_hash,
        "operatorId": operator, "reason": reason, "publishedAtMs": published,
    }


__all__ = [
    "initialize_risk_policy_schema",
    "load_active_versioned_risk_policy",
    "publish_versioned_risk_policy",
]
