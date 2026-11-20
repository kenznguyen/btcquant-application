"""Fail-closed path contract for the isolated PAPER SQLite database."""

import os
import sqlite3
from pathlib import Path


class PaperDatabasePathError(sqlite3.OperationalError):
    """PAPER_DB is missing, unsafe, or aliases a T0 database."""


def _canonical_path(value, *, code, reject_symlink=False):
    if not isinstance(value, str) or not value.strip():
        raise PaperDatabasePathError(code)
    raw = Path(value).expanduser()
    try:
        if reject_symlink and raw.is_symlink():
            raise PaperDatabasePathError("PAPER_DB_SYMLINK_FORBIDDEN")
        path = raw.resolve(strict=False)
        if path.exists() and not path.is_file():
            raise PaperDatabasePathError(code)
        return path
    except PaperDatabasePathError:
        raise
    except (OSError, RuntimeError, ValueError):
        raise PaperDatabasePathError(code) from None


def _overlaps(left, right):
    if left == right:
        return True
    try:
        if left.exists() and right.exists() and os.path.samefile(left, right):
            return True
    except OSError:
        raise PaperDatabasePathError("PAPER_DB_ALIAS_CHECK_FAILED") from None
    return left in right.parents or right in left.parents


def resolve_paper_db_path(environ=None, *, require_exists=False):
    """Resolve PAPER_DB and reject path, inode, symlink, and directory aliases.

    This function never creates directories, files, tables, or SQLite connections.
    """
    env = os.environ if environ is None else environ
    paper_value = env.get("PAPER_DB")
    if not isinstance(paper_value, str) or not paper_value.strip():
        raise PaperDatabasePathError("PAPER_DB_UNCONFIGURED")
    paper = _canonical_path(paper_value, code="PAPER_DB_PATH_INVALID", reject_symlink=True)

    for key in ("MARKET_DATA_DB", "T0_FEEDER_LEASE_DB"):
        value = env.get(key)
        if not value:
            continue
        t0_path = _canonical_path(value, code="T0_DATABASE_PATH_INVALID")
        if _overlaps(paper, t0_path):
            code = ("T0_LEDGER_PATH_FORBIDDEN" if key == "T0_FEEDER_LEASE_DB"
                    else "PAPER_DB_MUST_BE_DISTINCT_FROM_T0")
            raise PaperDatabasePathError(code)

    legacy = env.get("PAPER_TRADING_DB")
    if legacy:
        legacy_path = _canonical_path(legacy, code="PAPER_DB_PATH_INVALID")
        if legacy_path != paper:
            raise PaperDatabasePathError("PAPER_DB_ENV_ALIAS_MISMATCH")

    if require_exists and not paper.is_file():
        raise PaperDatabasePathError("PAPER_DB_FILE_REQUIRED")
    return paper
