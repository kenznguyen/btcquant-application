"""Regression tests for the independent PAPER_DB path contract."""

import os
import tempfile
import unittest
from pathlib import Path

from paper_execution.database_paths import PaperDatabasePathError, resolve_paper_db_path


class PaperDatabasePathTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.t0 = self.root / "market.sqlite3"
        self.t0.write_bytes(b"t0")
        self.paper = self.root / "paper.sqlite3"

    def test_paper_db_is_required(self):
        with self.assertRaisesRegex(PaperDatabasePathError, "PAPER_DB_UNCONFIGURED"):
            resolve_paper_db_path({"MARKET_DATA_DB": str(self.t0)})

    def test_same_path_is_rejected_even_before_paper_file_exists(self):
        with self.assertRaisesRegex(PaperDatabasePathError, "PAPER_DB_MUST_BE_DISTINCT"):
            resolve_paper_db_path({"MARKET_DATA_DB": str(self.t0), "PAPER_DB": str(self.t0)})

    def test_normalized_path_alias_is_rejected(self):
        alias = self.root / "nested" / ".." / "market.sqlite3"
        with self.assertRaisesRegex(PaperDatabasePathError, "PAPER_DB_MUST_BE_DISTINCT"):
            resolve_paper_db_path({"MARKET_DATA_DB": str(self.t0), "PAPER_DB": str(alias)})

    def test_hard_link_alias_is_rejected(self):
        os.link(self.t0, self.paper)
        with self.assertRaisesRegex(PaperDatabasePathError, "PAPER_DB_MUST_BE_DISTINCT"):
            resolve_paper_db_path({"MARKET_DATA_DB": str(self.t0), "PAPER_DB": str(self.paper)})

    def test_symlink_paper_path_is_rejected(self):
        alias = self.root / "paper-link.sqlite3"
        alias.symlink_to(self.paper)
        with self.assertRaisesRegex(PaperDatabasePathError, "PAPER_DB_SYMLINK_FORBIDDEN"):
            resolve_paper_db_path({"MARKET_DATA_DB": str(self.t0), "PAPER_DB": str(alias)})

    def test_missing_paper_file_is_rejected_when_required(self):
        with self.assertRaisesRegex(PaperDatabasePathError, "PAPER_DB_FILE_REQUIRED"):
            resolve_paper_db_path(
                {"MARKET_DATA_DB": str(self.t0), "PAPER_DB": str(self.paper)},
                require_exists=True,
            )

    def test_t0_feeder_lease_path_is_also_excluded(self):
        lease = self.root / "lease.sqlite3"
        lease.write_bytes(b"lease")
        with self.assertRaisesRegex(PaperDatabasePathError, "T0_LEDGER_PATH_FORBIDDEN"):
            resolve_paper_db_path(
                {"MARKET_DATA_DB": str(self.t0), "T0_FEEDER_LEASE_DB": str(lease),
                 "PAPER_DB": str(lease)}
            )


if __name__ == "__main__":
    unittest.main()
