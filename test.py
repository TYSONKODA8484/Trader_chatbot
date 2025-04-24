import requests

# 1. Create a new session
resp = requests.post("http://127.0.0.1:8000/sessions")
resp.raise_for_status()
session_id = resp.json()["session_id"]
print("Created session:", session_id)

# 2. Send a chat message
payload = {
    "session_id": session_id,
    "message": "Hello! What makes FastAPI so powerful?"
}
res = requests.post("http://127.0.0.1:8000/chat", json=payload)
res.raise_for_status()

# 3. Print the full response (includes reply + history)
print(res.json())
