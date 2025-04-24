# backend.py
from fastapi import FastAPI, Request
from pydantic import BaseModel
from flask import jsonify, request
from agents import  agent_router# Import agent handling functions
from utils import get_chat_history, add_to_history  # Helper functions
from config import MODEL_NAME  # Model selection config

# FastAPI setup
app = FastAPI()

class UserQuery(BaseModel):
    text: str
    location: str = None

@app.post("/chat")
async def chat(query: UserQuery):
    try:
        # Get the reply from the appropriate agent
        reply = agent_router(query.text, query.location)
        return {"reply": reply}
    except Exception as e:
        return {"error": str(e)}

@app.post("/reset")
def reset():
    global History
    History = []
    session.clear()
    return jsonify({"status": "Session cleared."})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
