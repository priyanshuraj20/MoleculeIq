"""
orchestrator/builder.py

LangGraph StateGraph builder for MoleculeIQ research pipeline.

Constructs and compiles the sequential execution DAG:
  START -> clinical_node -> literature_node -> market_node -> patent_node -> END
"""

import logging
from langgraph.graph import StateGraph, START, END

from app.domain.agent_state import AgentState
from app.orchestrator.nodes import (
    clinical_node,
    literature_node,
    market_node,
    patent_node,
)

logger = logging.getLogger(__name__)


def build_research_graph():
    """
    Constructs and compiles the LangGraph StateGraph pipeline.

    Sequential Execution Flow:
        START
          ↓
      clinical_node
          ↓
     literature_node
          ↓
      market_node
          ↓
      patent_node
          ↓
         END

    Returns:
        Compiled LangGraph Pregel graph executable.
    """
    logger.info("[Orchestrator] Building LangGraph StateGraph pipeline...")

    # 1. Initialize StateGraph with AgentState
    builder = StateGraph(AgentState)

    # 2. Add Worker Agent nodes
    builder.add_node("clinical_node",   clinical_node)
    builder.add_node("literature_node", literature_node)
    builder.add_node("market_node",     market_node)
    builder.add_node("patent_node",     patent_node)

    # 3. Add sequential execution edges
    builder.add_edge(START,             "clinical_node")
    builder.add_edge("clinical_node",   "literature_node")
    builder.add_edge("literature_node", "market_node")
    builder.add_edge("market_node",     "patent_node")
    builder.add_edge("patent_node",     END)

    # 4. Compile graph
    compiled_graph = builder.compile()
    logger.info("[Orchestrator] LangGraph pipeline compiled successfully.")
    return compiled_graph
