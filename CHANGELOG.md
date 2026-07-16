# Changelog

## [0.0.3] - LLMLingua Prompt Compression

**JIRA:** CK-
**Author:** Mukund Upadhyay

### Features
- Integrated LLMLingua-2 for prompt compression before LLM inference.
- Added a dedicated `llmlingua_service.py` for context compression.

### Improvements
- Reduced prompt size by compressing retrieved Knowledge Base context.
- Preserved the original context for semantic cache storage while sending the compressed context to the LLM.
- Improved LLM efficiency without changing the existing RAG workflow.

## [0.0.2] - Semantic Cache Enhancement

**JIRA:** CK-351
**Author:** Mukund Upadhyay

### Features
- Implemented semantic answer caching using Qdrant to reduce redundant LLM calls.
- Added cache repository and service layers for cache retrieval and storage.
- Introduced automatic cache hit detection using embedding similarity.
- Added cache collection creation script for Qdrant.
- Configured cache behaviour through environment-based settings.
- Added cache similarity threshold and cache management configuration.

### Improvements
- Merged configuration files into a single `app_settings.py` module.
- Refactored project imports to use centralized application settings.
- Improved document metadata extraction by handling JSON responses wrapped in Markdown code blocks.
- Updated Qdrant utility scripts to use centralized configuration.
- Cleaned and resolved merge conflicts after rebasing onto the latest `feature/knowledge-base-refactor-v2` branch.
- Improved project organization by removing duplicate configuration logic.
- Enhanced logging around Knowledge Base query processing and cache operations.

### Bug Fixes
- Fixed import inconsistencies introduced during branch rebasing.
- Resolved configuration and constant conflicts after merging application settings.
- Fixed metadata extraction failures caused by invalid JSON parsing.
- Corrected cache configuration and response validation.
- Updated Knowledge Base services to use centralized application configuration.
- Fixed Qdrant collection creation scripts after configuration refactoring.

### Future Enhancements
- Add cache expiration (TTL) support.
- Introduce cache invalidation on Knowledge Base updates.
- Implement cache analytics and monitoring.
- Support configurable cache replacement strategies.
- Optimize semantic cache retrieval with hybrid search.

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