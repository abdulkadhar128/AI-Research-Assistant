from typing import List, Dict, Any
from backend.search.search_models import SearchResult


class CitationFormatter:
    """
    Helper class to format SearchResult lists into string representations
    for the LLM prompt and final citation references.
    """

    @staticmethod
    def build_bibliography(sources: List[Dict[str, Any]]) -> str:
        """
        Build a numbered bibliography string from verified source dicts.
        Format: [N] Title — URL
        (Snippet is included as a context hint to help the Writer LLM
        write accurate inline citations, but is stripped from the final DB entry.)

        This is the canonical citation builder — always called after verification
        so only real, confirmed URLs appear in the bibliography.
        """
        lines = []
        for i, src in enumerate(sources, 1):
            title   = src.get("title", "Untitled").strip()
            url     = src.get("url", "").strip()
            snippet = src.get("snippet", "").strip()
            if len(snippet) > 200:
                snippet = snippet[:200] + "..."
            lines.append(f"[{i}] {title} — {url}\n    {snippet}")
        return "\n\n".join(lines)

    @staticmethod
    def build_bibliography_compact(sources: List[Dict[str, Any]]) -> str:
        """
        Compact version (no snippets) for storage in the database and display in the UI.
        Format: [N] Title — URL
        """
        lines = []
        for i, src in enumerate(sources, 1):
            title = src.get("title", "Untitled").strip()
            url   = src.get("url", "").strip()
            lines.append(f"[{i}] {title} — {url}")
        return "\n".join(lines)

    @staticmethod
    def format_search_results_for_context(results: List[SearchResult]) -> str:
        """
        Format list of results into detailed contextual text blocks.
        Limit to top 5 sources and truncate snippet to max 500 characters.
        """
        lines = []
        for i, res in enumerate(results[:5], 1):
            snippet = res.snippet or ""
            if len(snippet) > 500:
                snippet = snippet[:500] + "..."
            lines.append(
                f"Source [{i}] ({res.source_domain}): {res.title}\n"
                f"URL: {res.url}\n"
                f"Content: {snippet}"
            )
        return "\n\n".join(lines)

