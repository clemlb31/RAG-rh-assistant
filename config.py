import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

# LLM
MISTRAL_MODEL = "mistral-small-latest"
MISTRAL_TEMPERATURE = 0
MISTRAL_EMBED_MODEL = "mistral-embed"

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
HR_DOCS_DIR = os.path.join(DATA_DIR, "hr_documents")
DB_PATH = os.path.join(DATA_DIR, "employees.db")
FAISS_INDEX_DIR = os.path.join(DATA_DIR, "faiss_index")

# RAG
RAG_CHUNK_SIZE = 500
RAG_CHUNK_OVERLAP = 50
RAG_TOP_K = 3

# Demo employee
DEFAULT_EMPLOYEE_NAME = "Jean Dupont"
