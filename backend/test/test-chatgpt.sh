#!/bin/bash

# Set the API base URL
API_URL="http://localhost:8000"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Testing GPT Chat Functionality${NC}"
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

# Test 2: Initialize the database (if needed)
echo -e "\n${YELLOW}TEST 2: Initialize the database${NC}"
RESPONSE=$(curl -s -X POST $API_URL/initialize-db)
echo "Response: $RESPONSE"
if [[ $RESPONSE == *"Database initialized successfully"* ]]; then
    echo -e "${GREEN}✓ Database initialized${NC}"
else
    echo -e "${RED}✗ Database initialization failed${NC}"
    # Continue anyway as the database might already be initialized
fi

# Test 3: Ask GPT to create a ticket for a login issue
echo -e "\n${YELLOW}TEST 3: Ask GPT to create a ticket for a login issue${NC}"
RESPONSE=$(curl -s -X POST $API_URL/chat \
    -H "Content-Type: application/json" \
    -d '{"query": "Create a ticket for login issue where users cannot access their accounts after password reset", "history": []}')
echo "Response: $RESPONSE"
if [[ $RESPONSE == *"ticket"* && $RESPONSE == *"login"* && $RESPONSE == *"password reset"* ]]; then
    echo -e "${GREEN}✓ GPT acknowledged the ticket creation request${NC}"
else
    echo -e "${RED}✗ GPT did not properly acknowledge the ticket creation${NC}"
fi

# Sleep to allow time for any async processing
sleep 2

# Test 4: Check if a ticket with login issue keywords exists
echo -e "\n${YELLOW}TEST 4: Verify ticket creation for login issue${NC}"
RESPONSE=$(curl -s $API_URL/tickets)
echo "Response: $RESPONSE"
if [[ $RESPONSE == *"login"* && $RESPONSE == *"password reset"* ]]; then
    echo -e "${GREEN}✓ Ticket with login issue was created${NC}"
    
    # Try to extract the ticket number for later reference
    TICKET_NUMBER=$(echo $RESPONSE | grep -o '"ticket_number":"[^"]*"' | head -1 | cut -d'"' -f4)
    echo "Detected ticket number: $TICKET_NUMBER"
else
    echo -e "${RED}✗ Could not find ticket with login issue${NC}"
    TICKET_NUMBER=""
fi

# Test 5: Ask GPT to create a ticket for a performance issue
echo -e "\n${YELLOW}TEST 5: Ask GPT to create a ticket for a performance issue${NC}"
RESPONSE=$(curl -s -X POST $API_URL/chat \
    -H "Content-Type: application/json" \
    -d '{"query": "Please create a new bug ticket for slow loading times on the dashboard page. Loading takes more than 10 seconds.", "history": []}')
echo "Response: $RESPONSE"
if [[ $RESPONSE == *"ticket"* && $RESPONSE == *"dashboard"* && $RESPONSE == *"loading"* ]]; then
    echo -e "${GREEN}✓ GPT acknowledged the performance issue ticket request${NC}"
else
    echo -e "${RED}✗ GPT did not properly acknowledge the performance ticket creation${NC}"
fi

# Sleep to allow time for any async processing
sleep 2

# Test 6: Check if a ticket with performance issue keywords exists
echo -e "\n${YELLOW}TEST 6: Verify ticket creation for performance issue${NC}"
RESPONSE=$(curl -s $API_URL/tickets)
echo "Response: $RESPONSE"
if [[ $RESPONSE == *"dashboard"* && $RESPONSE == *"loading"* && $RESPONSE == *"10 seconds"* ]]; then
    echo -e "${GREEN}✓ Ticket with performance issue was created${NC}"
    
    # Try to extract the second ticket number
    PERF_TICKET_NUMBER=$(echo $RESPONSE | grep -o '"ticket_number":"[^"]*"' | grep -v "$TICKET_NUMBER" | head -1 | cut -d'"' -f4)
    echo "Detected performance ticket number: $PERF_TICKET_NUMBER"
