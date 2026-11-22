"""Synthetic-only SQLite staging schema v2 tests; disposable DBs only."""
import sqlite3
import unittest

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
        object_id = "obj1:" + suffix * 64
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


if __name__ == "__main__":
    unittest.main()
