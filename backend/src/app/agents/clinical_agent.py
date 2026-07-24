"""
agents/clinical_agent.py

Clinical Trials Worker Agent.

Responsibility:
  1. Accepts AgentState.
  2. Reads molecule_name.
  3. Invokes ClinicalTrialsClient.search_molecule().
  4. Maps raw JSON payload into strongly-typed ClinicalDomain objects.
  5. Updates state.clinical_trials.
  6. Handles all network/parsing errors gracefully without crashing.
"""

import logging
import time
from typing import Optional

from app.domain.agent_state import AgentState
from app.domain.clinical import ClinicalDomain, ClinicalTrialRecord
from app.infrastructure.clients.clinicaltrials_client import ClinicalTrialsClient

logger = logging.getLogger(__name__)


class ClinicalTrialsAgent:
    """
    Worker agent for searching and processing clinical trials intelligence.

    Encapsulates all logic for querying ClinicalTrialsClient and converting
    raw API payloads into domain entities.
    """

    def __init__(self, client: Optional[ClinicalTrialsClient] = None):
        # Allow dependency injection for testing; default to fresh client
        self._client = client or ClinicalTrialsClient()

    async def execute(self, state: AgentState) -> AgentState:
        """
        Executes the clinical trials research node.

        Args:
            state: Current AgentState container.

        Returns:
            Updated AgentState with state.clinical_trials populated.
        """
        molecule_name = state.molecule_name
        logger.info("[ClinicalTrialsAgent] Execution started for molecule '%s'", molecule_name)
        start_time = time.monotonic()

        try:
            # 1. Fetch raw API data
            raw_response = await self._client.search_molecule(molecule_name)
            elapsed = round(time.monotonic() - start_time, 2)

            # 2. Check for empty or invalid response
            if not raw_response or "studies" not in raw_response:
                logger.warning(
                    "[ClinicalTrialsAgent] No study data returned for '%s' (took %.2fs)",
                    molecule_name, elapsed
                )
                state.clinical_trials = ClinicalDomain(molecule_name=molecule_name, trials=[], total_found=0)
                if not raw_response:
                    state.errors.append(f"ClinicalTrials API query failed or timed out for '{molecule_name}'")
                return state

            # 3. Map raw JSON studies into domain objects
            studies_json = raw_response.get("studies", [])
            total_found = raw_response.get("totalCount", len(studies_json))

            synonyms = getattr(state, "synonyms", [])
            mapped_trials = []
            for study in studies_json:
                record = self._map_study(study, molecule_name, synonyms)
                if record:
                    mapped_trials.append(record)

            total_found = len(mapped_trials) if mapped_trials else 0

            # 4. Construct ClinicalDomain model
            domain_model = ClinicalDomain(
                molecule_name=molecule_name,
                trials=mapped_trials,
                total_found=total_found,
                source="ClinicalTrials.gov API v2",
            )

            state.clinical_trials = domain_model
            logger.info(
                "[ClinicalTrialsAgent] Completed for '%s' in %.2fs: %d trials mapped (total found: %d)",
                molecule_name, elapsed, len(mapped_trials), total_found
            )

        except Exception as exc:
            elapsed = round(time.monotonic() - start_time, 2)
            error_msg = f"ClinicalTrialsAgent encountered unexpected failure for '{molecule_name}': {str(exc)}"
            logger.error("[ClinicalTrialsAgent] %s (after %.2fs)", error_msg, elapsed)
            state.clinical_trials = ClinicalDomain(molecule_name=molecule_name, trials=[], total_found=0)
            state.errors.append(error_msg)

        return state

    # ------------------------------------------------------------------ #
    # Helper mapping functions
    # ------------------------------------------------------------------ #

    def _map_study(self, study_dict: dict, molecule_name: str = "", synonyms: list[str] | None = None) -> Optional[ClinicalTrialRecord]:
        """
        Safely extracts fields from a ClinicalTrials.gov v2 study dictionary.
        """
        try:
            protocol = study_dict.get("protocolSection", {})

            # Identification
            ident = protocol.get("identificationModule", {})
            nct_id = ident.get("nctId", "UNKNOWN")
            brief_title = ident.get("briefTitle", "")
            official_title = ident.get("officialTitle", "")
            title = brief_title or official_title or "Untitled Study"

            # Relevance validation: study must reference target molecule_name or synonyms
            valid_targets = [molecule_name.lower().strip()] if molecule_name else []
            if synonyms:
                for s in synonyms:
                    ls = s.lower().strip()
                    if ls and ls not in valid_targets:
                        valid_targets.append(ls)

            if valid_targets:
                bt_lower = brief_title.lower()
                ot_lower = official_title.lower()
                interventions = str(protocol.get("armsInterventionsModule", {})).lower()
                conditions = str(protocol.get("conditionsModule", {})).lower()
                matched = any(
                    target in bt_lower or target in ot_lower or target in interventions or target in conditions
                    for target in valid_targets
                )
                if not matched:
                    return None

            # Status & Dates
            status_mod = protocol.get("statusModule", {})
            overall_status = status_mod.get("overallStatus", "UNKNOWN")
            start_date = status_mod.get("startDateStruct", {}).get("date")
            completion_date = status_mod.get("completionDateStruct", {}).get("date")

            # Design & Enrollment
            design_mod = protocol.get("designModule", {})
            phases = design_mod.get("phases", [])
            enrollment = design_mod.get("enrollmentInfo", {}).get("count")

            # Conditions
            conditions_mod = protocol.get("conditionsModule", {})
            conditions = conditions_mod.get("conditions", [])

            # Sponsor
            sponsors_mod = protocol.get("sponsorCollaboratorsModule", {})
            lead_sponsor = sponsors_mod.get("leadSponsor", {}).get("name")

            return ClinicalTrialRecord(
                nct_id=nct_id,
                title=title,
                status=overall_status,
                phases=phases,
                conditions=conditions,
                lead_sponsor=lead_sponsor,
                start_date=start_date,
                completion_date=completion_date,
                enrollment_count=enrollment,
                data_source="ClinicalTrials.gov"
            )
        except Exception as exc:
            logger.warning("[ClinicalTrialsAgent] Failed to map study record: %s", str(exc))
            return None


# Helper function for functional execution (matches LangGraph node pattern)
async def run_clinical_agent(state: AgentState, client: Optional[ClinicalTrialsClient] = None) -> AgentState:
    """
    Standalone function entrypoint for executing the Clinical Trials Agent.
    """
    agent = ClinicalTrialsAgent(client=client)
    return await agent.execute(state)
