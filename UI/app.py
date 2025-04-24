import gradio as gr
import requests

BASE_URL = "http://127.0.0.1:8000"

def initialize_session():
    resp = requests.post(f"{BASE_URL}/sessions")
    sid = resp.json()["session_id"]
    return sid, []

def update_config(provider, temperature, max_tokens):
    requests.patch(
        f"{BASE_URL}/config",
        json={
            "provider": provider,
            "temperature": temperature,
            "max_output_tokens": max_tokens
        }
    )

def user_message(message, history, sid, provider, temperature, max_tokens):
    if sid == "":
        sid, history = initialize_session()
    update_config(provider, temperature, max_tokens)
    resp = requests.post(
        f"{BASE_URL}/chat",
        json={"session_id": sid, "message": message}
    )
    data = resp.json()
    history.append((message, data["reply"]))
    return "", history, data["session_id"]

with gr.Blocks() as demo:
    gr.Markdown("## Trading Copilot Chat")

    with gr.Row():
        provider = gr.Dropdown(
            choices=["gemini", "openai", "claude"],
            value="gemini", label="Model Provider"
        )
        temperature = gr.Slider(0.0,1.0, value=0.2, step=0.1, label="Temperature")
        max_tokens = gr.Slider(10,500, value=150, step=10, label="Max Tokens")
        new_session = gr.Button("New Session")

    session_state = gr.State("")
    history_state = gr.State([])

    chatbot = gr.Chatbot()
    user_input = gr.Textbox(placeholder="Type your message…", show_label=False)

    new_session.click(
        fn=lambda: initialize_session(),
        outputs=[session_state, history_state]
    )
    provider.change(
        fn=lambda p,t,m: update_config(p,t,m),
        inputs=[provider,temperature,max_tokens],
        outputs=[]
    )
    temperature.change(
        fn=lambda p,t,m: update_config(p,t,m),
        inputs=[provider,temperature,max_tokens],
        outputs=[]
    )
    max_tokens.change(
        fn=lambda p,t,m: update_config(p,t,m),
        inputs=[provider,temperature,max_tokens],
        outputs=[]
    )
    user_input.submit(
        fn=user_message,
        inputs=[user_input,history_state,session_state,provider,temperature,max_tokens],
        outputs=[user_input,chatbot,session_state]
    )

demo.launch()
