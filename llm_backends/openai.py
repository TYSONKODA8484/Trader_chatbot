# llm_backends/openai.py

import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def chat(prompt: str, config: dict) -> str:
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user",   "content": prompt}
    ]
    completion = client.chat.completions.create(
        model=config.get("model", "gpt-3.5-turbo"),
        messages=messages,
        temperature=config["temperature"],
        max_tokens=config["max_output_tokens"],
    )
    return completion.choices[0].message.content.strip()
