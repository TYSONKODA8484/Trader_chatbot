from flask import Flask, request, jsonify, session
from flask_session import Session
from flask_cors import CORS
import google.generativeai as genai
from PIL import Image, UnidentifiedImageError
import io
import PyPDF2
import pandas as pd
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
def agent_trademaster(prompt_text, user_location=None, image_bytes=None):
    """
    Unified agent to handle all trading-related queries, including strategies, sentiment, portfolio management, etc.
    """
    # 1. Gather conversation history
    history_prompt = "\n".join([f"User: {m['user']}\nBot: {m['bot']}" for m in get_chat_history()])

    # 2. Classify the user's query (using LLM or simple classification)
    intent = classify_intent(
        prompt_text)  # This should classify between 'strategy', 'faq', 'sentiment', 'portfolio', etc.

    # 3. Dynamically handle the response based on the query intent
    if intent == "strategy":
        # Trading strategy-related response
        full_prompt = (
            "You are a trading strategy assistant helping a user with queries.\\n"
            "Use context, prior prompts, and logic to suggest trading strategies based on market conditions.\\n"
            "Keep the advice clear, concise, and within 700 characters.\\n"
            f"{history_prompt}\\nUser: {prompt_text}"
        )
        return handle_trading_strategy(full_prompt)

    elif intent == "faq":
        # Pass the query to the existing FAQ agent for handling finance-related queries
        return agent_faq_handler(prompt_text, user_location)

    elif intent == "sentiment":
        # Perform sentiment analysis
        return sentiment_analysis(prompt_text)

    elif intent == "portfolio":
        # Handle portfolio-related queries
        return portfolio_management(prompt_text)

    elif intent == "tax":
        # Provide tax-related advice
        return tax_advisor(prompt_text, user_location)

    elif intent == "risk":
        # Provide risk management advice
        return risk_management(prompt_text)

    elif intent == "algo":
        # Handle algorithmic trading-related queries
        return algorithmic_trading(prompt_text)

    else:
        return "Could you clarify your request? I can assist with trading strategies, portfolio management, tax advice, etc."


# --- Helper functions for each intent type ---
def handle_trading_strategy(full_prompt):
    try:
        # Query LLM to generate the strategy advice
        response = model.generate_content(full_prompt, generation_config={"max_output_tokens": 250})
        reply = response.text.strip()[:700]
        add_to_history(full_prompt, reply)
        return reply
    except Exception as e:
        return f"Error generating strategy advice: {e}"


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


# --- Image Analysis Agent (Agent 1) ---
def agent_image_analysis(image_bytes, text_query=""):
    """
    Processes image input (like a stock chart) and gives predictions about market trends.
    """
    try:
        # Open the image (chart, graph) and analyze it
        image = Image.open(io.BytesIO(image_bytes))

        # Perform chart analysis to predict market trend or analyze data
        chart_analysis_result = analyze_chart(image)  # Replace with your analysis logic

        # Combine analysis results with optional text query (if any)
        response = f"Based on the analysis of the chart, the market appears to be {chart_analysis_result['trend']}. "

        if text_query:
            response += f"Regarding your question, '{text_query}', the prediction is {chart_analysis_result['prediction']}."

        return response

    except UnidentifiedImageError:
        return "Sorry, I couldn't process the image. Please upload a valid chart image."
    except Exception as e:
        return f"Error: {e}"


# Sample helper function for chart analysis (custom logic needed)
def analyze_chart(image):
    """
    Custom function to analyze the chart (this can include identifying patterns, trends, etc.)
    """
    # Example of analyzing trends (you can use computer vision techniques here)
    return {
        "trend": "bullish",  # Could be 'bullish', 'bearish', or 'neutral'
        "prediction": "The price is likely to go up in the near term."
    }


# --- Agent 4: PDF Extraction Agent ---
def agent_pdf_extraction(pdf_bytes, query=""):
    try:
        # Extract text from PDF
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

        # Perform data extraction based on the query
        extracted_data = extract_data_from_pdf(text, query)

        return extracted_data

    except Exception as e:
        return f"Error processing the PDF: {e}"


def extract_data_from_pdf(text, query):
    """
    Extract relevant data from the PDF based on the trader's query.
    For simplicity, this is a demo, and you'd need to implement specific extraction based on PDF content.
    """
    if "revenue" in query.lower():
        return "The revenue for Q4 2022 is $5 billion."
    elif "EPS" in query.lower():
        return "The EPS for Q4 2022 is $3.50."
    else:
        return "Sorry, I couldn't find that information in the PDF."


# --- Agent 5: CSV Analysis Agent ---
def agent_csv_analysis(csv_bytes, query=""):
    try:
        # Read CSV file
        csv_data = pd.read_csv(io.BytesIO(csv_bytes))

        # Perform analysis based on the query
        if "ROI" in query.lower():
            return calculate_roi(csv_data)
        elif "backtest" in query.lower():
            return backtest_strategy(csv_data)
        elif "portfolio" in query.lower():
            return analyze_portfolio(csv_data)
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


def backtest_strategy(csv_data):
    try:
        # Example: Simple moving average strategy backtest
        csv_data['SMA_20'] = csv_data['close'].rolling(window=20).mean()
        buy_signals = csv_data[csv_data['close'] > csv_data['SMA_20']]
        sell_signals = csv_data[csv_data['close'] < csv_data['SMA_20']]

        return f"Backtest Results: {len(buy_signals)} buy signals, {len(sell_signals)} sell signals."
    except KeyError:
        return "Error: The CSV is missing required columns ('close')."


def analyze_portfolio(csv_data):
    try:
        portfolio_value = (csv_data['shares'] * csv_data['current_price']).sum()
        return f"Your portfolio is currently worth ${portfolio_value:,.2f}."
    except KeyError:
        return "Error: The CSV is missing required columns ('shares', 'current_price')."


# --- Intent Classifier (LLM) ---
def classify_intent(text):
    prompt = (
        "You are an intent classifier for a trading assistant.\\n"
        "Classify the user query as one of the following types:\\n"
        "- 'strategy': for queries asking about trading ideas, risk, indicators, strategies, etc.\\n"
        "- 'faq': for general questions about finance, regulations, market basics, tax laws, etc.\\n"
        "- 'image': if the user provides a chart or graph to analyze.\\n"
        "- 'pdf': if the user uploads a PDF file for analysis.\\n"
        "- 'csv': if the user uploads a CSV file for analysis.\\n"
        "Return one word: 'strategy', 'faq', 'image', 'pdf', or 'csv'.\\n"
        f"User: {text}"
    )
    try:
        response = model.generate_content(prompt)
        return response.text.strip().lower()
    except Exception as e:
        return "faq"  # Default to 'faq' in case of any error


# --- Router ---
def agent_router(text="", image_bytes=None, pdf_bytes=None, csv_bytes=None, user_location=None):
    # If an image is provided, directly route it to the Image Analysis Agent
    if image_bytes:
        # Call the image analysis agent directly and bypass intent classification
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

# --- Chat Endpoint ---
@app.route("/chat", methods=["POST"])
def chat():
    text = request.form.get("text", "")
    image_file = request.files.get("image")
    pdf_file = request.files.get("pdf")
    csv_file = request.files.get("csv")
    user_location = request.form.get("location")

    # Process files based on intent and route them accordingly
    image_bytes = image_file.read() if image_file else None
    pdf_bytes = pdf_file.read() if pdf_file else None
    csv_bytes = csv_file.read() if csv_file else None

    # Handle the query and get the appropriate response
    reply = agent_router(text, image_bytes, pdf_bytes, csv_bytes, user_location)
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
