import json
import time

from llm import llm_json


def extract_claims(transcript_chunk: str) -> list:
    """
    Agent 1's main job: read a chunk of meeting transcript
    and extract any checkable claims (numbers, dates, timelines,
    commitments, factual statements).
    """
    system = """You are a meeting claim extractor. Your job is to read meeting transcript text and extract any factual claims that can be verified.

Look for:
- Numbers (budgets, metrics, percentages)
- Timelines and dates (deadlines, delivery dates)
- Status claims ("is complete", "is ready", "is approved")
- Commitments ("we can do X by Y")
- Policy/process claims ("we don't need X")

Return a JSON array of claims. Each claim should have:
- "claim": the exact claim made
- "speaker": who said it
- "type": one of "number", "timeline", "status", "commitment", "policy"

If no checkable claims found, return an empty array [].
Return ONLY valid JSON, no other text."""
    user = f"Extract claims from this meeting transcript:\n\n{transcript_chunk}"
    return llm_json(system=system, user=user, default=[], temperature=0.1)


def format_question_for_agent2(question: str, transcript_so_far: str) -> dict:
    """
    When a user asks a question, Agent 1 packages it with
    meeting context and sends it to Agent 2.
    """
    return {"type": "question", "question": question, "meeting_context": transcript_so_far}


def read_transcript_live(filepath: str, delay: float = 2.0):
    """
    Simulates a live meeting by reading transcript line by line
    with a delay between each line.
    Yields (claim, transcript_so_far) for each detected claim.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    transcript_so_far = ""
    for line in lines:
        line = line.strip()
        if not line:
            continue

        transcript_so_far += line + "\n"
        print(f"\n🎤 {line}")

        claims = extract_claims(line)
        if claims:
            for claim in claims:
                print(f"  ⚡ Claim detected: {claim['claim']} (type: {claim['type']})")
                yield claim, transcript_so_far

        time.sleep(delay)


if __name__ == "__main__":
    print("Testing Agent 1 - Claim Extractor\n")

    test_text = """
    [00:01] Sarah: Our budget for Project Atlas is 200 thousand dollars.
    [00:15] Mike: I think we can launch by next Friday.
    """

    claims = extract_claims(test_text)
    print("Extracted claims:")
    for claim in claims:
        print(f"  - {claim}")
