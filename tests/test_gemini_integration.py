#!/usr/bin/env python3
"""
Test script to verify Gemini integration with TradingAgents
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

def test_gemini_integration():
    """Test the Gemini integration"""
    
    # Check if Google API key is available
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY environment variable not set")
        print("Please set it with: export GOOGLE_API_KEY=your_key_here")
        return False
    
    # Create a config for Gemini
    config = DEFAULT_CONFIG.copy()
    config["llm_provider"] = "google"
    config["backend_url"] = "https://generativelanguage.googleapis.com/v1"
    config["deep_think_llm"] = "gemini-2.0-flash"
    config["quick_think_llm"] = "gemini-2.0-flash"
    config["max_debate_rounds"] = 1
    config["online_tools"] = True
    
    try:
        print("🚀 Testing Gemini integration...")
        
        # Initialize the graph with Gemini
        graph = TradingAgentsGraph(
            selected_analysts=["market", "news"],  # Use fewer analysts for testing
            debug=True,
            config=config
        )
        
        print("✅ TradingAgentsGraph initialized successfully with Gemini")
        
        # Test a simple propagation
        print("🔄 Testing propagation with SPY...")
        _, decision = graph.propagate("SPY", "2024-12-01")
        
        print(f"✅ Propagation completed successfully!")
        print(f"📊 Final decision: {decision}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during Gemini integration test: {str(e)}")
        return False

def test_memory_system():
    """Test the memory system with Gemini embeddings"""
    
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY environment variable not set")
        return False
    
    try:
        from tradingagents.agents.utils.memory import FinancialSituationMemory
        
        config = {
            "llm_provider": "google",
            "backend_url": "https://generativelanguage.googleapis.com/v1"
        }
        
        print("🧠 Testing memory system with Gemini embeddings...")
        
        memory = FinancialSituationMemory("test_memory", config)
        
        # Test adding situations
        test_data = [
            ("High inflation with rising interest rates", "Consider defensive sectors"),
            ("Tech sector volatility increasing", "Reduce exposure to growth stocks")
        ]
        
        memory.add_situations(test_data)
        print("✅ Memory system working with Gemini embeddings")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in memory system test: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testing TradingAgents Gemini Integration")
    print("=" * 50)
    
    # Test memory system first
    memory_success = test_memory_system()
    
    if memory_success:
        # Test full integration
        integration_success = test_gemini_integration()
        
        if integration_success:
            print("\n🎉 All Gemini integration tests passed!")
        else:
            print("\n❌ Gemini integration test failed")
    else:
        print("\n❌ Memory system test failed") 