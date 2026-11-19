"""Validated, versioned account-level risk limits.

Strategy ledgers consume this contract; they never own or override risk limits.
"""
from contextlib import closing
from decimal import Decimal, InvalidOperation
import hashlib
import hmac
import json
from pathlib import Path
import sqlite3


SCHEMA_VERSION = 1
REQUIRED_LIMITS = (
    "maxDrawdownPct",
    "maxDailyLossUsdt",
    "maxExposureUsdt",
)


def _normalize_limits(limits):
    if not isinstance(limits, dict) or set(limits) != set(REQUIRED_LIMITS):
        raise ValueError("ACCOUNT_RISK_CONTRACT_INVALID")
    normalized = {}
    for key in REQUIRED_LIMITS:
        try:
            value = Decimal(str(limits[key]))
        except (InvalidOperation, TypeError, ValueError):
            raise ValueError("ACCOUNT_RISK_CONTRACT_INVALID") from None
        if not value.is_finite() or value <= 0:
            raise ValueError("ACCOUNT_RISK_CONTRACT_INVALID")
        if key == "maxDrawdownPct" and value > 100:
            raise ValueError("ACCOUNT_RISK_CONTRACT_INVALID")
        normalized[key] = format(value.normalize(), "f")
    return normalized


def _canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _digest(account_id, schema_version, contract_version, limits_json, source, created_at_ms):
    document = {
        "accountId": account_id,
        "schemaVersion": schema_version,
        "contractVersion": contract_version,
        "limits": json.loads(limits_json),
        "source": source,
        "createdAtMs": created_at_ms,
    }
    return hashlib.sha256(_canonical_json(document).encode("utf-8")).hexdigest()


def _ensure_schema(connection):
    connection.execute("""CREATE TABLE IF NOT EXISTS paper_account_risk_contract (
        account_id INTEGER PRIMARY KEY CHECK(account_id=1),
        schema_version INTEGER NOT NULL,
        contract_version INTEGER NOT NULL,
        limits_json TEXT NOT NULL,
        contract_hash TEXT NOT NULL,
        source TEXT NOT NULL,
        created_at_ms INTEGER NOT NULL
    )""")
    connection.execute("""CREATE TABLE IF NOT EXISTS paper_account_risk_contract_audit (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER NOT NULL CHECK(account_id=1),
        from_contract_hash TEXT,
        to_contract_hash TEXT NOT NULL,
        contract_version INTEGER NOT NULL,
        source TEXT NOT NULL,
        reason TEXT NOT NULL,
        recorded_at_ms INTEGER NOT NULL
    )""")


def load_account_risk_contract(connection):
    """Load and integrity-check the persisted account contract from an open DB connection."""
    table = connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='paper_account_risk_contract'"
    ).fetchone()
    if not table:
        return None
    try:
        row = connection.execute(
            """SELECT account_id,schema_version,contract_version,limits_json,
                      contract_hash,source,created_at_ms
               FROM paper_account_risk_contract WHERE account_id=1"""
        ).fetchone()
    except sqlite3.DatabaseError:
        raise sqlite3.DatabaseError("ACCOUNT_RISK_CONTRACT_INVALID") from None
    if row is None:
        return None
    account_id, schema_version, contract_version, limits_json, contract_hash, source, created_at_ms = row
    if (
        type(account_id) is not int or account_id != 1
        or type(schema_version) is not int or schema_version != SCHEMA_VERSION
        or type(contract_version) is not int or contract_version < 1
        or not isinstance(limits_json, str)
        or not isinstance(contract_hash, str)
        or not isinstance(source, str) or not source.strip()
        or type(created_at_ms) is not int or created_at_ms <= 0
    ):
        raise sqlite3.DatabaseError("ACCOUNT_RISK_CONTRACT_INVALID")
    try:
        decoded = json.loads(limits_json)
        normalized = _normalize_limits(decoded)
        canonical = _canonical_json(normalized)
    except (TypeError, ValueError, json.JSONDecodeError):
        raise sqlite3.DatabaseError("ACCOUNT_RISK_CONTRACT_INVALID") from None
    if canonical != limits_json:
        raise sqlite3.DatabaseError("ACCOUNT_RISK_CONTRACT_INVALID")
    expected = _digest(account_id, schema_version, contract_version, limits_json, source, created_at_ms)
    if not hmac.compare_digest(expected, contract_hash):
        raise sqlite3.DatabaseError("ACCOUNT_RISK_CONTRACT_INVALID")
    return {
        "accountId": account_id,
        "schemaVersion": schema_version,
        "contractVersion": contract_version,
        "limits": {key: Decimal(value) for key, value in normalized.items()},
        "contractHash": contract_hash,
        "source": source,
        "createdAtMs": created_at_ms,
    }


