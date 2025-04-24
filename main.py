import os
import uuid
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import List, Dict, Literal

# Import LLM adapters
from llm_backends.gemini import chat as gemini_chat
from llm_backends.openai import chat as openai_chat
from llm_backends.claude import chat as claude_chat
import google.generativeai as genai

# ─── Load environment ───
load_dotenv()

# ─── Global state ───
sessions: Dict[str, List[Dict[str, str]]] = {}  # session_id -> history
supported_providers = ["gemini", "openai", "claude"]
active_provider = "gemini"
generation_config = {
    "temperature": 0.2,
    "max_output_tokens": 150
}

# ─── App ───
app = FastAPI()

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

@app.post("/sessions", response_model=SessionInfo)
async def create_session():
    sid = str(uuid.uuid4())
    sessions[sid] = []
    return SessionInfo(session_id=sid)

@app.get("/sessions")
async def list_sessions():
    return [
        {"session_id": sid} for sid in sessions
    ]

@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"session_id": session_id, "history": sessions[session_id]}

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

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    sid = req.session_id or str(uuid.uuid4())
    if sid not in sessions:
        sessions[sid] = []

    sessions[sid].append({"role": "user", "content": req.message})

    try:
        if active_provider == "gemini":
            if not os.getenv("GEMINI_API_KEY"):
                ai_reply = "Gemini API key missing. Please set it in .env"
            else:
                ai_reply = gemini_chat(req.message, generation_config)

        elif active_provider == "openai":
            if not os.getenv("OPENAI_API_KEY"):
                ai_reply = "OpenAI API key missing. Please set it in .env"
            else:
                ai_reply = openai_chat(req.message, generation_config)

        elif active_provider == "claude":
            if not os.getenv("ANTHROPIC_API_KEY"):
                ai_reply = "Anthropic API key missing. Please set it in .env"
            else:
                ai_reply = claude_chat(req.message, generation_config)
        else:
            ai_reply = "Unsupported provider."

    except Exception as e:
        ai_reply = f"Error with {active_provider} provider: {e}"

    sessions[sid].append({"role": "assistant", "content": ai_reply})
    return ChatResponse(session_id=sid, reply=ai_reply, history=sessions[sid])

@app.post("/chat/stream")
async def stream_chat(req: ChatRequest):
    sid = req.session_id or str(uuid.uuid4())
    if sid not in sessions:
        sessions[sid] = []

    sessions[sid].append({"role": "user", "content": req.message})

    def format_event(data):
        return f"data: {data}\n\n"

    async def token_stream():
        yield format_event("[thinking...]")
        response = genai.GenerativeModel("gemini-2.0-flash").generate_content(
            contents=req.message,
            generation_config=generation_config,
            stream=True
        )
        full_text = ""
        async for chunk in response:
            part = chunk.text
            full_text += part
            yield format_event(part)
            await asyncio.sleep(0.01)
        sessions[sid].append({"role": "assistant", "content": full_text})

    return StreamingResponse(token_stream(), media_type="text/event-stream")

@app.get("/health")
async def health():
    return {"status": "ok"}