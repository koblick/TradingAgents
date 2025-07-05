#!/bin/bash
# to run ./load_env.sh
# TradingAgents Environment Loader
# This script loads API keys from .env file

echo "🚀 Loading TradingAgents Environment..."
echo "======================================"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please create a .env file with your API keys:"
    echo "   FINNHUB_API_KEY=your_finnhub_key_here"
    echo "   OPENAI_API_KEY=your_openai_key_here"
    exit 1
fi

# Load environment variables from .env file
set -a  # automatically export all variables
source .env
set +a  # stop automatically exporting

# Verify that the keys were loaded
if [ -z "$FINNHUB_API_KEY" ] || [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Failed to load API keys from .env file!"
    echo "Please check that your .env file contains:"
    echo "   FINNHUB_API_KEY=your_finnhub_key_here"
    echo "   OPENAI_API_KEY=your_openai_key_here"
    exit 1
fi

echo "✅ API keys loaded successfully!"
echo "   FINNHUB_API_KEY: ${FINNHUB_API_KEY:0:8}..."
echo "   OPENAI_API_KEY: ${OPENAI_API_KEY:0:8}..."
echo ""
echo "🎉 You can now run TradingAgents!"
echo ""
echo "🚀 Launching TradingAgents CLI..."
echo "=================================="
echo ""

uv run python -m cli.main 