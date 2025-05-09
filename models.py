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