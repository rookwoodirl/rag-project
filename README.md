# RAG Project API

A FastAPI-based web server with endpoints for chat and web search functionality using OpenAI and Perplexity, with PostgreSQL database integration for ticket management.

## Setup

1. Install dependencies:
```
pip install -r requirements.txt
```

2. Set up environment variables:
Create a `.env` file in the root directory with:
```
PERPLEXITY_API_KEY=your_perplexity_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
POSTGRES_URL=postgresql://username:password@localhost:5432/database
```

You'll need to obtain API keys from Perplexity AI and OpenAI, and configure your PostgreSQL connection string.

3. Initialize the database:
After setting up PostgreSQL, initialize the database tables:
```
curl -X POST "http://localhost:8000/initialize-db"
```

## Running the Server

Start the web server with:
```
uvicorn main:app --reload
```

The server will be available at: http://127.0.0.1:8000

## API Endpoints

### Chat and Search
- `GET /`: Status check endpoint
- `POST /chat`: Chat endpoint that uses OpenAI GPT-4 Turbo
- `POST /web_search`: Web search endpoint that uses Perplexity AI to search the web

### Ticket Management
- `POST /tickets`: Create a new ticket
- `GET /tickets`: List tickets with filtering and pagination
- `GET /tickets/{ticket_number}`: Get a specific ticket
- `PUT /tickets/{ticket_number}`: Update a ticket (creates a new version)
- `DELETE /tickets/{ticket_number}`: Delete a ticket
- `POST /initialize-db`: Initialize the database tables

### Ticket Comments
- `POST /tickets/{ticket_number}/comments`: Add a comment to a ticket
- `GET /tickets/{ticket_number}/comments`: Get comments for a ticket
- `PUT /tickets/comments/{comment_id}`: Update a comment
- `DELETE /tickets/comments/{comment_id}`: Delete a comment

## Ticket System

The application includes a ticket management system with versioning:

- **Versioning**: Each update to a ticket creates a new version while preserving history
- **Soft Delete**: Tickets are soft-deleted by default (marked inactive)
- **Time Tracking**: Each version has valid_from/valid_to timestamps
- **Filtering**: Tickets can be filtered by category and active status
- **Pagination**: Results are paginated for performance
- **Comments**: Full support for adding, updating and deleting comments on tickets
- **Rich Content**: Comments support links and document attachments (stored as JSONB)

## Database Integration

The application uses PostgreSQL for data persistence. The `PostgresHandler` class in `db.py` provides:
- Single connection management (lightweight)
- Safe parameterized queries
- Transaction support
- Different query result formats (all rows, single row, single value, affected rows)

## Example Requests

### Create a Ticket
```bash
curl -X POST "http://localhost:8000/tickets" \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_category": "bug",
    "ticket_number": "BUG-123",
    "description": "Fix login page error"
  }'
```

### Update a Ticket
```bash
curl -X PUT "http://localhost:8000/tickets/BUG-123" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Fix login page authentication error"
  }'
```

### Add a Comment to a Ticket
```bash
curl -X POST "http://localhost:8000/tickets/BUG-123/comments" \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_category": "bug",
    "ticket_number": "BUG-123",
    "author": "John Doe",
    "content": "I found the root cause of this issue. It appears to be related to the authentication service.",
    "links": [
      {"url": "https://example.com/auth-docs", "title": "Auth Documentation"}
    ]
  }'
```

### Get Comments for a Ticket
```bash
curl -X GET "http://localhost:8000/tickets/BUG-123/comments"
```

### List Tickets
```bash
curl -X GET "http://localhost:8000/tickets?category=bug&limit=10&offset=0"
```

### Chat

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is machine learning?", "history": []}'
```

### Web Search

```bash
curl -X POST "http://localhost:8000/web_search" \
  -H "Content-Type: application/json" \
  -d '{"query": "latest news on AI", "num_results": 3}'
```

## API Documentation

FastAPI automatically generates documentation for the API, which can be accessed at:
- http://127.0.0.1:8000/docs - Swagger UI
- http://127.0.0.1:8000/redoc - ReDoc 