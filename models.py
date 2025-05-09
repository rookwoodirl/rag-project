from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

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

# Ticket models
class TicketBase(BaseModel):
    ticket_category: str
    ticket_number: str
    description: str

class TicketCreate(TicketBase):
    pass

class TicketUpdate(BaseModel):
    ticket_category: Optional[str] = None
    description: Optional[str] = None

class TicketResponse(TicketBase):
    id: int
    version: int
    valid_from: datetime
    valid_to: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True

class TicketList(BaseModel):
    tickets: List[TicketResponse]
    total: int

# Ticket comment models
class Link(BaseModel):
    url: str
    title: Optional[str] = None

class Document(BaseModel):
    name: str
    content_type: str
    size: int
    url: str

class TicketCommentBase(BaseModel):
    ticket_category: str
    ticket_number: str
    author: str
    content: str
    links: Optional[List[Link]] = None
    attached_documents: Optional[List[Document]] = None

class TicketCommentCreate(TicketCommentBase):
    pass

class TicketCommentUpdate(BaseModel):
    content: Optional[str] = None
    links: Optional[List[Link]] = None
    attached_documents: Optional[List[Document]] = None

class TicketCommentResponse(TicketCommentBase):
    id: int
    timestamp: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TicketCommentList(BaseModel):
    comments: List[TicketCommentResponse]
    total: int 