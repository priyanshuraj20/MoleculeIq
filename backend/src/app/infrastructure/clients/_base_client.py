"""
infrastructure/clients/_base_client.py

Shared async HTTP base client used by all external API clients.
Includes automatic exponential backoff retry and WAF-bypassing curl.exe fallback.
"""

import asyncio
import logging
import time

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)


class BaseAPIClient:
    """
    Shared async HTTP client base class.
    Subclasses get retry, timeout, WAF fallback, and logging for free.
    """

    _client_name: str = "APIClient"

    def __init__(self):
        self._http = httpx.AsyncClient(
            timeout=httpx.Timeout(
                connect=settings.API_CONNECT_TIMEOUT,
                read=settings.API_READ_TIMEOUT,
                write=settings.API_CONNECT_TIMEOUT,
                pool=settings.API_CONNECT_TIMEOUT,
            ),
            follow_redirects=True,
            headers={
                "User-Agent": DEFAULT_USER_AGENT,
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
                "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
            },
        )

    async def close(self):
        """Close the underlying HTTP connection pool."""
        await self._http.aclose()

    async def _get(
        self,
        url: str,
        params: dict | None = None,
        headers: dict | None = None,
    ) -> dict:
        """
        Perform a GET request with exponential backoff retry.
        Returns parsed JSON dict on success, empty dict {} on failure.
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

                # Handle HTTP 403 WAF blocks
                if response.status_code == 403:
                    logger.warning(
                        "[%s] 403 WAF block on httpx for %s — executing curl.exe fallback",
                        self._client_name, url
                    )
                    curl_data = await self._curl_fallback(url, params=params, headers=headers)
                    if curl_data:
                        return curl_data

                if 400 <= response.status_code < 500:
                    logger.warning(
                        "[%s] 4xx response %d for %s — not retrying",
                        self._client_name, response.status_code, url
                    )
                    return {}

                if response.status_code >= 500:
                    raise httpx.HTTPStatusError(
                        f"5xx {response.status_code}",
                        request=response.request,
                        response=response,
                    )

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

            if attempt < settings.API_MAX_RETRIES:
                wait = settings.API_RETRY_WAIT_MIN * (2 ** (attempt - 1))
                logger.info("[%s] Retrying in %.0fs...", self._client_name, wait)
                await asyncio.sleep(wait)

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
        Fallback using system curl.exe with full browser User-Agent headers
        when Python's httpx TLS fingerprint is challenged by Cloudflare/WAF.
        """
        import json
        import urllib.parse

        full_url = url
        if params:
            full_url = f"{url}?{urllib.parse.urlencode(params)}"

        cmd = [
            "curl.exe",
            "-s",
            "-L",
            "-m", str(int(settings.API_READ_TIMEOUT)),
            "-A", DEFAULT_USER_AGENT,
            "-H", "Accept: application/json",
            full_url,
        ]

        if headers:
            for key, val in headers.items():
                if key.lower() not in ("user-agent", "accept"):
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
