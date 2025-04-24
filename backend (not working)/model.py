# model.py
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration: Get the Gemini API key from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def initialize_gemini():
    # Initialize the Gemini model
    genai.configure(api_key=GEMINI_API_KEY)
    return genai.GenerativeModel("gemini-2.0-flash")

# Function to generate response using Gemini
def generate_response_with_gemini(text):
    model = initialize_gemini()
    try:
        response = model.generate_content(text)
        return response.text.strip()
    except Exception as e:
        return f"Error with Gemini model: {e}"
