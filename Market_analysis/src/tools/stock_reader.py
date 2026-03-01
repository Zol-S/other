from __future__ import annotations

import re
import html
import math

import requests
import datetime as dt

from dataclasses import dataclass

from urllib.parse import quote_plus
import xml.etree.ElementTree as ET

from typing import Any, Dict, List, Optional

from langchain.tools import tool


_YAHOO_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
_DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; AgentTool/1.0; +https://example.com/bot)",
    "Accept": "application/json,text/plain,*/*",
}

@dataclass
class Stock:
    symbol: str
    currency: Optional[str]
    as_of: str
    value: float
    changes_pct: Dict[str, Optional[float]]
    source: str

def _utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _pct_change(current: float, past: float) -> Optional[float]:
    if past is None or past == 0 or current is None:
        return None
    return (current / past - 1.0) * 100.0


def _nearest_prior_close(timestamps: list[int], closes: list[Optional[float]], target_ts: int) -> Optional[float]:
    """
    Find the close price at or before target_ts.
    We walk from the end for speed (timestamps are ascending).
    """
    for i in range(len(timestamps) - 1, -1, -1):
        if timestamps[i] <= target_ts:
            c = closes[i]
            if c is not None and not (isinstance(c, float) and math.isnan(c)):
                return float(c)
    return None


def _fetch_yahoo_chart(symbol: str, session: Optional[requests.Session] = None) -> Dict[str, Any]:
    """
    Fetch up to 1y daily data so we can compute 1/3/6 month changes.
    """
    s = session or requests.Session()
    url = _YAHOO_CHART_URL.format(symbol=symbol)
    params = {
        "range": "1y",
        "interval": "1d",
        "includePrePost": "false",
        "events": "div,splits",
    }
    resp = s.get(url, params=params, headers=_DEFAULT_HEADERS, timeout=20)
    resp.raise_for_status()
    data = resp.json()

    # Basic validation
    chart = data.get("chart", {})
    if chart.get("error"):
        raise ValueError(f"Yahoo chart error for {symbol}: {chart['error']}")
    result = (chart.get("result") or [None])[0]
    if not result:
        raise ValueError(f"No chart result for {symbol}")

    return result

@tool
def get_stock_value(symbol: str) -> str:
    """
    Reads the current stock price for the given symbol and computes percentage changes over 1m/3m/6m lookbacks.
    """
    symbol = symbol.strip()
    if not symbol:
        raise ValueError("symbol must be non-empty, e.g. 'AAPL' or 'MSFT' or 'BTC-USD'")

    result = _fetch_yahoo_chart(symbol)
    meta = result.get("meta", {}) or {}

    timestamps = result.get("timestamp") or []
    indicators = (result.get("indicators") or {}).get("quote") or []
    quote0 = indicators[0] if indicators else {}
    closes = quote0.get("close") or []

    if not timestamps or not closes:
        raise ValueError(f"Missing price series for {symbol}")

    # Current value: prefer meta regularMarketPrice; fallback to last non-null close
    current_value = meta.get("regularMarketPrice")
    if current_value is None:
        # last valid close
        current_value = next((float(c) for c in reversed(closes) if c is not None and not (isinstance(c, float) and math.isnan(c))), None)
    if current_value is None:
        raise ValueError(f"Could not determine current value for {symbol}")

    # Approximate trading-day lookbacks
    lookbacks = {
        "1m": 21,
        "3m": 63,
        "6m": 126
    }

    # Use timestamps to find a price near the lookback date (calendar-based), not index-based,
    # because holidays / missing days can shift counts.
    # We compute target_ts by subtracting N calendar days that roughly correspond to the trading-day window.
    # (This is intentionally simple and robust.)
    calendar_day_map = {
        "1m": 31,
        "3m": 93,
        "6m": 186,
    }

    latest_ts = int(timestamps[-1])
    changes: Dict[str, Optional[float]] = {}

    for k in ("1m", "3m", "6m"):
        target_ts = latest_ts - calendar_day_map[k] * 24 * 3600
        past_close = _nearest_prior_close(timestamps, closes, target_ts)
        changes[k] = None if past_close is None else round(_pct_change(float(current_value), float(past_close)), 4)

    return Stock(
        symbol=symbol,
        currency=meta.get("currency"),
        as_of=_utc_now_iso(),
        value=float(current_value),
        changes_pct=changes,
        source="yahoo_finance_chart_v8",
    )