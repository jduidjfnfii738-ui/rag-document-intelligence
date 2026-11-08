# RAG Document Intelligence

A privacy-conscious, local-LLM-powered Retrieval-Augmented Generation (RAG) application that allows users to upload documents, ask questions, and receive answers grounded in retrieved document content.

> **Project Status:** Work in Progress
> **Final Selected LLM:** Gemma 3 4B Instruct (GGUF)

## 1. Project Overview

RAG Document Intelligence is a document question-answering application built using Python, Streamlit, ChromaDB, Sentence Transformers, and a locally running language model.

The goal is to build an application where users can upload PDF and TXT documents and interact with their contents through a conversational interface.

Instead of relying entirely on a language model's pretrained knowledge, the application retrieves relevant document passages and supplies them as context to the model.

The application also implements user authentication and user-specific document isolation.

## 2. Original Project Goals

The project was planned around the following objectives:

- Build a complete document-based RAG pipeline.
- Support PDF and TXT document uploads.
- Extract and split document text into manageable chunks.
- Generate semantic embeddings.
- Store and retrieve document chunks using ChromaDB.
- Generate answers using a local language model.
- Provide source and page references.
- Avoid answering questions unsupported by uploaded documents.
- Implement user authentication.
- Ensure users can only access their own documents.
- Build an interactive Streamlit interface.

## 3. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application |
| Streamlit | User interface |
| ChromaDB | Vector database |
| Sentence Transformers | Semantic embeddings |
| all-MiniLM-L6-v2 | Embedding model |
| LangChain Text Splitters | Document chunking |
| PyPDF | PDF text extraction |
| llama-cpp-python | Local GGUF inference |
| Gemma 3 4B Instruct | Final selected language model |
| SQLite | User authentication database |
| PBKDF2-HMAC-SHA256 | Password hashing |

## 4. System Architecture

### Document indexing

1. User uploads a PDF or TXT file.
2. The application validates the file.
3. Text is extracted from the document.
4. Extracted text is divided into chunks.
5. Each chunk is converted into an embedding.
6. Embeddings and metadata are stored in ChromaDB.
7. Document ownership information is attached to the stored records.

### Question answering

1. User submits a question.
2. The question is converted into an embedding.
3. ChromaDB retrieves the most relevant document chunks.
4. Retrieved results are filtered using a distance threshold.
5. Relevant context is passed to the local language model.
6. The model generates an answer.
7. Source and page references are returned with the answer.

## 5. Development Journey

This project was developed incrementally, with attention to both implementation and debugging.

### Phase 1 — Building the RAG foundation

The initial work focused on understanding and implementing the core RAG pipeline:

- Document loading.
- Text extraction.
- Chunking.
- Embedding generation.
- Vector storage.
- Semantic retrieval.
- Context-based answer generation.

The objective was to understand how each component contributes to the final response rather than treating RAG as a single black-box function.

### Phase 2 — Document processing and retrieval

PDF and TXT support was implemented.

The application uses:

- Chunk size: 500 characters.
- Chunk overlap: 50 characters.
- Embedding model: all-MiniLM-L6-v2.
- Retrieval top-k: 3.
- Initial distance threshold: 1.3.

These are project configuration values and may need further evaluation on different datasets.

### Phase 3 — Local LLM selection

One of the most challenging parts of development was selecting a language model that could produce useful answers from retrieved context.

The first priority was not simply finding a model that could generate fluent text. The model also needed to follow instructions, use retrieved information, and avoid unsupported answers.

Several model experiments were performed.

**GPT-2-style experiments**

Initial experiments were used to understand local inference performance and model behavior. A benchmark was also conducted using a fixed prompt and generation length.

**Qwen2.5-0.5B-Instruct**

Qwen2.5-0.5B-Instruct was explored in the RAG experiments. Its behavior was evaluated using document-based questions and refusal scenarios.

Some responses demonstrated that generating fluent text does not necessarily mean that the answer is supported by the retrieved context.

**Gemma 3 4B Instruct — Final selection**

After experimenting with alternative models and generation configurations, Gemma 3 4B Instruct was selected as the application's final model.

Model file:

`gemma-3-4b-it-Q4_K_M.gguf`

The model runs locally through `llama-cpp-python`.

The selection was based on the observed behavior during project experiments. It is not a claim that the model is hallucination-free or universally better than every alternative.

### Phase 4 — Improving answer reliability

A major RAG challenge was preventing the language model from adding information that was not present in the retrieved documents.

Several mechanisms were implemented:

- Context-only answer instructions.
- Relevance filtering.
- Insufficient-information refusal.
- Source and page citations.
- A separate answer-validation module.

The application can respond with:

"I don't have enough information in the provided documents."

when no sufficiently relevant context is available.

The validation module was developed separately; its integration into the main answer pipeline remains a future improvement.

### Phase 5 — Building the application interface

The Streamlit application was expanded beyond a basic chat interface.

Implemented sections include:

- Authentication.
- Dashboard.
- Document management.
- Document upload and deletion.
- Chat interface.
- Application settings.

The interface also includes document statistics, source references, and reusable frontend components.

### Phase 6 — Authentication and multi-user privacy

