"""Regression guards for the approved WSGI/Gunicorn retirement."""

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class WsgiRetirementTest(unittest.TestCase):
    def test_legacy_wsgi_module_is_not_importable(self):
        self.assertIsNone(importlib.util.find_spec("market_data.api"))

    def test_gunicorn_is_absent_from_t0_runtime_manifest_and_lock(self):
        manifest = (ROOT / "requirements-market-data.txt").read_text().lower()
        lock = (ROOT / "requirements-market-data.lock").read_text().lower()
        self.assertNotIn("gunicorn", manifest)
        self.assertNotIn("gunicorn", lock)


if __name__ == "__main__":
    unittest.main()
