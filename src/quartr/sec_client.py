"""Async HTTP access to the SEC, with throttling and retries."""

import asyncio
import time
from typing import Any

import httpx

from quartr import constants


class SecClient:

    def __init__(self) -> None:
        self._client = httpx.AsyncClient(
            headers={
                "User-Agent": constants.SEC_USER_AGENT,
                "Accept-Encoding": "gzip, deflate",
            },
            timeout=httpx.Timeout(30.0),
            follow_redirects=True,
        )
        self._interval = 1 / constants.REQUESTS_PER_SECOND
        self._lock = asyncio.Lock()
        self._last_request = 0.0

    async def __aenter__(self) -> "SecClient":
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        await self._client.aclose()

    async def get_json(self, url: str) -> Any:
        response = await self._get(url)
        return response.json()

    async def _get(self, url: str) -> httpx.Response:
        last_error: Exception | None = None

        for attempt in range(constants.MAX_RETRIES + 1):
            if attempt:
                await asyncio.sleep(0.5 * 2**(attempt - 1))

            await self._wait_for_slot()
            try:
                response = await self._client.get(url)
            except httpx.TransportError as error:
                last_error = error
                continue

            if response.status_code in constants.RETRYABLE_STATUSES:
                last_error = httpx.HTTPStatusError(
                    f"{response.status_code} from {url}",
                    request=response.request,
                    response=response,
                )
                continue

            # Anything else is final, including 404s that retrying cannot fix.
            response.raise_for_status()
            return response

        raise RuntimeError(
            f"Giving up on {url} after {constants.MAX_RETRIES} retries"
        ) from last_error

    async def _wait_for_slot(self) -> None:
        """Space requests out so concurrent callers stay under the rate limit."""
        async with self._lock:
            delay = self._last_request + self._interval - time.monotonic()
            if delay > 0:
                await asyncio.sleep(delay)
            self._last_request = time.monotonic()
