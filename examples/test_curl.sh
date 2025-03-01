#!/bin/bash

# Check if URL argument is provided
if [ -z "$1" ]; then
    echo "Usage: ./test_curl.sh <deployed-url>"
    echo "Example: ./test_curl.sh https://your-app.repl.co"
    exit 1
fi

BASE_URL=$1

# Remove trailing slash if present
BASE_URL=${BASE_URL%/}

echo "Testing MCP Service at $BASE_URL"
echo "================================"

# Simple test with minimal code
curl -X POST "$BASE_URL/v1/sca/analyze" \
     -H "Content-Type: application/json" \
     -d '{
         "code": "import requests\nfrom flask import Flask",
         "session_id": "test_session",
         "file_path": "test.py"
     }' | python3 -m json.tool

echo -e "\nDone! Check the response above for analysis results."