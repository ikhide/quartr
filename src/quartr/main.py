"""CLI entry point and orchestration: tickers in, PDFs on disk."""

import asyncio
from pathlib import Path
from typing import Annotated

import typer

from quartr import constants, filings
from quartr.models import Company, Filing, Result
from quartr.pdf_renderer import PdfRenderer
from quartr.sec_client import SecClient

# A lookup either found the filing, or produced a reason it did not.
Lookup = Filing | str

app = typer.Typer(help="Fetch the latest 10-K annual reports from SEC EDGAR.")


@app.callback()
def cli() -> None:
    """Keeps `fetch` an explicit subcommand rather than the app's only command."""

@app.command()
def fetch(
    companies: Annotated[
        str, typer.Argument(help="Comma-separated tickers, e.g. AAPL,MSFT")
    ] = constants.DEFAULT_TICKERS,
    output_dir: Annotated[
        Path, typer.Option(help="Where to write the PDFs.")
    ] = Path("output"),
) -> None:
    tickers = [
        ticker.strip().upper() for ticker in companies.split(",") if ticker.strip()
    ]
    if not tickers:
        raise typer.BadParameter("No tickers given.")

    results = asyncio.run(run(tickers, output_dir))
    
    for result in results:
        if result.ok:
            typer.echo(f"  {result.ticker:<6} {result.path}")
        else:
            typer.secho(f"  {result.ticker:<6} {result.error}", fg=typer.colors.RED)

    succeeded = sum(1 for result in results if result.ok)
    typer.echo(f"\n{succeeded} of {len(results)} saved to {output_dir}")
    if not succeeded:
        raise typer.Exit(1)


async def run(tickers: list[str], output_dir: Path) -> list[Result]:
    async with SecClient() as client:
        index = await filings.fetch_company_index(client)
        lookups = await _lookup_all(client, tickers, index)
        
        print(f"Hello, my name is {lookups}")
        

    if not any(isinstance(lookup, Filing) for lookup in lookups.values()):
        return [Result(ticker, error=str(lookups[ticker])) for ticker in tickers]

    output_dir.mkdir(parents=True, exist_ok=True)
    return await _render_all(tickers, lookups, output_dir)


async def _lookup_all(
    client: SecClient, tickers: list[str], index: dict[str, Company]
) -> dict[str, Lookup]:
    async def lookup(ticker: str) -> Lookup:
        company = index.get(ticker)
        if company is None:
            return "not a recognised SEC ticker"
        try:
            filing = await filings.latest_10k(client, company)
        except Exception as error:  # noqa: BLE001 - reported, never fatal
            return _describe(error)
        return filing if filing else "no 10-K on file"

    found = await asyncio.gather(*(lookup(ticker) for ticker in tickers))
    return dict(zip(tickers, found))


async def _render_all(
    tickers: list[str], lookups: dict[str, Lookup], output_dir: Path
) -> list[Result]:
 
    results: list[Result] = []

    async with PdfRenderer() as renderer:
        for ticker in tickers:
            lookup = lookups[ticker]
            if not isinstance(lookup, Filing):
                results.append(Result(ticker, error=lookup))
                continue

            destination = output_dir / lookup.filename
            try:
                await renderer.render(lookup.document_url, destination)
            except Exception as error:  # noqa: BLE001 - reported, never fatal
                results.append(Result(ticker, error=_describe(error)))
            else:
                results.append(Result(ticker, path=destination))

    return results


def _describe(error: Exception) -> str:
    return str(error) or type(error).__name__


if __name__ == "__main__":
    app()
