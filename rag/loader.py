"""Loads and chunks HR markdown documents for the vector store."""
import os
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import HR_DOCS_DIR, RAG_CHUNK_SIZE, RAG_CHUNK_OVERLAP


def load_hr_documents() -> list[Document]:
    """Read all .md files from HR_DOCS_DIR, split them into chunks with metadata."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=RAG_CHUNK_SIZE,
        chunk_overlap=RAG_CHUNK_OVERLAP,
        separators=["\n## ", "\n### ", "\n\n", "\n", " "],
    )

    documents = []
    for filename in sorted(os.listdir(HR_DOCS_DIR)):
        if not filename.endswith(".md"):
            continue

        filepath = os.path.join(HR_DOCS_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        title = filename.replace(".md", "").replace("_", " ").capitalize()
        chunks = splitter.split_text(content)

        for i, chunk in enumerate(chunks):
            documents.append(
                Document(
                    page_content=chunk,
                    metadata={"source": filename, "title": title, "chunk_index": i},
                )
            )

    return documents
