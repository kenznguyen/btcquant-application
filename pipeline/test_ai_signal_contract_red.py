"""M2.4 RED specification for the independent AI signal contract.

The missing production module is intentional in this increment. These tests define
the public contract before a later, separately approved GREEN implementation.
"""

import unittest


NOW_MS = 1_800_000_000_000
POLICY = {
    "policyVersion": "ai-signal-policy-fixture-v1",
    "confidenceMin": "0.6",  # test fixture only; not a production threshold
    "minCalibrationSamples": 100,
    "minCalibrationPeriodMs": 100,
    "maxCalibrationAgeMs": 60_000,
    "labelDefinition": "direction_correct_at_horizon",
    "forecastHorizonMs": 900_000,
}


def valid_report(action="LONG"):
    return {
        "schemaVersion": 1,
        "source": "AI_STRATEGY",
        "action": action,
        "exchange": "binance",
        "marketType": "USDT_PERPETUAL",
        "symbol": "BTCUSDT",
        "timeframe": "15m",
        "strategyVersion": "ai-strategy-fixture-v1",
        "modelVersion": "model-fixture-v1",
        "datasetVersion": "sha256:" + "a" * 64,
        "inputSnapshotId": "snapshot-fixture-001",
        "decisionAtMs": NOW_MS - 1_000,
        "validUntilMs": NOW_MS + 30_000,
        "calibration": {
            "calibratedConfidence": "0.8",
            "calibrationVersion": "cal-fixture-v1",
            "calibrationMethod": "isotonic-fixture",
            "calibrationArtifactHash": "sha256:" + "b" * 64,
            "calibrationDatasetVersion": "sha256:" + "c" * 64,
            "calibrationSampleCount": 1_000,
            "calibrationStartMs": NOW_MS - 10_000,
            "calibrationEndMs": NOW_MS - 2_000,
            "calibratedAtMs": NOW_MS - 1_500,
            "labelDefinition": "direction_correct_at_horizon",
            "forecastHorizonMs": 900_000,
            "modelVersion": "model-fixture-v1",
            "strategyVersion": "ai-strategy-fixture-v1",
            "trainingDatasetVersion": "sha256:" + "a" * 64,
            "trainedThroughMs": NOW_MS - 20_000,
            "evidence": {
                "verificationStatus": "SIGNATURE_VERIFIED",
                "registryStatus": "ACTIVE",
                "trustedTimeStatus": "VERIFIED",
                "oosEvidenceStatus": "VERIFIED",
                "manifestDigest": "sha256:" + "d" * 64,
            },
        },
    }


class AISignalContractRedTest(unittest.TestCase):
    def validate(self, report, now_ms=NOW_MS, policy=POLICY):
        # Import inside each test so the RED run records each missing contract case.
        from pipeline.ai_signal_contract import validate_ai_signal

        return validate_ai_signal(report, now_ms, policy)

    def assert_wait(self, result):
        self.assertEqual(result["action"], "WAIT")
        self.assertIsNone(result["signal"])

    def test_ai_long_is_valid_without_any_core_signal_input(self):
        result = self.validate(valid_report("LONG"))
        self.assertEqual(result["source"], "AI_STRATEGY")
        self.assertEqual(result["action"], "LONG")
        self.assertIsNotNone(result["signal"])

    def test_ai_short_is_valid_without_any_core_signal_input(self):
        result = self.validate(valid_report("SHORT"))
        self.assertEqual(result["source"], "AI_STRATEGY")
        self.assertEqual(result["action"], "SHORT")
        self.assertIsNotNone(result["signal"])

    def test_core_wait_or_missing_core_report_does_not_suppress_ai_signal(self):
        # There is deliberately no Core report argument or Core state dependency.
        result = self.validate(valid_report("LONG"))
        self.assertEqual(result["action"], "LONG")

    def test_wait_is_diagnostic_and_never_creates_a_signal(self):
        result = self.validate(valid_report("WAIT"))
        self.assertEqual(result["action"], "WAIT")
        self.assertIsNone(result["signal"])

    def test_missing_calibration_or_policy_fails_closed(self):
        report = valid_report("LONG")
        report.pop("calibration")
        self.assert_wait(self.validate(report))
        self.assert_wait(self.validate(valid_report("LONG"), policy=None))

    def test_confidence_below_threshold_and_malformed_values_fail_closed(self):
        for confidence in ("0.59", "-0.01", "1.01", "NaN", "Infinity", True, "bad"):
            report = valid_report("LONG")
            report["calibration"]["calibratedConfidence"] = confidence
            with self.subTest(confidence=confidence):
                self.assert_wait(self.validate(report))

    def test_missing_or_mismatched_provenance_fails_closed(self):
        for field in ("strategyVersion", "modelVersion", "datasetVersion", "inputSnapshotId"):
            report = valid_report("LONG")
            report.pop(field)
            with self.subTest(field=field):
                self.assert_wait(self.validate(report))

    def test_wrong_market_and_expired_or_future_reports_fail_closed(self):
        cases = (
            {"symbol": "ETHUSDT"},
            {"timeframe": "1h"},
            {"decisionAtMs": NOW_MS + 1},
            {"validUntilMs": NOW_MS - 1},
        )
        for changes in cases:
            report = valid_report("LONG")
            report.update(changes)
            with self.subTest(changes=changes):
                self.assert_wait(self.validate(report))

    def test_calibration_leakage_staleness_and_unverified_evidence_fail_closed(self):
        cases = (
            {"calibrationStartMs": NOW_MS - 30_000, "trainedThroughMs": NOW_MS - 10_000},
            {"calibratedAtMs": NOW_MS - 120_000},
            {"verificationStatus": "UNVERIFIED"},
            {"registryStatus": "REVOKED"},
            {"trustedTimeStatus": "UNVERIFIED"},
            {"oosEvidenceStatus": "UNVERIFIED"},
        )
        for change in cases:
            report = valid_report("LONG")
            if "calibrationStartMs" in change:
                report["calibration"].update(change)
            elif "calibratedAtMs" in change:
                report["calibration"].update(change)
            else:
                report["calibration"]["evidence"].update(change)
            with self.subTest(change=change):
                self.assert_wait(self.validate(report))

    def test_output_is_signal_only_and_contains_no_execution_or_sizing_fields(self):
        result = self.validate(valid_report("LONG"))
        self.assertEqual(
            set(result),
            {"schemaVersion", "source", "action", "reason", "signal"},
        )
        forbidden = {
            "order", "intent", "quantity", "leverage", "marginBudget",
            "reservation", "ledger", "exchangeOrderId",
        }
        self.assertTrue(forbidden.isdisjoint(result))
        self.assertTrue(forbidden.isdisjoint(result["signal"]))


if __name__ == "__main__":
    unittest.main()
