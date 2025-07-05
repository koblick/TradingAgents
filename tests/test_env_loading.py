#!/usr/bin/env python3
"""
Test script to demonstrate the new environment loading functionality
"""

from tradingagents.utils.env_loader import load_environment_variables, print_environment_status, get_llm_config

def test_environment_loading():
    """Test the environment loading functionality"""
    
    print("🧪 Testing Environment Loading")
    print("=" * 40)
    
    # Test environment loading
    env_info = load_environment_variables()
    
    print(f"\n📁 Environment file: {env_info['env_file_path']}")
    print(f"🔑 FinnHub available: {env_info['validation']['finnhub_available']}")
    print(f"🤖 LLM providers: {env_info['validation']['llm_providers_available']}")
    print(f"✅ All required available: {env_info['validation']['all_required_available']}")
    
    if env_info['validation']['warnings']:
        print("\n⚠️  Warnings:")
        for warning in env_info['validation']['warnings']:
            print(f"   • {warning}")
    
    return env_info

def test_provider_configs():
    """Test provider configuration retrieval"""
    
    print("\n🔧 Testing Provider Configurations")
    print("=" * 40)
    
    providers = ["openai", "google", "anthropic"]
    
    for provider in providers:
        config = get_llm_config(provider)
        print(f"\n📋 {provider.upper()} Configuration:")
        print(f"   Backend URL: {config.get('backend_url', 'Not needed')}")
        print(f"   Embedding Model: {config.get('embedding_model', 'Unknown')}")
        print(f"   API Key Env: {config.get('api_key_env', 'Unknown')}")
        
        quick_models = config.get('supported_models', {}).get('quick_think', [])
        deep_models = config.get('supported_models', {}).get('deep_think', [])
        
        print(f"   Quick Think Models: {len(quick_models)} available")
        print(f"   Deep Think Models: {len(deep_models)} available")

def test_gemini_specific():
    """Test Gemini-specific configuration"""
    
    print("\n🤖 Testing Gemini Configuration")
    print("=" * 40)
    
    google_config = get_llm_config("google")
    
    print(f"Backend URL: {google_config.get('backend_url')}")
    print(f"Embedding Model: {google_config.get('embedding_model')}")
    
    if google_config.get('backend_url') is None:
        print("✅ Correct: Google doesn't need backend_url")
    else:
        print("❌ Incorrect: Google should not have backend_url")
    
    # Test model availability
    quick_models = google_config.get('supported_models', {}).get('quick_think', [])
    deep_models = google_config.get('supported_models', {}).get('deep_think', [])
    
    print(f"\nAvailable Gemini Models:")
    print(f"  Quick Think: {quick_models}")
    print(f"  Deep Think: {deep_models}")

if __name__ == "__main__":
    print("🚀 TradingAgents Environment Testing")
    print("=" * 50)
    
    # Test environment loading
    env_info = test_environment_loading()
    
    # Test provider configurations
    test_provider_configs()
    
    # Test Gemini-specific configuration
    test_gemini_specific()
    
    # Show full environment status
    print("\n" + "=" * 50)
    print_environment_status()
    
    print("\n✅ Environment testing completed!") 