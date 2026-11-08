from pypdf import PdfReader
from pathlib import Path

def load_pdf(file_path:Path):
    reader=PdfReader(file_path)

    pages=reader.pages

    documents=[]

    for page_number,page in enumerate(pages,start=1):

        text=page.extract_text() or ""

        document={
            "text":text,
            "metadata":{
                "source":file_path.name,
                "page":page_number
            }
        }

        documents.append(document)

    return documents


def load_txt(file_path:Path):

    with open(file_path,"r",encoding="utf-8") as file:
        text=file.read()

    document={
        "text":text,
        "metadata":{
            "source":file_path.name,
            "page":None
        }
    }

    return [document]


def load_document(file_path:Path):

    if not file_path.exists():
        raise FileNotFoundError(f"File not found :{file_path}")

    extension=file_path.suffix.lower()

    if extension==".pdf":
        return load_pdf(file_path)

    elif extension==".txt":
        return load_txt(file_path)

    else:
        raise ValueError(f"Unsupported file format: {extension}")
