import unittest
from unittest.mock import patch

from src.tools.news_reader import (
    NewsItem,
    StockNewsReader,
    _parse_rfc2822_to_iso,
    _strip_html,
)


class TestNewsReader(unittest.TestCase):
    def test_parse_rfc2822_to_iso_returns_utc_iso(self) -> None:
        self.assertEqual(
            _parse_rfc2822_to_iso("Fri, 16 Feb 2026 14:22:00 GMT"),
            "2026-02-16T14:22:00Z",
        )

    def test_parse_rfc2822_to_iso_returns_none_for_invalid_input(self) -> None:
        self.assertIsNone(_parse_rfc2822_to_iso("not a date"))

    def test_strip_html_unescapes_and_normalizes_whitespace(self) -> None:
        text = "<p>Hello&nbsp;<b>World</b></p>\n<div> Earnings &amp; revenue </div>"
        self.assertEqual(_strip_html(text), "Hello World Earnings & revenue")

    def test_build_google_query_avoids_duplicate_ticker_in_company(self) -> None:
        reader = StockNewsReader()
        query = reader._build_google_query(ticker="AAPL", company="Apple AAPL")
        self.assertTrue(query.startswith("Apple AAPL"))
        self.assertNotIn("AAPL AAPL", query)

    def test_fetch_news_requires_ticker_or_company(self) -> None:
        reader = StockNewsReader()
        with self.assertRaisesRegex(ValueError, "Provide at least one"):
            reader.fetch_news()

    def test_fetch_news_dedupes_sorts_and_limits(self) -> None:
        reader = StockNewsReader()

        yahoo_items = [
            NewsItem(
                title="Old Yahoo",
                url="https://example.com/1",
                publisher="Yahoo",
                published="2026-02-01T00:00:00Z",
                summary="old",
                source="yahoo_rss",
            ),
            NewsItem(
                title="Duplicate URL",
                url="https://example.com/dup",
                publisher="Yahoo",
                published="2026-02-02T00:00:00Z",
                summary="dup",
                source="yahoo_rss",
            ),
        ]
        google_items = [
            NewsItem(
                title="New Google",
                url="https://example.com/2",
                publisher="Google",
                published="2026-02-03T00:00:00Z",
                summary="new",
                source="google_news_rss",
            ),
            NewsItem(
                title="Duplicate URL Again",
                url="https://example.com/dup",
                publisher="Google",
                published="2026-02-04T00:00:00Z",
                summary="dup2",
                source="google_news_rss",
            ),
            NewsItem(
                title="No Published",
                url="https://example.com/3",
                publisher="Google",
                published=None,
                summary="nopub",
                source="google_news_rss",
            ),
        ]

        with patch.object(reader, "_fetch_yahoo_rss", return_value=yahoo_items), patch.object(
            reader, "_fetch_google_news_rss", return_value=google_items
        ), patch("src.tools.news_reader._utc_now_iso", return_value="2026-03-01T00:00:00Z"):
            result = reader.fetch_news(ticker="AAPL", company="Apple", limit=3)

        self.assertEqual(result["query"], "Apple")
        self.assertEqual(result["as_of"], "2026-03-01T00:00:00Z")

        items = result["items"]
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0]["url"], "https://example.com/2")
        self.assertEqual(items[1]["url"], "https://example.com/dup")
        self.assertEqual(items[2]["url"], "https://example.com/1")

    def test_parse_rss_items_extracts_fields_and_strips_description_html(self) -> None:
        xml = """
        <rss>
          <channel>
            <item>
              <title>Headline</title>
              <link>https://news.example.com/a</link>
              <pubDate>Fri, 16 Feb 2026 14:22:00 GMT</pubDate>
              <source>Reuters</source>
              <description><![CDATA[<p>Strong <b>earnings</b> reported</p>]]></description>
            </item>
          </channel>
        </rss>
        """

        reader = StockNewsReader()
        items = reader._parse_rss_items(xml, source="google_news_rss", default_publisher="Google News", limit=10)

        self.assertEqual(len(items), 1)
        item = items[0]
        self.assertEqual(item.title, "Headline")
        self.assertEqual(item.url, "https://news.example.com/a")
        self.assertEqual(item.publisher, "Reuters")
        self.assertEqual(item.published, "2026-02-16T14:22:00Z")
        self.assertEqual(item.summary, "Strong earnings reported")
        self.assertEqual(item.source, "google_news_rss")


if __name__ == "__main__":
    unittest.main()
