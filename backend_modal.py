import modal
import os
import gc
import torch
from fastapi import UploadFile, File, Form

app_image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install("ffmpeg")
    .pip_install(
        "torch",
        "transformers",
        "accelerate",
        "bitsandbytes",
        "openai-whisper",
        "google-generativeai",
        "fastapi[standard]",
        "python-multipart"
    )
)

app = modal.App("meeting-assistant-backend", image=app_image)

def clear_vram():
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

@app.function(
    gpu="T4",
    timeout=600,
    secrets=[modal.Secret.from_name("gemini-secret")]
)
@modal.fastapi_endpoint(method="POST")
def process_audio(file: UploadFile = File(...), glossary: str = Form("")):
    import whisper
    import google.generativeai as genai

    # Temporary Audio Save
    temp_path = "/tmp/meeting.wav"
    with open(temp_path, "wb") as f:
        f.write(file.file.read())

    # --- Stage 1: Whisper STT ---
    stt_model = whisper.load_model("small", device="cuda")
    stt_result = stt_model.transcribe(temp_path)
    raw_transcript = stt_result["text"]
    del stt_model
    clear_vram()

    # --- Stage 2: Refinement & Glossary Applied ---
    refined_transcript = raw_transcript
    if glossary:
        terms = [t.strip() for t in glossary.split(",") if t.strip()]
        for term in terms:
            if term.lower() in raw_transcript.lower():
                refined_transcript += f"\n[Glossary verified: {term}]"

    # --- Stages 3, 4, 5, 6: Gemini Flash API Integration ---
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"""Analyze this transcript and output valid JSON only:
Transcript:
{raw_transcript}

Required JSON format:
{{
  "summary": "3 sentence summary",
  "minutes": [{{"topic": "Topic Name", "text": "Details"}}],
  "decisions": [{{"text": "Decision", "status": "Agreed", "cited_lines": [1]}}],
  "tasks": [{{"text": "Task description", "owner": "Name", "deadline": "Day", "cited_lines": [1]}}],
  "flags": [{{"type": "info", "description": "Verification status"}}]
}}"""

    response = gemini_model.generate_content(prompt)
    
    try:
        import json
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        parsed_json = json.loads(clean_text)
    except Exception as e:
        parsed_json = {
            "summary": "Extraction processing failed format verification.",
            "minutes": [], "decisions": [], "tasks": [], "flags": [{"type": "error", "description": str(e)}]
        }

    parsed_json["raw_transcript"] = raw_transcript
    parsed_json["refined_transcript"] = refined_transcript

    if os.path.exists(temp_path):
        os.remove(temp_path)

    return parsed_json
