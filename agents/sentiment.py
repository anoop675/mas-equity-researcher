# agents/sentiment.py
from crewai import Agent
from crewai.tools import tool
from llm import get_agent_llm
import feedparser

@tool("get_yahoo_finance_news")
def get_yahoo_finance_news(ticker: str) -> list:
    """Fetches latest news headlines from Yahoo Finance RSS."""
    url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US"
    feed = feedparser.parse(url)
    # Only return 5 headlines, titles only (no summaries) to save tokens
    return [
        {"title": e.get("title", ""), "published": e.get("published", "")}
        for e in feed.entries[:5]
    ]

@tool("get_google_news")
def get_google_news(ticker: str) -> list:
    """Fetches latest news from Google News RSS."""
    coin = ticker.replace("-USD", "")
    url = f"https://news.google.com/rss/search?q={coin}+stock&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(url)
    # Only return 5 headlines, titles only to save tokens
    return [
        {"title": e.get("title", ""), "published": e.get("published", "")}
        for e in feed.entries[:5]
    ]

@tool("get_seeking_alpha_news")
def get_seeking_alpha_news(ticker: str) -> list:
    """Fetches news from Seeking Alpha RSS feed."""
    try:
        url = f"https://seekingalpha.com/api/sa/combined/{ticker}.xml"
        feed = feedparser.parse(url)
        return [
            {"title": e.get("title", ""), "published": e.get("published", "")}
            for e in feed.entries[:3]
        ]
    except Exception:
        return [{"title": "Seeking Alpha unavailable", "published": ""}]

def create_sentiment_agent():
    return Agent(
        role="Market Sentiment Analyst",
        goal=(
            "Analyze news headlines to determine market sentiment. "
            "Classify as Bullish, Neutral, or Bearish with 3 reasons."
        ),
        backstory=(
            "You are a sentiment analyst who reads financial news daily "
            "and translates it into clear sentiment signals."
        ),
        tools=[get_yahoo_finance_news, get_google_news, get_seeking_alpha_news],
        llm="groq/llama-3.3-70b-versatile",
        verbose=True,
        allow_delegation=False,
    )