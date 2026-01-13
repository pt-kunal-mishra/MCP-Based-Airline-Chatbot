import streamlit as st
import requests

# ---------------- CONFIG ----------------
API_URL = "https://esqizm4qw8.execute-api.ap-south-1.amazonaws.com/chat"

st.set_page_config(
    page_title="✈️ Airline Chatbot",
    page_icon="✈️",
    layout="centered"
)

# ---------------- UI HEADER ----------------
st.title("✈️ Airline Assistant")
st.caption("Ask questions about flights, delays, routes, and dates")

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- DISPLAY CHAT HISTORY ----------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------- USER INPUT ----------------
user_input = st.chat_input("Ask about airline flights...")

if user_input:
    # Show user message
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )
    with st.chat_message("user"):
        st.markdown(user_input)

    # Call API Gateway
    try:
        response = requests.post(
            API_URL,
            json={"question": user_input},
            timeout=30
        )
        response.raise_for_status()
        answer = response.json().get("answer", "No response received.")

    except Exception as e:
        answer = f"⚠️ Error contacting airline service: {str(e)}"

    # Show assistant response
    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )
    with st.chat_message("assistant"):
        st.markdown(answer)
