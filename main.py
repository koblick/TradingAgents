from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from datetime import datetime
import argparse
import sys
import os

class DualOutput:
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.file = open(filename, 'w')
    
    def write(self, message):
        self.terminal.write(message)
        self.file.write(message)
        self.file.flush()  # Ensure immediate write to file
    
    def flush(self):
        self.terminal.flush()
        self.file.flush()
    
    def close(self):
        self.file.close()

def extract_price_target(decision_text):
    """Extract price target from decision text using various patterns."""
    import re
    
    # Common patterns for price targets
    patterns = [
        r'price target[:\s]*\$?([0-9,]+\.?[0-9]*)',  # "price target: $150.50"
        r'target price[:\s]*\$?([0-9,]+\.?[0-9]*)',  # "target price: $150.50"
        r'\$([0-9,]+\.?[0-9]*)\s*(?:price target|target)',  # "$150.50 price target"
        r'([0-9,]+\.?[0-9]*)\s*(?:price target|target)',  # "150.50 price target"
        r'target[:\s]*\$?([0-9,]+\.?[0-9]*)',  # "target: $150.50"
        r'recommended price[:\s]*\$?([0-9,]+\.?[0-9]*)',  # "recommended price: $150.50"
        r'fair value[:\s]*\$?([0-9,]+\.?[0-9]*)',  # "fair value: $150.50"
        r'valuation[:\s]*\$?([0-9,]+\.?[0-9]*)',  # "valuation: $150.50"
    ]
    
    decision_text_lower = decision_text.lower()
    
    for pattern in patterns:
        match = re.search(pattern, decision_text_lower)
        if match:
            price_str = match.group(1).replace(',', '')
            try:
                price = float(price_str)
                return f"${price:.2f}"
            except ValueError:
                continue
    
    return None

def extract_decision_and_target(decision_text):
    """Extract both decision (BUY/HOLD/SELL) and price target from the decision text."""
    import re
    
    # Extract decision (BUY/HOLD/SELL)
    decision_patterns = [
        r'\b(BUY|HOLD|SELL)\b',
        r'\b(buy|hold|sell)\b',
        r'recommendation[:\s]*(BUY|HOLD|SELL)',
        r'decision[:\s]*(BUY|HOLD|SELL)',
    ]
    
    decision = None
    for pattern in decision_patterns:
        match = re.search(pattern, decision_text, re.IGNORECASE)
        if match:
            decision = match.group(1).upper()
            break
    
    # Extract price target
    price_target = extract_price_target(decision_text)
    
    return decision, price_target

