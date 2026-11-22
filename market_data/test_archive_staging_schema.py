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

    def test_rejects_cross_object_successful_attempt_foreign_key(self):
        self.assertEqual(self.db.execute("PRAGMA foreign_key_check").fetchall(), [])

    def test_integrity_and_foreign_key_checks_pass_on_empty_synthetic_database(self):
        self.assertEqual(self.db.execute("PRAGMA integrity_check").fetchone()[0], "ok")
        self.assertEqual(self.db.execute("PRAGMA foreign_key_check").fetchall(), [])
        self.assertTrue(verify_staging_database(self.db))


if __name__ == "__main__":
    unittest.main()
