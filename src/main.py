import uuid

import streamlit as st

from auth.session_manager import SessionManager
from components.analysis_form import show_analysis_form
from components.auth_pages import show_login_page
from components.chat_history import messages_for_display
from components.footer import show_footer
from components.sidebar import show_sidebar
from config.app_config import APP_ICON, APP_NAME
from services.ai_service import get_chat_response

st.set_page_config(page_title="MedRAG", page_icon="🩺", layout="wide")
SessionManager.init_session()


def reset_report():
    for key in ("current_report_text", "analysis_result", "chat_messages", "vector_store", "vector_store_key", "knowledge_base"):
        st.session_state.pop(key, None)
    st.session_state.current_session = None
    st.session_state.report_source = "Upload PDF"


def create_session():
    if st.session_state.get("user"):
        ok, session = SessionManager.create_chat_session()
        if not ok:
            st.error("Could not create a saved session. Check your Supabase setup.")
            return
    else:
        session = {"id": str(uuid.uuid4()), "title": "Guest report", "guest": True}
    st.session_state.current_session = session
    st.session_state.chat_messages = []
    st.session_state.current_report_text = ""
    st.session_state.analysis_result = None
    st.session_state.pop("vector_store", None)
    st.session_state.pop("vector_store_key", None)
    st.session_state.pop("knowledge_base", None)


def get_messages():
    session = st.session_state.get("current_session")
    if not session:
        return []
    if session.get("guest"):
        return st.session_state.get("chat_messages", [])
    ok, messages = st.session_state.auth_service.get_session_messages(session["id"])
    return [message for message in messages if message.get("role") != "system"] if ok else []


def save_message(content, role):
    session = st.session_state.current_session
    if session.get("guest"):
        st.session_state.chat_messages.append({"role": role, "content": content})
    else:
        st.session_state.auth_service.save_chat_message(session["id"], content, role=role)


st.title(f"{APP_ICON} {APP_NAME}")
st.caption("Medical Intelligence & Retrieval Agent")
st.info("Privacy: uploaded report text and questions are held in this browser session for guests. When you run AI analysis or chat, report text and prompts are sent to Groq. Hugging Face may download the embedding model. Guest history is not saved to Supabase. Session memory is temporary, not a guaranteed secure deletion mechanism.")
st.warning("For information only; this tool does not diagnose or replace care from a qualified health professional.")

if st.session_state.get("user"):
    show_sidebar()
else:
    with st.sidebar:
        st.caption("Guest mode · no saved history")
        if st.button("New Report / Reset", use_container_width=True):
            reset_report()
            st.rerun()
        if st.button("Log in or sign up", use_container_width=True):
            st.session_state.show_auth = not st.session_state.get("show_auth", False)
            st.rerun()
        if st.session_state.get("show_auth"):
            show_login_page()

session = st.session_state.get("current_session")
if session and not session.get("guest") and st.session_state.get("loaded_session_id") != session.get("id"):
    ok, saved = st.session_state.auth_service.get_session_messages(session["id"])
    if ok:
        st.session_state.current_report_text = ""
        st.session_state.analysis_result = None
        for item in saved:
            content = item.get("content", "")
            if item.get("role") == "system" and content.startswith("__REPORT_TEXT__\n"):
                st.session_state.current_report_text = content.split("__REPORT_TEXT__\n", 1)[1].split("\n__END_REPORT_TEXT__", 1)[0]
            elif item.get("role") == "assistant" and not st.session_state.analysis_result:
                st.session_state.analysis_result = content
    st.session_state.loaded_session_id = session.get("id")
if not session:
    st.subheader("Try MedRAG")
    left, right = st.columns(2)
    with left:
        if st.button("Use Sample Report", type="primary", use_container_width=True):
            create_session()
            st.session_state.report_source = "Use Sample PDF"
            st.rerun()
    with right:
        if st.button("Upload My PDF", use_container_width=True):
            create_session()
            st.rerun()
else:
    if st.button("New Report / Reset"):
        reset_report()
        st.rerun()
    if not st.session_state.get("analysis_result"):
        show_analysis_form()
    else:
        st.subheader("Report analysis")
        st.markdown(st.session_state.analysis_result)
        for msg in messages_for_display(
            get_messages(), st.session_state.analysis_result
        ):
            if msg.get("role") == "user":
                st.chat_message("user").write(msg.get("content", ""))
            elif msg.get("role") == "assistant":
                st.chat_message("assistant").write(msg.get("content", ""))
        if prompt := st.chat_input("Ask a follow-up question about this report"):
            save_message(prompt, "user")
            with st.spinner("Searching the report and preparing an answer…"):
                answer = get_chat_response(prompt, st.session_state.current_report_text, get_messages())
            save_message(answer, "assistant")
            st.rerun()

show_footer()
