# quartr

Fetch the latest 10-K annual report for a set of companies from SEC EDGAR and save each as a PDF.

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
