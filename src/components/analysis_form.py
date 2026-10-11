import streamlit as st

from config.prompts import SPECIALIST_PROMPTS
from config.sample_data import SAMPLE_REPORT
from config.app_config import MAX_UPLOAD_SIZE_MB
from services.ai_service import generate_analysis
from utils.pdf_extractor import extract_text_from_pdf


def show_analysis_form():
    if not st.session_state.get("current_session"):
        return
    source = st.radio("Report source", ["Upload PDF", "Use Sample PDF"], horizontal=True,
                      index=1 if st.session_state.get("report_source") == "Use Sample PDF" else 0,
                      key="report_source")
    text = SAMPLE_REPORT
    if source == "Upload PDF":
        uploaded = st.file_uploader("Upload a medical report PDF", type=["pdf"],
                                    help=f"Maximum {MAX_UPLOAD_SIZE_MB} MB; text-based PDFs only")
        if not uploaded:
            return
        if uploaded.size > MAX_UPLOAD_SIZE_MB * 1024 * 1024:
            st.error(f"PDF exceeds the {MAX_UPLOAD_SIZE_MB} MB limit.")
            return
        text = extract_text_from_pdf(uploaded)
        if not text or text.startswith(("Invalid", "File size", "PDF exceeds", "Could not", "The uploaded", "Unable", "Error")):
            st.error(text or "No readable report text was found.")
            return
        with st.expander("Preview extracted report"):
            st.text(text[:12000])
    else:
        with st.expander("Preview sample report"):
            st.text(SAMPLE_REPORT)

    if st.button("Analyze report", type="primary"):
        with st.spinner("Analyzing report…"):
            result = generate_analysis({"report": text}, SPECIALIST_PROMPTS["comprehensive_analyst"])
        if not result.get("success"):
            st.error(result.get("error", "Analysis failed. Check your AI provider configuration."))
            return
        st.session_state.current_report_text = text
        content = result.get("content", "")
        if result.get("model_used"):
            content += f"\n\n*Generated with {result['model_used']}*"
        st.session_state.analysis_result = content
        session = st.session_state.current_session
        if session.get("guest"):
            st.session_state.setdefault("chat_messages", []).append({"role": "assistant", "content": content})
        else:
            st.session_state.auth_service.save_chat_message(
                session["id"], f"__REPORT_TEXT__\n{text}\n__END_REPORT_TEXT__", role="system"
            )
            st.session_state.auth_service.save_chat_message(session["id"], content, role="assistant")
        st.rerun()
