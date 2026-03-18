import time

import requests
import streamlit as st

API_URL = "http://localhost:8000"

st.set_page_config(page_title="ClaimCheck", page_icon="🛡️", layout="wide")

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Fraunces:opsz,wght@9..144,600;700&display=swap');

:root{
  --bg0: #070A12;
  --bg1: #0B1020;
  --panel: rgba(255,255,255,0.06);
  --panel2: rgba(255,255,255,0.08);
  --stroke: rgba(255,255,255,0.10);
  --text: rgba(255,255,255,0.92);
  --muted: rgba(255,255,255,0.68);
  --good: #2DE2A6;
  --warn: #FFB020;
  --bad: #FF4D6D;
  --brand: #7C5CFF;
  --brand2:#00D4FF;
}

.stApp{
  background:
    radial-gradient(1100px 500px at 10% 0%, rgba(124,92,255,0.23), transparent 60%),
    radial-gradient(900px 450px at 95% 10%, rgba(0,212,255,0.18), transparent 55%),
    linear-gradient(180deg, var(--bg0), var(--bg1));
}

html, body, [class*="css"]  { font-family: "DM Sans", system-ui, -apple-system, Segoe UI, sans-serif; }

/* tighter default spacing */
.block-container { padding-top: 1.0rem; padding-bottom: 1.5rem; }

/* hide default Streamlit header padding artifacts */
header[data-testid="stHeader"]{ background: transparent; }

.dg-hero{
  border: 1px solid var(--stroke);
  background: linear-gradient(135deg, rgba(124,92,255,0.18), rgba(0,212,255,0.08));
  box-shadow: 0 18px 60px rgba(0,0,0,0.40);
  border-radius: 18px;
  padding: 18px 18px;
  margin: 0 0 14px 0;
  position: relative;
  overflow: hidden;
}
.dg-hero:before{
  content:"";
  position:absolute; inset:-2px;
  background: radial-gradient(700px 180px at 20% 10%, rgba(255,255,255,0.10), transparent 60%);
  pointer-events:none;
}
.dg-title{
  font-family: "Fraunces", serif;
  letter-spacing: 0.2px;
  color: var(--text);
  font-size: 34px;
  line-height: 1.1;
  margin: 0;
}
.dg-sub{
  color: var(--muted);
  margin: 6px 0 0 0;
  font-size: 14px;
}
.dg-row{
  display:flex; gap:10px; flex-wrap:wrap; margin-top: 10px;
}
.dg-pill{
  border: 1px solid var(--stroke);
  background: rgba(255,255,255,0.06);
  color: var(--muted);
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 12px;
}
.dg-pill b{ color: var(--text); font-weight: 700; }

.dg-panel{
  border: 1px solid var(--stroke);
  background: rgba(255,255,255,0.05);
  border-radius: 16px;
  padding: 12px 12px;
  box-shadow: 0 14px 40px rgba(0,0,0,0.28);
}

.dg-section-title{
  font-size: 13px;
  color: var(--muted);
  letter-spacing: 0.18em;
  text-transform: uppercase;
  margin: 0 0 10px 0;
}

.dg-transcript{
  border: 1px solid var(--stroke);
  background: rgba(0,0,0,0.18);
  border-radius: 14px;
  padding: 10px 10px;
  height: 340px;
  overflow: auto;
}
.dg-line{
  padding: 8px 10px;
  margin: 8px 0;
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.08);
  background: rgba(255,255,255,0.05);
  color: var(--text);
  font-size: 14px;
}
.dg-line .meta{ color: var(--muted); font-size: 12px; margin-bottom: 3px; }

.dg-card{
  border: 1px solid var(--stroke);
  background: rgba(255,255,255,0.05);
  border-radius: 14px;
  padding: 12px 12px;
  margin: 10px 0;
  position: relative;
}
.dg-card:before{
  content:"";
  position:absolute; left:0; top:0; bottom:0; width:4px;
  border-radius: 14px 0 0 14px;
  background: var(--stroke);
}
.dg-badge{
  display:inline-flex; align-items:center; gap:6px;
  padding: 5px 10px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.12);
  background: rgba(255,255,255,0.06);
  font-size: 12px;
  color: var(--text);
  font-weight: 700;
}
.dg-claim{ color: var(--text); font-size: 14px; margin-top: 8px; }
.dg-small{ color: var(--muted); font-size: 12px; margin-top: 8px; }

.dg-verified:before{ background: var(--good); }
.dg-contradicted:before{ background: var(--bad); }
.dg-unverifiable:before{ background: var(--warn); }

/* make buttons more modern */
div.stButton > button{
  border-radius: 12px !important;
  border: 1px solid rgba(255,255,255,0.18) !important;
  background: linear-gradient(135deg, rgba(124,92,255,0.85), rgba(0,212,255,0.55)) !important;
  color: #0B1020 !important;
  font-weight: 800 !important;
}
div.stButton > button:hover{ filter: brightness(1.06); }

/* inputs */
.stTextInput input, .stTextArea textarea, .stFileUploader label, .stSelectbox div{
  border-radius: 12px !important;
}
</style>

