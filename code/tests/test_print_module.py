import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.google_api.print import extract_printers_from_telemetry, enrich_print_logs
from backend.fonction.metier.repository.rapport import recuperation_json_brut
from backend.fonction.metier.service.backfill_service import _resolve_historic_date, _should_skip_historical_insert


class DummyCursor:
    def __init__(self, rows=None):
        self.rows = rows or [(1, 2, 3, "2026-10-05T00:00:00Z", {"ok": True})]
        self.executed = None

    def execute(self, query, params):
        self.executed = (query, params)

    def fetchall(self):
        return self.rows


class TestPrintModule(unittest.TestCase):
    def test_print_module_exports(self):
        self.assertTrue(callable(extract_printers_from_telemetry))
        self.assertTrue(callable(enrich_print_logs))

    def test_recuperation_json_brut_filters_by_device_and_day(self):
        cursor = DummyCursor()

        rows = recuperation_json_brut(cursor, 42, "2026-10-05")

        self.assertEqual(rows, cursor.rows)
        self.assertIsNotNone(cursor.executed)
        query, params = cursor.executed
        self.assertIn("WHERE id_device = %s", query)
        self.assertIn("DATE(report_time)", query)
        self.assertEqual(params, (42, "2026-10-05"))

    def test_resolve_historic_date_uses_raw_json_report_time(self):
        fallback = "2026-10-10T08:00:00Z"
        rows = [
            (2, 42, 9, "2026-10-05T12:00:00Z", {"reportTime": "2026-10-05T12:00:00Z"}),
            (1, 42, 9, "2026-10-05T11:15:00Z", {"reportTime": "2026-10-05T11:15:00Z"}),
        ]

        result = _resolve_historic_date(rows, fallback)

        self.assertEqual(result.isoformat(), "2026-10-05T12:00:00+00:00")

    def test_should_skip_historical_insert_when_row_already_exists(self):
        class ExistingCursor:
            def execute(self, query, params):
                self.query = query
                self.params = params

            def fetchone(self):
                return (1,)

        cursor = ExistingCursor()
        past_date = "2026-10-05T12:00:00+00:00"

        self.assertTrue(_should_skip_historical_insert(cursor, "t_device_ram", 42, past_date))

if __name__ == "__main__":
    unittest.main()
