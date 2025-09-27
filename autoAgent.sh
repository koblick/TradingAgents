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
TICKERS=("BA" "AAPL" "GOOGL" "AMZN" "CVX" "NVDA" "UNH" "TSM" "ASML")

# Define base output directory
BASE_OUTPUT_DIR="./results/"

# Get current date in YYYY-MM-DD format
CURRENT_DATE=$(date +"%Y-%m-%d_%H-%M-%S")

# Create date-specific output directory
OUTPUT_DIR="$BASE_OUTPUT_DIR$CURRENT_DATE/"

# Create the directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Define providers array
PROVIDERS=('ollama')

echo "📊 Analyzing the following stocks: ${TICKERS[*]}"
echo "📁 Base output directory: $BASE_OUTPUT_DIR"
echo "📅 Date-specific directory: $OUTPUT_DIR"
echo "🤖 Providers: ${PROVIDERS[*]}"
echo "🔄 Running all analyses sequentially..."
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
    
    # Create a detailed log file for this ticker
    local log_file="$ticker_output_dir/full_analysis_log.txt"
    
    echo "📝 Full analysis log will be saved to: $log_file"
    
    # Try different methods to run the analysis with full output capture
    if command -v uv &> /dev/null; then
        echo "Using uv command for $ticker..."
        echo "=== ANALYSIS START: $(date) ===" >> "$log_file"
        uv run python main.py --tickers "$ticker" -p "$provider" --output-dir "$ticker_output_dir" 2>&1 | tee -a "$log_file"
        echo "=== ANALYSIS END: $(date) ===" >> "$log_file"
    else
        echo "Using system Python for $ticker..."
        echo "=== ANALYSIS START: $(date) ===" >> "$log_file"
        python main.py --tickers "$ticker" -p "$provider" --output-dir "$ticker_output_dir" 2>&1 | tee -a "$log_file"
        echo "=== ANALYSIS END: $(date) ===" >> "$log_file"
    fi
    
    echo "✅ Completed analysis for $ticker with $provider provider"
    echo "📁 Results saved in: $ticker_output_dir"
    echo "📝 Full log saved in: $log_file"
    echo "========================================================"
}

# Run all analyses sequentially
echo "🔄 Starting sequential analyses..."
echo "================================="

for provider in "${PROVIDERS[@]}"; do
    echo "🤖 Starting $provider provider analysis..."
    echo "----------------------------------------"
    
    for ticker in "${TICKERS[@]}"; do
        echo "📊 Processing $ticker with $provider..."
        run_ticker_analysis "$ticker" "$provider" "$OUTPUT_DIR"
        
        if [ $? -eq 0 ]; then
            echo "✅ Completed $ticker with $provider"
        else
            echo "❌ Failed $ticker with $provider"
        fi
        echo ""
    done
    
    echo "✅ Completed all tickers for $provider provider"
    echo "=============================================="
    echo ""
done

echo ""
echo "🎉 All analyses completed successfully!"
echo "📁 Results saved in: $OUTPUT_DIR"
echo "📄 Files include:"
echo "   - {ticker}/trading_analysis_{date}_{provider}.txt (console output)"
echo "   - {ticker}/structured_report_{ticker}_{date}_{provider}.md (structured reports)"
