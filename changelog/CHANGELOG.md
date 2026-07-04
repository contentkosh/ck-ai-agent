# Changelog

## [0.0.1] - Initial Release

**JIRA:** CK-350  
**Author:** Siddhidatri Singhal

### Added

- Initial FastAPI application setup
- Layered architecture (API, Service, Repository)
- Qdrant vector database integration
- Sentence Transformer embedding model
- OpenRouter LLM integration
- Generic PDF document ingestion pipeline
- Automatic LLM-based document metadata extraction
- Semantic text chunking
- Embedding generation and vector storage
- Knowledge Base question answering
- Health Check API
- File upload support
- Request and response DTOs
- Configuration management
- Request context implementation
- File utility helpers
- Repository helper methods
- Input validation
- Structured logging
- Custom exception handling
- Environment-based configuration

### Changed

- Refactored project into a modular layered architecture
- Replaced hardcoded document mapping with LLM-based metadata extraction
- Simplified the document ingestion workflow
- Improved repository payload structure
- Updated chatbot to support generic document metadata
- Enhanced logging, exception handling, and code maintainability

### Removed

- Hardcoded NCERT chapter mapping
- Subject-specific metadata
- Static document classification
- Filename-based document handling
- Auto tagger implementation

### Planned

- Delete document update support
- Metadata-based filtering
- Hybrid search (Vector + Keyword)
- Batch document ingestion
- Asynchronous processing
- OCR support for scanned PDFs
- Multi-format document support (DOCX, TXT, Markdown)
- Authentication and authorization
- Swagger API enhancements