"""
SupportPearlz - Streamlit edition.

Run with:
    streamlit run app.py

The visitor signs in with their own OpenAI API key (verified once, kept
only in the browser's Streamlit session, never written to disk), then
asks support questions that are answered using data/knowledge.txt.
"""
from __future__ import annotations

import time

import streamlit as st

from knowledge import KnowledgeBase
from openai_helper import ApiKeyInvalidError, answer_question, verify_api_key

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
OPENAI_MODEL = "gpt-4o-mini"
MAX_QUESTIONS_PER_MINUTE = 10  # simple abuse guard, per browser session
MAX_QUESTION_LENGTH = 800

st.set_page_config(
    page_title="SupportPearlz",
    page_icon="🦪",
    layout="centered",
)

# ---------------------------------------------------------------------------
# Styling - keeps the same teal / pearl brand look as the rest of the project
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Inter:wght@400;500;600&display=swap');

    html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }
    h1, h2, h3 { font-family: 'Fraunces', serif !important; color: #234f49; }

    .sp-brand {
        display: flex; align-items: center; gap: 10px; margin-bottom: 6px;
    }
    .sp-brand__mark {
        width: 32px; height: 32px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-family: 'Fraunces', serif; font-weight: 600; font-size: 13px;
        color: #fff; background: linear-gradient(135deg, #2f6f66, #cf9f92);
    }
    .sp-brand__name {
        font-family: 'Fraunces', serif; font-weight: 600; font-size: 17px;
        color: #21302e;
    }
    .sp-hint { color: #6b7671; font-size: 13px; margin-top: 10px; }

    div.stButton > button {
        background: #2f6f66; color: #fff; border: none; border-radius: 8px;
        padding: 0.5rem 1.2rem; font-weight: 500;
    }
    div.stButton > button:hover { background: #234f49; color: #fff; }
    </style>
    """,
    unsafe_allow_html=True,
)


def brand_header() -> None:
    st.markdown(
        """
        <div class="sp-brand">
            <span class="sp-brand__mark">SP</span>
            <span class="sp-brand__name">SupportPearlz</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Cached resources
# ---------------------------------------------------------------------------
@st.cache_resource
def get_knowledge_base() -> KnowledgeBase:
    return KnowledgeBase("data/knowledge.txt")


# ---------------------------------------------------------------------------
# Session state defaults
# ---------------------------------------------------------------------------
st.session_state.setdefault("authenticated", False)
st.session_state.setdefault("api_key", "")
st.session_state.setdefault("messages", [])  # [{"role": "user"/"assistant", "content": str}]
st.session_state.setdefault("request_times", [])  # timestamps for rate limiting


def rate_limited() -> bool:
    """True if this session has asked too many questions in the last minute."""
    now = time.time()
    st.session_state.request_times = [
        t for t in st.session_state.request_times if now - t < 60
    ]
    return len(st.session_state.request_times) >= MAX_QUESTIONS_PER_MINUTE


# ---------------------------------------------------------------------------
# Login screen
# ---------------------------------------------------------------------------
def render_login() -> None:
    brand_header()
    st.title("Sign in to continue")
    st.write("Enter your own OpenAI API key to start a support session.")

    with st.form("login_form"):
        api_key = st.text_input("OpenAI API key", type="password", placeholder="sk-...")
        submitted = st.form_submit_button("Continue")

    if submitted:
        if not api_key.strip():
            st.error("Please enter your OpenAI API key.")
        else:
            with st.spinner("Verifying your key..."):
                try:
                    verify_api_key(api_key.strip())
                except ApiKeyInvalidError as exc:
                    st.error(str(exc))
                else:
                    st.session_state.authenticated = True
                    st.session_state.api_key = api_key.strip()
                    st.rerun()

    st.markdown(
        '<p class="sp-hint">Your key is verified with OpenAI, then kept only in '
        "this browser session's memory &mdash; it is never written to disk or "
        "stored in the project files.</p>",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Chat screen
# ---------------------------------------------------------------------------
def render_chat() -> None:
    top_left, top_right = st.columns([4, 1])
    with top_left:
        brand_header()
    with top_right:
        if st.button("Log out"):
            st.session_state.authenticated = False
            st.session_state.api_key = ""
            st.session_state.messages = []
            st.rerun()

    st.title("Customer Support")
    st.write("Ask about warranty, returns, shipping, installation, or safety.")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    question = st.chat_input("Example: How long is the warranty?")

    if question:
        question = question.strip()
        if len(question) > MAX_QUESTION_LENGTH:
            st.error(f"Please keep questions under {MAX_QUESTION_LENGTH} characters.")
        elif rate_limited():
            st.error("You're asking questions a bit fast — please wait a moment and try again.")
        else:
            st.session_state.request_times.append(time.time())
            st.session_state.messages.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.write(question)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    answer = answer_question(
                        api_key=st.session_state.api_key,
                        question=question,
                        knowledge_base=get_knowledge_base(),
                        model=OPENAI_MODEL,
                    )
                st.write(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})

    if st.session_state.messages:
        st.button(
            "Clear conversation",
            on_click=lambda: st.session_state.update(messages=[]),
        )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if st.session_state.authenticated:
    render_chat()
else:
    render_login()
