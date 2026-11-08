from src.ingestion import ingest_document
from pathlib import Path
from src.vector_store import get_collection_count
from src.vector_store import get_collection

# PDF_PATH = Path("data/sample.pdf")

# result = ingest_document(PDF_PATH)

# print("Ingestion Result:")
# print(result)
# count = get_collection_count()

# print("Total records in ChromaDB:", count)

collection = get_collection()

# stored_records = collection.get(
#     where={
#         "document_id": result["document_id"]
#     }
# )

# print("Records for this document:", len(stored_records["ids"]))

TXT_PATH = Path("data/sample.txt")

txt_result = ingest_document(TXT_PATH)

print("TXT Ingestion Result:")
print(txt_result)

txt_records = collection.get(
    where={
        "document_id": txt_result["document_id"]
    }
)

print(
    "TXT records stored:",
    len(txt_records["ids"])
)