<div class="dg-hero">
  <div class="dg-title">ClaimCheck</div>
  <div class="dg-sub">AI decision auditor for meetings — live fact‑checking + Q&A</div>
  <div class="dg-row">
    <div class="dg-pill"><b>Listener</b> extracts claims</div>
    <div class="dg-pill"><b>RAG</b> checks internal docs</div>
    <div class="dg-pill"><b>3 flags</b>: verified / contradicted / unverifiable</div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)


def _verdict_style(verdict: str) -> tuple[str, str]:
    v = (verdict or "").strip().upper()
    if v == "VERIFIED":
        return ("dg-verified", "🟢 VERIFIED")
    if v == "CONTRADICTED":
        return ("dg-contradicted", "🔴 CONTRADICTION")
    # For the UI demo we map UNVERIFIABLE -> PARTIAL MATCH
    return ("dg-unverifiable", "🟡 PARTIAL MATCH")


def _fmt_sources(sources) -> str:
    if not sources:
        return ""
    if isinstance(sources, str):
        return sources
    try:
        return ", ".join([str(s) for s in sources if s])
    except Exception:
        return str(sources)

if "transcript_lines" not in st.session_state:
    st.session_state.transcript_lines = []
if "fact_checks" not in st.session_state:
    st.session_state.fact_checks = []
if "full_transcript" not in st.session_state:
    st.session_state.full_transcript = ""
if "is_running" not in st.session_state:
    st.session_state.is_running = False
if "qa_history" not in st.session_state:
    st.session_state.qa_history = []
if "sim_lines" not in st.session_state:
    st.session_state.sim_lines = []
if "sim_idx" not in st.session_state:
    st.session_state.sim_idx = 0
if "_sim_tick_rerun" not in st.session_state:
    st.session_state._sim_tick_rerun = False

with st.sidebar:
    st.markdown("### Controls")
    st.caption("Tune playback speed and choose input source.")
    sim_speed = st.slider("Dialogue speed", min_value=0.05, max_value=0.8, value=0.25, step=0.05)
    st.markdown("---")
    st.markdown("### Stats")
    total = len(st.session_state.fact_checks)
    contradicted = len(
        [f for f in st.session_state.fact_checks if f.get("verdict") == "CONTRADICTED"]
    )
    verified = len([f for f in st.session_state.fact_checks if f.get("verdict") == "VERIFIED"])
    unverifiable = total - contradicted - verified
    st.metric("Claims checked", total)
    st.metric("Contradicted", contradicted)
    st.metric("Verified", verified)
    st.metric("Partial matches", unverifiable)
    st.markdown("---")
    st.markdown("### About")
    st.write(
        "ClaimCheck watches a meeting transcript, extracts checkable claims, "
        "and validates them against internal documents (RAG)."
    )
    st.markdown("### Future scope")
    st.write("- Live Zoom/Teams ingestion")
    st.write("- Cross‑meeting decision memory")
    st.write("- Alerts + owner assignment")


