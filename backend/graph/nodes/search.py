"""
Search Agent node.

Retrieves web search results using SearchProvider (LangChain Tavily backend)
and stores them as a structured list of dicts in state.sources.
No LLM is called here — search is a pure tool invocation step.
Citations are NOT built here — that happens in verify_node after filtering,
so only real, verified source URLs end up in the bibliography.
"""

from backend.graph.state import ResearchState
from backend.search.search_client import SearchProvider


def search_node(state: ResearchState) -> dict:
    """
    Execute a web search for the research topic.

    Routes to:
      1. TavilySearchResults (langchain-community) — when TAVILY_API_KEY is set
      2. Serper              (direct HTTP)          — when SERPER_API_KEY is set
      3. Deterministic mock results                 — offline / mock mode
    """
    topic = state.get("topic", "")
    print(f"\n{'='*60}")
    print(f"[SEARCH] TOPIC: {topic!r}")
    print(f"{'='*60}")

    if not topic:
        print("[SEARCH] WARNING: topic is empty! Search will return mock results.")

    provider = SearchProvider()
    results  = provider.search(topic)

    print(f"[SEARCH] Retrieved {len(results)} results for topic: {topic!r}")
    for i, r in enumerate(results, 1):
        print(f"  [{i}] {r.title[:60]!r} — {r.url[:70]}")

    # Build structured source dicts for the Verification node.
    # NOTE: citations field is intentionally NOT set here.
    # verify_node will build citations from only the verified subset of these sources.
    sources = [
        {
            "title":         r.title,
            "url":           r.url,
            "snippet":       r.snippet,
            "source_domain": r.source_domain,
        }
        for r in results
    ]

    return {"sources": sources}

