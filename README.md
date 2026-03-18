# ClaimCheck
AI that improves judgment, not just productivity

--------------------------------------------------

WHAT IS CLAIMCHECK?

ClaimCheck is an AI system that helps teams make better decisions during meetings.

Instead of just summarizing conversations, it:
- listens to discussions
- detects important claims
- checks if they are correct
- warns you before wrong decisions are made

In simple words:
It helps you avoid mistakes in real time.

--------------------------------------------------

PROBLEM

In meetings:
- People make assumptions
- Teams overpromise timelines
- No one verifies information
- Wrong decisions are made

Example:
Client: “Can you deliver in 2 weeks?”
Team: “Yes” (without checking)

This leads to:
- missed deadlines
- loss of trust
- bad decisions

--------------------------------------------------

SOLUTION

ClaimCheck:
- listens to conversations
- detects risky statements
- verifies them using data
- gives real-time alerts

We don’t just summarize — we validate decisions.

--------------------------------------------------

HOW IT WORKS

1. Meeting input (audio or transcript)

2. Agent 1 (Listener)
   - detects claims (deadlines, numbers, commitments)

3. Agent 2 (Brain)
   - verifies using:
     - company documents
     - external data (web)

4. Output:
   - Verified
   - Contradicted
   - Uncertain

--------------------------------------------------

PROJECT STRUCTURE

claim-check/

app.py                -> Streamlit frontend (UI)
api.py                -> FastAPI backend (API)

agent1_listener.py    -> detects claims
agent2_brain.py       -> reasoning engine
agent2_rag.py         -> RAG (data retrieval)

video_processor.py    -> handles video/audio
llm.py                -> LLM integration
config.py             -> config/settings

sample_data/          -> test data
requirements.txt      -> dependencies
PROJECT.md            -> project description

--------------------------------------------------

INSTALLATION

1. Go to folder:
cd claim-check

2. Create virtual environment:
python3 -m venv .venv
source .venv/bin/activate

3. Install dependencies:
pip install -r requirements.txt

--------------------------------------------------

HOW TO RUN

You need TWO terminals.

Terminal 1 (Backend):
uvicorn api:app --reload --port 8000

Open:
http://127.0.0.1:8000/docs

Terminal 2 (Frontend):
streamlit run app.py

Open:
http://localhost:8501

--------------------------------------------------

EXAMPLE

Input:
“We can deliver in 2 weeks”

Output:
CONTRADICTION
Actual timeline: 5–6 weeks
Dependencies exist

Recommendation: Do not commit

--------------------------------------------------

FEATURES

- Real-time claim detection
- Fact-checking (RAG)
- Risk analysis
- Live Q&A
- Evidence-based answers
- Human fallback

--------------------------------------------------

OUTPUT TYPES

Verified -> correct
Contradicted -> wrong
Uncertain -> not enough data

Each includes:
- evidence
- risk
- recommendation

--------------------------------------------------

FUTURE SCOPE

- Zoom / Teams integration
- Memory across meetings
- Learning from past decisions
- Role-based validation

--------------------------------------------------

TECH STACK

- Python
- FastAPI
- Streamlit
- OpenAI / Anthropic
- ChromaDB
- MoviePy

--------------------------------------------------

WHY THIS MATTERS

Most tools:
- summarize meetings
- increase speed

ClaimCheck:
improves decision quality

--------------------------------------------------

FINAL THOUGHT

Other tools help you remember meetings.
DecisionGuard helps you make better decisions.

--------------------------------------------------

TEAM
Siya Singh
Misha Kumari 
Neha Valeti
Abhinav Reja