else
    echo -e "${RED}✗ Could not find ticket with performance issue${NC}"
    PERF_TICKET_NUMBER=""
fi

# Test 7: Ask GPT to update the login issue ticket
if [[ ! -z "$TICKET_NUMBER" ]]; then
    echo -e "\n${YELLOW}TEST 7: Ask GPT to update the login issue ticket${NC}"
    RESPONSE=$(curl -s -X POST $API_URL/chat \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"Update ticket $TICKET_NUMBER to add that this only affects users on mobile devices\", \"history\": []}")
    echo "Response: $RESPONSE"
    if [[ $RESPONSE == *"update"* && $RESPONSE == *"$TICKET_NUMBER"* && $RESPONSE == *"mobile"* ]]; then
        echo -e "${GREEN}✓ GPT acknowledged the ticket update request${NC}"
    else
        echo -e "${RED}✗ GPT did not properly acknowledge the ticket update${NC}"
    fi

    # Sleep to allow time for any async processing
    sleep 2

    # Test 8: Check if the ticket was updated with mobile information
    echo -e "\n${YELLOW}TEST 8: Verify ticket update with mobile information${NC}"
    RESPONSE=$(curl -s $API_URL/tickets/$TICKET_NUMBER)
    echo "Response: $RESPONSE"
    if [[ $RESPONSE == *"mobile"* ]]; then
        echo -e "${GREEN}✓ Ticket was updated with mobile information${NC}"
    else
        echo -e "${RED}✗ Could not verify ticket update with mobile information${NC}"
    fi
else
    echo -e "\n${YELLOW}TEST 7 & 8: Skipping ticket update tests - no ticket number available${NC}"
fi

# Test 9: Ask GPT to query information about tickets
echo -e "\n${YELLOW}TEST 9: Ask GPT to summarize all open tickets${NC}"
RESPONSE=$(curl -s -X POST $API_URL/chat \
    -H "Content-Type: application/json" \
    -d '{"query": "List all open tickets and give me a summary", "history": []}')
echo "Response: $RESPONSE"
if [[ $RESPONSE == *"ticket"* ]]; then
    echo -e "${GREEN}✓ GPT provided information about tickets${NC}"
else
    echo -e "${RED}✗ GPT did not properly provide ticket information${NC}"
fi

# Test 10: Ask GPT to create a comment on a ticket
if [[ ! -z "$PERF_TICKET_NUMBER" ]]; then
    echo -e "\n${YELLOW}TEST 10: Ask GPT to add a comment to the performance ticket${NC}"
    RESPONSE=$(curl -s -X POST $API_URL/chat \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"Add a comment to ticket $PERF_TICKET_NUMBER that we need to optimize database queries\", \"history\": []}")
    echo "Response: $RESPONSE"
    if [[ $RESPONSE == *"comment"* && $RESPONSE == *"$PERF_TICKET_NUMBER"* ]]; then
        echo -e "${GREEN}✓ GPT acknowledged the comment addition request${NC}"
    else
        echo -e "${RED}✗ GPT did not properly acknowledge the comment addition${NC}"
    fi

    # Sleep to allow time for any async processing
    sleep 2

    # Test 11: Check if a comment was added to the ticket
    echo -e "\n${YELLOW}TEST 11: Verify comment addition to performance ticket${NC}"
    RESPONSE=$(curl -s $API_URL/tickets/$PERF_TICKET_NUMBER/comments)
    echo "Response: $RESPONSE"
    if [[ $RESPONSE == *"database queries"* ]]; then
        echo -e "${GREEN}✓ Comment was added to the performance ticket${NC}"
    else
        echo -e "${RED}✗ Could not verify comment addition to performance ticket${NC}"
    fi
else
    echo -e "\n${YELLOW}TEST 10 & 11: Skipping comment tests - no performance ticket number available${NC}"
fi

echo -e "\n${GREEN}All GPT chat function tests completed!${NC}" 