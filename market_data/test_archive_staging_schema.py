"""Synthetic-only SQLite staging schema v2 tests; disposable DBs only."""
import hashlib
import sqlite3
import tempfile
import unittest
from pathlib import Path

from market_data.archive_staging_schema import (
    SCHEMA_CONTRACT_ID,
    SCHEMA_VERSION,
    compute_schema_fingerprint,
    connect_staging_database,
    verify_staging_database,
)


class StagingSchemaV2Tests(unittest.TestCase):
    def setUp(self):
        self.db = connect_staging_database(":memory:")

    def tearDown(self):
        self.db.close()

    def test_initializes_versioned_strict_schema_and_enables_foreign_keys(self):
        self.assertEqual(self.db.execute("PRAGMA user_version").fetchone()[0], SCHEMA_VERSION)
        self.assertEqual(SCHEMA_CONTRACT_ID, "T0_STAGING_SCHEMA_V2")
        self.assertEqual(self.db.execute("PRAGMA foreign_keys").fetchone()[0], 1)
        rows = self.db.execute(
            "SELECT name, sql FROM sqlite_schema WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
        self.assertGreaterEqual(len(rows), 11)
        self.assertTrue(all("STRICT" in sql.upper() for _, sql in rows))
        triggers = self.db.execute(
            "SELECT name FROM sqlite_schema WHERE type='trigger' ORDER BY name"
        ).fetchall()
        self.assertEqual(
            triggers,
            [("trg_run_events_no_delete",), ("trg_run_events_no_update",)],
        )

    def test_rejects_null_mandatory_values_in_verified_object_check_branch(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("""
                INSERT INTO archive_objects(
                    object_id, inventory_id, inventory_blob_sha256, inventory_entry_identity,
                    object_key, object_kind, timeframe, partition, period, paired_object_key,
                    response_bytes_total, verification_status, requested_key, expected_size_bytes,
                    expected_sha256, measured_size_bytes, measured_sha256, response_status,
                    local_relative_path, exclusive_create, workflow_run_id, workflow_job_id,
                    workflow_event, trigger_sha, checkout_sha, retrieved_at_utc
                ) VALUES (
                    'obj1:' || printf('%064d', 1), 'inv1:' || printf('%064d', 1),
                    printf('%064d', 0), 'synthetic-entry', 'synthetic.zip', 'ZIP', '15m',
                    'monthly', '2022-08', 'synthetic.CHECKSUM', 0, 'VERIFIED',
                    'synthetic.zip', NULL, printf('%064d', 0), 1, printf('%064d', 0),
                    200, 'synthetic/object.zip', 1, 'run', 'job', 'workflow_dispatch',
                    printf('%040d', 0), printf('%040d', 0), '2026-01-01T00:00:00Z'
                )
            """)

    def test_run_events_are_append_only_through_managed_connection(self):
        self.db.execute("""
            INSERT INTO reconstruction_run(
                run_id, inventory_id, inventory_blob_sha256, inventory_raw_bytes, label,
                parser_contract_id, parser_source_sha, importer_source_sha, schema_contract_id,
                schema_fingerprint_sha256, created_at_utc, coverage_manifest_json,
                coverage_manifest_sha256
            ) VALUES (
                'run1:' || printf('%064d', 1), 'inv1:' || printf('%064d', 1),
                printf('%064d', 0), X'01', 'RECONSTRUCTED — PARTIAL COVERAGE',
                'T0_ARCHIVE_CSV_HEADER_V1', printf('%040d', 0), printf('%040d', 0),
                'T0_STAGING_SCHEMA_V2', printf('%064d', 0), '2026-01-01T00:00:00Z',
                '{}', printf('%064d', 0)
            )
        """)
        run_id = self.db.execute("SELECT run_id FROM reconstruction_run").fetchone()[0]
        self.db.execute(
            "INSERT INTO run_events(run_id,event_seq,event_type,occurred_at_utc) VALUES(?,1,'BUILDING','2026-01-01T00:00:00Z')",
            (run_id,),
        )
        # Remove the connection-local authorizer to prove the database triggers
        # independently enforce append-only semantics for every SQLite connection.
        self.db.set_authorizer(None)
        for sql in (
            "UPDATE run_events SET reason_code='mutated' WHERE event_seq=1",
            "DELETE FROM run_events WHERE event_seq=1",
        ):
            with self.subTest(sql=sql), self.assertRaises(sqlite3.DatabaseError):
                self.db.execute(sql)

    def test_schema_fingerprint_is_deterministic_and_matches_database(self):
        first = compute_schema_fingerprint()
        second = compute_schema_fingerprint()
        self.assertRegex(first, r"^[0-9a-f]{64}$")
        self.assertEqual(first, second)
        self.assertTrue(verify_staging_database(self.db))

    def _insert_quarantined_object(self, suffix):
        object_id = "obj1:" + hashlib.sha256(suffix.encode("utf-8")).hexdigest()
        self.db.execute("""
            INSERT INTO archive_objects(
                object_id, inventory_id, inventory_blob_sha256, inventory_entry_identity,
                object_key, object_kind, timeframe, partition, period, paired_object_key,
                response_bytes_total, verification_status, failure_code
            ) VALUES (?, ?, ?, ?, ?, 'ZIP', '15m', 'monthly', '2022-08', ?, 0,
                      'QUARANTINED', 'SYNTHETIC_QUARANTINE')
        """, (object_id, "inv1:" + "1" * 64, "0" * 64, "entry-" + suffix,
              "synthetic-" + suffix + ".zip", "paired-" + suffix))
        return object_id

    def _insert_failed_attempt(self, object_id, suffix):
        self.db.execute("""
            INSERT INTO acquisition_attempts(
                attempt_id, object_id, attempt_number, workflow_run_id, workflow_job_id,
                workflow_event, trigger_sha, checkout_sha, requested_key,
                expected_size_bytes, expected_sha256, started_at_utc, finished_at_utc,
                outcome, failure_subtype, response_status, response_bytes_received,
                is_complete_object, failure_code
            ) VALUES (?, ?, 1, 'run', 'job', 'workflow_dispatch', ?, ?, 'synthetic.zip',
                      1, ?, '2026-01-01T00:00:00Z', '2026-01-01T00:00:01Z',
                      'FAILED', 'HTTP_FAILED', 503, 0, 0, 'HTTP_STATUS_NOT_SUCCESS')
        """, ("att1:" + suffix * 64, object_id, "2" * 40, "3" * 40, "4" * 64))
        return "att1:" + suffix * 64

    def test_rejects_cross_object_successful_attempt_foreign_key(self):
        first = self._insert_quarantined_object("a")
        second = self._insert_quarantined_object("b")
        first_attempt = self._insert_failed_attempt(first, "c")
        second_attempt = self._insert_failed_attempt(second, "d")
        self.db.execute(
            "INSERT INTO object_successful_attempt(object_id,attempt_id) VALUES(?,?)",
            (first, first_attempt),
        )
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(
                "INSERT INTO object_successful_attempt(object_id,attempt_id) VALUES(?,?)",
                (first, second_attempt),
            )

    def test_rejects_null_required_verified_pair_evidence(self):
        zip_id = self._insert_quarantined_object("e")
        sidecar_id = self._insert_quarantined_object("f")
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("""
                INSERT INTO archive_pairs(
                    pair_id, zip_object_id, sidecar_object_id, zip_size_bytes, zip_sha256,
                    sidecar_size_bytes, sidecar_sha256, sidecar_asserted_zip_sha256,
                    assertion_matches, zip_crc_ok, candidate_member_count, structural_ok,
                    disposition
                ) VALUES (?, ?, ?, 1, ?, 1, ?, ?, NULL, 1, 1, 1, 'VERIFIED')
            """, ("pair1:" + "a" * 64, zip_id, sidecar_id, "1" * 64,
                  "2" * 64, "1" * 64))

    def test_rejects_null_required_verified_member_evidence(self):
        zip_id = self._insert_quarantined_object("1")
        sidecar_id = self._insert_quarantined_object("2")
        pair_id = "pair1:" + "b" * 64
        self.db.execute("""
            INSERT INTO archive_pairs(pair_id,zip_object_id,sidecar_object_id,disposition,failure_code)
            VALUES(?,?,?,'QUARANTINED','SYNTHETIC_QUARANTINE')
        """, (pair_id, zip_id, sidecar_id))
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("""
                INSERT INTO csv_members(
                    candidate_id,member_id,pair_id,central_directory_ordinal,member_path,
                    member_size_bytes,member_sha256,encoding,bom_present,newline,delimiter,
                    header_present,header_contract_id,parser_contract_id,parser_source_sha,
                    data_row_count,first_open_time_ms,last_open_time_ms,disposition
                ) VALUES(?, ?, ?, 1, 'synthetic.csv', 1, ?, 'UTF-8', NULL, 'LF', ',',
                         1, 'T0_ARCHIVE_CSV_HEADER_V1', 'T0_ARCHIVE_CSV_HEADER_V1',
                         ?, 1, 0, 0, 'VERIFIED')
            """, ("cand1:" + "c" * 64, "mem1:" + "d" * 64, pair_id,
                  "5" * 64, "6" * 40))

    def test_rejects_null_required_accepted_source_row_identity(self):
        zip_id = self._insert_quarantined_object("3")
        sidecar_id = self._insert_quarantined_object("4")
        pair_id = "pair1:" + "e" * 64
        self.db.execute("""
            INSERT INTO archive_pairs(pair_id,zip_object_id,sidecar_object_id,disposition,failure_code)
            VALUES(?,?,?,'QUARANTINED','SYNTHETIC_QUARANTINE')
        """, (pair_id, zip_id, sidecar_id))
        member_id = "mem1:" + "f" * 64
        self.db.execute("""
            INSERT INTO csv_members(
                candidate_id,member_id,pair_id,central_directory_ordinal,member_path,
                member_size_bytes,member_sha256,disposition,failure_code
            ) VALUES(?, ?, ?, 1, 'synthetic.csv', 1, ?, 'QUARANTINED','SYNTHETIC_QUARANTINE')
        """, ("cand1:" + "a" * 64, member_id, pair_id, "7" * 64))
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("""
                INSERT INTO source_rows(
                    source_row_id,member_id,physical_record_ordinal,data_row_ordinal,
                    raw_fields_json,raw_row_digest,parser_contract_id,parser_source_sha,
                    importer_contract_id,importer_source_sha,exchange,market_type,symbol,
                    timeframe,open_time_ms,candle_value_id,disposition
                ) VALUES(?, ?, 2, 1, '[]', ?, 'T0_ARCHIVE_CSV_HEADER_V1', ?,
                         'T0_ARCHIVE_IMPORTER_V1', ?, NULL, 'usdm', 'BTCUSDT',
                         '15m', 0, ?, 'ACCEPTED')
            """, ("row1:" + "b" * 64, member_id, "8" * 64, "9" * 40,
                  "a" * 40, "cv1:" + "c" * 64))

    def test_integrity_and_foreign_key_checks_pass_on_empty_synthetic_database(self):
        self.assertEqual(self.db.execute("PRAGMA integrity_check").fetchone()[0], "ok")
        self.assertEqual(self.db.execute("PRAGMA foreign_key_check").fetchall(), [])
        self.assertTrue(verify_staging_database(self.db))

    def test_creates_and_verifies_a_disposable_temporary_database(self):
        self.assertGreaterEqual(sqlite3.sqlite_version_info, (3, 37, 0))
        with tempfile.TemporaryDirectory(prefix="t0-staging-v2-") as directory:
            path = Path(directory) / "synthetic-staging-test.sqlite3"
            temporary_db = connect_staging_database(path, allow_disposable_path=True)
            try:
                self.assertTrue(path.is_file())
                self.assertEqual(temporary_db.execute("PRAGMA user_version").fetchone()[0], 2)
                self.assertEqual(temporary_db.execute("PRAGMA integrity_check").fetchone()[0], "ok")
                self.assertTrue(verify_staging_database(temporary_db))
            finally:
                temporary_db.close()


    def test_verified_object_rejects_non_hex_digests_and_invalid_http_status(self):
        columns = (
            "object_id,inventory_id,inventory_blob_sha256,inventory_entry_identity,"
            "object_key,object_kind,timeframe,partition,period,paired_object_key,"
            "requested_key,expected_size_bytes,expected_sha256,measured_size_bytes,"
            "measured_sha256,response_bytes_total,response_status,local_relative_path,"
            "exclusive_create,workflow_run_id,workflow_job_id,workflow_event,trigger_sha,"
            "checkout_sha,retrieved_at_utc,verification_status"
        )
        base = [
            "obj1:" + "a" * 64, "inv1:" + "b" * 64, "0" * 64, "synthetic-entry",
            "synthetic.zip", "ZIP", "15m", "monthly", "2022-08", "synthetic.CHECKSUM",
            "synthetic.zip", 1, "1" * 64, 1, "2" * 64, 1, 200,
            "synthetic/object.zip", 1, "123", "456", "workflow_dispatch",
            "3" * 40, "4" * 40, "2026-01-01T00:00:00Z", "VERIFIED",
        ]
        invalid_cases = (
            (12, "g" * 64),  # expected SHA-256
            (22, "g" * 40),  # trigger SHA-1
            (16, 99),        # invalid HTTP status lower bound
            (16, 600),       # invalid HTTP status upper bound
        )
        for index, invalid in invalid_cases:
            values = list(base)
            values[index] = invalid
            placeholders = ",".join("?" for _ in values)
            with self.subTest(column=columns.split(",")[index], value=invalid), self.assertRaises(sqlite3.IntegrityError):
                self.db.execute(
                    f"INSERT INTO archive_objects({columns}) VALUES({placeholders})",
                    values,
                )

    def test_failed_attempt_rejects_non_hex_expected_sha256(self):
        object_id = self._insert_quarantined_object("9")
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("""
                INSERT INTO acquisition_attempts(
                    attempt_id,object_id,attempt_number,workflow_run_id,workflow_job_id,
                    workflow_event,trigger_sha,checkout_sha,requested_key,expected_size_bytes,
                    expected_sha256,started_at_utc,finished_at_utc,outcome,failure_subtype,
                    response_status,response_bytes_received,is_complete_object,failure_code
                ) VALUES(?, ?, 1, 'run', 'job', 'workflow_dispatch', ?, ?, 'synthetic.zip',
                         1, ?, '2026-01-01T00:00:00Z', '2026-01-01T00:00:01Z',
                         'FAILED', 'HTTP_FAILED', 503, 0, 0, 'HTTP_STATUS_NOT_SUCCESS')
            """, ("att1:" + "9" * 64, object_id, "2" * 40, "3" * 40, "g" * 64))

    def test_run_event_snapshot_digest_requires_lowercase_hex(self):
        self.db.execute("""
            INSERT INTO reconstruction_run(
                run_id, inventory_id, inventory_blob_sha256, inventory_raw_bytes, label,
                parser_contract_id, parser_source_sha, importer_source_sha, schema_contract_id,
                schema_fingerprint_sha256, created_at_utc, coverage_manifest_json,
                coverage_manifest_sha256
            ) VALUES (
                'run1:' || printf('%064d', 1), 'inv1:' || printf('%064d', 1),
                printf('%064d', 0), X'01', 'RECONSTRUCTED — PARTIAL COVERAGE',
                'T0_ARCHIVE_CSV_HEADER_V1', printf('%040d', 0), printf('%040d', 0),
                'T0_STAGING_SCHEMA_V2', printf('%064d', 0), '2026-01-01T00:00:00Z',
                '{}', printf('%064d', 0)
            )
        """)
        run_id = self.db.execute("SELECT run_id FROM reconstruction_run").fetchone()[0]
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("""
                INSERT INTO run_events(
                    run_id,event_seq,event_type,occurred_at_utc,candidate_snapshot_sha256
                ) VALUES(?,1,'CANDIDATE','2026-01-01T00:00:00Z',?)
            """, (run_id, "g" * 64))


    def test_every_mandatory_verified_and_accepted_field_rejects_null(self):
        def insert_values(table, values):
            columns = tuple(values)
            placeholders = ",".join("?" for _ in columns)
            self.db.execute(
                f"INSERT INTO {table}({','.join(columns)}) VALUES({placeholders})",
                tuple(values[column] for column in columns),
            )

        object_fields = (
            "requested_key", "expected_size_bytes", "expected_sha256",
            "measured_size_bytes", "measured_sha256", "response_status",
            "local_relative_path", "exclusive_create", "workflow_run_id",
            "workflow_job_id", "workflow_event", "trigger_sha", "checkout_sha",
            "retrieved_at_utc",
        )
        for i, field in enumerate(object_fields, start=1):
            key = f"null-object-{i}.zip"
            values = {
                "object_id": "obj1:" + f"{i:064x}",
                "inventory_id": "inv1:" + "1" * 64,
                "inventory_blob_sha256": "0" * 64,
                "inventory_entry_identity": f"synthetic-entry-{i}",
                "object_key": key, "object_kind": "ZIP", "timeframe": "15m",
                "partition": "monthly", "period": "2022-08",
                "paired_object_key": f"null-object-{i}.CHECKSUM",
                "requested_key": key, "expected_size_bytes": 1,
                "expected_sha256": "1" * 64, "measured_size_bytes": 1,
                "measured_sha256": "2" * 64, "response_bytes_total": 1,
                "response_status": 200, "local_relative_path": f"synthetic/{i}.zip",
                "exclusive_create": 1, "workflow_run_id": "123",
                "workflow_job_id": "456", "workflow_event": "workflow_dispatch",
                "trigger_sha": "3" * 40, "checkout_sha": "4" * 40,
                "retrieved_at_utc": "2026-01-01T00:00:00Z",
                "verification_status": "VERIFIED",
            }
            values[field] = None
            with self.subTest(table="archive_objects", field=field), self.assertRaises(sqlite3.IntegrityError):
                insert_values("archive_objects", values)

        pair_fields = (
            "zip_size_bytes", "zip_sha256", "sidecar_size_bytes",
            "sidecar_sha256", "sidecar_asserted_zip_sha256", "assertion_matches",
            "zip_crc_ok", "candidate_member_count", "structural_ok",
        )
        for i, field in enumerate(pair_fields, start=1):
            left = chr(33 + i * 2)
            right = chr(34 + i * 2)
            zip_id = self._insert_quarantined_object(left)
            sidecar_id = self._insert_quarantined_object(right)
            values = {
                "pair_id": "pair1:" + f"{i:064x}", "zip_object_id": zip_id,
                "sidecar_object_id": sidecar_id, "zip_size_bytes": 1,
                "zip_sha256": "1" * 64, "sidecar_size_bytes": 1,
                "sidecar_sha256": "2" * 64, "sidecar_asserted_zip_sha256": "1" * 64,
                "assertion_matches": 1, "zip_crc_ok": 1,
                "candidate_member_count": 1, "structural_ok": 1,
                "disposition": "VERIFIED",
            }
            values[field] = None
            with self.subTest(table="archive_pairs", field=field), self.assertRaises(sqlite3.IntegrityError):
                insert_values("archive_pairs", values)

        member_fields = (
            "member_id", "member_path", "member_size_bytes", "member_sha256",
            "encoding", "bom_present", "newline", "delimiter", "header_present",
            "header_contract_id", "parser_contract_id", "parser_source_sha",
            "data_row_count", "first_open_time_ms", "last_open_time_ms",
        )
        for i, field in enumerate(member_fields, start=1):
            left = chr(65 + i * 2)
            right = chr(66 + i * 2)
            zip_id = self._insert_quarantined_object(left)
            sidecar_id = self._insert_quarantined_object(right)
            pair_id = "pair1:" + f"{100 + i:064x}"
            insert_values("archive_pairs", {
                "pair_id": pair_id, "zip_object_id": zip_id,
                "sidecar_object_id": sidecar_id, "disposition": "QUARANTINED",
                "failure_code": "SYNTHETIC_QUARANTINE",
            })
            values = {
                "candidate_id": "cand1:" + f"{i:064x}",
                "member_id": "mem1:" + f"{i:064x}", "pair_id": pair_id,
                "central_directory_ordinal": 1, "member_path": f"synthetic/{i}.csv",
                "member_size_bytes": 1, "member_sha256": "5" * 64,
                "encoding": "UTF-8", "bom_present": 0, "newline": "LF",
                "delimiter": ",", "header_present": 1,
                "header_contract_id": "T0_ARCHIVE_CSV_HEADER_V1",
                "parser_contract_id": "T0_ARCHIVE_CSV_HEADER_V1",
                "parser_source_sha": "6" * 40, "data_row_count": 1,
                "first_open_time_ms": 0, "last_open_time_ms": 0,
                "disposition": "VERIFIED",
            }
            values[field] = None
            with self.subTest(table="csv_members", field=field), self.assertRaises(sqlite3.IntegrityError):
                insert_values("csv_members", values)

        source_fields = (
            "member_id", "physical_record_ordinal", "data_row_ordinal",
            "raw_fields_json", "raw_row_digest", "parser_contract_id",
            "parser_source_sha", "importer_contract_id", "importer_source_sha",
            "exchange", "market_type", "symbol", "timeframe", "open_time_ms",
            "candle_value_id",
        )
        for i, field in enumerate(source_fields, start=1):
            left = chr(97 + i)
            right = chr(112 + i)
            zip_id = self._insert_quarantined_object(left)
            sidecar_id = self._insert_quarantined_object(right)
            pair_id = "pair1:" + f"{200 + i:064x}"
            insert_values("archive_pairs", {
                "pair_id": pair_id, "zip_object_id": zip_id,
                "sidecar_object_id": sidecar_id, "disposition": "QUARANTINED",
                "failure_code": "SYNTHETIC_QUARANTINE",
            })
            member_id = "mem1:" + f"{200 + i:064x}"
            insert_values("csv_members", {
                "candidate_id": "cand1:" + f"{200 + i:064x}",
                "member_id": member_id, "pair_id": pair_id,
                "central_directory_ordinal": 1, "member_path": "synthetic.csv",
                "member_size_bytes": 1, "member_sha256": "7" * 64,
                "disposition": "QUARANTINED", "failure_code": "SYNTHETIC_QUARANTINE",
            })
            values = {
                "source_row_id": "row1:" + f"{i:064x}", "member_id": member_id,
                "physical_record_ordinal": 2, "data_row_ordinal": 1,
                "raw_fields_json": '[""]', "raw_row_digest": "8" * 64,
                "parser_contract_id": "T0_ARCHIVE_CSV_HEADER_V1",
                "parser_source_sha": "9" * 40,
                "importer_contract_id": "T0_ARCHIVE_IMPORTER_V1",
                "importer_source_sha": "a" * 40, "exchange": "binance",
                "market_type": "usdm", "symbol": "BTCUSDT", "timeframe": "15m",
                "open_time_ms": 0, "candle_value_id": "cv1:" + "b" * 64,
                "disposition": "ACCEPTED",
            }
            values[field] = None
            with self.subTest(table="source_rows", field=field), self.assertRaises(sqlite3.IntegrityError):
                insert_values("source_rows", values)



    def test_source_row_sha_and_identity_columns_require_lowercase_hex(self):
        self.db.execute("PRAGMA foreign_keys=OFF")
        base = {
            "source_row_id": "row1:" + "1" * 64,
            "member_id": "mem1:" + "2" * 64,
            "physical_record_ordinal": 2,
            "data_row_ordinal": 1,
            "raw_fields_json": "[]",
            "raw_row_digest": "3" * 64,
            "parser_contract_id": "T0_ARCHIVE_CSV_HEADER_V1",
            "parser_source_sha": "4" * 40,
            "importer_contract_id": "T0_ARCHIVE_IMPORTER_V1",
            "importer_source_sha": "5" * 40,
            "disposition": "REJECTED",
            "rejection_code": "SYNTHETIC_REJECTED",
        }
        columns = tuple(base)
        sql = (
            f"INSERT INTO source_rows ({','.join(columns)}) "
            f"VALUES ({','.join('?' for _ in columns)})"
        )
        for field in ("source_row_id", "parser_source_sha", "importer_source_sha"):
            values = dict(base)
            values[field] = ("row1:" if field == "source_row_id" else "") + "g" * (64 if field == "source_row_id" else 40)
            with self.subTest(field=field), self.assertRaises(sqlite3.IntegrityError):
                self.db.execute(sql, tuple(values[name] for name in columns))

    def test_candle_and_link_value_ids_require_lowercase_hex_suffix(self):
        candle_values = (
            "binance", "usdm", "BTCUSDT", "15m", 0, "1", "2", "1", "2", "1",
            900000, "BAR_CLOSE_BOUNDARY", "cv1:" + "g" * 64,
        )
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(
                """INSERT INTO candles (
                    exchange,market_type,symbol,timeframe,open_time_ms,open,high,low,
                    close,volume,available_at_ms,availability_kind,candle_value_id
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                candle_values,
            )
        self.db.execute("PRAGMA foreign_keys=OFF")
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(
                """INSERT INTO candle_provenance_links (
                    link_id,exchange,market_type,symbol,timeframe,open_time_ms,
                    source_row_id,candle_value_id,duplicate_disposition
                ) VALUES (?,?,?,?,?,?,?,?,?)""",
                ("lnk1:" + "g" * 64, "binance", "usdm", "BTCUSDT", "15m", 0,
                 "row1:" + "1" * 64, "cv1:" + "2" * 64, "UNIQUE"),
            )

    def test_object_inventory_digest_and_identity_require_lowercase_hex(self):
        values = (
            "obj1:" + "g" * 64, "inv1:" + "1" * 64, "g" * 64, "entry",
            "synthetic.zip", "ZIP", "15m", "synthetic", "000", "synthetic.CHECKSUM",
            0, "QUARANTINED", "SYNTHETIC_FAILURE",
        )
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(
                """INSERT INTO archive_objects (
                    object_id,inventory_id,inventory_blob_sha256,inventory_entry_identity,
                    object_key,object_kind,timeframe,partition,period,paired_object_key,
                    response_bytes_total,verification_status,failure_code
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                values,
            )


class StagingSafetyAndAtomicityTests(unittest.TestCase):
    def test_file_database_requires_explicit_disposable_path_policy(self):
        with tempfile.TemporaryDirectory(prefix="t0-staging-v2-") as directory:
            path = Path(directory) / "synthetic-staging-test.sqlite3"
            with self.assertRaises((TypeError, ValueError)):
                connect_staging_database(path)
            self.assertFalse(path.exists())

    def test_disposable_path_policy_rejects_existing_file(self):
        with tempfile.TemporaryDirectory(prefix="t0-staging-v2-") as directory:
            path = Path(directory) / "synthetic-staging-test.sqlite3"
            path.write_bytes(b"do-not-open")
            with self.assertRaises((TypeError, ValueError)):
                connect_staging_database(path, allow_disposable_path=True)
            self.assertEqual(path.read_bytes(), b"do-not-open")

    def test_schema_initialization_rolls_back_table_phase_failure(self):
        from unittest.mock import patch
        import market_data.archive_staging_schema as schema

        connection = sqlite3.connect(":memory:")
        try:
            with patch.object(schema, "TABLE_DDL", schema.TABLE_DDL + ("CREATE TABLE broken (",)):
                with self.assertRaises(sqlite3.DatabaseError):
                    schema.initialize_staging_schema(connection)
            self.assertEqual(connection.execute("PRAGMA user_version").fetchone()[0], 0)
            self.assertEqual(
                connection.execute(
                    "SELECT name FROM sqlite_schema WHERE name NOT LIKE 'sqlite_%'"
                ).fetchall(),
                [],
            )
            self.assertFalse(connection.in_transaction)
        finally:
            connection.close()

    def test_schema_initialization_rolls_back_index_phase_failure(self):
        from unittest.mock import patch
        import market_data.archive_staging_schema as schema

        connection = sqlite3.connect(":memory:")
        try:
            with patch.object(schema, "INDEX_DDL", schema.INDEX_DDL + ("CREATE INDEX broken ON missing_table(x)",)):
                with self.assertRaises(sqlite3.DatabaseError):
                    schema.initialize_staging_schema(connection)
            self.assertEqual(connection.execute("PRAGMA user_version").fetchone()[0], 0)
            self.assertEqual(
                connection.execute(
                    "SELECT name FROM sqlite_schema WHERE name NOT LIKE 'sqlite_%'"
                ).fetchall(),
                [],
            )
        finally:
            connection.close()

    def test_schema_initialization_rolls_back_trigger_phase_failure(self):
        from unittest.mock import patch
        import market_data.archive_staging_schema as schema

        connection = sqlite3.connect(":memory:")
        try:
            with patch.object(schema, "TRIGGER_DDL", schema.TRIGGER_DDL + ("CREATE TRIGGER broken BEFORE INSERT ON missing_table BEGIN SELECT 1; END",)):
                with self.assertRaises(sqlite3.DatabaseError):
                    schema.initialize_staging_schema(connection)
            self.assertEqual(connection.execute("PRAGMA user_version").fetchone()[0], 0)
            self.assertEqual(
                connection.execute(
                    "SELECT name FROM sqlite_schema WHERE name NOT LIKE 'sqlite_%'"
                ).fetchall(),
                [],
            )
        finally:
            connection.close()


if __name__ == "__main__":
    unittest.main()
