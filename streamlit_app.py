import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Agentic SQL Assistant",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Agentic SQL Assistant")
st.caption("Ask questions about your sales data in plain English")

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = "user_streamlit_1"

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sql"):
            with st.expander("🔍 SQL Used"):
                st.code(msg["sql"], language="sql")

# Chat input
if prompt := st.chat_input("Ask about your sales data..."):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call API
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{API_URL}/chat",
                    json={
                        "session_id": st.session_state.session_id,
                        "question": prompt
                    }
                )
                data = response.json()
                answer = data.get("answer", "Sorry, something went wrong.")
                sql = data.get("sql_used")

                st.markdown(answer)
                if sql:
                    with st.expander("🔍 SQL Used"):
                        st.code(sql, language="sql")

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sql": sql
                })

            except Exception as e:
                st.error(f"Could not connect to API: {e}")

# Sidebar
with st.sidebar:
    st.header("💡 Try asking:")
    examples = [
        "How many customers do we have?",
        "What are total sales for last month?",
        "Which product has highest sales?",
        "Show me sales by category",
        "Who are our top customers?"
    ]
    for ex in examples:
        st.code(ex)

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()