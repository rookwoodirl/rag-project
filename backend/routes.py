from fastapi import APIRouter, HTTPException, Body, Depends, File, UploadFile, Form, Query, Path
import httpx
import os
import json
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

from models import (
    Document, DocumentList, DocumentCreate, DocumentCreateFromUrl,
    DocumentUpdateMetadata, DocumentContent, DocumentSummary,
    SearchQuery, SearchResponse, SearchResult,
    TicketCreate, TicketUpdate, TicketResponse, TicketList,
    TodoItemCreate, TodoItemUpdate, TodoItemResponse, TodoItemList
)

from ragie_service import RagieService
from ticket_service import TicketService

# Load environment variables from .env file
load_dotenv()

# Create API router
router = APIRouter()

@router.get("/")
def read_root():
    return {"status": "API is running"}

# Dependency to get RAGIE service
async def get_ragie_service():
    try:
        return RagieService()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

# Dependency to get ticket service
async def get_ticket_service():
    try:
        service = TicketService()
        return service
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

# Document API endpoints
@router.post("/documents", response_model=Document, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    metadata: Optional[str] = Form(None),
    partition_id: Optional[str] = Form(None),
    ragie_service: RagieService = Depends(get_ragie_service)
):
    """Upload a document file to RAGIE"""
    try:
        # Read file content
        content = await file.read()
        
        # Parse metadata if provided
        metadata_dict = None
        if metadata:
            try:
                metadata_dict = json.loads(metadata)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid metadata JSON format")
        
        # Create document
        document = await ragie_service.create_document(
            file_content=content,
            filename=file.filename,
            metadata=metadata_dict,
            partition_id=partition_id
        )
        
        return document
    except httpx.HTTPError as e:
        status_code = e.response.status_code if hasattr(e, "response") else 500
        detail = e.response.text if hasattr(e, "response") else str(e)
        raise HTTPException(status_code=status_code, detail=detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload document: {str(e)}")

@router.post("/documents/raw", response_model=Document, status_code=201)
async def create_document_raw(
    request: DocumentCreate = Body(...),
    ragie_service: RagieService = Depends(get_ragie_service)
):
    """Create a document from raw text content"""
    try:
        document = await ragie_service.create_document_raw(
            content=request.content,
            filename=request.filename,
            content_type=request.content_type,
            metadata=request.metadata,
            partition_id=request.partition_id
        )
        
        return document
    except httpx.HTTPError as e:
        status_code = e.response.status_code if hasattr(e, "response") else 500
        detail = e.response.text if hasattr(e, "response") else str(e)
        raise HTTPException(status_code=status_code, detail=detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create document: {str(e)}")

@router.post("/documents/url", response_model=Document, status_code=201)
async def create_document_from_url(
    request: DocumentCreateFromUrl = Body(...),
    ragie_service: RagieService = Depends(get_ragie_service)
):
    """Create a document from a URL"""
    try:
        document = await ragie_service.create_document_from_url(
            url=request.url,
            metadata=request.metadata,
            partition_id=request.partition_id
        )
        
        return document
    except httpx.HTTPError as e:
        status_code = e.response.status_code if hasattr(e, "response") else 500
        detail = e.response.text if hasattr(e, "response") else str(e)
        raise HTTPException(status_code=status_code, detail=detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create document from URL: {str(e)}")

@router.get("/documents", response_model=DocumentList)
async def list_documents(
    partition_id: Optional[str] = Query(None, description="Filter by partition ID"),
    limit: int = Query(100, ge=1, le=1000, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    ragie_service: RagieService = Depends(get_ragie_service)
):
    """List all documents"""
    try:
        result = await ragie_service.list_documents(
            partition_id=partition_id,
            limit=limit,
            offset=offset
        )
        
        return result
    except httpx.HTTPError as e:
        status_code = e.response.status_code if hasattr(e, "response") else 500
        detail = e.response.text if hasattr(e, "response") else str(e)
        raise HTTPException(status_code=status_code, detail=detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")

@router.get("/documents/{document_id}", response_model=Document)
async def get_document(
    document_id: str = Path(..., description="Document ID"),
    ragie_service: RagieService = Depends(get_ragie_service)
):
    """Get document details by ID"""
    try:
        document = await ragie_service.get_document(document_id)
        
        return document
    except httpx.HTTPError as e:
        status_code = e.response.status_code if hasattr(e, "response") else 500
        detail = e.response.text if hasattr(e, "response") else str(e)
        raise HTTPException(status_code=status_code, detail=detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get document: {str(e)}")

@router.delete("/documents/{document_id}", status_code=204)
async def delete_document(
    document_id: str = Path(..., description="Document ID"),
    ragie_service: RagieService = Depends(get_ragie_service)
):
    """Delete a document by ID"""
    try:
        await ragie_service.delete_document(document_id)
        
    except httpx.HTTPError as e:
        status_code = e.response.status_code if hasattr(e, "response") else 500
        detail = e.response.text if hasattr(e, "response") else str(e)
        raise HTTPException(status_code=status_code, detail=detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")

@router.patch("/documents/{document_id}/metadata")
async def update_document_metadata(
    document_id: str = Path(..., description="Document ID"),
    request: DocumentUpdateMetadata = Body(...),
    ragie_service: RagieService = Depends(get_ragie_service)
):
    """Update document metadata"""
    try:
        result = await ragie_service.update_document_metadata(
            document_id=document_id,
            metadata=request.metadata
        )
        
        return result
    except httpx.HTTPError as e:
        status_code = e.response.status_code if hasattr(e, "response") else 500
        detail = e.response.text if hasattr(e, "response") else str(e)
        raise HTTPException(status_code=status_code, detail=detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update document metadata: {str(e)}")

@router.get("/documents/{document_id}/content", response_model=DocumentContent)
async def get_document_content(
    document_id: str = Path(..., description="Document ID"),
    ragie_service: RagieService = Depends(get_ragie_service)
):
    """Get document content"""
    try:
        content = await ragie_service.get_document_content(document_id)
        
        return {"content": content}
    except httpx.HTTPError as e:
        status_code = e.response.status_code if hasattr(e, "response") else 500
        detail = e.response.text if hasattr(e, "response") else str(e)
        raise HTTPException(status_code=status_code, detail=detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get document content: {str(e)}")

@router.get("/documents/{document_id}/summary", response_model=DocumentSummary)
async def get_document_summary(
    document_id: str = Path(..., description="Document ID"),
    ragie_service: RagieService = Depends(get_ragie_service)
):
    """Get document summary"""
    try:
        summary = await ragie_service.get_document_summary(document_id)
        
        return summary
    except httpx.HTTPError as e:
        status_code = e.response.status_code if hasattr(e, "response") else 500
        detail = e.response.text if hasattr(e, "response") else str(e)
        raise HTTPException(status_code=status_code, detail=detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get document summary: {str(e)}")

@router.post("/search", response_model=SearchResponse)
async def search_documents(
    request: SearchQuery = Body(...),
    ragie_service: RagieService = Depends(get_ragie_service)
):
    """Search/retrieve documents based on a query"""
    try:
        results = await ragie_service.retrieve(
            query=request.query,
            partition_id=request.partition_id,
            document_ids=request.document_ids,
            top_k=request.top_k
        )
        
        return results
    except httpx.HTTPError as e:
        status_code = e.response.status_code if hasattr(e, "response") else 500
        detail = e.response.text if hasattr(e, "response") else str(e)
        raise HTTPException(status_code=status_code, detail=detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search documents: {str(e)}")

# Ticket API endpoints
@router.post("/tickets", response_model=TicketResponse, status_code=201)
async def create_ticket(
    request: TicketCreate = Body(...),
    ticket_service: TicketService = Depends(get_ticket_service)
):
    """Create a new ticket"""
    try:
        ticket = await ticket_service.create_ticket(
            request.ticket_category,
            request.ticket_number,
            request.description,
            request.completion_criteria
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
    include_todos: bool = Query(False, description="Include todo items"),
    limit: int = Query(100, ge=1, le=1000, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    ticket_service: TicketService = Depends(get_ticket_service)
):
    """List all tickets with optional filtering"""
    try:
        result = await ticket_service.list_tickets(
            category=category,
            active_only=active_only,
            include_todos=include_todos,
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
    include_history: bool = Query(False, description="Include ticket history"),
    ticket_service: TicketService = Depends(get_ticket_service)
):
    """Get a specific ticket by number"""
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
    """Update a ticket"""
    try:
        updated_ticket = await ticket_service.update_ticket(
            ticket_number=ticket_number,
            ticket_category=request.ticket_category,
            description=request.description,
            completion_criteria=request.completion_criteria
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
    """Delete a ticket (soft delete by default)"""
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
    """Initialize database tables and create sample data if needed"""
    try:
        # Initialize database tables
        result = await ticket_service.initialize_db()
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to initialize database")
        
        # Create sample tickets if none exist
        conn = await ticket_service.get_connection()
        try:
            count = await conn.fetchval("SELECT COUNT(*) FROM tickets")
            
            if count == 0:
                # Create sample tickets
                await ticket_service.create_ticket(
                    ticket_category="Vacation", 
                    description="Plan summer vacation to Italy",
                    completion_criteria="Flights, hotels, and itinerary booked"
                )
                
                await ticket_service.create_ticket(
                    ticket_category="Home Renovation", 
                    description="Kitchen remodeling project",
                    completion_criteria="New cabinets, countertops, and appliances installed"
                )
                
                await ticket_service.create_ticket(
                    ticket_category="Fitness", 
                    description="Training for half marathon",
                    completion_criteria="Complete a 21km run"
                )
                
                sample_ticket = await ticket_service.get_ticket("VAC", include_todos=False)
                if sample_ticket:
                    # Add some todo items
                    await ticket_service.add_todo_item(
                        ticket_number=sample_ticket['ticket_number'],
                        description="Research destinations"
                    )
                    
                    await ticket_service.add_todo_item(
                        ticket_number=sample_ticket['ticket_number'],
                        description="Book flights"
                    )
                    
                    await ticket_service.add_todo_item(
                        ticket_number=sample_ticket['ticket_number'],
                        description="Reserve accommodations"
                    )
        finally:
            await ticket_service.pool.release(conn)
        
        return {"message": "Database initialized successfully"}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to initialize database: {str(e)}")

# Todo Item API endpoints
@router.post("/tickets/{ticket_number}/todos", response_model=TodoItemResponse, status_code=201)
async def create_todo_item(
    ticket_number: str = Path(..., description="The ticket number"),
    request: TodoItemCreate = Body(...),
    ticket_service: TicketService = Depends(get_ticket_service)
):
    """Add a todo item to a ticket"""
    try:
        todo_item = await ticket_service.add_todo_item(
            ticket_number=ticket_number,
            description=request.description,
            position=request.position
        )
        return todo_item
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add todo item: {str(e)}")
    finally:
        await ticket_service.close()

@router.get("/tickets/{ticket_number}/todos", response_model=List[TodoItemResponse])
async def list_todo_items(
    ticket_number: str = Path(..., description="The ticket number"),
    ticket_service: TicketService = Depends(get_ticket_service)
):
    """Get all todo items for a ticket"""
    try:
        todo_items = await ticket_service.get_todo_items(ticket_number)
        return todo_items
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get todo items: {str(e)}")
    finally:
        await ticket_service.close()

@router.put("/todos/{todo_id}", response_model=TodoItemResponse)
async def update_todo_item(
    todo_id: int = Path(..., description="The todo item ID"),
    request: TodoItemUpdate = Body(...),
    ticket_service: TicketService = Depends(get_ticket_service)
):
    """Update a todo item"""
    try:
        updated_item = await ticket_service.update_todo_item(
            todo_id=todo_id,
            description=request.description,
            done=request.done,
            position=request.position
        )
        
        if not updated_item:
            raise HTTPException(status_code=404, detail=f"Todo item with ID {todo_id} not found")
            
        return updated_item
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to update todo item: {str(e)}")
    finally:
        await ticket_service.close()

@router.delete("/todos/{todo_id}", status_code=204)
async def delete_todo_item(
    todo_id: int = Path(..., description="The todo item ID"),
    ticket_service: TicketService = Depends(get_ticket_service)
):
    """Delete a todo item"""
    try:
        result = await ticket_service.delete_todo_item(todo_id=todo_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"Todo item with ID {todo_id} not found")
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to delete todo item: {str(e)}")
    finally:
        await ticket_service.close() 
