"""PandaScore API client for Rainbow Six Siege match data."""

from __future__ import annotations

from typing import Any

import aiohttp

from .const import API_BASE_URL, UPCOMING_MATCHES_PATH


class PandaScoreApiError(Exception):
    """Generic PandaScore API error."""


class PandaScoreAuthError(PandaScoreApiError):
    """Raised when the API token is missing or invalid."""


class PandaScoreRateLimitError(PandaScoreApiError):
    """Raised when the API rate limit has been exceeded."""

    def __init__(self, retry_after: int | None = None) -> None:
        super().__init__("PandaScore API rate limit exceeded")
        self.retry_after = retry_after


class PandaScoreApiClient:
    """Thin async client for the PandaScore R6 Siege matches endpoint."""

    def __init__(self, session: aiohttp.ClientSession, api_key: str) -> None:
        self._session = session
        self._api_key = api_key

    async def async_get_upcoming_matches(self, per_page: int = 5) -> list[dict[str, Any]]:
        """Return upcoming R6 Siege matches, soonest first."""
        url = f"{API_BASE_URL}{UPCOMING_MATCHES_PATH}"
        headers = {"Authorization": f"Bearer {self._api_key}"}
        params = {"sort": "begin_at", "per_page": str(per_page), "page": "1"}

        try:
            async with self._session.get(url, headers=headers, params=params) as response:
                if response.status in (401, 403):
                    raise PandaScoreAuthError(
                        f"PandaScore rejected the API token ({response.status})"
                    )
                if response.status == 429:
                    retry_after = response.headers.get("Retry-After")
                    raise PandaScoreRateLimitError(
                        int(retry_after) if retry_after else None
                    )
                if response.status >= 400:
                    body = await response.text()
                    raise PandaScoreApiError(
                        f"PandaScore API error {response.status}: {body}"
                    )
                return await response.json()
        except aiohttp.ClientError as err:
            raise PandaScoreApiError(
                f"Error communicating with PandaScore API: {err}"
            ) from err
