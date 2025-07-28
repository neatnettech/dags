#!/bin/bash

# API Testing Script for DAG Execution Engine
# This script tests the API endpoints using curl

set -e  # Exit on any error

# Configuration
API_BASE="http://localhost:8000/api/v1"
CONTENT_TYPE="Content-Type: application/json"

echo "🚀 Testing DAG Execution API"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to make API calls and display results
api_call() {
    local method=$1
    local endpoint=$2
    local data=$3
    local description=$4
    
    echo -e "\n${BLUE}📋 Test: ${description}${NC}"
    echo -e "${YELLOW}${method} ${API_BASE}${endpoint}${NC}"
    
    if [ -n "$data" ]; then
        echo -e "${YELLOW}Request Body:${NC}"
        echo "$data" | jq '.' 2>/dev/null || echo "$data"
        echo ""
        
        response=$(curl -s -X "$method" \
            -H "$CONTENT_TYPE" \
            -d "$data" \
            -w "\nHTTP_STATUS:%{http_code}" \
            "${API_BASE}${endpoint}")
    else
        response=$(curl -s -X "$method" \
            -w "\nHTTP_STATUS:%{http_code}" \
            "${API_BASE}${endpoint}")
    fi
    
    # Extract status code and response body
    http_status=$(echo "$response" | tail -n1 | sed 's/HTTP_STATUS://')
    response_body=$(echo "$response" | sed '$d')
    
    echo -e "${YELLOW}Response (Status: $http_status):${NC}"
    echo "$response_body" | jq '.' 2>/dev/null || echo "$response_body"
    
    # Color code the status
    if [[ $http_status =~ ^2[0-9][0-9]$ ]]; then
        echo -e "${GREEN}✅ Success (${http_status})${NC}"
    else
        echo -e "${RED}❌ Error (${http_status})${NC}"
    fi
    
    echo "----------------------------------------"
}

# Check if server is running
echo -e "${BLUE}🔍 Checking if API server is running...${NC}"
if ! curl -s "$API_BASE/" > /dev/null; then
    echo -e "${RED}❌ API server is not running at $API_BASE${NC}"
    echo -e "${YELLOW}💡 Start the server with: poetry run dag-api${NC}"
    exit 1
fi
echo -e "${GREEN}✅ API server is running${NC}"

# Test 1: Root endpoint
api_call "GET" "/" "" "Get API information"

# Test 2: Health check
api_call "GET" "/health" "" "Health check"

# Test 3: Get supported types
api_call "GET" "/supported-types" "" "Get supported file types"

# Test 4: Simple manifest execution
simple_manifest='{
  "id": "test-manifest-001",
  "creationTimeStamp": "2024-01-01T00:00:00Z",
  "manifestTemplate": "standard",
  "processType": "test_process",
  "processName": "Simple Test Process",
  "processDate": "2024-01-01",
  "fileTypesToProcess": [
    {
      "stepID": "step1",
      "interfaceType": "File_Thomson",
      "sourceLocationOld": "/old/path/file1.thomson",
      "sourceLocationNew": "/new/path/file1.thomson",
      "prerequisites": []
    }
  ]
}'

api_call "POST" "/execute-manifest" "$simple_manifest" "Execute simple manifest"

# Test 5: Complex manifest with dependencies
complex_manifest='{
  "id": "test-manifest-002",
  "creationTimeStamp": "2024-01-01T00:00:00Z",
  "manifestTemplate": "standard",
  "processType": "complex_process",
  "processName": "Multi-Step Process with Dependencies",
  "processDate": "2024-01-01",
  "fileTypesToProcess": [
    {
      "stepID": "extract_thomson",
      "interfaceType": "File_Thomson",
      "sourceLocationOld": "/old/data/thomson_feed.thomson",
      "sourceLocationNew": "/new/data/thomson_feed.thomson",
      "prerequisites": []
    },
    {
      "stepID": "extract_reuters",
      "interfaceType": "File_Reuters",
      "sourceLocationOld": "/old/data/reuters_feed.reuters",
      "sourceLocationNew": "/new/data/reuters_feed.reuters",
      "prerequisites": []
    },
    {
      "stepID": "process_thomson",
      "interfaceType": "File_Thomson",
      "sourceLocationOld": "/processed/thomson_data.thomson",
      "sourceLocationNew": "/final/thomson_processed.thomson",
      "prerequisites": [
        {"stepId": "extract_thomson"}
      ]
    },
    {
      "stepID": "final_merge",
      "interfaceType": "File_Reuters",
      "sourceLocationOld": "/final/merged_data.reuters",
      "sourceLocationNew": "/output/final_result.reuters",
      "prerequisites": [
        {"stepId": "extract_reuters"},
        {"stepId": "process_thomson"}
      ]
    }
  ]
}'

