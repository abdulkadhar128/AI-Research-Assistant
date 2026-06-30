from backend.graph.state import ResearchState
from backend.llm.client import LLMClient
from backend.search.search_client import SearchProvider
from backend.search.citation_formatter import CitationFormatter

def search_node(state: ResearchState) -> dict:
    """
    Search node that retrieves web search results using the raw query,
    enabling parallel planning and search execution.
    """
    query = state.get("query", "")
    
    import time
    # Bypass query generation LLM to run in parallel and save ~2 seconds.
    provider = SearchProvider()
    results = provider.search(query)
    
    search_context = CitationFormatter.format_search_results_for_context(results)
    citations = CitationFormatter.format_citations(results)
    
    return {
        "search_results": search_context,
        "citations": citations,
        "search_finish_time": time.time()
    }
