import os
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

DB_DIR = "./sebek_memory_db"
embed_model = OllamaEmbeddings(model="nomic-embed-text")

print("\n🦅 SEBEK MASS DIGESTION SEQUENCE INITIATED...")

# WSL path to your external F: drive
target_dir = "/mnt/f/"
print(f"Scanning the Vault at {target_dir} for Knowledge Files (.md, .txt, .csv)...")

documents = []
supported_extensions = (".md", ".txt", ".csv")

file_count = 0
for root, dirs, files in os.walk(target_dir):
    # Skip duplicates and system folders to prevent junk memory
    if '90_DUPLICATES' in root or '$RECYCLE.BIN' in root or 'System Volume Information' in root:
        continue
        
    for file in files:
        if file.lower().endswith(supported_extensions):
            path = os.path.join(root, file)
            try:
                # Load text safely
                loader = TextLoader(path, encoding='utf-8')
                documents.extend(loader.load())
                file_count += 1
                if file_count % 100 == 0:
                    print(f"  -> Successfully ingested {file_count} files so far...")
            except Exception:
                # Silently skip files with complex formatting or unreadable encoding
                pass

print(f"\nFound {len(documents)} valid text documents in the Vault. Slicing into neural data blocks...")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = text_splitter.split_documents(documents)

print(f"Generating memory vectors for {len(chunks)} blocks. (This will take heavy CPU crunching...)")

# Connect to the existing memory database and insert in batches to prevent crashes
vector_db = Chroma(persist_directory=DB_DIR, embedding_function=embed_model)
BATCH_SIZE = 5000

for i in range(0, len(chunks), BATCH_SIZE):
    batch = chunks[i:i+BATCH_SIZE]
    print(f"  -> Committing batch {i} to {i+len(batch)} of {len(chunks)} to permanent memory...")
    vector_db.add_documents(batch)

print(f"\n✅ MASS DIGESTION COMPLETE. SEBEK has permanently memorized {len(chunks)} data blocks from the Vault.")
