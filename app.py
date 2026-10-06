import streamlit as st
import requests
import time
import pandas as pd

# ---------------------------------------------------------
# 1. Page Config & CSS Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="AURA | AI Meeting Intelligence",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Professional UI Styling
st.markdown("""
<style>
    /* Dark Theme Container Polish */
    .main {
        background-color: #0e1117;
    }
    
    /* Header Card */
    .header-card {
        background: linear-gradient(135deg, #1e2640 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    }
    
    /* Metrics Custom Display */
    .metric-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }
    .metric-value {
        font-size: 22px;
        font-weight: 700;
        color: #38bdf8;
    }
    .metric-label {
        font-size: 12px;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Custom Primary Button */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #2563eb 0%, #7c3aed 100%);
        color: white;
        border: none;
        padding: 14px 28px;
        font-size: 16px;
        font-weight: 600;
        border-radius: 12px;
        width: 100%;
        box-shadow: 0 4px 14px 0 rgba(124, 58, 237, 0.39);
        transition: all 0.3s ease;
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px 0 rgba(124, 58, 237, 0.55);
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. Sidebar & Backend Connection Config
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/isometric-headers/100/microphone.png", width=64)
    st.title("Settings & Status")
    
    st.markdown("---")
    st.subheader("🌐 Serverless API Backend")
    backend_url = st.text_input(
        "API Endpoint URL",
        value="https://your-modal-app.modal.run/process",
        help="Modal.com ya RunPod Serverless API ka endpoint paste karein"
    )
    
    st.markdown("---")
    st.subheader("⚡ Model Pipeline Architecture")
    st.caption("• **STT:** NVIDIA Canary-1B / Whisper")
    st.caption("• **LLM 1:** Qwen-2.5-7B (Summarizer)")
    st.caption("• **LLM 2:** Llama-3.1-8B (Action Extractor)")
    
    st.markdown("---")
    st.markdown("<div style='text-align: center; color: #64748b; font-size: 12px;'>Hybrid Architecture • Frontend on Streamlit Cloud</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. Main Header Section
# ---------------------------------------------------------
st.markdown("""
<div class="header-card">
    <h1 style="margin:0; font-size: 32px; color: #f8fafc;">🎙️ AURA Meeting Intelligence</h1>
    <p style="margin-top:8px; color: #94a3b8; font-size: 15px;">
        Automated Speech-to-Text & Multi-LLM Executive Insights Pipeline
    </p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. File Upload & Input Area
# ---------------------------------------------------------
col_input, col_info = st.columns([2, 1])

with col_input:
    uploaded_file = st.file_uploader(
        "Upload Meeting Audio File",
        type=["wav", "mp3", "m4a", "flac"],
        help="Supported formats: WAV, MP3, M4A, FLAC"
    )

with col_info:
    st.markdown("<br>", unsafe_allow_html=True)
    if uploaded_file is not None:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{round(uploaded_file.size / (1024*1024), 2)} MB</div>
            <div class="metric-label">Audio File Size</div>
        </div>
        """, unsafe_allow_html=True)
        st.audio(uploaded_file)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 5. Process Pipeline Button & Backend Execution
# ---------------------------------------------------------
if st.button("🚀 Process Pipeline (Run STT + Dual LLMs)"):
    if uploaded_file is None:
        st.warning("⚠️ Kripya pehle koi audio file upload karein!")
    else:
        with st.spinner("⚡ Sending audio to GPU Serverless Backend..."):
            start_time = time.time()
            
            # --- BACKEND API CALL (MODAL / RUNPOD) ---
            try:
                # files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                # response = requests.post(backend_url, files=files, timeout=300)
                # result = response.json()
                
                # Testing Simulation (Jab tak Modal/RunPod API ready na ho)
                time.sleep(3)
                result = {
                    "status": "success",
                    "transcript": "Good morning team. Today we reviewed the Q3 financial roadmap, confirmed deployment of our AI Assistant pipeline on Modal.com serverless GPU, and assigned Rahul to run benchmark tests against Canary 1B.",
                    "summary": "### 📋 Executive Summary\n- **Q3 Roadmap:** Financial targets for Q3 were formally approved.\n- **Architecture Upgrade:** Shifted from local HF Spaces to Hybrid Architecture (Streamlit Cloud + Modal Serverless API).\n- **Infrastructure Cost:** GPU compute cost reduced to $0 while idle.",
                    "action_items": [
                        {"Task": "Benchmark Canary-1B vs Whisper", "Assignee": "Rahul", "Priority": "High", "Status": "Pending"},
                        {"Task": "Deploy Modal.com Endpoint", "Assignee": "Backend Team", "Priority": "Critical", "Status": "In Progress"},
                        {"Task": "Finalize Q3 Budget Docs", "Assignee": "Finance", "Priority": "Medium", "Status": "Completed"}
                    ]
                }
                
                elapsed = round(time.time() - start_time, 2)
                st.success(f"✅ Pipeline Executed Successfully in {elapsed}s!")
                
                # Save into Session State to avoid reload loss
                st.session_state["pipeline_output"] = result

            except Exception as e:
                st.error(f"❌ Backend Connection Error: {str(e)}")

# ---------------------------------------------------------
# 6. Structured Tab Output
# ---------------------------------------------------------
if "pipeline_output" in st.session_state:
    data = st.session_state["pipeline_output"]
    
    st.markdown("<br>", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs([
        "📝 Speech-to-Text Transcript", 
        "📊 Executive Summary (LLM 1)", 
        "✅ Action Matrix (LLM 2)"
    ])
    
    with tab1:
        st.subheader("Raw Audio Transcript")
        st.text_area(
            label="Transcript Output",
            value=data["transcript"],
            height=200,
            label_visibility="collapsed"
        )
        st.download_button(
            "📥 Download Transcript",
            data=data["transcript"],
            file_name="meeting_transcript.txt",
            mime="text/plain"
        )

    with tab2:
        st.markdown(data["summary"])
        st.download_button(
            "📥 Download Summary",
            data=data["summary"],
            file_name="executive_summary.md",
            mime="text/markdown"
        )

    with tab3:
        st.subheader("Decisions & Action Items")
        df_actions = pd.DataFrame(data["action_items"])
        st.dataframe(
            df_actions,
            use_container_width=True,
            hide_index=True
        )
