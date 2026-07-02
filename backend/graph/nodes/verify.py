"""
Verification Agent node.

Uses a fast LLM to verify that retrieved search results are actually relevant
to the user's topic before they are passed to the Writer.
Builds the final, authoritative citations bibliography from ONLY verified sources.
"""

import json
import re
from typing import List, Dict, Any
from backend.graph.state import ResearchState
from backend.llm.client import LangChainLLMService
from backend.llm.config import LLMConfig
from backend.llm.prompts import VERIFY_TEMPLATE
from backend.search.citation_formatter import CitationFormatter


def verify_node(state: ResearchState) -> dict:
    """
    Filter search results using an LLM to check relevance to the topic.
    Builds the authoritative citation bibliography from verified sources only.

    Steps
    -----
    1. Check if sources exist.
    2. Format sources for the LLM.
    3. Use VERIFY_TEMPLATE to get a JSON array of relevant source IDs.
    4. Build verified sources list.
    5. Build two citation strings:
       - citations_for_writer: rich (title + URL + snippet) for the Writer LLM prompt
       - citations_compact:    clean  (title + URL only) for DB storage and UI display
    """
    topic   = state.get("topic", "")
    sources: List[Dict[str, Any]] = state.get("sources", []) or []

    print(f"\n{'='*60}")
    print(f"[VERIFY] TOPIC: {topic!r}")
    print(f"[VERIFY] Input sources: {len(sources)}")
    print(f"{'='*60}")

    if not sources:
        print("[VERIFY] No sources to verify.")
        return {"verified_sources": [], "citations": ""}

    # Prepare sources text for the LLM
    sources_text = ""
    for i, src in enumerate(sources, 1):
        sources_text += f"[{i}] {src.get('title', 'Untitled')}\nURL: {src.get('url', '')}\nSnippet: {src.get('snippet', '')}  \n\n"

    llm_service = LangChainLLMService(
        model_name=LLMConfig.get_fast_model(),
        temperature=0.1,
        json_mode=False,
    )
    messages = VERIFY_TEMPLATE.format_messages(topic=topic, sources_text=sources_text)

    print(f"[VERIFY] Sending {len(sources)} sources to LLM for relevance check.")
    response = llm_service.invoke(messages)
    cleaned = _strip_code_fences(response.content)

    relevant_ids = []
    try:
        relevant_ids = json.loads(cleaned)
        if not isinstance(relevant_ids, list):
            relevant_ids = []
    except Exception as e:
        print(f"[VERIFY] JSON parse failed: {e}. Output was: {cleaned[:100]}")
        # Regex fallback: extract numbers inside brackets
        m = re.search(r'\[(.*?)\]', cleaned)
        if m:
            nums = m.group(1).split(',')
            for n in nums:
                n = n.strip()
                if n.isdigit():
                    relevant_ids.append(int(n))

    # Safely construct the verified sources list
    verified = []
    for sid in relevant_ids:
        if isinstance(sid, int) and 1 <= sid <= len(sources):
            verified.append(sources[sid - 1])

    # Fallback: if the LLM filtered out everything, forward top 3 as fallback
    if not verified:
        print("[VERIFY] LLM found no relevant sources. Forwarding top 3 as fallback.")
        verified = sources[:3]

    # --- Build citation strings from ONLY verified, real sources ---
    # Rich version (with snippets) for the Writer LLM
    citations_for_writer = CitationFormatter.build_bibliography(verified)
    # Compact version (title + URL only) for DB storage and UI display
    citations_compact = CitationFormatter.build_bibliography_compact(verified)

    print(f"[VERIFY] Forwarding {len(verified)} verified sources to Writer")
    for i, src in enumerate(verified, 1):
        print(f"  [{i}] {src.get('title', '')[:60]!r} — {src.get('url', '')[:60]}")

    return {
        "verified_sources":    verified,
        "citations":           citations_compact,        # stored in DB, shown in UI
        "citations_for_writer": citations_for_writer,   # rich version for Writer LLM
    }


def _strip_code_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    return text.strip()

