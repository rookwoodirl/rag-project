from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# Models for request/response payloads
class ChatRequest(BaseModel):
    query: str
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

