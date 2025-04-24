import streamlit as st
import requests
import streamlit.components.v1 as components

# --- CONFIG ---
BASE_URL = "http://127.0.0.1:8000"

# --- SESSION STATE INIT ---
if "session_id" not in st.session_state:
    st.session_state.session_id = ""
    st.session_state.chat_history = []
    st.session_state.past_sessions = []

# --- TOP NAVBAR ---
st.markdown("""
    <style>
    .navbar {
        background-color: #0e1117;
        padding: 1rem;
        color: white;
        font-weight: bold;
        font-size: 1.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #333;
    }
    .settings-button {
        cursor: pointer;
        color: white;
        font-size: 1.2rem;
    }
    .message-user {
        background-color: #1e293b;
        color: white;
        padding: 10px;
        border-radius: 10px;
        margin: 5px;
        max-width: 70%;
        align-self: flex-end;
    }
    .message-bot {
        background-color: #f1f5f9;
        color: black;
        padding: 10px;
        border-radius: 10px;
        margin: 5px;
        max-width: 70%;
        align-self: flex-start;
    }
    .chat-container {
        display: flex;
        flex-direction: column;
    }
    </style>
    <div class="navbar">
        Trading Copilot
        <span class="settings-button" onclick="document.getElementById('settings-block').style.display='block'">
            ⚙️ Settings
        </span>
    </div>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.title("\U0001F4AC Chats")
model_provider = st.sidebar.selectbox("LLM Provider", ["gemini", "openai", "claude"], index=0)

if st.sidebar.button("➕ New Chat"):
    if st.session_state.session_id:
        st.session_state.past_sessions.append({
            "session_id": st.session_state.session_id,
            "history": st.session_state.chat_history.copy()
        })
    response = requests.post(f"{BASE_URL}/sessions")
    st.session_state.session_id = response.json()["session_id"]
    st.session_state.chat_history = []

# Show past sessions
st.sidebar.markdown("---")
st.sidebar.subheader("Past Chats")
for i, sess in enumerate(reversed(st.session_state.past_sessions)):
    with st.sidebar.expander(f"Chat {len(st.session_state.past_sessions) - i}"):
        for msg in sess["history"]:
            st.markdown(f"**{msg['role'].capitalize()}:** {msg['content']}")

# --- SETTINGS BLOCK (right top floating) ---
with st.container():
    with st.expander("⚙️ Settings", expanded=False):
        temperature = st.slider("Temperature", 0.0, 1.0, 0.2, 0.1)
        max_tokens = st.slider("Max Tokens", 50, 500, 150, 10)
        requests.patch(f"{BASE_URL}/config", json={
            "provider": model_provider,
            "temperature": temperature,
            "max_output_tokens": max_tokens
        })

# --- MAIN CHAT INTERFACE ---
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(f"<div class='message-user'>{msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='message-bot'>{msg['content']}</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# --- INPUT HANDLER ---
if prompt := st.chat_input("Ask about trades, markets, or strategies..."):
    if not st.session_state.session_id:
        response = requests.post(f"{BASE_URL}/sessions")
        st.session_state.session_id = response.json()["session_id"]
        st.session_state.chat_history = []

    st.session_state.chat_history.append({"role": "user", "content": prompt})
    st.markdown(f"<div class='message-user'>{prompt}</div>", unsafe_allow_html=True)

    res = requests.post(f"{BASE_URL}/chat", json={
        "session_id": st.session_state.session_id,
        "message": prompt
    })
    reply = res.json()["reply"]
    st.session_state.chat_history.append({"role": "assistant", "content": reply})
    st.markdown(f"<div class='message-bot'>{reply}</div>", unsafe_allow_html=True)
