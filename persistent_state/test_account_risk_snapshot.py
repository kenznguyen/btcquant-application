import unittest
from dataclasses import FrozenInstanceError
from typing import get_type_hints

from persistent_state.account_risk import (
    AccountRiskProvenance,
    AccountRiskSnapshot,
    AccountRiskSnapshotProvider,
)


def valid_snapshot(**overrides):
    values = {
        "snapshot_id": "risk-snapshot-001",
        "schema_version": 1,
        "account_scope_id": "paper-account",
        "session_id": "session-001",
        "fencing_generation": 3,
        "generated_at_ms": 2_000,
        "as_of_ms": 1_900,
        "quote_asset": "USDT",
        "account_equity_quote": "1000.00",
        "gross_exposure_quote": "250.00",
        "reserved_margin_quote": "25.00",
        "drawdown_quote": "10.00",
        "daily_loss_quote": "5.00",
        "provenance": AccountRiskProvenance(
            provider_id="paper-account-provider",
            source_id="account-ledger-v1",
            source_snapshot_id="source-snapshot-001",
            source_version="ledger-schema-v3",
            source_payload_sha256="sha256:" + "a" * 64,
        ),
        "verified": True,
        "ledger_reconciled": True,
    }
    values.update(overrides)
    return AccountRiskSnapshot(**values)


class AccountRiskSnapshotContractTests(unittest.TestCase):
    def test_valid_snapshot_is_immutable_and_exact_decimal(self):
        snapshot = valid_snapshot()
        self.assertEqual(snapshot.account_equity_quote, "1000.00")
        with self.assertRaises(FrozenInstanceError):
            snapshot.account_equity_quote = "1"

    def test_provider_provenance_is_required_and_immutable(self):
        provenance = valid_snapshot().provenance
        with self.assertRaises(FrozenInstanceError):
            provenance.source_id = "other-source"

    def test_rejects_wrong_schema_version(self):
        with self.assertRaisesRegex(ValueError, "schema_version"):
            valid_snapshot(schema_version=2)

    def test_rejects_missing_or_blank_identity_and_scope(self):
        for field in ("snapshot_id", "account_scope_id", "session_id"):
            with self.subTest(field=field), self.assertRaises(ValueError):
                valid_snapshot(**{field: " "})

    def test_rejects_invalid_fencing_generation(self):
        for value in (0, -1, True, 1.0):
            with self.subTest(value=value), self.assertRaises(ValueError):
                valid_snapshot(fencing_generation=value)

    def test_rejects_invalid_timestamps_and_future_source_time(self):
        for changes in (
            {"generated_at_ms": -1},
            {"as_of_ms": -1},
            {"as_of_ms": 2_001},
            {"generated_at_ms": True},
        ):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                valid_snapshot(**changes)

    def test_rejects_binary_float_and_noncanonical_money(self):
        for value in (1000.0, "1e3", "NaN", "Infinity", "-1", "+1", " 1", ""):
            with self.subTest(value=value), self.assertRaises(ValueError):
                valid_snapshot(account_equity_quote=value)

    def test_equity_must_be_strictly_positive(self):
        for value in ("0", "0.00"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                valid_snapshot(account_equity_quote=value)

    def test_other_risk_amounts_must_be_nonnegative_exact_decimals(self):
        for field in (
            "gross_exposure_quote", "reserved_margin_quote",
            "drawdown_quote", "daily_loss_quote",
        ):
            for value in ("-0.01", "NaN", 1.0):
                with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                    valid_snapshot(**{field: value})

    def test_quote_asset_must_be_canonical_uppercase_code(self):
        for value in ("usdt", "USDT-PERP", "", "BTC USDT"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                valid_snapshot(quote_asset=value)

    def test_rejects_invalid_provenance_and_payload_hash(self):
        for changes in (
            {"provider_id": ""},
            {"source_id": " "},
            {"source_snapshot_id": ""},
            {"source_version": ""},
            {"source_payload_sha256": "a" * 64},
        ):
            provenance = valid_snapshot().provenance
            fields = {
                "provider_id": provenance.provider_id,
                "source_id": provenance.source_id,
                "source_snapshot_id": provenance.source_snapshot_id,
                "source_version": provenance.source_version,
                "source_payload_sha256": provenance.source_payload_sha256,
            }
            fields.update(changes)
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                AccountRiskProvenance(**fields)

    def test_verification_and_reconciliation_flags_must_be_boolean(self):
        for field in ("verified", "ledger_reconciled"):
            with self.subTest(field=field), self.assertRaises(ValueError):
                valid_snapshot(**{field: 1})

    def test_unverified_or_unreconciled_snapshot_is_representable_for_fail_closed_gate_tests(self):
        self.assertFalse(valid_snapshot(verified=False).verified)
        self.assertFalse(valid_snapshot(ledger_reconciled=False).ledger_reconciled)

    def test_snapshot_binding_requires_exact_account_session_and_fence(self):
        from persistent_state.account_risk import validate_snapshot_binding

        snapshot = valid_snapshot()
        self.assertIs(
            validate_snapshot_binding(
                snapshot, account_scope_id="paper-account",
                session_id="session-001", fencing_generation=3,
            ),
            snapshot,
        )
        for changes in (
            {"account_scope_id": "other-account"},
            {"session_id": "other-session"},
            {"fencing_generation": 4},
        ):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                validate_snapshot_binding(
                    snapshot, account_scope_id=changes.get("account_scope_id", "paper-account"),
                    session_id=changes.get("session_id", "session-001"),
                    fencing_generation=changes.get("fencing_generation", 3),
                )

    def test_unverified_or_unreconciled_snapshot_is_rejected_by_binding_gate(self):
        from persistent_state.account_risk import validate_snapshot_binding

        for snapshot in (
            valid_snapshot(verified=False),
            valid_snapshot(ledger_reconciled=False),
        ):
            with self.subTest(snapshot=snapshot), self.assertRaises(ValueError):
                validate_snapshot_binding(
                    snapshot, account_scope_id="paper-account",
                    session_id="session-001", fencing_generation=3,
                )

    def test_binding_gate_rejects_untyped_snapshot(self):
        from persistent_state.account_risk import validate_snapshot_binding

        with self.assertRaises(ValueError):
            validate_snapshot_binding(
                object(), account_scope_id="paper-account",
                session_id="session-001", fencing_generation=3,
            )

    def test_provider_protocol_requires_scoped_snapshot_read(self):
        hints = get_type_hints(AccountRiskSnapshotProvider.read_snapshot)
        self.assertEqual(
            set(hints),
            {"account_scope_id", "session_id", "fencing_generation", "return"},
        )
        self.assertIs(hints["return"], AccountRiskSnapshot)


if __name__ == "__main__":
    unittest.main()
