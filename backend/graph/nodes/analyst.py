"""
Legacy Analyst node — superseded by the Writer Agent.

Analysis and SWOT evaluation are now integrated directly into the Writer's
system prompt (see backend.llm.prompts.WRITER_TEMPLATE → ## Analysis section).
Kept as a stub to prevent ImportError.
"""

import logging
from backend.graph.state import ResearchState

logger = logging.getLogger(__name__)


def analyst_node(state: ResearchState) -> dict:
    """No-op stub. Returns state unchanged."""
    logger.warning(
        "analyst_node called but is deprecated. "
        "Analysis is now integrated into writer_node."
    )
    return {}
