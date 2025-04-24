# main.py

import os, uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai
from typing import List, Dict, Literal

# ─── 1) Load env & configure Gemini ─────────────────────────────────────────────
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY in .env")

genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel(model_name="gemini-2.0-flash")

# ─── 2) In-memory stores ────────────────────────────────────────────────────────
sessions: Dict[str, List[Dict[str, str]]] = {}
# Global config
supported_providers = ["gemini", "openai", "claude"]
active_provider: str = "gemini"
generation_config = {
    "temperature": 0.2,
    "max_output_tokens": 150
}

# ─── 3) Schemas ─────────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str

class ChatResponse(BaseModel):
    session_id: str
    reply: str
    history: List[Dict[str, str]]

class SessionInfo(BaseModel):
    session_id: str

class ConfigRequest(BaseModel):
    provider: Literal["gemini","openai","claude"]
    temperature: float | None = None
    max_output_tokens: int | None = None

class ConfigResponse(BaseModel):
    provider: str
    temperature: float
    max_output_tokens: int

# ─── 4) FastAPI app ────────────────────────────────────────────────────────────
app = FastAPI()

# 4a) Create a new session
@app.post("/sessions", response_model=SessionInfo)
async def create_session():
    sid = str(uuid.uuid4())
    sessions[sid] = []
    return SessionInfo(session_id=sid)

# 4b) List all sessions
@app.get("/sessions", response_model=List[SessionInfo])
async def list_sessions():
    return [SessionInfo(session_id=sid) for sid in sessions]

# 4c) Fetch history for one session
@app.get("/sessions/{session_id}", response_model=List[Dict[str, str]])
async def get_session(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return sessions[session_id]

# 4d) List available providers
@app.get("/models", response_model=List[str])
async def get_models():
    return supported_providers

# 4e) Update config (provider, temperature, max tokens)
@app.patch("/config", response_model=ConfigResponse)
async def update_config(cfg: ConfigRequest):
    global active_provider, generation_config
    if cfg.provider not in supported_providers:
        raise HTTPException(status_code=400, detail="Unsupported provider")
    active_provider = cfg.provider
    if cfg.temperature is not None:
        generation_config["temperature"] = cfg.temperature
    if cfg.max_output_tokens is not None:
        generation_config["max_output_tokens"] = cfg.max_output_tokens
    return ConfigResponse(
        provider=active_provider,
        temperature=generation_config["temperature"],
        max_output_tokens=generation_config["max_output_tokens"]
    )

# 4f) Chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    # Determine session
    sid = req.session_id or str(uuid.uuid4())
    if sid not in sessions:
        sessions[sid] = []

    # Append user message
    sessions[sid].append({"role": "user", "content": req.message})

    # Route to the active provider
    try:
        if active_provider == "gemini":
            resp = gemini_model.generate_content(
                contents=req.message,
                generation_config=generation_config
            )
            ai_reply = resp.text

        else:
            # Placeholder for other providers
            raise NotImplementedError(f"{active_provider} integration not yet implemented.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {e}")

    # Append assistant reply
    sessions[sid].append({"role": "assistant", "content": ai_reply})

    return ChatResponse(session_id=sid, reply=ai_reply, history=sessions[sid])

# 4g) Health check
@app.get("/health")
async def health():
    return {"status": "ok"}
