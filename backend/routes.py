from fastapi import APIRouter, HTTPException, Body, Depends, File, UploadFile, Form, Query, Path
import httpx
import os
import json
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

from models import (
    Document, DocumentList, DocumentCreate, DocumentCreateFromUrl,
    DocumentUpdateMetadata, DocumentContent, DocumentSummary,
    SearchQuery, SearchResponse, SearchResult
)

from ragie_service import RagieService

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