def save_structured_report(final_state, ticker, analysis_date, provider, output_dir):
    """Save structured Markdown report similar to CLI's display_complete_report."""
    
    # Create filename
    report_filename = f"structured_report_{ticker}_{analysis_date}_{provider}.md"
    report_path = os.path.join(output_dir, report_filename)
    
    with open(report_path, 'w') as f:
        # Header
        f.write(f"# Trading Analysis Report\n\n")
        f.write(f"**Company:** {ticker}\n")
        f.write(f"**Analysis Date:** {analysis_date}\n")
        f.write(f"**LLM Provider:** {provider.upper()}\n")
        f.write(f"**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        # I. Analyst Team Reports
        f.write("## I. Analyst Team Reports\n\n")
        
        # Market Analyst Report
        if final_state.get("market_report"):
            f.write("### Market Analyst\n\n")
            f.write(f"{final_state['market_report']}\n\n")
            f.write("---\n\n")
        
        # Social Analyst Report
        if final_state.get("sentiment_report"):
            f.write("### Social Analyst\n\n")
            f.write(f"{final_state['sentiment_report']}\n\n")
            f.write("---\n\n")
        
        # News Analyst Report
        if final_state.get("news_report"):
            f.write("### News Analyst\n\n")
            f.write(f"{final_state['news_report']}\n\n")
            f.write("---\n\n")
        
        # Fundamentals Analyst Report
        if final_state.get("fundamentals_report"):
            f.write("### Fundamentals Analyst\n\n")
            f.write(f"{final_state['fundamentals_report']}\n\n")
            f.write("---\n\n")
        
        # II. Research Team Reports
        if final_state.get("investment_debate_state"):
            f.write("## II. Research Team Decision\n\n")
            debate_state = final_state["investment_debate_state"]
            
            # Bull Researcher Analysis
            if debate_state.get("bull_history"):
                f.write("### Bull Researcher\n\n")
                f.write(f"{debate_state['bull_history']}\n\n")
                f.write("---\n\n")
            
            # Bear Researcher Analysis
            if debate_state.get("bear_history"):
                f.write("### Bear Researcher\n\n")
                f.write(f"{debate_state['bear_history']}\n\n")
                f.write("---\n\n")
            
            # Research Manager Decision
            if debate_state.get("judge_decision"):
                f.write("### Research Manager\n\n")
                f.write(f"{debate_state['judge_decision']}\n\n")
                f.write("---\n\n")
        
        # III. Trading Team Reports
        if final_state.get("trader_investment_plan"):
            f.write("## III. Trading Team Plan\n\n")
            f.write("### Trader\n\n")
            f.write(f"{final_state['trader_investment_plan']}\n\n")
            f.write("---\n\n")
        
        # IV. Risk Management Team Reports
        if final_state.get("risk_debate_state"):
            f.write("## IV. Risk Management Team Decision\n\n")
            risk_state = final_state["risk_debate_state"]
            
            # Aggressive (Risky) Analyst Analysis
            if risk_state.get("risky_history"):
                f.write("### Aggressive Analyst\n\n")
                f.write(f"{risk_state['risky_history']}\n\n")
                f.write("---\n\n")
            
            # Conservative (Safe) Analyst Analysis
            if risk_state.get("safe_history"):
                f.write("### Conservative Analyst\n\n")
                f.write(f"{risk_state['safe_history']}\n\n")
                f.write("---\n\n")
            
            # Neutral Analyst Analysis
            if risk_state.get("neutral_history"):
                f.write("### Neutral Analyst\n\n")
                f.write(f"{risk_state['neutral_history']}\n\n")
                f.write("---\n\n")
            
            # Portfolio Manager Decision
            if risk_state.get("judge_decision"):
                f.write("## V. Portfolio Manager Decision\n\n")
                f.write("### Portfolio Manager\n\n")
                f.write(f"{risk_state['judge_decision']}\n\n")
                f.write("---\n\n")
        
        # Final Decision Summary
        if final_state.get("final_trade_decision"):
            f.write("## Final Trading Decision\n\n")
            f.write(f"{final_state['final_trade_decision']}\n\n")
    
    return report_path

def main():
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Run trading analysis for stock symbols')
    parser.add_argument('--tickers', '-t', nargs='+', default=['NVDA'], 
                       help='Stock symbols to analyze (e.g., NVDA BA AAPL)')
    parser.add_argument('--date', '-d', default=None,
                       help='Date to analyze (YYYY-MM-DD format). Defaults to today.')
    parser.add_argument('--provider', '-p', choices=['openai', 'deepseek', 'ollama'], default='openai',
                       help='LLM provider to use: openai, deepseek, or ollama')
    parser.add_argument('--output-dir', '-o', default='.',
                       help='Directory to save output files (default: current directory)')
    
    args = parser.parse_args()
    
    # Create a custom config
    config = DEFAULT_CONFIG.copy()
    config["llm_provider"] = args.provider
    
    # Configure models based on provider
    if args.provider == "openai":
        config["deep_think_llm"] = "o1"
        config["quick_think_llm"] = "gpt-4o-mini"
    elif args.provider == "deepseek":
        config["deep_think_llm"] = "deepseek-reasoner"
        config["quick_think_llm"] = "deepseek-coder"
    elif args.provider == "ollama":
        # Use the Ollama configuration from default_config
        config["deep_think_llm"] = config["ollama_deep_model"]
        config["quick_think_llm"] = config["ollama_quick_model"]
    
    config["max_debate_rounds"] = 1             # Increase debate rounds
    config["online_tools"] = True               # Enable online tools

    # Initialize with custom config
    ta = TradingAgentsGraph(debug=False, config=config)

    # Get date (today if not specified)
    if args.date:
        analysis_date = args.date
    else:
        analysis_date = datetime.now().strftime("%Y-%m-%d")

    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Create output filename with full path
    output_filename = os.path.join(args.output_dir, f"trading_analysis_{analysis_date}_{args.provider}.txt")
    
    # Set up dual output (console + file)
    original_stdout = sys.stdout
    dual_output = DualOutput(output_filename)
    sys.stdout = dual_output
    
    try:
        # Print model configuration
        print(f"\n{'='*60}")
        print(f"MODEL CONFIGURATION:")
        print(f"Provider: {args.provider.upper()}")
        print(f"Deep Think Model: {config['deep_think_llm']}")
        print(f"Quick Think Model: {config['quick_think_llm']}")
        print(f"Analysis Date: {analysis_date}")
        print(f"Output Directory: {os.path.abspath(args.output_dir)}")
        print(f"{'='*60}\n")

        # Process each ticker
        for ticker in args.tickers:
            print(f"\n{'='*50}")
            print(f"Analyzing {ticker} for date: {analysis_date}")
            print(f"Using {args.provider.upper()} LLM provider")
            print(f"{'='*50}")
            
            # forward propagate
            final_state, decision = ta.propagate(ticker, analysis_date)
            
            # Extract decision and price target
            decision_type, price_target = extract_decision_and_target(decision)
            
            # Display decision with price target
            if decision_type and price_target:
                print(f"Decision for {ticker}: {decision_type} | Price Target: {price_target}")
            elif decision_type:
                print(f"Decision for {ticker}: {decision_type}")
            else:
                print(f"Decision for {ticker}: {decision}")
            
            # Save structured Markdown report
            report_path = save_structured_report(final_state, ticker, analysis_date, args.provider, args.output_dir)
            print(f"Structured report saved: {os.path.basename(report_path)}")

        # Memorize mistakes and reflect
        # ta.reflect_and_remember(1000) # parameter is the position returns
    
    finally:
        # Restore stdout and close file
        sys.stdout = original_stdout
        dual_output.close()
    
    # Print confirmation to console
    print(f"\nAnalysis completed! Results also saved to: {output_filename}")

if __name__ == "__main__":
    main()
