#!/bin/bash

# Set the API base URL
API_URL="http://localhost:8000"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Testing Todo List Functionality${NC}"
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

# Test 3: Create a todo-list ticket
echo -e "\n${YELLOW}TEST 3: Create a todo-list ticket${NC}"
RESPONSE=$(curl -s -X POST $API_URL/tickets \
    -H "Content-Type: application/json" \
    -d '{"ticket_category": "todo", "description": "Implement todo list functionality"}')
echo "Response: $RESPONSE"
if [[ $RESPONSE == *"todo"* && $RESPONSE == *"Implement todo list functionality"* ]]; then
    echo -e "${GREEN}✓ Todo list ticket created successfully${NC}"
    # Extract the ticket number for later use
    TICKET_NUMBER=$(echo $RESPONSE | grep -o '"ticket_number":"[^"]*"' | head -1 | cut -d'"' -f4)
    echo "Ticket number: $TICKET_NUMBER"
else
    echo -e "${RED}✗ Failed to create todo list ticket${NC}"
    exit 1
fi

# Test 4: Add a todo item to the ticket
echo -e "\n${YELLOW}TEST 4: Add a todo item to the ticket${NC}"
RESPONSE=$(curl -s -X POST $API_URL/tickets/$TICKET_NUMBER/todos \
    -H "Content-Type: application/json" \
    -d '{"description": "Create database schema for todo items"}')
