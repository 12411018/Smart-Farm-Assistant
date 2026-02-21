import os
from typing import List
from .vectorstore import FaissVectorStore
from .data_loader import load_all_documents


class RAGSearch:
    def __init__(
        self,
        persist_dir: str = "faiss_store",
        embedding_model: str = "all-MiniLM-L6-v2",
    ):
        self.vectorstore = FaissVectorStore(persist_dir, embedding_model)
        faiss_path = os.path.join(persist_dir, "faiss.index")
        meta_path = os.path.join(persist_dir, "metadata.pkl")
        if not (os.path.exists(faiss_path) and os.path.exists(meta_path)):
            data_dir = os.path.join(os.path.dirname(__file__), "data")
            docs = load_all_documents(data_dir)
            if docs:
                self.vectorstore.build_from_documents(docs)
            else:
                print("[WARNING] No documents loaded for vector store build.")
        else:
            self.vectorstore.load()

    def retrieve_context(self, query: str, top_k: int = 8) -> List[str]:
        results = self.vectorstore.query(query, top_k=top_k)
        return [r["metadata"].get("text", "") for r in results if r.get("metadata")]


def build_context_text(chunks: List[str]) -> str:
    cleaned = [c.strip() for c in chunks if c and c.strip()]
    return "\n\n".join(cleaned)


if __name__ == "__main__":
    rag = RAGSearch()
    sample = rag.retrieve_context("wheat irrigation", top_k=3)
    print(build_context_text(sample))
