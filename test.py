import requests

# Define the base URL of the Flask app
BASE_URL = "http://127.0.0.1:5000"

# Function to test the chat endpoint
def test_chat_endpoint(text, location=None):
    payload = {"text": text, "location": location}
    response = requests.post(f"{BASE_URL}/chat", data=payload)
    print(f"Response for '{text}': {response.json()['reply']}")
    return response.json()

# Function to test the reset endpoint
def test_reset_endpoint():
    response = requests.post(f"{BASE_URL}/reset")
    print(f"Reset Status: {response.json()['status']}")

# --- Testing the Finance Agents ---
print("Testing Agent 1: Strategy Advisor (Trading Ideas)\n")
# Example of a strategy-related query
test_chat_endpoint("What is the best strategy for trading stocks during a recession?")

print("\nTesting Agent 2: Financial FAQ (Market Regulation)\n")
# Example of a financial FAQ
test_chat_endpoint("What are the regulations on short selling in the US?")

# Testing with location provided for market regulations
print("\nTesting Agent 2 with Location (Regulatory Query)\n")
test_chat_endpoint("What is the tax rate for capital gains in India?", location="India")

# Testing Reset
print("\nTesting Reset Endpoint\n")
test_reset_endpoint()
