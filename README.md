# quartr (test)

To fetch the latest 10-K annual report for a set of companies from SEC EDGAR and save each as a PDF.

## Prerequisites

- [`uv`](https://docs.astral.sh/uv/) — install with `curl -LsSf https://astral.sh/uv/install.sh | sh` (macOS/Linux) or see the [install docs](https://docs.astral.sh/uv/getting-started/installation/) for other options.

## Setup

```bash
uv sync
uv run playwright install chromium
cp .env.example .env
```

Edit `.env` and set `SEC_USER_AGENT` to your name and email. The SEC rejects requests
without contact information in the User-Agent header.

## Usage

```bash
uv run quartr fetch                                  # default companies
uv run quartr fetch AAPL,MSFT --output-dir reports   # specific tickers
```

## How it works

The pipeline is:
(1) Resolve each ticker to a CIK (via `company_tickers.json`)
(2) Fetch the company's submissions
(3) Select its latest 10-K
(4) Download and render that document to PDF.

Modules:

- `constants` — configuration, read once from the environment
- `sec_client` — async HTTP to the SEC, with rate-limiting and retries
- `filings` — ticker -> CIK resolution and 10-K selection
- `pdf_renderer` — headless Chromium, HTML -> PDF
- `models` — `Company`, `Filing`, `Result`
- `cli` — Typer entry point and orchestration

Lookups run concurrently; rendering runs sequentially, since the documents are large and
share one browser instance.

## Output

- `output/` — one PDF per successfully fetched company.

## Assumptions and decisions

- **Original filings only.** `10-K/A` amendments are excluded; only the original `10-K` is fetched.
- **Most recent filing.** When a company has multiple 10-Ks, the latest by filing date is chosen.
- **A CLI, not a service.** The task is a batch fetch, so there's no need for a long-running
  server or exposed endpoint — a CLI covers it and stays simple to run and reason about.

## Limitations

- The SEC submissions JSON is consumed without schema validation. A change in its shape
  surfaces as a caught, per-company failure rather than being validated at the boundary.
- The renderer uses Playwright's own browser fetch, so document downloads bypass the
  `sec_client` rate limiter. This is harmless at six companies but would matter at scale.

## Potential Next Steps

- **Docker**: A pinned, reproducible image bundling the Chromium install, so the
  environment is identical everywhere it runs.
- **Unified throttling**: Route document HTML through the rate-limited client
  (`set_content`) or extend throttling to the browser, so all SEC traffic respects the limit.
- **Avoid full-map loads**: Cache or query CIK lookups instead of fetching the entire ticker map for a handful of companies.
- **Caching**: Persist the index and filings to avoid refetching unchanged data.
- **Observability**: Structured logging and metrics for a shared, multi-team service.
- **Retry-After**: Check and use the `Retry-After` the header if available on 429s instead of only using fixed backoff.
- **Tests**: Add Unit integration and contract tests for reliablilty.
- **Expose Data**: Use sqlite or JSON file to keep log of created PDFs and their links. This can be exposed via command to find and download already saved PDFs.

## AI usage

See [`AI_USAGE.md`](./AI_USAGE.md).
