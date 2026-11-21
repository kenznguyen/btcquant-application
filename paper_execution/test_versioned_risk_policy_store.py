import hashlib
import json
import sqlite3
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from paper_execution.versioned_risk_policy_store import (
    initialize_risk_policy_schema,
    load_active_versioned_risk_policy,
    publish_versioned_risk_policy,
)


class VersionedRiskPolicyStoreTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        initialize_risk_policy_schema(
            self.db, source_sha="a" * 40, applied_at_ms=1_800_000_000_000
        )
        self.policy = {
            "schemaVersion": 1,
            "policyVersion": "paper-risk-v1",
            "quoteAsset": "USDT",
            "maxSnapshotAgeMs": 120_000,
            "drawdownLimit": {"mode": "ABSOLUTE_QUOTE", "value": "100"},
            "maxDailyLossQuote": "25",
            "maxGrossExposureQuote": "500",
        }

    def tearDown(self):
        self.db.close()

    def publish(self, policy=None, expected=None, **metadata):
        document = self.policy if policy is None else policy
        raw = json.dumps(document, sort_keys=True, separators=(",", ":"))
        return publish_versioned_risk_policy(
            self.db,
            raw,
            expected_active_hash=expected,
            source_git_commit_sha="b" * 40,
            source_policy_sha256=hashlib.sha256(raw.encode()).hexdigest(),
            source_policy_path="config/risk_policies/paper-risk-v1.json",
            operator_id="operator:test",
            reason="Owner-approved test publication",
            published_at_ms=1_800_000_000_100,
            **metadata,
        )

    def test_publication_stores_full_canonical_payload_and_activates_atomically(self):
        result = self.publish()
        loaded = load_active_versioned_risk_policy(self.db)
        canonical = json.dumps(self.policy, sort_keys=True, separators=(",", ":"))
        expected_hash = hashlib.sha256(canonical.encode()).hexdigest()
        self.assertEqual(result["policyVersion"], "paper-risk-v1")
        self.assertEqual(result["payloadSha256"], expected_hash)
        self.assertEqual(loaded["payload"], self.policy)
        self.assertEqual(loaded["payloadSha256"], expected_hash)
        self.assertEqual(loaded["sourceGitCommitSha"], "b" * 40)

    def test_stale_compare_and_swap_cannot_replace_active_policy(self):
        first = self.publish()
        changed = dict(self.policy, policyVersion="paper-risk-v2", maxDailyLossQuote="20")
        with self.assertRaises(ValueError):
            self.publish(changed, expected="0" * 64)
        self.assertEqual(
            load_active_versioned_risk_policy(self.db)["payloadSha256"],
            first["payloadSha256"],
        )

    def test_successive_publication_preserves_immutable_history(self):
        first = self.publish()
        changed = dict(self.policy, policyVersion="paper-risk-v2", maxDailyLossQuote="20")
        second = self.publish(changed, expected=first["payloadSha256"])
        versions = self.db.execute(
            "SELECT policy_version,payload_json FROM paper_risk_policy_versions "
            "ORDER BY policy_version"
        ).fetchall()
        self.assertEqual([row[0] for row in versions], ["paper-risk-v1", "paper-risk-v2"])
        self.assertEqual(json.loads(versions[0][1]), self.policy)
        self.assertEqual(second["activationSequence"], 2)

    def test_published_payload_and_audit_rows_cannot_be_updated_or_deleted(self):
        self.publish()
        for statement in (
            "UPDATE paper_risk_policy_versions SET payload_json='{}'",
            "DELETE FROM paper_risk_policy_versions",
            "UPDATE paper_risk_policy_publication_audit SET reason='tampered'",
            "DELETE FROM paper_risk_policy_publication_audit",
        ):
            with self.subTest(statement=statement), self.assertRaises(sqlite3.IntegrityError):
                self.db.execute(statement)

    def test_active_pointer_requires_matching_audit_and_cannot_be_deleted_directly(self):
        self.publish()
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(
                "UPDATE paper_risk_policy_active SET payload_sha256=? WHERE account_id=1",
                ("0" * 64,),
            )
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("DELETE FROM paper_risk_policy_active WHERE account_id=1")

    def test_source_file_hash_must_match_exact_published_bytes(self):
        raw = json.dumps(self.policy, sort_keys=True, separators=(",", ":"))
        with self.assertRaises(ValueError):
            publish_versioned_risk_policy(
                self.db, raw, expected_active_hash=None,
                source_git_commit_sha="b" * 40,
                source_policy_path="config/risk_policies/paper-risk-v1.json",
                source_policy_sha256="0" * 64,
                operator_id="operator:test", reason="hash mismatch",
                published_at_ms=1_800_000_000_100,
            )

    def test_percent_high_water_drawdown_is_rejected_until_engine_contract_supports_it(self):
        percent_policy = dict(
            self.policy,
            drawdownLimit={"mode": "PERCENT_HWM", "value": "12.5"},
        )
        with self.assertRaisesRegex(ValueError, "RISK_POLICY_DRAWDOWN_MODE_UNSUPPORTED"):
            self.publish(percent_policy)
        self.assertIsNone(load_active_versioned_risk_policy(self.db))

    def test_invalid_policy_schema_and_git_provenance_are_rejected(self):
        invalid = [
            dict(self.policy, schemaVersion=2),
            dict(self.policy, policyVersion=""),
            dict(self.policy, maxSnapshotAgeMs=0),
            dict(self.policy, maxDailyLossQuote="NaN"),
            dict(self.policy, drawdownLimit={"mode": "UNKNOWN", "value": "10"}),
        ]
        for policy in invalid:
            with self.subTest(policy=policy), self.assertRaises(ValueError):
                self.publish(policy)
        with self.assertRaises(ValueError):
            publish_versioned_risk_policy(
                self.db, json.dumps(self.policy, sort_keys=True, separators=(",", ":")), expected_active_hash=None,
                source_git_commit_sha="not-a-commit", source_policy_sha256=hashlib.sha256(json.dumps(self.policy, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
                source_policy_path="../outside.json", operator_id="operator:test",
                reason="invalid source", published_at_ms=1_800_000_000_100,
            )

    def test_concurrent_publishers_with_same_expected_hash_have_exactly_one_winner(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "policy.sqlite3"
            setup = sqlite3.connect(path)
            initialize_risk_policy_schema(
                setup, source_sha="a" * 40, applied_at_ms=1_800_000_000_000
            )
            setup.close()

            def attempt(version):
                document = dict(self.policy, policyVersion=version)
                raw = json.dumps(document, sort_keys=True, separators=(",", ":"))
                db = sqlite3.connect(path, timeout=5, isolation_level=None)
                try:
                    return publish_versioned_risk_policy(
                        db, raw, expected_active_hash=None,
                        source_git_commit_sha="b" * 40,
                        source_policy_path=f"config/risk_policies/{version}.json",
                        source_policy_sha256=hashlib.sha256(raw.encode()).hexdigest(),
                        operator_id=f"operator:{version}", reason="concurrent CAS test",
                        published_at_ms=1_800_000_000_100,
                    )
                finally:
                    db.close()

            def capture(version):
                try:
                    return ("PASS", attempt(version))
                except ValueError as exc:
                    return ("DENIED", str(exc))

            with ThreadPoolExecutor(max_workers=2) as pool:
                results = list(pool.map(capture, ("paper-risk-a", "paper-risk-b")))
            self.assertEqual(sum(status == "PASS" for status, _ in results), 1)
            self.assertEqual(sum(
                status == "DENIED" and value == "RISK_POLICY_ACTIVE_VERSION_CONFLICT"
                for status, value in results
            ), 1)
            db = sqlite3.connect(path)
            try:
                self.assertEqual(
                    db.execute("SELECT COUNT(*) FROM paper_risk_policy_active").fetchone()[0],
                    1,
                )
                self.assertEqual(
                    db.execute("SELECT COUNT(*) FROM paper_risk_policy_publication_audit").fetchone()[0],
                    1,
                )
                self.assertEqual(
                    db.execute("SELECT COUNT(*) FROM paper_risk_policy_versions").fetchone()[0],
                    1,
                )
            finally:
                db.close()

    def test_existing_database_schema_is_required_and_not_auto_created_by_publish(self):
        empty = sqlite3.connect(":memory:")
        try:
            with self.assertRaises(sqlite3.DatabaseError):
                publish_versioned_risk_policy(
                    empty, json.dumps(self.policy, sort_keys=True, separators=(",", ":")), expected_active_hash=None,
                    source_git_commit_sha="b" * 40,
                    source_policy_path="config/risk_policies/paper-risk-v1.json", source_policy_sha256=hashlib.sha256(json.dumps(self.policy, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
                    operator_id="operator:test", reason="no schema",
                    published_at_ms=1_800_000_000_100,
                )
            self.assertEqual(
                empty.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall(),
                [],
            )
        finally:
            empty.close()


if __name__ == "__main__":
    unittest.main()
