#!/bin/sh

# Source .env file if it exists
if [ -f ./.env ]; then
. ./.env
fi

# Check if API_TOKEN environment variable is set
if [ -z "$API_TOKEN" ]; then
echo "Error: API_TOKEN environment variable is not set"
exit 1
fi

# Make HTTP request with Authorization header
curl -X POST \
-H "Authorization: Bearer $API_TOKEN" \
http://localhost:5000/
