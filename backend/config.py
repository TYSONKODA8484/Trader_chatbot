# config.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration for model switching
MODEL_NAME = os.getenv("MODEL_NAME", "gemini")  # Default to Gemini
