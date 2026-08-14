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
import streamlit as st
import json
import os
from datetime import datetime

# 1. Define the Memory Vault Path (Ensure this folder exists on your F: drive)
MEMORY_VAULT = r"F:\AI_VAULT\05_SOVEREIGN_AI_CORE\Session_Ledgers"
os.makedirs(MEMORY_VAULT, exist_ok=True)

# 2. Add the Sidebar Control Panel for Memory Operations
st.sidebar.header("🧠 Core Memory & Recall")

# --- ARCHIVE & COMPRESS BUTTON ---
if st.sidebar.button("💾 Compress & Archive Session"):
    if "messages" in st.session_state and len(st.session_state.messages) > 1:
        st.sidebar.info("Compressing session weight...")

        # Gather the raw conversation text
        raw_chat = " ".join([m["content"] for m in st.session_state.messages])

        # Command the LLM to parse and summarize the chat to save weight
        summary_prompt = f"Extract the core facts, decisions, and system directives from this conversation into a highly dense summary. Do not include conversational filler. Conversation: {raw_chat}"

        # Call SEBEK to generate the compressed summary
        compressed_memory = sebek_llm.invoke(summary_prompt).content

        # Save as a lightweight JSON checkpoint
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{MEMORY_VAULT}\\checkpoint_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump({"timestamp": timestamp, "compressed_memory": compressed_memory}, f)

        st.sidebar.success(f"Session locked and parsed: checkpoint_{timestamp}.json")
    else:
        st.sidebar.warning("No active conversation to compress.")

# --- ESSENTIAL RECALL DROPDOWN ---
# Find all saved JSON checkpoints in the vault
saved_checkpoints = [f for f in os.listdir(MEMORY_VAULT) if f.endswith(".json")]

if saved_checkpoints:
    selected_checkpoint = st.sidebar.selectbox("🔗 Inject Past Correlating Context", ["-- Select Checkpoint --"] + saved_checkpoints)

    if selected_checkpoint != "-- Select Checkpoint --":
        if st.sidebar.button("Inject Memory Anchor"):
            # Load the lightweight JSON summary
            with open(os.path.join(MEMORY_VAULT, selected_checkpoint), "r") as f:
                data = json.load(f)
                recalled_memory = data.get("compressed_memory", "")

            # Inject it silently as a System message to guide the LLM without printing it to the user chat
            if "messages" not in st.session_state:
                st.session_state.messages = []

            st.session_state.messages.insert(0, {"role": "system", "content": f"BACKGROUND CONTEXT ANCHOR: {recalled_memory}"})
            st.sidebar.success("Memory Anchor Injected. Drifting Lulled.")
