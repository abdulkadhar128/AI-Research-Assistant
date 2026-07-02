"""
Legacy Fact-Checker node — superseded by the Verification Agent.

Kept as a stub to prevent ImportError. All logic has moved to:
  - backend.graph.nodes.verify  (deterministic dedup + quality filtering)
"""

import logging
from backend.graph.state import ResearchState

logger = logging.getLogger(__name__)


def fact_checker_node(state: ResearchState) -> dict:
    """No-op stub. Returns state unchanged."""
    logger.warning(
        "fact_checker_node called but is deprecated. Use verify_node instead."
    )
    return {}
