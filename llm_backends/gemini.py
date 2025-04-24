# llm_backends/gemini.py
import os, google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel(model_name="gemini-2.0-flash")

def chat(prompt: str, config: dict) -> str:
    return model.generate_content(contents=prompt, generation_config=config).text
