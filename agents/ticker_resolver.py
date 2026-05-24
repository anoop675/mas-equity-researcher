# This agent takes any natural language input and resolves it to a valid stock ticker symbol.
from crewai import Agent
from crewai.tools import tool
import yfinance as yf
import requests
from config import GROQ_API_KEY
import os

os.environ["GROQ_API_KEY"] = GROQ_API_KEY

@tool("search_ticker_by_name")
def search_ticker_by_name(company_name: str) -> dict:
    """Searches for a stock ticker given a company name or description.
    Returns ticker, full company name, exchange, and sector."""
    # Yahoo Finance search endpoint (free, no key needed)
    url = "https://query2.finance.yahoo.com/v1/finance/search"
    params = {
        "q": company_name,
        "quotesCount": 5,
        "newsCount": 0,
        "listsCount": 0,
    }
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        resp = requests.get(url, params=params, headers=headers)
        quotes = resp.json().get("quotes", [])

        if not quotes:
            return {"error": f"No ticker found for: {company_name}"}

        # Filter to only stocks (not ETFs, futures, etc.)
        stocks = [q for q in quotes if q.get("quoteType") == "EQUITY"]
        if not stocks:
            stocks = quotes  # fallback to all results

        top = stocks[0]
        return {
            "ticker": top.get("symbol"),
            "company_name": top.get("longname") or top.get("shortname"),
            "exchange": top.get("exchange"),
            "sector": top.get("sector", "Unknown"),
            "all_matches":  [{"ticker": q.get("symbol"), "name": q.get("longname") or q.get("shortname")} for q in stocks[:5]]
        }
    except Exception as e:
        return {"error": str(e)}

@tool("validate_ticker")
def validate_ticker(ticker: str) -> dict:
    """
    Validates that a ticker symbol actually exists and has data.
    Returns basic info if valid, error if not.
    """
    try:
        stock = yf.Ticker(ticker.upper())
        info = stock.info

        # If yfinance can't find it, info will be mostly empty
        name = info.get("longName") or info.get("shortName")
        if not name:
            return {
                "valid":  False,
                "reason": f"Ticker '{ticker}' not found or has no data"
            }

        return {
            "valid": True,
            "ticker": ticker.upper(),
            "company_name": name,
            "sector": info.get("sector", "Unknown"),
            "market_cap": info.get("marketCap", 0),
            "currency": info.get("currency", "USD"),
            "is_crypto": ticker.endswith("-USD"),
        }
    except Exception as e:
        return {"valid": False, "reason": str(e)}

def create_ticker_resolver_agent():
    return Agent(
        role="Stock Research Input Specialist",
        goal=(
            "Understand what stock or asset the user wants analyzed — "
            "no matter how they phrase it — and return the single correct "
            "ticker symbol. Always validate the ticker before returning it."
        ),
        backstory=(
            "You are the intake specialist at an equity research firm. "
            "Clients describe stocks in all kinds of ways — by nickname, "
            "CEO name, product name, or partial company name. "
            "Your job is to figure out exactly which publicly traded "
            "company they mean and return the correct ticker. "
            "You never guess — you always verify with the validation tool."
        ),
        tools=[search_ticker_by_name, validate_ticker],
        llm="groq/llama-3.3-70b-versatile",
        verbose=True,
        allow_delegation=False,
        max_iter=4,
    )