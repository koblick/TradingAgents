#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Add uv to PATH
export PATH="/usr/local/bin:/opt/homebrew/bin:$HOME/.local/bin:$PATH"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

echo "🚀 Loading TradingAgents Environment..."
echo "======================================"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please create a .env file with your API keys:"
    echo "   FINNHUB_API_KEY=your_finnhub_key_here"
    echo "   OPENAI_API_KEY=your_openai_key_here"
    echo "   GOOGLE_API_KEY=your_google_key_here (for Gemini)"
    echo "   DEEPSEEK_API_KEY=your_deepseek_key_here"
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
    echo "   GOOGLE_API_KEY=your_google_key_here (for Gemini)"
    echo "   DEEPSEEK_API_KEY=your_deepseek_key_here"
    exit 1
fi

echo "✅ API keys loaded successfully!"
echo "   FINNHUB_API_KEY: ${FINNHUB_API_KEY:0:8}..."
echo "   OPENAI_API_KEY: ${OPENAI_API_KEY:0:8}..."
echo "   GOOGLE_API_KEY: ${GOOGLE_API_KEY:0:8}..."
echo "   DEEPSEEK_API_KEY: ${DEEPSEEK_API_KEY:0:8}..."
echo ""
echo "🎉 You can now run TradingAgents!"
echo ""
echo "🚀 Launching TradingAgents CLI..."
echo "=================================="
echo ""

# Define ticker symbols array
TICKERS=("BA" "AAPL" "GOOGL" "AMZN" "CVX")

# Define base output directory
BASE_OUTPUT_DIR="/Users/koblick/Library/Mobile Documents/com~apple~CloudDocs/Coorbital/StockAnalysis/"

# Get current date in YYYY-MM-DD format
CURRENT_DATE=$(date +"%Y-%m-%d")

# Create date-specific output directory
OUTPUT_DIR="$BASE_OUTPUT_DIR$CURRENT_DATE/"

# Create the directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Define providers array
PROVIDERS=("deepseek" "openai")

echo "📊 Analyzing the following stocks: ${TICKERS[*]}"
echo "📁 Base output directory: $BASE_OUTPUT_DIR"
echo "📅 Date-specific directory: $OUTPUT_DIR"
echo "🤖 Providers: ${PROVIDERS[*]}"
echo ""

# Loop through each provider
for provider in "${PROVIDERS[@]}"; do
    echo "🔄 Starting analysis with $provider provider..."
    echo "================================================"
    
    # Try different methods to run the analysis
    if command -v uv &> /dev/null; then
        echo "Using uv command..."
        uv run python main.py --tickers "${TICKERS[@]}" -p "$provider" --output-dir "$OUTPUT_DIR"
    elif [ -f ".venv/bin/python" ]; then
        echo "Using virtual environment Python..."
        .venv/bin/python main.py --tickers "${TICKERS[@]}" -p "$provider" --output-dir "$OUTPUT_DIR"
    else
        echo "Using system Python..."
        python main.py --tickers "${TICKERS[@]}" -p "$provider" --output-dir "$OUTPUT_DIR"
    fi
    
    echo ""
    echo "✅ Completed analysis with $provider provider"
    echo "=============================================="
    echo ""
done

# Copy detailed JSON logs to output directory
echo "📋 Copying detailed JSON logs to output directory..."
for ticker in "${TICKERS[@]}"; do
    # Check if the eval_results directory exists for this ticker
    if [ -d "eval_results/$ticker/TradingAgentsStrategy_logs/" ]; then
        # Copy all JSON files for this ticker to the output directory
        cp eval_results/$ticker/TradingAgentsStrategy_logs/*.json "$OUTPUT_DIR" 2>/dev/null || true
        echo "   ✅ Copied JSON logs for $ticker"
    else
        echo "   ⚠️  No JSON logs found for $ticker"
    fi
done

echo ""
echo "🎉 All provider analyses completed!"
echo "📁 Results saved in: $OUTPUT_DIR"
echo "📄 Files include:"
echo "   - trading_analysis_{date}_{provider}.txt (console output)"
echo "   - full_states_log_{date}.json (detailed analysis logs)"
