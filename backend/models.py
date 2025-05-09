
from pydantic import BaseModel
from typing import List, Optional

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

