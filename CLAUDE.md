# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TradingAgents is a multi-agent LLM financial trading framework that mirrors real-world trading firm dynamics. The system uses specialized AI agents for analysis, research, trading, and risk management to make collaborative trading decisions.

## Common Development Commands

### Environment Setup
```bash
# Install dependencies (pip recommended - uv not available)
pip install -r requirements.txt
# Or install in editable mode
pip install -e .
```

### Running the Application
```bash
# Interactive CLI interface
python -m cli.main

# Direct Python usage
python main.py --tickers NVDA AAPL --provider openai --date 2024-05-10

# Command line options for main.py:
# --tickers/-t: Stock symbols to analyze (default: NVDA)
# --date/-d: Analysis date in YYYY-MM-DD format (default: today)
# --provider/-p: LLM provider (openai, deepseek) (default: openai)
# --output-dir/-o: Output directory (default: current directory)
```

### Testing
```bash
# Run tests using pytest (configured in pyproject.toml)
pytest

# Run with coverage
pytest --cov=tradingagents

# Run specific test markers
pytest -m "not slow"  # Skip slow tests
pytest -m integration  # Run integration tests only
pytest -m unit  # Run unit tests only
```

## Architecture Overview

### Core Framework Structure

The system is built on **LangGraph** for modularity and uses a multi-agent architecture:

**Main Components:**
- `TradingAgentsGraph`: Main orchestrator class that coordinates all agents
- Agent types: Analysts → Researchers → Trader → Risk Management → Portfolio Manager
- Data flows: Real-time and cached financial data processing
- Graph-based execution: Conditional logic and propagation system

### Agent Hierarchy and Flow

1. **Analyst Team** (`tradingagents/agents/analysts/`):
   - `market_analyst.py`: Technical analysis and market indicators
   - `fundamentals_analyst.py`: Company financials and valuation
   - `news_analyst.py`: News impact analysis
   - `social_media_analyst.py`: Social sentiment analysis

2. **Research Team** (`tradingagents/agents/researchers/`):
   - `bull_researcher.py`: Bullish perspective analysis  
   - `bear_researcher.py`: Bearish perspective analysis
   - Research debates with configurable rounds (`max_debate_rounds`)

3. **Trading Team** (`tradingagents/agents/trader/`):
   - `trader.py`: Creates investment plans based on analyst/research input

4. **Risk Management** (`tradingagents/agents/risk_mgmt/`):
   - `aggresive_debator.py`: High-risk tolerance perspective
   - `conservative_debator.py`: Low-risk tolerance perspective  
   - `neutral_debator.py`: Balanced risk assessment
   - Risk debates with configurable rounds (`max_risk_discuss_rounds`)

5. **Management Layer** (`tradingagents/agents/managers/`):
   - `research_manager.py`: Judges research team debates
   - `risk_manager.py`: Final portfolio management decisions

### Data Processing System

**Data Sources** (`tradingagents/dataflows/`):
- `finnhub_utils.py`: FinnHub API integration (financial data)
- `yfin_utils.py`: Yahoo Finance integration
- `reddit_utils.py`: Reddit sentiment analysis (requires PRAW)
- `googlenews_utils.py`: News feed processing
- `stockstats_utils.py`: Technical indicator calculations

**Configuration System**:
- `tradingagents/default_config.py`: Central configuration
- Environment variables for API keys (OPENAI_API_KEY, FINNHUB_API_KEY, etc.)
- Online vs cached data modes (`online_tools` flag)

### LLM Integration

**Supported Providers**:
- OpenAI: `o1` (deep thinking), `gpt-4o-mini` (quick thinking)
- DeepSeek: `deepseek-reasoner` (deep), `deepseek-coder` (quick)
- Anthropic and Google models also supported

**Model Configuration**:
- `deep_think_llm`: Complex reasoning tasks (o1, deepseek-reasoner)
- `quick_think_llm`: Fast operations (gpt-4o-mini, deepseek-coder)
- Provider selection via `llm_provider` config parameter

### Graph Execution System

**Core Graph Components** (`tradingagents/graph/`):
- `trading_graph.py`: Main TradingAgentsGraph orchestrator
- `conditional_logic.py`: Decision flow routing
- `propagation.py`: Data propagation between agents  
- `setup.py`: Graph initialization and configuration
- `reflection.py`: Learning and memory systems
- `signal_processing.py`: Market signal processing

**State Management**:
- `AgentState`: Main state container for the trading pipeline
- `InvestDebateState`: Research team discussion state
- `RiskDebateState`: Risk management discussion state

## Required API Keys

Set these environment variables:
- `FINNHUB_API_KEY`: Financial data (free tier supported)
- `OPENAI_API_KEY`: OpenAI models
- `DEEPSEEK_API_KEY`: DeepSeek models (optional)
- `ANTHROPIC_API_KEY`: Claude models (optional)  
- `GOOGLE_API_KEY`: Gemini models (optional)

## Key Configuration Parameters

In `tradingagents/default_config.py`:
- `max_debate_rounds`: Research team discussion rounds (default: 3)
- `max_risk_discuss_rounds`: Risk management discussion rounds (default: 3)
- `online_tools`: Use real-time data vs cached data (default: True)
- `results_dir`: Output directory for analysis results

## Output and Reporting

**CLI Mode**: Interactive interface with real-time progress display
**Script Mode**: Generates two output files:
- Text file: Complete analysis log (`trading_analysis_{date}_{provider}.txt`)
- Markdown report: Structured report (`structured_report_{ticker}_{date}_{provider}.md`)

## Memory and Learning System

The framework includes a financial situation memory system (`tradingagents/agents/utils/memory.py`) that can learn from trading outcomes and adjust future decisions. This is accessed via the `reflect_and_remember()` method on TradingAgentsGraph instances.