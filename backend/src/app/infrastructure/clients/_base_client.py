"""
infrastructure/clients/_base_client.py

Shared async HTTP base client used by all three external API clients.

Why a shared base?
  ClinicalTrials, Europe PMC, and Comtrade all need the same things:
  connection timeouts, read timeouts, retry with exponential backoff,
  and consistent failure logging.

  Putting this once here means each client only writes its own
  request logic — no retry boilerplate repeated three times.

Retry strategy:
  Up to API_MAX_RETRIES attempts (default 3).
  Wait time doubles each attempt: 2s → 4s → 8s (exponential backoff).
  Retries on: Timeout, network error, HTTP 5xx.
  Does NOT retry on: HTTP 4xx (client error — retrying won't help).
  Returns empty dict on final failure — never raises to caller.
"""

import asyncio
import logging
import time

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class BaseAPIClient:
    """
    Shared async HTTP client base class.

    Subclasses get retry, timeout, and logging for free.
    They only need to implement search_molecule().
    """

    # Subclasses set this for logging context (e.g. "ClinicalTrials")
    _client_name: str = "APIClient"

    def __init__(self):
        # One shared AsyncClient per instance — reuses connection pool
        self._http = httpx.AsyncClient(
            timeout=httpx.Timeout(
                connect=settings.API_CONNECT_TIMEOUT,
                read=settings.API_READ_TIMEOUT,
                write=settings.API_CONNECT_TIMEOUT,
                pool=settings.API_CONNECT_TIMEOUT,
            ),
            follow_redirects=True,
            headers={
                # ClinicalTrials.gov v2 returns 403 for generic/bot User-Agents.
                # Using a standard browser UA string resolves this.
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "Accept": "application/json",
            },
        )

    async def close(self):
        """Close the underlying HTTP connection pool."""
        await self._http.aclose()

    # ------------------------------------------------------------------ #
    # Protected: used by subclasses to make GET requests with retry
    # ------------------------------------------------------------------ #

    async def _get(
        self,
        url: str,
        params: dict | None = None,
        headers: dict | None = None,
    ) -> dict:
        """
        Perform a GET request with exponential backoff retry.

        Returns parsed JSON dict on success.
        Returns empty dict {} on all failures — never raises.
        """
        last_error: Exception | None = None

        for attempt in range(1, settings.API_MAX_RETRIES + 1):
            start = time.monotonic()

            try:
                logger.info(
                    "[%s] GET %s (attempt %d/%d)",
                    self._client_name, url, attempt, settings.API_MAX_RETRIES
                )

                response = await self._http.get(url, params=params, headers=headers)
                elapsed = round(time.monotonic() - start, 2)

                # 4xx — check for 403 WAF block, try curl.exe fallback before giving up
                if 400 <= response.status_code < 500:
                    if response.status_code == 403:
                        logger.warning(
                            "[%s] 403 WAF block on httpx for %s — trying curl.exe fallback",
                            self._client_name, url
                        )
                        curl_data = await self._curl_fallback(url, params=params, headers=headers)
                        if curl_data:
                            return curl_data

                    logger.warning(
                        "[%s] 4xx response %d for %s — not retrying",
                        self._client_name, response.status_code, url
                    )
                    return {}

                # 5xx — server error, retry
                if response.status_code >= 500:
                    raise httpx.HTTPStatusError(
                        f"5xx {response.status_code}",
                        request=response.request,
                        response=response,
                    )

                # Success
                logger.info(
                    "[%s] Success %d in %.2fs",
                    self._client_name, response.status_code, elapsed
                )
                return response.json()

            except httpx.TimeoutException as exc:
                elapsed = round(time.monotonic() - start, 2)
                last_error = exc
                logger.warning(
                    "[%s] Timeout after %.2fs on attempt %d",
                    self._client_name, elapsed, attempt
                )

            except httpx.NetworkError as exc:
                last_error = exc
                logger.warning(
                    "[%s] Network error on attempt %d: %s",
                    self._client_name, attempt, str(exc)
                )

            except httpx.HTTPStatusError as exc:
                last_error = exc
                logger.warning(
                    "[%s] HTTP error on attempt %d: %s",
                    self._client_name, attempt, str(exc)
                )

            except ValueError as exc:
                # JSON decode failure — body was not valid JSON
                last_error = exc
                logger.warning(
                    "[%s] Invalid JSON response on attempt %d: %s",
                    self._client_name, attempt, str(exc)
                )

            except Exception as exc:
                last_error = exc
                logger.warning(
                    "[%s] Unexpected error on attempt %d: %s",
                    self._client_name, attempt, str(exc)
                )

            # Exponential backoff before next attempt
            if attempt < settings.API_MAX_RETRIES:
                wait = settings.API_RETRY_WAIT_MIN * (2 ** (attempt - 1))
                logger.info(
                    "[%s] Retrying in %.0fs...", self._client_name, wait
                )
                await asyncio.sleep(wait)

        # All attempts exhausted
        logger.error(
            "[%s] All %d attempts failed for %s. Last error: %s",
            self._client_name, settings.API_MAX_RETRIES, url, str(last_error)
        )
        return {}

    async def _curl_fallback(
        self,
        url: str,
        params: dict | None = None,
        headers: dict | None = None,
    ) -> dict:
        """
        Fallback using system curl.exe when Python's httpx TLS fingerprint is blocked by WAF.

        ClinicalTrials.gov uses WAF rules that block httpx default TLS ciphers with HTTP 403.
        curl.exe bypasses WAF fingerprinting cleanly.
        """
        import json
        import urllib.parse

        full_url = url
        if params:
            full_url = f"{url}?{urllib.parse.urlencode(params)}"

        cmd = ["curl.exe", "-s", "-m", str(int(settings.API_READ_TIMEOUT)), full_url]

        if headers:
            for key, val in headers.items():
                cmd.extend(["-H", f"{key}: {val}"])

        try:
            logger.info("[%s] Executing curl.exe fallback for %s", self._client_name, url)
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()

            if proc.returncode == 0 and stdout:
                data = json.loads(stdout.decode("utf-8"))
                logger.info("[%s] curl.exe fallback succeeded for %s", self._client_name, url)
                return data
            else:
                logger.warning(
                    "[%s] curl.exe fallback failed (code %d): %s",
                    self._client_name, proc.returncode, stderr.decode("utf-8")
                )
        except Exception as exc:
            logger.error("[%s] Exception during curl.exe fallback: %s", self._client_name, str(exc))

        return {}

