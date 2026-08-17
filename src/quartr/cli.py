from typing import Annotated
import typer
from dotenv import load_dotenv

load_dotenv()

app = typer.Typer()
DEFAULT_COMPANIES = "AAPL,META,GOOGL,AMZN,NFLX,GS"

@app.command()
def fetch(companies:  Annotated[str, typer.Argument(envvar="DEFAULT_LIST")]= DEFAULT_COMPANIES, output_dir: str = "output"):
    "Fetch the latest 10-K. for each company and save as PDF."
    
    companyArray = companies.split(",")
    typer.echo(f"Would fetch: {companyArray} -> {output_dir}")

if __name__ == "__main__":
    app()