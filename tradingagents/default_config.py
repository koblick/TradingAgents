import os

DEFAULT_CONFIG = {
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
    "results_dir": os.getenv("TRADINGAGENTS_RESULTS_DIR", "./results"),
    "data_dir": "/Users/yluo/Documents/Code/ScAI/FR1-data", # TODO: change to your own data directory
    "data_cache_dir": os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
        "dataflows/data_cache",
    ),
    # API Keys - load from environment variables
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    "FINNHUB_API_KEY": os.getenv("FINNHUB_API_KEY"),
    "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
    "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
    "DEEPSEEK_API_KEY": os.getenv("DEEPSEEK_API_KEY"),
    # LLM settings
    "llm_provider": "openai",
    "deep_think_llm": "o4-mini",
    "quick_think_llm": "gpt-4o-mini",
    "backend_url": "https://api.openai.com/v1",
    # Debate and discussion settings
    "max_debate_rounds": 3,
    "max_risk_discuss_rounds": 3,
    "max_recur_limit": 100,
    # Tool settings
    "online_tools": True,
}
