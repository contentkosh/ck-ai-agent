# CK AI Agent

CK AI Agent is a FastAPI application that allows users to upload PDF documents, store their embeddings in Qdrant, and ask questions about those documents using a locally running language model.

The application uses a Retrieval-Augmented Generation (RAG) pipeline to retrieve relevant information from uploaded documents and generate context-based answers.

The complete application supports both CPU-only and NVIDIA GPU execution. An NVIDIA GPU is optional.

## Current Technology Stack

| Component               | Technology                    | Purpose                                            |
| ----------------------- | ----------------------------- | -------------------------------------------------- |
| Language                | Python 3.12                   | Runs the backend                                   |
| API                     | FastAPI                       | Provides HTTP endpoints                            |
| ASGI server             | Uvicorn                       | Runs the API                                       |
| Validation              | Pydantic                      | Validates request and response data                |
| Vector database         | Qdrant                        | Stores embeddings and searches for relevant chunks |
| Database runtime        | Docker                        | Runs Qdrant locally                                |
| PDF processing          | pypdf                         | Reads PDF files                                    |
| Chunking                | Project's local text splitter | Splits extracted text into chunks                  |
| Embeddings              | Sentence Transformers         | Converts text into vectors                         |
| Embedding model         | BAAI/bge-base-en-v1.5         | Generates 768-dimensional embeddings               |
| Deep-learning framework | PyTorch                       | Runs the embedding model and local LLM             |
| GPU acceleration        | CUDA                          | Optional acceleration for NVIDIA GPUs              |
| Local LLM               | LiquidAI/LFM2-1.2B-RAG        | Generates answers                                  |
| Model runtime           | Hugging Face Transformers     | Loads and runs the local LLM                       |
| Cache                   | Qdrant                        | Stores semantically similar previous answers       |
| Logging                 | Python logging                | Records application activity and errors            |
| Testing                 | pytest                        | Runs automated tests                               |

PyTorch is used by both Sentence Transformers and Transformers.

The application supports CPU execution without CUDA. When a compatible NVIDIA GPU and CUDA-enabled PyTorch installation are available, GPU acceleration can be used.

## RAG Workflow

### Document Ingestion

```text
PDF upload
    |
    v
Validate PDF files
    |
    v
Extract text page by page
    |
    v
Split text into chunks
    |
    v
Generate embeddings (BGE, 768 dimensions)
    |
    v
Save vectors and payload in Qdrant
```

### Question Answering

```text
User question
    |
    v
Generate query embedding
    |
    v
Check semantic cache
    |
    +---- Cache hit ----> Return cached answer
    |
    v
Search Qdrant using business_id and course_ids
    |
    v
Build context from retrieved chunks
    |
    v
Generate answer using local LLM
    |
    v
Save answer in semantic cache
    |
    v
Return answer
```

If the cache lookup fails, the query pipeline can continue with Knowledge Base retrieval. If writing to the cache fails, the generated answer can still be returned.

## How Documents Are Organized in Qdrant

The application uses a separate Knowledge Base collection for each business.

The collection name follows this pattern:

```text
kb_{business_id}_bge
```

For example, the business ID `Mukund` uses:

```text
kb_mukund_bge
```

The cache has a separate collection for that business:

```text
cache_mukund_bge
```

Course IDs are stored in each point's payload. They are not separate Qdrant collections.

An upload request accepts:

- One `business_id`
- One or more `course_ids`
- One or more PDF files

Every uploaded PDF in that request is associated with all the supplied course IDs.

For example, if an upload contains three PDFs and `course_ids` is `["ncert", "upsc"]`, every chunk from all three PDFs stores both course IDs.

When querying with more than one course ID, retrieval uses OR matching: a chunk is eligible if it contains at least one of the selected course IDs.

The business ID keeps each business's collection separate.

Uploading a document again creates new document and chunk points. It does not automatically replace an older upload just because the filename or course IDs are the same.

## Models

The project uses two separate local models:

1. An embedding model for converting text into vectors.
2. A language model for generating answers.

Both models use PyTorch and can run on a CPU.

### Embedding Model

The current embedding model is:

```text
BAAI/bge-base-en-v1.5
```

- Runs locally through Sentence Transformers.
- Produces 768-dimensional embeddings.
- Uses CUDA when PyTorch detects a compatible NVIDIA GPU.
- Falls back to CPU when CUDA is unavailable.

