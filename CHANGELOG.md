# Changelog

## [0.0.2] - Semantic Answer Cache

**JIRA:** CK-351
**Author:** Mukund Upadhyay

### Features

- Implemented semantic answer caching using Qdrant to reduce repeated LLM calls.
- Added a dedicated cache collection for storing question embeddings, answers, and metadata.
- Integrated cache lookup into the Knowledge Base query workflow.
- Configured cache settings through environment variables.
- Added cache repository and cache service layers for cache management.
- Added script to create the semantic cache collection.

### Improvements

- Updated Knowledge Base chat service to support cache hit and cache miss flow.
- Added similarity score support in API responses.
- Improved logging for cache retrieval and storage operations.
- Enhanced overall query performance for semantically similar requests.
- Updated project documentation with cache workflow and configuration details.

### Future Enhancements

- Cache eviction using LRU or TTL policy.
- Automatic cache cleanup for stale entries.
- Configurable cache expiration.
- Cache analytics and hit/miss metrics.
- Support for distributed cache synchronization.

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