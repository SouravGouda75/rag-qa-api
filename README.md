# Reliable RAG API

A streamlined, production-ready Retrieval-Augmented Generation (RAG) API built with FastAPI, LangChain, ChromaDB, Sentence-Transformers, and Google Gemini (`gemini-3.1-flash-lite`). The system ingests multi-format documents (PDF, Markdown, TXT), performs semantic retrieval with bi-encoder cosine search and lead-chunk prior routing for global summary queries, and produces strictly grounded answers backed by cited excerpts while refusing unanswerable questions. Managed with `uv` for reproducible environments and dependency resolution.

---

## Technical Highlights

| Component | Implementation |
|---|---|
| **Package Management with `uv`** | Uses Astral's `uv` (`pyproject.toml` + `uv.lock`) for sub-second dependency installation, environment isolation, and multi-stage Docker builds. |
| **LangChain Core Integration** | Implements LangChain primitives: `RecursiveCharacterTextSplitter` for chunking, `HuggingFaceEmbeddings` for vectorization (`all-MiniLM-L6-v2`), `langchain-chroma` for persistence, and `ChatGoogleGenerativeAI` with `.with_structured_output(GroundedAnswer)` for type-safe grounded answers. |
| **Streamlined Retrieval** | Lightweight bi-encoder cosine retrieval via ChromaDB paired with query intent routing (`_is_summary_query`) that injects lead structural chunks for document overview queries without heavy cross-encoders or PyTorch rerankers in Docker. |
| **Uniform Document Ingestion** | Uses `pypdf` for clean, lightweight PDF text extraction and native UTF-8/encoding detection via `chardet` for TXT and Markdown files without heavy OCR frameworks. |
| **Non-English Documents** | Automated language detection via `langdetect`. Ingest response returns explicit diagnostic warnings if document language is outside supported models. |
| **Edge-Case Hardening** | File size limits (HTTP 413), character bounds on inputs, encoding auto-detection via `chardet`, duplicate upload replacement, global error handler, and retry loops. |

---

## Architecture

```
┌────────────────────────────────────────────────────────┐
│                        Client                          │
└────────────┬─────────────────────────────┬─────────────┘
             │ (POST /ingest)              │ (POST /query)
             ▼                             │
┌─────────────────────────┐                │
│ Ingestion Engine        │                │
├─────────────────────────┤                ▼
│ • Sanitize Path         │          ┌─────────────┐
│ • Detect Charset        │          │ Query Route │
│ • pypdf / Text Parser   │          └──────┬──────┘
│ • Detect Language       │                 │
│ • LangChain TextSplitter│                 ▼
└────────────┬────────────┘          ┌──────────────────────────┐
             │                       │ Bi-Encoder Search        │
             ▼                       │ • all-MiniLM-L6-v2       │
┌─────────────────────────┐          │ • Lead-Chunk Prior Prior │
│ LangChain Chroma Store  │◀─────────┤   (if summary query)     │
│ (HNSW Cosine Space)     │          └──────────┬───────────────┘
└─────────────────────────┘                     ▼
                             ┌──────────────────────────────────┐
                             │ LangChain ChatGoogleGenerativeAI │
                             │ • Grounded Prompt (qa_prompt.yml)│
                             │ • with_structured_output(...)    │
                             │ • Strict Hallucination Refusal   │
                             └──────────────────────────────────┘
```

---

## Project Structure

```
.
├── pyproject.toml            # uv project configuration and dependencies
├── uv.lock                   # Locked reproducible dependency tree
├── requirements.txt          # Exported dependencies
├── app/
│   ├── main.py               # FastAPI application, global error handler, health checks
│   ├── config.py             # Pydantic Settings with .env configuration
│   ├── api/
│   │   ├── ingest.py         # POST /ingest (validation, parsing, language check, storage)
│   │   └── query.py          # POST /query (synchronous retrieval & grounded generation)
│   ├── core/
│   │   ├── parser.py         # Multi-format parser (pypdf, TXT/MD with chardet)
│   │   ├── chunker.py        # LangChain RecursiveCharacterTextSplitter with adaptive sizing
│   │   ├── embedder.py       # LangChain HuggingFaceEmbeddings wrapper (all-MiniLM-L6-v2)
│   │   ├── retriever.py      # Chroma store with summary intent routing & lead-chunk prior
│   │   └── answerer.py       # LangChain ChatGoogleGenerativeAI + structured GroundedAnswer
│   └── models/
│       └── schemas.py        # Pydantic request, response, and structured output models
├── prompts/
│   └── qa_prompt.yml         # Externalized YAML prompt templates and refusal rules
├── tests/
│   ├── conftest.py           # Pytest test client and test isolation fixtures
│   ├── test_core.py          # Unit tests: parsing, encoding, adaptive chunking, sizing
│   ├── test_ingest.py        # Ingestion tests: valid docs, duplicates, errors, language
│   └── test_query.py         # Query tests: structured answers, validation, health stats
├── sample_docs/              # Test corpus: PDF, TXT, and Markdown files
│   ├── language_models_are_unsupervised_multitask_learners.pdf
│   ├── company_policy.txt
│   ├── python_basics.md
│   ├── machine_learning.md
│   └── history_of_internet.txt
├── evaluation/
│   ├── questions.json        # 13 evaluation questions (Answerable, Unanswerable, Multi-evidence)
│   └── run_eval.py           # Automated evaluation runner with detailed metrics
├── Dockerfile                # Streamlined Dockerfile with uv and pre-cached bi-encoder
├── docker-compose.yml        # Docker compose setup with volume persistence
└── .env.example              # Environment variables template
```

