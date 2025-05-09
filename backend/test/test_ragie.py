#!/usr/bin/env python3

import os
import asyncio
import unittest
from pathlib import Path
import sys

# Add the parent directory to path so we can import the ragie_service
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ragie_service import RagieService

class TestRagieService(unittest.TestCase):
    """Test cases for the RAGIE document service"""
    
    def setUp(self):
        """Set up the test environment"""
        # Make sure the RAGIE_API_KEY is set
        if not os.environ.get("RAGIE_API_KEY"):
            self.skipTest("RAGIE_API_KEY environment variable not set")
        
        # Path to test document
        self.test_doc_path = Path(__file__).parent / "test-hello-world.txt"
        if not self.test_doc_path.exists():
            self.fail(f"Test document not found at {self.test_doc_path}")
        
        # Initialize service
        self.ragie_service = RagieService()
        
        # Store created document IDs for cleanup
        self.document_ids = []
    
    async def async_setUp(self):
        """Async setup - nothing to do here yet"""
        pass

    async def async_tearDown(self):
        """Clean up any created documents"""
        for doc_id in self.document_ids:
            try:
                await self.ragie_service.delete_document(doc_id)
                print(f"Deleted test document: {doc_id}")
            except Exception as e:
                print(f"Error deleting document {doc_id}: {e}")
    
    async def test_document_crud(self):
        """Test document creation, retrieval, update, and deletion"""
        # Read test document content
        with open(self.test_doc_path, "r") as f:
            content = f.read()
        
        # 1. Create document
        response = await self.ragie_service.create_document_raw(
            content=content,
            filename="test_hello_world.txt",
            metadata={"source": "test", "category": "documentation"}
        )
        
        self.assertIn("id", response, "Document creation failed")
        doc_id = response["id"]
        self.document_ids.append(doc_id)
        print(f"Created document with ID: {doc_id}")
        
        # 2. Get document
        doc = await self.ragie_service.get_document(doc_id)
        self.assertEqual(doc["id"], doc_id, "Document retrieval failed")
        self.assertEqual(doc["filename"], "test_hello_world.txt", "Filename doesn't match")
        
        # 3. Update document metadata
        updated = await self.ragie_service.update_document_metadata(
            doc_id, 
            {"source": "test", "category": "documentation", "status": "reviewed"}
        )
        self.assertEqual(updated["metadata"]["status"], "reviewed", "Metadata update failed")
        
        # 4. Get document content
        content_response = await self.ragie_service.get_document_content(doc_id)
        self.assertIn("Lorem ipsum", content_response, "Document content retrieval failed")
        
        # 5. List all documents
        docs = await self.ragie_service.list_documents()
        self.assertIn("documents", docs, "Document listing failed")
        self.assertGreaterEqual(len(docs["documents"]), 1, "Expected at least one document")
        
        # We'll skip actual deletion here as it's handled in tearDown
    
    async def test_search_retrieval(self):
        """Test document retrieval functionality"""
        # Read test document content
        with open(self.test_doc_path, "r") as f:
            content = f.read()
        
        # 1. Create document
        response = await self.ragie_service.create_document_raw(
            content=content,
            filename="retrieval_test.txt",
            metadata={"source": "test", "purpose": "retrieval test"}
        )
        
        doc_id = response["id"]
        self.document_ids.append(doc_id)
        print(f"Created document with ID: {doc_id} for retrieval test")
        
        # Wait a moment for indexing
        await asyncio.sleep(2)
        
        # 2. Retrieve documents with query
        retrieval = await self.ragie_service.retrieve(
            query="password reset mobile",
            top_k=5
        )
        
        self.assertIn("results", retrieval, "Retrieval results not found")
        
        # Check if our document is in the results
        found = False
        for result in retrieval["results"]:
            if result["document"]["id"] == doc_id:
                found = True
                break
        
        # This is not a strict requirement as retrieval depends on the model
        if not found:
            print("Note: Test document was not found in retrieval results. This may be normal depending on content relevance.")

    def test_run_async_tests(self):
        """Run all async tests"""
        loop = asyncio.get_event_loop()
        
        async def run_tests():
            await self.async_setUp()
            try:
                await self.test_document_crud()
                await self.test_search_retrieval()
            finally:
                await self.async_tearDown()
        
        loop.run_until_complete(run_tests())

if __name__ == "__main__":
    unittest.main() 