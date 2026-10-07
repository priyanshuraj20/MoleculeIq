"""
infrastructure/clients/opentargets_client.py

Client for Open Targets Platform GraphQL API & ChEMBL REST API.

API Documentation:
    https://platform-docs.opentargets.org/data-access/graphql-api

Endpoint:
    POST https://api.platform.opentargets.org/api/v4/graphql
    GET  https://www.ebi.ac.uk/chembl/api/data/molecule/search.json?q={query}
"""

import logging
from typing import Optional, Dict, Any, List

from app.infrastructure.clients._base_client import BaseAPIClient

logger = logging.getLogger(__name__)

OPEN_TARGETS_GRAPHQL_URL = "https://api.platform.opentargets.org/api/v4/graphql"
CHEMBL_SEARCH_URL = "https://www.ebi.ac.uk/chembl/api/data/molecule/search.json"


class OpenTargetsClient(BaseAPIClient):
    """
    Client for Open Targets Platform GraphQL API with ChEMBL REST fallback.
    """

    _client_name = "OpenTargets"

    async def search_drug(self, query_string: str) -> Optional[str]:
        """
        Searches for a drug by name and returns its ChEMBL ID.
        Falls back to ChEMBL REST API search if Open Targets returns no match.
        """
        clean_query = query_string.strip()
        gql_search = """
        query searchDrug($queryString: String!) {
          search(queryString: $queryString, entityNames: ["drug"]) {
            total
            hits {
              id
              name
              entity
              description
            }
          }
        }
        """
        payload = {
            "query": gql_search,
            "variables": {"queryString": clean_query}
        }

        res = await self._post(OPEN_TARGETS_GRAPHQL_URL, json_data=payload)
        hits = res.get("data", {}).get("search", {}).get("hits", [])
        if hits:
            # Match top drug hit
            chembl_id = hits[0].get("id")
            logger.info("[OpenTargets] Resolved '%s' -> %s (%s)", clean_query, chembl_id, hits[0].get("name"))
            return chembl_id

        # Fallback to ChEMBL REST API
        logger.info("[OpenTargets] No Open Targets hit for '%s'. Trying ChEMBL REST API fallback...", clean_query)
        chembl_res = await self._get(CHEMBL_SEARCH_URL, params={"q": clean_query})
        molecules = chembl_res.get("molecules", [])
        if molecules:
            top_mol = molecules[0]
            chembl_id = top_mol.get("molecule_chembl_id")
            logger.info("[OpenTargets] ChEMBL fallback resolved '%s' -> %s", clean_query, chembl_id)
            return chembl_id

        logger.warning("[OpenTargets] Could not resolve ChEMBL ID for '%s'", clean_query)
        return None

    async def get_drug_details(self, chembl_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves mechanisms of action, targets, and known indications for a drug.
        """
        query = """
        query drugDetails($chemblId: String!) {
          drug(chemblId: $chemblId) {
            id
            name
            mechanismsOfAction {
              rows {
                mechanismOfAction
                targets {
                  id
                  approvedSymbol
                  approvedName
                }
              }
            }
            indications {
              rows {
                disease {
                  id
                  name
                }
              }
            }
          }
        }
        """
        payload = {
            "query": query,
            "variables": {"chemblId": chembl_id}
        }

        res = await self._post(OPEN_TARGETS_GRAPHQL_URL, json_data=payload)
        drug_data = res.get("data", {}).get("drug")
        return drug_data

    async def get_target_associated_diseases(self, target_id: str, size: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieves associated diseases and scores for a specific protein target.
        """
        query = """
        query targetDiseases($targetId: String!, $size: Int!) {
          target(ensemblId: $targetId) {
            id
            approvedSymbol
            approvedName
            associatedDiseases(page: { index: 0, size: $size }) {
              count
              rows {
                score
                disease {
                  id
                  name
                }
              }
            }
          }
        }
        """
        payload = {
            "query": query,
            "variables": {"targetId": target_id, "size": size}
        }

        res = await self._post(OPEN_TARGETS_GRAPHQL_URL, json_data=payload)
        rows = res.get("data", {}).get("target", {}).get("associatedDiseases", {}).get("rows", [])
        return rows
