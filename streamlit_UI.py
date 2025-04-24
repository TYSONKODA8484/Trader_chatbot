import streamlit as st
import requests
from PIL import Image
import base64

# Streamlit page configuration
st.set_page_config(page_title="💹 Trading Assistant", layout="centered")
st.title("💹 Trading Assistant Chatbot")

API_URL = "http://127.0.0.1:5000/chat"  # Make sure this points to your Flask API
RESET_URL = "http://127.0.0.1:5000/reset"
MODEL_SELECTION_URL = "http://127.0.0.1:5000/select_model"  # Endpoint for switching models

# Initialize session state for chat history and model selection
if "history" not in st.session_state:
    st.session_state.history = []

if "model" not in st.session_state:
    st.session_state.model = "gemini"  # Default model

# Sidebar to select model
with st.sidebar:
    st.header("Model Selection")
    model_choice = st.selectbox("Choose LLM Model", ["Google Gemini", "OpenAI GPT", "Anthropic Claude"])
    if st.button("Switch Model"):
        model_mapping = {
            "Google Gemini": "gemini",
            "OpenAI GPT": "openai",
            "Anthropic Claude": "claude"
        }
        model_response = requests.post(MODEL_SELECTION_URL, json={"model_name": model_mapping[model_choice]})
        model_status = model_response.json().get("status", "Model change failed.")
        st.success(model_status)

    if st.button("🔁 Reset Conversation"):
        requests.post(RESET_URL)
        st.session_state.history.clear()
        st.success("Chat history cleared.")

# Chat Container
chat_container = st.container()
with chat_container:
    for item in st.session_state.history:
        with st.chat_message("user"):
            st.markdown(item["user"])
        with st.chat_message("assistant"):
            st.markdown(item["bot"])

# Input area for user messages
with st.chat_message("user"):
    with st.form("chat_form", clear_on_submit=True):
        # User text input
        text = st.text_input("Message", placeholder="Type your question about trading...", label_visibility="collapsed")

        # Optional location input (if needed for the trading assistant)
        location = st.text_input("Your City (optional)", placeholder="e.g. New York", key="location_input")

        # File upload for image (e.g., stock chart)
        uploaded_image = st.file_uploader("Upload stock chart image (optional)", type=["jpg", "jpeg", "png"])

        # File upload for PDF (e.g., financial report)
        uploaded_pdf = st.file_uploader("Upload PDF document (optional)", type=["pdf"])

        # File upload for CSV (e.g., trading history or backtest data)
        uploaded_csv = st.file_uploader("Upload CSV file (optional)", type=["csv"])

        submitted = st.form_submit_button("Send")

if submitted:
    # Prepare the data and files to send to the API
    files = {
        "image": (uploaded_image.name, uploaded_image, uploaded_image.type) if uploaded_image else None,
        "pdf": (uploaded_pdf.name, uploaded_pdf, uploaded_pdf.type) if uploaded_pdf else None,
        "csv": (uploaded_csv.name, uploaded_csv, uploaded_csv.type) if uploaded_csv else None
    }
    data = {"text": text, "location": location, "model": st.session_state.model}

    try:
        # Send the request to the Trading Assistant Flask API
        response = requests.post(API_URL, data=data, files=files)
        bot_reply = response.json().get("reply", "(No reply from server)")
    except Exception as e:
        bot_reply = f"❌ Error: {e}"

    # Save the user message and bot reply to chat history
    st.session_state.history.append({"user": text or "(image/pdf/csv only)", "bot": bot_reply})

    # Refresh the chat Frontend
    st.rerun()