The same embedding model and vector dimension must be used for both document ingestion and question embedding.

Existing Qdrant collections must have the matching vector dimension.

### Local Language Model

The current local LLM is:

```text
LiquidAI/LFM2-1.2B-RAG
```

The application loads it from:

```text
models/LFM2-1.2B-RAG/
```

It is loaded using Hugging Face Transformers and PyTorch.

The model files must already be present in that directory because the application loads the model locally.

The language model does not require an internet connection for inference after its model files have been downloaded, provided all required files are available locally.

### CPU-only Execution

The application can run completely on a CPU-only machine.

In CPU-only mode:

- PDF extraction runs on the CPU.
- Embedding generation runs on the CPU.
- Vector retrieval is handled by Qdrant.
- Local LLM inference runs on the CPU.
- CUDA is not required.

CPU execution will generally be slower than GPU execution, particularly during embedding generation and language model inference.

The tester should ensure that sufficient system RAM is available for loading both models and processing documents.

Closing unnecessary applications can help when memory is limited.

## Project Structure

```text
ck-ai-agent/
├── api/
│   ├── app.py
│   ├── dependencies.py
│   └── routes/
│       ├── file_routes.py
│       ├── health_routes.py
│       ├── kb_routes.py
│       └── upload_routes.py
├── common/
│   ├── collection_utils.py
│   ├── custom_exceptions.py
│   ├── embedding_client.py
│   ├── exception_handler.py
│   ├── file_utils.py
│   ├── llm_client.py
│   └── logger.py
├── configuration/
│   ├── config.py
│   ├── constants.py
│   ├── context.py
│   └── middleware.py
├── database/
│   ├── collection_setup.py
│   └── qdrant_client_manager.py
├── db_scripts/
├── dto/
├── exceptions/
├── models/
│   └── LFM2-1.2B-RAG/
├── repositories/
│   ├── cache_repository.py
│   └── kb_repository.py
├── services/
│   ├── cache_service.py
│   ├── file_service.py
│   ├── kb_ingestion_service.py
│   ├── kb_query_service.py
│   ├── kb_service.py
│   └── query_job_manager.py
├── validators/
├── logs/
├── uploads/
├── main.py
├── requirements.txt
└── README.md
```

## Requirements

The following software and resources are required to run the complete application.

- Python 3.12.
- Docker Desktop or another Docker installation for local Qdrant.
- CPU-compatible PyTorch installation.
- Sufficient system RAM for the embedding model and local LLM.
- Internet access during the initial installation and model downloads.
- Local `LFM2-1.2B-RAG` model files in `models/LFM2-1.2B-RAG/`.

An NVIDIA GPU is optional.

The application can run without CUDA using CPU-compatible PyTorch.

### Hardware Considerations

The complete application loads two local models.

The embedding model is used during document ingestion and question retrieval. The local LLM is used to generate answers.

CPU-only execution is supported, but:

- Initial model loading can take longer.
- Large PDF files may take longer to process.
- Embedding generation may be slower.
- LLM response generation may take longer.
- Available system RAM can affect whether both models can run comfortably.

The exact performance depends on the processor, available RAM, document size, and number of concurrent requests.

## Setup

### 1. Install Python

Install Python 3.12.

Verify the installation:

```powershell
python --version
```

Expected output:

```text
Python 3.12.x
```

### 2. Create and Activate a Virtual Environment

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Upgrade pip

```powershell
python -m pip install --upgrade pip
```

### 4. Install PyTorch

Choose the installation appropriate for the tester's hardware.

#### A. CPU-only installation (recommended for testers without an NVIDIA GPU)

Install CPU-compatible PyTorch:

```powershell
python -m pip install torch==2.8.0 --index-url https://download.pytorch.org/whl/cpu
```

This installation does not require CUDA or an NVIDIA GPU.

#### B. NVIDIA GPU installation (optional)

For a compatible NVIDIA GPU and CUDA 12.8 environment:

```powershell
python -m pip install torch==2.8.0 torchvision==0.23.0 torchaudio==2.8.0 --index-url https://download.pytorch.org/whl/cu128
```

This step is only necessary when GPU acceleration is desired.

### 5. Install Project Dependencies

After installing the appropriate PyTorch build:

```powershell
python -m pip install -r requirements.txt
```

Check for dependency conflicts:

```powershell
python -m pip check
```

If the command reports dependency conflicts, resolve them before starting the application.

### 6. Verify PyTorch

Run:

