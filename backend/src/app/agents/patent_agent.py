"""
agents/patent_agent.py

Patent Landscape Worker Agent.

Responsibility:
  1. Accepts AgentState.
  2. Reads molecule_name.
  3. Invokes PatentRepository.get_by_molecule().
  4. Updates state.patent with PatentLandscapeDomain.
  5. Appends warning if no patent data is found.
  6. Handles all database errors gracefully without crashing.
"""

import logging
import time
from typing import Optional

from app.domain.agent_state import AgentState
from app.domain.patent import PatentLandscapeDomain
from app.infrastructure.database.patent_repository import PatentRepository

logger = logging.getLogger(__name__)


class PatentAgent:
    """
    Worker agent for retrieving and evaluating patent landscape & FTO intelligence.

    Consumes PatentRepository and attaches PatentLandscapeDomain to AgentState.
    """

    def __init__(self, repository: Optional[PatentRepository] = None):
        # Allow dependency injection for testing; default to fresh repository
        self._repo = repository or PatentRepository()

    def execute(self, state: AgentState) -> AgentState:
        """
        Executes the patent research node synchronously (repository calls are DB-backed).

        Args:
            state: Current AgentState container.

        Returns:
            Updated AgentState with state.patent populated.
        """
        molecule_name = state.molecule_name
        logger.info("[PatentAgent] Execution started for molecule '%s'", molecule_name)
        start_time = time.monotonic()

        try:
            # 1. Fetch patent data from repository
            synonyms = getattr(state, "synonyms", None)
            patent_domain = self._repo.get_by_molecule(molecule_name, synonyms=synonyms)
            elapsed = round(time.monotonic() - start_time, 2)

            # 2. Check if repository returned empty result
            if patent_domain.is_empty:
                warn_msg = f"No patent landscape data found in database for '{molecule_name}'"
                logger.warning("[PatentAgent] %s (took %.2fs)", warn_msg, elapsed)
                state.warnings.append(warn_msg)
            else:
                logger.info(
                    "[PatentAgent] Completed for '%s' in %.2fs: %d patent records mapped (FTO summary: '%s')",
                    molecule_name,
                    elapsed,
                    len(patent_domain.patents),
                    patent_domain.fto_summary
                )

            # 3. Assign to state
            state.patent = patent_domain

        except Exception as exc:
            elapsed = round(time.monotonic() - start_time, 2)
            warn_msg = f"PatentAgent encountered unexpected failure for '{molecule_name}': {str(exc)}"
            logger.error("[PatentAgent] %s (after %.2fs)", warn_msg, elapsed)
            state.patent = PatentLandscapeDomain(molecule_name=molecule_name)
            state.warnings.append(warn_msg)

        return state


# Helper function for functional execution (matches LangGraph node pattern)
def run_patent_agent(state: AgentState, repository: Optional[PatentRepository] = None) -> AgentState:
    """
    Standalone function entrypoint for executing the Patent Agent.
    """
    agent = PatentAgent(repository=repository)
    return agent.execute(state)
