"""FAISS vector store for HR document search (singleton, built lazily)."""
import os
from langchain_mistralai import MistralAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import MISTRAL_EMBED_MODEL, FAISS_INDEX_DIR, RAG_TOP_K
from rag.loader import load_hr_documents

_vectorstore: FAISS | None = None


def get_embeddings() -> MistralAIEmbeddings:
    return MistralAIEmbeddings(model=MISTRAL_EMBED_MODEL)


def build_vectorstore() -> FAISS:
    """Build a fresh FAISS index from the HR docs and persist it to disk."""
    documents = load_hr_documents()
    vs = FAISS.from_documents(documents, get_embeddings())
    vs.save_local(FAISS_INDEX_DIR)
    return vs


def get_vectorstore() -> FAISS:
    """Return the FAISS index, loading from disk or building it on first call."""
    global _vectorstore
    if _vectorstore is None:
        if os.path.exists(FAISS_INDEX_DIR):
            _vectorstore = FAISS.load_local(
                FAISS_INDEX_DIR, get_embeddings(), allow_dangerous_deserialization=True,
            )
        else:
            _vectorstore = build_vectorstore()
    return _vectorstore


def search_documents(query: str, k: int = RAG_TOP_K) -> list[Document]:
    vs = get_vectorstore()
    return vs.similarity_search(query, k=k)