```powershell
python -c "import torch; print('PyTorch:', torch.__version__); print('CUDA available:', torch.cuda.is_available()); print('Device:', 'CUDA' if torch.cuda.is_available() else 'CPU')"
```

For a CPU-only machine, expected output should indicate:

```text
CUDA available: False
Device: CPU
```

This is normal and does not indicate an installation problem.

## Download the Models

The application uses two models from Hugging Face.

Both must be downloaded before running the application for the first time.

Make sure the virtual environment is activated.

The project uses `huggingface_hub` for downloading the model files.

### A. Download the Embedding Model

The embedding model is:

```text
BAAI/bge-base-en-v1.5
```

It converts document chunks and user questions into 768-dimensional vectors.

Download it using:

```powershell
python -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='BAAI/bge-base-en-v1.5')"
```

The model will be downloaded into the Hugging Face cache on your system.

You do not need to download it again every time you start the application. Sentence Transformers will reuse the cached model.

Hugging Face repository:

https://huggingface.co/BAAI/bge-base-en-v1.5	

### B. Download the Local LLM

The language model is:

```text
LiquidAI/LFM2-1.2B-RAG
```

Unlike the embedding model, this model must be stored inside your project because the application loads it from a local directory.

First, create the model directory:

```powershell
New-Item -ItemType Directory -Force .\models\LFM2-1.2B-RAG
```

Download the model into that directory:

```powershell
python -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='LiquidAI/LFM2-1.2B-RAG', local_dir='models/LFM2-1.2B-RAG')"
```

After downloading, your project should contain:

```text
models/
└── LFM2-1.2B-RAG/
    ├── config.json
    ├── generation_config.json
    ├── model.safetensors
    ├── tokenizer.json
    ├── tokenizer_config.json
    └── ...
```

The exact files may vary depending on the repository.

Hugging Face repository:

https://huggingface.co/LiquidAI/LFM2-1.2B-RAG

If Hugging Face requires authentication, log in using:

```powershell
hf auth login
```

Follow the instructions to authenticate.

Never put your Hugging Face access token directly into your README or commit it to source control.

**Important:** The LLM is loaded locally. If the model files are missing from `models/LFM2-1.2B-RAG/`, the application will not be able to initialize the LLM.

### CPU-only Model Execution

On a CPU-only machine, the models will run without CUDA.

The tester does not need to install NVIDIA drivers or CUDA Toolkit.

The initial model download requires internet access, but subsequent inference can use the downloaded model files locally.

## Verify Both Models

Before starting the API, verify that both models can load successfully.

### A. Verify the Embedding Model

Run:

```powershell
python -c "from common.embedding_client import get_embedding_model; m=get_embedding_model(); e=m.encode('Testing embedding model'); print('Embedding shape:', e.shape); print('Device:', m.device); print('SUCCESS')"
```

Expected embedding shape:

```text
(768,)
```

On a CPU-only machine, the device should indicate CPU.

### B. Verify the Local LLM

Run:

```powershell
python -c "from common.llm_client import get_llm; llm=get_llm(); print('LLM initialized successfully')"
```

If both commands succeed, the models are ready to use.

The LLM initialization may take some time on a CPU-only machine.

## Configure Environment Variables

Create a `.env` file in the project root.

The following configuration reflects the current setup:

```dotenv
# API
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=True

# QDRANT
QDRANT_HOST=localhost
QDRANT_PORT=6333
KB_COLLECTION_PREFIX=kb_
CACHE_COLLECTION_PREFIX=cache_
SCROLL_LIMIT=5000

# EMBEDDINGS
EMBEDDING_MODEL=BAAI/bge-base-en-v1.5
EMBEDDING_DIMENSION=768

# CHUNKING
CHUNK_SIZE=500
CHUNK_OVERLAP=50

# FILE STORAGE
UPLOAD_FOLDER=uploads
MAX_FILE_SIZE=157286400

# QUERY VALIDATION
MAX_QUERY_LENGTH=1000

# EMBEDDING BATCH
EMBEDDING_BATCH_SIZE=32

# AUTHENTICATION
AUTH_ENABLED=False

# LOCAL LLM
LLM_MODEL_NAME=LFM2-1.2B-RAG
LLM_MAX_NEW_TOKENS=512

# CACHE
CACHE_ENABLED=True
CACHE_SIMILARITY_THRESHOLD=0.85
CACHE_TOP_K=1
MAX_CACHE_SIZE=5000
```

