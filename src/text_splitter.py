from src.config import CHUNK_SIZE,CHUNK_OVERLAP
from langchain_text_splitters import RecursiveCharacterTextSplitter

def split_text(text:str):

    if not text.strip():
        return []

    if CHUNK_OVERLAP>=CHUNK_SIZE:
        raise ValueError(f"CHUNK_OVERLAP must be smaller than CHUNK_SIZE")

    spiltter=RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )

    chunks=spiltter.split_text(text)

    return chunks
