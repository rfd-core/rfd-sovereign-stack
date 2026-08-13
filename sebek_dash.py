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

# Safe similarity search helper to avoid embedding context-length crashes
def safe_similarity_search(vector_db, query, k=3, logger=None, max_chars=3000):
    """
    Run similarity_search while protecting against embedding context-length errors.
    - max_chars: conservative character limit for the embedding input (adjust as needed).
    - Keeps the tail of the query on truncation (recent context) and prefixes with a truncation note.
    - Retries once with more aggressive truncation if the embedding raises a context-length error.
    """
    def truncate_for_embedding(s, maxc):
        if len(s) <= maxc:
            return s
        tail = s[-maxc+32:]
        return "[TRUNCATED CONTEXT]\n" + tail

    q = query
    if len(q) > max_chars:
        if logger and hasattr(logger, "warning"):
            logger.warning(f"Query length {len(q)} > {max_chars}, truncating for embedding.")
        else:
            print(f"Query length {len(q)} > {max_chars}, truncating for embedding.")
        q = truncate_for_embedding(q, max_chars)

    try:
        return vector_db.similarity_search(q, k=k)
    except ValueError as ve:
        text = str(ve)
        if "context length" in text or "input length" in text:
            if logger and hasattr(logger, "warning"):
                logger.warning("Embedding rejected input due to context length; retrying with smaller input.")
            else:
                print("Embedding rejected input due to context length; retrying with smaller input.")
            q2 = truncate_for_embedding(q, int(max_chars / 2))
            try:
                return vector_db.similarity_search(q2, k=k)
            except Exception as e2:
                if logger and hasattr(logger, "exception"):
                    logger.exception("Retry after truncation failed: %s", e2)
                else:
                    print(f"Retry after truncation failed: {e2}")
                return []
        else:
            if logger and hasattr(logger, "exception"):
                logger.exception("Embedding call failed: %s", ve)
            else:
                print(f"Embedding call failed: {ve}")
            return []
    except Exception as e:
        if logger and hasattr(logger, "exception"):
            logger.exception("Unexpected error during similarity_search: %s", e)
        else:
            print(f"Unexpected error during similarity_search: {e}")
        return []

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
                results = safe_similarity_search(vector_db, prompt, k=3, logger=st, max_chars=3000)
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
