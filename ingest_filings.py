import requests
import re
import time
from tools.vector_store import ingest_10k_text
import yfinance as yf

def chunk_text(text: str, size: int = 400) -> list:
    """Splits text into overlapping 400-word chunks."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), size - 30):  # 30-word overlap
        chunk = " ".join(words[i:i+size])
        if len(chunk) > 100:  # skip tiny leftover chunks
            chunks.append(chunk)
    return chunks

def ingest_ticker(ticker: str):
    print(f"Fetching 10-K for {ticker}...")

    # SEC EDGAR full-text search (free, no key needed)
    headers = {"User-Agent": "research@example.com"}  # SEC requires this
    search = requests.get(f"https://efts.sec.gov/LATEST/search-index?q=%22{ticker}%22&forms=10-K", headers=headers)
    hits = search.json().get("hits", {}).get("hits", [])
    if not hits:
        print(f"No 10-K found for {ticker}")
        return

    # Get the filing URL and fetch text
    accession = hits[0]["_source"]["period_of_report"]
    text_url = hits[0].get("_source", {}).get("period_of_report", "")

    # Simpler approach: use yfinance to get SEC filing links
    stock = yf.Ticker(ticker)

    # Use the business description as a proxy (real project: use SEC EDGAR API)
    description = stock.info.get("longBusinessSummary", "")
    if not description:
        print(f"No description for {ticker}")
        return

    chunks = chunk_text(description)
    ingest_10k_text(ticker, chunks)
    print(f"Ingested {len(chunks)} chunks for {ticker}")
    time.sleep(1)  # be polite to SEC servers

if __name__ == "__main__":
    tickers = ["TSLA", "AAPL", "NVDA", "MSFT", "AMZN"]
    for t in tickers:
        ingest_ticker(t)