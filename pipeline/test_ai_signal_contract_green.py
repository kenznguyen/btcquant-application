"""M2.5 GREEN coverage for the pure AI Strategy signal validator."""
import unittest

from pipeline.ai_signal_contract import validate_ai_signal

NOW = 1_800_000_000_000
POLICY = {
    "policyVersion": "policy-v1",
    "confidenceMin": "0.6",
    "minCalibrationSamples": 100,
    "minCalibrationPeriodMs": 100,
    "maxCalibrationAgeMs": 60_000,
    "labelDefinition": "direction_correct_at_horizon",
    "forecastHorizonMs": 900_000,
}


def report(action="LONG"):
    return {
        "schemaVersion": 1,
        "source": "AI_STRATEGY",
        "action": action,
        "exchange": "binance",
        "marketType": "USDT_PERPETUAL",
        "symbol": "BTCUSDT",
        "timeframe": "15m",
        "strategyVersion": "strategy-v1",
        "modelVersion": "model-v1",
        "datasetVersion": "sha256:" + "a" * 64,
        "inputSnapshotId": "snapshot-1",
        "decisionAtMs": NOW - 1_000,
        "validUntilMs": NOW + 30_000,
        "calibration": {
            "calibratedConfidence": "0.8",
            "calibrationVersion": "cal-v1",
            "calibrationMethod": "isotonic",
            "calibrationArtifactHash": "sha256:" + "b" * 64,
            "calibrationDatasetVersion": "sha256:" + "c" * 64,
            "calibrationSampleCount": 1_000,
            "calibrationStartMs": NOW - 10_000,
            "calibrationEndMs": NOW - 2_000,
            "calibratedAtMs": NOW - 1_500,
            "labelDefinition": "direction_correct_at_horizon",
            "forecastHorizonMs": 900_000,
            "modelVersion": "model-v1",
            "strategyVersion": "strategy-v1",
            "trainingDatasetVersion": "sha256:" + "a" * 64,
            "trainedThroughMs": NOW - 20_000,
            "evidence": {
                "verificationStatus": "SIGNATURE_VERIFIED",
                "registryStatus": "ACTIVE",
                "trustedTimeStatus": "VERIFIED",
                "oosEvidenceStatus": "VERIFIED",
                "manifestDigest": "sha256:" + "d" * 64,
            },
        },
    }


