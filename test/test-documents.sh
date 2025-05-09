#!/bin/bash

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Base URL for the API
API_URL="http://localhost:8000/api"

# Create a temporary test file
TEST_FILE="/tmp/test-document-$$.txt"
echo "This is a test document for the RAGIE API." > "$TEST_FILE"
echo "It contains some sample text that will be used to test document operations." >> "$TEST_FILE"
echo "The document should be properly processed and indexed." >> "$TEST_FILE"

# Function to print section header
print_header() {
    echo -e "\n${BLUE}=== $1 ===${NC}\n"
}

# Function to handle errors
handle_error() {
    echo -e "${RED}ERROR: $1${NC}"
    exit 1
}

# Test creating a document from raw text
test_create_document_raw() {
    print_header "Testing Document Creation from Raw Text"
    
    # Create a document with raw text
    echo -e "${YELLOW}Creating document from raw text...${NC}"
    RESPONSE=$(curl -s -X POST "$API_URL/documents/raw" \
        -H "Content-Type: application/json" \
        -d '{
            "content": "This is a test document created from raw text.",
            "filename": "test-raw.txt",
            "content_type": "text/plain",
            "metadata": {"source": "test", "type": "raw"}
        }')
    
    # Check if document was created
    if echo "$RESPONSE" | grep -q "id"; then
        echo -e "${GREEN}SUCCESS: Document created from raw text${NC}"
        # Extract document ID
        DOC_ID=$(echo "$RESPONSE" | grep -o '"id":"[^"]*"' | head -1 | cut -d':' -f2 | tr -d '"')
        echo "Document ID: $DOC_ID"
        # Save for later tests
        echo "$DOC_ID" > /tmp/ragie-doc-id-raw.txt
    else
        echo -e "${RED}FAILED: Could not create document from raw text${NC}"
        echo "Response: $RESPONSE"
        return 1
    fi
    
    return 0
}

# Test creating a document from file upload
test_create_document_upload() {
    print_header "Testing Document Upload"
    
    # Upload a document
    echo -e "${YELLOW}Uploading document file...${NC}"
    RESPONSE=$(curl -s -X POST "$API_URL/documents" \
        -F "file=@$TEST_FILE" \
        -F 'metadata={"source": "test", "type": "upload"}')
    
    # Check if document was uploaded
    if echo "$RESPONSE" | grep -q "id"; then
        echo -e "${GREEN}SUCCESS: Document uploaded${NC}"
        # Extract document ID
        DOC_ID=$(echo "$RESPONSE" | grep -o '"id":"[^"]*"' | head -1 | cut -d':' -f2 | tr -d '"')
        echo "Document ID: $DOC_ID"
        # Save for later tests
        echo "$DOC_ID" > /tmp/ragie-doc-id-upload.txt
    else
        echo -e "${RED}FAILED: Could not upload document${NC}"
        echo "Response: $RESPONSE"
        return 1
    fi
    
    return 0
}

# Test creating a document from URL
test_create_document_url() {
    print_header "Testing Document Creation from URL"
    
    # Create a document from URL
    echo -e "${YELLOW}Creating document from URL...${NC}"
    RESPONSE=$(curl -s -X POST "$API_URL/documents/url" \
        -H "Content-Type: application/json" \
        -d '{
            "url": "https://raw.githubusercontent.com/fastapi-users/fastapi-users/master/README.md",
            "metadata": {"source": "test", "type": "url"}
        }')
    
    # Check if document was created
    if echo "$RESPONSE" | grep -q "id"; then
        echo -e "${GREEN}SUCCESS: Document created from URL${NC}"
        # Extract document ID
        DOC_ID=$(echo "$RESPONSE" | grep -o '"id":"[^"]*"' | head -1 | cut -d':' -f2 | tr -d '"')
        echo "Document ID: $DOC_ID"
        # Save for later tests
        echo "$DOC_ID" > /tmp/ragie-doc-id-url.txt
    else
        echo -e "${RED}FAILED: Could not create document from URL${NC}"
        echo "Response: $RESPONSE"
        return 1
    fi
    
    return 0
}

