from src.document_loader import load_document
from pathlib import Path

file_path=Path("data/missing.pdf")
documents=load_document(file_path)
print(documents)
