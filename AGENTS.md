Tools
CLI tool: Typer
HTTP client: httpx
PDF: Playwright (headless Chromium)
Other: stdlib dataclasses — no Pydantic, no pandas

Task

- To fetch the 10-K report, an annual report that the companies need to submit to the SEC.
- Pull the latest 10-K reports from some of the world's leading companies. Default - Apple, Meta, Alphabet, Amazon, Netflix, Goldman Sachs.

##API

Get CIK from ticker: {SEC_URL}/files/company_tickers.json
Get Submission by CIK: {SEC_DATA_URL}/submissions/CIK##########.json
Fetch 10-k document by accession number: {SEC_URL}/Archives/edgar/data/{cik}/{accession-no-dashes}/{primaryDocument}

Note: filing documents live on www.sec.gov, NOT data.sec.gov — data.sec.gov/Archives/... returns 404.
The CIK is zero-padded to ten digits for submissions, but left unpadded in the Archives path.

Max rate: 10 requests per second
Header must contain User-Agent, including contact info. The SEC returns 403 to any request
without it — including browser-shaped ones. Chromium also advertises "HeadlessChrome" through
the sec-ch-ua client hint, which is rejected as an "undeclared automated tool", so the browser
context must override sec-ch-ua as well as user-agent.

Files

- main.py — Typer CLI plus orchestrator: the company list → concurrent fetch → render → save.
  Accepts a list of company tickers, default to Apple, Meta, Alphabet, Amazon, Netflix, Goldman Sachs. (see constants.py)
  Accepts a --output-dir flag to specify the output directory. Default is ./output.
- sec_client.py: To talk with the API - async HTTP client httpx.
  Pass base URLs and the User-Agent header from .env.
  Retry with exponential backoff. Default to 3 retries.
  Functions are clean, readable and testable, minimal commenting.

- filings.py: This calls sec_client to:
  Resolve ticker to CIK
  fetch submissions
  select the latest 10-K
  build the document URL

- pdf_renderer.py — To convert html to pdf. Use Playwright.
  Must be headless: page.pdf() raises "PDF generation is only supported for Headless Chromium".
  Renders from the live URL, since the filing's image src attributes are relative.

- models.py — frozen dataclasses for Company and Filing.

- constants.py - To hold constant values, read directly from .env. No other module reads .env.
