# CK AI Agent

## Overview

CK AI Agent is a Knowledge Base service that enables semantic document search using Large Language Models (LLMs) and the Qdrant vector database. Users can upload PDF documents, automatically extract metadata using an LLM, generate embeddings, store them in Qdrant, and query the knowledge base using natural language through REST APIs.

---

# Features

- PDF document upload
- Automatic metadata extraction using LLM
- Semantic document chunking
- Embedding generation using Sentence Transformers
- Vector storage using Qdrant
- Semantic search
- AI-powered question answering
- REST APIs using FastAPI
- Structured logging
- Custom exception handling
- Input validation
- Modular layered architecture
- Optional Gradio UI for Knowledge Base ingestion

---

# Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.12 |
| Framework | FastAPI |
| UI | Gradio (Optional) |
| LLM | OpenRouter (NVIDIA Nemotron) |
| Embeddings | Sentence Transformers |
| Vector Database | Qdrant |
| PDF Processing | PyPDF |
| Environment | python-dotenv |

---

# Project Structure

```text
CK-AI-Agent/

├── api/
│   ├── app.py
│   └── kb_api.py
│
├── common/
│   ├── custom_exceptions.py
│   ├── file_utils.py
│   ├── logger.py
│   └── validators.py
│
├── configuration/
│   ├── app_settings.py
│   ├── constants.py
│   └── context.py
│
├── database/
│   └── qdrant_client_manager.py
│
├── dto/
│   ├── request_dto.py
│   └── response_dto.py
│
├── repositories/
│   └── kb_repository.py
│
├── services/
│   ├── document_metadata_service.py
│   ├── kb_chat_service.py
│   └── kb_ingestion_service.py
│
├── uploads/
├── logs/
├── changelog/
├── validators/
│
├── kb_ui.py
├── main.py
├── requirements.txt
├── .env
└── README.md
```

---

# System Workflow

```text
User Uploads PDF
        │
        ▼
Validate Request
        │
        ▼
Save Uploaded File
        │
        ▼
Extract PDF Text
        │
        ▼
Extract Metadata using LLM
        │
        ▼
Split into Chunks
        │
        ▼
Generate Embeddings
        │
        ▼
Store Vectors in Qdrant
        │
        ▼
Knowledge Base Ready
```

---

# Question Answering Flow

```text
User Question
      │
      ▼
Generate Query Embedding
      │
      ▼
Semantic Search in Qdrant
      │
      ▼
Retrieve Relevant Chunks
      │
      ▼
Build Context
      │
      ▼
LLM Generates Answer
      │
      ▼
Return Response
```

---

# API Endpoints

## Health Check

```http
GET /
```

---

## Upload Documents

```http
POST /llm/upload
```

Uploads one or more PDF documents into the Knowledge Base.

---

## Query Knowledge Base

```http
POST /llm/kb
```

Returns an AI-generated answer based on the uploaded documents.

---

## View Knowledge Base

```http
GET /llm/kb
```

Returns all stored document chunks.

---

## View Uploaded Documents

```http
GET /llm/files
```

Returns uploaded document metadata.

---

## Delete Document

```http
DELETE /llm/files/{document_id}
```

Deletes all chunks belonging to a document.

---

## Clear Knowledge Base

```http
DELETE /llm/files
```

Deletes all vectors from the Knowledge Base.

---

# Installation

Clone the repository

```bash
git clone <repository-url>
cd ck-ai-agent
```

Create a virtual environment

```bash
python -m venv .venv
```

Activate the virtual environment

### Windows

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

Install dependencies

```bash
python -m pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file.

```env
OPENROUTER_API_KEY=

QDRANT_HOST=localhost
QDRANT_PORT=6333

COLLECTION_NAME=knowledge_base

EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

LLM_MODEL=nvidia/nemotron-3-super-120b-a12b:free

CHUNK_SIZE=500
CHUNK_OVERLAP=50

UPLOAD_FOLDER=uploads
MAX_FILE_SIZE=20971520
```

---

# Running the Application

## FastAPI Server

Using the entry point:

```bash
python main.py
```

or directly with Uvicorn:

```bash
python -m uvicorn api.app:app --reload
```

Application URL

```
http://127.0.0.1:8000
```

Swagger Documentation

```
http://127.0.0.1:8000/docs
```

ReDoc Documentation

```
http://127.0.0.1:8000/redoc
```

---

## Optional Knowledge Base UI

To launch the Gradio interface for uploading PDF documents:

```bash
python kb_ui.py
```

Default URL:

```
http://127.0.0.1:7860
```

---

# Architecture

```text
                Client
                   │
        ┌──────────┴──────────┐
        │                     │
        ▼                     ▼
   FastAPI APIs          Gradio UI (Optional)
        │                     │
        └──────────┬──────────┘
                   ▼
              Service Layer
                   │
                   ▼
            Repository Layer
                   │
                   ▼
         Qdrant Vector Database
```

---

# Coding Standards

This project follows the Engineering Team Coding Standards:

- Layered architecture
- SOLID principles
- DRY principle
- Structured logging
- Custom exception handling
- Input validation
- Environment-based configuration
- Type hints
- No hardcoded values
- Feature branch workflow
- Pull Request-based development

---

# Future Enhancements

- OCR support
- Multiple document formats
- Hybrid Search
- Metadata filtering
- Authentication & Authorization
- Streaming responses
- Docker deployment
- Unit tests
- Integration tests

---

# Version

**Version:** 1.0.0

---

# Author

Developed as part of the **CK AI Agent** project.