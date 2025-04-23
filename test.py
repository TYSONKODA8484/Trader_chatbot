import requests

payload = {"message": "Hello! What makes FastAPI so powerful?", "history": []}
res = requests.post("http://127.0.0.1:8000/chat", json=payload)
print(res.json())
