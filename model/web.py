from __future__ import annotations

import html
import re
from dataclasses import dataclass
from urllib.parse import unquote

import requests


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str


class WebSearch:

    def __init__(self):
        self.search_url = "https://html.duckduckgo.com/html/"

        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            )
        }

        self.timeout = 10

    @staticmethod
    def _clean_text(text: str) -> str:
        text = html.unescape(text)

        text = re.sub(
            r"<[^>]+>",
            "",
            text
        )

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    @staticmethod
    def _decode_url(url: str) -> str:
        url = html.unescape(url)

        if "uddg=" in url:
            match = re.search(
                r"[?&]uddg=([^&]+)",
                url
            )

            if match:
                return unquote(
                    match.group(1)
                )

        return url

    def search(
        self,
        query: str,
        max_results: int = 5,
    ) -> list[SearchResult]:

        query = query.strip()

        if not query:
            return []

        try:
            response = requests.get(
                self.search_url,
                params={
                    "q": query
                },
                headers=self.headers,
                timeout=self.timeout,
            )

            response.raise_for_status()

        except requests.RequestException:
            return []

        page = response.text

        results: list[SearchResult] = []

        result_blocks = re.findall(
            r'<div[^>]+class="[^"]*\bresult\b[^"]*"[^>]*>'
            r'.*?'
            r'</div>\s*</div>',
            page,
            re.IGNORECASE | re.DOTALL,
        )

        for block in result_blocks:

            if len(results) >= max_results:
                break

            title_match = re.search(
                r'<a[^>]+class="[^"]*result__a[^"]*"'
                r'[^>]+href="([^"]+)"[^>]*>'
                r'(.*?)'
                r'</a>',
                block,
                re.IGNORECASE | re.DOTALL,
            )

            if not title_match:
                continue

            url = self._decode_url(
                title_match.group(1)
            )

            title = self._clean_text(
                title_match.group(2)
            )

            snippet_match = re.search(
                r'class="[^"]*result__snippet[^"]*"'
                r'[^>]*>'
                r'(.*?)'
                r'</(?:a|div|span)>',
                block,
                re.IGNORECASE | re.DOTALL,
            )

            if snippet_match:
                snippet = self._clean_text(
                    snippet_match.group(1)
                )
            else:
                snippet = ""

            if not title:
                continue

            results.append(
                SearchResult(
                    title=title,
                    url=url,
                    snippet=snippet,
                )
            )

        return results

    def search_text(
        self,
        query: str,
        max_results: int = 5,
    ) -> str:

        results = self.search(
            query,
            max_results
        )

        if not results:
            return (
                f"I couldn't find any web results "
                f"for '{query}'."
            )

        lines: list[str] = []

        for index, result in enumerate(
            results,
            start=1
        ):

            lines.append(
                f"{index}. {result.title}"
            )

            if result.snippet:
                lines.append(
                    f"   {result.snippet}"
                )

            lines.append(
                f"   {result.url}"
            )

        return "\n".join(lines)


web_search = WebSearch()


def search_web(
    query: str,
    max_results: int = 5,
) -> list[SearchResult]:

    return web_search.search(
        query,
        max_results
    )


def search_web_text(
    query: str,
    max_results: int = 5,
) -> str:

    return web_search.search_text(
        query,
        max_results
    )