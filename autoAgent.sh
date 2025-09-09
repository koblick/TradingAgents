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
TICKERS=("AAPL" "GOOGL" "AMZN" "CVX" "NVDA" "UNH" "TSM" "SNOW" "IAU" "SPY")

# Define base output directory
BASE_OUTPUT_DIR="/Users/koblick/Library/Mobile Documents/com~apple~CloudDocs/Coorbital/StockAnalysis/"

# Get current date in YYYY-MM-DD format
CURRENT_DATE=$(date +"%Y-%m-%d_%H-%M-%S")

# Create date-specific output directory
OUTPUT_DIR="$BASE_OUTPUT_DIR$CURRENT_DATE/"

# Create the directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Define providers array
# PROVIDERS=("openai" "deepseek")
PROVIDERS=("deepseek")


echo "📊 Analyzing the following stocks: ${TICKERS[*]}"
echo "📁 Base output directory: $BASE_OUTPUT_DIR"
echo "📅 Date-specific directory: $OUTPUT_DIR"
echo "🤖 Providers: ${PROVIDERS[*]}"
echo "⚡ Running tickers in parallel for faster processing!"
echo ""

# Function to run analysis for a single ticker
run_ticker_analysis() {
    local ticker=$1
    local provider=$2
    local output_dir=$3
    
    echo "🔄 Starting analysis for $ticker with $provider provider..."
    echo "========================================================"
    
    # Create ticker-specific output directory
    local ticker_output_dir="$output_dir${ticker}/"
    mkdir -p "$ticker_output_dir"
    
    # Try different methods to run the analysis
    if command -v uv &> /dev/null; then
        echo "Using uv command for $ticker..."
        uv run python main.py --tickers "$ticker" -p "$provider" --output-dir "$ticker_output_dir"
    else
        echo "Using system Python for $ticker..."
        python main.py --tickers "$ticker" -p "$provider" --output-dir "$ticker_output_dir"
    fi
    
    echo "✅ Completed analysis for $ticker with $provider provider"
    echo "📁 Results saved in: $ticker_output_dir"
    echo "========================================================"
}

# Array to store all background process PIDs
declare -a all_pids=()

echo "🔄 Starting all analyses in parallel..."
echo "======================================"

# Start analysis for each ticker and provider combination in parallel
for provider in "${PROVIDERS[@]}"; do
    for ticker in "${TICKERS[@]}"; do
        run_ticker_analysis "$ticker" "$provider" "$OUTPUT_DIR" &
        all_pids+=($!)
        echo "🚀 Started background process for $ticker with $provider (PID: $!)"
    done
done

echo ""
echo "⏳ Waiting for all analyses to complete..."
echo "Running processes: ${all_pids[*]}"
echo "Total processes: ${#all_pids[@]}"
echo ""

# Wait for all background processes to complete
for pid in "${all_pids[@]}"; do
    wait $pid
    echo "✅ Process $pid completed"
done

echo ""
echo "✅ Completed all analyses!"
echo "========================="
echo ""

echo ""
echo "🎉 All provider analyses completed!"
echo "📁 Results saved in: $OUTPUT_DIR"
echo "📄 Files include:"
echo "   - {ticker}/trading_analysis_{date}_{provider}.txt (console output)"
echo "   - {ticker}/structured_report_{ticker}_{date}_{provider}.md (structured reports)"
