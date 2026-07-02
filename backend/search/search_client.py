"""
Search provider with LangChain Community TavilySearchResults as the primary backend.

Falls back to Serper (direct HTTP) and DuckDuckGo mock results when Tavily is
not configured or unavailable, preserving 100% offline test-ability.
"""

import os
import json
import urllib.parse
import logging
from typing import List

import httpx
from backend.search.search_models import SearchResult

logger = logging.getLogger(__name__)


class SearchProvider:
    """
    Unified search provider abstraction.

    Priority order:
      1. Tavily  via langchain_community.tools.TavilySearchResults  (preferred)
      2. Serper  via direct HTTP call
      3. DuckDuckGo mock results (offline / CI fallback)
    """

    def __init__(self) -> None:
        self.tavily_key = os.getenv("TAVILY_API_KEY", "")
        self.serper_key = os.getenv("SERPER_API_KEY", "")

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def search(self, query: str, max_results: int = 3) -> List[SearchResult]:
        """
        Execute a search and return a list of SearchResult objects.

        Results are cached in CacheService to avoid redundant API calls on
        repeated workflow invocations with the same query.
        """
        from backend.services.cache_service import CacheService
        from backend.llm.config import LLMConfig

        cache_key = f"{query}|||{max_results}"
        cached = CacheService.get("search", cache_key)
        if cached:
            try:
                return [SearchResult(**item) for item in json.loads(cached)]
            except Exception:
                pass

        # Always use mock results in mock mode to avoid network calls
        if LLMConfig.PROVIDER == "mock":
            results = self._search_mock(query, max_results)
        else:
            results = self._search_with_fallbacks(query, max_results)

        # Persist to cache
        try:
            CacheService.set("search", cache_key, json.dumps([r.__dict__ for r in results]))
        except Exception:
            pass

        return results

    # ------------------------------------------------------------------
    # Provider implementations
    # ------------------------------------------------------------------

    def _search_with_fallbacks(self, query: str, max_results: int) -> List[SearchResult]:
        """Try each provider in priority order, returning the first success."""
        # 1. Tavily via LangChain Community
        if self.tavily_key:
            try:
                return self._search_tavily_lc(query, max_results)
            except Exception as exc:
                logger.warning("Tavily (LangChain) search failed: %s — trying fallback.", exc)

        # 2. Serper via direct HTTP
        if self.serper_key:
            try:
                return self._search_serper(query, max_results)
            except Exception as exc:
                logger.warning("Serper search failed: %s — using mock fallback.", exc)

        # 3. DuckDuckGo mock
        return self._search_mock(query, max_results)

    def _search_tavily_lc(self, query: str, max_results: int) -> List[SearchResult]:
        """
        Use langchain_community TavilySearchResults for structured web search.

        Returns rich results with title, URL, and content snippet.
        """
        from langchain_community.tools.tavily_search import TavilySearchResults

        tool = TavilySearchResults(
            max_results=max_results,
            tavily_api_key=self.tavily_key,
            include_answer=False,
            include_raw_content=False,
        )
        raw: list = tool.invoke({"query": query})

        results = []
        for item in raw:
            url    = item.get("url", "")
            title  = item.get("title") or url  # title may be absent
            domain = urllib.parse.urlparse(url).netloc
            results.append(SearchResult(
                title=title,
                url=url,
                snippet=item.get("content", ""),
                source_domain=domain,
            ))
        logger.info("Tavily (LangChain): retrieved %d results for '%s'.", len(results), query)
        return results

    def _search_serper(self, query: str, max_results: int) -> List[SearchResult]:
        """Serper.dev Google search fallback (direct HTTP)."""
        headers = {
            "X-API-KEY": self.serper_key,
            "Content-Type": "application/json",
        }
        res = httpx.post(
            "https://google.serper.dev/search",
            json={"q": query},
            headers=headers,
            timeout=10.0,
        )
        res.raise_for_status()
        data = res.json()

        results = []
        for item in data.get("organic", [])[:max_results]:
            url    = item.get("link", "")
            domain = urllib.parse.urlparse(url).netloc
            results.append(SearchResult(
                title=item.get("title", "No Title"),
                url=url,
                snippet=item.get("snippet", ""),
                source_domain=domain,
            ))
        return results

    def _search_mock(self, query: str, max_results: int) -> List[SearchResult]:
        """
        Deterministic offline mock results — used in mock mode and CI.
        Returns realistic-looking placeholder data so the full pipeline completes.
        """
        domain_list = ["wikipedia.org", "arxiv.org", "github.com", "medium.com", "techcrunch.com"]
        results = []
        for i in range(1, max_results + 1):
            domain = domain_list[i % len(domain_list)]
            url = f"https://www.{domain}/wiki/{urllib.parse.quote(query.replace(' ', '_'))}"
            results.append(SearchResult(
                title=f"Source {i}: Comprehensive overview of '{query}'",
                url=url,
                snippet=(
                    f"This source covers key trends, definitions, historical background, and "
                    f"state-of-the-art developments for '{query}'. Includes architectural details "
                    f"and real-world implementation examples from industry practitioners."
                ),
                source_domain=domain,
            ))
        return results
