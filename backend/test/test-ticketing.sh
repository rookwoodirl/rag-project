#!/bin/bash

# Set the API base URL
API_URL="http://localhost:8000"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Running Ticket API Tests${NC}"
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

# Test 2: Initialize the database
echo -e "\n${YELLOW}TEST 2: Initialize the database${NC}"
RESPONSE=$(curl -s -X POST $API_URL/initialize-db)
echo "Response: $RESPONSE"
if [[ $RESPONSE == *"Database initialized successfully"* ]]; then
    echo -e "${GREEN}✓ Database initialized${NC}"
else
    echo -e "${RED}✗ Database initialization failed${NC}"
fi

# Test 3: Create a ticket
echo -e "\n${YELLOW}TEST 3: Create a ticket${NC}"
RESPONSE=$(curl -s -X POST $API_URL/tickets \
    -H "Content-Type: application/json" \
    -d '{"ticket_category": "bug", "ticket_number": "BUG-123", "description": "Test ticket description"}')
echo "Response: $RESPONSE"
if [[ $RESPONSE == *"BUG-123"* ]]; then
    echo -e "${GREEN}✓ Ticket created successfully${NC}"
else
    echo -e "${RED}✗ Failed to create ticket${NC}"
fi

# Test 4: Get tickets list
echo -e "\n${YELLOW}TEST 4: Get tickets list${NC}"
RESPONSE=$(curl -s $API_URL/tickets)
echo "Response: $RESPONSE"
if [[ $RESPONSE == *"tickets"* ]]; then
    echo -e "${GREEN}✓ Retrieved tickets list${NC}"
else
    echo -e "${RED}✗ Failed to retrieve tickets list${NC}"
fi

# Test 5: Get specific ticket
echo -e "\n${YELLOW}TEST 5: Get specific ticket${NC}"
RESPONSE=$(curl -s $API_URL/tickets/BUG-123)
echo "Response: $RESPONSE"
if [[ $RESPONSE == *"BUG-123"* ]]; then
    echo -e "${GREEN}✓ Retrieved specific ticket${NC}"
else
    echo -e "${RED}✗ Failed to retrieve specific ticket${NC}"
fi

# Test 6: Update ticket
echo -e "\n${YELLOW}TEST 6: Update ticket${NC}"
RESPONSE=$(curl -s -X PUT $API_URL/tickets/BUG-123 \
    -H "Content-Type: application/json" \
    -d '{"ticket_category": "bug", "description": "Updated test ticket description"}')
echo "Response: $RESPONSE"
if [[ $RESPONSE == *"Updated test ticket description"* ]]; then
    echo -e "${GREEN}✓ Ticket updated successfully${NC}"
else
    echo -e "${RED}✗ Failed to update ticket${NC}"
fi

# Test 7: Create a comment on ticket
echo -e "\n${YELLOW}TEST 7: Create comment on ticket${NC}"
RESPONSE=$(curl -s -X POST $API_URL/tickets/BUG-123/comments \
    -H "Content-Type: application/json" \
    -d '{"ticket_category": "bug", "author": "test_user", "content": "Test comment", "links": ["https://example.com"], "attached_documents": []}')
echo "Response: $RESPONSE"
if [[ $RESPONSE == *"Test comment"* ]]; then
    echo -e "${GREEN}✓ Comment created successfully${NC}"
    # Extract the comment ID for later tests
    COMMENT_ID=$(echo $RESPONSE | grep -o '"id":[0-9]*' | cut -d':' -f2)
else
    echo -e "${RED}✗ Failed to create comment${NC}"
    COMMENT_ID="1" # Fallback ID for continuing tests
fi

# Test 8: Get comments for a ticket
echo -e "\n${YELLOW}TEST 8: Get comments for ticket${NC}"
RESPONSE=$(curl -s $API_URL/tickets/BUG-123/comments)
echo "Response: $RESPONSE"
if [[ $RESPONSE == *"comments"* ]]; then
    echo -e "${GREEN}✓ Retrieved comments successfully${NC}"
else
    echo -e "${RED}✗ Failed to retrieve comments${NC}"
fi

# Test 9: Update a comment
echo -e "\n${YELLOW}TEST 9: Update comment${NC}"
RESPONSE=$(curl -s -X PUT $API_URL/tickets/comments/$COMMENT_ID \
    -H "Content-Type: application/json" \
    -d '{"content": "Updated test comment", "links": ["https://example.com"], "attached_documents": []}')
echo "Response: $RESPONSE"
if [[ $RESPONSE == *"Updated test comment"* ]]; then
    echo -e "${GREEN}✓ Comment updated successfully${NC}"
else
    echo -e "${RED}✗ Failed to update comment${NC}"
fi

# Test 10: Delete a comment
echo -e "\n${YELLOW}TEST 10: Delete comment${NC}"
RESPONSE=$(curl -s -X DELETE -w "%{http_code}" $API_URL/tickets/comments/$COMMENT_ID)
echo "Response code: $RESPONSE"
if [[ $RESPONSE == "204" ]]; then
    echo -e "${GREEN}✓ Comment deleted successfully${NC}"
else
    echo -e "${RED}✗ Failed to delete comment${NC}"
fi

# Test 11: Soft delete ticket
echo -e "\n${YELLOW}TEST 11: Soft delete ticket${NC}"
RESPONSE=$(curl -s -X DELETE -w "%{http_code}" $API_URL/tickets/BUG-123)
echo "Response code: $RESPONSE"
if [[ $RESPONSE == "204" ]]; then
    echo -e "${GREEN}✓ Ticket soft deleted successfully${NC}"
else
    echo -e "${RED}✗ Failed to soft delete ticket${NC}"
fi

# Test 12: Hard delete ticket
echo -e "\n${YELLOW}TEST 12: Hard delete ticket${NC}"
RESPONSE=$(curl -s -X DELETE -w "%{http_code}" $API_URL/tickets/BUG-123?hard_delete=true)
echo "Response code: $RESPONSE"
if [[ $RESPONSE == "204" ]]; then
    echo -e "${GREEN}✓ Ticket hard deleted successfully${NC}"
else
    echo -e "${RED}✗ Failed to hard delete ticket${NC}"
fi

echo -e "\n${GREEN}All tests completed!${NC}" 