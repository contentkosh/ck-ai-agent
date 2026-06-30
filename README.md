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

---

# Project Structure

```
Knowledge_Base_Project
│
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

---

# Installation

Clone the repository

```bash
git clone <repository-url>
cd Knowledge_Base_Project
```

Create a virtual environment

```bash
python -m venv .venv
```

Activate the environment

Windows

```bash
.venv\Scripts\activate
```

Linux / macOS

```bash
source .venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
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

---

# Author

**CK AI Agent – Knowledge Base Module**

Developed as part of the CK AI Agent project.