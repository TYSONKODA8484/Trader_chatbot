from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_session import Session
import google.generativeai as genai
import openai
import os
import secrets
from dotenv import load_dotenv
from PIL import Image
import io
import PyPDF2
import pandas as pd

# --- Load Environment ---
load_dotenv()

# --- Initialize Flask App ---
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = "./flask_session_dir"
app.config["SESSION_PERMANENT"] = False
Session(app)
CORS(app, supports_credentials=True)

# --- Global Memory ---
History = []

# --- Initialize Models ---
current_model = "gemini"

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

# --- Model Configuration and Switching ---
def set_model(model_name):
    global current_model
    if model_name == "gemini":
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        if not GEMINI_API_KEY:
            return "API key for Google Gemini is missing. Please provide the API key in the environment variables."
        genai.configure(api_key=GEMINI_API_KEY)
        current_model = "gemini"
    elif model_name == "openai":
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        if not OPENAI_API_KEY:
            return "API key for OpenAI is missing. Please provide the API key in the environment variables."
        openai.api_key = OPENAI_API_KEY
        current_model = "openai"
    else:
        return "Invalid model selected. Choose 'gemini' or 'openai'."
    return f"Model switched to {model_name.capitalize()} successfully!"

# --- Generate Model Response ---
def generate_with_gemini(prompt):
    try:
        response = genai.GenerativeModel("gemini-2.0-flash").generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error with Gemini model: {e}"

def generate_with_openai(prompt):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",  # or "gpt-3.5-turbo", "gpt-4" based on model
            prompt=prompt,
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.7,
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Error with OpenAI model: {e}"

# --- Chat Endpoint ---
@app.route("/chat", methods=["POST"])
def chat():
    text = request.form.get("text", "")
    image_file = request.files.get("image")
    pdf_file = request.files.get("pdf")
    csv_file = request.files.get("csv")
    user_location = request.form.get("location")

    image_bytes = image_file.read() if image_file else None
    pdf_bytes = pdf_file.read() if pdf_file else None
    csv_bytes = csv_file.read() if csv_file else None

    reply = agent_router(text, image_bytes, pdf_bytes, csv_bytes, user_location)
    return jsonify({"reply": reply})

# --- Agent Router ---
def agent_router(text="", image_bytes=None, pdf_bytes=None, csv_bytes=None, user_location=None):
    # Add logic to handle different types of inputs here
    if image_bytes:
        return "Image received, processing..."  # Placeholder logic for image
    elif text:
        return "Text received: " + text
    else:
        return "Please provide input."

# --- Reset Session ---
@app.route("/reset", methods=["POST"])
def reset():
    global History
    History = []
    session.clear()
    return jsonify({"status": "Session cleared."})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
