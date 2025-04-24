# utils.py
from flask import session

History = []

def get_chat_history():
    if "history" not in session:
        session["history"] = []
    return History

def add_to_history(user_msg, bot_msg):
    History.append({"user": user_msg, "bot": bot_msg})
    history = get_chat_history()
    history.append({"user": user_msg, "bot": bot_msg})
    session["history"] = history
    session["last_question"] = user_msg
