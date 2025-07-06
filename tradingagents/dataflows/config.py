import tradingagents.default_config as default_config
from typing import Dict, Optional
import os

# Use default config but allow it to be overridden
_config: Optional[Dict] = None
DATA_DIR: Optional[str] = None


def validate_api_keys(config: Dict) -> None:
    """Validate that required API keys are present based on LLM provider."""
    llm_provider = config.get("llm_provider", "openai").lower()
    
    # Always require OpenAI API key since many functions use it
    if not config.get("OPENAI_API_KEY"):
        raise ValueError(
            "OPENAI_API_KEY is required in environment variables. "
            "Many functions and tools require OpenAI API access."
        )
    
    # Provider-specific validations
    if llm_provider == "openai":
        if not config.get("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY is required for OpenAI provider")
    # elif llm_provider == "anthropic":
    #     if not config.get("anthropic_api_key"):
    #         raise ValueError("ANTHROPIC_API_KEY is required for Anthropic provider")
    elif llm_provider == "google":
        if not config.get("GOOGLE_API_KEY"):
            raise ValueError("GOOGLE_API_KEY is required for Google provider")


def initialize_config():
    """Initialize the configuration with default values."""
    global _config, DATA_DIR
    if _config is None:
        _config = default_config.DEFAULT_CONFIG.copy()
        DATA_DIR = _config["data_dir"]
        validate_api_keys(_config)


def set_config(config: Dict):
    """Update the configuration with custom values."""
    global _config, DATA_DIR
    if _config is None:
        _config = default_config.DEFAULT_CONFIG.copy()
    _config.update(config)
    DATA_DIR = _config["data_dir"]
    validate_api_keys(_config)


def get_config() -> Dict:
    """Get the current configuration."""
    if _config is None:
        initialize_config()
    return _config.copy()


# Initialize with default config
initialize_config()