# Test listing documents
test_list_documents() {
    print_header "Testing Document Listing"
    
    # List documents
    echo -e "${YELLOW}Listing documents...${NC}"
    RESPONSE=$(curl -s -X GET "$API_URL/documents?limit=10")
    
    # Check if documents were listed
    if echo "$RESPONSE" | grep -q "documents"; then
        echo -e "${GREEN}SUCCESS: Documents listed${NC}"
        # Count documents
        TOTAL=$(echo "$RESPONSE" | grep -o '"total":[0-9]*' | cut -d':' -f2)
        echo "Total documents: $TOTAL"
    else
        echo -e "${RED}FAILED: Could not list documents${NC}"
        echo "Response: $RESPONSE"
        return 1
    fi
    
    return 0
}

# Test getting a document by ID
test_get_document() {
    print_header "Testing Get Document"
    
    # Get document ID from file
    DOC_ID=$(cat /tmp/ragie-doc-id-raw.txt)
    if [ -z "$DOC_ID" ]; then
        echo -e "${RED}FAILED: No document ID found from previous test${NC}"
        return 1
    fi
    
    # Get document
    echo -e "${YELLOW}Getting document with ID: $DOC_ID...${NC}"
    RESPONSE=$(curl -s -X GET "$API_URL/documents/$DOC_ID")
    
    # Check if document was retrieved
    if echo "$RESPONSE" | grep -q "id"; then
        echo -e "${GREEN}SUCCESS: Document retrieved${NC}"
        # Extract document filename
        FILENAME=$(echo "$RESPONSE" | grep -o '"filename":"[^"]*"' | head -1 | cut -d':' -f2 | tr -d '"')
        echo "Document filename: $FILENAME"
    else
        echo -e "${RED}FAILED: Could not get document${NC}"
        echo "Response: $RESPONSE"
        return 1
    fi
    
    return 0
}

# Test getting document content
test_get_document_content() {
    print_header "Testing Get Document Content"
    
    # Get document ID from file
    DOC_ID=$(cat /tmp/ragie-doc-id-raw.txt)
    if [ -z "$DOC_ID" ]; then
        echo -e "${RED}FAILED: No document ID found from previous test${NC}"
        return 1
    fi
    
    # Get document content
    echo -e "${YELLOW}Getting content for document with ID: $DOC_ID...${NC}"
    RESPONSE=$(curl -s -X GET "$API_URL/documents/$DOC_ID/content")
    
    # Check if content was retrieved
    if echo "$RESPONSE" | grep -q "content"; then
        echo -e "${GREEN}SUCCESS: Document content retrieved${NC}"
        # Extract the first part of content
        CONTENT_PREVIEW=$(echo "$RESPONSE" | grep -o '"content":"[^"]*"' | head -1 | cut -d':' -f2 | tr -d '"' | cut -c1-50)
        echo "Content preview: $CONTENT_PREVIEW..."
    else
        echo -e "${RED}FAILED: Could not get document content${NC}"
        echo "Response: $RESPONSE"
        return 1
    fi
    
    return 0
}

# Test updating document metadata
test_update_document_metadata() {
    print_header "Testing Update Document Metadata"
    
    # Get document ID from file
    DOC_ID=$(cat /tmp/ragie-doc-id-raw.txt)
    if [ -z "$DOC_ID" ]; then
        echo -e "${RED}FAILED: No document ID found from previous test${NC}"
        return 1
    fi
    
    # Update document metadata
    echo -e "${YELLOW}Updating metadata for document with ID: $DOC_ID...${NC}"
    RESPONSE=$(curl -s -X PATCH "$API_URL/documents/$DOC_ID/metadata" \
        -H "Content-Type: application/json" \
        -d '{
            "metadata": {
                "source": "test-updated",
                "type": "raw-updated",
                "tags": ["test", "updated"]
            }
        }')
    
    # Check if metadata was updated
    if echo "$RESPONSE" | grep -q "metadata"; then
        echo -e "${GREEN}SUCCESS: Document metadata updated${NC}"
    else
        echo -e "${RED}FAILED: Could not update document metadata${NC}"
        echo "Response: $RESPONSE"
        return 1
    fi
    
    return 0
}

