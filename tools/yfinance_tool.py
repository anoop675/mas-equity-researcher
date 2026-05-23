# tools/yfinance_tool.py
import yfinance as yf
from crewai.tools import tool

@tool("fetch_financial_statements")
def fetch_financial_statements(ticker: str) -> dict:
    """Fetches key financial metrics for a given stock ticker."""
    stock = yf.Ticker(ticker)
    info = stock.info

    return {
        "company_name": info.get("longName", ticker),
        "sector": info.get("sector", "Unknown"),
        "market_cap": info.get("marketCap", 0),
        "market_cap_billions": round((info.get("marketCap", 0) or 0) / 1e9, 2),
        "revenue": info.get("totalRevenue", 0),
        "revenue_billions": round((info.get("totalRevenue", 0) or 0) / 1e9, 2),
        "net_income": info.get("netIncomeToCommon", 0),
        "net_income_billions": round((info.get("netIncomeToCommon", 0) or 0) / 1e9, 2),
        "free_cash_flow": info.get("freeCashflow", 0),
        "fcf_billions": round((info.get("freeCashflow", 0) or 0) / 1e9, 2),
        "total_debt": info.get("totalDebt", 0),
        "cash": info.get("totalCash", 0),
        "shares_outstanding": info.get("sharesOutstanding", 1),
        "earnings_growth": info.get("earningsGrowth", 0.10),
        "revenue_growth": info.get("revenueGrowth", 0.10),
        "beta": info.get("beta", 1.0),
        "pe_ratio": info.get("trailingPE", 0),
        "profit_margin": info.get("profitMargins", 0),
        "return_on_equity": info.get("returnOnEquity", 0),
        "debt_to_equity": info.get("debtToEquity", 0),
        "ebitda": info.get("ebitda", 0),
        "ebitda_billions": round((info.get("ebitda", 0) or 0) / 1e9, 2),
    }

@tool("fetch_stock_price")
def fetch_stock_price(ticker: str) -> dict:
    """Fetches current price, 52-week high/low, and recent price trend."""
    stock = yf.Ticker(ticker)
    info = stock.info
    hist = stock.history(period="1y")

    current_price = round(hist["Close"].iloc[-1], 2) if not hist.empty else 0

    return {
        "current_price": current_price,
        "52w_high": round(hist["Close"].max(), 2) if not hist.empty else 0,
        "52w_low": round(hist["Close"].min(), 2) if not hist.empty else 0,
        "avg_volume": int(hist["Volume"].mean()) if not hist.empty else 0,
        "currency": info.get("currency", "USD"),
    }