import time

import requests
import streamlit as st

API_URL = "http://localhost:8000"

st.set_page_config(page_title="DecisionGuard", page_icon="🛡️", layout="wide")

st.title("🛡️ DecisionGuard")
st.caption("AI Decision Auditor for Meetings — Live Fact-Checking + Q&A")

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

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 Meeting Transcript")

    uploaded_file = st.file_uploader("Upload transcript (.txt)", type="txt")
    use_sample = st.checkbox("Use sample transcript", value=True)

    if st.button("▶️ Start Meeting Simulation", type="primary"):
        st.session_state.is_running = True
        st.session_state.transcript_lines = []
        st.session_state.fact_checks = []
        st.session_state.full_transcript = ""
        st.session_state.qa_history = []

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

        lines = [l.strip() for l in content.split("\n") if l.strip()]

        progress_bar = st.progress(0)
        transcript_container = st.empty()

        for i, line in enumerate(lines):
            st.session_state.transcript_lines.append(line)
            st.session_state.full_transcript += line + "\n"

            transcript_container.text_area(
                "Live Transcript",
                "\n".join(st.session_state.transcript_lines),
                height=300,
                key=f"transcript_{i}",
            )

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
                st.stop()
            except Exception as e:
                st.error(f"API error: {e}")

            progress_bar.progress((i + 1) / len(lines))
            time.sleep(1)

        st.session_state.is_running = False
        st.success("✅ Meeting simulation complete!")

    if st.session_state.transcript_lines and not st.session_state.is_running:
        st.text_area(
            "Full Transcript", "\n".join(st.session_state.transcript_lines), height=300
        )

with col2:
    st.subheader("⚡ Fact-Check Results")

    if not st.session_state.fact_checks:
        st.info("Waiting for meeting data... Start the simulation to see results.")

    for i, check in enumerate(st.session_state.fact_checks):
        verdict = check.get("verdict", "UNKNOWN")
        claim_text = check.get("original_claim", "")
        speaker = check.get("speaker", "Unknown")

        if verdict == "CONTRADICTED":
            st.error(f"🔴 **CONTRADICTED** — {claim_text}")
        elif verdict == "VERIFIED":
            st.success(f"🟢 **VERIFIED** — {claim_text}")
        else:
            st.warning(f"🟡 **UNVERIFIABLE** — {claim_text}")

        with st.expander(
            f"Details — {speaker}", expanded=(verdict == "CONTRADICTED")
        ):
            st.write(f"**Evidence:** {check.get('evidence', 'N/A')}")
            st.write(f"**Confidence:** {check.get('confidence', 'N/A')}")
            if check.get("risk"):
                st.write(f"**Risk:** {check['risk']}")
            st.write(f"**Recommendation:** {check.get('recommendation', 'N/A')}")
            sources = check.get("sources", [])
            if sources:
                st.write(f"**Sources:** {', '.join(sources)}")

st.markdown("---")
st.subheader("💬 Ask a Question")

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

with st.sidebar:
    st.header("ℹ️ About")
    st.write(
        "**DecisionGuard** is an AI Decision Auditor that watches meetings "
        "and automatically fact-checks claims against company documents and public data."
    )

    st.markdown("---")
    st.header("📊 Stats")
    total = len(st.session_state.fact_checks)
    contradicted = len(
        [f for f in st.session_state.fact_checks if f.get("verdict") == "CONTRADICTED"]
    )
    verified = len([f for f in st.session_state.fact_checks if f.get("verdict") == "VERIFIED"])
    unverifiable = total - contradicted - verified

    st.metric("Total Claims Checked", total)
    st.metric("Contradictions Found", contradicted)
    st.metric("Verified Claims", verified)
    st.metric("Unverifiable", unverifiable)

    st.markdown("---")
    st.header("💬 Q&A History")
    for qa in st.session_state.qa_history:
        st.write(f"**Q:** {qa['question']}")
        ans = qa["answer"]
        if ans.get("needs_human"):
            st.write(f"**A:** 🙋 Needs human — {ans.get('human_reason', '')}")
        else:
            st.write(f"**A:** {ans.get('answer', '')[:200]}...")
        st.markdown("---")

    st.header("🔮 Future Scope")
    st.write("• Live Zoom/Teams integration via RTMS")
    st.write("• 15-min deep summary push between agents")
    st.write("• Decision memory across meetings")
    st.write("• Outcome tracking & learning")

