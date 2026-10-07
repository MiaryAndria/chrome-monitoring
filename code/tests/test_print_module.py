import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.google_api.print import extract_printers_from_telemetry, enrich_print_logs


class TestPrintModule(unittest.TestCase):
    def test_print_module_exports(self):
        self.assertTrue(callable(extract_printers_from_telemetry))
        self.assertTrue(callable(enrich_print_logs))


if __name__ == "__main__":
    unittest.main()
