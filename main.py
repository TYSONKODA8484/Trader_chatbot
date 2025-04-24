import os
import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import List, Dict, Literal

# Import LLM adapters
from llm_backends.gemini import chat as gemini_chat
from llm_backends.openai import chat as openai_chat
from llm_backends.claude import chat as claude_chat

# ─── Load environment variables ─────────────────────────────────────────────────
load_dotenv()  # expects .env with GEMINI_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY

# ─── In-memory session store & configuration ───────────────────────────────────
sessions: Dict[str, List[Dict[str, str]]] = {}
supported_providers = ["gemini", "openai", "claude"]
active_provider: str = "gemini"
generation_config = {
    "temperature": 0.2,
    "max_output_tokens": 150
}

# ─── Pydantic schemas ─────────────────────────────────────────────────────────
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

# ─── FastAPI app initialization ─────────────────────────────────────────────
app = FastAPI()

# 1️⃣ Create a new session
@app.post("/sessions", response_model=SessionInfo)
async def create_session():
    sid = str(uuid.uuid4())
    sessions[sid] = []
    return SessionInfo(session_id=sid)

# 2️⃣ List all sessions
@app.get("/sessions", response_model=List[SessionInfo])
async def list_sessions():
    return [SessionInfo(session_id=sid) for sid in sessions]

# 3️⃣ Fetch history for a session
@app.get("/sessions/{session_id}", response_model=List[Dict[str, str]])
async def get_session(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return sessions[session_id]

# 4️⃣ List available providers
@app.get("/models", response_model=List[str])
async def get_models():
    return supported_providers

# 5️⃣ Update runtime configuration
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

# 6️⃣ Chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    sid = req.session_id or str(uuid.uuid4())
    if sid not in sessions:
        sessions[sid] = []
    sessions[sid].append({"role": "user", "content": req.message})

    try:
        if active_provider == "claude":
            key = os.getenv("ANTHROPIC_API_KEY")
            if not key:
                ai_reply = (
                    "Anthropic API key is missing. "
                    "Please set ANTHROPIC_API_KEY in your .env to use Claude."
                )
            else:
                try:
                    ai_reply = claude_chat(req.message, generation_config)
                except Exception as e:
                    err = str(e)
                    if "authentication_error" in err or "invalid x-api-key" in err:
                        ai_reply = (
                            "Anthropic API key is invalid or expired. "
                            "Please verify your ANTHROPIC_API_KEY and try again."
                        )
                    else:
                        ai_reply = f"Error calling Claude: {e}"

        # … your existing gemini & openai branches …

    except Exception as e:
        ai_reply = f"Error with {active_provider} provider: {e}"

    sessions[sid].append({"role": "assistant", "content": ai_reply})
    return ChatResponse(session_id=sid, reply=ai_reply, history=sessions[sid])


# 7️⃣ Health check
@app.get("/health")
async def health():
    return {"status": "ok"}
