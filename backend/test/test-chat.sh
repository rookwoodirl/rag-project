#!/bin/bash

# Load environment variables from .env file
source "$(dirname "$(dirname "$0")")/.env"

# Set the API base URL
API_URL="http://localhost:8000/api"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Testing Chat Functionality${NC}"
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

# Test 2: Basic chat query
echo -e "\n${YELLOW}TEST 2: Basic chat query${NC}"
RESPONSE=$(curl -s -X POST $API_URL/chat \
    -H "Content-Type: application/json" \
    -d '{"query": "What is RAG in AI context?", "history": []}')
echo "Response: $RESPONSE"

if [[ $RESPONSE == *"response"* ]]; then
    echo -e "${GREEN}✓ Chat endpoint working${NC}"
else
    echo -e "${RED}✗ Failed to get chat response${NC}"
fi

# Test 3: Create a ticket for testing ticket chat
echo -e "\n${YELLOW}TEST 3: Create a ticket for testing ticket chat${NC}"
TICKET_NUMBER="CHAT-TEST-$(date +%s)"
RESPONSE=$(curl -s -X POST $API_URL/tickets \
    -H "Content-Type: application/json" \
    -d "{\"ticket_category\": \"support\", \"ticket_number\": \"$TICKET_NUMBER\", \"description\": \"User is experiencing slow performance when uploading large documents to the RAG system. They need to upload a 50MB PDF but the application freezes during upload.\", \"completion_criteria\": \"Issue resolved, user can upload large documents successfully\"}") 
echo "Response: $RESPONSE"

if [[ $RESPONSE == *"$TICKET_NUMBER"* ]]; then
    echo -e "${GREEN}✓ Created test ticket: $TICKET_NUMBER${NC}"
else
    echo -e "${RED}✗ Failed to create test ticket${NC}"
    exit 1
fi

# Test 4: Ticket-contextualized chat
echo -e "\n${YELLOW}TEST 4: Ticket-contextualized chat${NC}"
RESPONSE=$(curl -s -X POST $API_URL/chat/ticket \
    -H "Content-Type: application/json" \
    -d "{\"query\": \"What might be causing the issue described in this ticket?\", \"ticket_number\": \"$TICKET_NUMBER\", \"history\": []}")
echo "Response: $RESPONSE"

if [[ $RESPONSE == *"response"* ]]; then
    echo -e "${GREEN}✓ Ticket chat endpoint working${NC}"
else
    echo -e "${RED}✗ Failed to get ticket chat response${NC}"
fi

# Test 5: Chat with conversation history
echo -e "\n${YELLOW}TEST 5: Chat with conversation history${NC}"
RESPONSE=$(curl -s -X POST $API_URL/chat \
    -H "Content-Type: application/json" \
    -d "{\"query\": \"What's the next step I should take?\", \"history\": [{\"role\": \"user\", \"content\": \"I'm having trouble with my application performance\"}, {\"role\": \"assistant\", \"content\": \"What kind of performance issues are you experiencing?\"}]}")
echo "Response: $RESPONSE"

if [[ $RESPONSE == *"response"* ]]; then
    echo -e "${GREEN}✓ Chat with history working${NC}"
else
    echo -e "${RED}✗ Failed to get chat response with history${NC}"
fi

# Clean up: Delete the test ticket
echo -e "\n${YELLOW}Cleaning up: Deleting test ticket${NC}"
RESPONSE=$(curl -s -X DELETE "$API_URL/tickets/$TICKET_NUMBER?hard_delete=true")
echo -e "${GREEN}✓ Test ticket deleted${NC}"

echo -e "\n${GREEN}All chat tests completed!${NC}" 