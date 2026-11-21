import sqlite3
import tempfile
import unittest
from pathlib import Path

from paper_execution.ledger import PaperLedger
from paper_execution.account_scope_binding import (
    migrate_paper_account_scope_binding,
    resolve_paper_account_binding,
)
from persistent_state.repository import SQLiteStateRepository
from persistent_state.test_session_fencing import start_running


class PaperAccountScopeFencingBindingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.paper_path = Path(self.temp.name) / "paper.sqlite3"
        self.state_path = Path(self.temp.name) / "state.sqlite3"
        PaperLedger(
            self.paper_path, strategy_id="STRATEGY_CORE",
            source_sha="a" * 40, max_position_base="1",
        )
        self.state = SQLiteStateRepository(self.state_path)
        self.state.initialize()

    def bind_paper_scope(self, scope="paper-account"):
        with sqlite3.connect(self.paper_path) as db:
            migrate_paper_account_scope_binding(
                db, account_scope_id=scope, source_sha="a" * 40,
                applied_at_ms=1_800_000_000_000,
            )

    def test_account_scope_migration_is_explicit_immutable_and_idempotent(self):
        self.bind_paper_scope()
        self.bind_paper_scope()
        with sqlite3.connect(self.paper_path) as db:
            self.assertEqual(
                db.execute("SELECT account_scope_id FROM paper_accounts WHERE account_id=1").fetchone()[0],
                "paper-account",
            )
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute(
                    "UPDATE paper_accounts SET account_scope_id='other' WHERE account_id=1"
                )
        with sqlite3.connect(self.paper_path) as db:
            with self.assertRaisesRegex(sqlite3.DatabaseError, "ACCOUNT_SCOPE_BINDING_CONFLICT"):
                migrate_paper_account_scope_binding(
                    db, account_scope_id="other", source_sha="a" * 40,
                    applied_at_ms=1_800_000_000_001,
                )

    def test_binding_requires_active_authoritative_session_and_exact_fence(self):
        self.bind_paper_scope()
        token = start_running(self.state, "session-1")
        binding = resolve_paper_account_binding(
            self.paper_path, self.state, account_id=1,
            session_id=token.session_id,
            fencing_generation=token.fencing_generation,
        )
        self.assertEqual(binding.account_scope_id, "paper-account")
        self.assertEqual(binding.session_id, "session-1")
        self.assertEqual(binding.fencing_generation, 1)

    def test_binding_rejects_stale_session_after_new_owner_claim(self):
        self.bind_paper_scope()
        old = start_running(self.state, "session-old")
        start_running(self.state, "session-new", start=1_800_000_010_000)
        with self.assertRaisesRegex(ValueError, "PAPER_SESSION_FENCE_NOT_CURRENT"):
            resolve_paper_account_binding(
                self.paper_path, self.state, account_id=1,
                session_id=old.session_id,
                fencing_generation=old.fencing_generation,
            )

    def test_binding_rejects_wrong_scope_and_non_paper_account(self):
        self.bind_paper_scope()
        token = start_running(self.state, "session-1", account="another-scope")
        with self.assertRaisesRegex(ValueError, "PAPER_SESSION_FENCE_NOT_CURRENT"):
            resolve_paper_account_binding(
                self.paper_path, self.state, account_id=1,
                session_id=token.session_id,
                fencing_generation=token.fencing_generation,
            )
        with self.assertRaisesRegex(ValueError, "PAPER_ACCOUNT_IDENTITY_INVALID"):
            resolve_paper_account_binding(
                self.paper_path, self.state, account_id=2,
                session_id=token.session_id,
                fencing_generation=token.fencing_generation,
            )

    def test_binding_rejects_session_that_has_not_reached_running(self):
        self.bind_paper_scope()
        token = self.state.claim_writer(
            __import__("persistent_state.test_session_fencing", fromlist=["make_session"]).make_session("session-starting")
        )
        with self.assertRaisesRegex(ValueError, "PAPER_SESSION_FENCE_NOT_CURRENT"):
            resolve_paper_account_binding(
                self.paper_path, self.state, account_id=1,
                session_id=token.session_id,
                fencing_generation=token.fencing_generation,
            )

    def test_unbound_legacy_paper_account_fails_closed(self):
        with self.assertRaisesRegex(sqlite3.DatabaseError, "PAPER_ACCOUNT_SCOPE_BINDING_MISSING"):
            resolve_paper_account_binding(
                self.paper_path, self.state, account_id=1,
                session_id="session-1", fencing_generation=1,
            )


if __name__ == "__main__":
    unittest.main()
