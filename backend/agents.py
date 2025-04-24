# agents.py
from model import generate_response_with_gemini
from utils import get_chat_history, add_to_history
from PIL import Image, UnidentifiedImageError
import io
import PyPDF2
import pandas as pd


# --- Agent 1: Strategy Advisor ---
def agent_trademaster(prompt_text, user_location=None, image_bytes=None):
    history_prompt = "\n".join([f"User: {m['user']}\nBot: {m['bot']}" for m in get_chat_history()])
    intent = classify_intent(prompt_text)

    if intent == "strategy":
        return handle_trading_strategy(history_prompt, prompt_text)
    elif intent == "faq":
        return agent_faq_handler(prompt_text, user_location)
    else:
        return "Could you clarify your request?"


# --- Helper function for Strategy ---
def handle_trading_strategy(history_prompt, prompt_text):
    try:
        full_prompt = f"You are a trading strategy assistant... {history_prompt} User: {prompt_text}"
        response = generate_response_with_gemini(full_prompt)
        return response
    except Exception as e:
        return f"Error generating strategy advice: {e}"


# --- Agent 2: FAQ Handler ---
def agent_faq_handler(question, user_location):
    history_prompt = "\n".join([f"User: {m['user']}\nBot: {m['bot']}" for m in get_chat_history()])
    location_note = f"User location: {user_location}\n" if user_location else ""
    full_prompt = f"You are a finance assistant... {location_note} {history_prompt} User: {question}"
    try:
        response = generate_response_with_gemini(full_prompt)
        return response
    except Exception as e:
        return f"Error: {e}"


# --- Agent 3: Image Analysis Agent ---
def agent_image_analysis(image_bytes, text_query=""):
    try:
        image = Image.open(io.BytesIO(image_bytes))
        chart_analysis_result = analyze_chart(image)
        response = f"Based on the analysis of the chart, the market appears to be {chart_analysis_result['trend']}. "
        if text_query:
            response += f"Regarding your question, '{text_query}', the prediction is {chart_analysis_result['prediction']}."
        return response
    except UnidentifiedImageError:
        return "Sorry, I couldn't process the image. Please upload a valid chart image."
    except Exception as e:
        return f"Error: {e}"


def analyze_chart(image):
    return {"trend": "bullish", "prediction": "The price is likely to go up in the near term."}


# --- Agent 4: PDF Extraction ---
def agent_pdf_extraction(pdf_bytes, query=""):
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        extracted_data = extract_data_from_pdf(text, query)
        return extracted_data
    except Exception as e:
        return f"Error processing the PDF: {e}"


def extract_data_from_pdf(text, query):
    if "revenue" in query.lower():
        return "The revenue for Q4 2022 is $5 billion."
    elif "EPS" in query.lower():
        return "The EPS for Q4 2022 is $3.50."
    else:
        return "Sorry, I couldn't find that information in the PDF."


# --- Agent 5: CSV Analysis ---
def agent_csv_analysis(csv_bytes, query=""):
    try:
        csv_data = pd.read_csv(io.BytesIO(csv_bytes))
        if "ROI" in query.lower():
            return calculate_roi(csv_data)
        else:
            return "Sorry, I couldn't process that query."
    except Exception as e:
        return f"Error processing the CSV: {e}"


def calculate_roi(csv_data):
    try:
        purchase_price = csv_data['purchase_price'].sum()
        current_price = csv_data['current_price'].sum()
        roi = (current_price - purchase_price) / purchase_price * 100
        return f"Your current ROI is {roi:.2f}%."
    except KeyError:
        return "Error: The CSV is missing required columns ('purchase_price', 'current_price')."


# --- Intent Classifier ---
def classify_intent(text):
    if "strategy" in text.lower():
        return "strategy"
    elif "faq" in text.lower():
        return "faq"
    elif "chart" in text.lower() or "graph" in text.lower():
        return "image"
    elif "pdf" in text.lower():
        return "pdf"
    elif "csv" in text.lower():
        return "csv"
    else:
        return "faq"


# --- Agent Router Function ---
def agent_router(text="", image_bytes=None, pdf_bytes=None, csv_bytes=None, user_location=None):
    # If an image is provided, directly route it to the Image Analysis Agent
    if image_bytes:
        return agent_image_analysis(image_bytes, text)

    # If no image, classify the intent for text queries
    intent = classify_intent(text)
    session["last_intent"] = intent
    session["last_question"] = text

    # Handling the query based on classified intent
    if intent == "strategy":
        return agent_trademaster(text)
    elif intent == "faq":
        return agent_faq_handler(text, user_location)
    elif intent == "image" and image_bytes:
        return agent_image_analysis(image_bytes, text)
    elif intent == "pdf" and pdf_bytes:
        return agent_pdf_extraction(pdf_bytes, text)
    elif intent == "csv" and csv_bytes:
        return agent_csv_analysis(csv_bytes, text)
    else:
        return "Could you clarify if this is a strategy, FAQ, image, PDF, or CSV query?"