"""Streamlit UI for the AI shopping agent. Run with: uv run streamlit run app.py"""

import os

import streamlit as st

from src.agent import build_agent, chat

st.set_page_config(page_title="AI Shopping Agent", page_icon="🛒")

SAMPLE_QUESTIONS = [
    "Find me organic honey under $20 with 4.5+ rating",
    "Show organic snacks under $10",
    "What's the best rated coffee?",
    "Find dairy alternatives rated 4.5 or higher",
    "Cheapest grains you have?",
]

if "messages" not in st.session_state:
    st.session_state.messages = []


@st.cache_resource
def get_agent():
    return build_agent()


# ---------- Sidebar ----------
with st.sidebar:
    if st.button("➕ New chat", use_container_width=True, type="primary"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("#### Try asking")
    pending = None
    for q in SAMPLE_QUESTIONS:
        if st.button(q, use_container_width=True):
            pending = q

# ---------- Main ----------
st.title("🛒 AI Shopping Agent")
st.caption("Search products and place orders by chatting.")

if not os.getenv("GROQ_API_KEY"):
    st.error("GROQ_API_KEY is not set. Add it to a `.env` file in the project root.")
    st.stop()

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

prompt = st.chat_input("Ask for a product or place an order…") or pending

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            try:
                reply = chat(get_agent(), st.session_state.messages)
            except Exception as e:
                reply = f"Sorry, something went wrong: `{e}`"
        st.markdown(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})
