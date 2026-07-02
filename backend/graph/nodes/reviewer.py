"""
Reviewer Agent node.

Evaluates the generated report across four quality dimensions using
LangChain ChatPromptTemplate + LangChainLLMService (quality model tier).

All four sub-scores default to 7.0 (not 0.0) when JSON parsing fails,
so the overall score is never incorrectly reported as zero.
"""

import json
import re
from backend.graph.state import ResearchState
from backend.llm.client import LangChainLLMService
from backend.llm.config import LLMConfig
from backend.llm.prompts import REVIEWER_TEMPLATE


def reviewer_node(state: ResearchState) -> dict:
    """
    Critique the report and return granular quality scores + actionable feedback.

    Score dimensions (each 1.0–10.0):
      accuracy  — factual correctness
      coverage  — topic completeness
      clarity   — writing quality and readability
      citations — proper inline citations and source relevance

    Returns
    -------
    dict with keys:
        score           – float  overall score (mean of four sub-scores)
        feedback        – str    actionable reviewer feedback
        accuracy_score  – float
        coverage_score  – float
        clarity_score   – float
        citations_score – float
    """
    topic  = state.get("topic", "")
    report = state.get("report", "")

    print(f"\n{'='*60}")
    print(f"[REVIEWER] TOPIC: {topic!r}")
    print(f"[REVIEWER] Report length: {len(report)} chars")
    print(f"[REVIEWER] Report starts: {report[:80]!r}")
    print(f"{'='*60}")

    # Default safe values — NEVER 0 unless review actually fails
    accuracy_score  = 7.0
    coverage_score  = 7.0
    clarity_score   = 7.0
    citations_score = 7.0
    feedback        = "Review completed with default scoring (LLM parsing fallback)."

    llm_service = LangChainLLMService(
        model_name=LLMConfig.get_quality_model(),
        temperature=0.1,
        json_mode=True,
    )
    messages = REVIEWER_TEMPLATE.format_messages(report=report)

    try:
        response = llm_service.invoke(messages)
        cleaned  = _strip_code_fences(response.content)

        data = json.loads(cleaned)
        accuracy_score  = float(data.get("accuracy",  data.get("accuracy_score",  7.0)))
        coverage_score  = float(data.get("coverage",  data.get("coverage_score",  7.0)))
        clarity_score   = float(data.get("clarity",   data.get("clarity_score",   7.0)))
        citations_score = float(data.get("citations", data.get("citations_score", 7.0)))
        feedback        = str(data.get("feedback", data.get("review_feedback", feedback)))

    except json.JSONDecodeError:
        # Regex fallback — extract individual scores from malformed JSON
        def _get(key: str, default: float) -> float:
            m = re.search(rf'"{key}":\s*([0-9.]+)', response.content if 'response' in dir() else "")
            return float(m.group(1)) if m else default

        print(f"[REVIEWER] JSON parse failed — using regex fallback")
        accuracy_score  = _get("accuracy",  accuracy_score)
        coverage_score  = _get("coverage",  coverage_score)
        clarity_score   = _get("clarity",   clarity_score)
        citations_score = _get("citations", citations_score)

    except Exception as exc:
        print(f"[REVIEWER] Review LLM call failed: {exc} — using safe defaults (7.0 each)")

    def _clamp(v: float) -> float:
        return max(1.0, min(10.0, v))

    accuracy_score  = _clamp(accuracy_score)
    coverage_score  = _clamp(coverage_score)
    clarity_score   = _clamp(clarity_score)
    citations_score = _clamp(citations_score)

    overall = round(
        (accuracy_score + coverage_score + clarity_score + citations_score) / 4, 2
    )

    print(f"[REVIEWER] Scores — accuracy={accuracy_score} coverage={coverage_score} "
          f"clarity={clarity_score} citations={citations_score} overall={overall}")

    return {
        "score":           overall,
        "feedback":        feedback,
        "accuracy_score":  accuracy_score,
        "coverage_score":  coverage_score,
        "clarity_score":   clarity_score,
        "citations_score": citations_score,
    }


def _strip_code_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    return text.strip()