class ValidatorGreenTests(unittest.TestCase):
    def assert_wait(self, result):
        self.assertEqual(result["action"], "WAIT")
        self.assertIsNone(result["signal"])
        self.assertTrue(result["reason"].startswith("AI_"))

    def test_long_and_short_are_independent_and_signal_only(self):
        for action in ("LONG", "SHORT"):
            result = validate_ai_signal(report(action), NOW, POLICY)
            self.assertEqual(result["action"], action)
            self.assertEqual(result["reason"], "AI_SIGNAL_VALIDATED")
            self.assertEqual(result["signal"]["calibratedConfidence"], "0.8")
            self.assertEqual(
                set(result), {"schemaVersion", "source", "action", "reason", "signal"}
            )
            self.assertEqual(result["source"], "AI_STRATEGY")

    def test_wait_is_diagnostic_without_calibration_or_policy(self):
        value = report("WAIT")
        value.pop("calibration")
        self.assert_wait(validate_ai_signal(value, NOW, None))

    def test_missing_policy_and_calibration_fail_closed(self):
        self.assert_wait(validate_ai_signal(report(), NOW, None))
        value = report()
        value.pop("calibration")
        self.assert_wait(validate_ai_signal(value, NOW, POLICY))

    def test_bad_confidence_values_fail_closed(self):
        for confidence in ("0.59", "-0.1", "1.01", "NaN", "Infinity", True, "bad", None):
            value = report()
            value["calibration"]["calibratedConfidence"] = confidence
            with self.subTest(confidence=confidence):
                self.assert_wait(validate_ai_signal(value, NOW, POLICY))

    def test_policy_must_be_explicit_and_well_formed(self):
        cases = (
            ("confidenceMin", "1"),
            ("confidenceMin", True),
            ("minCalibrationSamples", True),
            ("minCalibrationPeriodMs", 0),
            ("maxCalibrationAgeMs", -1),
            ("forecastHorizonMs", 0),
            ("labelDefinition", ""),
            ("policyVersion", None),
        )
        for field, value in cases:
            policy = dict(POLICY)
            policy[field] = value
            with self.subTest(field=field, value=value):
                self.assert_wait(validate_ai_signal(report(), NOW, policy))

    def test_market_identity_and_timestamp_window_fail_closed(self):
        cases = (
            {"symbol": "ETHUSDT"},
            {"timeframe": "1h"},
            {"exchange": "okx"},
            {"marketType": "SPOT"},
            {"decisionAtMs": NOW + 1},
            {"validUntilMs": NOW - 1},
            {"validUntilMs": NOW + 60_001},
            {"decisionAtMs": True},
            {"validUntilMs": 1.0},
            {"schemaVersion": 1.0},
        )
        for changes in cases:
            value = report()
            value.update(changes)
            with self.subTest(changes=changes):
                self.assert_wait(validate_ai_signal(value, NOW, POLICY))

    def test_provenance_required_and_must_match(self):
        for field in ("strategyVersion", "modelVersion", "datasetVersion", "inputSnapshotId"):
            value = report()
            value.pop(field)
            with self.subTest(field=field):
                self.assert_wait(validate_ai_signal(value, NOW, POLICY))
        for field, replacement in (
            ("modelVersion", "other"),
            ("strategyVersion", "other"),
            ("trainingDatasetVersion", "sha256:" + "e" * 64),
        ):
            value = report()
            value["calibration"][field] = replacement
            with self.subTest(field=field):
                self.assert_wait(validate_ai_signal(value, NOW, POLICY))

    def test_calibration_minimums_and_temporal_order(self):
        cases = (
            {"calibrationSampleCount": 99},
            {"calibrationStartMs": NOW - 100},
            {"calibrationEndMs": NOW - 15_000},
            {"trainedThroughMs": NOW - 5_000},
            {"calibratedAtMs": NOW + 1},
            {"calibratedAtMs": NOW - 120_000},
        )
        for changes in cases:
            value = report()
            value["calibration"].update(changes)
            with self.subTest(changes=changes):
                self.assert_wait(validate_ai_signal(value, NOW, POLICY))

    def test_calibration_policy_label_and_horizon_must_match(self):
        cases = (
            ("labelDefinition", "other"),
            ("forecastHorizonMs", 300_000),
            ("calibrationDatasetVersion", ""),
        )
        for field, replacement in cases:
            value = report()
            value["calibration"][field] = replacement
            with self.subTest(field=field):
                self.assert_wait(validate_ai_signal(value, NOW, POLICY))

    def test_evidence_envelope_must_be_verified_active_and_well_formed(self):
        cases = (
            {"verificationStatus": "UNVERIFIED"},
            {"registryStatus": "REVOKED"},
            {"trustedTimeStatus": "UNVERIFIED"},
            {"oosEvidenceStatus": "UNVERIFIED"},
            {"manifestDigest": "bad"},
        )
        for changes in cases:
            value = report()
            value["calibration"]["evidence"].update(changes)
            with self.subTest(changes=changes):
                self.assert_wait(validate_ai_signal(value, NOW, POLICY))

    def test_unknown_action_and_malformed_input_never_raise(self):
        for action in (None, [], "BUY", {}, 7):
            value = report()
            value["action"] = action
            self.assert_wait(validate_ai_signal(value, NOW, POLICY))
        for value in (None, [], "bad", True):
            self.assert_wait(validate_ai_signal(value, NOW, POLICY))

    def test_input_is_not_mutated_and_result_is_deterministic(self):
        value = report()
        before = repr(value)
        first = validate_ai_signal(value, NOW, POLICY)
        second = validate_ai_signal(value, NOW, POLICY)
        self.assertEqual(repr(value), before)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
