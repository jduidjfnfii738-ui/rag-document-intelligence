# Central configuration for the RAG application

from pathlib import Path

BASE_DIR=Path(__file__).resolve().parent.parent

DATA_DIR=BASE_DIR/"data"

CHROMA_DIR=BASE_DIR/"chroma_db"

EMBEDDING_MODEL_NAME="sentence-transformers/all-MiniLM-L6-v2"

LLM_MODEL_NAME="Gemma 3 4B Instruct"

MODEL_PATH = (
    BASE_DIR
    / "models"
    / "gemma-3-4b-it-Q4_K_M.gguf"
)

CHUNK_SIZE=500

CHUNK_OVERLAP=50

TOP_K=3

COLLECTION_NAME="rag_documents"

DISTANCE_THRESHOLD = 1.3
