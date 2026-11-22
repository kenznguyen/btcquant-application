"""Versioned, synthetic-only SQLite staging schema v2.

This module never discovers or opens an existing database implicitly. Callers
must pass an explicit path; tests use :memory: or disposable temporary paths.
"""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import tempfile
from pathlib import Path
from typing import Union

from market_data.archive_provenance_validator import encode_t0enc1

SCHEMA_CONTRACT_ID = "T0_STAGING_SCHEMA_V2"
SCHEMA_VERSION = 2
SQLITE_MINIMUM_VERSION = (3, 37, 0)

TABLE_DDL = (
    """CREATE TABLE reconstruction_run (
      singleton_key INTEGER PRIMARY KEY CHECK(singleton_key=1),
      run_id TEXT NOT NULL UNIQUE CHECK(length(run_id)=69 AND substr(run_id,1,5)='run1:'),
      inventory_id TEXT NOT NULL CHECK(length(inventory_id)=69 AND substr(inventory_id,1,5)='inv1:'),
      inventory_blob_sha256 TEXT NOT NULL CHECK(length(inventory_blob_sha256)=64 AND inventory_blob_sha256 NOT GLOB '*[^0-9a-f]*'),
      inventory_raw_bytes BLOB NOT NULL,
      label TEXT NOT NULL CHECK(label='RECONSTRUCTED — PARTIAL COVERAGE'),
      parser_contract_id TEXT NOT NULL CHECK(parser_contract_id='T0_ARCHIVE_CSV_HEADER_V1'),
      parser_source_sha TEXT NOT NULL CHECK(length(parser_source_sha)=40 AND parser_source_sha NOT GLOB '*[^0-9a-f]*'),
      importer_source_sha TEXT NOT NULL CHECK(length(importer_source_sha)=40 AND importer_source_sha NOT GLOB '*[^0-9a-f]*'),
      schema_contract_id TEXT NOT NULL CHECK(schema_contract_id='T0_STAGING_SCHEMA_V2'),
      schema_fingerprint_sha256 TEXT NOT NULL CHECK(length(schema_fingerprint_sha256)=64 AND schema_fingerprint_sha256 NOT GLOB '*[^0-9a-f]*'),
      created_at_utc TEXT NOT NULL,
      coverage_manifest_json TEXT NOT NULL,
      coverage_manifest_sha256 TEXT NOT NULL CHECK(length(coverage_manifest_sha256)=64 AND coverage_manifest_sha256 NOT GLOB '*[^0-9a-f]*')
    ) STRICT""",
    """CREATE TABLE run_events (
      run_id TEXT NOT NULL REFERENCES reconstruction_run(run_id),
      event_seq INTEGER NOT NULL CHECK(event_seq>0),
      event_type TEXT NOT NULL CHECK(event_type IN ('BUILDING','CANDIDATE','QUARANTINED','VALIDATED')),
      occurred_at_utc TEXT NOT NULL,
      reason_code TEXT,
      candidate_snapshot_sha256 TEXT CHECK(candidate_snapshot_sha256 IS NULL OR (candidate_snapshot_sha256 IS NOT NULL AND length(candidate_snapshot_sha256)=64 AND candidate_snapshot_sha256 NOT GLOB '*[^0-9a-f]*')),
      validator_payload_sha256 TEXT CHECK(validator_payload_sha256 IS NULL OR (validator_payload_sha256 IS NOT NULL AND length(validator_payload_sha256)=64 AND validator_payload_sha256 NOT GLOB '*[^0-9a-f]*')),
      PRIMARY KEY(run_id,event_seq),
      CHECK(event_type NOT IN ('CANDIDATE','VALIDATED') OR candidate_snapshot_sha256 IS NOT NULL),
      CHECK(event_type<>'VALIDATED' OR validator_payload_sha256 IS NOT NULL)
    ) STRICT""",
    """CREATE TABLE archive_objects (
      object_id TEXT PRIMARY KEY CHECK(length(object_id)=69 AND substr(object_id,1,5)='obj1:'),
      inventory_id TEXT NOT NULL,
      inventory_blob_sha256 TEXT NOT NULL CHECK(length(inventory_blob_sha256)=64),
      inventory_entry_identity TEXT NOT NULL,
      object_key TEXT NOT NULL UNIQUE,
      object_kind TEXT NOT NULL CHECK(object_kind IN ('ZIP','CHECKSUM_SIDECAR')),
      timeframe TEXT NOT NULL CHECK(timeframe IN ('15m','1h')),
      partition TEXT NOT NULL,
      period TEXT NOT NULL,
      paired_object_key TEXT NOT NULL,
      requested_key TEXT,
      expected_size_bytes INTEGER CHECK(expected_size_bytes IS NULL OR expected_size_bytes>=0),
      expected_sha256 TEXT CHECK(expected_sha256 IS NULL OR (length(expected_sha256)=64 AND expected_sha256 NOT GLOB '*[^0-9a-f]*')),
      measured_size_bytes INTEGER CHECK(measured_size_bytes IS NULL OR measured_size_bytes>=0),
      measured_sha256 TEXT CHECK(measured_sha256 IS NULL OR (length(measured_sha256)=64 AND measured_sha256 NOT GLOB '*[^0-9a-f]*')),
      response_bytes_total INTEGER NOT NULL CHECK(response_bytes_total>=0),
      response_status INTEGER CHECK(response_status IS NULL OR response_status BETWEEN 100 AND 599),
      local_relative_path TEXT,
      exclusive_create INTEGER CHECK(exclusive_create IS NULL OR exclusive_create IN (0,1)),
      retrieval_source TEXT,
      workflow_run_id TEXT,
      workflow_job_id TEXT,
      workflow_event TEXT,
      trigger_sha TEXT CHECK(trigger_sha IS NULL OR (length(trigger_sha)=40 AND trigger_sha NOT GLOB '*[^0-9a-f]*')),
      checkout_sha TEXT CHECK(checkout_sha IS NULL OR (length(checkout_sha)=40 AND checkout_sha NOT GLOB '*[^0-9a-f]*')),
      retrieved_at_utc TEXT,
      verification_status TEXT NOT NULL CHECK(verification_status IN ('VERIFIED','QUARANTINED')),
      failure_code TEXT,
      CHECK(requested_key IS NULL OR requested_key=object_key),
      CHECK(
        (verification_status='VERIFIED'
         AND requested_key IS NOT NULL AND requested_key=object_key
         AND expected_size_bytes IS NOT NULL AND expected_sha256 IS NOT NULL
         AND measured_size_bytes IS NOT NULL AND measured_sha256 IS NOT NULL
         AND response_status IS NOT NULL AND local_relative_path IS NOT NULL
         AND exclusive_create IS NOT NULL AND exclusive_create=1
         AND workflow_run_id IS NOT NULL AND workflow_job_id IS NOT NULL
         AND workflow_event IS NOT NULL AND trigger_sha IS NOT NULL
         AND checkout_sha IS NOT NULL AND retrieved_at_utc IS NOT NULL
         AND failure_code IS NULL)
        OR (verification_status='QUARANTINED' AND failure_code IS NOT NULL)
      )
    ) STRICT""",
    """CREATE TABLE acquisition_attempts (
      attempt_id TEXT PRIMARY KEY CHECK(length(attempt_id)=69 AND substr(attempt_id,1,5)='att1:'),
      object_id TEXT NOT NULL REFERENCES archive_objects(object_id),
      attempt_number INTEGER NOT NULL CHECK(attempt_number>0),
      workflow_run_id TEXT NOT NULL,
      workflow_job_id TEXT NOT NULL,
      workflow_event TEXT NOT NULL CHECK(workflow_event='workflow_dispatch'),
      trigger_sha TEXT NOT NULL CHECK(length(trigger_sha)=40 AND trigger_sha NOT GLOB '*[^0-9a-f]*'),
      checkout_sha TEXT NOT NULL CHECK(length(checkout_sha)=40 AND checkout_sha NOT GLOB '*[^0-9a-f]*'),
      requested_key TEXT NOT NULL,
      expected_size_bytes INTEGER NOT NULL CHECK(expected_size_bytes>=0),
      expected_sha256 TEXT NOT NULL CHECK(length(expected_sha256)=64 AND expected_sha256 NOT GLOB '*[^0-9a-f]*'),
      started_at_utc TEXT NOT NULL,
      finished_at_utc TEXT,
      outcome TEXT NOT NULL CHECK(outcome IN ('STARTED','FAILED','TRANSFERRED','UNKNOWN')),
      failure_subtype TEXT CHECK(failure_subtype IS NULL OR failure_subtype IN ('HTTP_FAILED','TRANSFER_FAILED','VALIDATION_FAILED')),
      response_status INTEGER,
      response_bytes_received INTEGER CHECK(response_bytes_received IS NULL OR response_bytes_received>=0),
      is_complete_object INTEGER NOT NULL CHECK(is_complete_object IN (0,1)),
      partial_body_sha256 TEXT CHECK(partial_body_sha256 IS NULL OR (length(partial_body_sha256)=64 AND partial_body_sha256 NOT GLOB '*[^0-9a-f]*')),
      complete_object_sha256 TEXT CHECK(complete_object_sha256 IS NULL OR (length(complete_object_sha256)=64 AND complete_object_sha256 NOT GLOB '*[^0-9a-f]*')),
      failure_code TEXT,
      UNIQUE(object_id,attempt_number),
      UNIQUE(object_id,attempt_id),
      CHECK((outcome='STARTED' AND finished_at_utc IS NULL AND is_complete_object=0 AND failure_subtype IS NULL AND failure_code IS NULL)
         OR (outcome='FAILED' AND finished_at_utc IS NOT NULL AND is_complete_object=0 AND failure_subtype IS NOT NULL AND failure_code IS NOT NULL)
         OR (outcome='TRANSFERRED' AND finished_at_utc IS NOT NULL AND is_complete_object=1 AND failure_subtype IS NULL AND response_bytes_received IS NOT NULL AND complete_object_sha256 IS NOT NULL AND failure_code IS NULL)
         OR (outcome='UNKNOWN' AND finished_at_utc IS NOT NULL AND is_complete_object=0 AND failure_subtype IS NULL))
    ) STRICT""",
    """CREATE TABLE object_successful_attempt (
      object_id TEXT PRIMARY KEY REFERENCES archive_objects(object_id),
      attempt_id TEXT NOT NULL UNIQUE,
      FOREIGN KEY(object_id,attempt_id) REFERENCES acquisition_attempts(object_id,attempt_id)
    ) STRICT""",
    """CREATE TABLE archive_pairs (
      pair_id TEXT PRIMARY KEY CHECK(length(pair_id)=70 AND substr(pair_id,1,6)='pair1:'),
      zip_object_id TEXT NOT NULL UNIQUE REFERENCES archive_objects(object_id),
      sidecar_object_id TEXT NOT NULL UNIQUE REFERENCES archive_objects(object_id),
      zip_size_bytes INTEGER CHECK(zip_size_bytes IS NULL OR zip_size_bytes>=0),
      zip_sha256 TEXT CHECK(zip_sha256 IS NULL OR (length(zip_sha256)=64 AND zip_sha256 NOT GLOB '*[^0-9a-f]*')),
      sidecar_size_bytes INTEGER CHECK(sidecar_size_bytes IS NULL OR sidecar_size_bytes>=0),
      sidecar_sha256 TEXT CHECK(sidecar_sha256 IS NULL OR (length(sidecar_sha256)=64 AND sidecar_sha256 NOT GLOB '*[^0-9a-f]*')),
      sidecar_asserted_zip_sha256 TEXT CHECK(sidecar_asserted_zip_sha256 IS NULL OR (length(sidecar_asserted_zip_sha256)=64 AND sidecar_asserted_zip_sha256 NOT GLOB '*[^0-9a-f]*')),
      assertion_matches INTEGER CHECK(assertion_matches IS NULL OR assertion_matches IN (0,1)),
      zip_crc_ok INTEGER CHECK(zip_crc_ok IS NULL OR zip_crc_ok IN (0,1)),
      candidate_member_count INTEGER CHECK(candidate_member_count IS NULL OR candidate_member_count>=0),
      structural_ok INTEGER CHECK(structural_ok IS NULL OR structural_ok IN (0,1)),
      disposition TEXT NOT NULL CHECK(disposition IN ('VERIFIED','QUARANTINED')),
      failure_code TEXT,
      CHECK((disposition='VERIFIED'
             AND zip_size_bytes IS NOT NULL AND zip_sha256 IS NOT NULL
             AND sidecar_size_bytes IS NOT NULL AND sidecar_sha256 IS NOT NULL
             AND sidecar_asserted_zip_sha256 IS NOT NULL
             AND assertion_matches IS NOT NULL AND assertion_matches=1
             AND zip_crc_ok IS NOT NULL AND zip_crc_ok=1
             AND candidate_member_count IS NOT NULL AND candidate_member_count=1
             AND structural_ok IS NOT NULL AND structural_ok=1
             AND failure_code IS NULL)
         OR (disposition='QUARANTINED' AND failure_code IS NOT NULL)),
      CHECK(zip_object_id<>sidecar_object_id)
    ) STRICT""",
    """CREATE TABLE csv_members (
      candidate_id TEXT PRIMARY KEY CHECK(length(candidate_id)=70 AND substr(candidate_id,1,6)='cand1:'),
      member_id TEXT UNIQUE CHECK(member_id IS NULL OR (length(member_id)=69 AND substr(member_id,1,5)='mem1:')),
      pair_id TEXT NOT NULL REFERENCES archive_pairs(pair_id),
      central_directory_ordinal INTEGER NOT NULL CHECK(central_directory_ordinal>0),
      member_path TEXT,
      member_size_bytes INTEGER CHECK(member_size_bytes IS NULL OR member_size_bytes>=0),
      member_sha256 TEXT CHECK(member_sha256 IS NULL OR (length(member_sha256)=64 AND member_sha256 NOT GLOB '*[^0-9a-f]*')),
      encoding TEXT,
      bom_present INTEGER CHECK(bom_present IS NULL OR bom_present IN (0,1)),
      newline TEXT,
      delimiter TEXT,
      header_present INTEGER CHECK(header_present IS NULL OR header_present IN (0,1)),
      header_contract_id TEXT,
      parser_contract_id TEXT,
      parser_source_sha TEXT CHECK(parser_source_sha IS NULL OR (length(parser_source_sha)=40 AND parser_source_sha NOT GLOB '*[^0-9a-f]*')),
      data_row_count INTEGER CHECK(data_row_count IS NULL OR data_row_count>=0),
      first_open_time_ms INTEGER CHECK(first_open_time_ms IS NULL OR first_open_time_ms>=0),
      last_open_time_ms INTEGER CHECK(last_open_time_ms IS NULL OR last_open_time_ms>=0),
      disposition TEXT NOT NULL CHECK(disposition IN ('VERIFIED','QUARANTINED')),
      failure_code TEXT,
      UNIQUE(pair_id,central_directory_ordinal),
      CHECK((member_id IS NOT NULL AND member_path IS NOT NULL AND member_size_bytes IS NOT NULL AND member_sha256 IS NOT NULL) OR member_id IS NULL),
      CHECK((disposition='VERIFIED'
             AND member_id IS NOT NULL AND member_path IS NOT NULL
             AND member_size_bytes IS NOT NULL AND member_sha256 IS NOT NULL
             AND encoding IS NOT NULL AND encoding='UTF-8'
             AND bom_present IS NOT NULL AND bom_present=0
             AND newline IS NOT NULL AND newline='LF'
             AND delimiter IS NOT NULL AND delimiter=','
             AND header_present IS NOT NULL AND header_present=1
             AND header_contract_id IS NOT NULL AND header_contract_id='T0_ARCHIVE_CSV_HEADER_V1'
             AND parser_contract_id IS NOT NULL AND parser_contract_id='T0_ARCHIVE_CSV_HEADER_V1'
             AND parser_source_sha IS NOT NULL AND data_row_count IS NOT NULL AND data_row_count>0
             AND first_open_time_ms IS NOT NULL AND last_open_time_ms IS NOT NULL
             AND failure_code IS NULL)
         OR (disposition='QUARANTINED' AND failure_code IS NOT NULL)),
      CHECK((header_present=1 AND header_contract_id='T0_ARCHIVE_CSV_HEADER_V1')
         OR (header_present=0 AND header_contract_id IS NULL)
         OR (header_present IS NULL AND header_contract_id IS NULL)),
      CHECK(data_row_count IS NULL OR
         (data_row_count=0 AND first_open_time_ms IS NULL AND last_open_time_ms IS NULL)
         OR (data_row_count>0 AND first_open_time_ms IS NOT NULL AND last_open_time_ms IS NOT NULL))
    ) STRICT""",
    """CREATE TABLE source_rows (
      source_row_id TEXT PRIMARY KEY CHECK(length(source_row_id)=69 AND substr(source_row_id,1,5)='row1:'),
      member_id TEXT NOT NULL REFERENCES csv_members(member_id),
      physical_record_ordinal INTEGER NOT NULL CHECK(physical_record_ordinal>0),
      data_row_ordinal INTEGER NOT NULL CHECK(data_row_ordinal>0),
      raw_fields_json TEXT NOT NULL,
      raw_row_digest TEXT NOT NULL CHECK(length(raw_row_digest)=64 AND raw_row_digest NOT GLOB '*[^0-9a-f]*'),
      parser_contract_id TEXT NOT NULL CHECK(parser_contract_id='T0_ARCHIVE_CSV_HEADER_V1'),
      parser_source_sha TEXT NOT NULL CHECK(length(parser_source_sha)=40),
      importer_contract_id TEXT NOT NULL CHECK(importer_contract_id='T0_ARCHIVE_IMPORTER_V1'),
      importer_source_sha TEXT NOT NULL CHECK(length(importer_source_sha)=40),
      exchange TEXT,
      market_type TEXT,
      symbol TEXT,
      timeframe TEXT,
      open_time_ms INTEGER CHECK(open_time_ms IS NULL OR open_time_ms>=0),
      candle_value_id TEXT CHECK(candle_value_id IS NULL OR (length(candle_value_id)=68 AND substr(candle_value_id,1,4)='cv1:')),
      disposition TEXT NOT NULL CHECK(disposition IN ('ACCEPTED','REJECTED')),
      rejection_code TEXT,
      UNIQUE(member_id,physical_record_ordinal),
      UNIQUE(member_id,data_row_ordinal),
      CHECK((disposition='ACCEPTED'
             AND exchange IS NOT NULL AND exchange='binance'
             AND market_type IS NOT NULL AND market_type='usdm'
             AND symbol IS NOT NULL AND symbol='BTCUSDT'
             AND timeframe IS NOT NULL AND timeframe IN ('15m','1h')
             AND open_time_ms IS NOT NULL AND candle_value_id IS NOT NULL
             AND rejection_code IS NULL)
         OR (disposition='REJECTED' AND candle_value_id IS NULL AND rejection_code IS NOT NULL))
    ) STRICT""",
    """CREATE TABLE candles (
      exchange TEXT NOT NULL CHECK(exchange='binance'),
      market_type TEXT NOT NULL CHECK(market_type='usdm'),
      symbol TEXT NOT NULL CHECK(symbol='BTCUSDT'),
      timeframe TEXT NOT NULL CHECK(timeframe IN ('15m','1h')),
      open_time_ms INTEGER NOT NULL CHECK(open_time_ms>=0),
      open TEXT NOT NULL,
      high TEXT NOT NULL,
      low TEXT NOT NULL,
      close TEXT NOT NULL,
      volume TEXT NOT NULL,
      available_at_ms INTEGER NOT NULL CHECK(available_at_ms>open_time_ms),
      availability_kind TEXT NOT NULL CHECK(availability_kind='BAR_CLOSE_BOUNDARY'),
      candle_value_id TEXT NOT NULL CHECK(length(candle_value_id)=68 AND substr(candle_value_id,1,4)='cv1:'),
      PRIMARY KEY(exchange,market_type,symbol,timeframe,open_time_ms)
    ) STRICT""",
    """CREATE TABLE candle_provenance_links (
      link_id TEXT PRIMARY KEY CHECK(length(link_id)=69 AND substr(link_id,1,5)='lnk1:'),
      exchange TEXT NOT NULL,
      market_type TEXT NOT NULL,
      symbol TEXT NOT NULL,
      timeframe TEXT NOT NULL,
      open_time_ms INTEGER NOT NULL,
      source_row_id TEXT NOT NULL UNIQUE REFERENCES source_rows(source_row_id),
      candle_value_id TEXT NOT NULL CHECK(length(candle_value_id)=68 AND substr(candle_value_id,1,4)='cv1:'),
      duplicate_disposition TEXT NOT NULL CHECK(duplicate_disposition IN ('UNIQUE','IDENTICAL_DUPLICATE')),
      FOREIGN KEY(exchange,market_type,symbol,timeframe,open_time_ms)
        REFERENCES candles(exchange,market_type,symbol,timeframe,open_time_ms)
    ) STRICT""",
    """CREATE TABLE failure_observations (
      subject_kind TEXT NOT NULL CHECK(subject_kind IN ('RUN','OBJECT','ATTEMPT','PAIR','MEMBER','SOURCE_ROW','CANDLE','LINK')),
      subject_id TEXT NOT NULL,
      failure_ordinal INTEGER NOT NULL CHECK(failure_ordinal>0),
      failure_code TEXT NOT NULL,
      failure_detail_code TEXT,
      observed_at_utc TEXT NOT NULL,
      evidence_sha256 TEXT CHECK(evidence_sha256 IS NULL OR (length(evidence_sha256)=64 AND evidence_sha256 NOT GLOB '*[^0-9a-f]*')),
      PRIMARY KEY(subject_kind,subject_id,failure_ordinal)
    ) STRICT""",
)

