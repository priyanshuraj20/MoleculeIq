"""
orchestrator/nodes.py

LangGraph node definitions for the MoleculeIQ research pipeline.

Each node wraps a single Worker Agent, ensuring:
  1. Standard node interface (accepts AgentState, returns updated AgentState).
  2. Isolated execution logging and timing.
  3. Exception containment — if a node encounters an unexpected error, the error
     is appended to state.errors and execution continues to subsequent nodes.
"""

import logging
import time

from app.domain.agent_state import AgentState
from app.agents.clinical_agent import ClinicalTrialsAgent
from app.agents.literature_agent import LiteratureAgent
from app.agents.market_agent import MarketAgent
from app.agents.patent_agent import PatentAgent

logger = logging.getLogger(__name__)

# Reusable agent instances inside node execution pool
_clinical_agent   = ClinicalTrialsAgent()
_literature_agent = LiteratureAgent()
_market_agent     = MarketAgent()
_patent_agent     = PatentAgent()


async def clinical_node(state: AgentState) -> AgentState:
    """
    Node 1: Executes ClinicalTrialsAgent to gather active/completed clinical trial data.
    """
    logger.info("[Node: clinical] Executing for molecule '%s'", state.molecule_name)
    start_time = time.monotonic()
    try:
        updated_state = await _clinical_agent.execute(state)
        elapsed = round(time.monotonic() - start_time, 2)
        logger.info("[Node: clinical] Completed in %.2fs", elapsed)
        return updated_state
    except Exception as exc:
        elapsed = round(time.monotonic() - start_time, 2)
        err_msg = f"Node 'clinical' unhandled exception for '{state.molecule_name}': {str(exc)}"
        logger.error("[Node: clinical] %s (after %.2fs)", err_msg, elapsed)
        state.errors.append(err_msg)
        return state


async def literature_node(state: AgentState) -> AgentState:
    """
    Node 2: Executes LiteratureAgent to gather PubMed/Europe PMC scientific publications.
    """
    logger.info("[Node: literature] Executing for molecule '%s'", state.molecule_name)
    start_time = time.monotonic()
    try:
        updated_state = await _literature_agent.execute(state)
        elapsed = round(time.monotonic() - start_time, 2)
        logger.info("[Node: literature] Completed in %.2fs", elapsed)
        return updated_state
    except Exception as exc:
        elapsed = round(time.monotonic() - start_time, 2)
        err_msg = f"Node 'literature' unhandled exception for '{state.molecule_name}': {str(exc)}"
        logger.error("[Node: literature] %s (after %.2fs)", err_msg, elapsed)
        state.errors.append(err_msg)
        return state


async def market_node(state: AgentState) -> AgentState:
    """
    Node 3: Executes MarketAgent to gather IQVIA sales and market size data.
    """
    logger.info("[Node: market] Executing for molecule '%s'", state.molecule_name)
    start_time = time.monotonic()
    try:
        # MarketAgent.execute is synchronous (DB-backed); run directly
        updated_state = _market_agent.execute(state)
        elapsed = round(time.monotonic() - start_time, 2)
        logger.info("[Node: market] Completed in %.2fs", elapsed)
        return updated_state
    except Exception as exc:
        elapsed = round(time.monotonic() - start_time, 2)
        err_msg = f"Node 'market' unhandled exception for '{state.molecule_name}': {str(exc)}"
        logger.error("[Node: market] %s (after %.2fs)", err_msg, elapsed)
        state.errors.append(err_msg)
        return state


async def patent_node(state: AgentState) -> AgentState:
    """
    Node 4: Executes PatentAgent to gather patent filings and FTO status.
    """
    logger.info("[Node: patent] Executing for molecule '%s'", state.molecule_name)
    start_time = time.monotonic()
    try:
        # PatentAgent.execute is synchronous (DB-backed); run directly
        updated_state = _patent_agent.execute(state)
        elapsed = round(time.monotonic() - start_time, 2)
        logger.info("[Node: patent] Completed in %.2fs", elapsed)
        return updated_state
    except Exception as exc:
        elapsed = round(time.monotonic() - start_time, 2)
        err_msg = f"Node 'patent' unhandled exception for '{state.molecule_name}': {str(exc)}"
        logger.error("[Node: patent] %s (after %.2fs)", err_msg, elapsed)
        state.errors.append(err_msg)
        return state
