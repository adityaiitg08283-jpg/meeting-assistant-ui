import streamlit as st
import requests
import time
import pandas as pd
import json

# ---------------------------------------------------------
# 1. Page Config & Professional Theme
# ---------------------------------------------------------
st.set_page_config(
    page_title="AURA | AI Meeting Intelligence",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .header-card {
        background: linear-gradient(135deg, #1e2640 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 25px;
    }
    .status-card {
        background: #1e293b;
        border-left: 4px solid #38bdf8;
        padding: 14px 20px;
        border-radius: 8px;
        margin-bottom: 15px;
    }
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #2563eb 0%, #7c3aed 100%);
        color: white;
        border: none;
        padding: 14px 28px;
        font-size: 16px;
        font-weight: 600;
        border-radius: 12px;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. Sidebar Configuration
# ---------------------------------------------------------
with st.sidebar:
    st.title("⚙️ Pipeline Config")
    
    st.subheader("🌐 Serverless API Endpoint")
    backend_url = st.text_input(
        "Modal API Endpoint URL",
        value="https://your-modal-app.modal.run/process",
        help="Modal.com backend endpoint paste karein"
    )
    
    st.markdown("---")
    st.subheader("📖 Domain Glossary")
    st.caption("Technical terms, jargon, aur names jo ASR miss na kare:")
    default_glossary = "Kubernetes, PostgreSQL, Redis, CI/CD, OKR, Priya, Anirban"
    glossary_input = st.text_area("Edit Glossary", value=default_glossary, height=100)
    
    st.markdown("---")
    st.subheader("🤖 Active Models")
    st.caption("• **STT:** OpenAI Whisper-small")
    st.caption("• **Refinement:** Qwen2.5-3B + Code Guards")
    st.caption("• **Documentation:** Gemini Flash API")

# ---------------------------------------------------------
# 3. Main Header & File Input
# ---------------------------------------------------------
st.markdown("""
<div class="header-card">
    <h1 style="margin:0; color: #f8fafc; font-size: 30px;">🎙️ Meeting Assistant Pipeline</h1>
    <p style="margin-top:8px; color: #94a3b8; font-size: 14px;">
        6-Stage Verified Intelligence: STT ➔ Refinement ➔ Extraction ➔ Rules ➔ Verification ➔ Minutes
    </p>
</div>
""", unsafe_allow_html=True)

col_upload, col_preview = st.columns([2, 1])
with col_upload:
    uploaded_audio = st.file_uploader("Upload Meeting Audio", type=["wav", "mp3", "m4a", "flac", "ogg"])

with col_preview:
    if uploaded_audio is not None:
        st.caption(f"📁 **File:** {uploaded_audio.name} ({round(uploaded_audio.size / (1024*1024), 2)} MB)")
        st.audio(uploaded_audio)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. Pipeline Execution Logic
# ---------------------------------------------------------
if st.button("🚀 Run 6-Step Meeting Pipeline"):
    if uploaded_audio is None:
        st.warning("⚠️ Kripya pehle audio file upload karein!")
    else:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        stages = [
            ("1/6 Speech-to-Text", "Whisper transcribing audio and generating hypotheses..."),
            ("2/6 Refinement", "Qwen2.5-3B applying domain glossary and code guards..."),
            ("3/6 Stage A: Extraction", "Gemini Flash extracting draft decisions & action tasks..."),
            ("4/6 Stage B: Filter Rules", "Python code filtering bad citations & unconfirmed items..."),
            ("5/6 Stage D: Verification Pass", "Cross-checking extracted items against cited transcript lines..."),
            ("6/6 Stage C: Final Writing", "Generating executive summary and topic-wise minutes...")
        ]
        
        try:
            # Send file to serverless API backend
            files = {"file": (uploaded_audio.name, uploaded_audio.getvalue(), uploaded_audio.type)}
            data_payload = {"glossary": glossary_input}
            
            # API Request
            for idx, (stage_name, stage_desc) in enumerate(stages):
                status_text.markdown(f'<div class="status-card"><b>Current Stage ({stage_name}):</b> {stage_desc}</div>', unsafe_allow_html=True)
                progress_bar.progress((idx + 1) / 6)
                time.sleep(0.8)

            response = requests.post(backend_url, files=files, data=data_payload, timeout=600)
            
            if response.status_code == 200:
                result = response.json()
                st.session_state["pipeline_result"] = result
                st.success("✅ Pipeline Executed Successfully!")
            else:
                st.error(f"❌ Server Error {response.status_code}: {response.text}")

        except Exception as e:
            st.error(f"❌ Backend Connection Error: {str(e)}")

# ---------------------------------------------------------
# 5. Output Tabs Display
# ---------------------------------------------------------
if "pipeline_result" in st.session_state:
    res = st.session_state["pipeline_result"]
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📝 Transcripts", 
        "📊 Summary & Minutes", 
        "✅ Decisions & Action Items", 
        "🚩 Review Flags"
    ])
    
    with tab1:
        col_r, col_f = st.columns(2)
        with col_r:
            st.subheader("Raw Transcript (Whisper)")
            st.text_area("Raw", res.get("raw_transcript", ""), height=250, label_visibility="collapsed")
            st.download_button("📥 Download raw_transcript.txt", res.get("raw_transcript", ""), "raw_transcript.txt")
        with col_f:
            st.subheader("Refined Transcript (Glossary Applied)")
            st.text_area("Refined", res.get("refined_transcript", ""), height=250, label_visibility="collapsed")
            st.download_button("📥 Download refined_transcript.txt", res.get("refined_transcript", ""), "refined_transcript.txt")

    with tab2:
        st.subheader("📋 Executive Summary")
        st.info(res.get("summary", "No summary generated."))
        st.subheader("📌 Topic Minutes")
        for item in res.get("minutes", []):
            st.markdown(f"**• {item.get('topic', 'Topic')}**")
            st.write(item.get("text", ""))

    with tab3:
        col_d, col_a = st.columns(2)
        with col_d:
            st.subheader("🎯 Decisions")
            st.dataframe(pd.DataFrame(res.get("decisions", [])), use_container_width=True, hide_index=True)
        with col_a:
            st.subheader("⚡ Action Tasks")
            st.dataframe(pd.DataFrame(res.get("tasks", [])), use_container_width=True, hide_index=True)

    with tab4:
        st.subheader("🚩 Audit Flags & Code Overrules")
        st.dataframe(pd.DataFrame(res.get("flags", [])), use_container_width=True, hide_index=True)
        st.download_button("📥 Download Record (JSON)", json.dumps(res, indent=2), "meeting_record.json", "application/json")