# Test search functionality
test_search_documents() {
    print_header "Testing Document Search"
    
    # Wait a bit for indexing to complete
    echo -e "${YELLOW}Waiting for document indexing to complete...${NC}"
    sleep 5
    
    # Search documents
    echo -e "${YELLOW}Searching documents...${NC}"
    RESPONSE=$(curl -s -X POST "$API_URL/search" \
        -H "Content-Type: application/json" \
        -d '{
            "query": "test document",
            "top_k": 3
        }')
    
    # Check if search was successful
    if echo "$RESPONSE" | grep -q "results"; then
        echo -e "${GREEN}SUCCESS: Search completed${NC}"
        # Count results
        RESULTS_COUNT=$(echo "$RESPONSE" | grep -o '"document_id"' | wc -l)
        echo "Number of results: $RESULTS_COUNT"
    else
        echo -e "${RED}FAILED: Could not search documents${NC}"
        echo "Response: $RESPONSE"
        return 1
    fi
    
    return 0
}

# Test document deletion
test_delete_document() {
    print_header "Testing Document Deletion"
    
    # Get all document IDs
    DOC_IDS=()
    for FILE in /tmp/ragie-doc-id-*.txt; do
        if [ -f "$FILE" ]; then
            DOC_ID=$(cat "$FILE")
            if [ -n "$DOC_ID" ]; then
                DOC_IDS+=("$DOC_ID")
            fi
        fi
    done
    
    if [ ${#DOC_IDS[@]} -eq 0 ]; then
        echo -e "${RED}FAILED: No document IDs found from previous tests${NC}"
        return 1
    fi
    
    # Delete each document
    for DOC_ID in "${DOC_IDS[@]}"; do
        echo -e "${YELLOW}Deleting document with ID: $DOC_ID...${NC}"
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "$API_URL/documents/$DOC_ID")
        
        # Check if document was deleted
        if [ "$HTTP_CODE" -eq 204 ]; then
            echo -e "${GREEN}SUCCESS: Document deleted (ID: $DOC_ID)${NC}"
        else
            echo -e "${RED}FAILED: Could not delete document (ID: $DOC_ID)${NC}"
            echo "HTTP Status: $HTTP_CODE"
        fi
    done
    
    # Cleanup temp files
    rm -f /tmp/ragie-doc-id-*.txt
    
    return 0
}

# Run tests
main() {
    print_header "Starting RAGIE Document API Tests"
    
    # Check if server is running
    echo -e "${YELLOW}Checking if API server is running...${NC}"
    if ! curl -s "$API_URL" > /dev/null; then
        handle_error "API server is not running. Please start it with 'uvicorn main:app --reload'"
    fi
    
    # Run tests
    test_create_document_raw || handle_error "Failed to create document from raw text"
    test_create_document_upload || handle_error "Failed to upload document"
    test_create_document_url || handle_error "Failed to create document from URL"
    test_list_documents || handle_error "Failed to list documents"
    test_get_document || handle_error "Failed to get document"
    test_get_document_content || handle_error "Failed to get document content"
    test_update_document_metadata || handle_error "Failed to update document metadata"
    test_search_documents || handle_error "Failed to search documents"
    test_delete_document || handle_error "Failed to delete documents"
    
    # Cleanup
    rm -f "$TEST_FILE"
    
    print_header "All Tests Completed Successfully!"
}

# Run the main function
main 