"""Synthetic-only B4 resource policy contract tests.

These tests deliberately use authored metadata only. They must never open archives,
inspect the host filesystem, perform network requests, or create a database.
"""
import unittest

from market_data.archive_resource_policy import (
    RESOURCE_LIMITS,
    classify_zip_member,
    retry_delay_seconds,
    validate_concurrency,
    validate_resource_metadata,
)


def valid_resource_metadata():
    return {
        "response_bytes_total": 1,
        "zip_body_bytes": 1,
        "sidecar_bytes": 1,
        "zip_entry_count": 1,
        "member_uncompressed_bytes": 1,
        "zip_uncompressed_bytes": 1,
        "run_uncompressed_bytes": 1,
        "member_compressed_bytes": 1,
        "member_path": "data.csv",
    }


class ResourceCeilingTests(unittest.TestCase):
    def test_frozen_policy_ceilings(self):
        self.assertEqual(RESOURCE_LIMITS["response_bytes_total"], 100 * 1024 * 1024)
        self.assertEqual(RESOURCE_LIMITS["zip_body_bytes"], 64 * 1024 * 1024)
        self.assertEqual(RESOURCE_LIMITS["sidecar_bytes"], 64 * 1024)
        self.assertEqual(RESOURCE_LIMITS["zip_entry_count"], 1024)
        self.assertEqual(RESOURCE_LIMITS["member_uncompressed_bytes"], 256 * 1024 * 1024)
        self.assertEqual(RESOURCE_LIMITS["zip_uncompressed_bytes"], 512 * 1024 * 1024)
        self.assertEqual(RESOURCE_LIMITS["run_uncompressed_bytes"], 4 * 1024 * 1024 * 1024)
        self.assertEqual(RESOURCE_LIMITS["compression_ratio"], 100)
        self.assertEqual(RESOURCE_LIMITS["member_path_bytes"], 1024)

    def test_values_at_or_below_each_ceiling_are_accepted(self):
        metadata = valid_resource_metadata()
        for key, ceiling in RESOURCE_LIMITS.items():
            if key in metadata:
                metadata[key] = ceiling
        self.assertEqual(validate_resource_metadata(metadata), ())

    def test_each_limit_is_rejected_above_its_ceiling(self):
        mapping = {
            "response_bytes_total": "response_bytes_total",
            "zip_body_bytes": "zip_body_bytes",
            "sidecar_bytes": "sidecar_bytes",
            "zip_entry_count": "zip_entry_count",
            "member_uncompressed_bytes": "member_uncompressed_bytes",
            "zip_uncompressed_bytes": "zip_uncompressed_bytes",
            "run_uncompressed_bytes": "run_uncompressed_bytes",
        }
        for field, code in mapping.items():
            with self.subTest(field=field):
                metadata = valid_resource_metadata()
                metadata[field] = RESOURCE_LIMITS[field] + 1
                self.assertIn(code.upper() + "_EXCEEDED", validate_resource_metadata(metadata))

    def test_compression_ratio_is_bounded(self):
        metadata = valid_resource_metadata()
        metadata.update(member_compressed_bytes=1, member_uncompressed_bytes=101)
        self.assertIn("COMPRESSION_RATIO_EXCEEDED", validate_resource_metadata(metadata))

    def test_zero_compressed_size_with_nonzero_payload_fails_closed(self):
        metadata = valid_resource_metadata()
        metadata.update(member_compressed_bytes=0, member_uncompressed_bytes=1)
        self.assertIn("COMPRESSED_SIZE_INVALID", validate_resource_metadata(metadata))

    def test_multibyte_member_path_uses_utf8_byte_length(self):
        metadata = valid_resource_metadata()
        metadata["member_path"] = "é" * 513
        self.assertIn("MEMBER_PATH_TOO_LONG", validate_resource_metadata(metadata))

    def test_missing_boolean_float_negative_and_overflow_metadata_fail_closed(self):
        for mutate in (
            lambda value: value.pop("zip_entry_count"),
            lambda value: value.update(zip_entry_count=True),
            lambda value: value.update(zip_entry_count=1.5),
            lambda value: value.update(zip_entry_count=-1),
            lambda value: value.update(zip_entry_count=2**80),
        ):
            with self.subTest(mutate=mutate):
                metadata = valid_resource_metadata()
                mutate(metadata)
                self.assertTrue(validate_resource_metadata(metadata))


class ZipMemberSafetyTests(unittest.TestCase):
    def test_safe_relative_csv_member(self):
        self.assertEqual(classify_zip_member({"path": "nested/data.csv"}), "ACCEPT")

    def test_rejects_absolute_drive_parent_nul_and_duplicate_paths(self):
        cases = (
            ({"path": "/data.csv"}, "ABSOLUTE_PATH"),
            ({"path": "C:/data.csv"}, "DRIVE_PATH"),
            ({"path": "../data.csv"}, "PATH_TRAVERSAL"),
            ({"path": "nested/../../data.csv"}, "PATH_TRAVERSAL"),
            ({"path": "data\u0000.csv"}, "NUL_PATH"),
        )
        for metadata, expected in cases:
            with self.subTest(path=metadata["path"]):
                self.assertEqual(classify_zip_member(metadata), expected)
        self.assertEqual(
            classify_zip_member({"path": "data.csv"}, seen_paths=("data.csv",)),
            "DUPLICATE_PATH",
        )

    def test_rejects_symlink_encrypted_and_unsupported_compression(self):
        self.assertEqual(classify_zip_member({"path": "data.csv", "is_symlink": True}), "SYMLINK")
        self.assertEqual(classify_zip_member({"path": "data.csv", "encrypted": True}), "ENCRYPTED")
        self.assertEqual(
            classify_zip_member({"path": "data.csv", "compression_method": 99}),
            "UNSUPPORTED_COMPRESSION",
        )


class RetryAndConcurrencyTests(unittest.TestCase):
    def test_only_transient_failures_are_retried(self):
        self.assertEqual(retry_delay_seconds(attempt=1, status_code=408), 2)
        self.assertEqual(retry_delay_seconds(attempt=2, status_code=429), 10)
        self.assertEqual(retry_delay_seconds(attempt=1, status_code=503), 2)
        self.assertIsNone(retry_delay_seconds(attempt=1, status_code=404))
        self.assertIsNone(retry_delay_seconds(attempt=1, status_code=400))
        self.assertIsNone(retry_delay_seconds(attempt=1, status_code=200))

    def test_connection_failure_and_retry_after_are_bounded(self):
        self.assertEqual(retry_delay_seconds(attempt=1, transient_error=True), 2)
        self.assertEqual(
            retry_delay_seconds(attempt=2, status_code=429, retry_after_seconds=4),
            4,
        )
        self.assertIsNone(
            retry_delay_seconds(attempt=1, status_code=429, retry_after_seconds=11)
        )

    def test_no_retry_after_three_total_attempts(self):
        self.assertIsNone(retry_delay_seconds(attempt=3, status_code=503))
        self.assertIsNone(retry_delay_seconds(attempt=0, status_code=503))

    def test_network_and_zip_processing_concurrency_are_each_one(self):
        self.assertTrue(validate_concurrency(network_active=1, zip_active=1))
        self.assertFalse(validate_concurrency(network_active=2, zip_active=1))
        self.assertFalse(validate_concurrency(network_active=1, zip_active=2))
        self.assertFalse(validate_concurrency(network_active=0, zip_active=1))
        self.assertFalse(validate_concurrency(network_active=True, zip_active=1))


if __name__ == "__main__":
    unittest.main()
