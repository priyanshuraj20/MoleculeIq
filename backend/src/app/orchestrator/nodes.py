"""
orchestrator/nodes.py

LangGraph node definitions for the MoleculeIQ research pipeline.
Each node executes a single Worker Agent on a local state copy and returns
only the domain keys it owns so parallel fan-out nodes never conflict.
"""

import asyncio
import logging
import time

from app.domain.agent_state import AgentState
from app.agents.clinical_agent import ClinicalTrialsAgent
from app.agents.literature_agent import LiteratureAgent
from app.agents.market_agent import MarketAgent
from app.agents.patent_agent import PatentAgent
from app.agents.repurposing_agent import RepurposingAgent

logger = logging.getLogger(__name__)

_clinical_agent    = ClinicalTrialsAgent()
_literature_agent  = LiteratureAgent()
_market_agent      = MarketAgent()
_patent_agent      = PatentAgent()
_repurposing_agent = RepurposingAgent()


def _clone_input_state(state: AgentState) -> AgentState:
    return AgentState(molecule_name=state.molecule_name, synonyms=list(state.synonyms))


async def clinical_node(state: AgentState) -> dict:
    """Node 1: Executes ClinicalTrialsAgent."""
    logger.info("[Node: clinical] Executing for molecule '%s'", state.molecule_name)
    start_time = time.monotonic()
    try:
        res = await asyncio.wait_for(_clinical_agent.execute(_clone_input_state(state)), timeout=25.0)
        logger.info("[Node: clinical] Completed in %.2fs", round(time.monotonic() - start_time, 2))
        return {"clinical_trials": res.clinical_trials, "errors": res.errors, "warnings": res.warnings}
    except Exception as exc:
        err_msg = f"Node 'clinical' failed for '{state.molecule_name}': {exc}"
        logger.error("[Node: clinical] %s", err_msg)
        return {"errors": [err_msg]}


async def literature_node(state: AgentState) -> dict:
    """Node 2: Executes LiteratureAgent."""
    logger.info("[Node: literature] Executing for molecule '%s'", state.molecule_name)
    start_time = time.monotonic()
    try:
        res = await asyncio.wait_for(_literature_agent.execute(_clone_input_state(state)), timeout=25.0)
        logger.info("[Node: literature] Completed in %.2fs", round(time.monotonic() - start_time, 2))
        return {"literature": res.literature, "errors": res.errors, "warnings": res.warnings}
    except Exception as exc:
        err_msg = f"Node 'literature' failed for '{state.molecule_name}': {exc}"
        logger.error("[Node: literature] %s", err_msg)
        return {"errors": [err_msg]}


async def market_node(state: AgentState) -> dict:
    """Node 3: Executes MarketAgent in worker thread."""
    logger.info("[Node: market] Executing for molecule '%s'", state.molecule_name)
    start_time = time.monotonic()
    try:
        res = await asyncio.wait_for(asyncio.to_thread(_market_agent.execute, _clone_input_state(state)), timeout=15.0)
        logger.info("[Node: market] Completed in %.2fs", round(time.monotonic() - start_time, 2))
        return {"market": res.market, "errors": res.errors, "warnings": res.warnings}
    except Exception as exc:
        err_msg = f"Node 'market' failed for '{state.molecule_name}': {exc}"
        logger.error("[Node: market] %s", err_msg)
        return {"errors": [err_msg]}


async def patent_node(state: AgentState) -> dict:
    """Node 4: Executes PatentAgent in worker thread."""
    logger.info("[Node: patent] Executing for molecule '%s'", state.molecule_name)
    start_time = time.monotonic()
    try:
        res = await asyncio.wait_for(asyncio.to_thread(_patent_agent.execute, _clone_input_state(state)), timeout=15.0)
        logger.info("[Node: patent] Completed in %.2fs", round(time.monotonic() - start_time, 2))
        return {"patent": res.patent, "errors": res.errors, "warnings": res.warnings}
    except Exception as exc:
        err_msg = f"Node 'patent' failed for '{state.molecule_name}': {exc}"
        logger.error("[Node: patent] %s", err_msg)
        return {"errors": [err_msg]}


async def repurposing_node(state: AgentState) -> dict:
    """Node 5: Executes RepurposingAgent."""
    logger.info("[Node: repurposing] Executing for molecule '%s'", state.molecule_name)
    start_time = time.monotonic()
    try:
        res = await asyncio.wait_for(_repurposing_agent.execute(_clone_input_state(state)), timeout=25.0)
        logger.info("[Node: repurposing] Completed in %.2fs", round(time.monotonic() - start_time, 2))
        return {"repurposing": res.repurposing, "errors": res.errors, "warnings": res.warnings}
    except Exception as exc:
        err_msg = f"Node 'repurposing' failed for '{state.molecule_name}': {exc}"
        logger.error("[Node: repurposing] %s", err_msg)
        return {"errors": [err_msg]}
