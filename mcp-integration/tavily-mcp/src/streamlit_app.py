# streamlit app

import streamlit as st
from agent import run_agent

st.set_page_config(page_title="Bank Rate Assistant", layout="centered")
st.title("Bank Rate Assistant (RAG + Tavily MCP)")

query = st.text_area("Ask about FD, home loans, or personal loans:", height=120)

if st.button("Ask"):
    if not query.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Querying agent..."):
            result = run_agent(query)

        st.subheader("Answer")
        st.write(result["answer"])

        st.subheader("Internal RAG data used")
        for doc in result["rag_docs"]:
            st.write(f"- {doc['text']} (Bank: {doc['metadata']['bank']} / Country: {doc['metadata']['country']})")

        st.subheader("External tools used")
        st.write(result["tools_used"])

        with st.expander("Debug: Raw Response"):
            st.json(result["raw"].to_dict() if hasattr(result["raw"], "to_dict") else str(result["raw"]))
