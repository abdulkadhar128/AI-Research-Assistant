from typing import TypedDict, List, Dict, Any, Optional


class ResearchState(TypedDict, total=False):
    """
    Represents the shared state of the research assistant workflow.
    All fields are optional (total=False) to allow nodes to return partial updates.
    """
    # Input
    topic: str

    # Intent analysis
    confidence: float
    clarification_needed: bool
    clarification_prompt: str
    interpretations: List[str]

    # Planner
    plan: str

    # Search
    sources: List[Dict[str, Any]]

    # Verify
    verified_sources: List[Dict[str, Any]]

    # Writer
    report: str
    revision_count: int

    # Reviewer
    score: float
    feedback: str
    accuracy_score: float
    coverage_score: float
    clarity_score: float
    citations_score: float

    # Citations / bibliography
    citations: str              # compact [N] Title — URL (stored in DB, shown in UI)
    citations_for_writer: str   # rich version with snippets (passed to Writer LLM only)

    # Timing
    generation_time: float
