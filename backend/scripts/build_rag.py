import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from vectorstore.vectorstore import FaissVectorStore
from vectorstore.embedding import EmbeddingPipeline
from langchain_community.document_loaders import PyPDFLoader, CSVLoader

pdfs = [
    r"vectorstore/data/fertilizers rag3.pdf",
    r"vectorstore/data/nutricient manual for crops.pdf",
    r"vectorstore/data/Rabi-Agro-Advisory-2021-22_0.pdf",
    r"vectorstore/data/scgemes rag2.pdf",
    r"vectorstore/data/schemes2 rag 4.pdf",
]

store = FaissVectorStore("faiss_store")
try:
    store.load()
    print("[INFO] Loaded existing index; will append new embeddings")
except Exception:
    print("[INFO] No existing index; creating new")

pipe = EmbeddingPipeline()

def add_docs(docs, label: str):
    if not docs:
        print(f"[WARN] No docs for {label}")
        return
    chunks = pipe.chunk_documents(docs)
    if not chunks:
        print(f"[WARN] No chunks for {label}")
        return
    embs = pipe.embed_chunks(chunks).astype("float32")
    metas = [{"text": c.page_content} for c in chunks]
    store.add_embeddings(embs, metas)
    print(f"[INFO] Added {len(chunks)} chunks from {label}")

for pdf in pdfs:
    try:
        docs = PyPDFLoader(pdf).load()
        print(f"[INFO] Loaded {len(docs)} docs from {pdf}")
        add_docs(docs, pdf)
    except Exception as e:
        print(f"[ERROR] Failed {pdf}: {e}")

# CSV (optional)
csv_path = "vectorstore/data/questionsv4.csv"
if os.path.exists(csv_path):
    try:
        docs = CSVLoader(csv_path).load()
        print(f"[INFO] Loaded {len(docs)} docs from {csv_path}")
        add_docs(docs, csv_path)
    except Exception as e:
        print(f"[ERROR] CSV load failed: {e}")
else:
    print("[WARN] CSV not found")

store.save()
print(f"[INFO] Final metadata count: {len(store.metadata)}")
if store.index:
    print(f"[INFO] FAISS ntotal: {store.index.ntotal}")
