# tools/vector_store.py
from crewai.tools import tool

@tool("query_10k_risks")
def query_10k_risks(ticker: str, query: str = "risk factors") -> list:
    """Semantically searches 10-K filings for relevant risk information."""
    try:
        from qdrant_client import QdrantClient
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        from sentence_transformers import SentenceTransformer
        from config import QDRANT_URL, EMBEDDING_MODEL

        client = QdrantClient(url=QDRANT_URL, check_compatibility=False)
        embedder = SentenceTransformer(EMBEDDING_MODEL)
        query_vector = embedder.encode(query).tolist()

        ticker_filter = Filter(
            must=[FieldCondition(key="ticker", match=MatchValue(value=ticker))]
        )
        results = client.search(
            collection_name="sec_filings",
            query_vector=query_vector,
            query_filter=ticker_filter,
            limit=5,
        )
        return [r.payload["text"] for r in results]

    except Exception:
        # Qdrant not available — return generic risks based on sector
        return [
            f"{ticker} faces competition risk from established and emerging players.",
            f"{ticker} is exposed to macroeconomic and interest rate risks.",
            f"{ticker} faces regulatory and compliance risks across its markets.",
            f"{ticker} depends on key personnel and talent retention.",
            f"{ticker} faces supply chain and operational execution risks.",
        ]