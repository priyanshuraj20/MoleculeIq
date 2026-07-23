"""
orchestrator/graph.py

Main entrypoint for executing the MoleculeIQ LangGraph research pipeline.

Exposes:
  - research_graph: Compiled LangGraph executable instance.
  - run_research_pipeline(molecule_name: str) -> AgentState: Convenience async function.
"""

import logging
import time

from app.domain.agent_state import AgentState
from app.orchestrator.builder import build_research_graph

logger = logging.getLogger(__name__)

# Single compiled graph instance shared across API requests
research_graph = build_research_graph()


async def run_research_pipeline(molecule_name: str) -> AgentState:
    """
    Executes the complete multi-agent research pipeline for a given molecule.

    Args:
        molecule_name: Name of the drug or chemical entity (e.g., "Metformin").

    Returns:
        Fully populated AgentState object containing data from all worker agents.
    """
    logger.info("[ResearchPipeline] Starting pipeline for molecule '%s'", molecule_name)
    start_time = time.monotonic()

    # 1. Construct initial input state
    initial_state = AgentState(molecule_name=molecule_name)

    # 2. Invoke compiled LangGraph asynchronously
    final_state_dict_or_obj = await research_graph.ainvoke(initial_state)

    elapsed = round(time.monotonic() - start_time, 2)

    # 3. Ensure response is returned as AgentState dataclass object
    if isinstance(final_state_dict_or_obj, AgentState):
        final_state = final_state_dict_or_obj
    elif isinstance(final_state_dict_or_obj, dict):
        # LangGraph in dictionary mode fallback
        final_state = AgentState(
            molecule_name=final_state_dict_or_obj.get("molecule_name", molecule_name),
            clinical_trials=final_state_dict_or_obj.get("clinical_trials"),
            literature=final_state_dict_or_obj.get("literature"),
            market=final_state_dict_or_obj.get("market"),
            patent=final_state_dict_or_obj.get("patent"),
            errors=final_state_dict_or_obj.get("errors", []),
            warnings=final_state_dict_or_obj.get("warnings", []),
        )
    else:
        final_state = initial_state

    logger.info(
        "[ResearchPipeline] Completed for '%s' in %.2fs (Errors: %d, Warnings: %d)",
        molecule_name, elapsed, len(final_state.errors), len(final_state.warnings)
    )

    return final_state