TRIGGER_DDL = (
    "CREATE TRIGGER trg_run_events_no_update BEFORE UPDATE ON run_events "
    "BEGIN SELECT RAISE(ABORT,'run_events are append-only'); END",
    "CREATE TRIGGER trg_run_events_no_delete BEFORE DELETE ON run_events "
    "BEGIN SELECT RAISE(ABORT,'run_events are append-only'); END",
)

INDEX_DDL = (
    "CREATE INDEX idx_archive_objects_pair_key ON archive_objects(paired_object_key,object_kind)",
    "CREATE INDEX idx_acquisition_attempts_object_number ON acquisition_attempts(object_id,attempt_number)",
    "CREATE INDEX idx_archive_pairs_zip_sidecar ON archive_pairs(zip_object_id,sidecar_object_id)",
    "CREATE INDEX idx_csv_members_pair_disposition ON csv_members(pair_id,disposition)",
    "CREATE INDEX idx_source_rows_member_ordinal ON source_rows(member_id,physical_record_ordinal)",
    "CREATE INDEX idx_source_rows_candle_identity ON source_rows(exchange,market_type,symbol,timeframe,open_time_ms)",
    "CREATE INDEX idx_candle_links_candle_identity ON candle_provenance_links(exchange,market_type,symbol,timeframe,open_time_ms)",
    "CREATE INDEX idx_failure_observations_subject_code ON failure_observations(subject_kind,subject_id,failure_code)",
)

