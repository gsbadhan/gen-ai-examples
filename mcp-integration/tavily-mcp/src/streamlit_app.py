# streamlit app

import streamlit as st
from agent import run_agent

st.set_page_config(page_title="Bank Rate Assistant", layout="centered")
st.title("Bank Rate Assistant (RAG + Tavily MCP)")

# Define the options for the drop-down list
options = ['India', 'USA', 'UK', 'Australia', 'Canada', 'Russia', 'UAE', 'Ukraine']

# Create the drop-down list
country = st.selectbox(
    'Ask about FD, Home loans and Personal loans, Select country',  
    options,              
    index=0            
)
st.write('You selected:', country)

if st.button("Ask"):
    if not country.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Querying agent..."):
            result = run_agent(country)

        st.subheader("Answer")
        st.write(result["answer"])

        st.subheader("Internal RAG data used")
        for doc in result["rag_docs"]:
            st.write(f"- {doc['text']} (Bank: {doc['metadata']['bank']} / Country: {doc['metadata']['country']})")
