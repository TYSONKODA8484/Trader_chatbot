import os
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    # Key-check happens in main.py
    client = None
else:
    client = Anthropic(api_key=ANTHROPIC_API_KEY)

def chat(prompt: str, config: dict) -> str:
    if client is None:
        raise RuntimeError("Anthropic key not set")
    full_prompt = f"{HUMAN_PROMPT} {prompt}{AI_PROMPT}"
    resp = client.completions.create(
        model=config.get("model", "claude-2"),
        prompt=full_prompt,
        temperature=config["temperature"],
        max_tokens_to_sample=config["max_output_tokens"],
    )
    return resp.completion.strip()
