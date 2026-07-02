"""
Legacy Researcher node — superseded by the Search + Verify + Writer pipeline.

This module is kept as a stub to prevent ImportError if any external code
still references it. All logic has been moved to:
  - backend.graph.nodes.search   (web search via LangChain Tavily)
  - backend.graph.nodes.verify   (deduplication + quality filtering)
  - backend.graph.nodes.writer   (report synthesis)
"""

import logging
from backend.graph.state import ResearchState

logger = logging.getLogger(__name__)


def researcher_node(state: ResearchState) -> dict:
    """No-op stub. Returns state unchanged."""
    logger.warning(
        "researcher_node called but is deprecated. "
        "Use search_node + verify_node + writer_node instead."
    )
    return {}
