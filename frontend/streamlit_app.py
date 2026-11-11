"""
streamlit_app.py - Modern, interactive web UI for the AI-Powered SQL Agent.
Features:
- Chat interface with conversational follow-up memory.
- Instant pre-set buttons for the 5 assignment questions.
- Display of Human-readable explanation, generated SQL, and interactive data table.
- Security badges and malicious injection prevention alerts.
- Live database schema inspection in sidebar.
"""

import streamlit as st
import pandas as pd
import requests
import json
import os
import sys
from pathlib import Path

# Add project root to sys.path so we can run directly or via FastAPI
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.agent import run_agent
from app.database import get_schema_summary
from app.conversation import conversation_manager

st.set_page_config(
    page_title="AI-Powered SQL Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F3F4F6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3B82F6;
    }
    .stCodeBlock {
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Session state setup
if "session_id" not in st.session_state:
    st.session_state.session_id = "streamlit_session_1"
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar: Schema & Settings
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4248/4248443.png", width=60)
    st.title("SQL Agent Control")
    st.caption("AI-Powered Natural Language to SQL Assistant")
    
    st.markdown("---")
    st.subheader("📊 Database Schema")
    with st.expander("View Tables & Columns", expanded=True):
        schema_text = get_schema_summary()
        st.markdown(f"```\n{schema_text}\n```")

    st.markdown("---")
    if st.button("🗑️ Clear Conversation History", use_container_width=True):
        conversation_manager.clear_session(st.session_state.session_id)
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("### 🛡️ Security Features")
    st.markdown("""
    - **Read-Only SQLite Engine** (`mode=ro`)
    - **Forbidden Verbs Filter** (DROP, DELETE, INSERT, UPDATE, ALTER)
    - **Single Statement Enforcement**
    - **AST Validation with sqlglot**
    """)

# Main Content Header
st.markdown('<div class="main-header">🤖 AI-Powered SQL Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Ask complex business questions in natural English — get validated SQL, instant execution, and human explanations.</div>', unsafe_allow_html=True)

# Pre-set Assignment Prompts
st.markdown("##### ⚡ Quick Assignment Scenarios:")
col1, col2, col3, col4, col5 = st.columns(5)

prompt_to_send = None

with col1:
    if st.button("🏆 Top 10 Customers", use_container_width=True):
        prompt_to_send = "What are the top 10 customers by revenue?"
with col2:
    if st.button("📅 Revenue Last Month", use_container_width=True):
        prompt_to_send = "What was the total revenue last month?"
with col3:
    if st.button("🌍 Highest AOV Country", use_container_width=True):
        prompt_to_send = "Which country has the highest average order value?"
with col4:
    if st.button("⏳ Inactive (90 Days)", use_container_width=True):
        prompt_to_send = "List customers without orders in the last 90 days"
with col5:
    if st.button("❌ Cancelled Orders %", use_container_width=True):
        prompt_to_send = "What is the percentage of cancelled orders?"

# Edge Case Pre-set Row
st.markdown("##### 🧪 Edge Case Tests:")
ec1, ec2, ec3 = st.columns(3)
with ec1:
    if st.button("💬 Follow-up: Only Egypt", use_container_width=True):
        prompt_to_send = "Only those from Egypt"
with ec2:
    if st.button("🚫 Malicious: DROP TABLE", use_container_width=True):
        prompt_to_send = "DROP TABLE customers;"
with ec3:
    if st.button("❓ Out-of-Scope Question", use_container_width=True):
        prompt_to_send = "What is the capital of France?"

# Chat Input
user_input = st.chat_input("Ask a question about customers, revenue, orders, or products...")
query_to_execute = prompt_to_send or user_input

# Display previous messages in history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "user":
            st.markdown(f"**{msg['content']}**")
        else:
            data = msg.get("data", {})
            if data.get("error"):
                st.error(data["explanation"])
                if data.get("sql"):
                    st.code(data["sql"], language="sql")
            else:
                st.markdown(data["explanation"])
                with st.expander("🔍 Generated SQL Query", expanded=False):
                    st.code(data["sql"], language="sql")
                if data.get("rows"):
                    df = pd.DataFrame(data["rows"])
                    st.dataframe(df, use_container_width=True)
                    st.caption(f"Returned {data['row_count']} rows")

# Execute new query
if query_to_execute:
    # 1. Show user message
    st.session_state.messages.append({"role": "user", "content": query_to_execute})
    with st.chat_message("user"):
        st.markdown(f"**{query_to_execute}**")

    # 2. Run Agent
    with st.chat_message("assistant"):
        with st.spinner("Analyzing question, generating secure SQL, and executing..."):
            result = run_agent(question=query_to_execute, session_id=st.session_state.session_id)
            
            if not result["success"]:
                st.error(result["explanation"])
                if result.get("sql"):
                    with st.expander("Attempted Query", expanded=True):
                        st.code(result["sql"], language="sql")
                st.session_state.messages.append({"role": "assistant", "data": result})
            else:
                # Human readable answer
                st.success("Analysis Complete")
                st.markdown(f"### 💡 Answer\n{result['explanation']}")

                # Generated SQL
                with st.expander("🔍 Generated SQL Query", expanded=True):
                    st.code(result["sql"], language="sql")

                # Results Dataframe
                if result.get("rows"):
                    st.markdown("### 📋 Result Data")
                    df = pd.DataFrame(result["rows"])
                    st.dataframe(df, use_container_width=True)
                    st.caption(f"Displaying {result['row_count']} records")
                else:
                    st.info("Query executed successfully, but returned 0 records.")

                st.session_state.messages.append({"role": "assistant", "data": result})
