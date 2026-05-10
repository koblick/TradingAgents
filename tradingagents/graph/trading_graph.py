# TradingAgents/graph/trading_graph.py

import json
import os
import sys
import time
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from langchain_anthropic import ChatAnthropic
from langchain_deepseek import ChatDeepSeek
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode
from openai import APIConnectionError

from tradingagents.agents import *
from tradingagents.agents.utils.memory import FinancialSituationMemory
from tradingagents.agents.utils.agent_states import (
    AgentState,
    InvestDebateState,
    RiskDebateState,
)
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.dataflows.interface import set_config
from tradingagents.progress import ProgressLogger

from .conditional_logic import ConditionalLogic
from .propagation import Propagator
from .reflection import Reflector
from .setup import GraphSetup
from .signal_processing import SignalProcessor

try:
    import httpx
except ImportError:  # pragma: no cover - httpx is an optional dependency
    httpx = None

RETRYABLE_EXCEPTIONS = (APIConnectionError,)
if httpx is not None:
    RETRYABLE_EXCEPTIONS = RETRYABLE_EXCEPTIONS + (httpx.HTTPError,)


class TradingAgentsGraph:
    """Main class that orchestrates the trading agents framework."""

    def __init__(
        self,
        selected_analysts=["market", "social", "news", "fundamentals"],
        debug=False,
        config: Dict[str, Any] = None,
    ):
        """Initialize the trading agents graph and components.

        Args:
            selected_analysts: List of analyst types to include
            debug: Whether to run in debug mode
            config: Configuration dictionary. If None, uses default config
        """
        self.debug = debug
        self.config = config or DEFAULT_CONFIG
        self.retry_attempts = max(0, int(self.config.get("llm_max_retries", 3)))
        self.retry_backoff = max(1, int(self.config.get("llm_retry_backoff_seconds", 5)))
        self.llm_timeout = self.config.get("llm_timeout_seconds")
        self.retryable_errors = RETRYABLE_EXCEPTIONS
        self.progress_logger = ProgressLogger(self._resolve_progress_log_path())

        # Update the interface's config
        set_config(self.config)

        # Create necessary directories
        os.makedirs(
            os.path.join(self.config["project_dir"], "dataflows/data_cache"),
            exist_ok=True,
        )

        # Initialize LLMs
        if self.config["llm_provider"].lower() == "openai" or self.config["llm_provider"] == "ollama" or self.config["llm_provider"] == "openrouter":
            self.deep_thinking_llm = ChatOpenAI(model=self.config["deep_think_llm"], base_url=self.config["backend_url"], timeout=self.llm_timeout)
            self.quick_thinking_llm = ChatOpenAI(model=self.config["quick_think_llm"], base_url=self.config["backend_url"], timeout=self.llm_timeout)
        elif self.config["llm_provider"].lower() == "anthropic":
            self.deep_thinking_llm = ChatAnthropic(model=self.config["deep_think_llm"], base_url=self.config["backend_url"], timeout=self.llm_timeout)
            self.quick_thinking_llm = ChatAnthropic(model=self.config["quick_think_llm"], base_url=self.config["backend_url"], timeout=self.llm_timeout)
        elif self.config["llm_provider"].lower() == "google":
            self.deep_thinking_llm = ChatGoogleGenerativeAI(model=self.config["deep_think_llm"], timeout=self.llm_timeout)
            self.quick_thinking_llm = ChatGoogleGenerativeAI(model=self.config["quick_think_llm"], timeout=self.llm_timeout)
        elif self.config["llm_provider"].lower() == "deepseek":
            self.deep_thinking_llm = ChatDeepSeek(model=self.config["deep_think_llm"]
            , api_key=self.config["DEEPSEEK_API_KEY"]
            , base_url='https://api.deepseek.com'
            , timeout=self.llm_timeout)
            self.quick_thinking_llm = ChatDeepSeek(model=self.config["quick_think_llm"]
            , api_key=self.config["DEEPSEEK_API_KEY"]
            , base_url='https://api.deepseek.com'
            , timeout=self.llm_timeout)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.config['llm_provider']}")
        
        self.toolkit = Toolkit(config=self.config)

        # Initialize memories
        self.bull_memory = FinancialSituationMemory("bull_memory", self.config)
        self.bear_memory = FinancialSituationMemory("bear_memory", self.config)
        self.trader_memory = FinancialSituationMemory("trader_memory", self.config)
        self.invest_judge_memory = FinancialSituationMemory("invest_judge_memory", self.config)
        self.risk_manager_memory = FinancialSituationMemory("risk_manager_memory", self.config)

        # Create tool nodes
        self.tool_nodes = self._create_tool_nodes()

        # Initialize components
        self.conditional_logic = ConditionalLogic()
        self.graph_setup = GraphSetup(
            self.quick_thinking_llm,
            self.deep_thinking_llm,
            self.toolkit,
            self.tool_nodes,
            self.bull_memory,
            self.bear_memory,
            self.trader_memory,
            self.invest_judge_memory,
            self.risk_manager_memory,
            self.conditional_logic,
            self.progress_logger,
        )

        self.propagator = Propagator()
        self.reflector = Reflector(self.quick_thinking_llm)
        self.signal_processor = SignalProcessor(self.quick_thinking_llm)

        # State tracking
        self.curr_state = None
        self.ticker = None
        self.log_states_dict = {}  # date to full state dict

        # Set up the graph
        self.graph = self.graph_setup.setup_graph(selected_analysts)

    def _resolve_progress_log_path(self):
        if not self.config.get("enable_progress_logging", True):
            return None

        configured_path = self.config.get("progress_log_path")
        if configured_path:
            return configured_path

        return os.path.join(self.config["results_dir"], "progress.jsonl")

    def _create_tool_nodes(self) -> Dict[str, ToolNode]:
        """Create tool nodes for different data sources."""
        return {
            "market": ToolNode(
                [
                    # online tools
                    self.toolkit.get_YFin_data_online,
                    self.toolkit.get_stockstats_indicators_report_online,
                    # offline tools
                    self.toolkit.get_YFin_data,
                    self.toolkit.get_stockstats_indicators_report,
                ]
            ),
            "social": ToolNode(
                [
                    # online tools
                    self.toolkit.get_stock_news_openai,
                    # offline tools
                    self.toolkit.get_reddit_stock_info,
                ]
            ),
            "news": ToolNode(
                [
                    # online tools
                    self.toolkit.get_global_news_openai,
                    self.toolkit.get_google_news,
                    # offline tools
                    self.toolkit.get_finnhub_news,
                    self.toolkit.get_reddit_news,
                ]
            ),
            "fundamentals": ToolNode(
                [
                    # online tools
                    self.toolkit.get_fundamentals_openai,
                    # offline tools
                    self.toolkit.get_finnhub_company_insider_sentiment,
                    self.toolkit.get_finnhub_company_insider_transactions,
                    self.toolkit.get_simfin_balance_sheet,
                    self.toolkit.get_simfin_cashflow,
                    self.toolkit.get_simfin_income_stmt,
                ]
            ),
        }

    def propagate(self, company_name, trade_date):
        """Run the trading agents graph for a company on a specific date."""

        self.ticker = company_name
        self.progress_logger.log(
            "analysis_start",
            ticker=company_name,
            trade_date=str(trade_date),
            provider=self.config.get("llm_provider"),
            quick_model=self.config.get("quick_think_llm"),
            deep_model=self.config.get("deep_think_llm"),
        )

        # Initialize state
        init_agent_state = self.propagator.create_initial_state(
            company_name, trade_date
        )
        args = self.propagator.get_graph_args()

        attempt = 0
        while True:
            try:
                if self.debug:
                    # Debug mode with tracing
                    trace = []
                    for chunk in self.graph.stream(init_agent_state, **args):
                        if len(chunk["messages"]) == 0:
                            pass
                        else:
                            chunk["messages"][-1].pretty_print()
                            trace.append(chunk)

                    final_state = trace[-1]
                else:
                    # Standard mode without tracing
                    final_state = self.graph.invoke(init_agent_state, **args)
                break
            except self.retryable_errors as exc:
                self.progress_logger.log(
                    "analysis_retryable_error",
                    ticker=company_name,
                    trade_date=str(trade_date),
                    attempt=attempt + 1,
                    error_type=type(exc).__name__,
                    error=str(exc),
                )
                if attempt >= self.retry_attempts:
                    raise RuntimeError(
                        f"Failed to complete analysis for {company_name} after {self.retry_attempts} retries due to LLM connection errors."
                    ) from exc
                attempt += 1
                wait_time = self.retry_backoff * attempt
                print(
                    f"Warning: LLM request failed ({exc}). Retrying in {wait_time} seconds "
                    f"(attempt {attempt} of {self.retry_attempts})...",
                    file=sys.stderr,
                )
                time.sleep(wait_time)

        # Store current state for reflection
        self.curr_state = final_state

        # Log state
        self._log_state(trade_date, final_state)

        # Return decision and processed signal
        processed_signal = self.process_signal(final_state["final_trade_decision"])
        self.progress_logger.log(
            "analysis_end",
            ticker=company_name,
            trade_date=str(trade_date),
            decision=processed_signal,
        )
        return final_state, processed_signal

    def _log_state(self, trade_date, final_state):
        """Log the final state to a JSON file."""
        self.log_states_dict[str(trade_date)] = {
            "company_of_interest": final_state["company_of_interest"],
            "trade_date": final_state["trade_date"],
            "market_report": final_state["market_report"],
            "sentiment_report": final_state["sentiment_report"],
            "news_report": final_state["news_report"],
            "fundamentals_report": final_state["fundamentals_report"],
            "investment_debate_state": {
                "bull_history": final_state["investment_debate_state"]["bull_history"],
                "bear_history": final_state["investment_debate_state"]["bear_history"],
                "history": final_state["investment_debate_state"]["history"],
                "current_response": final_state["investment_debate_state"][
                    "current_response"
                ],
                "judge_decision": final_state["investment_debate_state"][
                    "judge_decision"
                ],
            },
            "trader_investment_decision": final_state["trader_investment_plan"],
            "risk_debate_state": {
                "risky_history": final_state["risk_debate_state"]["risky_history"],
                "safe_history": final_state["risk_debate_state"]["safe_history"],
                "neutral_history": final_state["risk_debate_state"]["neutral_history"],
                "history": final_state["risk_debate_state"]["history"],
                "judge_decision": final_state["risk_debate_state"]["judge_decision"],
            },
            "investment_plan": final_state["investment_plan"],
            "final_trade_decision": final_state["final_trade_decision"],
        }

        # Save to file
        directory = Path(f"eval_results/{self.ticker}/TradingAgentsStrategy_logs/")
        directory.mkdir(parents=True, exist_ok=True)

        with open(
            f"eval_results/{self.ticker}/TradingAgentsStrategy_logs/full_states_log_{trade_date}.json",
            "w",
        ) as f:
            json.dump(self.log_states_dict, f, indent=4)

    def reflect_and_remember(self, returns_losses):
        """Reflect on decisions and update memory based on returns."""
        self.reflector.reflect_bull_researcher(
            self.curr_state, returns_losses, self.bull_memory
        )
        self.reflector.reflect_bear_researcher(
            self.curr_state, returns_losses, self.bear_memory
        )
        self.reflector.reflect_trader(
            self.curr_state, returns_losses, self.trader_memory
        )
        self.reflector.reflect_invest_judge(
            self.curr_state, returns_losses, self.invest_judge_memory
        )
        self.reflector.reflect_risk_manager(
            self.curr_state, returns_losses, self.risk_manager_memory
        )

    def process_signal(self, full_signal):
        """Process a signal to extract the core decision."""
        return self.signal_processor.process_signal(full_signal)
