
# CK AI Agent

## Overview

CK AI Agent is a Knowledge Base Management System built using FastAPI, Qdrant, and Large Language Models (LLMs). It enables users to upload PDF documents, automatically extract document metadata, generate embeddings, store document chunks in a vector database, and retrieve accurate answers through semantic search.

The application follows a layered architecture with separate API, Service, Repository, and Validation layers, making it scalable, maintainable, and easy to test.

---
## Features

- Upload one or more PDF documents
- Automatic document metadata extraction using LLM
- PDF text extraction and intelligent chunking
- Embedding generation using Sentence Transformers
- Semantic vector search using Qdrant
- AI-powered Question Answering using OpenRouter LLM
- Knowledge Base retrieval
- View uploaded documents
- Delete individual documents
- Clear the entire Knowledge Base
- Structured request logging with unique Request IDs
- Global exception handling
- Request and Response DTOs
- Input validation
- Unit testing using Pytest
- HTML test report generation
- API testing using Postman

---


## Technology Stack

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

---

# Installation

## Clone the Repository

```bash
git clone <repository-url>
cd Knowledge_Base_Project
cd ck-ai-agent
```

## Install Dependencies

```bash
pip install -r requirements.txt
python -m pip install -r requirements.txt
```

---

# Docker & Qdrant Setup

## Install Docker Desktop

Download Docker Desktop from:

https://www.docker.com/products/docker-desktop/

Install Docker and ensure it is running.

---

## Pull the Qdrant Docker Image

```bash
docker pull qdrant/qdrant
```

---

## Start Qdrant

### Windows (PowerShell)

```bash
docker run -d `
  --name qdrant `
  -p 6333:6333 `
  -v qdrant_storage:/qdrant/storage `
  qdrant/qdrant
```

### Linux / macOS

```bash
docker run -d \
  --name qdrant \
  -p 6333:6333 \
  -v qdrant_storage:/qdrant/storage \
  qdrant/qdrant
```

---

## Verify Qdrant is Running

```bash
docker ps
```

Qdrant will be available at:

```
http://localhost:6333
```

---

# Postman Setup

## Install Postman

Download Postman from:

https://www.postman.com/downloads/

---

## Import the Postman Collection

1. Open Postman.
2. Click **Import**.
3. Select:

```
docs/postman/CK_AI_Agent_APIs.postman_collection.json
```

4. Import the collection.

---

## Configure Base URL

Run the FastAPI server locally:

```
http://127.0.0.1:8000
```

Use this as the base URL for all API requests.

---

# Running the Application

Run the application using:

```bash
python main.py
```

or

```bash
uvicorn api.app:app --reload
```

---

## Swagger Documentation

```
http://127.0.0.1:8000/docs
```

---

## OpenAPI Specification

```
http://127.0.0.1:8000/openapi.json
```

---

# API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/llm/upload` | Upload PDF documents |
| POST | `/llm/kb` | Query the Knowledge Base |
| GET | `/llm/files` | Retrieve uploaded documents |
| DELETE | `/llm/files/{document_id}` | Delete a specific document |
| DELETE | `/llm/files` | Clear the Knowledge Base |
| GET | `/health` | Health Check |

---

# Running Tests

Run all unit tests:

```bash
pytest
```

Generate an HTML report:

```bash
pytest --html=reports/report.html --self-contained-html
```

---

# Project Structure

```
ck-ai-agent/
│
├── api/
├── common/
├── configuration/
├── database/
├── dto/
├── exceptions/
├── repositories/
├── services/
├── tests/
├── validators/
├── docs/
│   └── postman/
│       └── CK_AI_Agent_APIs.postman_collection.json
├── requirements.txt
├── README.md
└── main.py
```

---

# Version

**Current Version:** 0.0.1

---

# Author

Developed as part of the **CK AI Agent** project.
