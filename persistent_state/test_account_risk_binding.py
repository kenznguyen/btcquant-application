import unittest

from persistent_state.account_risk import (
    PaperAccountBinding,
    validate_paper_account_binding,
)


class PaperAccountBindingTests(unittest.TestCase):
    def binding(self, **changes):
        values = dict(
            account_id=1,
            account_mode="PAPER",
            account_scope_id="paper-account",
            session_id="session-001",
            fencing_generation=7,
        )
        values.update(changes)
        return PaperAccountBinding(**values)

    def test_binding_accepts_only_exact_account_session_and_fence(self):
        binding = self.binding()
        self.assertIs(
            validate_paper_account_binding(
                binding,
                account_id=1,
                account_mode="PAPER",
                account_scope_id="paper-account",
                session_id="session-001",
                fencing_generation=7,
            ),
            binding,
        )

    def test_binding_rejects_wrong_or_live_account_identity(self):
        for changes in (
            {"account_id": 2},
            {"account_mode": "LIVE"},
            {"account_id": True},
            {"account_mode": ""},
        ):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.binding(**changes)

    def test_binding_rejects_account_scope_session_or_fence_mismatch(self):
        binding = self.binding()
        mismatches = (
            {"account_id": 2},
            {"account_mode": "LIVE"},
            {"account_scope_id": "other-account"},
            {"session_id": "other-session"},
            {"fencing_generation": 8},
        )
        for changes in mismatches:
            expected = dict(
                account_id=1,
                account_mode="PAPER",
                account_scope_id="paper-account",
                session_id="session-001",
                fencing_generation=7,
            )
            expected.update(changes)
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                validate_paper_account_binding(binding, **expected)

    def test_binding_gate_rejects_untyped_and_missing_context(self):
        with self.assertRaises(ValueError):
            validate_paper_account_binding(
                object(),
                account_id=1,
                account_mode="PAPER",
                account_scope_id="paper-account",
                session_id="session-001",
                fencing_generation=7,
            )
        with self.assertRaises(ValueError):
            validate_paper_account_binding(
                self.binding(),
                account_id=1,
                account_mode="PAPER",
                account_scope_id="paper-account",
                session_id="",
                fencing_generation=7,
            )


if __name__ == "__main__":
    unittest.main()
