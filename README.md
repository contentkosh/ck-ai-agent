
# CK AI Agent

## Overview

CK AI Agent is a Knowledge Base Management System built using FastAPI, Qdrant, and Large Language Models (LLMs). It enables users to upload PDF documents, automatically extract document metadata, generate embeddings, store document chunks in a vector database, and retrieve accurate answers through semantic search.

The application follows a layered architecture with separate API, Service, Repository, and Validation layers, making it scalable, maintainable, and easy to test.

---

## Features

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

## Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.12 |
| Framework | FastAPI |
| LLM | OpenRouter (NVIDIA Nemotron) |
| Embeddings | Sentence Transformers |
| Vector Database | Qdrant |
| PDF Processing | PyPDF |
| Testing | Pytest |
| API Testing | Postman |

-----

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd ck-ai-agent
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Running the Application

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

**Version:** 0.0.1

---

## Author

Developed as part of the **CK AI Agent** project.
