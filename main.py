from flask import Flask, request, jsonify, session
from flask_session import Session
from flask_cors import CORS
import google.generativeai as genai
from PIL import Image, UnidentifiedImageError
import io
from dotenv import load_dotenv
import os
import secrets

# --- Load Environment ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# --- App Setup ---
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = "./flask_session_dir"
app.config["SESSION_PERMANENT"] = False
Session(app)
CORS(app, supports_credentials=True)

# --- Global Memory ---
History = []

def get_chat_history():
    if "history" not in session:
        session["history"] = []
    return History

def add_to_history(user_msg, bot_msg):
    History.append({"user": user_msg, "bot": bot_msg})
    history = get_chat_history()
    history.append({"user": user_msg, "bot": bot_msg})
    session["history"] = history
    session["last_question"] = user_msg

# --- Location Extraction --- (Optional for Agent 2)
def extract_location(text):
    history_prompt = "\n".join([f"User: {m['user']}\nBot: {m['bot']}" for m in get_chat_history()])
    prompt = (
        "You are a location extractor for a finance assistant chatbot.\\n"
        "Extract the city or region the user is talking about based on the current message and previous conversations.\\n"
        "If unclear, return 'unknown'.\\n"
        f"Chat history:\n{history_prompt}\nUser: {text}"
    )
    try:
        response = model.generate_content(prompt)
        location = response.text.strip().split("\n")[0]
        return location if location.lower() != "unknown" else None
    except:
        return None


# --- Agent 1: Strategy Advisor ---
def agent_strategy_advice(prompt_text):
    history_prompt = "\n".join([f"User: {m['user']}\nBot: {m['bot']}" for m in get_chat_history()])
    full_prompt = (
        "You are a trading strategy assistant helping a user with queries.\\n"
        "Use context, prior prompts, and logic to suggest trading strategies based on market conditions.\\n"
        "Keep the advice clear, concise, and within 700 characters.\\n"
        f"{history_prompt}\\nUser: {prompt_text}"
    )
    try:
        response = model.generate_content(full_prompt, generation_config={"max_output_tokens": 250})
        reply = response.text.strip()[:700]
        add_to_history(prompt_text, reply)
        return reply
    except Exception as e:
        return f"Error: {e}"


# --- Agent 2: Financial FAQ Handler ---
def agent_faq_handler(question, user_location):
    history_prompt = "\n".join([f"User: {m['user']}\nBot: {m['bot']}" for m in get_chat_history()])
    location_note = f"User location: {user_location}\n" if user_location else ""
    prompt = (
        "You are a finance knowledge assistant for investors and traders.\\n"
        "Answer the user's questions based on context and their location if relevant.\\n"
        "Provide concise and informative responses in under 700 characters.\\n"
        f"{location_note}{history_prompt}\\nUser: {question}"
    )
    try:
        response = model.generate_content(prompt, generation_config={"max_output_tokens": 250})
        reply = response.text.strip()[:700]
        add_to_history(question, reply)
        return reply
    except Exception as e:
        return f"Error: {e}"


# --- Intent Classifier (LLM) ---
def classify_intent(text):
    prompt = (
        "You are an intent classifier for a trading assistant.\\n"
        "Classify the user query as one of the following types:\\n"
        "- 'strategy': for queries asking about trading ideas, risk, indicators, strategies, etc.\\n"
        "- 'faq': for general questions about finance, regulations, market basics, tax laws, etc.\\n"
        "Return only one word: 'strategy' or 'faq'.\\n"
        f"User: {text}"
    )
    try:
        response = model.generate_content(prompt)
        return response.text.strip().lower()
    except Exception as e:
        return "faq"  # Default to 'faq' in case of any error


# --- Router ---
def agent_router(text="", image_bytes=None, user_location=None):
    has_image = image_bytes is not None

    # Use the classify_intent function to determine the type of query (strategy or faq)
    intent = classify_intent(text)
    session["last_intent"] = intent
    session["last_question"] = text

    if intent == "strategy":
        return agent_strategy_advice(text)
    elif intent == "faq":
        return agent_faq_handler(text, user_location)
    else:
        return "Could you clarify if this is a strategy question or a general finance FAQ?"


# --- Chat Endpoint ---
@app.route("/chat", methods=["POST"])
def chat():
    text = request.form.get("text", "")
    if not text:
        return jsonify({"reply": "Please enter a query."})

    reply = agent_router(text)
    return jsonify({"reply": reply})

# --- Reset Session ---
@app.route("/reset", methods=["POST"])
def reset():
    global History
    History = []
    session.clear()
    return jsonify({"status": "Session cleared."})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