api_call "POST" "/execute-manifest" "$complex_manifest" "Execute complex manifest with dependencies"

# Test 6: Invalid manifest (should fail)
invalid_manifest='{
  "id": "test-manifest-003",
  "creationTimeStamp": "2024-01-01T00:00:00Z",
  "manifestTemplate": "standard",
  "processType": "invalid_process",
  "processName": "Invalid Process",
  "processDate": "2024-01-01",
  "fileTypesToProcess": [
    {
      "stepID": "invalid_step",
      "interfaceType": "File_Unknown",
      "sourceLocationOld": "/old/invalid.unknown",
      "sourceLocationNew": "/new/invalid.unknown",
      "prerequisites": []
    }
  ]
}'

api_call "POST" "/execute-manifest" "$invalid_manifest" "Execute manifest with unsupported file type (should fail)"

# Test 7: Manifest with cyclic dependencies (should fail)
cyclic_manifest='{
  "id": "test-manifest-004",
  "creationTimeStamp": "2024-01-01T00:00:00Z",
  "manifestTemplate": "standard",
  "processType": "cyclic_process",
  "processName": "Process with Cyclic Dependencies",
  "processDate": "2024-01-01",
  "fileTypesToProcess": [
    {
      "stepID": "step_a",
      "interfaceType": "File_Thomson",
      "sourceLocationOld": "/old/a.thomson",
      "sourceLocationNew": "/new/a.thomson",
      "prerequisites": [
        {"stepId": "step_b"}
      ]
    },
    {
      "stepID": "step_b",
      "interfaceType": "File_Reuters",
      "sourceLocationOld": "/old/b.reuters",
      "sourceLocationNew": "/new/b.reuters",
      "prerequisites": [
        {"stepId": "step_a"}
      ]
    }
  ]
}'

api_call "POST" "/execute-manifest" "$cyclic_manifest" "Execute manifest with cyclic dependencies (should fail)"

# Test 8: Empty manifest (should fail)
empty_manifest='{
  "id": "test-manifest-005",
  "creationTimeStamp": "2024-01-01T00:00:00Z",
  "manifestTemplate": "standard",
  "processType": "empty_process",
  "processName": "Empty Process",
  "processDate": "2024-01-01",
  "fileTypesToProcess": []
}'

api_call "POST" "/execute-manifest" "$empty_manifest" "Execute empty manifest (should fail)"

# Test 9: Malformed JSON (should fail)
echo -e "\n${BLUE}📋 Test: Execute malformed JSON (should fail)${NC}"
echo -e "${YELLOW}POST ${API_BASE}/execute-manifest${NC}"
echo -e "${YELLOW}Request Body: Invalid JSON${NC}"

response=$(curl -s -X POST \
    -H "$CONTENT_TYPE" \
    -d '{"invalid": json}' \
    -w "\nHTTP_STATUS:%{http_code}" \
    "${API_BASE}/execute-manifest")

http_status=$(echo "$response" | tail -n1 | sed 's/HTTP_STATUS://')
response_body=$(echo "$response" | sed '$d')

echo -e "${YELLOW}Response (Status: $http_status):${NC}"
echo "$response_body" | jq '.' 2>/dev/null || echo "$response_body"

if [[ $http_status =~ ^4[0-9][0-9]$ ]]; then
    echo -e "${GREEN}✅ Correctly rejected malformed JSON (${http_status})${NC}"
else
    echo -e "${RED}❌ Unexpected response (${http_status})${NC}"
fi

echo "----------------------------------------"

echo -e "\n${GREEN}🎉 API Testing Complete!${NC}"
echo -e "\n${BLUE}📖 Summary:${NC}"
echo "• All major API endpoints tested"
echo "• Both success and failure scenarios covered"
echo "• Manifest execution with various complexities"
echo "• Error handling validation"
echo ""
echo -e "${YELLOW}💡 To start the API server: poetry run dag-api${NC}"
echo -e "${YELLOW}💡 To view API docs: http://localhost:8000/docs${NC}"