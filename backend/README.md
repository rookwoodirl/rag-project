# RAG Project Backend

This backend provides an API for working with document-based RAG (Retrieval Augmented Generation) functionality using RAGIE.

## Setup

1. Create a virtual environment and install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

2. Set up environment variables by creating a `.env` file:
```
RAGIE_API_KEY=your_ragie_api_key_here
```

## Running the Server

Start the web server with:
```bash
uvicorn main:app --reload
```

The server will be available at: http://127.0.0.1:8000

## API Endpoints

### Document Management
- `POST /documents`: Upload a document file
- `POST /documents/raw`: Create a document from raw text content
- `POST /documents/url`: Create a document from a URL
- `GET /documents`: List all documents
- `GET /documents/{document_id}`: Get document details by ID
- `DELETE /documents/{document_id}`: Delete a document
- `PATCH /documents/{document_id}/metadata`: Update document metadata
- `GET /documents/{document_id}/content`: Get document content
- `GET /documents/{document_id}/summary`: Get document summary

### Search
- `POST /search`: Search/retrieve documents based on a query

## Example Requests

### Upload a Document
```bash
curl -X POST "http://localhost:8000/documents" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/document.pdf" \
  -F 'metadata={"title": "Example Document", "author": "John Doe"}'
```

### Create a Document from Text
```bash
curl -X POST "http://localhost:8000/documents/raw" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "This is a test document content.",
    "filename": "test.txt",
    "content_type": "text/plain",
    "metadata": {"source": "manual"}
  }'
```

### Search Documents
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "example search query",
    "top_k": 5
  }'
```

## API Documentation

FastAPI automatically generates documentation for the API, which can be accessed at:
- http://127.0.0.1:8000/docs - Swagger UI
- http://127.0.0.1:8000/redoc - ReDoc 