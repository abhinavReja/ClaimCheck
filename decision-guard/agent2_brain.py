import json

from agent2_rag import search_docs
from llm import llm_json


def fact_check(claim: dict) -> dict:
    """
    Agent 2's MAIN job: take a claim from Agent 1,
    check it against company docs (RAG) + public web,
    return a verdict with evidence and recommendation.
    """
    claim_text = claim.get("claim", "")
    claim_type = claim.get("type", "unknown")
    speaker = claim.get("speaker", "Unknown")

    doc_results = search_docs(claim_text, n_results=3)
    doc_context = "\n\n".join(
        [f"[Source: {r['source']}]\n{r['content']}" for r in doc_results]
    )

    web_context = ""

    system = """You are a fact-checking agent for meetings. You receive a claim made during a meeting and evidence from company documents and web search.

Your job:
1. Compare the claim against the evidence
2. Determine if the claim is VERIFIED, CONTRADICTED, or UNVERIFIABLE
3. Provide specific evidence for your verdict
4. Rate your confidence: HIGH, MEDIUM, or LOW
5. If contradicted, explain the risk and recommend an action

Return ONLY valid JSON with this exact structure:
{
    "verdict": "VERIFIED" or "CONTRADICTED" or "UNVERIFIABLE",
    "confidence": "HIGH" or "MEDIUM" or "LOW",
    "evidence": "specific evidence from docs/web that supports your verdict",
    "risk": "what could go wrong if this claim is wrong (empty string if verified)",
    "recommendation": "what the team should do",
    "sources": ["list of source filenames or URLs used"]
}

Be specific. Cite exact numbers and dates from the evidence. Do NOT wrap in markdown.""",
    user = f"""CLAIM: {claim_text}
CLAIM TYPE: {claim_type}
SPEAKER: {speaker}

COMPANY DOCUMENTS:
{doc_context}

WEB SEARCH RESULTS:
{web_context if web_context else 'Web search disabled for this deployment.'}""",
    result = llm_json(
        system=system,
        user=user,
        default={
            "verdict": "UNVERIFIABLE",
            "confidence": "LOW",
            "evidence": "Could not process this claim.",
            "risk": "",
            "recommendation": "Needs human review.",
            "sources": [],
        },
        temperature=0.1,
    )

    result["original_claim"] = claim_text
    result["speaker"] = speaker
    return result


def answer_question(question: str, meeting_context: str) -> dict:
    """
    Q&A mode: user asks a question, Agent 2 answers using
    meeting transcript + company docs + web search.
    Returns answer with confidence and human-fallback flag.
    """
    doc_results = search_docs(question, n_results=3)
    doc_context = "\n\n".join(
        [f"[Source: {r['source']}]\n{r['content']}" for r in doc_results]
    )

    web_context = ""

    system = """You are a meeting knowledge assistant. Answer the user's question using the meeting context, company documents, and web search results provided.

Return ONLY valid JSON with this exact structure:
{
    "answer": "your detailed answer",
    "confidence": "HIGH" or "MEDIUM" or "LOW",
    "sources": ["sources used"],
    "needs_human": true or false,
    "human_reason": "why a human is needed (empty string if needs_human is false)"
}

If you cannot answer confidently, set needs_human to true and explain why.
Do NOT wrap in markdown.""",
    user = f"""QUESTION: {question}

MEETING TRANSCRIPT SO FAR:
{meeting_context}

COMPANY DOCUMENTS:
{doc_context}

WEB SEARCH:
{web_context if web_context else 'Web search disabled for this deployment.'}""",
    return llm_json(
        system=system,
        user=user,
        default={
            "answer": "I could not process this question properly.",
            "confidence": "LOW",
            "sources": [],
            "needs_human": True,
            "human_reason": "Processing error — please ask a team member.",
        },
        temperature=0.1,
    )


if __name__ == "__main__":
    from agent2_rag import load_documents

    print("Loading docs...\n")
    load_documents()

    print("\n--- Testing fact-check ---")
    test_claim = {
        "claim": "Our budget for Project Atlas is 200 thousand dollars",
        "speaker": "Sarah",
        "type": "number",
    }
    result = fact_check(test_claim)
    print(json.dumps(result, indent=2))

    print("\n\n--- Testing Q&A ---")
    answer = answer_question(
        "Are we ready to launch?",
        "Sarah said we can launch Friday. Mike said engineering is done. Security review is complete.",
    )
    print(json.dumps(answer, indent=2))
