import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")  # Make sure this exists in your .env

if not api_key:
    raise ValueError("Missing GEMINI_API_KEY in .env")

genai.configure(api_key=api_key)

# Initialize model
model = genai.GenerativeModel(model_name="gemini-2.0-flash")

# Send a request
response = model.generate_content(
    contents="Hello Gemini! Does your API integration work?",
    generation_config={"temperature": 0.2, "max_output_tokens": 150}
)

# Print the result
print("Gemini replies:", response.text)
