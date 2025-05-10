from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# Models for request/response payloads
class ChatRequest(BaseModel):
    query: str
    history: Optional[List[dict]] = []

class TicketChatRequest(BaseModel):
    query: str
    ticket_number: str
    ticket_category: Optional[str] = None
    history: Optional[List[dict]] = []

class ChatResponse(BaseModel):
    response: str

class WebSearchRequest(BaseModel):
    query: str
    num_results: Optional[int] = 5

class WebSearchResponse(BaseModel):
    results: List[dict]

class Document(BaseModel):
    """Document model representing a document in RAGIE"""
    id: str
    filename: str
    created_at: str
    status: str
    partition_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class DocumentList(BaseModel):
    """Response model for listing documents"""
    documents: List[Document]
    total: int

class DocumentCreate(BaseModel):
    """Model for creating a document from raw text content"""
    content: str
    filename: str
    content_type: str = "text/plain"
    metadata: Optional[Dict[str, Any]] = None
    partition_id: Optional[str] = None

class DocumentCreateFromUrl(BaseModel):
    """Model for creating a document from a URL"""
    url: str
    metadata: Optional[Dict[str, Any]] = None
    partition_id: Optional[str] = None

class DocumentUpdateMetadata(BaseModel):
    """Model for updating document metadata"""
    metadata: Dict[str, Any]

class DocumentContent(BaseModel):
    """Model representing document content"""
    content: str

class DocumentSummary(BaseModel):
    """Model representing document summary"""
    summary: str

class SearchQuery(BaseModel):
    """Model for document search/retrieval query"""
    query: str
    partition_id: Optional[str] = None
    document_ids: Optional[List[str]] = None
    top_k: int = Field(default=5, ge=1, le=100)

class SearchResult(BaseModel):
    """Model representing a search result"""
    document_id: str
    score: float
    content: str
    metadata: Optional[Dict[str, Any]] = None

class SearchResponse(BaseModel):
    """Response model for search/retrieval"""
    results: List[SearchResult]

# Todo Item Models
class TodoItemCreate(BaseModel):
    """Model for creating a todo item"""
    description: str
    position: Optional[int] = None

class TodoItemUpdate(BaseModel):
    """Model for updating a todo item"""
    description: Optional[str] = None
    done: Optional[bool] = None
    position: Optional[int] = None

class TodoItemResponse(BaseModel):
    """Model for todo item response"""
    id: int
    description: str
    done: bool
    position: int
    created_at: str
    updated_at: str
    ticket_number: str

class TodoItemList(BaseModel):
    """Response model for listing todo items"""
    todo_items: List[TodoItemResponse]
    total: int

# Ticket Models
class TicketCreate(BaseModel):
    """Model for creating a ticket"""
    ticket_category: str
    ticket_number: Optional[str] = None
    description: str = ""
    completion_criteria: Optional[str] = None

class TicketUpdate(BaseModel):
    """Model for updating a ticket"""
    ticket_category: Optional[str] = None
    description: Optional[str] = None
    completion_criteria: Optional[str] = None

class TicketResponse(BaseModel):
    """Model for ticket response"""
    id: int
    ticket_number: str
    ticket_category: str
    description: str
    completion_criteria: Optional[str] = None
    status: str
    created_at: str
    updated_at: str
    todo_items: List[TodoItemResponse] = []

class TicketList(BaseModel):
    """Response model for listing tickets"""
    tickets: List[TicketResponse]
    total: int
    limit: int
    offset: int

