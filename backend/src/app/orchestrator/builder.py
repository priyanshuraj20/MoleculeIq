"""
orchestrator/builder.py

LangGraph StateGraph builder for MoleculeIQ research pipeline.

Constructs and compiles a parallel fan-out execution DAG:
  START -> [clinical_node, literature_node, market_node, patent_node, repurposing_node] -> END
"""

import logging
from langgraph.graph import StateGraph, START, END

from app.domain.agent_state import AgentState
from app.orchestrator.nodes import (
    clinical_node,
    literature_node,
    market_node,
    patent_node,
    repurposing_node,
)

logger = logging.getLogger(__name__)


def build_research_graph():
    """
    Constructs and compiles the parallel LangGraph StateGraph pipeline.
    All 5 domain agents fan out concurrently from START and merge into AgentState.
    """
    logger.info("[Orchestrator] Building parallel LangGraph StateGraph pipeline...")

    builder = StateGraph(AgentState)

    builder.add_node("clinical_node",    clinical_node)
    builder.add_node("literature_node",  literature_node)
    builder.add_node("market_node",      market_node)
    builder.add_node("patent_node",      patent_node)
    builder.add_node("repurposing_node", repurposing_node)

    # Parallel fan-out from START -> all 5 domain agents -> END
    builder.add_edge(START, "clinical_node")
    builder.add_edge(START, "literature_node")
    builder.add_edge(START, "market_node")
    builder.add_edge(START, "patent_node")
    builder.add_edge(START, "repurposing_node")

    builder.add_edge("clinical_node",    END)
    builder.add_edge("literature_node",  END)
    builder.add_edge("market_node",      END)
    builder.add_edge("patent_node",      END)
    builder.add_edge("repurposing_node", END)

    compiled_graph = builder.compile()
    logger.info("[Orchestrator] Parallel LangGraph pipeline compiled successfully.")
    return compiled_graph
