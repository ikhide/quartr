##API

Get CIK from ticker: https://{Sec_url}/files/company_tickers.json
Get Submission by CIK: https://{sec_data_url}submissions/CIK##########.json
Fetch 10-k document by accession number: https://{sec_data_url}/Archives/edgar/data/##########/##########-##-##-##########.txt

Max rate: 10 requests per second
Header must contain User-Agent

Tools
CLI tool: Typer
HTTP client: httpx
PDF: Playwright or WeasyPrint
Other: Pydantic, pandas?

Task

- To fetch the 10-K report, an annual report that the companies need to submit to the SEC.
- Pull the latest 10-K reports from some of the world's leading companies. Default - Apple, Meta, Alphabet, Amazon, Netflix, Goldman Sachs.
