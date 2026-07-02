"""
Intent Analyzer Agent node.

Evaluates the user's topic for ambiguity before the research pipeline starts.
Low-confidence queries trigger a clarification response instead of a full report.
"""

import json
import re
from backend.graph.state import ResearchState
from backend.llm.client import LangChainLLMService
from backend.llm.config import LLMConfig
from backend.llm.prompts import INTENT_TEMPLATE


def intent_analyzer_node(state: ResearchState) -> dict:
    """
    Analyse the user's topic for clarity and research intent.
    """
    topic = state.get("topic", "")
    print(f"\n{'='*60}")
    print(f"[INTENT ANALYZER] TOPIC: {topic!r}")
    print(f"{'='*60}")

    llm_service = LangChainLLMService(
        model_name=LLMConfig.get_fast_model(),
        temperature=0.1,
        json_mode=True,
    )
    messages = INTENT_TEMPLATE.format_messages(topic=topic)
    print(f"[INTENT ANALYZER] Sending to LLM: model={LLMConfig.get_fast_model()}")

    response = llm_service.invoke(messages)
    cleaned  = _strip_code_fences(response.content)

    # Defaults
    confidence           = 0.9
    interpretations      = [topic]
    clarification_prompt = ""

    try:
        data = json.loads(cleaned)
        confidence           = float(data.get("confidence", 0.9))
        interpretations      = data.get("interpretations", [topic])
        clarification_prompt = data.get("clarification_prompt", "")
    except Exception as e:
        print(f"[INTENT ANALYZER] JSON parse failed ({e}), using regex fallback")
        m = re.search(r'"confidence":\s*([0-9.]+)', cleaned)
        if m:
            confidence = float(m.group(1))
        im = re.search(r'"interpretations":\s*(\[.*?\])', cleaned, re.DOTALL)
        if im:
            try:
                interpretations = json.loads(im.group(1))
            except Exception:
                pass
        pm = re.search(r'"clarification_prompt":\s*"(.*?)"', cleaned, re.DOTALL)
        if pm:
            clarification_prompt = pm.group(1)

    confidence           = max(0.0, min(1.0, confidence))
    clarification_needed = confidence < 0.7

    print(f"[INTENT ANALYZER] Confidence: {confidence:.2f} | Clarification needed: {clarification_needed}")
    print(f"[INTENT ANALYZER] Interpretations: {interpretations}")

    return {
        "confidence":           confidence,
        "clarification_needed": clarification_needed,
        "clarification_prompt": clarification_prompt if clarification_needed else "",
        "interpretations":      interpretations,
    }


def _strip_code_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    return text.strip()
