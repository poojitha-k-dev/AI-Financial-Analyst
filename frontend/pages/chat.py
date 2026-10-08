import streamlit as st
import uuid
from frontend import api_client as api
from frontend.theme import page_header


SUGGESTED_QUESTIONS = [
    "What is the current profitability outlook?",
    "How healthy is the balance sheet?",
    "What are the top 3 risks?",
    "Is the company generating free cash flow?",
    "How does leverage compare to industry norms?",
    "What's the revenue growth trend?",
    "Explain the cash conversion cycle.",
    "What's the Altman Z-Score and what does it mean?",
]


def show():
    page_header("Chat Analyst", "Context-aware AI financial Q&A — ask anything about your data", "💬")

    companies = api.get_companies()
    if not companies:
        st.warning("Add a company and upload data first.")
        return

    company_map = {c["name"]: c["id"] for c in companies}

    # ── Controls row ──
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        selected = st.selectbox("Company", list(company_map.keys()), label_visibility="collapsed")
    cid = company_map[selected]

    session_key = f"chat_session_{cid}"
    msgs_key    = f"chat_msgs_{cid}"

    if session_key not in st.session_state:
        st.session_state[session_key] = str(uuid.uuid4())
    session_id = st.session_state[session_key]

    with col2:
        if st.button("🔄 New Session", use_container_width=True):
            st.session_state[session_key] = str(uuid.uuid4())
            if msgs_key in st.session_state:
                del st.session_state[msgs_key]
            st.rerun()
    with col3:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            api.clear_chat(cid, session_id)
            if msgs_key in st.session_state:
                del st.session_state[msgs_key]
            st.rerun()

    # Load messages if not in state
    if msgs_key not in st.session_state:
        history = api.get_chat_history(cid, session_id, limit=50)
        st.session_state[msgs_key] = history or []

    messages = st.session_state[msgs_key]

    # ── Chat window ──
    chat_area = st.container()
    with chat_area:
        st.markdown("""
        <div style="min-height:360px;max-height:480px;overflow-y:auto;
                    background:var(--bg-card);border:1px solid var(--border);
                    border-radius:var(--radius);padding:1rem;margin-bottom:1rem;" id="chat-window">
        """, unsafe_allow_html=True)

        if not messages:
            st.markdown("""
            <div style="text-align:center;padding:2rem 1rem;">
                <div style="font-size:2.5rem;margin-bottom:0.75rem;">🤖</div>
                <div style="font-weight:600;color:var(--text-primary);margin-bottom:0.5rem;">
                    AI Financial Analyst
                </div>
                <div style="font-size:0.85rem;color:var(--text-muted);max-width:320px;margin:0 auto;">
                    Ask me anything about this company's financials, KPIs, risks, or strategy.
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                ts = str(msg.get("created_at", ""))[:16]

                if role == "user":
                    st.markdown(f"""
                    <div style="display:flex;justify-content:flex-end;margin:8px 0;">
                        <div>
                            <div style="text-align:right;font-size:0.68rem;color:var(--text-muted);
                                        margin-bottom:3px;">You · {ts}</div>
                            <div class="chat-bubble-user">{content}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Render markdown for AI responses
                    import re
                    # Simple markdown to HTML conversion for chat
                    safe_content = content.replace("**", "<strong>").replace("</strong>", "</strong>")
                    st.markdown(f"""
                    <div style="display:flex;justify-content:flex-start;margin:8px 0;">
                        <div>
                            <div style="display:flex;align-items:center;gap:6px;
                                        margin-bottom:3px;">
                                <span style="font-size:0.75rem;background:linear-gradient(135deg,#3b82f6,#6366f1);
                                             border-radius:999px;padding:1px 8px;color:white;
                                             font-weight:600;font-size:0.65rem;">AI</span>
                                <span style="font-size:0.68rem;color:var(--text-muted);">{ts}</span>
                            </div>
                            <div class="chat-bubble-ai">{content}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # ── Suggested questions ──
    st.markdown("<p class='section-title'>Quick Questions</p>", unsafe_allow_html=True)
    suggestion_cols = st.columns(4)
    for i, suggestion in enumerate(SUGGESTED_QUESTIONS):
        with suggestion_cols[i % 4]:
            if st.button(
                suggestion[:40] + "…" if len(suggestion) > 40 else suggestion,
                key=f"sug_{i}",
                use_container_width=True,
                help=suggestion,
            ):
                _send(suggestion, cid, session_id, msgs_key)
                st.rerun()

    # ── Input form ──
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    with st.form("chat_form", clear_on_submit=True):
        col_input, col_send = st.columns([5, 1])
        with col_input:
            user_question = st.text_input(
                "Your question",
                placeholder="e.g. What is the debt-to-equity ratio and is it concerning?",
                label_visibility="collapsed",
            )
        with col_send:
            send_btn = st.form_submit_button("Send →", use_container_width=True)

    if send_btn and user_question.strip():
        _send(user_question.strip(), cid, session_id, msgs_key)
        st.rerun()

    # ── Context info card ──
    with st.expander("ℹ️ What data does the AI have access to?", expanded=False):
        stmts = api.get_statements(cid)
        if stmts:
            st.markdown(f"""
            - **Latest period:** {stmts[0]['period']}
            - **Total periods available:** {len(stmts)}
            - **Financial data:** Revenue, income, balance sheet, cash flow
            - **KPIs:** 40+ calculated ratios
            - **Risk scores:** Altman Z, Piotroski F, custom flags
            - **Last analysis:** Available if you ran AI Insights
            """)
        else:
            st.markdown("No financial data loaded yet. Upload statements to improve AI accuracy.")


def _send(question: str, cid: int, session_id: str, msgs_key: str):
    # Optimistically show user message
    st.session_state[msgs_key].append({"role": "user", "content": question, "created_at": ""})

    with st.spinner("🤖 Thinking..."):
        result = api.send_chat(question, cid, session_id)

    if result:
        answer = result.get("answer", "I couldn't generate a response. Please try again.")
        st.session_state[msgs_key].append({"role": "assistant", "content": answer, "created_at": ""})
