"""Resolving tickers to companies and finding their latest 10-K."""

from datetime import date

from quartr import constants
from quartr.models import Company, Filing
from quartr.sec_client import SecClient

FORM_10K = "10-K"


async def fetch_company_index(client: SecClient) -> dict[str, Company]:
    rows = await client.get_json(constants.TICKERS_URL)
    return {
        row["ticker"].upper(): Company(
            ticker=row["ticker"].upper(),
            cik=row["cik_str"],
            name=row["title"],
        )
        for row in rows.values()
    }


async def latest_10k(client: SecClient, company: Company) -> Filing | None:
    submissions = await client.get_json(company.submissions_url)
    recent = submissions["filings"]["recent"]

    # "recent" is a set of parallel arrays sharing one index, newest first.
    for index, form in enumerate(recent["form"]):
        if form == FORM_10K:
          
            return Filing(
                company=company,
                accession_number=recent["accessionNumber"][index],
                filing_date=date.fromisoformat(recent["filingDate"][index]),
                report_date=date.fromisoformat(recent["reportDate"][index]),
                primary_document=recent["primaryDocument"][index],
                form=form,
            )
    return None