echo "Response: $RESPONSE"
if [[ $RESPONSE == *"Create database schema for todo items"* ]]; then
    echo -e "${GREEN}✓ Todo item added successfully${NC}"
    # Extract the todo item ID for later use
    TODO_ITEM_ID=$(echo $RESPONSE | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
    echo "Todo item ID: $TODO_ITEM_ID"
else
    echo -e "${RED}✗ Failed to add todo item${NC}"
    TODO_ITEM_ID=1  # Fallback ID
fi

# Test 5: Add a second todo item to the ticket
echo -e "\n${YELLOW}TEST 5: Add another todo item to the ticket${NC}"
RESPONSE=$(curl -s -X POST $API_URL/tickets/$TICKET_NUMBER/todos \
    -H "Content-Type: application/json" \
    -d '{"description": "Implement API endpoints for todo items"}')
echo "Response: $RESPONSE"
if [[ $RESPONSE == *"Implement API endpoints for todo items"* ]]; then
    echo -e "${GREEN}✓ Second todo item added successfully${NC}"
    # Extract the second todo item ID
    TODO_ITEM_ID2=$(echo $RESPONSE | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
    echo "Second todo item ID: $TODO_ITEM_ID2"
else
    echo -e "${RED}✗ Failed to add second todo item${NC}"
    TODO_ITEM_ID2=2  # Fallback ID
fi

# Test 6: Get all todo items for the ticket
echo -e "\n${YELLOW}TEST 6: Get all todo items for the ticket${NC}"
RESPONSE=$(curl -s $API_URL/tickets/$TICKET_NUMBER/todos)
echo "Response: $RESPONSE"
if [[ $RESPONSE == *"Create database schema for todo items"* && $RESPONSE == *"Implement API endpoints for todo items"* ]]; then
    echo -e "${GREEN}✓ Retrieved todo items successfully${NC}"
    # Count the number of todo items
    TODO_COUNT=$(echo $RESPONSE | grep -o '"id":' | wc -l)
    echo "Todo item count: $TODO_COUNT"
else
    echo -e "${RED}✗ Failed to retrieve todo items${NC}"
fi

# Test 7: Get ticket with todo items
echo -e "\n${YELLOW}TEST 7: Get ticket with todo items${NC}"
RESPONSE=$(curl -s $API_URL/tickets/$TICKET_NUMBER)
echo "Response: $RESPONSE"
if [[ $RESPONSE == *"todo_items"* && $RESPONSE == *"Create database schema for todo items"* ]]; then
    echo -e "${GREEN}✓ Retrieved ticket with todo items successfully${NC}"
else
    echo -e "${RED}✗ Failed to retrieve ticket with todo items${NC}"
fi

# Test 8: Mark first todo item as done
echo -e "\n${YELLOW}TEST 8: Mark first todo item as done${NC}"
RESPONSE=$(curl -s -X PUT $API_URL/todos/$TODO_ITEM_ID \
    -H "Content-Type: application/json" \
    -d '{"done": true}')
echo "Response: $RESPONSE"
if [[ $RESPONSE == *"done\":true"* ]]; then
    echo -e "${GREEN}✓ Todo item marked as done${NC}"
else
    echo -e "${RED}✗ Failed to mark todo item as done${NC}"
fi

# Test 9: Update a todo item description
echo -e "\n${YELLOW}TEST 9: Update a todo item description${NC}"
RESPONSE=$(curl -s -X PUT $API_URL/todos/$TODO_ITEM_ID2 \
    -H "Content-Type: application/json" \
    -d '{"description": "Implement REST API endpoints for todo items"}')
echo "Response: $RESPONSE"
if [[ $RESPONSE == *"Implement REST API endpoints for todo items"* ]]; then
    echo -e "${GREEN}✓ Todo item description updated${NC}"
else
    echo -e "${RED}✗ Failed to update todo item description${NC}"
fi

# Test 10: Add a third todo item with specific position
echo -e "\n${YELLOW}TEST 10: Add a third todo item with specific position${NC}"
RESPONSE=$(curl -s -X POST $API_URL/tickets/$TICKET_NUMBER/todos \
    -H "Content-Type: application/json" \
    -d '{"description": "Write documentation for todo list feature", "position": 0}')
echo "Response: $RESPONSE"
if [[ $RESPONSE == *"Write documentation for todo list feature"* && $RESPONSE == *"position\":0"* ]]; then
    echo -e "${GREEN}✓ Positioned todo item added successfully${NC}"
    # Extract the third todo item ID
    TODO_ITEM_ID3=$(echo $RESPONSE | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
    echo "Third todo item ID: $TODO_ITEM_ID3"
else
    echo -e "${RED}✗ Failed to add positioned todo item${NC}"
    TODO_ITEM_ID3=3  # Fallback ID
fi

# Test 11: Get all todo items to verify order
echo -e "\n${YELLOW}TEST 11: Get all todo items to verify order${NC}"
RESPONSE=$(curl -s $API_URL/tickets/$TICKET_NUMBER/todos)
echo "Response: $RESPONSE"
if [[ $RESPONSE == *"position\":0"* ]]; then
    echo -e "${GREEN}✓ Todo items retrieved with correct position${NC}"
else
    echo -e "${RED}✗ Failed to verify todo item positions${NC}"
fi

# Test 12: Delete a todo item
echo -e "\n${YELLOW}TEST 12: Delete a todo item${NC}"
RESPONSE=$(curl -s -X DELETE -w "%{http_code}" $API_URL/todos/$TODO_ITEM_ID3)
echo "Response code: $RESPONSE"
if [[ $RESPONSE == "204" ]]; then
    echo -e "${GREEN}✓ Todo item deleted successfully${NC}"
else
    echo -e "${RED}✗ Failed to delete todo item${NC}"
fi

# Test 13: Verify todo item was deleted
echo -e "\n${YELLOW}TEST 13: Verify todo item deletion${NC}"
RESPONSE=$(curl -s $API_URL/tickets/$TICKET_NUMBER/todos)
echo "Response: $RESPONSE"
NEW_TODO_COUNT=$(echo $RESPONSE | grep -o '"id":' | wc -l)
if [[ $NEW_TODO_COUNT -eq $((TODO_COUNT - 1)) ]]; then
    echo -e "${GREEN}✓ Todo item deletion verified (count: $NEW_TODO_COUNT)${NC}"
else
    echo -e "${RED}✗ Todo item count doesn't match expected value after deletion${NC}"
    echo "Expected: $((TODO_COUNT - 1)), Actual: $NEW_TODO_COUNT"
fi

# Test 14: Clean up - Delete the ticket (hard delete)
echo -e "\n${YELLOW}TEST 14: Clean up - Delete the ticket${NC}"
RESPONSE=$(curl -s -X DELETE -w "%{http_code}" $API_URL/tickets/$TICKET_NUMBER?hard_delete=true)
echo "Response code: $RESPONSE"
if [[ $RESPONSE == "204" ]]; then
    echo -e "${GREEN}✓ Ticket deleted successfully${NC}"
else
    echo -e "${RED}✗ Failed to delete ticket${NC}"
fi

echo -e "\n${GREEN}All todo list tests completed!${NC}" 