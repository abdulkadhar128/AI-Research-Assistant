from typing import List
from backend.search.search_models import SearchResult

class CitationFormatter:
    """
    Helper class to format SearchResult lists into string representations
    for the LLM prompt and final citation references.
    """
    
    @staticmethod
    def format_citations(results: List[SearchResult]) -> str:
        """
        Format list of results into a numbered bibliography. Limit to top 3 sources.
        """
        citations = []
        for i, res in enumerate(results[:3], 1):
            citations.append(f"[{i}] {res.title}\n{res.url}")
        return "\n\n".join(citations)

    @staticmethod
    def format_search_results_for_context(results: List[SearchResult]) -> str:
        """
        Format list of results into detailed contextual text blocks.
        Limit to top 3 sources and truncate snippet to max 500 characters.
        """
        lines = []
        for i, res in enumerate(results[:3], 1):
            snippet = res.snippet or ""
            if len(snippet) > 500:
                snippet = snippet[:500] + "..."
            lines.append(f"Source [{i}] ({res.source_domain}): {res.title}\nURL: {res.url}\nContent: {snippet}")
        return "\n\n".join(lines)