Do not commit a real `.env` file or secrets to source control.

Some settings are optional and use defaults in `configuration/config.py` when omitted.

Current defaults include:

| Setting                    |                  Default |
| -------------------------- | -----------------------: |
| `SEARCH_LIMIT`           |                    `5` |
| `SEARCH_SCORE_THRESHOLD` |                 `0.50` |
| `LLM_REPETITION_PENALTY` |                 `1.05` |
| `LOG_FILE_PATH`          | `logs/application.log` |
| `LOG_MAX_BYTES`          |     `10485760` (10 MB) |
| `LOG_BACKUP_COUNT`       |                    `5` |

`API_KEY` can be configured if API authentication is enabled. Protected endpoints require the configured key in the `X-API-Key` header.

With `AUTH_ENABLED=False`, API key verification is disabled.

## Start Qdrant Using Docker

Start Docker Desktop first.

Run:

```powershell
docker run -d `
  --name qdrant `
  -p 6333:6333 `
  -v qdrant_storage:/qdrant/storage `
  qdrant/qdrant
```

This creates a named Docker volume so Qdrant data survives container restarts.

If the container already exists, start it instead:

```powershell
docker start qdrant
```

Check whether it is running:

```powershell
docker ps
```

Open the Qdrant dashboard:

```text
http://localhost:6333/dashboard
```

Do not remove the `qdrant_storage` volume unless you intentionally want to delete the stored Qdrant data.

Qdrant runs independently of the application's PyTorch device. It does not require an NVIDIA GPU.

## Start the API

From the project root, with the virtual environment activated:

```powershell
python main.py
```

Open Swagger UI:

```text
http://127.0.0.1:8000/docs
```

Health endpoint:

```text
http://127.0.0.1:8000/
```

Stop the API using `Ctrl+C`.

The first application startup may take longer because the local embedding model and language model need to load into memory.

## API Endpoints

The exact request and response schemas are available in Swagger UI at `/docs`.

| Method     | Endpoint                     | Purpose                                   |
| ---------- | ---------------------------- | ----------------------------------------- |
| `GET`    | `/`                        | Health check                              |
| `POST`   | `/llm/upload`              | Upload and ingest PDF files               |
| `POST`   | `/llm/kb/query`            | Ask a question against the Knowledge Base |
| `GET`    | `/llm/kb`                  | Retrieve Knowledge Base records           |
| `GET`    | `/llm/files`               | List uploaded documents                   |
| `DELETE` | `/llm/files/{document_id}` | Delete a document and its chunks          |
| `DELETE` | `/llm/files`               | Clear a business's Knowledge Base         |
| `POST`   | `/query/{job_id}/stop`     | Request cancellation of a query job       |

### Upload PDFs

`POST /llm/upload` uses multipart form data:

- `business_id`: One business identifier.
- `course_ids`: One or more course IDs.
- `files`: One or more PDF files.

All files in the same upload request receive the same supplied course ID list.

For multiple files, provide multiple `files` entries in the multipart form data.

### Ask a Question

`POST /llm/kb/query` accepts JSON similar to:

```json
{
  "job_id": "job-001",
  "query": "Explain Megasporangium",
  "business_id": "Mukund",
  "course_ids": ["ncert"]
}
```

To search across multiple courses:

```json
{
  "job_id": "job-002",
  "query": "Explain Megasporangium",
  "business_id": "Mukund",
  "course_ids": ["ncert", "upsc"]
}
```

The course filter uses OR matching: a document chunk is eligible when it contains at least one of the requested course IDs.

## Job Tracking and Logs

Query jobs are managed by the application's in-memory query job manager.

The job manager keeps job status and results while the application process is running.

This means:

- Job records are lost when the application process restarts.
- The current in-memory manager is not shared between multiple worker processes.
- Completed jobs remain in memory unless the manager removes them.

Application logs are separate from job storage.

Logs are written to the configured log file, by default:

```text
logs/application.log
```

Logs help investigate a job even after its in-memory record is gone.

For production use, consider persistent job storage and centralized or durable log collection.

## Cache

When `CACHE_ENABLED=True`, the application checks a separate Qdrant cache collection for a semantically similar previous question.

If a suitable cached result is found, it can return that result without running Knowledge Base retrieval and LLM generation.

The current configuration uses:

- Similarity threshold: `0.85`
- Cache top K: `1`
- Maximum cache size setting: `5000`

