import re
from typing import Optional
from backend.graph.state import ResearchState
from backend.llm.client import LLMClient
from backend.llm.prompts import REVIEWER_PROMPT

def reviewer_node(state: ResearchState) -> dict:
    """
    Reviewer node that evaluates the written report and assigns a quality score.

    Args:
        state (ResearchState): The current state of the research workflow.

    Returns:
        dict: A dictionary containing the updated 'review_feedback' and 'quality_score' keys.
    """
    report = state.get("report", "")

    reviewer = ReportReviewer()
    review_feedback, quality_score = reviewer.review(report)

    return {
        "review_feedback": review_feedback,
        "quality_score": quality_score
    }

class ReportReviewer:
    """
    ReportReviewer component responsible for evaluating report quality.
    Can be replaced or extended with a real LLM review and extraction service.
    """
    def __init__(self, client: Optional[LLMClient] = None):
        self.client = client or LLMClient()

    def review(self, report: str) -> tuple[str, float]:
        """
        Review the report content. Returns a tuple of (feedback, quality_score).

        Args:
            report: The written markdown report to evaluate.

        Returns:
            tuple[str, float]: The evaluation feedback and numeric quality score (0-10).
        """
        prompt = REVIEWER_PROMPT.format(report=report)
        response = self.client.generate(prompt=prompt, system_instruction="Reviewing constraint")

        # Clean up any potential markdown code block backticks from LLM output
        cleaned_response = response.strip()
        if cleaned_response.startswith("```"):
            cleaned_response = re.sub(r"^```(?:json)?\n", "", cleaned_response)
            cleaned_response = re.sub(r"\n```$", "", cleaned_response)
            cleaned_response = cleaned_response.strip()

        try:
            import json
            data = json.loads(cleaned_response)
            review_feedback = data.get("review_feedback", response)
            quality_score = float(data.get("quality_score", 0.0))
            return review_feedback, quality_score
        except Exception:
            # Fallback to legacy regex parsing if JSON parsing fails
            score_match = re.search(r"Score:\s*([0-9.]+)", response, re.IGNORECASE)
            quality_score = 0.0
            if score_match:
                try:
                    quality_score = float(score_match.group(1))
                except ValueError:
                    pass
            return response, quality_score
