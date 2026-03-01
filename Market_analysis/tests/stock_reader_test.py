import unittest
from unittest.mock import patch

from src.tools import stock_reader


class TestStockReader(unittest.TestCase):
    def test_pct_change_returns_none_for_invalid_inputs(self) -> None:
        self.assertIsNone(stock_reader._pct_change(100.0, 0.0))
        self.assertIsNone(stock_reader._pct_change(100.0, None))
        self.assertIsNone(stock_reader._pct_change(None, 50.0))

    def test_pct_change_computes_expected_value(self) -> None:
        self.assertAlmostEqual(stock_reader._pct_change(120.0, 100.0), 20.0)

    def test_nearest_prior_close_skips_none_and_nan(self) -> None:
        timestamps = [100, 200, 300, 400]
        closes = [10.0, None, float("nan"), 20.0]

        self.assertEqual(stock_reader._nearest_prior_close(timestamps, closes, 350), 10.0)

    def test_nearest_prior_close_returns_none_when_no_valid_value(self) -> None:
        timestamps = [100, 200]
        closes = [None, float("nan")]

        self.assertIsNone(stock_reader._nearest_prior_close(timestamps, closes, 200))

    def test_get_stock_value_uses_meta_price_and_computes_changes(self) -> None:
        day = 24 * 3600
        start = 1_700_000_000
        timestamps = [
            start,
            start + 31 * day,
            start + 62 * day,
            start + 93 * day,
            start + 124 * day,
            start + 155 * day,
            start + 186 * day,
        ]
        closes = [100.0, 110.0, 120.0, 130.0, 140.0, 150.0, 160.0]

        fake_result = {
            "meta": {"currency": "USD", "regularMarketPrice": 200.0},
            "timestamp": timestamps,
            "indicators": {"quote": [{"close": closes}]},
        }

        with patch.object(stock_reader, "_fetch_yahoo_chart", return_value=fake_result), patch.object(
            stock_reader, "_utc_now_iso", return_value="2026-03-01T00:00:00Z"
        ):
            output = stock_reader.get_stock_value.invoke({"symbol": "AAPL"})

        self.assertEqual(output.symbol, "AAPL")
        self.assertEqual(output.currency, "USD")
        self.assertEqual(output.as_of, "2026-03-01T00:00:00Z")
        self.assertEqual(output.value, 200.0)
        self.assertEqual(output.source, "yahoo_finance_chart_v8")

        self.assertEqual(output.changes_pct["1m"], round((200.0 / 150.0 - 1.0) * 100.0, 4))
        self.assertEqual(output.changes_pct["3m"], round((200.0 / 130.0 - 1.0) * 100.0, 4))
        self.assertEqual(output.changes_pct["6m"], round((200.0 / 100.0 - 1.0) * 100.0, 4))

    def test_get_stock_value_falls_back_to_last_valid_close_when_meta_price_missing(self) -> None:
        fake_result = {
            "meta": {"currency": "USD", "regularMarketPrice": None},
            "timestamp": [1, 2, 3],
            "indicators": {"quote": [{"close": [None, float("nan"), 99.5]}]},
        }

        with patch.object(stock_reader, "_fetch_yahoo_chart", return_value=fake_result), patch.object(
            stock_reader, "_utc_now_iso", return_value="2026-03-01T00:00:00Z"
        ):
            output = stock_reader.get_stock_value.invoke({"symbol": "MSFT"})

        self.assertEqual(output.value, 99.5)

    def test_get_stock_value_raises_for_empty_symbol(self) -> None:
        with self.assertRaisesRegex(ValueError, "symbol must be non-empty"):
            stock_reader.get_stock_value.invoke({"symbol": "   "})

    def test_get_stock_value_raises_for_missing_price_series(self) -> None:
        fake_result = {
            "meta": {},
            "timestamp": [],
            "indicators": {"quote": [{"close": []}]},
        }

        with patch.object(stock_reader, "_fetch_yahoo_chart", return_value=fake_result):
            with self.assertRaisesRegex(ValueError, "Missing price series"):
                stock_reader.get_stock_value.invoke({"symbol": "AAPL"})


if __name__ == "__main__":
    unittest.main()