Multi-user document isolation was an important part of the project.

The application uses:

- SQLite user accounts.
- UUID-based user identifiers.
- PBKDF2-HMAC-SHA256 password hashing.
- Random password salts.
- HMAC-signed authentication tokens.
- Encrypted browser cookies.

Each document is associated with a user ID.

Retrieval, document listing, deletion, and document management operations apply user-specific ownership filters.

During debugging, a document visibility issue was traced to an old Streamlit process still running stale code. Restarting the application process resolved the observed issue.

This experience highlighted the importance of verifying application state and runtime processes when debugging multi-user behavior.

## 6. Major Engineering Challenges

| Challenge | Approach |
|---|---|
| Extracting text from different document formats | Separate PDF and TXT loading logic |
| Choosing effective chunk sizes | Experimented with chunk size and overlap |
| Finding relevant document passages | Semantic embeddings and ChromaDB retrieval |
| Irrelevant retrieval results | Distance-based relevance filtering |
| Unsupported LLM answers | Context-only prompting and refusal behavior |
| Selecting a suitable local LLM | Tested multiple models and configurations |
| Document ownership isolation | User-specific metadata and retrieval filters |
| Authentication persistence | Signed tokens and encrypted cookies |
| Debugging stale application behavior | Restarted the old Streamlit process and verified behavior again |

## 7. Security and Privacy

The application includes several security-oriented mechanisms:

- Passwords are stored as PBKDF2-derived hashes, not plaintext.
- Authentication tokens are signed using HMAC-SHA256.
- Browser cookies use an encrypted cookie manager.
- Uploaded documents are stored in user-specific directories.
- ChromaDB records include user ownership metadata.
- Retrieval and document management apply user-specific filters.

**Important:** These mechanisms are an implementation foundation, not a guarantee of production-grade security. Additional security review, authorization testing, rate limiting, deployment hardening, and operational safeguards are still required.

## 8. Current Project Features

- PDF and TXT uploads.
- Document text extraction.
- Text chunking.
- Semantic embedding generation.
- Persistent ChromaDB storage.
- User-specific document retrieval.
- Local LLM inference.
- Context-based question answering.
- Insufficient-context refusal.
- Source and page references.
- Document listing and deletion.
- Duplicate document detection.
- User authentication.
- Streamlit dashboard and chat interface.

## 9. Project Structure

```text
rag-document-intelligence/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── src/
│   ├── auth.py
│   ├── config.py
│   ├── document_loader.py
│   ├── document_manager.py
│   ├── embeddings.py
│   ├── generator.py
│   ├── ingestion.py
│   ├── rag_pipeline.py
│   ├── retriever.py
│   ├── text_splitter.py
│   ├── validator.py
│   └── vector_store.py
│
├── frontend/
│   ├── auth_interface.py
│   ├── chat_interface.py
│   ├── components.py
│   ├── dashboard.py
│   ├── document_panel.py
│   ├── helpers.py
│   ├── session_auth.py
│   └── styles.css
│
├── data/
│   ├── sample.pdf
│   └── sample.txt
│
├── tests/
│
└── evaluation/
```

Runtime data, local models, authentication databases, and secrets are excluded from the repository.

## 10. Installation and Setup

### Prerequisites

- Python.
- Git.
- A local GGUF model file.
- Sufficient system memory for the selected model and embedding model.

### Clone the repository

```bash
git clone YOUR_REPOSITORY_URL
cd rag-document-intelligence
```

### Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure Streamlit secrets

Create:

`.streamlit/secrets.toml`

Add two strong, randomly generated secrets:

```toml
cookies_password = "YOUR_RANDOM_COOKIE_SECRET"
auth_token_secret = "YOUR_RANDOM_AUTH_SECRET"
```

Never commit this file or share its actual values.

### Add the local model

Place the selected GGUF model at:

```text
models/gemma-3-4b-it-Q4_K_M.gguf
```

The model weights are not included in this repository.

### Run the application

```bash
streamlit run app.py
```

## 11. Limitations

- Scanned PDFs requiring OCR are not currently supported by ordinary text extraction.
- Answer quality depends on document quality, retrieval relevance, and model behavior.
- The configured distance threshold requires further evaluation.
- The answer validator is not yet integrated into the main pipeline.
- The current vector-store ownership model relies on application-level filtering.
- Deployment and concurrent-user behavior require additional testing.

## 12. Future Improvements

- Integrate answer validation into the RAG pipeline.
- Add retrieval and generation evaluation metrics.
- Build a golden evaluation dataset.
- Experiment with hybrid retrieval.
- Add reranking and query rewriting.
- Improve document processing and OCR support.
- Add stronger authorization and deployment safeguards.
- Improve observability and error logging.
- Complete automated testing.
- Deploy a public version.

## 13. Learning Outcomes

This project provided practical experience with:

- Building a modular RAG architecture.
- Working with embeddings and vector databases.
- Integrating local GGUF language models.
- Evaluating model behavior.
- Handling unsupported answers.
- Building a multi-user Streamlit application.
- Implementing authentication and document ownership.
- Debugging real application and retrieval problems.

---

**RAG Document Intelligence**
An ongoing AI engineering portfolio project.
