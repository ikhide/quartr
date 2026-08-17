"""Rendering filing documents to PDF with headless Chromium."""

from pathlib import Path

from playwright.async_api import Browser, async_playwright

from quartr import constants


class PdfRenderer:

    def __init__(self) -> None:
        self._playwright = None
        self._browser: Browser | None = None

    async def __aenter__(self) -> "PdfRenderer":
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch()
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def render(self, url: str, destination: Path) -> None:
        if self._browser is None:
            raise RuntimeError("PdfRenderer must be used as a context manager")

        # The browser fetches the document and its images itself, so it needs the
        # same contact-carrying User-Agent the HTTP client uses. Chromium also
        # advertises "HeadlessChrome" via the sec-ch-ua client hint, which the SEC
        # rejects as an undeclared automated tool, so that is declared too.
        context = await self._browser.new_context(
            user_agent=constants.SEC_USER_AGENT,
            extra_http_headers={"sec-ch-ua": constants.SEC_USER_AGENT},
        )
        try:
            page = await context.new_page()
            response = await page.goto(url, wait_until="load")
            if response is None or not response.ok:
                status = response.status if response else "no response"
                raise RuntimeError(f"Could not load {url} ({status})")

            await page.pdf(
                path=str(destination),
                format="A4",
                print_background=True,
                margin={
                    "top": "12mm",
                    "bottom": "12mm",
                    "left": "10mm",
                    "right": "10mm",
                },
            )
        finally:
            await context.close()