---

## Quickstart

### 1. Using `uv` (Recommended)

```bash
# Clone and enter workspace
git clone <repo-url>
cd Crew-Task

# Install dependencies into virtual environment via uv
uv sync

# Configure environment
cp .env.example .env
# Edit .env and insert your GEMINI_API_KEY

# Run server
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Interactive Swagger documentation is available at `http://localhost:8000/docs`.

### 2. Standard pip / venv

```bash
python -m venv venv
# On Windows: venv\Scripts\activate
# On Linux/macOS: source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

### 3. Docker Deployment

```bash
cp .env.example .env
# Set GEMINI_API_KEY in .env

docker compose up --build
```

---

## API Reference

### 1. Ingest Document
`POST /ingest` (multipart/form-data)

Uploads, parses, chunks, and indexes a file (`.pdf`, `.txt`, `.md`).

**Example Request:**
```bash
curl -X POST http://localhost:8000/ingest \
  -F "file=@sample_docs/language_models_are_unsupervised_multitask_learners.pdf"
```

**Example Response:**
```json
{
  "document_name": "language_models_are_unsupervised_multitask_learners.pdf",
  "num_chunks": 309,
  "status": "ingested",
  "language": "en",
  "warnings": []
}
```

### 2. Query Knowledge Base
`POST /query` (application/json)

Answers a user query strictly using retrieved evidence.

**Example Request:**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "How many days of annual leave do employees get at Acme Corp?", "top_k": 3}'
```

**Example Response (Answerable):**
```json
{
  "answer": "All full-time employees are entitled to 24 days of paid annual leave per calendar year.",
  "evidence": [
    {
      "source_document": "company_policy.txt",
      "excerpt": "All full-time employees are entitled to 24 days of paid annual leave per calendar year."
    }
  ]
}
```

**Example Response (Unanswerable):**
```json
{
  "answer": "The provided documents do not contain information to answer this question.",
  "evidence": []
}
```

---

## Automated Tests & Evaluation

### Running Pytest

With `uv`:
```bash
uv run pytest tests/ -v
```

With standard pytest:
```bash
pytest tests/ -v
```

### Running Evaluation Suite
Ensure the server is running, then execute:

```bash
# With uv
uv run python evaluation/run_eval.py

# Or with python
python evaluation/run_eval.py
```

The script evaluates 13 scenarios across 3 categories:
1. **Answerable (7 questions):** Single-document factual queries across PDF, TXT, and Markdown.
2. **Unanswerable (3 questions):** Out-of-corpus queries verifying strict refusal without hallucination.
3. **Multi-Evidence (3 questions):** Synthesizing answers spanning multiple documents.

Full results are recorded in [evaluation/test_results.md](evaluation/test_results.md).

---

## Deliverables Summary

| Deliverable | Repository Location | Status |
|:---|:---|:---:|
| **1. Source Code Repository** | Root workspace with clean modular architecture ([app/](app/)) | Complete |
| **2. README & Architecture Decisions** | [README.md](README.md) with quickstart, Docker commands, diagrams, design decisions | Complete |
| **3. Sample Documents & Questions** | [sample_docs/](sample_docs/) (`.pdf`, `.txt`, `.md`) & [evaluation/questions.json](evaluation/questions.json) (13 scenarios) | Complete |
| **4. Automated Test Results & Limitations** | [evaluation/test_results.md](evaluation/test_results.md) + detailed discussion below | Complete |

---

## Automated Test Results (100% Pass Rate)

- **Unit & Integration Suite (Pytest):** **27/27 Passed (100%)** in ~11s.
- **End-to-End Evaluation Suite:** **13/13 Passed (100%)** via `evaluation/run_eval.py`.
- **Hallucination Prevention:** 100% adherence to explicit refusal string on out-of-corpus questions.

For the question-by-question breakdown, see [evaluation/test_results.md](evaluation/test_results.md).

---

## Discussion of Limitations

1. **Table Structure Preservation:** Linear text extraction via `pypdf` serializes PDF tables into plain text streams. Complex tables with merged column headers lose 2D layout semantics. Production systems handling dense financial balance sheets should use layout-aware parsing (e.g., LayoutLM or Textract) or ingest pre-formatted markdown tables.
2. **Visual & Diagrammatic Data:** Embedded raster images, charts, and architectural diagrams are not converted to text. A production multimodal pipeline (e.g. Gemini Multimodal / ColPali) should be deployed to embed page screenshot renderings directly.
3. **Bi-Encoder Granularity vs. Global Synthesis:** Bi-encoders (`all-MiniLM-L6-v2`) prioritize local chunk semantic similarity. While summary intent detection (`_is_summary_query`) and lead-chunk prior injection reliably answer document overviews, full multi-chapter book synthesis requires hierarchical tree indexing (such as RAPTOR).
4. **Embedded Vector Database Scalability:** Local ChromaDB persists to disk (`./chroma_data`) and operates in-process. For large-scale multi-tenant enterprise deployments (>500,000 vectors), Chroma should be transitioned to a standalone distributed vector cluster (Qdrant, Milvus, or PostgreSQL with `pgvector`).

