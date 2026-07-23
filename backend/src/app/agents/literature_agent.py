"""
agents/literature_agent.py

Literature Worker Agent.

Responsibility:
  1. Accepts AgentState.
  2. Reads molecule_name.
  3. Invokes EuropePMCClient.search_molecule().
  4. Maps raw JSON payload into strongly-typed LiteratureDomain objects.
  5. Updates state.literature.
  6. Handles all network/parsing errors gracefully without crashing.
"""

import logging
import time
from typing import Optional

from app.domain.agent_state import AgentState
from app.domain.literature import LiteratureDomain, LiteratureRecord
from app.infrastructure.clients.europepmc_client import EuropePMCClient

logger = logging.getLogger(__name__)


class LiteratureAgent:
    """
    Worker agent for searching and processing scientific literature intelligence.

    Encapsulates all logic for querying EuropePMCClient and converting
    raw API payloads into domain entities.
    """

    def __init__(self, client: Optional[EuropePMCClient] = None):
        # Allow dependency injection for testing; default to fresh client
        self._client = client or EuropePMCClient()

    async def execute(self, state: AgentState) -> AgentState:
        """
        Executes the literature research node.

        Args:
            state: Current AgentState container.

        Returns:
            Updated AgentState with state.literature populated.
        """
        molecule_name = state.molecule_name
        logger.info("[LiteratureAgent] Execution started for molecule '%s'", molecule_name)
        start_time = time.monotonic()

        try:
            # 1. Fetch raw API data
            raw_response = await self._client.search_molecule(molecule_name)
            elapsed = round(time.monotonic() - start_time, 2)

            # 2. Check for empty or invalid response
            if not raw_response or "resultList" not in raw_response:
                logger.warning(
                    "[LiteratureAgent] No publication data returned for '%s' (took %.2fs)",
                    molecule_name, elapsed
                )
                state.literature = LiteratureDomain(molecule_name=molecule_name, publications=[], total_found=0)
                if not raw_response:
                    state.errors.append(f"Europe PMC API query failed or timed out for '{molecule_name}'")
                return state

            # 3. Map raw JSON results into domain objects
            results_json = raw_response.get("resultList", {}).get("result", [])
            total_found = raw_response.get("hitCount", len(results_json))

            mapped_pubs = []
            for item in results_json:
                record = self._map_publication(item)
                if record:
                    mapped_pubs.append(record)

            # 4. Construct LiteratureDomain model
            domain_model = LiteratureDomain(
                molecule_name=molecule_name,
                publications=mapped_pubs,
                total_found=total_found,
                source="Europe PMC REST API",
                confidence=0.85
            )

            state.literature = domain_model
            logger.info(
                "[LiteratureAgent] Completed for '%s' in %.2fs: %d publications mapped (total found: %d)",
                molecule_name, elapsed, len(mapped_pubs), total_found
            )

        except Exception as exc:
            elapsed = round(time.monotonic() - start_time, 2)
            error_msg = f"LiteratureAgent encountered unexpected failure for '{molecule_name}': {str(exc)}"
            logger.error("[LiteratureAgent] %s (after %.2fs)", error_msg, elapsed)
            state.literature = LiteratureDomain(molecule_name=molecule_name, publications=[], total_found=0)
            state.errors.append(error_msg)

        return state

    # ------------------------------------------------------------------ #
    # Helper mapping functions
    # ------------------------------------------------------------------ #

    def _map_publication(self, item: dict) -> Optional[LiteratureRecord]:
        """
        Safely extracts fields from a Europe PMC publication JSON dictionary.
        """
        try:
            title = item.get("title", "Untitled Publication").rstrip(".")
            pmid = item.get("pmid")
            doi = item.get("doi")
            authors = item.get("authorString", "Unknown Authors")
            # Extract journal name cleanly across Europe PMC payload formats
            journal = (
                item.get("journalTitle")
                or item.get("journalInfo", {}).get("journal", {}).get("title")
                or item.get("journalInfo", {}).get("journal", {}).get("medlineAbbreviation")
                or item.get("bookTitle")
                or "Unknown Journal"
            )

            # Parse year cleanly
            pub_year = None
            raw_year = item.get("pubYear")
            if raw_year:
                try:
                    pub_year = int(raw_year)
                except (ValueError, TypeError):
                    pub_year = None

            # Parse citations
            citation_count = 0
            raw_cites = item.get("citedByCount")
            if raw_cites is not None:
                try:
                    citation_count = int(raw_cites)
                except (ValueError, TypeError):
                    citation_count = 0

            # Abstract
            abstract = item.get("abstractText")

            return LiteratureRecord(
                pmid=pmid,
                doi=doi,
                title=title,
                authors=authors,
                journal=journal,
                pub_year=pub_year,
                citation_count=citation_count,
                abstract=abstract,
                data_source="Europe PMC"
            )
        except Exception as exc:
            logger.warning("[LiteratureAgent] Failed to map publication record: %s", str(exc))
            return None


# Helper function for functional execution (matches LangGraph node pattern)
async def run_literature_agent(state: AgentState, client: Optional[EuropePMCClient] = None) -> AgentState:
    """
    Standalone function entrypoint for executing the Literature Agent.
    """
    agent = LiteratureAgent(client=client)
    return await agent.execute(state)
