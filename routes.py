from fastapi import APIRouter, HTTPException, Body, Depends, Query, Path
import httpx
import os
import json
import base64
from models import ChatRequest, ChatResponse, WebSearchRequest, WebSearchResponse
from models import TicketCreate, TicketUpdate, TicketResponse, TicketList
from models import TicketCommentCreate, TicketCommentUpdate, TicketCommentResponse, TicketCommentList
from typing import Optional, List
from dotenv import load_dotenv
from ticket_service import TicketService

# Load environment variables from .env file
load_dotenv()

# Create API router
router = APIRouter()

@router.get("/")
def read_root():
    return {"status": "API is running"}

# Dependency to get ticket service
async def get_ticket_service():
    service = TicketService()
    try:
        return service
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Tickets API endpoints
@router.post("/tickets", response_model=TicketResponse, status_code=201)
async def create_ticket(
    request: TicketCreate,
    ticket_service: TicketService = Depends(get_ticket_service)
):
    try:
        ticket = await ticket_service.create_ticket(
            request.ticket_category,
            request.ticket_number,
            request.description
        )
        return ticket
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create ticket: {str(e)}")
    finally:
        await ticket_service.close()

@router.get("/tickets", response_model=TicketList)
async def list_tickets(
    category: Optional[str] = Query(None, description="Filter by ticket category"),
    active_only: bool = Query(True, description="Show only active tickets"),
    limit: int = Query(100, ge=1, le=1000, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    ticket_service: TicketService = Depends(get_ticket_service)
):
    try:
        result = await ticket_service.list_tickets(
            category=category,
            active_only=active_only,
            limit=limit,
            offset=offset
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list tickets: {str(e)}")
    finally:
        await ticket_service.close()

@router.get("/tickets/{ticket_number}", response_model=TicketResponse)
async def get_ticket(
    ticket_number: str = Path(..., description="The ticket number"),
    category: Optional[str] = Query(None, description="The ticket category"),
    include_history: bool = Query(False, description="Include all versions of the ticket"),
    ticket_service: TicketService = Depends(get_ticket_service)
):
    try:
        ticket = await ticket_service.get_ticket(
            ticket_number=ticket_number,
            ticket_category=category,
            include_history=include_history
        )
        
        if not ticket:
            raise HTTPException(status_code=404, detail=f"Ticket {ticket_number} not found")
            
        return ticket
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to get ticket: {str(e)}")
    finally:
        await ticket_service.close()

@router.put("/tickets/{ticket_number}", response_model=TicketResponse)
async def update_ticket(
    ticket_number: str = Path(..., description="The ticket number"),
    request: TicketUpdate = Body(...),
    ticket_service: TicketService = Depends(get_ticket_service)
):
    try:
        updated_ticket = await ticket_service.update_ticket(
            ticket_number=ticket_number,
            ticket_category=request.ticket_category,
            description=request.description
        )
        
        if not updated_ticket:
            raise HTTPException(status_code=404, detail=f"Ticket {ticket_number} not found")
            
        return updated_ticket
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to update ticket: {str(e)}")
    finally:
        await ticket_service.close()

@router.delete("/tickets/{ticket_number}", status_code=204)
async def delete_ticket(
    ticket_number: str = Path(..., description="The ticket number"),
    category: Optional[str] = Query(None, description="The ticket category"),
    hard_delete: bool = Query(False, description="Permanently delete the ticket"),
    ticket_service: TicketService = Depends(get_ticket_service)
):
    try:
        if hard_delete:
            result = await ticket_service.hard_delete_ticket(
                ticket_number=ticket_number,
                ticket_category=category
            )
            if result == 0:
                raise HTTPException(status_code=404, detail=f"Ticket {ticket_number} not found")
        else:
            result = await ticket_service.delete_ticket(
                ticket_number=ticket_number,
                ticket_category=category
            )
            if not result:
                raise HTTPException(status_code=404, detail=f"Ticket {ticket_number} not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to delete ticket: {str(e)}")
    finally:
        await ticket_service.close()

@router.post("/initialize-db", status_code=200)
async def initialize_database(
    ticket_service: TicketService = Depends(get_ticket_service)
):
    try:
        result = await ticket_service.initialize_db()
        if result:
            return {"status": "Database initialized successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to initialize database")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initializing database: {str(e)}")
    finally:
        await ticket_service.close()

class OpenAIClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        self.base_url = "https://api.openai.com/v1"
        
    async def chat(self, query: str, history: List[dict] = None) -> str:
        """Send a chat request to OpenAI GPT-4.1 Turbo."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Format the conversation history for OpenAI's API
        messages = []
        
        # Add history if provided
        if history:
            for msg in history:
                # Assuming history is in format [{"role": "user", "content": "..."}, ...]
                messages.append(msg)
        
        # Add the current query
        messages.append({"role": "user", "content": query})
        
        payload = {
            "model": "gpt-4-turbo",  # Use GPT-4.1 Turbo (gpt-4-turbo is the API name)
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                
                return data.get("choices", [{}])[0].get("message", {}).get("content", "")
                
            except httpx.HTTPError as e:
                raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")

# Dependency to get OpenAI client
async def get_openai_client():
    try:
        return OpenAIClient()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest = Body(...),
    openai_client: OpenAIClient = Depends(get_openai_client)
):
    try:
        response = await openai_client.chat(request.query, request.history)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing error: {str(e)}")

class PerplexityClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("PERPLEXITY_API_KEY")
        if not self.api_key:
            raise ValueError("Perplexity API key is required. Set PERPLEXITY_API_KEY environment variable.")
        self.base_url = "https://api.perplexity.ai"
        
    async def search(self, query: str, max_results: int = 5) -> list:
        """Perform a web search using Perplexity API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3-sonar-small-32k-online",
            "messages": [{"role": "user", "content": f"Search the web for: {query}. Return results as a list of websites with title, url, and a brief snippet. Only include factual information."}],
            "options": {"stream": False}
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/v2/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                
                # Extract results from the response
                # Format varies, so we'll do our best to parse and format consistently
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                # Try to parse out search results from the AI response
                parsed_results = self._parse_search_results(content, max_results)
                return parsed_results
                
            except httpx.HTTPError as e:
                raise HTTPException(status_code=500, detail=f"Perplexity API error: {str(e)}")
    
    def _parse_search_results(self, content: str, max_results: int) -> list:
        """Parse search results from the AI response."""
        # This is a simplified parser - in a real app, you'd want more robust parsing
        results = []
        
        # Try to extract results whether they're in a list format or paragraph format
        lines = content.split('\n')
        current_result = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for title/URL patterns
            if line.startswith(('- ', '• ', '* ', '1. ', '2. ')):
                # If we have a previous result, add it to results
                if current_result and 'title' in current_result:
                    results.append(current_result)
                    if len(results) >= max_results:
                        break
                
                current_result = {'title': line.lstrip('- •*123456789. ')}
                
            # Look for URLs
            elif 'http' in line and ('title' in current_result and 'url' not in current_result):
                # Extract URL - simple approach
                url_start = line.find('http')
                url_end = line.find(' ', url_start) if line.find(' ', url_start) != -1 else len(line)
                current_result['url'] = line[url_start:url_end]
                
            # Look for descriptions
            elif 'title' in current_result and 'snippet' not in current_result:
                current_result['snippet'] = line
        
        # Add the last result if we have one
        if current_result and 'title' in current_result and current_result not in results:
            if 'url' not in current_result:
                current_result['url'] = "https://example.com"  # Placeholder if URL wasn't found
            if 'snippet' not in current_result:
                current_result['snippet'] = "No description available."
            results.append(current_result)
        
        # If we couldn't parse structured results, create a fallback
        if not results:
            # Just split the content into chunks and create results
            chunks = content.split('\n\n')
            for i, chunk in enumerate(chunks[:max_results]):
                results.append({
                    'title': f"Result {i+1}",
                    'url': "https://perplexity.ai",
                    'snippet': chunk[:200] + "..." if len(chunk) > 200 else chunk
                })
        
        return results[:max_results]

# Dependency to get Perplexity client
async def get_perplexity_client():
    try:
        return PerplexityClient()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/web_search", response_model=WebSearchResponse)
async def web_search_endpoint(
    request: WebSearchRequest = Body(...),
    perplexity_client: PerplexityClient = Depends(get_perplexity_client)
):
    try:
        results = await perplexity_client.search(request.query, request.num_results)
        return WebSearchResponse(results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Web search error: {str(e)}")

# Ticket Comment API endpoints
@router.post("/tickets/{ticket_number}/comments", response_model=TicketCommentResponse, status_code=201)
async def create_ticket_comment(
    ticket_number: str = Path(..., description="The ticket number"),
    request: TicketCommentCreate = Body(...),
    ticket_service: TicketService = Depends(get_ticket_service)
):
    try:
        comment = await ticket_service.create_comment(
            request.ticket_category,
            ticket_number,
            request.author,
            request.content,
            request.links,
            request.attached_documents
        )
        return comment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create comment: {str(e)}")
    finally:
        await ticket_service.close()

@router.get("/tickets/{ticket_number}/comments", response_model=TicketCommentList)
async def get_ticket_comments(
    ticket_number: str = Path(..., description="The ticket number"),
    category: Optional[str] = Query(None, description="The ticket category"),
    limit: int = Query(100, ge=1, le=1000, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    ticket_service: TicketService = Depends(get_ticket_service)
):
    try:
        result = await ticket_service.get_comments(
            ticket_number=ticket_number,
            ticket_category=category,
            limit=limit,
            offset=offset
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get comments: {str(e)}")
    finally:
        await ticket_service.close()

@router.put("/tickets/comments/{comment_id}", response_model=TicketCommentResponse)
async def update_ticket_comment(
    comment_id: int = Path(..., description="The comment ID"),
    request: TicketCommentUpdate = Body(...),
    ticket_service: TicketService = Depends(get_ticket_service)
):
    try:
        updated_comment = await ticket_service.update_comment(
            comment_id=comment_id,
            content=request.content,
            links=request.links,
            attached_documents=request.attached_documents
        )
        
        if not updated_comment:
            raise HTTPException(status_code=404, detail=f"Comment with ID {comment_id} not found")
            
        return updated_comment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to update comment: {str(e)}")
    finally:
        await ticket_service.close()

@router.delete("/tickets/comments/{comment_id}", status_code=204)
async def delete_ticket_comment(
    comment_id: int = Path(..., description="The comment ID"),
    ticket_service: TicketService = Depends(get_ticket_service)
):
    try:
        result = await ticket_service.delete_comment(comment_id=comment_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"Comment with ID {comment_id} not found")
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to delete comment: {str(e)}")
    finally:
        await ticket_service.close() 