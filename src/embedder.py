"""
embedder.py
Chunks ko vector embeddings mein convert karta hai
aur FAISS index disk par save karta hai.

Model: sentence-transformers/all-MiniLM-L6-v2
"""

import os
from pathlib import Path
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
VECTOR_STORE_DIR = "vector_store"


def get_embedding_model() -> HuggingFaceEmbeddings:
    """
    HuggingFace embedding model load karo.
    Pehli baar internet se download hoga (~90MB), phir cache.
    """
    print(f"Loading embedding model: {EMBEDDING_MODEL}")
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
    print("  ✓ Model ready")
    return embeddings


def create_and_save_index(
    chunks: list[Document],
    save_dir: str = VECTOR_STORE_DIR
) -> FAISS:
    """
    Chunks se FAISS index banao aur disk par save karo.
    """
    if not chunks:
        raise ValueError("Chunks empty hain! Pehle ingest karo.")

    embeddings = get_embedding_model()

    print(f"\nEmbedding {len(chunks)} chunks... (thoda time lagega)")
    vectorstore = FAISS.from_documents(chunks, embeddings)

    Path(save_dir).mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(save_dir)
    print(f"  ✓ Index saved to: {save_dir}/")

    return vectorstore


def load_index(save_dir: str = VECTOR_STORE_DIR) -> FAISS:
    """
    Disk se existing FAISS index load karo.
    """
    if not Path(save_dir).exists():
        raise FileNotFoundError(
            f"Vector store nahi mila: '{save_dir}/'\n"
            "Pehle chalao: python scripts/ingest.py"
        )

    embeddings = get_embedding_model()
    vectorstore = FAISS.load_local(
        save_dir,
        embeddings,
        allow_dangerous_deserialization=True
    )
    print(f"  ✓ Index loaded from: {save_dir}/")
    return vectorstore


def index_exists(save_dir: str = VECTOR_STORE_DIR) -> bool:
    """Check karo ki FAISS index already bana hua hai ya nahi."""
    return (
        Path(save_dir).exists()
        and Path(save_dir, "index.faiss").exists()
        and Path(save_dir, "index.pkl").exists()
    )


if __name__ == "__main__":
    from chunker import chunk_text

    sample_chunks = chunk_text(
        "GLA University mein B.Tech CSE Core fees 2.0L per year hai.",
        source_name="test.pdf"
    )

    vs = create_and_save_index(sample_chunks)
    print("\nIndex created successfully!")

    vs2 = load_index()
    results = vs2.similarity_search("B.Tech fees kitni hai?", k=1)
    print(f"Test query result: {results[0].page_content}")