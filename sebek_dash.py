import streamlit as st
import requests
import json
import os
import subprocess
try:
    from langchain_community.embeddings import OllamaEmbeddings
    from langchain_community.vectorstores import Chroma
    HAS_MEMORY = True
except ImportError:
    HAS_MEMORY = False

st.set_page_config(page_title="DSOS Command Center", page_icon="🦅", layout="wide")

st.title("🦅 SEBEK Local Intelligence Engine")
st.markdown("### Digital Sovereign Operating System (DSOS) - Control Interface")

# 1. Connect to SEBEK's New Neural Memory
DB_DIR = "./sebek_memory_db"
if HAS_MEMORY and os.path.exists(DB_DIR):
    embed_model = OllamaEmbeddings(model="nomic-embed-text")
    vector_db = Chroma(persist_directory=DB_DIR, embedding_function=embed_model)
    memory_status = "ONLINE (Neural Retrieval Active)"
else:
    vector_db = None
    memory_status = "OFFLINE"

# 2. Load the File Index Map safely
map_path = "sebek_master_map.json"
master_map = {}
if os.path.exists(map_path):
    try:
        with open(map_path, 'r', encoding='utf-8-sig') as f:
            master_map = json.load(f)
    except Exception as e:
        pass

total_files = master_map.get("total_files_across_all_territories", 0)

tab1, tab2 = st.tabs(["💬 Comms Link", "🗄️ Vault Explorer"])

with tab1:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("Direct Interface")
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Enter command or query for SEBEK..."):
            st.chat_message("user").markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            # --- THE NEURAL LINK ---
            # Search the local database for relevant memories before answering
            retrieved_context = ""
            if vector_db:
                results = vector_db.similarity_search(prompt, k=3)
                if results:
                    retrieved_context = "\n--- RECALLED VAULT MEMORY ---\n"
                    for r in results:
                        retrieved_context += f"{r.page_content}\n"
                    retrieved_context += "-----------------------------\n"

            vault_stats = f"System Context: You are SEBEK. You guard a vault with {total_files} files. "
            full_prompt = vault_stats + retrieved_context + "\nUser query: " + prompt

            url = "http://localhost:11434/api/generate"
            payload = {
                "model": "sebek-core",
                "prompt": full_prompt,
                "stream": False
            }
            try:
                response = requests.post(url, json=payload)
                sebek_reply = response.json().get("response", "Error: No response.")
            except Exception as e:
                sebek_reply = f"System Error: Could not connect to SEBEK engine. Details: {e}"

            with st.chat_message("assistant"):
                st.markdown(sebek_reply)
            st.session_state.messages.append({"role": "assistant", "content": sebek_reply})

    with col2:
        st.subheader("System Status")
        st.info("SEBEK Engine: ONLINE")
        st.success("Network: SECURE / LOCAL")
        st.write(f"**Files Indexed:** {total_files}")
        st.write(f"**Long-Term Memory:** {memory_status}")