def _validate_metadata(source, recorded_at_ms):
    if not isinstance(source, str) or not source.strip() or len(source) > 128:
        raise ValueError("ACCOUNT_RISK_CONTRACT_INVALID")
    if type(recorded_at_ms) is not int or recorded_at_ms <= 0:
        raise ValueError("ACCOUNT_RISK_CONTRACT_INVALID")


def provision_account_risk_contract(db_path, limits, *, source, recorded_at_ms):
    """Create the account contract once; repeated identical provisioning is idempotent."""
    normalized = _normalize_limits(limits)
    _validate_metadata(source, recorded_at_ms)
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(path, timeout=10)) as connection, connection:
        connection.execute("BEGIN IMMEDIATE")
        _ensure_schema(connection)
        existing = load_account_risk_contract(connection)
        if existing is not None:
            current = {key: format(value.normalize(), "f") for key, value in existing["limits"].items()}
            if current != normalized:
                raise ValueError("ACCOUNT_RISK_CONTRACT_CONFLICT")
            return existing
        limits_json = _canonical_json(normalized)
        contract_hash = _digest(1, SCHEMA_VERSION, 1, limits_json, source, recorded_at_ms)
        connection.execute(
            """INSERT INTO paper_account_risk_contract
               (account_id,schema_version,contract_version,limits_json,contract_hash,source,created_at_ms)
               VALUES (1,?,?,?,?,?,?)""",
            (SCHEMA_VERSION, 1, limits_json, contract_hash, source, recorded_at_ms),
        )
        connection.execute(
            """INSERT INTO paper_account_risk_contract_audit
               (account_id,from_contract_hash,to_contract_hash,contract_version,source,reason,recorded_at_ms)
               VALUES (1,NULL,?,1,?,'INITIAL_PROVISION',?)""",
            (contract_hash, source, recorded_at_ms),
        )
        return load_account_risk_contract(connection)


def update_account_risk_contract(
    db_path, limits, *, expected_contract_hash, source, reason, recorded_at_ms
):
    """Perform an explicit compare-and-swap contract revision with an audit record."""
    normalized = _normalize_limits(limits)
    _validate_metadata(source, recorded_at_ms)
    if not isinstance(reason, str) or not reason.strip() or len(reason) > 256:
        raise ValueError("ACCOUNT_RISK_CONTRACT_INVALID")
    path = Path(db_path)
    with closing(sqlite3.connect(path, timeout=10)) as connection, connection:
        connection.execute("BEGIN IMMEDIATE")
        _ensure_schema(connection)
        existing = load_account_risk_contract(connection)
        if existing is None:
            raise sqlite3.DatabaseError("ACCOUNT_RISK_CONTRACT_UNAVAILABLE")
        if not isinstance(expected_contract_hash, str) or not hmac.compare_digest(
            existing["contractHash"], expected_contract_hash
        ):
            raise ValueError("ACCOUNT_RISK_CONTRACT_VERSION_CONFLICT")
        current = {key: format(value.normalize(), "f") for key, value in existing["limits"].items()}
        if current == normalized:
            return existing
        version = existing["contractVersion"] + 1
        limits_json = _canonical_json(normalized)
        contract_hash = _digest(1, SCHEMA_VERSION, version, limits_json, source, recorded_at_ms)
        connection.execute(
            """UPDATE paper_account_risk_contract
               SET schema_version=?,contract_version=?,limits_json=?,contract_hash=?,
                   source=?,created_at_ms=? WHERE account_id=1 AND contract_hash=?""",
            (SCHEMA_VERSION, version, limits_json, contract_hash, source, recorded_at_ms, expected_contract_hash),
        )
        if connection.execute("SELECT changes()").fetchone()[0] != 1:
            raise ValueError("ACCOUNT_RISK_CONTRACT_VERSION_CONFLICT")
        connection.execute(
            """INSERT INTO paper_account_risk_contract_audit
               (account_id,from_contract_hash,to_contract_hash,contract_version,source,reason,recorded_at_ms)
               VALUES (1,?,?,?,?,?,?)""",
            (expected_contract_hash, contract_hash, version, source, reason, recorded_at_ms),
        )
        return load_account_risk_contract(connection)
