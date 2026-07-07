# CK AI Agent

## Overview

CK AI Agent is a Knowledge Base service that enables semantic document search using Large Language Models (LLMs) and the Qdrant vector database. Users can upload PDF documents, automatically extract document metadata, generate embeddings, store vectors in Qdrant, and retrieve relevant information using natural language queries.

---

## Features

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

---

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd ck-ai-agent
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

---

## Running the Application

Start the application using:

```bash
python main.py
```

Or run it directly with Uvicorn:

```bash
python -m uvicorn api.app:app --reload
```

---

## Coding Standards

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

## Future Enhancements

- OCR support
- Multiple document formats
- Hybrid semantic search
- Metadata-based filtering
- Authentication and authorization
- Streaming responses
- Docker deployment
- Unit testing
- Integration testing

- # Version

**Version:** 0.0.1

---

# Author

Developed as part of the **CK AI Agent** project.
