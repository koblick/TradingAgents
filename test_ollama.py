#!/usr/bin/env python3
"""
Simple test script to verify Ollama integration with TradingAgents
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

def test_ollama_connection():
    """Test basic Ollama connectivity"""
    print("Testing Ollama connection...")
    
    # Create custom config for Ollama
    config = DEFAULT_CONFIG.copy()
    config["llm_provider"] = "ollama"
    config["ollama_base_url"] = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    config["ollama_deep_model"] = os.getenv("OLLAMA_DEEP_MODEL", "gpt-oss:120b")
    config["ollama_quick_model"] = os.getenv("OLLAMA_QUICK_MODEL", "gpt-oss:latest")
    config["backend_url"] = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")  # Override backend URL for Ollama
    config["max_debate_rounds"] = 1  # Reduce rounds for faster testing
    config["max_risk_discuss_rounds"] = 1
    config["online_tools"] = True  # Use cached data for faster testing
    
    print(f"Configuration:")
    print(f"  Provider: {config['llm_provider']}")
    print(f"  Deep model: {config['ollama_deep_model']}")
    print(f"  Quick model: {config['ollama_quick_model']}")
    print(f"  Base URL: {config['ollama_base_url']}")
    
    try:
        # Initialize TradingAgentsGraph with Ollama config
        ta = TradingAgentsGraph(
            selected_analysts=["market"],  # Test with just one analyst for speed
            debug=True,  # Enable debug mode to see all outputs
            config=config
        )
        
        print("\n✅ TradingAgentsGraph initialized successfully with Ollama!")
        
        # Test a simple analysis
        print("\n🧪 Running test analysis on AAPL...")
        final_state, decision = ta.propagate("AAPL", "2025-08-30")
        
        print(f"\n📊 Analysis Results:")
        print(f"Decision: {decision}")
        
        print(f"\n📋 Final State Keys: {list(final_state.keys())}")
        
        # Print key components of final state
        for key, value in final_state.items():
            print(f"\n=== {key.upper()} ===")
            if isinstance(value, str):
                if len(value) > 500:
                    print(f"{value[:500]}...")
                else:
                    print(value)
            elif isinstance(value, dict):
                print(f"Dict with keys: {list(value.keys())}")
                for k, v in value.items():
                    if isinstance(v, str) and len(v) < 200:
                        print(f"  {k}: {v}")
                    else:
                        print(f"  {k}: {type(v)} (length: {len(str(v))})")
            else:
                print(f"{type(value)}: {str(value)[:200]}")
        
        print("\n🎉 Ollama integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error during Ollama test: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = test_ollama_connection()
    exit(0 if success else 1)