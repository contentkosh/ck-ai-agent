# Changelog

## [0.0.2] - Semantic Cache & LLM Optimization

**JIRA:** CK-351
**Author:** Mukund Upadhyay

### Features

#### Semantic Answer Cache

- Implemented semantic answer caching using Qdrant.
- Added embedding-based cache retrieval before Knowledge Base search and LLM invocation.
- Added configurable semantic similarity threshold for cache matching.
- Added cache storage for user questions, embeddings, retrieved context, and generated answers.
- Added cache hit and cache miss handling to reduce unnecessary LLM calls.

#### LLM Context Optimization

- Integrated LLMLingua for context compression before LLM invocation.
- Added query-aware context compression to reduce the amount of retrieved context sent to the LLM.

### Improvements

- Improved Knowledge Base query flow by checking the semantic cache before performing vector retrieval and LLM inference.
- Improved configuration by adding configurable semantic cache settings.
- Improved code organization for cache-related services, repositories, and database utilities.

---


## [0.0.1] - Initial Release

**JIRA:** CK-350  
**Author:** Siddhidatri Singhal

### Features
- Developed Knowledge Base module using FastAPI with a layered architecture.
- Integrated Qdrant for vector storage and Sentence Transformers for embeddings.
- Added OpenRouter LLM integration for document metadata extraction and question answering.
- Implemented PDF upload, semantic chunking, embedding generation, and document ingestion.
- Added Knowledge Base search, Health Check, file management, and chatbot APIs.
- Introduced request/response DTOs, validators, structured logging, custom exceptions, and request context.
- Added environment-based configuration and utility/helper modules.

### Improvements
- Refactored API endpoints into modular route files for better maintainability.
- Replaced hardcoded document mapping with LLM-based metadata extraction.
- Improved repository structure, logging, validation, and overall code organization.

### Future Enhancements
- Hybrid search, metadata filtering, OCR support, asynchronous ingestion, authentication, and multi-format document support.