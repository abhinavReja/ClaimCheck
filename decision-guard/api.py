from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent1_listener import extract_claims
from agent2_brain import answer_question, fact_check
from agent2_rag import load_documents

app = FastAPI(title="DecisionGuard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    load_documents()
    print("✅ Documents loaded. API ready.")


class TranscriptInput(BaseModel):
    text: str


class QuestionInput(BaseModel):
    question: str
    meeting_context: Optional[str] = ""


@app.post("/extract-claims")
async def api_extract_claims(data: TranscriptInput):
    claims = extract_claims(data.text)
    return {"claims": claims}


@app.post("/fact-check")
async def api_fact_check(data: dict):
    return fact_check(data)


@app.post("/process-transcript")
async def api_process_transcript(data: TranscriptInput):
    claims = extract_claims(data.text)
    results = [fact_check(claim) for claim in claims]
    return {"claims": claims, "results": results}


@app.post("/ask")
async def api_ask_question(data: QuestionInput):
    return answer_question(data.question, data.meeting_context or "")


@app.get("/health")
async def health():
    return {"status": "running", "service": "DecisionGuard"}

