import os
import httpx
import json
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class RagieService:
    """Service for interacting with the RAGIE document API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the RAGIE service"""
        self.api_key = api_key or os.environ.get("RAGIE_API_KEY")
        if not self.api_key:
            raise ValueError("RAGIE API key is required. Set RAGIE_API_KEY environment variable.")
        
        self.base_url = "https://api.ragie.ai"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def create_document(self, 
                            file_content: bytes, 
                            filename: str, 
                            metadata: Optional[Dict[str, Any]] = None,
                            partition_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Upload a document to RAGIE
        
        Args:
            file_content: Binary content of the file
            filename: Name of the file
            metadata: Optional metadata to attach to the document
            partition_id: Optional partition ID to store the document in
        
        Returns:
            Response from RAGIE API with document details
        """
        try:
            url = f"{self.base_url}/documents"
            
            # Prepare form data
            form_data = {}
            
            if metadata:
                form_data["metadata"] = json.dumps(metadata)
            
            if partition_id:
                form_data["partition_id"] = partition_id
            
            files = {
                "file": (filename, file_content)
            }
            
            # Update headers for multipart form data (remove Content-Type)
            headers = self.headers.copy()
            headers.pop("Content-Type", None)
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    url,
                    headers=headers,
                    data=form_data,
                    files=files
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPError as e:
            print(f"Error creating document: {str(e)}")
            if hasattr(e, "response") and e.response:
                print(f"Response: {e.response.text}")
            raise
    
    async def create_document_raw(self, 
                               content: str, 
                               filename: str, 
                               content_type: str = "text/plain",
                               metadata: Optional[Dict[str, Any]] = None,
                               partition_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a document from raw text content
        
        Args:
            content: Text content of the document
            filename: Name to assign to the document
            content_type: MIME type of the content
            metadata: Optional metadata to attach to the document
            partition_id: Optional partition ID to store the document in
        
        Returns:
            Response from RAGIE API with document details
        """
        try:
            url = f"{self.base_url}/documents/raw"
            
            payload = {
                "content": content,
                "filename": filename,
                "content_type": content_type
            }
            
            if metadata:
                payload["metadata"] = metadata
            
            if partition_id:
                payload["partition_id"] = partition_id
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPError as e:
            print(f"Error creating document from raw content: {str(e)}")
            if hasattr(e, "response") and e.response:
                print(f"Response: {e.response.text}")
            raise
    
    async def create_document_from_url(self, 
                                    url: str, 
                                    metadata: Optional[Dict[str, Any]] = None,
                                    partition_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a document from a URL
        
        Args:
            url: URL to fetch content from
            metadata: Optional metadata to attach to the document
            partition_id: Optional partition ID to store the document in
        
        Returns:
            Response from RAGIE API with document details
        """
        try:
            api_url = f"{self.base_url}/documents/url"
            
            payload = {
                "url": url
            }
            
            if metadata:
                payload["metadata"] = metadata
            
            if partition_id:
                payload["partition_id"] = partition_id
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    api_url,
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPError as e:
            print(f"Error creating document from URL: {str(e)}")
            if hasattr(e, "response") and e.response:
                print(f"Response: {e.response.text}")
            raise
    
    async def get_document(self, document_id: str) -> Dict[str, Any]:
        """
        Get document details by ID
        
        Args:
            document_id: ID of the document to retrieve
        
        Returns:
            Document details
        """
        try:
            url = f"{self.base_url}/documents/{document_id}"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    url,
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPError as e:
            print(f"Error getting document: {str(e)}")
            if hasattr(e, "response") and e.response:
                print(f"Response: {e.response.text}")
            raise
    
    async def delete_document(self, document_id: str) -> Dict[str, Any]:
        """
        Delete a document by ID
        
        Args:
            document_id: ID of the document to delete
        
        Returns:
            Response from RAGIE API
        """
        try:
            url = f"{self.base_url}/documents/{document_id}"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.delete(
                    url,
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPError as e:
            print(f"Error deleting document: {str(e)}")
            if hasattr(e, "response") and e.response:
                print(f"Response: {e.response.text}")
            raise
    
    async def list_documents(self, 
                          partition_id: Optional[str] = None,
                          limit: int = 100,
                          offset: int = 0) -> Dict[str, Any]:
        """
        List documents 
        
        Args:
            partition_id: Optional partition ID to filter by
            limit: Maximum number of documents to return
            offset: Offset for pagination
        
        Returns:
            List of documents
        """
        try:
            url = f"{self.base_url}/documents"
            
            params = {
                "limit": limit,
                "offset": offset
            }
            
            if partition_id:
                params["partition_id"] = partition_id
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    url,
                    params=params,
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPError as e:
            print(f"Error listing documents: {str(e)}")
            if hasattr(e, "response") and e.response:
                print(f"Response: {e.response.text}")
            raise
    
    async def update_document_metadata(self, 
                                    document_id: str, 
                                    metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update document metadata
        
        Args:
            document_id: ID of the document to update
            metadata: New metadata to apply
        
        Returns:
            Updated document details
        """
        try:
            url = f"{self.base_url}/documents/{document_id}/metadata"
            
            payload = {
                "metadata": metadata
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.patch(
                    url,
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPError as e:
            print(f"Error updating document metadata: {str(e)}")
            if hasattr(e, "response") and e.response:
                print(f"Response: {e.response.text}")
            raise
    
    async def get_document_content(self, document_id: str) -> str:
        """
        Get document content
        
        Args:
            document_id: ID of the document
        
        Returns:
            Document content as text
        """
        try:
            url = f"{self.base_url}/documents/{document_id}/content"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    url,
                    headers=self.headers
                )
                response.raise_for_status()
                return response.text
                
        except httpx.HTTPError as e:
            print(f"Error getting document content: {str(e)}")
            if hasattr(e, "response") and e.response:
                print(f"Response: {e.response.text}")
            raise
    
    async def get_document_summary(self, document_id: str) -> Dict[str, Any]:
        """
        Get document summary
        
        Args:
            document_id: ID of the document
        
        Returns:
            Document summary
        """
        try:
            url = f"{self.base_url}/documents/{document_id}/summary"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    url,
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPError as e:
            print(f"Error getting document summary: {str(e)}")
            if hasattr(e, "response") and e.response:
                print(f"Response: {e.response.text}")
            raise
    
    async def retrieve(self, 
                    query: str, 
                    partition_id: Optional[str] = None,
                    document_ids: Optional[List[str]] = None,
                    top_k: int = 5) -> Dict[str, Any]:
        """
        Search/retrieve documents based on a query
        
        Args:
            query: The search query
            partition_id: Optional partition ID to search in
            document_ids: Optional list of document IDs to search within
            top_k: Number of results to return
        
        Returns:
            Search results with relevant document chunks
        """
        try:
            url = f"{self.base_url}/retrievals"
            
            payload = {
                "query": query,
                "top_k": top_k
            }
            
            if partition_id:
                payload["partition_id"] = partition_id
            
            if document_ids:
                payload["document_ids"] = document_ids
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPError as e:
            print(f"Error retrieving documents: {str(e)}")
            if hasattr(e, "response") and e.response:
                print(f"Response: {e.response.text}")
            raise 