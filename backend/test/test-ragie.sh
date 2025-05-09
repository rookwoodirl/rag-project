#!/bin/bash

# Set the API base URL
API_URL="http://localhost:8000"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Testing RAGIE Document Functionality${NC}"
echo "=============================="

# Test 1: Check if API is running
echo -e "\n${YELLOW}TEST 1: Check if API is running${NC}"
RESPONSE=$(curl -s $API_URL/)
echo "Response: $RESPONSE"
if [[ $RESPONSE == *"API is running"* ]]; then
    echo -e "${GREEN}✓ API is running${NC}"
else
    echo -e "${RED}✗ API is not running${NC}"
    exit 1
fi

# Prepare test document path
TEST_DOC_PATH="backend/test/test-hello-world.txt"
if [ ! -f "$TEST_DOC_PATH" ]; then
    echo -e "${RED}Test document not found at $TEST_DOC_PATH${NC}"
    exit 1
fi

# Test 2: Upload a document using raw content
echo -e "\n${YELLOW}TEST 2: Upload document using raw content${NC}"
DOC_CONTENT=$(cat $TEST_DOC_PATH)
RESPONSE=$(curl -s -X POST $API_URL/documents/raw \
    -H "Content-Type: application/json" \
    -d "{\"content\": \"$DOC_CONTENT\", \"filename\": \"hello_world.txt\", \"metadata\": {\"source\": \"test\", \"category\": \"documentation\"}}")
echo "Response: $RESPONSE"

if [[ $RESPONSE == *"id"* ]]; then
    echo -e "${GREEN}✓ Document uploaded successfully${NC}"
    # Extract document ID for later use
    DOCUMENT_ID=$(echo $RESPONSE | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
    echo "Document ID: $DOCUMENT_ID"
else
    echo -e "${RED}✗ Failed to upload document${NC}"
    exit 1
fi

# Test 3: Get document details
echo -e "\n${YELLOW}TEST 3: Get document details${NC}"
RESPONSE=$(curl -s $API_URL/documents/$DOCUMENT_ID)
echo "Response: $RESPONSE"
if [[ $RESPONSE == *"$DOCUMENT_ID"* ]]; then
    echo -e "${GREEN}✓ Retrieved document details${NC}"
else
    echo -e "${RED}✗ Failed to retrieve document details${NC}"
fi

# Test 4: Get document content
echo -e "\n${YELLOW}TEST 4: Get document content${NC}"
RESPONSE=$(curl -s $API_URL/documents/$DOCUMENT_ID/content)
echo "Response: $RESPONSE"
if [[ $RESPONSE == *"Lorem ipsum"* ]]; then
    echo -e "${GREEN}✓ Retrieved document content${NC}"
else
    echo -e "${RED}✗ Failed to retrieve document content${NC}"
fi

# Test 5: Update document metadata
echo -e "\n${YELLOW}TEST 5: Update document metadata${NC}"
RESPONSE=$(curl -s -X PATCH $API_URL/documents/$DOCUMENT_ID/metadata \
    -H "Content-Type: application/json" \
    -d '{"metadata": {"source": "test", "category": "documentation", "status": "reviewed"}}')
echo "Response: $RESPONSE"
if [[ $RESPONSE == *"status"* && $RESPONSE == *"reviewed"* ]]; then
    echo -e "${GREEN}✓ Updated document metadata${NC}"
else
    echo -e "${RED}✗ Failed to update document metadata${NC}"
fi

# Test 6: Retrieve relevant documents
echo -e "\n${YELLOW}TEST 6: Retrieve relevant documents${NC}"
RESPONSE=$(curl -s -X POST $API_URL/retrievals \
    -H "Content-Type: application/json" \
    -d '{"query": "password reset mobile", "top_k": 3}')
echo "Response: $RESPONSE"
if [[ $RESPONSE == *"results"* ]]; then
    echo -e "${GREEN}✓ Retrieved documents based on query${NC}"
    
    # Check if our document is in results
    if [[ $RESPONSE == *"$DOCUMENT_ID"* ]]; then
        echo -e "${GREEN}✓ Test document found in search results${NC}"
    else
        echo -e "${YELLOW}⚠ Test document not found in search results${NC}"
    fi
else
    echo -e "${RED}✗ Failed to retrieve documents${NC}"
fi

# Test 7: List all documents
echo -e "\n${YELLOW}TEST 7: List all documents${NC}"
RESPONSE=$(curl -s $API_URL/documents)
echo "Response: $RESPONSE"
if [[ $RESPONSE == *"documents"* ]]; then
    echo -e "${GREEN}✓ Listed all documents${NC}"
    
    # Check document count
    DOC_COUNT=$(echo $RESPONSE | grep -o '"total":[0-9]*' | cut -d':' -f2)
    echo "Document count: $DOC_COUNT"
else
    echo -e "${RED}✗ Failed to list documents${NC}"
fi

# Test 8: Get document summary
echo -e "\n${YELLOW}TEST 8: Get document summary${NC}"
RESPONSE=$(curl -s $API_URL/documents/$DOCUMENT_ID/summary)
echo "Response: $RESPONSE"
if [[ $RESPONSE == *"summary"* ]]; then
    echo -e "${GREEN}✓ Retrieved document summary${NC}"
else
    echo -e "${RED}✗ Failed to retrieve document summary${NC}"
fi

# Test 9: Delete the document
echo -e "\n${YELLOW}TEST 9: Delete document${NC}"
RESPONSE=$(curl -s -X DELETE $API_URL/documents/$DOCUMENT_ID)
echo "Response: $RESPONSE"
if [[ $RESPONSE == *"success"* || $RESPONSE == *"deleted"* ]]; then
    echo -e "${GREEN}✓ Document deleted successfully${NC}"
else
    echo -e "${RED}✗ Failed to delete document${NC}"
fi

# Verify document was deleted
echo -e "\n${YELLOW}TEST 10: Verify document deletion${NC}"
RESPONSE=$(curl -s $API_URL/documents/$DOCUMENT_ID)
echo "Response: $RESPONSE"
if [[ $RESPONSE == *"not found"* || $RESPONSE == *"404"* ]]; then
    echo -e "${GREEN}✓ Document deletion verified${NC}"
else
    echo -e "${RED}✗ Document still exists after deletion attempt${NC}"
fi

echo -e "\n${GREEN}All RAGIE document tests completed!${NC}" 