"""
Writer Agent node.

Compiles verified sources and research plan into a polished Markdown report
using LangChain ChatPromptTemplate + LangChainLLMService (quality model tier).

The report is guaranteed to be about state["topic"] — it is the first field
in the human message template and is repeated explicitly throughout the prompt.

After LLM generation, the ## References section is deterministically replaced
with the exact bibliography built from real verified source URLs to prevent
any hallucinated references.
"""

import re
from backend.graph.state import ResearchState
from backend.llm.client import LangChainLLMService
from backend.llm.config import LLMConfig
from backend.llm.prompts import WRITER_TEMPLATE


def writer_node(state: ResearchState) -> dict:
    """
    Generate the final Markdown research report about state["topic"].
    Enforces real citations by rewriting the ## References section post-generation.
    """
    topic              = state.get("topic", "")
    plan               = state.get("plan", "")
    verified_sources   = state.get("verified_sources", []) or []
    citations_for_writer = state.get("citations_for_writer", "") or state.get("citations", "")
    citations_compact  = state.get("citations", "")
    feedback           = state.get("feedback", "")
    revision_count     = state.get("revision_count", 0)

    print(f"\n{'='*60}")
    print(f"[WRITER] TOPIC: {topic!r}")
    print(f"[WRITER] Verified sources: {len(verified_sources)}")
    print(f"[WRITER] Citations (writer): {len(citations_for_writer)} chars")
    print(f"[WRITER] Revision count: {revision_count}")
    print(f"{'='*60}")

    if not topic:
        print("[WRITER] CRITICAL: topic is empty — report will be about nothing!")

    # Format verified sources as a numbered context block
    sources_text = ""
    for i, src in enumerate(verified_sources, 1):
        sources_text += (
            f"[{i}] Title: {src.get('title', 'Untitled')}\n"
            f"    URL: {src.get('url', '')}\n"
            f"    Excerpt: {src.get('snippet', '')}\n\n"
        )

    if not sources_text:
        sources_text = f"(No external sources — generating from general knowledge about {topic})"

    # Append reviewer feedback on revision rounds
    revision_note = ""
    if revision_count > 0 and feedback:
        revision_note = (
            f"\n\nPrevious Reviewer Feedback — address ALL points:\n{feedback}"
        )

    llm_service = LangChainLLMService(
        model_name=LLMConfig.get_quality_model(),
        temperature=0.3,
    )
    messages = WRITER_TEMPLATE.format_messages(
        topic=topic,
        plan=plan,
        sources_text=sources_text,
        citations=citations_for_writer,
        revision_note=revision_note,
    )

    # Verify template injection is correct before sending to LLM
    human_msg = messages[-1].content if messages else ""
    print(f"[WRITER] Human message starts with: {human_msg[:80]!r}")
    assert human_msg.startswith(f"Topic: {topic}"), (
        f"[WRITER] BUG: human message does not start with 'Topic: {topic}'. "
        f"Got: {human_msg[:60]!r}"
    )

    response = llm_service.invoke(messages)
    report   = response.content

    print(f"[WRITER] Report generated ({len(report)} chars)")
    print(f"[WRITER] Report title line: {report.splitlines()[0]!r}")

    # --- Post-process: Replace ## References with real verified source URLs ---
    # This prevents any hallucinated URLs from appearing in the final report.
    if verified_sources and citations_compact:
        report = _enforce_real_references(report, citations_compact)

    return {
        "report":         report,
        "revision_count": revision_count + 1,
    }


def _enforce_real_references(report: str, citations_compact: str) -> str:
    """
    Replace the ## References section in the LLM-generated report with
    the authoritative compact bibliography built from verified real sources.
    This guarantees no hallucinated URLs appear in the final report.
    """
    # Build the authoritative references block
    real_refs = "## References\n\n" + citations_compact

    # Replace any existing ## References section (greedy to end of doc)
    pattern = r"##\s*References.*$"
    new_report = re.sub(pattern, real_refs, report, flags=re.IGNORECASE | re.DOTALL)

    # If no ## References section was found, append it
    if new_report == report:
        new_report = report.rstrip() + "\n\n" + real_refs

    print(f"[WRITER] References section enforced with {citations_compact.count(chr(10)) + 1} real sources")
    return new_report

