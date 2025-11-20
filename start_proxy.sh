#!/bin/bash
# Start LiteLLM proxy server with Cerebras → Z.AI fallback

set -e

echo "Starting LiteLLM proxy server..."
echo "Cerebras (primary) → Z.AI GLM-4.6 (fallback)"
echo ""

# Activate virtual environment
source .venv/bin/activate

# Export environment variables from .env file
export $(grep -v '^#' .env | xargs)

# Set log level to suppress verbose errors
export LITELLM_LOG=CRITICAL

# Start the proxy server
litellm --config config.yaml --port 4000
