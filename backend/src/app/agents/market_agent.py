"""
agents/market_agent.py

Market Insights Worker Agent.

Responsibility:
  1. Accepts AgentState.
  2. Reads molecule_name.
  3. Invokes MarketRepository.get_by_molecule().
  4. Updates state.market with MarketInsightsDomain.
  5. Appends warning if no market data is found.
  6. Handles all database errors gracefully without crashing.
"""

import logging
import time
from typing import Optional

from app.domain.agent_state import AgentState
from app.domain.market import MarketInsightsDomain
from app.infrastructure.database.market_repository import MarketRepository

logger = logging.getLogger(__name__)


class MarketAgent:
    """
    Worker agent for retrieving and evaluating pharmaceutical market intelligence.

    Consumes MarketRepository and attaches MarketInsightsDomain to AgentState.
    """

    def __init__(self, repository: Optional[MarketRepository] = None):
        # Allow dependency injection for testing; default to fresh repository
        self._repo = repository or MarketRepository()

    def execute(self, state: AgentState) -> AgentState:
        """
        Executes the market research node synchronously (repository calls are DB-backed).

        Args:
            state: Current AgentState container.

        Returns:
            Updated AgentState with state.market populated.
        """
        molecule_name = state.molecule_name
        logger.info("[MarketAgent] Execution started for molecule '%s'", molecule_name)
        start_time = time.monotonic()

        try:
            # 1. Fetch market data from repository
            market_domain = self._repo.get_by_molecule(molecule_name)
            elapsed = round(time.monotonic() - start_time, 2)

            # 2. Check if repository returned empty result
            if market_domain.is_empty:
                warn_msg = f"No market sales data found in database for '{molecule_name}'"
                logger.warning("[MarketAgent] %s (took %.2fs)", warn_msg, elapsed)
                state.warnings.append(warn_msg)
            else:
                logger.info(
                    "[MarketAgent] Completed for '%s' in %.2fs: %d data points found (Global size: $%sM)",
                    molecule_name,
                    elapsed,
                    len(market_domain.data_points),
                    market_domain.global_market_size_usd_mn or "N/A"
                )

            # 3. Assign to state
            state.market = market_domain

        except Exception as exc:
            elapsed = round(time.monotonic() - start_time, 2)
            warn_msg = f"MarketAgent encountered unexpected failure for '{molecule_name}': {str(exc)}"
            logger.error("[MarketAgent] %s (after %.2fs)", warn_msg, elapsed)
            state.market = MarketInsightsDomain(molecule_name=molecule_name)
            state.warnings.append(warn_msg)

        return state


# Helper function for functional execution (matches LangGraph node pattern)
def run_market_agent(state: AgentState, repository: Optional[MarketRepository] = None) -> AgentState:
    """
    Standalone function entrypoint for executing the Market Agent.
    """
    agent = MarketAgent(repository=repository)
    return agent.execute(state)
