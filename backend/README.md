# RAG Project API

A FastAPI-based web server with endpoints for chat and web search functionality.

## Setup

1. Install dependencies:
```
pip install -r requirements.txt
```

## Running the Server

Start the web server with:
```
uvicorn main:app --reload
```

The server will be available at: http://127.0.0.1:8000

## API Endpoints

- `GET /`: Status check endpoint
- `POST /chat`: Chat endpoint that processes queries
- `POST /web_search`: Web search endpoint that returns search results

## API Documentation

FastAPI automatically generates documentation for the API, which can be accessed at:
- http://127.0.0.1:8000/docs - Swagger UI
- http://127.0.0.1:8000/redoc - ReDoc 