_SCHEMA_NAMES = (
    "reconstruction_run", "run_events", "archive_objects", "acquisition_attempts",
    "object_successful_attempt", "archive_pairs", "csv_members", "source_rows",
    "candles", "candle_provenance_links", "failure_observations",
)
_TRIGGER_NAMES = ("trg_run_events_no_update", "trg_run_events_no_delete")
_INDEX_NAMES = (
    "idx_archive_objects_pair_key", "idx_acquisition_attempts_object_number",
    "idx_archive_pairs_zip_sidecar", "idx_csv_members_pair_disposition",
    "idx_source_rows_member_ordinal", "idx_source_rows_candle_identity",
    "idx_candle_links_candle_identity", "idx_failure_observations_subject_code",
)


def _require_sqlite_version() -> None:
    if sqlite3.sqlite_version_info < SQLITE_MINIMUM_VERSION:
        raise RuntimeError(
            f"SQLite >= 3.37.0 required for STRICT tables; found {sqlite3.sqlite_version}"
        )


def _canonical_manifest_bytes() -> bytes:
    manifest = {
        "schema_contract_id": SCHEMA_CONTRACT_ID,
        "user_version": SCHEMA_VERSION,
        "sqlite_minimum_version": "3.37.0",
        "tables": list(TABLE_DDL),
        "indexes": list(INDEX_DDL),
        "triggers": list(TRIGGER_DDL),
        "pragmas": ["PRAGMA user_version=2;"],
    }
    # Manifest values are strings/integers/arrays only; this is the JCS-compatible
    # deterministic JSON subset used by the frozen schema contract.
    return json.dumps(
        manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def compute_schema_fingerprint() -> str:
    framed = encode_t0enc1(
        "T0-SQLITE-SCHEMA-FINGERPRINT-V1",
        SCHEMA_CONTRACT_ID,
        SCHEMA_VERSION,
        _canonical_manifest_bytes(),
    )
    return hashlib.sha256(framed).hexdigest()


def _append_only_authorizer(action, arg1, arg2, database_name, trigger_name):
    if action in (sqlite3.SQLITE_UPDATE, sqlite3.SQLITE_DELETE) and arg1 == "run_events":
        return sqlite3.SQLITE_DENY
    return sqlite3.SQLITE_OK


def initialize_staging_schema(connection: sqlite3.Connection) -> None:
    """Atomically initialize only a truly empty SQLite database; never migrate files."""
    _require_sqlite_version()
    if connection.in_transaction:
        raise RuntimeError("refusing schema initialization inside a caller transaction")
    if connection.execute("PRAGMA user_version").fetchone()[0] != 0:
        raise RuntimeError("refusing to initialize a database with nonzero user_version")
    existing = connection.execute(
        "SELECT name FROM sqlite_schema WHERE type IN ('table','index','view','trigger') "
        "AND name NOT LIKE 'sqlite_%'"
    ).fetchall()
    if existing:
        raise RuntimeError("refusing to initialize a non-empty database")
    connection.execute("PRAGMA foreign_keys=ON")
    connection.execute("BEGIN IMMEDIATE")
    try:
        for statement in TABLE_DDL:
            connection.execute(statement)
        for statement in INDEX_DDL:
            connection.execute(statement)
        for statement in TRIGGER_DDL:
            connection.execute(statement)
        connection.execute("PRAGMA user_version=2")
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    connection.set_authorizer(_append_only_authorizer)


def _validate_disposable_test_path(database: Union[str, Path]) -> Path:
    path = Path(database)
    if path.is_symlink() or path.exists():
        raise ValueError("disposable staging path must be a new, non-symlink file")
    temporary_root = Path(tempfile.gettempdir()).resolve()
    parent = path.parent.resolve()
    if parent != path.parent or parent.parent != temporary_root:
        raise ValueError("disposable staging path must be directly inside the system temporary directory")
    if not parent.name.startswith("t0-staging-v2-"):
        raise ValueError("temporary directory must use the t0-staging-v2- prefix")
    if not path.name.startswith("synthetic-staging-"):
        raise ValueError("temporary database filename must use the synthetic-staging- prefix")
    return path


def connect_staging_database(
    database: Union[str, Path] = ":memory:", *,
    allow_disposable_path: bool = False,
) -> sqlite3.Connection:
    """Open in-memory by default; file DBs require explicit disposable-test path policy."""
    _require_sqlite_version()
    created_path = None
    if str(database) == ":memory:":
        connection = sqlite3.connect(":memory:")
    else:
        if not allow_disposable_path:
            raise ValueError("file-backed staging requires allow_disposable_path=True")
        path = _validate_disposable_test_path(database)
        flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(path, flags, 0o600)
        os.close(descriptor)
        created_path = path
        try:
            connection = sqlite3.connect(str(path))
        except Exception:
            path.unlink(missing_ok=True)
            raise
    try:
        connection.execute("PRAGMA foreign_keys=ON")
        initialize_staging_schema(connection)
        if connection.execute("PRAGMA foreign_keys").fetchone()[0] != 1:
            raise RuntimeError("SQLite foreign key enforcement could not be enabled")
        return connection
    except Exception:
        connection.close()
        if created_path is not None:
            created_path.unlink(missing_ok=True)
        raise


def verify_staging_database(connection: sqlite3.Connection) -> bool:
    """Read-only structural/integrity check; graph acceptance remains a later gate."""
    _require_sqlite_version()
    if connection.execute("PRAGMA user_version").fetchone()[0] != SCHEMA_VERSION:
        return False
    if connection.execute("PRAGMA foreign_keys").fetchone()[0] != 1:
        return False
    objects = connection.execute(
        "SELECT type,name,sql FROM sqlite_schema WHERE name NOT LIKE 'sqlite_%' ORDER BY type,name"
    ).fetchall()
    actual = {(kind, name): sql for kind, name, sql in objects}
    expected_tables = dict(zip(_SCHEMA_NAMES, TABLE_DDL))
    expected_indexes = {statement.split("CREATE INDEX ", 1)[1].split(" ", 1)[0]: statement
                        for statement in INDEX_DDL}
    expected_triggers = {statement.split("CREATE TRIGGER ", 1)[1].split(" ", 1)[0]: statement
                         for statement in TRIGGER_DDL}
    if {name for kind, name, _ in objects if kind == "table"} != set(_SCHEMA_NAMES):
        return False
    if {name for kind, name, _ in objects if kind == "index"} != set(_INDEX_NAMES):
        return False
    if {name for kind, name, _ in objects if kind == "trigger"} != set(_TRIGGER_NAMES):
        return False
    if any(kind not in ("table", "index", "trigger") for kind, _, _ in objects):
        return False
    for name, ddl in expected_tables.items():
        row = actual.get(("table", name))
        if row is None or row.strip() != ddl.strip() or "STRICT" not in row.upper():
            return False
    for name, ddl in expected_indexes.items():
        if actual.get(("index", name), "").strip() != ddl.strip():
            return False
    for name, ddl in expected_triggers.items():
        if actual.get(("trigger", name), "").strip() != ddl.strip():
            return False
    if connection.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
        return False
    if connection.execute("PRAGMA foreign_key_check").fetchall():
        return False
    run_rows = connection.execute(
        "SELECT schema_contract_id,schema_fingerprint_sha256 FROM reconstruction_run"
    ).fetchall()
    expected_fingerprint = compute_schema_fingerprint()
    if any(contract_id != SCHEMA_CONTRACT_ID or fingerprint != expected_fingerprint
           for contract_id, fingerprint in run_rows):
        return False
    return len(expected_fingerprint) == 64


__all__ = (
    "SCHEMA_CONTRACT_ID", "SCHEMA_VERSION", "SQLITE_MINIMUM_VERSION",
    "TABLE_DDL", "INDEX_DDL", "TRIGGER_DDL", "compute_schema_fingerprint",
    "initialize_staging_schema", "connect_staging_database",
    "verify_staging_database",
)
