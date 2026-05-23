import os
from dotenv import load_dotenv

load_dotenv()  # reads your .env file into os.environ

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
#LLM_MODEL = "llama3-groq-70b-8192-tool-use-preview" #depreciated
LLM_MODEL = "llama-3.3-70b-versatile"
MANAGER_MODEL = "llama-3.3-70b-versatile"
QDRANT_URL = "http://localhost:6333"
EMBEDDING_MODEL  = "all-MiniLM-L6-v2"  # small, fast, runs on CPU
CRYPTO_TICKERS = {
    "BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD",
    "XRP-USD", "ADA-USD", "DOGE-USD", "AVAX-USD",
    "MATIC-USD", "DOT-USD", "LINK-USD", "UNI-USD",
}

def is_crypto(ticker: str) -> bool:
    return ticker.upper() in CRYPTO_TICKERS or ticker.upper().endswith("-USD")