The cache is scoped by business and uses course information during lookup and storage.

Cache behavior should be tested when changing course-selection rules to ensure cached answers are not reused across incompatible course selections.

## CPU-only Testing Checklist

Before testing the complete application on a machine without an NVIDIA GPU, verify the following:

1. Python 3.12 is installed.
2. The virtual environment is activated.
3. CPU-compatible PyTorch is installed.
4. `torch.cuda.is_available()` returns `False`.
5. All Python dependencies install successfully.
6. Both Hugging Face models are downloaded.
7. The embedding model loads successfully.
8. The local LLM loads successfully.
9. Docker Desktop is running.
10. Qdrant is running and accessible.
11. The `.env` file is configured.
12. The FastAPI application starts successfully.

### Functional Testing

After completing setup, test the complete application:

1. Open Swagger UI.
2. Check the health endpoint.
3. Upload a PDF document.
4. Confirm that PDF text extraction succeeds.
5. Confirm that text is split into chunks.
6. Confirm that embeddings are generated.
7. Confirm that vectors are inserted into Qdrant.
8. Submit a question about the uploaded document.
9. Verify that relevant chunks are retrieved.
10. Verify that the local LLM generates an answer.
11. Repeat the question to test semantic caching.
12. Retrieve the uploaded document list.
13. Test document deletion if required.

The first ingestion and query may take longer because model loading and CPU inference can be slower.

## Logging and Troubleshooting

Application logs are written to:

```text
logs/application.log
```

When a query or upload fails, check the application log and the terminal running Uvicorn.

Use the request ID and `job_id` to follow the relevant log entries.

### Qdrant Connection Fails

- Make sure Docker Desktop is running.
- Run `docker ps` and confirm the Qdrant container is running.
- Check `QDRANT_HOST` and `QDRANT_PORT` in `.env`.
- Confirm that port `6333` is available.

### Embedding Model Fails to Load

- Check that `sentence-transformers` and PyTorch are installed in the active virtual environment.
- Check that the configured embedding model can be loaded.
- Check whether the model files are available in the Hugging Face cache.
- Check CUDA with `torch.cuda.is_available()`.
- CPU execution is supported when CUDA is unavailable.

### Local LLM Fails to Load

- Confirm that `models/LFM2-1.2B-RAG/` exists and contains the model files.
- Check that Transformers and PyTorch are installed.
- Check available system RAM.
- On CPU-only systems, allow additional time for model initialization.
- Check the application logs for model-loading errors.

### CPU Inference Is Slow

CPU inference is generally slower than GPU inference.

If the application is responding slowly:

- Close unnecessary applications.
- Check available RAM.
- Avoid running multiple ingestion or query operations simultaneously during initial testing.
- Allow sufficient time for local LLM generation.
- Monitor CPU and memory usage through Windows Task Manager.

Slow CPU inference does not necessarily indicate an application failure.

### Qdrant Vector Dimension Mismatch

The current embedding model produces 768-dimensional vectors.

The Knowledge Base and cache collections must use the same vector dimension.

If an existing collection has a different dimension, it must be recreated and its documents re-ingested.

Back up data and confirm before deleting any collection.

### API Returns an Internal Server Error

- Check the full traceback in the terminal and `logs/application.log`.
- Use the request ID and job ID to locate the relevant entries.
- Confirm that Qdrant and both local models are available.

### Dependency Installation Fails

- Confirm that Python 3.12 is being used.
- Confirm that the correct virtual environment is activated.
- Install the CPU-only PyTorch build for CPU-only machines.
- Run `python -m pip check` to identify dependency conflicts.
- Avoid installing incompatible OpenAI SDK versions into the same environment.

## Important Notes

- Start Qdrant before sending ingestion or query requests.
- Download both models before starting the application for the first time.
- The embedding model is local BGE (`BAAI/bge-base-en-v1.5`).
- The local LLM is `LiquidAI/LFM2-1.2B-RAG`.
- Both models use PyTorch.
- CUDA is optional and is used when a compatible NVIDIA GPU is available.
- CPU-only execution is supported.
- CPU inference will generally be slower than GPU inference.
- Each business has its own Knowledge Base collection and cache collection.
- Course IDs are payload filters inside a business collection, not separate collections.
- Re-uploading a PDF does not automatically replace an earlier upload.
- Query job state is currently stored in application memory, not in Qdrant.
- Do not commit `.env`, API keys, or other secrets.
