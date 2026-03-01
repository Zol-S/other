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

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; AgentTool/1.0; +https://example.com/bot)",
    "Accept": "application/rss+xml,application/xml;q=0.9,*/*;q=0.8",
}

@dataclass
class NewsItem:
    title: str
    url: str
    publisher: str
    published: Optional[str]
    summary: str
    source: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "url": self.url,
            "publisher": self.publisher,
            "published": self.published,
            "summary": self.summary,
            "source": self.source,
        }

def _utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def _parse_rfc2822_to_iso(s: str) -> Optional[str]:
    """
    RSS pubDate is often RFC 2822 (e.g., 'Fri, 16 Feb 2026 14:22:00 GMT').
    """
    if not s:
        return None
    s = s.strip()
    # dt.email.utils parsedate_to_datetime is clean, but keep deps minimal:
    try:
        from email.utils import parsedate_to_datetime

        d = parsedate_to_datetime(s)
        if d.tzinfo is None:
            d = d.replace(tzinfo=dt.timezone.utc)
        return d.astimezone(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    except Exception:
        return None


def _strip_html(text: str) -> str:
    if not text:
        return ""
    text = html.unescape(text)
    # remove tags
    text = re.sub(r"<[^>]+>", " ", text)
    # normalize whitespace
    return re.sub(r"\s+", " ", text).strip()


def _safe_text(elem: Optional[ET.Element]) -> str:
    if elem is None or elem.text is None:
        return ""
    return elem.text.strip()


class StockNewsReader:
    def __init__(
        self,
        session: Optional[requests.Session] = None,
        timeout_s: int = 20,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        self.session = session or requests.Session()
        self.timeout_s = timeout_s
        self.headers = headers or DEFAULT_HEADERS.copy()

    # ---------- Public API ----------

    def fetch_news(
        self,
        ticker: Optional[str] = None,
        company: Optional[str] = None,
        limit: int = 20,
        include_google: bool = True,
        include_yahoo: bool = True,
    ) -> Dict[str, Any]:
        """
        Fetch news items from enabled sources, dedupe by URL, and return newest-first where possible.
        """
        if not ticker and not company:
            raise ValueError("Provide at least one of: ticker='AAPL' or company='Apple'")

        items: List[NewsItem] = []

        if include_yahoo and ticker:
            items.extend(self._fetch_yahoo_rss(ticker=ticker, limit=limit))

        if include_google:
            # If company not provided, use ticker as query; if both exist, combine.
            query = self._build_google_query(ticker=ticker, company=company)
            items.extend(self._fetch_google_news_rss(query=query, limit=limit))

        # Dedupe by URL (keep first occurrence)
        seen = set()
        deduped: List[NewsItem] = []
        for it in items:
            if not it.url or it.url in seen:
                continue
            seen.add(it.url)
            deduped.append(it)

        # Sort: newest first when published is parseable; otherwise stable
        def sort_key(it: NewsItem):
            if not it.published:
                return (0, "")  # older bucket
            return (1, it.published)

        deduped.sort(key=sort_key, reverse=True)
        deduped = deduped[:limit]

        return {
            "query": company or ticker or "",
            "as_of": _utc_now_iso(),
            "items": [it.to_dict() for it in deduped],
        }

    # ---------- Yahoo Finance RSS ----------

    def _fetch_yahoo_rss(self, ticker: str, limit: int) -> List[NewsItem]:
        # Example:
        # https://feeds.finance.yahoo.com/rss/2.0/headline?s=AAPL&region=US&lang=en-US
        url = (
            "https://feeds.finance.yahoo.com/rss/2.0/headline"
            f"?s={quote_plus(ticker.strip())}&region=US&lang=en-US"
        )
        xml = self._get_text(url)
        return self._parse_rss_items(xml, source="yahoo_rss", default_publisher="Yahoo Finance", limit=limit)

    # ---------- Google News RSS ----------

    def _build_google_query(self, ticker: Optional[str], company: Optional[str]) -> str:
        parts = []
        if company:
            parts.append(company.strip())
        if ticker and (not company or ticker.strip().lower() not in company.strip().lower()):
            parts.append(ticker.strip())
        # Make it more finance-relevant without overconstraining:
        parts.append("stock OR shares OR earnings OR revenue OR guidance")
        return " ".join(parts)

    def _fetch_google_news_rss(self, query: str, limit: int) -> List[NewsItem]:
        # Example:
        # https://news.google.com/rss/search?q=Apple%20stock&hl=en-US&gl=US&ceid=US:en
        q = quote_plus(query.strip())
        url = f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"
        xml = self._get_text(url)
        # Google often includes source in <source> under item; we’ll parse it.
        return self._parse_rss_items(xml, source="google_news_rss", default_publisher="Google News", limit=limit)

    # ---------- HTTP + RSS parsing ----------

    def _get_text(self, url: str) -> str:
        resp = self.session.get(url, headers=self.headers, timeout=self.timeout_s)
        resp.raise_for_status()
        return resp.text

    def _parse_rss_items(
        self,
        xml_text: str,
        source: str,
        default_publisher: str,
        limit: int,
    ) -> List[NewsItem]:
        """
        Parses RSS 2.0 feeds. Works for both Yahoo Finance RSS and Google News RSS.
        """
        root = ET.fromstring(xml_text)
        channel = root.find("channel")
        if channel is None:
            return []

        out: List[NewsItem] = []
        for item in channel.findall("item"):
            title = _safe_text(item.find("title"))
            link = _safe_text(item.find("link"))

            pub = _parse_rfc2822_to_iso(_safe_text(item.find("pubDate")))

            # Prefer <source> for Google News RSS if present
            src_elem = item.find("source")
            publisher = _safe_text(src_elem) if src_elem is not None else default_publisher
            publisher = publisher or default_publisher

            desc = _safe_text(item.find("description"))
            summary = _strip_html(desc)

            if not title and not link:
                continue

            out.append(
                NewsItem(
                    title=title or "",
                    url=link or "",
                    publisher=publisher,
                    published=pub,
                    summary=summary,
                    source=source,
                )
            )

            if len(out) >= limit:
                break

        return out

@tool
def fetch_stock_news(
    ticker: Optional[str] = None,
    company: Optional[str] = None,
    limit: int = 20,
    include_google: bool = True,
    include_yahoo: bool = True,
) -> Dict[str, Any]:
    """
    A thin wrapper to expose StockNewsReader as a single tool function.
    """
    reader = StockNewsReader()

    return reader.fetch_news(
        ticker=ticker,
        company=company,
        limit=limit,
        include_google=include_google,
        include_yahoo=include_yahoo,
    )