# Changelog

All notable changes to this project will be documented in this file.

---

## [0.0.1] - Initial Setup

### Added

* Initial FastAPI application setup
* Qdrant vector database integration
* Sentence Transformer embedding model
* Basic document ingestion pipeline
* Recursive text chunking
* Basic semantic search
* OpenRouter LLM integration
* Knowledge Base query API
* Initial project structure

---

## [0.0.2] - Knowledge Base Features

### Added

* PDF document ingestion
* Automatic embedding generation
* Qdrant vector storage
* Question answering using retrieved context
* Metadata storage with document chunks
* File upload support
* Basic logging

### Improved

* Chunking strategy
* Embedding generation workflow

---

## [0.0.3] - Project Refactoring

### Added

* Repository layer for database operations
* Service layer for business logic
* DTOs for request and response models
* Configuration management
* Environment variable support
* Request context implementation
* File utility helpers
* Custom exception handling
* Validation utilities
* Application logging

### Changed

* Removed direct database access from API layer
* Introduced layered architecture
* Improved code readability and maintainability

---

## [0.0.4] - Generic Knowledge Base

### Removed

* Hardcoded NCERT chapter mapping
* Subject-specific metadata
* Static document classification
* Filename-based document handling
* Auto tagger implementation

### Added

* LLM-based document metadata extraction
* Generic document ingestion pipeline
* Automatic title extraction
* Automatic document type detection
* Automatic semantic tag generation
* Automatic document summary generation
* Support for any PDF document

### Changed

* Refactored ingestion workflow to use a single pipeline
* Simplified metadata model
* Improved repository payload structure
* Updated chatbot to use generic document metadata
* Updated APIs for generic document support

---

## [0.0.5] - Production Readiness

### Added

* Health Check API
* File Search API
* Upload validation
* File size validation
* Repository helper methods
* Structured logging
* Request tracing
* Environment-specific configuration
* Clean project structure

### Improved

* Exception handling across all layers
* Logging at API, Service and Repository layers
* Performance of document ingestion
* Code organization
* Maintainability

---

## Upcoming

### Planned

* Delete document API
* Update document API
* Metadata filtering
* Hybrid search (Vector + Keyword)
* Batch ingestion
* Async processing
* OCR support for scanned PDFs
* Multi-format document support (DOCX, TXT, Markdown)
* Authentication and authorization
* Swagger API enhancements
