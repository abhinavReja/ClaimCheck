# DecisionGuard — AI Decision Auditor for Meetings

## What Is This?

DecisionGuard is a two-agent AI system that watches meeting conversations
and automatically fact-checks claims in real time using company documents
(via RAG). It also supports on-demand Q&A where anyone
can ask a question and get an evidence-backed answer — or a "needs human"
flag if the system isn't confident.

Built for **DevHacks S3 — Track 2: Designing AI That Improves Judgment,
Not Just Productivity.**

---

## The Problem

In meetings, people constantly throw out numbers, timelines, and commitments
that may be wrong, outdated, or contradicted by actual company data. Nobody
checks in real time. Bad decisions get made based on bad information.

Existing tools (Zoom AI Companion, Teams Copilot) focus on summarization,
recaps, and Q&A — but none of them autonomously fact-check claims against
internal company truth + external public data without being asked.

---

## The Solution

Two AI agents working together:

### Agent 1 — The Listener
- Reads meeting transcript in real time (simulated via line-by-line feed)
- Extracts checkable claims: numbers, timelines, status claims, commitments,
  policy/process claims
- Sends each claim to Agent 2 for verification
- Also forwards user questions to Agent 2

### Agent 2 — The Brain
- Receives claims from Agent 1
- Checks against company docs via RAG (ChromaDB vector store)
- Uses LLM reasoning to produce a verdict:
  - VERIFIED — claim matches evidence
  - CONTRADICTED — claim conflicts with evidence (shows what's wrong)
  - UNVERIFIABLE — not enough data (flags for human review)
- Returns evidence, risk assessment, confidence score, and recommendation
- Also answers user questions using meeting context + docs

### Human Fallback
- If Agent 2's confidence is LOW or data is insufficient, it returns
  "needs human input" with an explanation of why
- This prevents hallucination and builds trust

---

## Architecture

```
Meeting Transcript (simulated)
        │
        ▼
   ┌─────────────┐
   │   Agent 1    │ ← Claim Extractor + Q&A Router
   │  (Listener)  │
   └──────┬───────┘
          │ claims / questions
          ▼
   ┌─────────────┐
   │   Agent 2    │ ← Fact-Checker + Q&A Answerer
   │   (Brain)    │
   │              │──→ Company Docs (ChromaDB RAG)
   │              │──→ LLM Reasoning (OpenAI)
   └──────┬───────┘
          │ verdict / answer
          ▼
   ┌─────────────┐
   │  Dashboard   │ ← Streamlit UI
   │  (Frontend)  │
   │              │──→ Transcript panel (left)
   │              │──→ Fact-check cards (right)
   │              │──→ Q&A input box (bottom)
   └──────────────┘
```

---

## Tech Stack

| Component        | Technology                          |
|------------------|-------------------------------------|
| Language         | Python                              |
| LLM              | OpenAI GPT-4o-mini (via API)        |
| Vector Store     | ChromaDB (local, persistent)        |
| Backend API      | FastAPI                             |
| Frontend         | Streamlit                           |
| Agent Comm       | Direct function calls (no framework)|

---

## File Structure

```
decision-guard/
├── .env                    ← API keys (OPENAI_API_KEY / ANTHROPIC_API_KEY)
├── requirements.txt        ← pip dependencies
├── config.py               ← shared config (keys, model, paths)
├── PROJECT.md              ← this file
├── sample_data/
│   ├── transcript.txt      ← fake meeting transcript
│   ├── budget_2025.txt     ← fake budget doc (contradicts transcript)
│   ├── eng_roadmap.txt     ← fake eng timeline (contradicts transcript)
│   ├── vendor_contract.txt ← fake vendor contract (contradicts transcript)
│   ├── metrics_dashboard.txt ← fake KPIs (contradicts transcript)
│   └── security_checklist.txt ← fake checklist (contradicts transcript)
├── agent1_listener.py      ← Agent 1: claim extraction + Q&A routing
├── agent2_rag.py           ← RAG: ChromaDB doc loading + search
├── agent2_brain.py         ← Agent 2: fact-check + Q&A reasoning
├── api.py                  ← FastAPI backend (connects everything)
└── app.py                  ← Streamlit frontend (user-facing dashboard)
```

---

## How to Run

### Setup

```bash
pip install -r requirements.txt
```

Create your `.env` (or copy `.env.example` and fill keys):

```bash
cp .env.example .env
```

### Run the Full App

```bash
# Terminal 1: Start API
uvicorn api:app --reload --port 8000

# Terminal 2: Start Frontend
streamlit run app.py
```

Open `http://localhost:8501`.
