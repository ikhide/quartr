"""Value objects passed between the client, the filing lookup and the renderer."""

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from quartr import constants


@dataclass(frozen=True)
class Company:
    ticker: str
    cik: int
    name: str

    @property
    def padded_cik(self) -> str:
        """CIK zero-padded to ten digits, as the submissions endpoint expects."""
        return str(self.cik).zfill(10)

    @property
    def submissions_url(self) -> str:
        return f"{constants.SEC_DATA_URL}/submissions/CIK{self.padded_cik}.json"


@dataclass(frozen=True)
class Filing:
    company: Company
    accession_number: str
    filing_date: date
    report_date: date
    primary_document: str
    form: str = "10-K"

    @property
    def document_url(self) -> str:
        accession = self.accession_number.replace("-", "")
        return (
            f"{constants.SEC_URL}/Archives/edgar/data"
            f"/{self.company.cik}/{accession}/{self.primary_document}"
        )

    @property
    def filename(self) -> str:
        return f"{self.company.ticker}_{self.form}_{self.report_date}.pdf"


@dataclass(frozen=True)
class Result:
    """The outcome for one ticker: either a saved PDF, or why there isn't one."""

    ticker: str
    path: Path | None = None
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None
