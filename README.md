# CK AI Agent – Knowledge Base Module

A modular AI-powered Knowledge Base built using **FastAPI**, **Qdrant**, **Sentence Transformers**, and **OpenRouter LLMs**. The application enables users to upload PDF documents, automatically extract metadata, generate vector embeddings, perform semantic search, and answer questions using Retrieval-Augmented Generation (RAG).

---

# Table of Contents

- Overview
- Features
- System Architecture
- Project Structure
- Technology Stack
- Prerequisites
- Installation
- Environment Variables
- Starting Qdrant
- Running the Application
- Knowledge Base Workflow
- Collection Creation
- API Documentation
- Sample Postman Requests
- Logging
- Troubleshooting
- Future Enhancements

---

# Overview

The Knowledge Base module allows users to:

- Upload one or more PDF documents.
- Automatically extract document metadata using an LLM.
- Split documents into semantic chunks.
- Generate embeddings using Sentence Transformers.
- Store vectors inside Qdrant.
- Retrieve relevant chunks using semantic similarity.
- Generate contextual answers using an OpenRouter-hosted LLM.

The project follows a modular architecture consisting of:

- API Layer
- Service Layer
- Repository Layer
- Database Layer
- Configuration Layer
- Common Utilities

CK AI Agent is a Knowledge Base service that enables semantic document search using Large Language Models (LLMs) and the Qdrant vector database. Users can upload PDF documents, automatically extract metadata using an LLM, generate embeddings, store them in Qdrant, and query the knowledge base using natural language through REST APIs.

---

# Features

- PDF Upload
- Automatic Metadata Extraction
- Semantic Chunking
- Vector Embedding Generation
- Qdrant Integration
- Semantic Search
- AI-powered Question Answering
- FastAPI REST APIs
- Structured Logging
- Custom Exception Handling
- Request Validation
- Modular Project Structure

---

# System Architecture

```
                    User
                      │
                      ▼
                 FastAPI APIs
                      │
      ┌───────────────┴────────────────┐
      │                                │
      ▼                                ▼
 Knowledge Base Service          Chat Service
      │                                │
      ▼                                ▼
 PDF Processing               Query Embedding
      │                                │
      ▼                                ▼
 Metadata Extraction        Semantic Search
      │                                │
      ▼                                ▼
 Text Chunking              Retrieved Chunks
      │                                │
      ▼                                ▼
 Embedding Model           Prompt Builder
      │                                │
      ▼                                ▼
 Qdrant Vector DB ─────────────► OpenRouter LLM
```
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

Create a virtual environment

```bash
python -m venv .venv
```

Activate the environment

Windows
Activate the virtual environment

### Windows

```bash
.venv\Scripts\activate
```

Linux / macOS
### Linux / macOS

```bash
source .venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
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

# Starting Qdrant

The application requires a running Qdrant instance before starting.

### Option 1 – Docker (Recommended)

```bash
docker run -p 6333:6333 qdrant/qdrant
```

### Option 2 – Local Installation

Start the Qdrant server according to your local installation.

Verify that Qdrant is running by opening:

```
http://localhost:6333/dashboard
```

or

```
http://localhost:6333
```

---

# Running the Application

Start FastAPI

```bash
uvicorn api.app:app --reload
```

Open Swagger UI
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

---

# Knowledge Base Workflow

**Important**

Documents **must be uploaded before asking questions**.

The ingestion pipeline follows this sequence:

```
Upload PDF
      │
      ▼
Validate File
      │
      ▼
Save File
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
Store in Qdrant
      │
      ▼
Knowledge Base Ready
```

Only after successful ingestion can the `/llm/kb` endpoint answer questions.

---

# Collection Creation

Collection Name

```
knowledge_base
```

The application **automatically creates the Qdrant collection** (if it does not already exist) during startup.

No manual collection creation is required.

---

# Question Answering Flow

```
User Question
      │
      ▼
Generate Query Embedding
      │
      ▼
Semantic Search
      │
      ▼
Retrieve Top Chunks
      │
      ▼
Build Prompt
      │
      ▼
OpenRouter LLM
      │
      ▼
Return Response
ReDoc Documentation

```
http://127.0.0.1:8000/redoc
```

---

# API Documentation

## Health Check

```
GET /
```

Returns application status.

---

## Upload Documents

```
POST /llm/upload
```

Uploads one or more PDF documents.

---

## Ask Question

```
POST /llm/kb
```

Generates an answer using the uploaded documents.

---

## View Knowledge Base

```
GET /llm/kb
```

Returns all indexed chunks.

---

## View Uploaded Files

```
GET /llm/files
```

Returns uploaded document metadata.

---

## Delete Document

```
DELETE /llm/files/{document_id}
```

Deletes one uploaded document.

---

## Clear Knowledge Base

```
DELETE /llm/files
```

Deletes all vectors from Qdrant.

---

# Sample Postman Requests

## Upload Document

**POST**

```
http://127.0.0.1:8000/llm/upload
```

Body → form-data

```
files : sample.pdf
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

## Ask Question

**POST**

```
http://127.0.0.1:8000/llm/kb
```

Body

```json
{
    "query":"What is Artificial Intelligence?"
}
```

---

## View Uploaded Files

```
GET http://127.0.0.1:8000/llm/files
```

---

## Delete Document

```
DELETE http://127.0.0.1:8000/llm/files/{document_id}
```

---

## Clear Knowledge Base

```
DELETE http://127.0.0.1:8000/llm/files
```

---

# Logging

Application logs include:

- API requests
- Upload status
- Metadata extraction
- Embedding generation
- Qdrant operations
- Chat requests
- Exceptions

Logs are stored inside the `logs/` directory.

---

# Troubleshooting

| Problem | Cause | Solution |
|----------|-------|----------|
| 500 Internal Server Error | Missing OpenRouter API Key | Verify `OPENROUTER_API_KEY` in `.env` |
| Qdrant Connection Failed | Qdrant not running | Start Qdrant before running the application |
| No Answer Returned | No documents uploaded | Upload documents before querying |
| Collection Not Found | Qdrant database is empty | Upload a document to create/populate the collection |
| Invalid PDF | Unsupported or corrupted file | Upload a valid PDF document |
| ModuleNotFoundError | Missing dependencies | Run `pip install -r requirements.txt` |
| Embedding Model Download Error | Internet unavailable | Ensure internet access during the first run |

---

# Future Enhancements

- OCR Support
- Hybrid Search
- Metadata Filtering
- Authentication
- Role-based Access
- Docker Deployment
- CI/CD Pipeline
- Unit Tests
- Integration Tests
- Streaming Responses
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

This project follows:

- Modular Architecture
- SOLID Principles
- DRY Principle
- Type Hints
- Structured Logging
- Environment-based Configuration
- Custom Exception Handling
- Feature Branch Development Workflow
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

**CK AI Agent – Knowledge Base Module**

Developed as part of the CK AI Agent project.
Developed as part of the **CK AI Agent** project.
