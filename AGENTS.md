Tools
CLI tool: Typer
HTTP client: httpx
PDF: Playwright or WeasyPrint
Other: Pydantic, pandas?

Task

- To fetch the 10-K report, an annual report that the companies need to submit to the SEC.
- Pull the latest 10-K reports from some of the world's leading companies. Default - Apple, Meta, Alphabet, Amazon, Netflix, Goldman Sachs.

##API

Get CIK from ticker: https://{Sec_url}/files/company_tickers.json
Get Submission by CIK: https://{sec_data_url}submissions/CIK##########.json
Fetch 10-k document by accession number: https://{sec_data_url}//Archives/edgar/data/{cik}/{accession-no-dashes}/{primaryDocument}

Max rate: 10 requests per second
Header must contain User-Agent

Files

- cli.py:
  Typer CLI tool.
  Accepts a list of company tickers, default to Apple, Meta, Alphabet, Amazon, Netflix, Goldman Sachs. (see constants.py)
  Accepts a --output-dir flag to specify the output directory. Default is current working directory.
- sec_client.py: To talk with the API - async HTTP client httpx.
  Pass base URLs and the User-Agent header from .env.
  Retry with exponential backoff. Default to 3 retries.
  Functions are clean, readable and testable, minimal commenting.

- filings.py: This calls sec_client to:
  Resolve ticker to CIK
  fetch submissions
  select the latest 10-K
  build the document URL

- pdf_renderer.py — To convert html to pdf. Use Playwrite with. Not headless.

- models.py — optional models.

- constants.py - To hold constant values, read directly from .env. cli.py no longer reads from .env. cli reads from constants.py.

- main.py — orchestrator: the company list → concurrent fetch → render → save.
