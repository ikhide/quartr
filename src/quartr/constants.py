"""Configuration for the package, read once from the environment.

This is the only module that touches ``.env``; everything else imports from here.
"""

import os

from dotenv import load_dotenv

load_dotenv()


def _required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(
            f"{name} is not set. Copy .env.example to .env and fill it in."
        )
    return value


SEC_URL = os.getenv("SEC_URL", "https://www.sec.gov").rstrip("/")
SEC_DATA_URL = os.getenv("SEC_DATA_URL", "https://data.sec.gov").rstrip("/")

SEC_USER_AGENT = _required("SEC_USER_AGENT")

DEFAULT_TICKERS = os.getenv("DEFAULT_TICKERS", "AAPL,META,GOOGL,AMZN,NFLX,GS")

TICKERS_URL = f"{SEC_URL}/files/company_tickers.json"

MAX_RETRIES = 3

REQUESTS_PER_SECOND = 8 # Keeping it under 10

RETRYABLE_STATUSES = frozenset({429, 500, 502, 503, 504})