col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown('<div class="dg-panel">', unsafe_allow_html=True)
    st.markdown('<div class="dg-section-title">Meeting transcript</div>', unsafe_allow_html=True)

    c1, c2 = st.columns([1.2, 0.8])
    with c1:
        uploaded_file = st.file_uploader("Upload transcript (.txt)", type="txt")
    with c2:
        use_sample = st.checkbox("Use sample transcript", value=True)

    start_clicked = st.button(
        "▶️ Start Meeting Simulation"
        if not st.session_state.is_running
        else "Started Meeting Simulation",
        type="primary",
        disabled=st.session_state.is_running,
    )

    if start_clicked:
        st.session_state.is_running = True
        st.session_state.transcript_lines = []
        st.session_state.fact_checks = []
        st.session_state.full_transcript = ""
        st.session_state.qa_history = []
        st.session_state.sim_lines = []
        st.session_state.sim_idx = 0
        st.session_state._sim_tick_rerun = False

        if uploaded_file:
            content = uploaded_file.read().decode("utf-8")
        elif use_sample:
            try:
                with open("sample_data/transcript.txt", "r", encoding="utf-8") as f:
                    content = f.read()
            except FileNotFoundError:
                st.error("sample_data/transcript.txt not found. Create it first.")
                st.stop()
        else:
            st.warning("Upload a transcript or check 'Use sample transcript'.")
            st.stop()

        st.session_state.sim_lines = [l.strip() for l in content.split("\n") if l.strip()]

    progress_bar = st.progress(
        0 if not st.session_state.sim_lines else (st.session_state.sim_idx / max(1, len(st.session_state.sim_lines)))
    )
    transcript_container = st.empty()

    if not st.session_state.transcript_lines:
        transcript_container.markdown(
            '<div class="dg-transcript"><div class="dg-small">Waiting for transcript…</div></div>',
            unsafe_allow_html=True,
        )
    else:
        # Render as chat-like bubbles
        rendered = ['<div class="dg-transcript">']
        for raw in st.session_state.transcript_lines[-120:]:
            line = raw.strip()
            if not line:
                continue
            # best-effort parse: "[00:01] Name (Role): message"
            meta = ""
            msg = line
            if "]" in line and ":" in line:
                try:
                    left, right = line.split("]:", 1)
                    meta = (left + "]").strip()
                    msg = right.strip()
                except Exception:
                    meta = ""
                    msg = line
            rendered.append(
                f'<div class="dg-line"><div class="meta">{meta}</div><div class="msg">{msg}</div></div>'
            )
        rendered.append("</div>")
        transcript_container.markdown("".join(rendered), unsafe_allow_html=True)

    # Process exactly one line per run. We DO NOT rerun immediately here,
    # otherwise the right-hand column won't render until the simulation ends.
    if st.session_state.is_running and st.session_state.sim_lines:
        i = st.session_state.sim_idx
        if i < len(st.session_state.sim_lines):
            line = st.session_state.sim_lines[i]
            st.session_state.transcript_lines.append(line)
            st.session_state.full_transcript += line + "\n"

            try:
                response = requests.post(
                    f"{API_URL}/process-transcript", json={"text": line}, timeout=60
                )
                if response.status_code == 200:
                    data = response.json()
                    for result in data.get("results", []):
                        st.session_state.fact_checks.append(result)
            except requests.exceptions.ConnectionError:
                st.error(
                    "Cannot connect to API. Make sure 'uvicorn api:app --reload --port 8000' is running."
                )
                st.session_state.is_running = False
            except Exception as e:
                st.error(f"API error: {e}")

            st.session_state.sim_idx += 1
            progress_bar.progress(st.session_state.sim_idx / len(st.session_state.sim_lines))
            st.session_state._sim_tick_rerun = True
        else:
            st.session_state.is_running = False
            st.session_state._sim_tick_rerun = False
            st.success("✅ Meeting simulation complete!")

    if st.session_state.transcript_lines and not st.session_state.is_running:
        st.text_area("Full Transcript", "\n".join(st.session_state.transcript_lines), height=300)

    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown('<div class="dg-panel">', unsafe_allow_html=True)
    st.markdown('<div class="dg-section-title">Fact-check results</div>', unsafe_allow_html=True)

    if not st.session_state.fact_checks:
        st.markdown(
            '<div class="dg-small">Start the simulation to see verdicts appear here in real time.</div>',
            unsafe_allow_html=True,
        )

    for i, check in enumerate(st.session_state.fact_checks):
        verdict = check.get("verdict", "UNKNOWN")
        claim_text = check.get("original_claim", "")
        speaker = check.get("speaker", "Unknown")
        cls, badge = _verdict_style(verdict)
        st.markdown(
            f"""
<div class="dg-card {cls}">
  <span class="dg-badge">{badge}</span>
  <div class="dg-claim">{claim_text}</div>
  <div class="dg-small">Speaker: <b>{speaker}</b></div>
</div>
""",
            unsafe_allow_html=True,
        )

        with st.expander(
            f"Details — {speaker}", expanded=(verdict == "CONTRADICTED")
        ):
            st.write(f"**Evidence:** {check.get('evidence', 'N/A')}")
            st.write(f"**Confidence:** {check.get('confidence', 'N/A')}")
            if check.get("risk"):
                st.write(f"**Risk:** {check['risk']}")
            st.write(f"**Recommendation:** {check.get('recommendation', 'N/A')}")
            sources = check.get("sources", [])
            src = _fmt_sources(sources)
            if src:
                st.write(f"**Sources:** {src}")

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")
st.markdown("### Ask a Question")

question = st.text_input("Ask anything about the meeting or company data:")

if st.button("Ask Agent") and question:
    with st.spinner("Agent 2 is thinking..."):
        try:
            response = requests.post(
                f"{API_URL}/ask",
                json={"question": question, "meeting_context": st.session_state.full_transcript},
                timeout=60,
            )
            if response.status_code == 200:
                answer_data = response.json()
                st.session_state.qa_history.append({"question": question, "answer": answer_data})

                if answer_data.get("needs_human"):
                    st.warning(
                        f"🙋 **Needs Human Input**\n\n"
                        f"{answer_data.get('human_reason', 'Insufficient data.')}"
                    )
                else:
                    confidence = answer_data.get("confidence", "N/A")
                    answer_text = answer_data.get("answer", "")
                    if confidence == "HIGH":
                        st.success(f"**Answer (Confidence: {confidence})**\n\n{answer_text}")
                    elif confidence == "MEDIUM":
                        st.info(f"**Answer (Confidence: {confidence})**\n\n{answer_text}")
                    else:
                        st.warning(
                            f"**Answer (Confidence: {confidence})**\n\n{answer_text}"
                        )

                    sources = answer_data.get("sources", [])
                    if sources:
                        st.caption(f"Sources: {', '.join(sources)}")
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to API. Is the backend running?")
        except Exception as e:
            st.error(f"Error: {e}")

if st.session_state.is_running and st.session_state._sim_tick_rerun:
    # Allow the UI (including right column) to render before advancing.
    st.session_state._sim_tick_rerun = False
    time.sleep(sim_speed)
    st.rerun()

