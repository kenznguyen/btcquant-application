"""Persistent server-side risk latch shared by every paper signal source.

All state lives in the same SQLite database as the paper ledger. Call
risk_block_reason() inside the ledger write transaction so a concurrent kill
cannot race an order submission.
"""
import sqlite3

from pipeline.values import stamp


def ensure(connection):
    connection.execute("""CREATE TABLE IF NOT EXISTS paper_risk_control (
        id INTEGER PRIMARY KEY CHECK(id=1),
        paused INTEGER NOT NULL CHECK(paused IN (0,1)),
        killed INTEGER NOT NULL CHECK(killed IN (0,1)),
        reason TEXT,
        updated_at_ms INTEGER NOT NULL
    )""")
    connection.execute(
        "INSERT OR IGNORE INTO paper_risk_control VALUES (1,0,0,NULL,0)"
    )


def snapshot(connection):
    exists = connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='paper_risk_control'"
    ).fetchone()
    if not exists:
        raise sqlite3.DatabaseError("RISK_CONTROL_STATE_UNAVAILABLE")
    try:
        row = connection.execute(
            "SELECT paused,killed,reason,updated_at_ms FROM paper_risk_control WHERE id=1"
        ).fetchone()
    except sqlite3.Error:
        raise sqlite3.DatabaseError("RISK_CONTROL_STATE_UNAVAILABLE") from None
    if row is None:
        raise sqlite3.DatabaseError("RISK_CONTROL_STATE_UNAVAILABLE")
    paused, killed, reason, updated_at_ms = row
    if type(paused) is not int or paused not in (0, 1):
        raise sqlite3.DatabaseError("RISK_CONTROL_STATE_INVALID")
    if type(killed) is not int or killed not in (0, 1):
        raise sqlite3.DatabaseError("RISK_CONTROL_STATE_INVALID")
    try:
        updated_at_ms = stamp(updated_at_ms)
    except (TypeError, ValueError):
        raise sqlite3.DatabaseError("RISK_CONTROL_STATE_INVALID") from None
    if reason is not None and not isinstance(reason, str):
        raise sqlite3.DatabaseError("RISK_CONTROL_STATE_INVALID")
    return {"paused": paused == 1, "killed": killed == 1,
            "reason": reason, "updatedAtMs": updated_at_ms,
            "mode": "PAPER", "liveTradingSupported": False}


def risk_block_reason(connection):
    state = snapshot(connection)
    if state["killed"]:
        return "KILL_SWITCH"
    if state["paused"]:
        return "RISK_PAUSED"
    return None


def set_kill(connection, enabled, at_ms, reason="OPERATOR_KILL_SWITCH"):
    if type(enabled) is not bool:
        raise ValueError("enabled must be boolean")
    at = stamp(at_ms)
    if enabled:
        connection.execute(
            "UPDATE paper_risk_control SET killed=1,reason=?,updated_at_ms=? WHERE id=1",
            (str(reason)[:160], at),
        )
    else:
        # A kill latch is intentionally not cleared by a generic resume call.
        # Explicit acknowledgement is required after readiness checks.
        raise ValueError("Kill switch requires explicit acknowledged reset")


def reset_kill(connection, acknowledge, ready, at_ms):
    if acknowledge is not True or ready is not True:
        raise ValueError("Kill reset requires acknowledgement and readiness")
    at = stamp(at_ms)
    connection.execute(
        "UPDATE paper_risk_control SET killed=0,reason=NULL,updated_at_ms=? WHERE id=1",
        (at,),
    )


def set_paused(connection, paused, at_ms):
    if type(paused) is not bool:
        raise ValueError("paused must be boolean")
    at = stamp(at_ms)
    connection.execute(
        "UPDATE paper_risk_control SET paused=?,reason=?,updated_at_ms=? WHERE id=1",
        (int(paused), "OPERATOR_PAUSE" if paused else None, at),
    )
