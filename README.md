
# CK AI Agent

## Overview

CK AI Agent is a Knowledge Base Management System built using FastAPI, Qdrant, and Large Language Models (LLMs). It enables users to upload PDF documents, automatically extract document metadata, generate embeddings, store document chunks in a vector database, and retrieve accurate answers through semantic search.

The application follows a layered architecture with separate API, Service, Repository, and Validation layers, making it scalable, maintainable, and easy to test.

---

# Table of Contents

- Upload one or more PDF documents
- Automatic document metadata extraction using LLM
- PDF text extraction and chunking
- Embedding generation using Sentence Transformers
- Semantic vector search using Qdrant
- AI-powered Question Answering using OpenRouter LLM
- Knowledge Base retrieval with optional tag filtering
- Uploaded document management
- Delete individual documents
- Clear entire Knowledge Base
- Request-based logging with unique Request IDs
- Global exception handling
- Request and response DTOs
- Input validation
- Automated unit testing using Pytest
- HTML test report generation

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
| Testing | Pytest |
| API Testing | Postman |

-----

# Project Structure

```
Knowledge_Base_Project
│
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
│
├── repositories/
│
├── services/
│
├── uploads/
│
├── logs/
│
├── requirements.txt
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

# Technology Stack

| Component | Technology |
|------------|------------|
| Language | Python 3.12 |
| Framework | FastAPI |
| Vector Database | Qdrant |
| Embedding Model | sentence-transformers/all-MiniLM-L6-v2 |
| LLM | OpenRouter |
| PDF Processing | PyPDF |
| Environment | python-dotenv |

---

# Prerequisites

- Python 3.12+
- Git
- Qdrant
- OpenRouter API Key
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
cd Knowledge_Base_Project
cd ck-ai-agent
```

Install dependencies:

```bash
pip install -r requirements.txt
python -m pip install -r requirements.txt
```

---

# Environment Variables

Run the application:

```bash
python main.py
```

or

```bash
uvicorn api.app:app --reload
```

Swagger UI:

```
http://127.0.0.1:8000/docs
```

OpenAPI JSON:

```
http://127.0.0.1:8000/openapi.json
```
---

## Testing

Run all tests:

```bash
pytest
```

Generate HTML report:

```bash
pytest --html=reports/report.html --self-contained-html
```

Current automated test coverage includes:

- API routes
- Services
- Repository layer
- Validators
- File upload validation

---

## Version

# Version

**Version:** 1.0.0

---

## Author

**CK AI Agent – Knowledge Base Module**

Developed as part of the CK AI Agent project.
Developed as part of the **CK AI Agent** project.
