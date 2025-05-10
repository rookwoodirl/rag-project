#!/bin/bash
API_URL="http://localhost:8080/api"
echo "Starting tests..."
echo "Testing API endpoint: $API_URL"
RESPONSE=$(curl -s "$API_URL/documents/raw" -H "Content-Type: application/json" -d '{"content": "Test content", "filename": "test.txt"}')
echo "Response: $RESPONSE"
