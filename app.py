import streamlit as st
import requests
import os
import pandas as pd
from dotenv import load_dotenv

# Load credentials
load_dotenv()

# Constants
BASEROW_TOKEN = os.getenv("BASEROW_API_TOKEN")
INCOMING_URL = os.getenv("INCOMING_MESSAGES_URL")
OUTGOING_URL = os.getenv("OUTGOING_MESSAGES_URL")
WHATSAPP_URL = os.getenv("WHATSAPP_API_URL")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")

# Headers
headers_baserow = {"Authorization": f"Token {BASEROW_TOKEN}"}
headers_wa = {
    "Authorization": f"Bearer {WHATSAPP_TOKEN}",
    "Content-Type": "application/json"
}

# Functions
def get_incoming():
    res = requests.get(INCOMING_URL, headers=headers_baserow)
    return res.json().get("results", [])

def send_whatsapp(to, message):
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }
    return requests.post(WHATSAPP_URL, json=payload, headers=headers_wa)

def log_outgoing(to, message):
    payload = {
        "fields": {
            "phone": to,
            "message": message,
            "sender": "admin"
        }
    }
    return requests.post(OUTGOING_URL, json=payload, headers=headers_baserow)

# UI
st.set_page_config(page_title="Mini WhatsApp Chatbox", layout="wide")
st.title("💬 Mini WhatsApp Chatbox")

# Load messages
messages = get_incoming()

# Unique users
users = list({msg['fields']['phone']: msg for msg in messages}.values())
user_selected = st.selectbox("👥 Select User", users, format_func=lambda u: f"{u['fields'].get('name', 'Unknown')} ({u['fields']['phone']})")

if user_selected:
    user_phone = user_selected["fields"]["phone"]
    st.subheader(f"📨 Chat with {user_phone}")

    chat_history = [m for m in messages if m["fields"]["phone"] == user_phone]

    for msg in sorted(chat_history, key=lambda x: x["id"]):
        align = "right" if msg["fields"].get("sender") == "admin" else "left"
        color = "#D1E7DD" if align == "right" else "#F8D7DA"
        st.markdown(f"""
            <div style='text-align: {align}; background-color: {color}; padding: 10px; margin: 5px; border-radius: 10px;'>
                {msg["fields"]["message"]}
            </div>
        """, unsafe_allow_html=True)

    with st.form("reply_form"):
        reply_text = st.text_input("✍️ Type your reply...")
        submitted = st.form_submit_button("Send")
        if submitted and reply_text:
            wa_response = send_whatsapp(user_phone, reply_text)
            log_response = log_outgoing(user_phone, reply_text)
            st.success("✅ Reply sent!")
            st.experimental_rerun()
