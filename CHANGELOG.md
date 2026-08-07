# Changelog

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